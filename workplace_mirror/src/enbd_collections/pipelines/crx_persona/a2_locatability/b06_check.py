"""TEMPORARY (mirror bundle 06): the old A2 vs the new engine, run in PROD.

Log blocks, aggregates only:

* ``compare_a2_outputs`` (``B06 OUTPUT``): the old output (``crx_<p>_a2_locatability``)
  against the new one (``crx_<p>_a2_locatability_b06_check``) in the latest month — an
  old row is matched to the new row of the same account and month (the month's latest
  old observation) — plus the new location / reachability shares per month.
* ``describe_a2_rules`` (``B06 RULES``): which rule fires, which source holds the
  deciding evidence, unknown reasons, call days, deceased sources.
* ``describe_debit_evidence`` (``B06 DEBIT``): the base customers' rows in
  ``prm_casa_card_transactions`` by month, channel / type and place (the Offline → Machine
  change, ATM placement), and their ``reason_for_excluding`` values.
* ``split_by_product`` (``B06 PRODUCT``, RL only): the latest month by ``loan_type``.
* ``explain_reachability`` (``B06 REACH``): reachability rebuilt under the earlier rule,
  then each change in turn, with the moves at every step.

Removed by the bundle's cleanup.
"""

import logging
from itertools import pairwise

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_uae

from .._common import GRAIN, window_months
from .codes import (
    CALL_CODES,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SUCCESS_CATEGORY,
)
from .signals import GONE_DARK_DAYS, _dcore_events

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B06 {name} START === [{model_id}]",
        *lines,
        f"=== B06 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<24}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _snake(col: str) -> F.Column:
    """'In Country' → 'in_country', 'Non-Reachable' → 'non_reachable'."""
    return F.regexp_replace(F.lower(F.trim(col)), "[ -]+", "_")


def compare_a2_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new in the latest month; new shares per month.

    The PROD old output may still carry the earlier single-state schema
    (``a2_state_v1``) instead of ``location_state`` / ``reachability_state``; the old
    side is compared on whichever it has.
    """
    latest_new = _latest_month(new)
    month = latest_new.agg(F.trunc(F.max("observation_date"), "month")).first()[0]
    in_month = Window.partitionBy("account_id").orderBy(
        F.col("observation_date").desc()
    )
    two_dim = "location_state" in old.columns
    old_cols = (
        [
            _snake("location_state").alias("old_location"),
            _snake("reachability_state").alias("old_reachability"),
        ]
        if two_dim
        else [_snake("a2_state_v1").alias("old_state")]
    )
    old_m = (
        old.filter(F.trunc("observation_date", "month") == F.lit(month))
        .withColumn("_rn", F.row_number().over(in_month))
        .filter(F.col("_rn") == 1)
        .select(F.col("account_id").cast("string").alias("account_id"), *old_cols)
        .withColumn("_old", F.lit(1))
    )
    both = latest_new.join(old_m, on="account_id", how="full")
    matched = both.filter(F.col("a2_state").isNotNull())
    if two_dim:
        compare = [
            "location old x new:",
            *_table(matched, "old_location", "location_state"),
            "reachability old x new:",
            *_table(matched, "old_reachability", "reachability_state"),
        ]
    else:
        compare = [
            "old a2_state_v1:",
            *_table(old_m, "old_state"),
            "old a2_state_v1 x new location:",
            *_table(matched, "old_state", "location_state"),
            "old a2_state_v1 x new reachability:",
            *_table(matched, "old_state", "reachability_state"),
        ]
    lines = [
        (
            f"month {month}: new rows {latest_new.count()}, old rows {old_m.count()}, "
            f"new only {both.filter(F.col('_old').isNull()).count()}, "
            f"old only {both.filter(F.col('a2_state').isNull()).count()}"
        ),
        "new a2_state:",
        *_table(latest_new, "a2_state"),
        *compare,
        "new location_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "location_state",
        ),
        "new reachability_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "reachability_state",
        ),
    ]
    _log("OUTPUT", model_id, lines)


def describe_a2_rules(new: DataFrame, model_id: str) -> None:
    """Rules, deciding sources, unknown reasons, call days and deceased sources in the
    latest month."""
    df = _latest_month(new)
    days = F.col("attempt_days_in_window")
    lines = [
        "location_rule x deciding source (L1: latest foreign, else latest UAE):",
        *_table(
            df.withColumn(
                "source",
                F.when(
                    F.col("location_rule") == "L1", F.col("last_foreign_source")
                ).otherwise(F.col("last_uae_source")),
            ),
            "location_rule",
            "source",
        ),
        "location_unknown_reason:",
        *_table(
            df.filter(F.col("location_state") == "unknown"), "location_unknown_reason"
        ),
        "L2 rows by months since the latest UAE evidence:",
        *_table(
            df.filter(F.col("location_rule") == "L2").withColumn(
                "months",
                F.floor(F.months_between("observation_date", "last_uae_date")).cast(
                    "int"
                ),
            ),
            "months",
        ),
        "reachability_state x reason:",
        *_table(df, "reachability_state", "reachability_unknown_reason"),
        "reachability_state x last contact (in W / before W / never):",
        *_table(
            df.withColumn(
                "last_contact",
                F.when(F.col("last_contact_date").isNull(), "never")
                .when(
                    F.col("last_contact_date")
                    >= F.add_months(
                        F.trunc("observation_date", "month"),
                        1 - window_months(model_id),
                    ),
                    "in_W",
                )
                .otherwise("before_W"),
            ),
            "reachability_state",
            "last_contact",
        ),
        "call days in the window:",
        *_table(
            df.withColumn(
                "call_days",
                F.when(days == 0, "0")
                .when(days < 3, "1-2")
                .when(days < 6, "3-5")
                .otherwise("6+"),
            ),
            "call_days",
        ),
        "skip-trace status ever (diagnostic) x location_state:",
        *_table(
            df.withColumn("skip_trace", F.col("last_skip_trace_date").isNotNull()),
            "skip_trace",
            "location_state",
        ),
        "deceased_source:",
        *_table(df.filter(F.col("deceased_flag") == 1), "deceased_source"),
    ]
    _log("RULES", model_id, lines)


def describe_debit_evidence(
    obs_base: DataFrame, casa_cards: DataFrame, model_id: str
) -> None:
    """The latest month's base customers' debit-card rows by month, type and place."""
    cifs = (
        _latest_month(obs_base)
        .select("cif_id")
        .filter(F.col("cif_id").isNotNull())
        .distinct()
    )
    uae = is_uae(F.col("place_country"))
    rows = (
        casa_cards.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .withColumn(
            "type",
            F.when(F.col("channel_desc") == "ATM Transactions", F.lit("ATM")).otherwise(
                F.coalesce(F.col("merchant_type_desc"), F.lit("NULL"))
            ),
        )
        .withColumn("place", F.when(uae, "uae").when(~uae, "abroad").otherwise("none"))
        .withColumn("month", F.trunc(F.coalesce("value_date", "tran_date"), "month"))
    )
    lines = [
        "rows by month x type x place:",
        *_table(rows, "month", "type", "place"),
        "place_source by type:",
        *_table(rows, "type", "place_source"),
        "reason_for_excluding (all months):",
        *_table(rows, "reason_for_excluding"),
    ]
    _log("DEBIT", model_id, lines)


def split_by_product(new: DataFrame, rl_spine: DataFrame, model_id: str) -> None:
    """The latest month's states by ``loan_type`` (RL)."""
    products = rl_spine.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(["account_id", "observation_date"])
    df = _latest_month(new).join(
        products, on=["account_id", "observation_date"], how="left"
    )
    lines = [
        "loan_type x location_state:",
        *_table(df, "loan_type", "location_state"),
        "loan_type x reachability_state:",
        *_table(df, "loan_type", "reachability_state"),
        "loan_type x deceased_flag:",
        *_table(df, "loan_type", "deceased_flag"),
    ]
    _log("PRODUCT", model_id, lines)


# Rang out / no answer only: the narrow failure set of the earlier rule.
_RINGING = frozenset({"RINGING NO REPLY", "RINGING NO RESPONSE", "NO ANSWER"})


def _gone_dark(
    calls: DataFrame, failed_names: frozenset, w_start: F.Column
) -> DataFrame:
    """Per row: gone dark (last GONE_DARK_DAYS call days all failed, oldest in W, no
    contact since) with ``failed_names`` as the failure set and the given calls."""
    outbound = F.col("action_code").isin(*OUTBOUND_CODES)
    days = calls.groupBy(*GRAIN, "day").agg(
        F.max(outbound.cast("int")).alias("_attempt"),
        F.max(F.col("_contact").cast("int")).alias("_c"),
        F.min(F.when(outbound, F.col("name").isin(*failed_names).cast("int"))).alias(
            "_all_failed"
        ),
    )
    days = days.withColumn(
        "_failed", ((F.col("_c") == 0) & (F.col("_all_failed") == 1)).cast("int")
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= GONE_DARK_DAYS)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n"),
            F.sum("_failed").alias("_f"),
            F.min("day").alias("_oldest"),
        )
    )
    contact = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_c") == 1, F.col("day"))).alias("_last_contact")
    )
    return last.join(contact, on=list(GRAIN), how="left").select(
        *GRAIN,
        (
            (F.col("_n") == GONE_DARK_DAYS)
            & (F.col("_f") == GONE_DARK_DAYS)
            & (F.col("_oldest") >= w_start)
            & (
                F.col("_last_contact").isNull()
                | (F.col("_last_contact") < F.col("_oldest"))
            )
        ).alias("gd"),
    )


def explain_reachability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    new: DataFrame,
    model_id: str,
) -> None:
    """Reachability rebuilt from the same DCORE calls under the earlier rule, then each
    change applied in turn, latest month: the state mix after every step and the moves
    between steps.

    R0 earlier rule: any contact ever → reachable, unless the last 3 call days only rang
       out (admin entries kept as calls) → non_reachable
    R1 + dead lines, invalid numbers and LEFT_MSG count as failed (D-A2-7, D-A2-17)
    R2 + admin / legal entries ignored (D-A2-17)
    R3 + the contact must be in W (= the new rule; checked against ``new``)
    """
    obs = _latest_month(obs_base).select(*GRAIN)
    events = _dcore_events(obs, followup, agreements)
    name, code = F.col("name"), F.col("action_code")
    events = events.withColumn(
        "_contact",
        code.isin(*INBOUND_CODES)
        | (code.isin(*OUTBOUND_CODES) & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT),
    )
    calls_all = events.filter(code.isin(*CALL_CODES))
    calls_new = calls_all.filter(
        ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    w_start = F.add_months(
        F.trunc("observation_date", "month"), 1 - window_months(model_id)
    )
    contact = calls_new.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact"), F.col("day"))).alias("last_contact")
    )
    variants = {
        "gd_r0": (calls_all, _RINGING),
        "gd_r1": (calls_all, FAILED_CALL),
        "gd_r2": (calls_new, FAILED_CALL),
    }
    df = obs.join(contact, on=list(GRAIN), how="left").withColumn("_w", w_start)
    for col, (calls, failed) in variants.items():
        gd = _gone_dark(calls, failed, w_start).withColumnRenamed("gd", col)
        df = df.join(gd, on=list(GRAIN), how="left")

    def state(gd: str, in_window: bool) -> F.Column:
        has_contact = (
            F.col("last_contact") >= F.col("_w")
            if in_window
            else F.col("last_contact").isNotNull()
        )
        return (
            F.when(F.coalesce(F.col(gd), F.lit(False)), "non_reachable")
            .when(has_contact, "reachable")
            .otherwise("unknown")
        )

    df = (
        df.withColumn("R0", state("gd_r0", False))
        .withColumn("R1", state("gd_r1", False))
        .withColumn("R2", state("gd_r2", False))
        .withColumn("R3", state("gd_r2", True))
        .cache()
    )
    steps = ["R0", "R1", "R2", "R3"]
    lines = []
    for step in steps:
        lines += [f"{step} state:", *_table(df, step)]
    for before, after in pairwise(steps):
        lines += [
            f"moves {before} -> {after}:",
            *_table(df.filter(F.col(before) != F.col(after)), before, after),
        ]
    engine = _latest_month(new).select(
        *GRAIN, F.col("reachability_state").alias("_engine")
    )
    mismatches = (
        df.join(engine, on=list(GRAIN), how="inner")
        .filter(F.col("R3") != F.col("_engine"))
        .count()
    )
    lines += [
        "R0 -> R3 (all changes):",
        *_table(df, "R0", "R3"),
        f"R3 vs the engine's reachability_state: {mismatches} mismatches",
    ]
    _log("REACH", model_id, lines)
    df.unpersist()
