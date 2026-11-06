"""CRX CC raw extract nodes: window-scoped Way4 extracts for A3.

# pylint: disable=too-many-locals

    build_cc_acct_windows : per-account [acct_start, acct_end] window from the A3
                            episode anchor (A4) and the observation rows; persisted
                            once, read by the three extracts below.
    build_cc_transactions : window-scoped transaction history with the prm_cc
                            derivations (A3 payments).
    build_cc_limits       : credit-limit snapshots pivoted by type_code, on its own
                            spell-table window (no persona reader at present).
    build_cc_balance      : window-scoped minimum_due / overdue buckets / total_due
                            (A3 dues).
    build_cc_billing      : window-scoped billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).

Quality filter (transactions + limits): primary_entry_idt != 0, org == 100.
Type cast: contract_idt (double -> long) at the DDI raw boundary.
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
from enbd_collections.pipelines.crx_persona._dpd_journey.anchor import episode_start
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def build_cc_acct_windows(
    crx_cc_obs_base: DataFrame,
    crx_cc_a4_deterioration: DataFrame,
    history_floor_date: str,
) -> DataFrame:
    """Shared per-account [acct_start, acct_end] window for the A3 extracts.

    acct_start covers 12 months plus one cycle before the earliest episode start the
    account's observation rows have (A3 Dimension C, D-A3-2), and at least 13 months
    before its first observation (A3 Dimensions A and B); never before
    history_floor_date minus 35 days (the statement just before the floor).
    acct_end = the account's last observation date.

    Persisted once and consumed by build_cc_transactions, build_cc_balance and
    build_cc_billing.

    Args:
        crx_cc_obs_base: account_id, observation_date, cif_id.
        crx_cc_a4_deterioration: the A4 rows the episode anchor is read from.
        history_floor_date: ISO date (params:cc_a3_history_floor_date).

    Returns:
        DataFrame with columns (account_id, acct_start, acct_end).
    """
    episodes = episode_start(crx_cc_obs_base, crx_cc_a4_deterioration)
    first = (
        crx_cc_obs_base.join(
            episodes, on=["account_id", "observation_date"], how="left"
        )
        .groupBy("account_id")
        .agg(
            F.least(
                F.min("episode_start"), F.trunc(F.min("observation_date"), "month")
            ).alias("_first"),
            F.max("observation_date").alias("acct_end"),
        )
    )
    floor = F.date_sub(F.lit(str(history_floor_date)).cast(DateType()), 35)
    return first.select(
        "account_id",
        F.greatest(F.add_months(F.col("_first"), -13), floor).alias("acct_start"),
        "acct_end",
    )


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped CC transaction history with enriched schema.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows).
    Partition pruning: raw_transaction is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a transaction happens (banking_date) and when it
    lands in its edp_load_date partition. Unlike stg_transaction.build() (whose
    spine, data_spine_contracts_way4, already bakes the lookback into
    observation_date, so it needs no extra buffer), cc_spine has no backward
    lookback at all — crx_cc_acct_windows builds that bound itself, so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.
    Quality filters: primary_entry_idt != 0, org == 100 (same as stg_transaction.build()).
    Replicates prm_cc.build_transaction() derivation logic for txn_category and
    is_international, and stg_transaction.build()'s is_post_block_x_fee sentinel-fee
    derivation (Block-W fee-accrual artifacts that must not be mistaken for real
    post-delinquency payment activity).

    Args:
        raw_transaction:     Raw Way4 transaction table (DDI-backed). Long history.
                             Required cols: primary_entry_idt, org, contract_idt,
                             banking_date, edp_load_date, settl_amount, direction,
                             txn_code, txn_description, add_info, trans_mcc,
                             trans_date, card_idt, service_class.
        crx_cc_acct_windows: T04c — build_cc_acct_windows output.
                             Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), direction (int),
            txn_amount_aed (double), txn_description (string),
            merchant_category_code (int), is_international (int),
            txn_category (string), is_post_block_x_fee (int)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        # Base quality filters (same as stg_transaction.build())
        .filter(F.col("primary_entry_idt") != 0).filter(F.col("org") == 100)
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # Derive txn_category from txn_code (replicates prm_cc.build_transaction logic).
    # Default NULL — unrecognized codes excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # Derive is_international from DOMESTIC flag in add_info JSON
    # (replicates prm_cc.build_transaction logic).
    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # Derive is_post_block_x_fee (replicates stg_transaction.build()'s sentinel-fee
    # derivation) — system-generated fee-accrual events posted after collector
    # Block W, flagged so A3 Dimension B/C never count them as a real payment.
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


def build_cc_limits(
    raw_stg_limit: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """Extract T0-anchored CC credit-limit snapshots, pivoted by type_code.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Pivot logic replicates stg_limit.build() but uses type_code FIN_LIMIT and
    AVAILABLE only (ADD_LIMIT excluded; not needed for util_ratio computation).

    Deliberately does NOT consume crx_cc_acct_windows — that window's forward
    edge is cc_spine-anchored (extends past T0), which this function does not
    need (see module docstring).

    Args:
        raw_stg_limit:       Raw Way4 limit table (DDI-backed).
                             Required cols: contract_idt, banking_date,
                             type_code, amount.
        crx_cc_spell_table:  T03 output. Used for per-account T0 window.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date),
            credit_limit (double), available_limit (double)
    """
    # Excludes both censored subtypes — see build_cc_transactions Step 0 comment.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)

    acct_windows = (
        spell.groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("acct_start"),
            F.trunc(F.max("t0"), "month").alias("acct_end"),
        )
        .select(
            F.col("account_id").alias("contract_idt"),
            "acct_start",
            "acct_end",
        )
    )

    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join). This T0-only
    # acct_windows is the one built just above, NOT crx_cc_acct_windows —
    # see module/function docstring for why this window is deliberately kept
    # separate.
    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped
        # Only limit types needed for util_ratio: FIN_LIMIT (credit_limit) + AVAILABLE
        .filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # Pivot — max() is deterministic when multiple rows exist for same key
        # (highest approved limit wins; highest available = least alarming)
        .groupBy("contract_idt", "banking_date")
        .pivot("type_code", ["FIN_LIMIT", "AVAILABLE"])
        .agg(F.max("amount"))
        .withColumnRenamed("FIN_LIMIT", "credit_limit")
        .withColumnRenamed("AVAILABLE", "available_limit")
    )

    return pivoted.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("credit_limit").cast("double"),
        F.col("available_limit").cast("double"),
    )


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped minimum_due/stmt_balance/total_due/overdue-bucket history.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge.

    Reuses prm_cc.derive_billing_amounts() and prm_cc.derive_overdue_buckets() —
    the authoritative, production-verified derivations — rather than hand-rolling
    the pivots here, per the standing team decision to never reverse-engineer
    billing amounts from raw stg_balance. raw_stg_balance already carries its own
    native banking_date column (the daily snapshot grain both derive_* functions
    group by) distinct from billing_date — scoping/output use banking_date
    directly rather than aliasing billing_date onto it.

    Way4 stores credit balances as negative; derive_billing_amounts/
    derive_overdue_buckets flip the sign.

    Partition pruning: raw_stg_balance is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a balance snapshot is taken (banking_date) and
    when it lands in its edp_load_date partition. cc_spine has no backward
    lookback at all (unlike data_spine_contracts_way4, which already bakes it
    into observation_date for the credit_card_way4 staging layer), so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.

    Args:
        raw_stg_balance:       Raw Way4 balance table (DDI-backed).
                               Required cols: contract_idt, banking_date,
                               edp_load_date, account_group_id, balance.
        raw_stg_account_group: Dimension table mapping account_group_id →
                               type_code / class_code.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), minimum_due (double),
            stmt_balance (double), total_due (double),
            overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_stg_balance, crx_cc_acct_windows).withColumn(
            "banking_date", F.col("banking_date").cast(DateType())
        )
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
    """Extract window-scoped billing-cycle header: billing_date, due_date,
    next_billing_date, dlq_level_m.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge. This is the
    primitive A3 Dimension B/C's payment-attribution helper
    (cc_a3_payment_credibility._signals_common.attribute_payments_to_billing_cycles)
    is built on.

    next_billing_date = F.lead(billing_date) per contract. A payment belongs to
    the cycle (billing_date, due_date) iff billing_date < banking_date <=
    next_billing_date — NOT billing_date < banking_date <= due_date. due_date is
    ~billing_date+25d while the next statement cuts ~billing_date+30d, leaving a
    ~5-6 day dead zone where late payments (common in practice) would otherwise
    be dropped or misattributed to the wrong cycle — found and fixed in the
    exploratory notebook (notebooks/data_engineering/crx_persona/
    cc_account_payment_profiling.ipynb). next_billing_date is NULL for the most
    recent cycle per contract — treated as open-ended by the attribution helper.

    dlq_level_m is Way4's own per-cycle DLQ bucket (0-9), extracted from the
    add_info KV field's BS_PMT_CYCLE_DUE= key — the identical extraction
    nodes/spine/cc_way4/spine_builders.py uses to build cc_spine's
    dlq_bucket_from_hist, so this is the same ground truth the rest of the
    business already treats as authoritative, not a reconstruction from
    crx_cc_balance's overdue buckets. [CONFIRM]: BS_PMT_CYCLE_DUE is
    sometimes blank/missing in add_info (seen in sample data) — regexp_extract
    then casts to NULL, same as spine_builders.py's own behavior; no fallback
    is applied. Consumed by build_a3_payment_cycles for the DPD-bucket-based
    alternative to Dimension B/C's payment-cycle method (see
    cc_a3_payment_credibility.constants._DLQ_LEVEL_SATURATED).

    Partition pruning: raw_stg_billing is filtered on edp_load_date to the
    global [min(acct_start), max(acct_end)] bound (from crx_cc_acct_windows)
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS (12 months), before the
    per-account join — same rationale as build_cc_transactions/build_cc_balance
    (cc_spine has no backward lookback of its own).

    Args:
        raw_stg_billing:       Raw Way4 billing table (DDI-backed).
                               Required cols: contract_idt, billing_date,
                               edp_load_date, due_date, add_info.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date, = billing_date),
            due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    # Partition prune on edp_load_date before the join (see docstring), then
    # scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
