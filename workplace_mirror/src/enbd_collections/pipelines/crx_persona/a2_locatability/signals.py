"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``. Run through
``crx_cc_a2_locatability`` / ``crx_rl_a2_locatability``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history up to the
                 observation date (D-A2-8);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    left_join_all,
    require_columns,
    scoped,
    segment,
    window_months,
    window_start,
)
from .._dcore_codes import (
    CALL_CODES,
    DECEASED,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SKIP_TRACE,
    SUCCESS_CATEGORY,
)

# Travel rule (L2, D-A2-18): the latest UAE evidence at most this many months after
# the last ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _cif_rows(obs_base: DataFrame) -> DataFrame:
    """``GRAIN + cif_id`` of the observation rows that have a CIF."""
    return obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def _latest_evidence(obs: DataFrame, location_features: DataFrame) -> DataFrame:
    """Per ``GRAIN``: the latest UAE and foreign evidence (date and source) and the last
    travel purchase, from the monthly rows up to the observation date."""
    return (
        obs.join(scoped(location_features, obs, "cif_id"), on="cif_id")
        .filter(F.col("month_end") <= F.col("observation_date"))
        .groupBy(*GRAIN)
        .agg(
            _latest("last_uae_date", "last_uae_source").alias("_uae"),
            _latest("last_foreign_date", "last_foreign_source").alias("_foreign"),
            F.max("last_travel_date").alias("last_travel_date"),
        )
        .select(
            *GRAIN,
            F.col("_uae.last_uae_date").alias("last_uae_date"),
            F.col("_uae.last_uae_source").alias("last_uae_source"),
            F.col("_foreign.last_foreign_date").alias("last_foreign_date"),
            F.col("_foreign.last_foreign_source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )


def _location_rule(window: int) -> Column:
    """The first of the rules L1–L4 that fires (see ``build_location_signals``);
    ``window`` is W in months."""
    uae, foreign, travel = (
        F.col("last_uae_date"),
        F.col("last_foreign_date"),
        F.col("last_travel_date"),
    )
    obs_date = F.col("observation_date")
    return (
        F.when(foreign.isNotNull() & (uae.isNull() | (foreign >= uae)), "L1")
        .when(
            travel.isNotNull()
            & (
                uae.isNull()
                | (
                    (uae <= F.add_months(travel, TRAVEL_GAP_MONTHS))
                    & (uae <= F.add_months(obs_date, -TRAVEL_SILENCE_MONTHS))
                )
            ),
            "L2",
        )
        .when(uae >= window_start(window), "L3")
        .otherwise("L4")
    )


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
                   (D-A2-3; the same day: foreign wins, D-A2-14)
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
                   (D-A2-15, D-A2-18)
    L3 in_country  the latest UAE evidence is in W (D-A2-3)
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    latest = _latest_evidence(_cif_rows(obs_base), location_features)
    rule = _location_rule(window_months(model_id))
    return (
        left_join_all(obs_base, [latest])
        .withColumn("location_rule", rule)
        .withColumn(
            "location_state",
            F.when(F.col("location_rule").isin("L1", "L2"), "skip")
            .when(F.col("location_rule") == "L3", "in_country")
            .otherwise("unknown"),
        )
        .withColumn(
            "location_unknown_reason",
            F.when(F.col("location_rule") != "L4", None)
            .when(F.col("last_uae_date").isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_days(events: DataFrame) -> DataFrame:
    """One row per ``(account_id, day)`` of ``dcore_account_events``, with the day's
    flags: ``_attempt`` (an outbound call), ``_contact`` (see ``build_dcore_signals``),
    ``_all_failed`` (every outbound call failed, NULL without one), ``_deceased`` and
    ``_skip_trace`` (a result of that kind). Reduced to days before the join with the
    observations."""
    code, category, name = F.col("action_code"), F.col("category"), F.col("name")
    call = (
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = call & code.isin(*OUTBOUND_CODES)
    contact = call & (
        code.isin(*INBOUND_CODES)
        | (outbound & (category == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    return events.groupBy("account_id", "day").agg(
        F.max(outbound.cast("int")).alias("_attempt"),
        F.max(contact.cast("int")).alias("_contact"),
        F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
            "_all_failed"
        ),
        F.max(name.isin(*DECEASED).cast("int")).alias("_deceased"),
        F.max(name.isin(*SKIP_TRACE).cast("int")).alias("_skip_trace"),
    )


def gone_dark_days(model_id: str) -> int:
    """The failed-call-day streak that makes ``model_id``'s segment Non-Reachable."""
    return GONE_DARK_DAYS[segment(model_id)]


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``_dcore_codes.FAILED_CALL``) and no contact was confirmed. A contact
    is an inbound call, an outbound call in category SUC, or a right-party result
    (off-list codes: D-A2-17).

    non_reachable  the last ``gone_dark_days`` call days all failed, the oldest in W,
                   and no contact since (D-A2-7, D-A2-20)
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = window_start(window_months(model_id))
    streak = gone_dark_days(model_id)
    days = (
        obs_base.select(*GRAIN)
        .join(
            _dcore_days(dcore_account_events(obs_base, followup, agreements)),
            on="account_id",
        )
        .filter(F.col("day") <= F.col("observation_date"))
    )
    day = F.col("day")
    attempt = F.col("_attempt") == 1
    contact = F.col("_contact") == 1
    # Attempt days, newest first: rank 1..n (other days sort last and are never read).
    rank = F.row_number().over(
        Window.partitionBy(*GRAIN).orderBy(F.when(attempt, day).desc_nulls_last())
    )
    last = attempt & (F.col("_rank") <= streak)
    failed = ~contact & (F.col("_all_failed") == 1)
    summary = (
        days.withColumn("_rank", rank)
        .groupBy(*GRAIN)
        .agg(
            F.max(F.when(F.col("_deceased") == 1, day)).alias("dcore_deceased_date"),
            F.max(F.when(F.col("_skip_trace") == 1, day)).alias("last_skip_trace_date"),
            F.lit(1).alias("_dcore_record"),
            F.max(F.when(contact, day)).alias("last_contact_date"),
            F.max(F.when(attempt, day)).alias("last_attempt_date"),
            F.count(F.when(attempt & (day >= w_start), day)).alias(
                "attempt_days_in_window"
            ),
            F.count(F.when(last, day)).alias("_n_last"),
            F.count(F.when(last & failed, day)).alias("_failed_last"),
            F.min(F.when(last, day)).alias("_oldest_last"),
        )
    )
    last_contact = F.col("last_contact_date")
    gone_dark = (
        (F.col("_n_last") == streak)
        & (F.col("_failed_last") == streak)
        & (F.col("_oldest_last") >= w_start)
        & (last_contact.isNull() | (last_contact < F.col("_oldest_last")))
    )
    return (
        left_join_all(obs_base, [summary])
        .withColumn(
            "reachability_state",
            F.when(gone_dark, "non_reachable")
            .when(last_contact >= w_start, "reachable")
            .otherwise("unknown"),
        )
        .withColumn(
            "reachability_unknown_reason",
            F.when(F.col("reachability_state") != "unknown", None)
            .when(F.col("_dcore_record").isNull(), "no_dcore_record")
            .otherwise("no_contact_in_window"),
        )
        .withColumn(
            "attempt_days_in_window", F.coalesce("attempt_days_in_window", F.lit(0))
        )
        .drop("_dcore_record", "_n_last", "_failed_last", "_oldest_last")
    )


# ── Deceased (Way4, demographics) ─────────────────────────────────────────────


def build_way4_deceased(
    obs_base: DataFrame, contracts: DataFrame, clients: DataFrame
) -> DataFrame:
    """``way4_deceased_flag`` (D-A2-9): block code 2 = D on the latest ``prm_contract``
    snapshot on or before the observation date, on any of the customer's cards. Rows
    with a card only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = _cif_rows(obs_base)
    cifs = obs.select("cif_id").distinct()
    snapshots = contracts.select(
        F.col("contract_id").cast("string").alias("contract_id"),
        "client_id",
        F.to_date("observation_date").alias("snapshot_date"),
        F.upper(F.trim("block_code_2")).alias("block_code_2"),
    )
    cards = (
        snapshots.select("contract_id", "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select("contract_id", "cif_id")
    )
    deceased = F.coalesce(F.col("block_code_2") == WAY4_DECEASED_BLOCK, F.lit(False))
    return (
        obs.join(cards, on="cif_id")
        .join(
            scoped(snapshots.drop("client_id"), cards, "contract_id"), on="contract_id"
        )
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .groupBy(*GRAIN, "contract_id")
        .agg(
            F.max(F.struct("snapshot_date", deceased.cast("int").alias("flag"))).alias(
                "_latest"
            )
        )
        .groupBy(*GRAIN)
        .agg(F.max("_latest.flag").alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag`` (D-A2-9): ``ft_deceased_flag`` of the customer (a
    death is permanent: the largest value per CIF, no date). Rows with a demographics
    record only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    obs = _cif_rows(obs_base)
    people = demographics.select(
        F.col("cif_id").cast("string").alias("cif_id"), "ft_deceased_flag"
    )
    flags = (
        scoped(people, obs, "cif_id")
        .groupBy("cif_id")
        .agg(
            F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
                "demographics_deceased_flag"
            )
        )
    )
    return obs.join(flags, on="cif_id").select(*GRAIN, "demographics_deceased_flag")
