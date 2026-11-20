"""CC raw extract nodes: Way4 extracts scoped to each account's window.

    build_cc_transactions : transaction history with the ``prm_cc`` derivations (A3
                            payments).
    build_cc_balance      : minimum_due / overdue buckets / total_due (A3 dues).
    build_cc_billing      : billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).

All three read ``crx_cc_acct_windows`` (``build_cc_acct_windows`` in
``cc_a3_payment_credibility.nodes``) and prune raw partitions with
``_window_utils.prune_by_edp_load_date``. ``contract_idt`` is cast double -> long at the
raw boundary; transactions keep primary_entry_idt != 0 and org == 100.
"""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import (
    derive_billing_amounts,
    derive_overdue_buckets,
)
from enbd_collections.nodes.utils.config import (
    POST_BLOCK_X_SENTINEL_DATE,
    TXN_CATEGORIES,
)
from enbd_collections.pipelines.crx_persona._common import require_columns
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    require_columns(
        acct_windows, ["account_id", "acct_start", "acct_end"], "crx_cc_acct_windows"
    )
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC transactions in each account's window, with ``txn_category`` (``prm_cc``'s
    ``TXN_CATEGORIES`` by ``txn_code``; NULL for an unrecognised code),
    ``is_international`` (``DOMESTIC=N`` in ``add_info``) and ``is_post_block_x_fee``
    (the Block-W fee-accrual artefacts, as in ``stg_transaction.build()``, which A3 must
    not read as payments).

    Returns::

        contract_id (long), observation_date (date, banking date), direction (int),
        txn_amount_aed (double), txn_description (string),
        merchant_category_code (int), is_international (int),
        txn_category (string), is_post_block_x_fee (int)
    """
    require_columns(
        raw_transaction,
        [
            "primary_entry_idt",
            "org",
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "settl_amount",
            "direction",
            "txn_code",
            "txn_description",
            "add_info",
            "trans_mcc",
            "trans_date",
            "card_idt",
            "service_class",
        ],
        "raw_transaction",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        .filter(F.col("primary_entry_idt") != 0)
        .filter(F.col("org") == 100)
    )
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # NULL for unrecognised codes: excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # System-generated fee accruals posted after collector Block W carry a sentinel
    # trans_date; flagged so A3 Dimension B/C never count them as a payment.
    sentinel = F.lit(POST_BLOCK_X_SENTINEL_DATE).cast(DateType())
    df = df.withColumn(
        "is_post_block_x_fee",
        F.when(
            (F.col("trans_date").cast(DateType()) == sentinel)
            & (F.col("card_idt") == 0)
            & (F.col("settl_amount") == 0)
            & (F.col("service_class") == "I"),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
        F.col("is_post_block_x_fee").cast("int"),
    ).distinct()


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC balance history in each account's window: the billing amounts and overdue
    buckets of ``prm_cc.derive_billing_amounts`` / ``derive_overdue_buckets`` per
    banking date (Way4 stores credit balances as negative; both flip the sign).

    Returns::

        contract_id (long), observation_date (date), minimum_due (double),
        stmt_balance (double), total_due (double),
        overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    require_columns(
        raw_stg_balance,
        ["contract_idt", "banking_date", "edp_load_date"],
        "raw_stg_balance",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = prune_by_edp_load_date(
        raw_stg_balance, crx_cc_acct_windows
    ).withColumn("banking_date", F.col("banking_date").cast(DateType()))
    scoped_balance = scope_to_acct_window(scoped_balance, acct_windows, "banking_date")

    billing_amounts = derive_billing_amounts(scoped_balance, raw_stg_account_group)
    overdue_buckets = derive_overdue_buckets(scoped_balance, raw_stg_account_group)

    combined = billing_amounts.join(
        overdue_buckets, on=["contract_idt", "banking_date"], how="left"
    )

    select_cols = [
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("minimum_due").cast("double"),
        F.col("stmt_balance").cast("double"),
        F.col("total_due").cast("double"),
    ] + [
        F.col(f"overdue_ovd_{i:02d}").cast("double").alias(f"overdue_bucket_{i:02d}")
        for i in range(1, 9)
    ]

    return combined.select(*select_cols)


def build_cc_billing(
    raw_stg_billing: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC billing-cycle headers in each account's window. ``next_billing_date`` is the
    next statement of the contract (NULL for its latest cycle). A payment belongs to the
    cycle ``(billing_date, next_billing_date]``, not ``(billing_date, due_date]``: the
    due date falls about 5 days before the next statement, and late payments would
    otherwise be dropped. ``dlq_level_m`` is Way4's per-cycle bucket
    (``BS_PMT_CYCLE_DUE`` in ``add_info``; NULL when blank).

    Returns::

        contract_id (long), observation_date (date, = billing_date),
        due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    require_columns(
        raw_stg_billing,
        ["contract_idt", "billing_date", "edp_load_date", "due_date", "add_info"],
        "raw_stg_billing",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    pruned = prune_by_edp_load_date(raw_stg_billing, crx_cc_acct_windows)
    scoped = (
        scope_to_acct_window(pruned, acct_windows, "billing_date")
        .withColumn("billing_date", F.col("billing_date").cast(DateType()))
        .withColumn("due_date", F.col("due_date").cast(DateType()))
        .withColumn(
            "dlq_level_m",
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1).cast(
                "int"
            ),
        )
        .select("contract_idt", "billing_date", "due_date", "dlq_level_m")
        .distinct()
    )

    next_billing_window = Window.partitionBy("contract_idt").orderBy("billing_date")
    with_next = scoped.withColumn(
        "next_billing_date", F.lead("billing_date").over(next_billing_window)
    )

    return with_next.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("billing_date").alias("observation_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
        F.col("dlq_level_m"),
    )
