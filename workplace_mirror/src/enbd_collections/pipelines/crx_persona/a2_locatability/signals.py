"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history (no T0);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, require_columns, window_months
from .codes import (
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

# Travel rule (L2): the latest UAE evidence at most this many months after the last
# ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
# Non-Reachable: the last this-many call days all failed.
GONE_DARK_DAYS = 3
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _window_start(months: int) -> Column:
    """First day of the observation's W-month window."""
    return F.add_months(F.trunc(F.col("observation_date"), "month"), 1 - months)


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
    L3 in_country  the latest UAE evidence is in W
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    latest = (
        obs.join(location_features, on="cif_id")
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
    uae, foreign, travel = (
        F.col("last_uae_date"),
        F.col("last_foreign_date"),
        F.col("last_travel_date"),
    )
    obs_date = F.col("observation_date")
    rule = (
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
        .when(uae >= _window_start(window_months(model_id)), "L3")
        .otherwise("L4")
    )
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
            .when(uae.isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Each observation row's DCORE events dated on or before it: ``day``,
    ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when missing)."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    events = followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
    return (
        obs_base.select(*GRAIN)
        .join(events, on="account_id")
        .filter(F.col("day") <= F.col("observation_date"))
    )


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``codes.FAILED_CALL``) and no contact was confirmed. A contact is an
    inbound call, an outbound call in category SUC, or a right-party result.

    non_reachable  the last GONE_DARK_DAYS call days all failed, the oldest in W, and no
                   contact since
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = _window_start(window_months(model_id))
    events = _dcore_events(obs_base, followup, agreements)
    name = F.col("name")
    code = F.col("action_code")
    calls = events.filter(
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = code.isin(*OUTBOUND_CODES)
    contact = (
        code.isin(*INBOUND_CODES)
        | (outbound & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    days = (
        calls.groupBy(*GRAIN, "day")
        .agg(
            F.max(outbound.cast("int")).alias("_attempt"),
            F.max(contact.cast("int")).alias("_contact"),
            F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
                "_all_failed"
            ),
        )
        .withColumn(
            "_failed",
            ((F.col("_contact") == 0) & (F.col("_all_failed") == 1)).cast("int"),
        )
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last_days = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= GONE_DARK_DAYS)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n_last"),
            F.sum("_failed").alias("_failed_last"),
            F.min("day").alias("_oldest_last"),
        )
    )
    day = F.col("day")
    calls_summary = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact") == 1, day)).alias("last_contact_date"),
        F.max(F.when(F.col("_attempt") == 1, day)).alias("last_attempt_date"),
        F.count(F.when((F.col("_attempt") == 1) & (day >= w_start), day)).alias(
            "attempt_days_in_window"
        ),
    )
    records = events.groupBy(*GRAIN).agg(
        F.max(F.when(name.isin(*DECEASED), day)).alias("dcore_deceased_date"),
        F.max(F.when(name.isin(*SKIP_TRACE), day)).alias("last_skip_trace_date"),
        F.lit(1).alias("_dcore_record"),
    )
    last_contact = F.col("last_contact_date")
    gone_dark = (
        (F.col("_n_last") == GONE_DARK_DAYS)
        & (F.col("_failed_last") == GONE_DARK_DAYS)
        & (F.col("_oldest_last") >= w_start)
        & (last_contact.isNull() | (last_contact < F.col("_oldest_last")))
    )
    return (
        left_join_all(obs_base, [records, calls_summary, last_days])
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
    """``way4_deceased_flag``: block code 2 = D on the latest ``prm_contract`` snapshot on
    or before the observation date, on any of the customer's cards. Rows with a card
    only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
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
    latest = Window.partitionBy(*GRAIN, "contract_id").orderBy(
        F.col("snapshot_date").desc(), deceased.desc()
    )
    return (
        obs.join(cards, on="cif_id")
        .join(snapshots.drop("client_id"), on="contract_id")
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .groupBy(*GRAIN)
        .agg(F.max(deceased.cast("int")).alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag``: ``ft_deceased_flag`` of the customer (a death is
    permanent: the largest value per CIF, no date). Rows with a demographics record
    only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    flags = demographics.groupBy(F.col("cif_id").cast("string").alias("cif_id")).agg(
        F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
            "demographics_deceased_flag"
        )
    )
    return (
        obs_base.filter(F.col("cif_id").isNotNull())
        .select(*GRAIN, "cif_id")
        .join(flags, on="cif_id")
        .select(*GRAIN, "demographics_deceased_flag")
    )
