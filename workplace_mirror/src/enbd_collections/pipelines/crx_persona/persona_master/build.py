"""The persona master: every axis state and its signals on one row per observation,
plus the exposure and the persona layer (segment, contact route, journey group)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    log_latest_month,
    pit_latest,
    require_columns,
    segment,
    string_key,
)
from .constants import (
    ABILITY_BAND,
    AXIS_DROP,
    CREDIBILITY_BAND,
    DECEASED_SEGMENT,
    JOURNEY_GROUP,
    ROUTE_ABROAD,
    ROUTE_DECEASED,
    ROUTE_GONE_DARK,
    ROUTE_REACHABLE,
    ROUTE_UNCONFIRMED,
    SEGMENTS,
)

# A snapshot outside the observation month is stale: no exposure.
_SNAPSHOT_MAX_AGE_M = 1
PERSONA_COLUMNS = (
    "persona_segment",
    "persona_contact_route",
    "persona_journey_group",
    "persona_ability_band",
    "persona_credibility_band",
)
_AXIS_STATES = {
    "a1": "a1_state",
    "a2": "a2_state",
    "a3": "a3_state",
    "a4": "det_state",
}


def build_cc_exposure(obs_base: DataFrame, balance: DataFrame) -> DataFrame:
    """``GRAIN``, ``product`` ("credit_card") and ``exposure_amt``: the statement
    balance on the latest ``crx_cc_balance`` snapshot in the observation month."""
    require_columns(
        balance, ["contract_id", "observation_date", "stmt_balance"], "balance"
    )
    src = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("stmt_balance").cast("double").alias("exposure_amt"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["exposure_amt"],
        inclusive=True,
        max_age_months=_SNAPSHOT_MAX_AGE_M,
    )
    return obs_base.select(*GRAIN, F.lit("credit_card").alias("product")).join(
        latest, on=list(GRAIN), how="left"
    )


def build_rl_exposure(obs_base: DataFrame, full_history: DataFrame) -> DataFrame:
    """``GRAIN``, ``product`` (the loan type) and ``exposure_amt``: the outstanding
    balance on the loan's ``crx_rl_full_history`` month in the observation month."""
    require_columns(
        full_history,
        ["account_id", "month_end_date", "outstanding_balance", "loan_type"],
        "full_history",
    )
    src = full_history.select(
        string_key(full_history).alias("account_id"),
        F.col("month_end_date").cast("date").alias("snapshot_date"),
        F.col("loan_type").cast("string").alias("product"),
        F.col("outstanding_balance").cast("double").alias("exposure_amt"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["product", "exposure_amt"],
        inclusive=True,
        max_age_months=_SNAPSHOT_MAX_AGE_M,
    )
    return left_join_all(obs_base, [latest])


def _mapped(key: Column, mapping: dict, default: str) -> Column:
    """``mapping[key]``; a key outside it, or NULL (the axis has no row), is
    ``default``."""
    pairs = [F.lit(x) for kv in mapping.items() for x in kv]
    return F.coalesce(F.create_map(*pairs)[key], F.lit(default))


def _contact_route() -> Column:
    return (
        F.when(F.col("deceased_flag") == 1, ROUTE_DECEASED)
        .when(F.col("location_state") == "skip", ROUTE_ABROAD)
        .when(F.col("reachability_state") == "non_reachable", ROUTE_GONE_DARK)
        .when(F.col("reachability_state") == "reachable", ROUTE_REACHABLE)
        .otherwise(ROUTE_UNCONFIRMED)
    )


def _axis(df: DataFrame, name: str) -> DataFrame:
    require_columns(df, [*GRAIN, _AXIS_STATES[name]], name)
    return df.drop(*AXIS_DROP)


def _a4_in_month(obs_base: DataFrame, a4: DataFrame) -> DataFrame:
    """A4 on the base grain: the latest A4 row on or before the observation date in its
    month (CC A4 rows carry the spine's billing dates), its date kept as ``a4_date``."""
    values = [c for c in a4.columns if c not in GRAIN]
    src = a4.select(
        string_key(a4).alias("account_id"),
        F.col("observation_date").cast("date").alias("a4_date"),
        *values,
    )
    return pit_latest(
        obs_base,
        src.withColumn("_d", F.col("a4_date")),
        key="account_id",
        date_col="_d",
        value_cols=["a4_date", *values],
        inclusive=True,
        max_age_months=_SNAPSHOT_MAX_AGE_M,
    )


def _persona_layer(df: DataFrame) -> DataFrame:
    """The bands, segment, contact route and journey group of the joined axes."""
    df = (
        df.withColumn("deceased_flag", F.coalesce(F.col("deceased_flag"), F.lit(0)))
        .withColumn(
            "persona_ability_band", _mapped(F.col("a1_state"), ABILITY_BAND, "unseen")
        )
        .withColumn(
            "persona_credibility_band",
            _mapped(F.col("a3_state"), CREDIBILITY_BAND, "unseen"),
        )
    )
    cells = {f"{a}|{c}": seg for (a, c), seg in SEGMENTS.items()}
    cell = F.concat_ws("|", "persona_ability_band", "persona_credibility_band")
    df = (
        df.withColumn(
            "persona_segment",
            F.when(F.col("deceased_flag") == 1, DECEASED_SEGMENT).otherwise(
                _mapped(cell, cells, "no_evidence")
            ),
        )
        .withColumn("persona_contact_route", _contact_route())
        .withColumn(
            "persona_journey_group",
            _mapped(F.col("det_state"), JOURNEY_GROUP, "unknown"),
        )
    )
    return df


def build_persona_master(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    exposure: DataFrame,
    a1: DataFrame,
    a2: DataFrame,
    a3: DataFrame,
    a4: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation-base row: ``GRAIN``, ``cif_id``, ``model_id``,
    ``segment``, ``product``, ``exposure_amt``, every column of the four axis outputs
    (as written; A4 from its latest row in the observation month, dated ``a4_date``),
    and the persona layer:

    - ``persona_ability_band`` (A1) and ``persona_credibility_band`` (A3): ``able`` /
      ``unable`` / ``unseen``, ``credible`` / ``not_credible`` / ``unseen``;
    - ``persona_segment``: the cell of the two bands, ``deceased`` overriding;
    - ``persona_contact_route`` (A2): ``deceased``, ``abroad``, ``gone_dark``,
      ``reachable`` or ``unconfirmed``;
    - ``persona_journey_group`` (A4): ``never_settled``, ``sudden_stop``,
      ``recurring``, ``partial_payer`` or ``unknown``.

    A row an axis did not classify keeps NULL axis columns and ``unseen`` /
    ``unknown`` in the persona layer. Two axes sharing a column name stop the run.
    """
    a4 = _a4_in_month(obs_base, _axis(a4, "a4"))
    axes = [_axis(a, n) for a, n in ((a1, "a1"), (a2, "a2"), (a3, "a3"))] + [a4]
    parts = [exposure, *axes]
    names = [c for part in parts for c in part.columns if c not in GRAIN]
    clashes = sorted({c for c in names if names.count(c) > 1})
    if clashes:
        raise ValueError(f"axis outputs share columns {clashes}")
    df = left_join_all(obs_base, parts).join(
        obs_base.select(*GRAIN, "cif_id"), on=list(GRAIN), how="left"
    )
    df = _persona_layer(df)
    out = df.select(
        *GRAIN,
        "cif_id",
        F.lit(model_id).alias("model_id"),
        F.lit(segment(model_id)).alias("segment"),
        "product",
        "exposure_amt",
        *PERSONA_COLUMNS,
        *[
            c
            for c in df.columns
            if c not in {*GRAIN, "cif_id", "product", "exposure_amt", *PERSONA_COLUMNS}
        ],
        F.current_timestamp().alias("computed_at"),
    )
    for col in ("persona_segment", "persona_contact_route"):
        log_latest_month(out, col, f"persona_master [{model_id}]", persona_end_date)
    return out
