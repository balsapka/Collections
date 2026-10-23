"""T04c — CRX CC Raw Extract nodes.

# pylint: disable=too-many-locals
# Rationale: three build functions, each with per-account T0-window scoping
# and schema derivations. Logic is self-contained within each function.

Three build functions promoted from T04b private helpers to persisted
intermediate catalog nodes:

    build_cc_transactions : T0-scoped transaction history with enriched schema
                            (replaces _load_t0_scoped_transactions + prm_cc
                            derivations; consumed by T04b, T05, T06)
    build_cc_limits       : T0-scoped credit-limit snapshots pivoted by type_code
                            (replaces prm_limit; consumed by T05)
    build_cc_balance      : T0-scoped total_due billing history
                            (replaces _load_t0_scoped_balance; consumed by T04b)

All three use the same per-account T0 window:
    acct_start = add_months(trunc(min(t0), 'month'), -12)
    acct_end   = trunc(max(t0), 'month')
computed over non-censored spells in crx_cc_spell_table.

Quality filter (transactions + limits): primary_entry_idt != 0, org == 100.
Type cast: contract_idt (double → long) at the DDI raw boundary.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.utils.config import TXN_CATEGORIES


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """Extract T0-anchored CC transaction history with enriched schema.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Quality filters: primary_entry_idt != 0, org == 100 (same as stg_transaction.build()).
    Replicates prm_cc.build_transaction() derivation logic for txn_category and
    is_international.

    Args:
        raw_transaction:      Raw Way4 transaction table (DDI-backed). Long history.
                              Required cols: primary_entry_idt, org, contract_idt,
                              banking_date, settl_amount, direction, txn_code,
                              txn_description, add_info, trans_mcc.
        crx_cc_spell_table:   T03 output at (account_id, spell_id) grain.
                              Used to derive per-account T0 window boundaries.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), direction (int),
            txn_amount_aed (double), txn_description (string),
            merchant_category_code (int), is_international (int),
            txn_category (string)
    """
    # Non-censored spells drive the T0 window boundaries.
    # Excludes both censored subtypes (data_depth + restructured_entry) — see
    # cc_payment_trajectory/nodes.py Step 0 comment for rationale.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)

    # Per-account T0 window: [min(T0) - 12m, max(T0)]
    acct_windows = (
        spell.groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("acct_start"),
            F.trunc(F.max("t0"), "month").alias("acct_end"),
        )
        .select(
            F.col("account_id").alias("contract_idt"),  # long — matches raw cast below
            "acct_start",
            "acct_end",
        )
    )

    df = (
        raw_transaction
        # Base quality filters (same as stg_transaction.build())
        .filter(F.col("primary_entry_idt") != 0)
        .filter(F.col("org") == 100)
        # Cast raw double key to long before join (raw DDI contract_idt is double)
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        # Scope + date filter via inner join on per-account windows
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col("banking_date").cast(DateType()) >= F.col("acct_start"))
            & (F.col("banking_date").cast(DateType()) <= F.col("acct_end"))
        )
    )

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

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
    ).distinct()


def build_cc_limits(
    raw_stg_limit: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """Extract T0-anchored CC credit-limit snapshots, pivoted by type_code.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Pivot logic replicates stg_limit.build() but uses type_code FIN_LIMIT and
    AVAILABLE only (ADD_LIMIT excluded; not needed for util_ratio computation).

    Args:
        raw_stg_limit:        Raw Way4 limit table (DDI-backed).
                              Required cols: contract_idt, banking_date,
                              type_code, amount.
        crx_cc_spell_table:   T03 output. Used for per-account T0 window.

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

    pivoted = (
        raw_stg_limit
        # Cast raw double key to long (DDI raw contract_idt is double)
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        # Scope + date filter via inner join on per-account windows
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col("banking_date").cast(DateType()) >= F.col("acct_start"))
            & (F.col("banking_date").cast(DateType()) <= F.col("acct_end"))
        )
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
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """Extract T0-anchored total_due billing history.

    Direct port of T04b _load_t0_scoped_balance promoted to a standalone node.
    Replicates prm_cc._derive_billing_amounts() logic using raw DDI sources,
    scoped to the T0-anchored per-account window.

    Way4 stores credit balances as negative; balance * -1 yields positive total_due.
    Account_group dimension lookup filters to TOTAL_DUE type (class_code=BALANCE_TYPE).

    Args:
        raw_stg_balance:        Raw Way4 balance table (DDI-backed).
                                Required cols: contract_idt, billing_date,
                                account_group_id, balance.
        raw_stg_account_group:  Dimension table mapping account_group_id →
                                type_code / class_code.
        crx_cc_spell_table:     T03 output. Used for per-account T0 window.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), total_due (double)
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

    # Account_group dimension — filter to TOTAL_DUE balance type (broadcast: small table)
    ag_total_due = F.broadcast(
        raw_stg_account_group.filter(
            (F.col("type_code") == "TOTAL_DUE")
            & (F.col("class_code") == "BALANCE_TYPE")
        )
        .select("account_group_id")
        .distinct()
    )

    return (
        raw_stg_balance
        # Cast raw double key to long (DDI raw contract_idt is double)
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        # Scope + date filter via inner join on per-account windows
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col("billing_date").cast(DateType()) >= F.col("acct_start"))
            & (F.col("billing_date").cast(DateType()) <= F.col("acct_end"))
        )
        # Inner join to retain only TOTAL_DUE rows
        .join(ag_total_due, on="account_group_id", how="inner")
        # total_due = sum(balance * -1) per (contract, billing_date)
        # Way4 stores credit balances as negative; flip sign for semantic clarity
        .groupBy("contract_idt", "billing_date")
        .agg(F.sum(F.col("balance") * -1).alias("total_due"))
        .select(
            F.col("contract_idt").alias("contract_id"),  # long
            F.col("billing_date").cast(DateType()).alias("observation_date"),
            F.col("total_due").cast("double"),
        )
    )
