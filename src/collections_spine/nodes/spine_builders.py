"""DLQ contract-spine builder, refactored for selectivity-first execution.

Goal: produce ``dlq_spine = (contract_idt, observation_date)`` for contracts in
DLQ buckets ``[dlq_min, dlq_max]`` at each billing observation date, over a
~billion-row SCD2 ``contract`` table and a ~billion-row daily ``billing`` table,
when the real target universe is only a few hundred thousand contracts.

Why the old single-function version was slow
--------------------------------------------
It built ``billing.distinct()`` over the WHOLE portfolio (a multi-billion-row
shuffle), joined the billion-row contract table to that full spine, and only then
applied the DLQ filter -- the one operation that collapses the universe. The most
selective filter ran last, on fully-expanded data.

Selectivity-first plan
-----------------------
1. ``slim_contract``       -- one narrow scan; parse DLQ_HIST once; window-prune.
2. ``dlq_candidate_ids``   -- contracts that EVER hit DLQ in range (superset,
                              ~few hundred k) -- broadcastable.
3. ``build_billing_spine`` -- prune the daily ``edp_load_date`` PARTITION;
                              semi-join candidates *before* the distinct.
4. ``contract_pit``        -- point-in-time active version via an exact-match
                              fast path + tiny as-of fallback (see below).
5. ``dlq_spine``           -- precise DLQ filter on the point-in-time version.

This table is "latest-record_date_from-wins" (record_date_to is always the
2100-01-01 sentinel), so the active version at an observation date is the one
with the greatest ``record_date_from <= obs`` -- NOT the one with the greatest
``edp_modifiedts``. The generic interval-based ``prefilter_scd2`` dedups by
``date_modified`` first and would pick a stale version when an old start gets a
late restatement; ``contract_pit`` below orders by ``record_date_from`` first and
treats ``edp_modifiedts`` only as the restatement tie-break (and as the
no-leakage knowledge cutoff: ``edp_modifiedts <= observation_date``).

Persist every intermediate to HDFS (see the catalog snippet in the package
README) so reruns read narrow parquet instead of re-scanning billions of rows.
"""

from src.collections_spine import Scd2Schema
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

#: Contract table's SCD2 column names. record_date_to is always the estate
#: 2100-01-01 sentinel, so selection is latest-record_date_from-wins.
_CONTRACT_SCD2 = Scd2Schema(
    key="contract_idt",
    eff_start="record_date_from",
    eff_end="record_date_to",
    modified="edp_modifiedts",
)

_DLQ_PATTERN = r"DLQ_HIST=([^;]+)"


def _dlq_bounds(modelling: dict) -> tuple[int, int]:
    scope = modelling.get("scope_filtering", {})
    return scope.get("dlq_min", 4), scope.get("dlq_max", 7)


def _parse_dlq_hist(add_info: Column) -> Column:
    """Extract integer DLQ_HIST from the free-text ``add_info`` field.

    ``regexp_extract`` returns ``''`` (not NULL) on no match, so the original
    ``isNotNull()`` guard was always true and ``''.cast(int)`` silently became
    NULL. Guard on a numeric match; treat missing/non-numeric as 0.
    """
    raw = F.regexp_extract(add_info, _DLQ_PATTERN, 1)
    return F.when(raw.rlike(r"^\d+$"), raw.cast("int")).otherwise(F.lit(0)).alias("dlq_hist")


# --------------------------------------------------------------------------- #
# 1. one narrow, DLQ-parsed scan of the contract table  (persist + reuse)
# --------------------------------------------------------------------------- #
def slim_contract(raw_stg_contract: DataFrame, modelling: dict) -> DataFrame:
    """Project contract to needed columns, parse DLQ once, window-prune.

    The single unavoidable billion-row scan. ``edp_modifiedts`` is cast to a date
    so a same-day correction counts as known at the observation date.
    """
    s = _CONTRACT_SCD2
    df = raw_stg_contract.select(
        F.col(s.key),
        F.col(s.eff_start).cast(DateType()).alias(s.eff_start),
        F.col(s.eff_end).cast(DateType()).alias(s.eff_end),
        F.col(s.modified).cast(DateType()).alias(s.modified),
        _parse_dlq_hist(F.col("add_info")),
    )
    # With a sentinel end this only drops future-dated starts; the heavy
    # historical-tail pruning happens per-candidate in contract_pit (anchor prune).
    return df.where(F.col(s.eff_start) <= F.lit(modelling["end_date"]))


# --------------------------------------------------------------------------- #
# 2. the DLQ universe (superset of contract ids) -- small, broadcastable
# --------------------------------------------------------------------------- #
def dlq_candidate_ids(contract_slim: DataFrame, modelling: dict) -> DataFrame:
    """Distinct contract_idt with ANY version in the DLQ band.

    Deliberately a superset; the precise per-pair DLQ test happens in dlq_spine
    on the point-in-time-active version. Pre-filtering versions before the PIT
    selection would create false positives when a restatement moves DLQ out of
    range. ~few hundred k rows -> broadcast downstream.
    """
    lo, hi = _dlq_bounds(modelling)
    return (
        contract_slim
        .where(F.col("dlq_hist").between(lo, hi))
        .select("contract_idt")
        .distinct()
    )


# --------------------------------------------------------------------------- #
# 3. billing spine -- prune the load_date PARTITION, then candidate-restrict
# --------------------------------------------------------------------------- #
def build_billing_spine(
    raw_stg_billing: DataFrame,
    dlq_candidate_ids: DataFrame,
    modelling: dict,
) -> DataFrame:
    """Collapse billing to distinct (contract_idt, observation_date) pairs.

    The table is partitioned on a daily ``edp_load_date``, so we prune on THAT
    (the ``billing_date`` filter alone prunes no files). A billing_date persists across
    its whole cycle, appearing in load partitions roughly ``[billing_date,
    billing_date + cycle]``; to capture every billing_date in the modelling window
    we read load partitions in ``[start, end + cycle_buffer_days]``.

    The candidate semi-join runs *before* the distinct, so the daily duplication
    is collapsed only for the few hundred k in-scope contracts -- not the
    universe. That is the change that removes the original portfolio-wide shuffle.
    """
    start, end = modelling["start_date"], modelling["end_date"]
    load_col = modelling.get("billing_load_date_col", "edp_load_date")
    buffer = modelling.get("billing_cycle_buffer_days", 35)

    billing = (
        raw_stg_billing
        # partition pruning on the daily load_date
        .where(F.col(load_col).between(F.lit(start), F.date_add(F.lit(end), buffer)))
        .select(
            "contract_idt",
            F.col("billing_date").cast(DateType()).alias("observation_date"),
        )
        .where(F.col("observation_date").between(F.lit(start), F.lit(end)))
    )

    return (
        billing
        .join(F.broadcast(dlq_candidate_ids), "contract_idt", "leftsemi")
        .distinct()
    )


# --------------------------------------------------------------------------- #
# 4. point-in-time active contract version  (exact fast path + as-of fallback)
# --------------------------------------------------------------------------- #
def contract_pit(
    contract_slim: DataFrame,
    billing_spine: DataFrame,
    modelling: dict,
) -> DataFrame:
    """One active contract version per spine pair, latest-start-wins, no leakage.

    * Restrict contract to the spine's contracts (broadcast key set).
    * Anchor-prune: per contract keep only versions with ``record_date_from`` on
      or after the latest start <= modelling start; older versions are
      permanently superseded and can never be active in the window.
    * Fast path (~99.9%): composite equi-join on
      ``(contract_idt, record_date_from == observation_date)`` -- a hash join
      instead of an interval scan.
    * Fallback (~0.1%): for pairs with no exact start, as-of pick the latest
      ``record_date_from <= observation_date``. Runs on the tiny residual only.

    Both paths enforce ``edp_modifiedts <= observation_date`` (no future
    restatement leakage) and tie-break restatements by latest ``edp_modifiedts``.
    """
    s = _CONTRACT_SCD2
    cidt, cfrom, cto, cmod = s.key, s.eff_start, s.eff_end, s.modified
    start = modelling["start_date"]
    payload = [cidt, "observation_date", cfrom, cto, cmod, "dlq_hist"]

    keys = billing_spine.select(cidt).distinct()
    cand = contract_slim.join(F.broadcast(keys), cidt, "leftsemi")

    # anchor prune (point 2): drop versions older than the window's active start
    anchor = F.max(F.when(F.col(cfrom) <= F.lit(start), F.col(cfrom))).over(Window.partitionBy(cidt))
    cand = (
        cand.withColumn("_anchor", anchor)
        .where(F.col("_anchor").isNull() | (F.col(cfrom) >= F.col("_anchor")))
        .drop("_anchor")
    )

    spine = billing_spine.select(cidt, "observation_date")

    # fast path (point 3): exact record_date_from == observation_date
    exact = (
        cand.withColumn("observation_date", F.col(cfrom))
        .join(spine, [cidt, "observation_date"], "inner")
        .where(F.col(cmod) <= F.col("observation_date"))
    )
    w_rest = Window.partitionBy(cidt, "observation_date").orderBy(
        F.col(cmod).desc(), F.col(cto).desc()
    )
    exact = (
        exact.withColumn("_rn", F.row_number().over(w_rest))
        .where(F.col("_rn") == 1)
        .select(*payload)
    )

    # as-of fallback for the residual pairs (no known exact-start version)
    residual = spine.join(exact.select(cidt, "observation_date"), [cidt, "observation_date"], "leftanti")
    fb = (
        cand.join(residual, cidt, "inner")
        .where((F.col(cfrom) <= F.col("observation_date")) & (F.col(cmod) <= F.col("observation_date")))
    )
    w_asof = Window.partitionBy(cidt, "observation_date").orderBy(
        F.col(cfrom).desc(), F.col(cmod).desc(), F.col(cto).desc()
    )
    fb = (
        fb.withColumn("_rn", F.row_number().over(w_asof))
        .where(F.col("_rn") == 1)
        .select(*payload)
    )

    return exact.unionByName(fb)


# --------------------------------------------------------------------------- #
# 5. precise DLQ filter on the point-in-time version -> final spine
# --------------------------------------------------------------------------- #
def dlq_spine(contract_pit: DataFrame, modelling: dict) -> DataFrame:
    """Keep pairs whose point-in-time-active version is in the DLQ band."""
    lo, hi = _dlq_bounds(modelling)
    return (
        contract_pit
        .where(F.col("dlq_hist").between(lo, hi))
        .select("contract_idt", "observation_date")
        .distinct()
    )
