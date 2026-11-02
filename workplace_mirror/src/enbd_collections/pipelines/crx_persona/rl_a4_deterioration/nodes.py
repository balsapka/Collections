"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_full_history_linked  crx_rl_full_history + int_loan_master
                                     + int_loan_restructure_link
                                     -> crx_rl_full_history_linked, crx_rl_restructure_chains
Node 2 build_rl_dpd_sequences        crx_rl_full_history + feature_retail_loans
                                     -> crx_rl_dpd_sequences
Node 3 build_rl_linked_dpd_sequences crx_rl_full_history_linked + chains
                                     + feature_retail_loans -> crx_rl_dpd_sequences_linked
Node 4 build_rl_a4_deterioration     both sequences + chains -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).

A restructure closes the old account and opens a new one. A matched new account gets the
original loans' months in front of its own, from the month both the restructure flag and
the closure have happened; before that month it keeps its own history, so nothing leaks
from the future. A loan is restructured if feature_retail_loans.has_restructured_loan_flag
says so; one with no original loan's months stays a blind spot.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns
from .._dpd_journey import (
    RL,
    _log_state_stats,
    build_deterioration,
    build_dpd_sequences,
    journey_params,
)
from .chains import Edge, resolve_chains

# Account columns of int_loan_restructure_link.
_LINK_ACCOUNT = "account_id"
_LINK_ORIGINAL = "orig_account_id"

_CHAIN_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("chain_known_date", T.DateType()),
        T.StructField("chain_n_originals", T.IntegerType()),
        T.StructField("chain_match_type", T.StringType()),
        T.StructField("chain_candidate_count", T.IntegerType()),
    ]
)
_MEMBER_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("original_id", T.StringType()),
    ]
)


def _edges(link: DataFrame) -> list[Edge]:
    """Matched link rows as ``Edge``s (an unmatched row has no original)."""
    rows = (
        link.filter(F.col(_LINK_ORIGINAL).isNotNull())
        .select(
            F.trim(F.col(_LINK_ACCOUNT).cast("string")).alias("account"),
            F.trim(F.col(_LINK_ORIGINAL).cast("string")).alias("original"),
            F.greatest(
                F.col("restr_flagged_date").cast("date"),
                F.col("orig_close_date").cast("date"),
            ).alias("known"),
            "match_type",
            F.col("candidate_count").cast("int").alias("candidates"),
        )
        .collect()
    )
    return [Edge(*r) for r in rows]


def build_rl_full_history_linked(
    crx_rl_full_history: DataFrame,
    int_loan_master: DataFrame,
    int_loan_restructure_link: DataFrame,
) -> tuple[DataFrame, DataFrame]:
    """Every spine account's history, with each matched restructured account's original
    loans re-keyed in front of its own months.

    Original rows: closed months dropped (their zero DPD would fake a cure), the worst
    bucket per month across originals, the account's own row kept where months overlap.

    Returns:
        crx_rl_full_history_linked: account_id, month_end_date, dlq_bucket.
        crx_rl_restructure_chains: one row per chain: account_id, chain_known_date,
        chain_n_originals, chain_match_type, chain_candidate_count, chain_months_added.
    """
    require_columns(
        int_loan_restructure_link,
        (
            _LINK_ACCOUNT,
            _LINK_ORIGINAL,
            "restr_flagged_date",
            "orig_close_date",
            "match_type",
            "candidate_count",
        ),
        "int_loan_restructure_link",
    )
    require_columns(
        int_loan_master,
        (
            "account_id",
            "observation_date",
            "dpd_bucket",
            "account_status",
        ),
        "int_loan_master",
    )
    own = crx_rl_full_history.select(
        "account_id",
        F.last_day("month_end_date").alias("month_end_date"),
        "dlq_bucket",
    )
    accounts = [r[0] for r in own.select("account_id").distinct().collect()]
    chains, members = resolve_chains(_edges(int_loan_restructure_link), accounts)
    spark = crx_rl_full_history.sparkSession
    chain_df = spark.createDataFrame([tuple(c) for c in chains], _CHAIN_SCHEMA)
    member_df = spark.createDataFrame([tuple(m) for m in members], _MEMBER_SCHEMA)

    original = (
        int_loan_master.select(
            F.trim(F.col("account_id").cast("string")).alias("original_id"),
            F.last_day(F.col("observation_date").cast("date")).alias("month_end_date"),
            F.col("dpd_bucket").cast("int").alias("dlq_bucket"),
            F.upper(F.col("account_status")).alias("_status"),
        )
        .join(F.broadcast(member_df), on="original_id")
        .filter(F.coalesce(F.col("_status"), F.lit("")) != "CLOSED")
        .groupBy("account_id", "month_end_date")
        .agg(F.max("dlq_bucket").alias("dlq_bucket"))
        .join(own, on=["account_id", "month_end_date"], how="left_anti")
    )
    added = original.groupBy("account_id").agg(
        F.count(F.lit(1)).cast("int").alias("chain_months_added")
    )
    chain_out = chain_df.join(added, on="account_id", how="left").withColumn(
        "chain_months_added", F.coalesce("chain_months_added", F.lit(0))
    )
    return own.unionByName(original), chain_out


def _history(full_history: DataFrame) -> DataFrame:
    return full_history.select(
        "account_id",
        F.col("month_end_date").alias("obs_date"),
        "dlq_bucket",
    )


def _restructured(feature_retail_loans: DataFrame) -> DataFrame:
    """One row per account: 1 if ``has_restructured_loan_flag`` is ever set."""
    require_columns(
        feature_retail_loans,
        ("account_id", "has_restructured_loan_flag"),
        "feature_retail_loans",
    )
    return feature_retail_loans.groupBy(
        F.trim(F.col("account_id").cast("string")).alias("account_id")
    ).agg(
        F.max(F.col("has_restructured_loan_flag").cast("int")).alias(
            "restructure_blind_spot_flag"
        )
    )


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (the loan is restructured)."""
    return build_dpd_sequences(
        _history(crx_rl_full_history),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans),
    )


def build_rl_linked_dpd_sequences(
    crx_rl_full_history_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """As build_rl_dpd_sequences on the linked history: an account with the original
    loans' months in front of its own is no longer a blind spot."""
    stitched = crx_rl_restructure_chains.filter(F.col("chain_months_added") > 0).select(
        "account_id"
    )
    return build_dpd_sequences(
        _history(crx_rl_full_history_linked),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans).join(
            F.broadcast(stitched), on="account_id", how="left_anti"
        ),
    )


def build_rl_a4_deterioration(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    crx_rl_dpd_sequences: DataFrame,
    crx_rl_dpd_sequences_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here.

    A row before its chain's ``chain_known_date`` reads the account's own history, every
    other row the linked one. Adds the ``chain_*`` columns of crx_rl_restructure_chains
    and chain_stitched_flag (1 if this row's history has the original loans' months)."""
    params = journey_params(crx_persona, RL, model_id)
    chains = F.broadcast(crx_rl_restructure_chains)
    spine = rl_spine.select(
        F.trim(F.col("account_id").cast("string")).alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
    ).join(chains.select("account_id", "chain_known_date"), on="account_id", how="left")
    before_chain = F.coalesce(
        F.col("observation_date") < F.col("chain_known_date"), F.lit(False)
    )
    keys = ("account_id", "observation_date")
    out = build_deterioration(
        crx_rl_dpd_sequences_linked,
        RL,
        params,
        spine.filter(~before_chain).select(*keys),
        log_states=False,
    ).unionByName(
        build_deterioration(
            crx_rl_dpd_sequences,
            RL,
            params,
            spine.filter(before_chain).select(*keys),
            log_states=False,
        )
    )
    out = out.join(chains, on="account_id", how="left").withColumn(
        "chain_stitched_flag",
        F.coalesce(
            (F.col("observation_date") >= F.col("chain_known_date"))
            & (F.col("chain_months_added") > 0),
            F.lit(False),
        ).cast("int"),
    )
    _log_state_stats(out, params.end_date, RL, params)
    return out
