"""Spark side: scoping, the history floor, and ONE shuffle that gathers each account's
monthly buckets into an array; the per-account core (history.py/states.py) then runs inside
the UDFs. Two stages (two Kedro nodes per product):

build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features
"""

from __future__ import annotations

import logging
import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.nodes.staging.retail_loans.stg_rr_portf import (
    ECL_WINNOWED_PRODUCT_CODES,
)

from ._dates import _month_col, _month_idx
from .constants import BucketScheme
from .history import build_history
from .logging import _log_sequence_stats, _log_state_stats
from .params import JourneyParams
from .states import DISPLAY_NAMES, classify

LOG = logging.getLogger(__name__)

_PACKAGE = __name__.rsplit(".", 1)[0]
_SUBMODULES = (
    "constants",
    "params",
    "_dates",
    "core",
    "states",
    "history",
    "spark",
    "logging",
)


def _ship_by_value() -> None:
    """Pickle every module of this package BY VALUE into the UDFs, so executors do not need
    the Kedro project installed (cloudpickle >= 2.0, bundled with PySpark >= 3.3). UDF
    closures reach build_history (history.py) and classify (states.py), not only this module
    — registering only this module (as the flat _dpd_journey.py once did) would leave those
    on pickle-by-reference, which only "works" locally (shared sys.path) and breaks on a
    real executor. If the project is installed on the executors this is harmless."""
    try:
        from pyspark import cloudpickle  # pylint: disable=import-outside-toplevel

        if not hasattr(cloudpickle, "register_pickle_by_value"):
            return  # pragma: no cover — older PySpark
        for name in (_PACKAGE, *(f"{_PACKAGE}.{m}" for m in _SUBMODULES)):
            mod = sys.modules.get(name)
            if mod is not None:
                cloudpickle.register_pickle_by_value(mod)
    except (
        Exception  # pylint: disable=broad-exception-caught
    ) as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning(
            "could not register %s for pickle-by-value (%s); the package must be "
            "importable on the executors",
            _PACKAGE,
            exc,
        )


_HISTORY_SCHEMA = T.StructType(
    [
        T.StructField("build_status", T.StringType()),
        T.StructField("first_month_idx", T.IntegerType()),
        T.StructField("last_month_idx", T.IntegerType()),
        T.StructField("buckets", T.ArrayType(T.IntegerType())),
        T.StructField("history_cropped", T.BooleanType()),
        T.StructField("n_gap_months_filled", T.IntegerType()),
        T.StructField("n_gap_months_rolled", T.IntegerType()),
        T.StructField("n_gap_months_inferred", T.IntegerType()),
        T.StructField("n_cycle_shift_moves", T.IntegerType()),
        T.StructField("legacy_drop", T.BooleanType()),
        T.StructField("n_months_truncated", T.IntegerType()),
        T.StructField("n_dup_month_rows", T.IntegerType()),
    ]
)

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None),
    ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()),
    ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()),
    ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()),
    ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()),
    ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()),
    ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()),
    ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType(
    [T.StructField("det_state", T.StringType())]
    + [T.StructField(n, t) for n, t in _FEATURES if t is not None]
)


def _string_key(df: DataFrame, col: str = "account_id") -> F.Column:
    """Safe string-cast join key — a Double/Decimal account_id cast straight to string
    renders as "1.23456789E8" and silently zeroes an == join. Same helper as
    rl_full_history/nodes.py._string_key (R18 — duplicated, not imported: that is a
    private helper in an unrelated pipeline module with no stability contract)."""
    dtype = df.schema[col].dataType
    c = F.col(col)
    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
        c = c.cast("long")
    return F.trim(c.cast("string"))


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(
        F.expr(f"make_date(cast({c} div 12 as int), cast({c} % 12 + 1 as int), 1)")
    )


# pylint: disable-next=too-many-locals
def build_dpd_sequences(
    history: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    restructure: DataFrame | None = None,
) -> DataFrame:
    """history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
    optionally restructure_flag (0/1 per row; max over the account's rows), optionally
    disbursement_date (date; max over the account's rows, robust to nulls elsewhere),
    optionally product_code (string; max over the account's rows, robust to nulls
    elsewhere).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag,
        ecl_gap_blind_spot_flag (1 if disbursement_date AND product_code are both present,
        params.ecl_gap_cutoff_date is set, the account disbursed before that cutoff, and its
        product_code is NOT one of ECL_WINNOWED_PRODUCT_CODES -- the pre-cutoff ECL
        historical extract is structurally winnowed server-side to those codes only, so a
        loan outside that set is genuinely, structurally absent from it regardless of
        disbursement date (confirmed root cause, RL-A4-5/RL-A4-6/RL-A4-8); 0 otherwise/when
        a required column or the param is absent, e.g. CC, which has neither column)
    """
    missing = [
        c for c in ("account_id", "obs_date", "dlq_bucket") if c not in history.columns
    ]
    if missing:
        raise ValueError(
            f"build_dpd_sequences: history is missing {missing}; has {sorted(history.columns)}"
        )
    _ship_by_value()
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None

    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(
            F.when(
                in_window,
                F.struct(
                    m.alias("m"),
                    F.datediff(
                        F.col("obs_date").cast("date"), F.lit("1970-01-01")
                    ).alias("d"),
                    bucket.alias("b"),
                ),
            )
        ).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias(
            "n_invalid_rows"
        ),  # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    has_ecl_gap_check = (
        "disbursement_date" in history.columns
        and "product_code" in history.columns
        and params.ecl_gap_cutoff_date
    )
    if has_ecl_gap_check:
        aggs.append(F.max(F.col("disbursement_date").cast("date")).alias("_disb_date"))
        aggs.append(
            F.max(F.trim(F.col("product_code").cast("string"))).alias("_product_code")
        )
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    per_acc = per_acc.crossJoin(F.broadcast(source_min))

    if has_ecl_gap_check:
        covered = list(ECL_WINNOWED_PRODUCT_CODES)
        per_acc = per_acc.withColumn(
            "_ecl_gap_blind_spot",
            (
                F.col("_disb_date").isNotNull()
                & (F.col("_disb_date") < F.lit(params.ecl_gap_cutoff_date).cast("date"))
                & F.col("_product_code").isNotNull()
                & (~F.col("_product_code").isin(covered))
            ).cast("int"),
        )
    else:
        per_acc = per_acc.withColumn("_ecl_gap_blind_spot", F.lit(0))

    offset, fill, how = (
        scheme.offset,
        params.fill_straight_roll_gaps,
        params.on_unresolvable_gap,
    )
    shift, max_inf = params.repair_cycle_shift, params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history(
            [(r["m"], r["d"], r["b"]) for r in rows],
            first_raw,
            global_min,
            offset,
            fill,
            how,
            shift,
            max_inf,
        )

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias(
            "dpd_string"
        ),
        F.col("_h.history_cropped").alias("history_cropped"),
        F.coalesce("_h.n_gap_months_filled", F.lit(0)).alias("n_gap_months_filled"),
        F.coalesce("_h.n_gap_months_rolled", F.lit(0)).alias("n_gap_months_rolled"),
        F.coalesce("_h.n_gap_months_inferred", F.lit(0)).alias("n_gap_months_inferred"),
        F.coalesce("_h.n_cycle_shift_moves", F.lit(0)).alias("n_cycle_shift_moves"),
        F.coalesce("_h.legacy_drop", F.lit(False)).alias("legacy_drop"),
        F.coalesce("_h.n_months_truncated", F.lit(0)).alias("n_months_truncated"),
        F.coalesce("_h.n_dup_month_rows", F.lit(0)).alias("n_dup_month_rows"),
        F.col("n_invalid_rows").cast("int"),
        (F.col("_rf") if "_rf" in s.columns else F.lit(None).cast("int")).alias("_rf"),
        F.col("_ecl_gap_blind_spot").alias("ecl_gap_blind_spot_flag"),
    )
    if restructure is not None:
        out = out.join(
            restructure.select(
                "account_id", F.col("restructure_blind_spot_flag").alias("_rs")
            ),
            "account_id",
            "left",
        )
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop(
        "_rf", "_rs"
    )
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


# pylint: disable-next=too-many-locals
def build_deterioration(
    sequences: DataFrame, scheme: BucketScheme, params: JourneyParams, spine: DataFrame
) -> DataFrame:
    """sequences: output of build_dpd_sequences (one row per account). spine: 2-column
    (account_id, observation_date) — one row per point-in-time state to classify, e.g.
    cc_spine/rl_spine already filtered to the run's model_id/DLQ-band scope. Classifies
    EVERY spine row, not one row per account: each row's billing history is the account's
    Stage 1 dlq_buckets array truncated up to and including that row's own month, run
    through the same, unmodified classify() engine.

    A spine row is kept only if its month falls inside the account's observed/gap-filled
    window (first_month..last_month) and the truncated bucket is itself delinquent
    (canonical >= 2) — both explainable "no billing history at this date" cases, not a
    silent drop. No model_id/segment bucket-set filter is applied here: that scoping is
    inherited for free from the spine's own population.

    Returns one row per (account_id, observation_date):
        account_id, observation_date, det_state, det_state_label, det_segment,
        current_bucket (native, as of this row's date), <features>, history_months
        (months observed as of this row), history_cropped, n_months_truncated,
        restructure_blind_spot_flag, ecl_gap_blind_spot_flag, computed_at
    """
    _ship_by_value()
    segment = params.segment
    offset, top = scheme.offset, scheme.canon_top
    repair = scheme.repair_jumps
    end_dt = F.to_date(F.lit(params.end_date))

    seq = (
        sequences.where(F.col("build_status") == "ok")
        .withColumn("_first_idx", _month_col(F.col("first_month")))
        .withColumn("_last_idx", _month_col(F.col("last_month")))
        .withColumn("_key", _string_key(sequences, "account_id"))
    )

    sp = spine.where(F.col("observation_date").cast("date") <= end_dt).select(
        _string_key(spine, "account_id").alias("_key"),
        F.col("observation_date").cast("date").alias("observation_date"),
    )

    # join on the safe string key only — account_id in the output keeps seq's own
    # native type (long for CC, string for RL), never the stringified join key.
    joined = sp.join(seq, "_key", "inner")
    obs_idx = _month_col(F.col("observation_date"))
    trunc_len = (obs_idx - F.col("_first_idx") + 1).cast("int")
    joined = (
        joined.withColumn("_obs_idx", obs_idx)
        .withColumn("_trunc_len", trunc_len)
        .where((F.col("_trunc_len") >= 1) & (F.col("_obs_idx") <= F.col("_last_idx")))
    )

    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot, ecl_gap_blind_spot):
        sl = list(buckets)[:trunc_len_]
        if not sl or max(sl[-1] + offset, 1) < 2:
            return None
        return classify(
            sl,
            bool(cropped),
            offset,
            top,
            repair,
            bool(restructure_blind_spot),
            bool(ecl_gap_blind_spot),
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema)(
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
            "ecl_gap_blind_spot_flag",
        ),
    ).where(F.col("_s").isNotNull())

    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    feat_cols = [
        F.col(f"_s.{f.name}").alias(f.name)
        for f in schema.fields
        if f.name != "det_state"
    ]
    out = res.select(
        F.col("account_id"),
        F.col("observation_date"),
        F.col("_s.det_state").alias("det_state"),
        labels[F.col("_s.det_state")].alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        F.element_at("dlq_buckets", F.col("_trunc_len")).alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("_trunc_len").alias("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        F.col("restructure_blind_spot_flag"),
        F.col("ecl_gap_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always-on, like every other persona axis's own state-distribution log
    # (cc_a2_locatability_v2/cc_a3_payment_credibility's own _log_*_stats) — not
    # gated behind log_stats, which here only controls the heavier Stage 1
    # build_dpd_sequences telemetry above. The month filter inside _log_state_stats
    # pushes down through the join, so this does not force materialization of the
    # full point-in-time result.
    _log_state_stats(out, params.end_date, scheme, params)
    return out
