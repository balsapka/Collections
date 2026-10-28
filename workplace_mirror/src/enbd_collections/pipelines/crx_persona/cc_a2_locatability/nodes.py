"""A2 Locatability axis — location x reachability (2-dimension cross).

# pylint: disable=too-many-locals, too-many-statements, too-many-lines

Build functions:
    build_a2_base(cc_spine, crx_cc_spell_table, crx_cc_departure_signature)
        -> crx_cc_a2_base

    build_a2_login_presence(crx_cc_a2_base, prm_digital_login_monthly)
        -> crx_cc_a2_login_presence

    build_a2_contact_signals(crx_cc_a2_base, dcore_observation_spine,
                             dcore_prm_followup_outcomes)
        -> crx_cc_a2_contact_signals

    build_a2_locatability(crx_cc_a2_base, crx_cc_a2_login_presence,
                          crx_cc_a2_contact_signals, model_id,
                          prm_contract=None, prm_client=None,
                          feat_demographics_cif=None)
        -> crx_cc_a2_locatability   <- shipped persona axis

Provenance: T12 (2026-09) shipped a 7-state contact-outcome x presence waterfall
(deceased | non_cooperative | reachable | avoiding | skip | gone | unknown). GRR
feedback (data/input/Axes and States for UC2 - Cards 61-180.xlsx, sheet "A1, A2, A4",
rows 8-14) asked for a simpler 2-dimension cross instead -- T29 built that redesign as a
parallel, additive pipeline (cc_a2_locatability_v2, R18) beside T12 so the two could be
compared before any integration decision (see
docs/context/results/MASTER_SUMMARY_a2_locatability_v2_20261012.md). The user has now
promoted T29's design to the shipped A2 derivation (2026-10-22) -- T12's 7-state
waterfall is retired (RESULTS.md). Node 4 below is T29's derivation ported in place of
T12's; Nodes 1-3 are unchanged -- T29 always consumed them read-only and never needed its
own copies.

Goal -- assign each (account_id, observation_date) a location x reachability pair:

    Location      in {Skip, In Country, Unknown}          -- presence evidence only
    Reachability  in {Reachable, Non-Reachable, Unknown} -- RPC-established condition

Location must be derived *purely* from departure_trail_flag / in_country_flag (login,
digital footprints, transactions) -- never mixed with any conversational/contact-outcome
condition. Reachability keeps T12's spirit but collapses the old non_cooperative/avoiding
split into a plain binary (confirmed contact vs. confirmed dead). Deceased stays a
separate pre-guard state; as of T34 (2026-10-12) the flag it fires on is
deceased_flag_v2, a corroborated combination rather than DCORE alone (see "Deceased
corroboration" below).

**Model-agnostic, shared across CC and RL.** build_a2_locatability is the one and only
state-derivation function for this axis -- RL's rl_a2_locatability pipeline imports it
directly from this module rather than duplicating it. Only the *upstream* intermediates
differ by domain (crx_rl_a2_base/crx_rl_a2_login_presence/crx_rl_a2_contact_signals,
schema-identical to CC's own intermediates); the location x reachability cross itself is
identical regardless of domain. The _TAU_RECENT_D_BY_MODEL_ID/_TAU_LABEL_D_BY_MODEL_ID
dicts below carry all four model_ids (cc_60_180, cc_180_plus, rl_60_180, rl_180_plus).

State rules (first match wins):
    1. deceased_flag_v2=1                                          -> Deceased
       (pre-guard, absolute first priority; deceased_flag_v2 = deceased_flag OR
        way4_deceased_flag OR demographics_deceased_flag -- T34)
    2. location_state:
        departure_trail_flag=1 AND in_country_flag=0              -> Skip
        in_country_flag=1                                          -> In Country
          (recent in-country evidence wins over a stale departure trail)
        otherwise (both flags 0)                                   -> Unknown
    3. reachability_state:
        guard: contact_attempts_n < _TAU_A_ATTEMPTS, or
        label_event_gap_d > _TAU_LABEL_D (model_id-resolved), or
        either NULL                                                -> Unknown
        recent_avoidance_flag=1                                    -> Non-Reachable
          (2026-10-22 amendment -- downgrades a lifetime-established confirmed
          contact when the last _TAU_RECENT_AVOIDANCE_N outbound attempts were ALL
          ringing/no-answer, zero confirmed among them, and recent -- see below.
          Checked BEFORE contact_confirmed_flag so a stale historical RPC cannot
          outrank a fresh, consistent avoidance pattern.)
        contact_confirmed_flag=1                                   -> Reachable
          (absorbs T12's non_cooperative -- contact was made, refusal or not;
          this is a LIFETIME count over [t0, obs) -- see recent_avoidance_flag
          above for the recency override)
        gone_contact_flag=1 AND last_attempt_contact_flag=0        -> Non-Reachable
          (absorbs T12's avoiding -- last-N attempts all dead-or-ringing, no
          confirmed contact, and the single most recent call-type action was not
          itself a confirmed contact)
        otherwise                                                  -> Unknown
    4. a2_state = "Deceased" if deceased_flag_v2=1, else
                  f"{location_state} - {reachability_state}"

location_state and reachability_state are emitted as their own columns (not just folded
into a2_state) so a consumer can cut by either dimension independently. Both are computed
unconditionally from the signals, even on deceased rows.

Segment-aware thresholds (amendment, 2026-10-08, ratified against T29's EDA): the
2026-10-07 T29 EDA run found location_state saturates to Unknown at 90.37% for
cc_180_plus under a flat 90-day _TAU_RECENT_D -- that segment's documented thinner
digital/contact cadence (T12b: 11.54% pre-obs login coverage). Both the location-recency
window (_TAU_RECENT_D) and the reachability staleness guard (_TAU_LABEL_D) vary by
model_id:

    _TAU_RECENT_D_BY_MODEL_ID = {"cc_60_180": 90, "cc_180_plus": 180,
                                 "rl_60_180": 90, "rl_180_plus": 180}  # days
    _TAU_LABEL_D_BY_MODEL_ID  = {"cc_60_180": 90, "cc_180_plus": 180,
                                 "rl_60_180": 90, "rl_180_plus": 180}  # days

Any model_id not in these dicts falls back to the 90-day default (fail soft, not hard --
see _resolve_tau). _TAU_A_ATTEMPTS is a count, not a time window, and stays flat at 3 for
every segment.

Reachability recency override -- recent_avoidance_flag (amendment, 2026-10-22): as shipped
2026-10-22, contact_confirmed_flag is a LIFETIME count over [t0, obs) -- once any contact is
confirmed anywhere in the delinquency spell, the account is Reachable for the rest of the
spell, even if every attempt since has gone dead/unanswered (gone_contact_flag is windowed
to the last _TAU_NOT_REACHABLE_N=2 attempts, but is only ever evaluated when
contact_confirmed_flag=0, so it can never override a historical confirmed contact). The user
asked for this fixed: Reachable should downgrade to Non-Reachable when the customer has gone
dark recently, not just when they were never reached at all. recent_avoidance_flag fires when
the last _TAU_RECENT_AVOIDANCE_N=3 distinct outbound attempt dates were ALL ringing/no-answer
(the T12 "avoiding" signal -- line confirmed live, no pickup; deliberately NOT mixed with
dead/invalid-number outcomes, which is a different failure mode), zero confirmed contact
among those 3, and the oldest of those 3 attempts is still within tau_label_d (the same
segment-aware staleness window as the 4.4c guard -- 90d for *_60_180, 180d for *_180_plus) of
observation_date. It is checked ahead of contact_confirmed_flag in the reachability_state
waterfall, so a fresh 3-strike avoidance run overrides a stale historical RPC. Computed from
a second chronologically-ranked window in build_a2_contact_signals (Step 5c), parallel to the
existing _TAU_NOT_REACHABLE_N=2 window that feeds not_reachable_flag/gone_contact_flag (Step
5b) -- the two windows are independent and intentionally different sizes (2 for the
never-confirmed path, 3 for the recency-override path, per the user's explicit threshold).

Deceased corroboration -- CC/RL asymmetry (T34, 2026-10-12): deceased_flag was DCORE-only
until this amendment. PROD evidence on cc_60_180 found Way4 block code block_code_2='D'
catches 36 accounts (81.8% of DCORE's own count) that DCORE missed -- material,
OR-combined in. For cc_180_plus, prm_contract matched zero rows for that snapshot (a
join-reach anomaly, not an absent code -- see RESULTS.md Proposed amendments); the
Way4/demographics terms are harmlessly 0 there. Both terms are wired **data-driven, not
domain-branched**: Way4 (prm_contract.block_code_1/block_code_2) activates only when
prm_contract is supplied *and* carries those columns -- CC-only, since RL has no
Way4-equivalent block-code table anywhere in its data model (grep-confirmed).
Demographics (feat_demographics_cif.ft_deceased_flag) activates whenever a cif_id is
resolvable: RL's crx_rl_a2_base already carries cif_id directly (no bridge needed), while
CC's crx_cc_a2_base does not, so CC must also supply prm_contract+prm_client to build the
bridge (_build_cif_bridge) before demographics can join. Net effect: CC's pipeline wires
Way4 + demographics; RL's pipeline wires demographics only (no Way4 inputs supplied --
prm_contract/prm_client stay None).

Design decisions (Nodes 1-3, unchanged since T12):
  - cc_spine is the grain anchor -- already model_id-scoped via Kedro namespace.
    No segment filter via max_dpd_so_far is needed or correct here.
  - Departure trail columns reused from crx_cc_departure_signature (T06, R14).
    Only the obs-anchored login presence is new here.
  - Schema guard in build_a2_contact_signals: empty/missing DCORE -> all-NULL /
    zero contact signals; state derivation handles NULL gracefully -> Unknown.
  - rpc_rate is now (rpc_n + rpc_proxy_n) / contact_attempts_n -- includes
    result descriptions miscategorised as INT/UNS (e.g. "REFUSED TO PAY" = INT).
  - contact_confirmed_n = _rpc_n + _rpc_proxy_n -- channel-agnostic confirmed
    contact count; used by the reachability derivation.
  - result_name-based allowlists used throughout -- self-documenting and stable
    across DCORE deployments; carried directly on dcore_prm_followup_outcomes.
  - Field visit events: only FIELD VISIT DONE counts as contact confirmation.
    Scheduling events (SENT/REJECTED/REQUEST) do not confirm contact.
  - not_reachable_flag fires when the last _TAU_NOT_REACHABLE_N distinct outbound
    attempt dates all produced dead/unconnected outcomes with no confirmed contact.
    Accounts with fewer than _TAU_NOT_REACHABLE_N distinct attempt dates fall
    through to the reachability guard anyway. not_reachable_n (total count) is
    kept in the output for diagnostics.
  - gone_contact_flag fires when the last _TAU_NOT_REACHABLE_N outbound dates were
    all dead OR ringing, no confirmed contact -- shared denominator with
    not_reachable_flag, different numerator (dead only vs. dead-or-ringing).
"""

# pylint: disable=too-many-lines
import datetime
import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.constants import (
    _DECEASED_RESULT_NAMES,
    _DEPARTURE_RESULT_NAMES,
    _FIELD_VISIT_RESULT_NAMES,
    _HARDSHIP_RESULT_NAMES,
    _NOT_REACHABLE_RESULT_NAMES,
    _PROMISE_TO_PAY_RESULT_NAMES,
    _REFUSING_RESULT_NAMES,
    _RIGHT_PARTY_CONTACT_RESULT_NAMES,
    _RINGING_RESULT_NAMES,
)
from enbd_collections.pipelines.crx_persona._spine_utils import (
    _build_cif_bridge,
    join_spine_to_spell,
)

LOG = logging.getLogger(__name__)

# ── Guard threshold shared with Node 3's chronological skip/gone check ─────────
_TAU_NOT_REACHABLE_N = (
    2  # skip + gone: last N outbound attempt dates checked chronologically  [CONFIRM]
    # skip requires all N dead; gone_contact_flag requires all N dead OR ringing.
)

# ── Guard threshold for the recent-avoidance override (2026-10-22 amendment) ──
_TAU_RECENT_AVOIDANCE_N = (
    3  # reachability override: last N outbound attempt dates checked chronologically.
    # Downgrades a lifetime-established Reachable state (contact_confirmed_n > 0
    # somewhere in [t0, obs)) to Non-Reachable when the most recent N attempts were
    # ALL ringing/no-answer ("avoiding" — line confirmed live, no pickup, no dead/
    # invalid-number mix) AND fall within the segment's tau_label recency window.
    # See build_a2_locatability Step 4b (recent_avoidance_flag).
)

# ── Node 4 guard thresholds — ported from T29 (cc_a2_locatability_v2) ─────────
# §4.4b: reachability Unknown if contact_attempts_n < this. A flat count, not a
# time window — stays the same across every model_id (unlike the two dicts below).
_TAU_A_ATTEMPTS = 3

# Segment-aware recency windows (amendment, 2026-10-08). cc_180_plus's documented
# thinner digital/contact cadence (T12b: 11.54% pre-obs login coverage) saturates
# location_state to Unknown at 90.37% under the flat 90d window — widened to 180d
# (6m) for that segment. The same thin-cadence argument applies to the
# reachability staleness guard. Default (90d) covers any model_id not listed here
# — fail soft, not hard.
_TAU_RECENT_D_BY_MODEL_ID = {  # in_country: login within this many days of obs_date
    "cc_60_180": 90,
    "cc_180_plus": 180,
    "rl_60_180": 90,
    "rl_180_plus": 180,
}
_TAU_LABEL_D_BY_MODEL_ID = (
    {  # §4.4c: reachability Unknown if contact evidence is this stale
        "cc_60_180": 90,
        "cc_180_plus": 180,
        "rl_60_180": 90,
        "rl_180_plus": 180,
    }
)
_TAU_DEFAULT_D = 90

# Way4 block-code deceased signal — CC-only (no RL equivalent exists). T34, PROD
# discovery 2026-10-12: confirmed on block_code_2 for cc_60_180 (47/19,292 rows);
# block_code_1 never carries it in either segment observed. Checked defensively on
# both columns — org-specific suffix patterns (BLOCK_CODE_ACC1_%/BLOCK_CODE_ACC2_%)
# mean this could in principle appear on either.
_WAY4_DECEASED_BLOCK_CODES = {"D"}


def _resolve_tau(model_id: str, tau_by_model_id: dict) -> int:
    """Segment-aware tau lookup with a soft default (never raises on an unknown id)."""
    return tau_by_model_id.get(model_id, _TAU_DEFAULT_D)


# ── Departure trail columns reused from T06 (R14 — never re-derive) ───────────
_DEPART_COLS = [
    "account_id",
    "spell_id",
    "travel_mcc_flag_h2",  # Pass A — travel MCC in H2 pre-T0
    "last_txn_foreign_flag",  # Pass A — last W_pre txn was international
    "foreign_login_flag",  # Pass J — most recent login before spine_obs_date is foreign
    "casa_inflow_stop_gap_d",  # Pass B — CASA salary stop gap (days)
]

# ── DCORE call action codes ──────────────────────────────────────────────────
_OUTBOUND_CODES = ["OC", "CB"]  # outbound call / callback attempt (we initiated)
_INBOUND_CODES = ["IC"]  # inbound call — customer called us (confirmed 2026-09-11)
_CALL_CODES = (
    _OUTBOUND_CODES + _INBOUND_CODES
)  # OC, CB, IC — real dial/call events only


# ── Node 1: build_a2_base ────────────────────────────────────────────────────


def build_a2_base(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    departure_sig: DataFrame,
) -> DataFrame:
    """Attach spell window + departure trail columns to the spine grain.

    Uses cc_spine as the grain anchor — it is already model_id-scoped
    (cc_60_180 spine contains only 60-180 DPD accounts; cc_180_plus spine
    contains only 180+ accounts).  No segment filter via max_dpd_so_far
    is needed or correct here.

    Joins spell_table only to obtain t0 and spell_id for feature windows.
    Then attaches reusable departure trail columns from T06 (R14 — do not
    re-derive what T06 already built).

    Args:
        cc_spine:      Model-id-scoped spine; grain (account_id, observation_date).
            Required cols: account_id (= contract_id), observation_date.
        spell_table:   crx_cc_spell_table; grain (account_id, spell_id).
            Required cols: account_id, spell_id, t0, spell_end.
        departure_sig: crx_cc_departure_signature (T06); grain (account_id, spell_id).
            Required cols: _DEPART_COLS.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id            (string)
            observation_date      (date)
            spell_id              (int)
            t0                    (date)
            cif_id                (string)
            travel_mcc_flag_h2    (int)
            last_txn_foreign_flag (int)
            foreign_login_flag    (int)
            casa_inflow_stop_gap_d (double)
    """
    # ── Step 1: join spine to spell_table to get t0 / spell_id ──────────────
    # Shared utility — equality join + date filters (same pattern as A1, A4).
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    # Recover cif_id from cc_spine (dropped by join_spine_to_spell).
    spine_cif = cc_spine.select(
        F.col("contract_id").cast("string").alias("_cid"),
        F.col("cif_id").cast("string"),
    )
    spine_with_spell = spine_with_spell.join(
        spine_cif, on=spine_with_spell["account_id"] == spine_cif["_cid"], how="left"
    ).drop("_cid")

    # ── Step 2: attach departure signature columns (T06 reuse, R14) ──────────
    base = spine_with_spell.join(
        departure_sig.select(*_DEPART_COLS),
        on=["account_id", "spell_id"],
        how="left",
    )

    n_rows = base.count()
    n_with_spell = base.filter(F.col("spell_id").isNotNull()).count()
    n_with_depart = base.filter(F.col("travel_mcc_flag_h2").isNotNull()).count()
    LOG.info(
        "build_a2_base: %d rows | spell join: %d (%.1f%%) | departure trail: %d (%.1f%%)",
        n_rows,
        n_with_spell,
        100.0 * n_with_spell / max(n_rows, 1),
        n_with_depart,
        100.0 * n_with_depart / max(n_rows, 1),
    )

    return base


# ── Node 2: build_a2_login_presence ──────────────────────────────────────────


def build_a2_login_presence(  # pylint: disable=too-many-locals
    base: DataFrame,
    prm_login: DataFrame,
    obs_month_end: bool = False,
) -> DataFrame:
    """Derive obs-anchored digital presence signals.

    A single PIT join is computed from the login table:

    1. Current presence (obs-date anchor): most recent login month strictly
       before trunc(observation_date, 'month') when obs_month_end=False
       (default — CC mid-month observations).  Use obs_month_end=True for
       month-end observation dates (retail loans, or CC if it ever moves
       to month-end) — the observation month is fully closed so <= is safe.

    Args:
        base:          crx_cc_a2_base; grain (account_id, observation_date).
            Required cols: account_id, observation_date, t0, cif_id.
            cif_id is propagated from build_a2_base — no PRM bridge needed.
        prm_login:     prm_digital_login_monthly — monthly login records per cif.
            Required cols: cif_id, month_number (yyyyMMdd string),
            last_login_date, last_login_foreign_flag,
            last_login_country, last_login_countrycode.
        obs_month_end: If True, include the observation month itself in the
                       PIT window (safe only when observation_date is the last
                       day of the month).  Default False (CC mid-month).

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id              (string)
            observation_date        (date)
            last_login_date         (date;   NULL if no pre-obs login found)
            last_digital_login_gap_d (int;   days; NULL if no login)
            last_login_foreign_flag (int;    0/1;  NULL if no login)
            last_login_country      (string; NULL if no login)
    """
    # ── Parse month_number string → date ──────────────────────────────────────
    prm_dated = prm_login.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    )

    # ── Base with CIF for obs-date join ───────────────────────────────────────
    base_with_cif = base.select("account_id", "observation_date", "cif_id").join(
        prm_dated.select(
            "cif_id",
            "_month_date",
            "last_login_date",
            "last_login_foreign_flag",
            "last_login_country",
            "last_login_countrycode",
        ),
        on="cif_id",
        how="inner",
    )

    # ── Join 1: current presence — latest login before trunc(obs, 'month') ─────
    # obs_month_end=False (CC default): exclude observation month — partial calendar
    #   month would introduce look-ahead for mid-month observation dates.
    # obs_month_end=True  (retail loans, or CC if moved to month-end): include it —
    #   the month is fully closed when observation_date is month-end.
    _obs_cutoff = F.trunc(F.col("observation_date"), "month")
    _obs_filter = (
        F.col("_month_date") <= _obs_cutoff
        if obs_month_end
        else F.col("_month_date") < _obs_cutoff
    )
    w_obs = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("_month_date").desc()
    )
    latest_obs = (
        base_with_cif.filter(_obs_filter)
        .withColumn("_rn", F.row_number().over(w_obs))
        .filter(F.col("_rn") == 1)
        .withColumn(
            "last_digital_login_gap_d",
            F.datediff(F.col("observation_date"), F.col("last_login_date")),
        )
        .select(
            "account_id",
            "observation_date",
            "last_login_date",
            "last_digital_login_gap_d",
            "last_login_foreign_flag",
            "last_login_country",
        )
    )

    # ── Left-join back to all base pairs (no login → NULLs) ───────────────────
    result = base.select("account_id", "observation_date").join(
        latest_obs, on=["account_id", "observation_date"], how="left"
    )

    n_rows = result.count()
    n_with_login = result.filter(F.col("last_login_date").isNotNull()).count()
    LOG.info(
        "build_a2_login_presence: %d rows | obs login: %d (%.1f%%)",
        n_rows,
        n_with_login,
        100.0 * n_with_login / max(n_rows, 1),
    )

    return result


# ── Node 3: build_a2_contact_signals ─────────────────────────────────────────


def build_a2_contact_signals(  # pylint: disable=too-many-locals
    base: DataFrame,
    observation_spine: DataFrame,
    followup: DataFrame,
) -> DataFrame:
    """Derive attempt-normalised contact signals from DCORE.

    Window: [t0, observation_date) — entire delinquency window to obs.
    All rates are normalised over contact_attempts_n (§4.4b denominator).

    result_name allowlists (carried directly on dcore_prm_followup_outcomes)
    are used for fine-grained signal classification:
      - rpc_proxy_n:         RPC events miscategorised as INT/UNS (e.g. REFUSED TO PAY)
      - refusing_n:          Explicit refusal/hang-up/dispute (non_cooperative signal)
      - ringing_n:           Ringing no-answer events (avoiding signal; ≥3 required)
      - deceased_flag:       Confirmed or claimed deceased (highest-priority state)
      - contact_confirmed_n: Channel-agnostic confirmed contact (_rpc_n + _rpc_proxy_n)
      - dcore_departure_n:   Contact record explicitly states customer left UAE
      - field_visit_n:       Completed field visits only (excluded from phone rpc_n)
      - not_reachable_n:     Contact info structurally invalid (wrong number, mobile off)

    rpc_rate = (rpc_n + rpc_proxy_n) / contact_attempts_n — corrected numerator.
    Field visit SUC codes are excluded from rpc_n to prevent inflation.

    Schema guard (R21): if dcore_prm_followup_outcomes is empty or missing
    required columns, this node emits all-NULL / zero contact signals.  The
    state derivation in build_a2_locatability handles this gracefully
    (falls through §4.4b guard → unknown).

    Args:
        base:              crx_cc_a2_base; grain (account_id, observation_date).
            Required cols: account_id, observation_date, t0.
        observation_spine: dcore_observation_spine — full account→agreement mapping.
            Required cols: contract_id, observation_date, agreement_id, cif_id.
            contract_id = account_id; joined on (account_id, observation_date).
        followup:          dcore_prm_followup_outcomes.
            Required cols: agreement_id, action_ts, action_code,
            result_category, result_name.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id               (string)
            observation_date         (date)
            contact_attempts_n       (int;    NULL if no DCORE coverage)
            rpc_rate                 (double; NULL if attempts=0 or no DCORE)
            uns_rate                 (double; NULL if attempts=0 or no DCORE)
            last_contact_attempt_dt  (date;   NULL if no attempts; call-type
                                              codes only (OC/CB/IC) — excludes
                                              IA administrative notes)
            label_event_gap_d        (int;    days; NULL if no attempts)
            refusing_n               (int;    0 if no DCORE; explicit refusal count)
            ringing_n                (int;    0 if no DCORE; ringing no-answer count)
            deceased_flag            (int;    0/1; 1 = DCORE confirmed/claimed deceased)
            contact_confirmed_n      (int;    0 if no DCORE; _rpc_n + _rpc_proxy_n)
            dcore_departure_flag     (int;    0/1)
            field_visit_flag         (int;    0/1; 1 = ≥1 completed field visit)
            not_reachable_flag       (int;    0/1; 1 = contact info structurally invalid)
            gone_contact_flag        (int;    0/1; 1 = last _TAU_NOT_REACHABLE_N outbound
                                              dates all produced ringing/dead result_names,
                                              no confirmed outbound contact)
            ptp_flag                 (int;    0/1; 1 = ≥1 promise-to-pay or payment commitment)
            hardship_flag            (int;    0/1; 1 = ≥1 hardship / special-case signal)
            recent3_attempt_dates_n  (int;    0 if no DCORE; distinct outbound attempt
                                              dates found within the last
                                              _TAU_RECENT_AVOIDANCE_N ranks, ≤3)
            recent3_ringing_n        (int;    0 if no DCORE; ringing/no-answer count among
                                              those same last-3-ranked attempts)
            recent3_confirmed_n      (int;    0 if no DCORE; confirmed-contact count among
                                              those same last-3-ranked attempts)
            recent3_oldest_gap_d     (int;    days; NULL if fewer than
                                              _TAU_RECENT_AVOIDANCE_N distinct outbound
                                              dates exist; gap between observation_date and
                                              the oldest of the last-3-ranked attempts —
                                              2026-10-22 amendment, feeds Node 4's
                                              recent_avoidance_flag)
    """
    _REQUIRED_FOLLOWUP_COLS = {
        "agreement_id",  # was "iagreementseqno"
        "action_ts",
        "action_code",
        "result_category",  # was "szcategorycode"
        "result_name",  # was "szresultname" — now carried directly, no join needed
    }

    def _null_signals(df: DataFrame) -> DataFrame:
        return df.select("account_id", "observation_date").select(
            F.col("account_id"),
            F.col("observation_date"),
            F.lit(None).cast("int").alias("contact_attempts_n"),
            F.lit(None).cast("double").alias("rpc_rate"),
            F.lit(None).cast("double").alias("uns_rate"),
            F.lit(None).cast("date").alias("last_contact_attempt_dt"),
            F.lit(None).cast("int").alias("label_event_gap_d"),
            F.lit(0).cast("int").alias("refusing_n"),
            F.lit(0).cast("int").alias("ringing_n"),
            F.lit(0).cast("int").alias("deceased_flag"),
            F.lit(0).cast("int").alias("contact_confirmed_n"),
            F.lit(0).cast("int").alias("dcore_departure_flag"),
            F.lit(0).cast("int").alias("field_visit_flag"),
            F.lit(0).cast("int").alias("inbound_call_flag"),
            F.lit(0).cast("int").alias("not_reachable_flag"),
            F.lit(0).cast("int").alias("gone_contact_flag"),
            F.lit(0).cast("int").alias("ptp_flag"),
            F.lit(0).cast("int").alias("hardship_flag"),
            F.lit(0).cast("int").alias("recent3_attempt_dates_n"),
            F.lit(0).cast("int").alias("recent3_ringing_n"),
            F.lit(0).cast("int").alias("recent3_confirmed_n"),
            F.lit(None).cast("int").alias("recent3_oldest_gap_d"),
        )

    # ── Schema guard: return all-NULL if DCORE is unavailable ──────────────────
    followup_cols = set(followup.columns)
    if not _REQUIRED_FOLLOWUP_COLS.issubset(followup_cols):
        missing = _REQUIRED_FOLLOWUP_COLS - followup_cols
        LOG.warning(
            "build_a2_contact_signals: dcore_prm_followup_outcomes missing columns %s "
            "— emitting all-NULL contact signals (§4.4b guard will fire → unknown).",
            missing,
        )
        return _null_signals(base)

    empty_check = followup.limit(1).count()
    if empty_check == 0:
        LOG.warning(
            "build_a2_contact_signals: dcore_prm_followup_outcomes is empty "
            "— emitting all-NULL contact signals."
        )
        return _null_signals(base)

    # ── Schema guard: observation_spine required columns ──────────────────────
    _SPINE_REQUIRED = {"account_id", "observation_date", "agreement_id", "cif_id"}
    if not _SPINE_REQUIRED.issubset(set(observation_spine.columns)):
        missing = _SPINE_REQUIRED - set(observation_spine.columns)
        LOG.warning(
            "build_a2_contact_signals: dcore_observation_spine missing columns %s "
            "— emitting all-NULL contact signals (§4.4b guard will fire → unknown).",
            missing,
        )
        return _null_signals(base)

    # ── Step 1: bridge base pairs to DCORE via observation_spine ──────────────
    scope = observation_spine.select(
        "account_id",
        "observation_date",
        F.col("agreement_id").alias("iagreementseqno"),
        "cif_id",
    ).distinct()

    base_with_agreement = base.select("account_id", "observation_date", "t0").join(
        scope,
        on=["account_id", "observation_date"],
        how="left",
    )

    # ── Step 2: filter followup to window [t0, observation_date) ──────────────
    # result_name is carried directly on dcore_prm_followup_outcomes — no join needed.
    followup_dated = followup.withColumn(
        "_action_date", F.col("action_ts").cast("date")
    )
    scoped_followup = base_with_agreement.join(
        followup_dated.select(
            F.col("agreement_id").alias("iagreementseqno"),
            "_action_date",
            "action_code",
            F.col("result_category").alias("szcategorycode"),
            "result_name",
        ),
        on="iagreementseqno",
        how="inner",
    ).filter(
        (F.col("_action_date") >= F.col("t0"))
        & (F.col("_action_date") < F.col("observation_date"))
    )

    # ── Step 5: aggregate per (account_id, observation_date) ──────────────────
    aggregated = scoped_followup.groupBy("account_id", "observation_date").agg(
        # contact_attempts_n: distinct outbound attempt dates (OC + CB only)
        F.countDistinct(
            F.when(F.col("action_code").isin(_OUTBOUND_CODES), F.col("_action_date"))
        ).alias("contact_attempts_n"),
        # rpc_n: SUC outcomes on outbound calls only (OC / CB).
        # Scoping to _OUTBOUND_CODES naturally excludes field visits (FV),
        # inbound calls (IC), and all non-call channels without extra conditions.
        F.sum(
            F.when(
                (F.col("szcategorycode") == "SUC")
                & F.col("action_code").isin(_OUTBOUND_CODES),
                1,
            ).otherwise(0)
        ).alias("_rpc_n"),
        # rpc_proxy_n: RPC events confirmed via result_name across all categories
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_rpc_proxy_n"),
        # refusing_n: explicit refusal/hang-up/dispute — drives non_cooperative state
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_REFUSING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("refusing_n"),
        # ringing_n: ringing no-answer events — drives avoiding state (≥_TAU_RINGING_N)
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES), 1
            ).otherwise(0)
        ).alias("ringing_n"),
        # _deceased_n: confirmed or claimed deceased — drives deceased_flag
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_DECEASED_RESULT_NAMES), 1
            ).otherwise(0)
        ).alias("_deceased_n"),
        # uns_n: UNS category hits
        F.sum(F.when(F.col("szcategorycode") == "UNS", 1).otherwise(0)).alias("_uns_n"),
        # dcore_departure_n: contact records indicating customer left UAE
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_DEPARTURE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_dcore_departure_n"),
        # field_visit_n: field visit lifecycle events
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_FIELD_VISIT_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_field_visit_n"),
        # not_reachable_n: contact info structurally invalid — wrong number,
        # mobile switched off, line disconnected, ININ-OUTBOUND invalid codes.
        # Drives skip state (skip-tracing intervention required).
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_NOT_REACHABLE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_not_reachable_n"),
        # ptp_n: promise-to-pay or willingness-to-pay signals — customer committed
        # to pay, made an arrangement, or actually paid.  Output as ptp_flag for
        # downstream strategy routing; does not change the locatability state.
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(
                    _PROMISE_TO_PAY_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_ptp_n"),
        # hardship_n: hardship / special-case signals — death, disability, job loss,
        # bankruptcy, incarceration.  Output as hardship_flag for routing; does not
        # change the locatability state.
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_HARDSHIP_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_hardship_n"),
        # inbound_call_n: customer-initiated calls (IC) — distinct dates
        F.countDistinct(
            F.when(F.col("action_code").isin(_INBOUND_CODES), F.col("_action_date"))
        ).alias("_inbound_call_n"),
        # last_contact_attempt_dt: restricted to call-type codes (OC/CB/IC) — an
        # IA-logged administrative note must not make genuinely stale contact
        # evidence look fresh (would silently suppress the §4.4c guard below).
        F.max(
            F.when(F.col("action_code").isin(_CALL_CODES), F.col("_action_date"))
        ).alias("last_contact_attempt_dt"),
        # _last_confirmed_contact_dt: most recent date with confirmed RPC or inbound call
        F.max(
            F.when(
                (
                    (
                        (F.col("szcategorycode") == "SUC")
                        & F.col("action_code").isin(_OUTBOUND_CODES)
                    )
                    | F.upper(F.trim(F.col("result_name"))).isin(
                        _RIGHT_PARTY_CONTACT_RESULT_NAMES
                    )
                    | F.col("action_code").isin(_INBOUND_CODES)
                ),
                F.col("_action_date"),
            ).otherwise(F.lit(None).cast("date"))
        ).alias("_last_confirmed_contact_dt"),
    )

    # ── Step 5b: chronological recent-dead-contact check ──────────────────────
    # Dense-rank distinct outbound attempt dates (most recent = rank 1) per
    # (account_id, observation_date). Check if the last _TAU_NOT_REACHABLE_N
    # attempt dates were all dead-contact outcomes with no confirmed contact.
    _w_attempt_rank = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("_action_date").desc()
    )
    _outbound_ranked = scoped_followup.filter(
        F.col("action_code").isin(_OUTBOUND_CODES)
    ).withColumn("_attempt_date_rank", F.dense_rank().over(_w_attempt_rank))
    _last_n = _outbound_ranked.filter(
        F.col("_attempt_date_rank") <= _TAU_NOT_REACHABLE_N
    )
    _last_n_signals = _last_n.groupBy("account_id", "observation_date").agg(
        F.max("_attempt_date_rank").alias("_n_attempt_dates"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_NOT_REACHABLE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_last_n_dead"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_last_n_ringing"),
        F.sum(
            F.when(
                (
                    (F.col("szcategorycode") == "SUC")
                    & F.col("action_code").isin(_OUTBOUND_CODES)
                )
                | F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_last_n_confirmed"),
    )

    # ── Step 5c: recent-avoidance window (2026-10-22 amendment) ───────────────
    # Same chronological ranking as Step 5b, windowed to _TAU_RECENT_AVOIDANCE_N (3)
    # instead of _TAU_NOT_REACHABLE_N (2) — feeds the reachability override in
    # Node 4 (Step 4b), which downgrades a lifetime Reachable determination when the
    # most recent attempts are all ringing/no-answer and recent.
    _recent_m = _outbound_ranked.filter(
        F.col("_attempt_date_rank") <= _TAU_RECENT_AVOIDANCE_N
    )
    _recent_m_signals = _recent_m.groupBy("account_id", "observation_date").agg(
        F.max("_attempt_date_rank").alias("_recent3_n_dates"),
        F.min("_action_date").alias("_recent3_oldest_date"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_recent3_ringing_n"),
        F.sum(
            F.when(
                (
                    (F.col("szcategorycode") == "SUC")
                    & F.col("action_code").isin(_OUTBOUND_CODES)
                )
                | F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_recent3_confirmed_n"),
    )

    result = (
        aggregated.join(
            _last_n_signals, on=["account_id", "observation_date"], how="left"
        )
        .join(_recent_m_signals, on=["account_id", "observation_date"], how="left")
        .withColumn(
            "rpc_rate",
            F.when(
                F.col("contact_attempts_n") > 0,
                (F.col("_rpc_n") + F.col("_rpc_proxy_n")) / F.col("contact_attempts_n"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .withColumn(
            "uns_rate",
            F.when(
                F.col("contact_attempts_n") > 0,
                F.col("_uns_n") / F.col("contact_attempts_n"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .withColumn(
            "label_event_gap_d",
            F.datediff(F.col("observation_date"), F.col("last_contact_attempt_dt")),
        )
        .withColumn(
            "dcore_departure_flag",
            F.when(F.col("_dcore_departure_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "field_visit_flag",
            F.when(F.col("_field_visit_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "inbound_call_flag",
            F.when(F.col("_inbound_call_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "not_reachable_n",
            F.col("_not_reachable_n").cast("int"),
        )
        .withColumn(
            "not_reachable_flag",
            F.when(
                F.col("_n_attempt_dates").isNotNull()
                & (F.col("_n_attempt_dates") >= _TAU_NOT_REACHABLE_N)
                & (F.col("_last_n_dead") > 0)
                & (F.col("_last_n_confirmed") == 0),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "gone_contact_flag",
            F.when(
                F.col("_n_attempt_dates").isNotNull()
                & (F.col("_n_attempt_dates") >= _TAU_NOT_REACHABLE_N)
                & (F.col("_last_n_confirmed") == 0)
                & ((F.col("_last_n_dead") > 0) | (F.col("_last_n_ringing") > 0)),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "ptp_flag",
            F.when(F.col("_ptp_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "hardship_flag",
            F.when(F.col("_hardship_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "deceased_flag",
            F.when(F.col("_deceased_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "contact_confirmed_n",
            (F.col("_rpc_n") + F.col("_rpc_proxy_n")).cast("int"),
        )
        .withColumn(
            "last_attempt_contact_flag",
            F.when(
                F.col("_last_confirmed_contact_dt").isNotNull()
                & (
                    F.col("_last_confirmed_contact_dt")
                    == F.col("last_contact_attempt_dt")
                ),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "recent3_attempt_dates_n",
            F.coalesce(F.col("_recent3_n_dates"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_ringing_n",
            F.coalesce(F.col("_recent3_ringing_n"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_confirmed_n",
            F.coalesce(F.col("_recent3_confirmed_n"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_oldest_gap_d",
            F.when(
                F.col("_recent3_oldest_date").isNotNull(),
                F.datediff(F.col("observation_date"), F.col("_recent3_oldest_date")),
            ).otherwise(F.lit(None).cast("int")),
        )
        .drop(
            "_rpc_n",
            "_rpc_proxy_n",
            "_uns_n",
            "_dcore_departure_n",
            "_field_visit_n",
            "_inbound_call_n",
            "_not_reachable_n",
            "_last_confirmed_contact_dt",
            "_ptp_n",
            "_hardship_n",
            "_deceased_n",
            "_n_attempt_dates",
            "_last_n_dead",
            "_last_n_ringing",
            "_last_n_confirmed",
            "_recent3_n_dates",
            "_recent3_oldest_date",
            "_recent3_ringing_n",
            "_recent3_confirmed_n",
        )
    )

    # ── Left-join back to all base pairs (no DCORE coverage → NULLs / zeros) ──
    final = (
        base.select("account_id", "observation_date")
        .join(result, on=["account_id", "observation_date"], how="left")
        .fillna(
            {
                "refusing_n": 0,
                "ringing_n": 0,
                "deceased_flag": 0,
                "contact_confirmed_n": 0,
                "dcore_departure_flag": 0,
                "field_visit_flag": 0,
                "inbound_call_flag": 0,
                "not_reachable_flag": 0,
                "gone_contact_flag": 0,
                "not_reachable_n": 0,
                "last_attempt_contact_flag": 0,
                "ptp_flag": 0,
                "hardship_flag": 0,
                "recent3_attempt_dates_n": 0,
                "recent3_ringing_n": 0,
                "recent3_confirmed_n": 0,
            }
        )
    )

    n_rows = final.count()
    n_with_contact = final.filter(F.col("contact_attempts_n").isNotNull()).count()
    LOG.info(
        "build_a2_contact_signals: %d rows | DCORE coverage: %d (%.1f%%)",
        n_rows,
        n_with_contact,
        100.0 * n_with_contact / max(n_rows, 1),
    )

    return final


# ── Node 4: build_a2_locatability ────────────────────────────────────────────


def build_a2_locatability(  # pylint: disable=too-many-locals,too-many-positional-arguments
    base: DataFrame,
    login_presence: DataFrame,
    contact_signals: DataFrame,
    model_id: str,
    prm_contract: DataFrame = None,
    prm_client: DataFrame = None,
    feat_demographics_cif: DataFrame = None,
) -> DataFrame:
    """Join the three upstream passes and derive the location x reachability A2 axis.

    Args:
        base:            crx_cc_a2_base.
        login_presence:  crx_cc_a2_login_presence.
        contact_signals: crx_cc_a2_contact_signals.
        model_id:        `cc_60_180` | `cc_180_plus` | `rl_60_180` | `rl_180_plus`
            (or any other model_id) — selects the segment-aware `_TAU_RECENT_D` /
            `_TAU_LABEL_D` values (amendment, 2026-10-08). Resolved from
            `${globals:model_id}` via `params:model_id`. CC and RL both call this
            same function (model-agnostic — see module docstring).
        prm_contract:    Optional. CC only — carries `block_code_1`/`block_code_2`
            (Way4 deceased corroboration, T34). RL supplies nothing here (no Way4
            equivalent exists). `None` by default.
        prm_client:      Optional. CC only — paired with `prm_contract` to bridge
            to `cif_id` when `base` doesn't already carry one. `None` by default.
        feat_demographics_cif: Optional. Both domains — `ft_deceased_flag` at CIF
            grain (T34). RL supplies this directly since `base` already carries
            `cif_id`; CC supplies it alongside `prm_contract`/`prm_client` to build
            the bridge. `None` by default.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id                 (string)
            observation_date           (date)
            spell_id                   (int)
            deceased_flag              (int;    0/1)
            location_state             (string; 'Skip' | 'In Country' | 'Unknown')
            reachability_state         (string; 'Reachable' | 'Non-Reachable' | 'Unknown')
            a2_state                   (string; 'Deceased' | '<location> - <reachability>')
            departure_trail_flag       (int;    0/1 — location evidence)
            in_country_flag            (int;    0/1 — location evidence)
            contact_confirmed_flag     (int;    0/1 — reachability evidence)
            gone_contact_flag          (int;    0/1 — reachability evidence)
            recent_avoidance_flag      (int;    0/1 — reachability evidence; 2026-10-22
                                                amendment; downgrades a lifetime Reachable
                                                determination to Non-Reachable when the last
                                                recent3_attempt_dates_n (≤3) outbound attempts
                                                were all ringing/no-answer, zero confirmed, and
                                                within tau_label of observation_date)
            reachability_guard_triggered (string; NULL | '4.4b_insufficient_attempts'
                                                | '4.4c_stale_evidence')
            contact_attempts_n         (int)
            label_event_gap_d          (int)
            last_digital_login_gap_d   (int)
            last_login_foreign_flag    (int)
            ringing_n                  (int)
            recent3_ringing_n          (int;    ringing/no-answer count among the last
                                                _TAU_RECENT_AVOIDANCE_N ranked outbound attempts)
            recent3_attempt_dates_n    (int;    distinct outbound attempt dates found
                                                within that same last-N-ranked window, ≤3)
            recent3_oldest_gap_d       (int;    days; NULL if fewer than
                                                _TAU_RECENT_AVOIDANCE_N distinct outbound dates
                                                exist)
            location_unknown_reason    (string; NULL when location_state != 'Unknown',
                                                else 'no_login_on_record' |
                                                'recent_login_but_foreign' |
                                                'login_stale_beyond_window' | 'other')
            way4_deceased_flag         (int;    0/1 — CC-only Way4 block-code deceased
                                                corroboration, T34; always 0 if
                                                `prm_contract` has no block-code columns)
            demographics_deceased_flag (int;    0/1 — `ft_deceased_flag` corroboration,
                                                T34; always 0 if `feat_demographics_cif` is
                                                not supplied or `cif_id` cannot be resolved)
            deceased_flag_v2           (int;    0/1 — OR of `deceased_flag`,
                                                `way4_deceased_flag`, `demographics_deceased_flag`,
                                                T34; drives `a2_state`'s "Deceased" branch.
                                                `deceased_flag` itself is untouched pass-through)
            computed_at                (string)
    """
    tau_recent_d = _resolve_tau(model_id, _TAU_RECENT_D_BY_MODEL_ID)
    tau_label_d = _resolve_tau(model_id, _TAU_LABEL_D_BY_MODEL_ID)

    # ── Step 1: join all three passes ─────────────────────────────────────────
    df = base.join(
        login_presence,
        on=["account_id", "observation_date"],
        how="left",
    ).join(
        contact_signals,
        on=["account_id", "observation_date"],
        how="left",
    )

    # ── Step 2: derived presence/reachability flags ───────────────────────────
    # departure_trail_flag: positive departure signal — pre-T0 sources only.
    # Intentionally pure location evidence — no reachability term mixed in, per
    # GRR's instruction.
    departure_trail_flag = F.when(
        (F.col("travel_mcc_flag_h2") == 1)
        | (F.col("last_txn_foreign_flag") == 1)
        | (F.col("foreign_login_flag") == 1)
        | (
            F.col("casa_inflow_stop_gap_d").isNotNull()
            & (F.col("casa_inflow_stop_gap_d") > 180)
        )
        | (F.col("dcore_departure_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))

    # in_country_flag: recent UAE login — also pure location evidence.
    in_country_flag = F.when(
        (F.col("last_login_foreign_flag") == 0)
        & F.col("last_digital_login_gap_d").isNotNull()
        & (F.col("last_digital_login_gap_d") <= tau_recent_d),
        F.lit(1),
    ).otherwise(F.lit(0))

    # contact_confirmed_flag: any confirmed two-way contact (outbound RPC or inbound call)
    contact_confirmed_flag = F.when(
        (F.col("contact_confirmed_n") > 0) | (F.col("inbound_call_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))

    # recent_avoidance_flag (2026-10-22 amendment): downgrades a lifetime-established
    # Reachable determination when the most recent _TAU_RECENT_AVOIDANCE_N outbound
    # attempts were ALL ringing/no-answer, zero confirmed among them, and recent
    # (within the segment's tau_label window) — see Step 4 below.
    recent_avoidance_flag = F.when(
        (F.col("recent3_attempt_dates_n") >= _TAU_RECENT_AVOIDANCE_N)
        & (F.col("recent3_confirmed_n") == 0)
        & (F.col("recent3_ringing_n") == _TAU_RECENT_AVOIDANCE_N)
        & F.col("recent3_oldest_gap_d").isNotNull()
        & (F.col("recent3_oldest_gap_d") <= tau_label_d),
        F.lit(1),
    ).otherwise(F.lit(0))

    df = (
        df.withColumn("departure_trail_flag", departure_trail_flag)
        .withColumn("in_country_flag", in_country_flag)
        .withColumn("contact_confirmed_flag", contact_confirmed_flag)
        .withColumn("recent_avoidance_flag", recent_avoidance_flag)
    )

    # ── Step 3: location_state — purely departure_trail_flag / in_country_flag ─
    location_state = (
        F.when(
            (F.col("departure_trail_flag") == 1) & (F.col("in_country_flag") == 0),
            F.lit("Skip"),
        )
        .when(F.col("in_country_flag") == 1, F.lit("In Country"))
        .otherwise(F.lit("Unknown"))
    )

    df = df.withColumn("location_state", location_state)

    # ── Step 3b: location_unknown_reason — diagnostic, present only when relevant —
    # Mirrors the EDA snippet's already-proven `_location_unknown_cause_expr`
    # (t29_a2_locatability_v2_eda.py:163-182), now shipped as a first-class column
    # against this function's own resolved tau_recent_d rather than something only
    # the EDA snippet can compute (T29 Oct-12 retest root-cause finding).
    location_unknown_reason = F.when(
        F.col("location_state") != "Unknown", F.lit(None).cast("string")
    ).otherwise(
        F.when(
            F.col("last_digital_login_gap_d").isNull(),
            F.lit("no_login_on_record"),
        )
        .when(
            (F.col("last_login_foreign_flag") == 1)
            & (F.col("last_digital_login_gap_d") <= tau_recent_d),
            F.lit("recent_login_but_foreign"),
        )
        .when(
            F.col("last_digital_login_gap_d") > tau_recent_d,
            F.lit("login_stale_beyond_window"),
        )
        .otherwise(F.lit("other"))
    )

    df = df.withColumn("location_unknown_reason", location_unknown_reason)

    # ── Step 4: reachability_state — guards, then confirmed-contact vs dead ────
    reachability_guard_triggered = (
        F.when(
            F.col("contact_attempts_n").isNull()
            | (F.col("contact_attempts_n") < _TAU_A_ATTEMPTS),
            F.lit("4.4b_insufficient_attempts"),
        )
        .when(
            F.col("label_event_gap_d").isNull()
            | (F.col("label_event_gap_d") > tau_label_d),
            F.lit("4.4c_stale_evidence"),
        )
        .otherwise(F.lit(None).cast("string"))
    )

    df = df.withColumn("reachability_guard_triggered", reachability_guard_triggered)

    reachability_state = (
        F.when(F.col("reachability_guard_triggered").isNotNull(), F.lit("Unknown"))
        .when(F.col("recent_avoidance_flag") == 1, F.lit("Non-Reachable"))
        .when(F.col("contact_confirmed_flag") == 1, F.lit("Reachable"))
        .when(
            (F.col("gone_contact_flag") == 1)
            & (F.col("last_attempt_contact_flag") == 0),
            F.lit("Non-Reachable"),
        )
        .otherwise(F.lit("Unknown"))
    )

    df = df.withColumn("reachability_state", reachability_state)

    # ── Step 4b: deceased corroboration beyond DCORE (T34, 2026-10-12) ──────
    # Way4 block code — CC only, activates iff prm_contract carries block codes.
    if (
        prm_contract is not None
        and "block_code_1" in prm_contract.columns
        and "block_code_2" in prm_contract.columns
    ):
        contract_block_codes = prm_contract.select(
            F.col("contract_id").alias("account_id"),
            "observation_date",
            F.upper(F.trim(F.col("block_code_1"))).alias("_block_code_1"),
            F.upper(F.trim(F.col("block_code_2"))).alias("_block_code_2"),
        )
        df = df.join(
            contract_block_codes, on=["account_id", "observation_date"], how="left"
        )
        way4_deceased_flag = F.when(
            F.col("_block_code_1").isin(_WAY4_DECEASED_BLOCK_CODES)
            | F.col("_block_code_2").isin(_WAY4_DECEASED_BLOCK_CODES),
            F.lit(1),
        ).otherwise(F.lit(0))
        df = df.withColumn("way4_deceased_flag", way4_deceased_flag).drop(
            "_block_code_1", "_block_code_2"
        )
    else:
        df = df.withColumn("way4_deceased_flag", F.lit(0))

    # Demographics — both domains. Use cif_id already on the frame if present (RL);
    # otherwise bridge via prm_contract/prm_client if supplied (CC). Skip cleanly if
    # neither path resolves cif_id.
    if feat_demographics_cif is not None:
        if (
            "cif_id" not in df.columns
            and prm_contract is not None
            and prm_client is not None
        ):
            cif_bridge = _build_cif_bridge(prm_contract, prm_client)
            df = df.join(
                cif_bridge, on=df["account_id"] == cif_bridge["contract_id"], how="left"
            ).drop("contract_id")
        if "cif_id" in df.columns:
            demo = feat_demographics_cif.select(
                "cif_id", F.col("ft_deceased_flag").alias("_ft_deceased_flag")
            )
            df = df.join(demo, on="cif_id", how="left")
            demographics_deceased_flag = F.when(
                F.col("_ft_deceased_flag") == 1, F.lit(1)
            ).otherwise(F.lit(0))
            df = df.withColumn(
                "demographics_deceased_flag", demographics_deceased_flag
            ).drop("_ft_deceased_flag")
        else:
            df = df.withColumn("demographics_deceased_flag", F.lit(0))
    else:
        df = df.withColumn("demographics_deceased_flag", F.lit(0))

    # ── Step 5: deceased pre-guard + combined state ──────────────────────────
    deceased_flag_v2 = F.when(
        (F.col("deceased_flag") == 1)
        | (F.col("way4_deceased_flag") == 1)
        | (F.col("demographics_deceased_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))
    df = df.withColumn("deceased_flag_v2", deceased_flag_v2)

    a2_state = F.when(F.col("deceased_flag_v2") == 1, F.lit("Deceased")).otherwise(
        F.concat(F.col("location_state"), F.lit(" - "), F.col("reachability_state"))
    )

    df = df.withColumn("a2_state", a2_state)

    # ── Step 6: emit typed schema ────────────────────────────────────────────
    output = df.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("deceased_flag").cast("int"),
        F.col("location_state").cast("string"),
        F.col("reachability_state").cast("string"),
        F.col("a2_state").cast("string"),
        F.col("departure_trail_flag").cast("int"),
        F.col("in_country_flag").cast("int"),
        F.col("contact_confirmed_flag").cast("int"),
        F.col("gone_contact_flag").cast("int"),
        F.col("recent_avoidance_flag").cast("int"),
        F.col("reachability_guard_triggered").cast("string"),
        F.col("contact_attempts_n").cast("int"),
        F.col("label_event_gap_d").cast("int"),
        F.col("last_digital_login_gap_d").cast("int"),
        F.col("last_login_foreign_flag").cast("int"),
        F.col("ringing_n").cast("int"),
        F.col("recent3_ringing_n").cast("int"),
        F.col("recent3_attempt_dates_n").cast("int"),
        F.col("recent3_oldest_gap_d").cast("int"),
        F.col("location_unknown_reason").cast("string"),
        F.col("way4_deceased_flag").cast("int"),
        F.col("demographics_deceased_flag").cast("int"),
        F.col("deceased_flag_v2").cast("int"),
        F.lit(datetime.date.today().isoformat()).alias("computed_at"),
    )

    _log_a2_stats(output)

    return output


def _log_a2_stats(df: DataFrame) -> None:
    """Log state distribution for post-run monitoring."""
    try:
        n_total = df.count()
        state_dist = df.groupBy("a2_state").count().collect()

        LOG.info("build_a2_locatability: total rows = %d", n_total)
        for row in state_dist:
            pct = 100.0 * row["count"] / max(n_total, 1)
            LOG.info(
                "  a2_state=%-25s n=%7d  (%.1f%%)",
                str(row["a2_state"]),
                row["count"],
                pct,
            )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("build_a2_locatability: stats logging failed: %s", exc)
