"""A2 locatability state: location × reachability, with a deceased override.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md`` §6.

    a2_state = deceased                              if any deceased source
             = <location_state>__<reachability_state> otherwise (9 values)

Both dimensions are kept on every row, deceased included, so each can be used alone.
"""

from __future__ import annotations

from itertools import chain

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .signals import LOCATION_EVIDENCE

LOCATION_LABELS = {"skip": "Skip", "in_country": "In Country", "unknown": "Unknown"}
REACHABILITY_LABELS = {
    "reachable": "Reachable",
    "non_reachable": "Non-Reachable",
    "unknown": "Unknown",
}
_OUTPUT = [
    *GRAIN,
    "a2_state",
    "a2_state_label",
    "location_state",
    "reachability_state",
    "deceased_flag",
    "deceased_source",
    "location_rule",
    "location_unknown_reason",
    *LOCATION_EVIDENCE,
    "reachability_unknown_reason",
    "last_contact_date",
    "last_attempt_date",
    "attempt_days_in_window",
    "last_skip_trace_date",
]


def _label(col: str, labels: dict[str, str]) -> Column:
    return F.create_map(*[F.lit(x) for x in chain(*labels.items())])[F.col(col)]


def build_a2_locatability(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    location: DataFrame,
    dcore: DataFrame,
    way4_deceased: DataFrame,
    demographics_deceased: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation: the A2 state, its label, both dimensions, the deceased
    flag with its sources (``dcore``, ``way4``, ``demographics``) and the diagnostics.
    """
    df = left_join_all(
        obs_base, [location, dcore, way4_deceased, demographics_deceased]
    ).fillna(0, subset=["way4_deceased_flag", "demographics_deceased_flag"])
    sources = F.concat_ws(
        ",",
        F.when(F.col("dcore_deceased_date").isNotNull(), F.lit("dcore")),
        F.when(F.col("way4_deceased_flag") == 1, F.lit("way4")),
        F.when(F.col("demographics_deceased_flag") == 1, F.lit("demographics")),
    )
    deceased = F.col("deceased_flag") == 1
    out = (
        df.withColumn("deceased_source", F.when(sources != "", sources))
        .withColumn("deceased_flag", F.col("deceased_source").isNotNull().cast("int"))
        .withColumn(
            "a2_state",
            F.when(deceased, "deceased").otherwise(
                F.concat_ws("__", "location_state", "reachability_state")
            ),
        )
        .withColumn(
            "a2_state_label",
            F.when(deceased, "Deceased").otherwise(
                F.concat_ws(
                    " – ",
                    _label("location_state", LOCATION_LABELS),
                    _label("reachability_state", REACHABILITY_LABELS),
                )
            ),
        )
        .select(*_OUTPUT)
    )
    log_latest_month(out, "a2_state", f"a2_locatability [{model_id}]", persona_end_date)
    return out
