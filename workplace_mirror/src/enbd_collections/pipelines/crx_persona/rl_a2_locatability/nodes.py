"""RL A2 Locatability axis — RL-specific adapter nodes (RL-A2-1).

# pylint: disable=too-many-locals

Four-node pipeline adapter that reuses CC A2 logic via thin wrappers:

    build_rl_a2_base            → crx_rl_a2_base            [Node 1]
    build_rl_a2_login_presence  → crx_rl_a2_login_presence  [Node 2]
    build_rl_a2_contact_signals→ crx_rl_a2_contact_signals[Node 3]
    build_a2_locatability       → crx_rl_a2_locatability    [Node 4] (CC import)

Node 1 difference from CC: crx_rl_a4_spine already carries (account_id,
observation_date, spell_id, t0, cif_id) from the spine-projection join (rl_a4_spine
pipeline) — no separate spell table join is needed. Departure signals sourced
from crx_rl_departure_signature (RL-A2-2 pre-computation pipeline).

Departure signals (RL-A2-2):
    travel_mcc_flag_h2     — H2 debit travel MCC from comp_financial_tran_repos_dly
    last_txn_foreign_flag  — FX leakage proxy (99.88% CIF coverage)
    foreign_login_flag     — PIT foreign login from prm_digital_login_monthly
    casa_inflow_stop_gap_d — from crx_rl_departure_signature itself (Pass B)

Node 2: obs_month_end=True because RL observation dates are month-end.

Node 3: applies DCORE 24-month partition floor before calling CC function
    (action_ts filter for performance — dcore_prm_followup_outcomes is large).
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.nodes import (
    build_a2_contact_signals,
    build_a2_locatability,  # noqa: F401 — re-exported for pipeline use
    build_a2_login_presence,
)

LOG = logging.getLogger(__name__)

__all__ = [
    "build_rl_a2_base",
    "build_rl_a2_login_presence",
    "build_rl_a2_contact_signals",
    "build_a2_locatability",
]


# ── Node 1: build_rl_a2_base ───────────────────────────────────────────────────


def build_rl_a2_base(
    crx_rl_a4_spine: DataFrame,
    crx_rl_departure_signature: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Build RL A2 base. Mirrors crx_cc_a2_base schema.

    crx_rl_a4_spine already carries (account_id, observation_date, spell_id,
    t0, cif_id). No separate spell table join needed.

    Departure signals sourced from crx_rl_departure_signature (RL-A2-2 pipeline):
        travel_mcc_flag_h2     — H2 debit travel MCC from comp_financial_tran_repos_dly
        last_txn_foreign_flag  — FX leakage proxy (99.88% CIF coverage)
        foreign_login_flag     — PIT foreign login from prm_digital_login_monthly
        casa_inflow_stop_gap_d — forwarded from crx_rl_a4_class

    Left-join crx_rl_departure_signature on (account_id, observation_date).
    All 4 departure-trail columns are non-null on join hit (coalesced in RL-A2-2 Node 3).

    Args:
        crx_rl_a4_spine:            RL spine at (account_id, observation_date) grain.
            Required cols: account_id, observation_date, spell_id, t0, cif_id.
        crx_rl_departure_signature: RL departure pre-computation (RL-A2-2).
            Required cols: account_id, observation_date, travel_mcc_flag_h2,
            last_txn_foreign_flag, foreign_login_flag, casa_inflow_stop_gap_d.
        crx_persona:                Persona param dict with persona_start_date /
                                    persona_end_date.

    Returns:
        DataFrame at grain (account_id, observation_date) — schema matches
        crx_cc_a2_base departure-trail columns::

            account_id              (string)
            observation_date        (date)
            spell_id                (int)
            t0                      (date)
            cif_id                  (string)
            travel_mcc_flag_h2      (int)    0/1
            last_txn_foreign_flag   (int)    0/1
            foreign_login_flag      (int)    0/1
            casa_inflow_stop_gap_d  (double) NULL if no salary inflow in [M0-24m, M0)
    """
    base = crx_rl_a4_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("cif_id").cast("string"),
    )

    depart = crx_rl_departure_signature.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
        F.col("last_txn_foreign_flag").cast("int"),
        F.col("foreign_login_flag").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
    )

    result = base.join(
        depart, on=["account_id", "observation_date"], how="left"
    ).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("cif_id").cast("string"),
        F.coalesce(F.col("travel_mcc_flag_h2"), F.lit(0))
        .cast("int")
        .alias("travel_mcc_flag_h2"),
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0))
        .cast("int")
        .alias("last_txn_foreign_flag"),
        F.coalesce(F.col("foreign_login_flag"), F.lit(0))
        .cast("int")
        .alias("foreign_login_flag"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
    )

    n_rows = result.count()
    LOG.info(
        "build_rl_a2_base [%s → %s]: %d spine rows | departure signals joined from "
        "crx_rl_departure_signature",
        crx_persona["persona_start_date"],
        crx_persona["persona_end_date"],
        n_rows,
    )

    return result


# ── Node 2: build_rl_a2_login_presence ─────────────────────────────────────────


def build_rl_a2_login_presence(
    base: DataFrame,
    prm_login: DataFrame,
) -> DataFrame:
    """Obs-date-anchored digital presence signals for RL. Thin wrapper.

    Delegates to build_a2_login_presence with obs_month_end=True because RL
    observation dates are month-end (the observation month is fully closed,
    so the login month is safe to include).

    Args:
        base:      crx_rl_a2_base — must carry cif_id (propagated from Node 1).
        prm_login: prm_digital_login_monthly.

    Returns:
        crx_rl_a2_login_presence — same schema as crx_cc_a2_login_presence.
    """
    return build_a2_login_presence(
        base=base,
        prm_login=prm_login,
        obs_month_end=True,
    )


# ── Node 3: build_rl_a2_contact_signals ────────────────────────────────────────


def build_rl_a2_contact_signals(
    base: DataFrame,
    observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """DCORE contact signals for RL. Thin wrapper with 24m partition floor.

    Applies a partition floor on dcore_prm_followup_outcomes to avoid scanning
    the full DCORE history (performance guard per TASKS_RL.md). Floor =
    persona_start_date - 24m; covers all T0 dates in the persona window plus
    the full post-T0 delinquency window up to observation_date.

    Delegates to build_a2_contact_signals from CC (R14 reuse).

    Args:
        base:              crx_rl_a2_base.
        observation_spine: dcore_observation_spine (RL-scoped, built by RL-D5).
            Required cols: account_id, observation_date, agreement_id, cif_id.
        followup_outcomes: dcore_prm_followup_outcomes.
        crx_persona:       params dict with persona_start_date.

    Returns:
        crx_rl_a2_contact_signals — same schema as crx_cc_a2_contact_signals.
    """
    persona_start_date = crx_persona["persona_start_date"]
    dcore_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=24)
    ).isoformat()

    followup_filtered = followup_outcomes.filter(
        F.col("action_ts").cast("date") >= F.lit(dcore_floor)
    )

    return build_a2_contact_signals(
        base=base,
        observation_spine=observation_spine,
        followup=followup_filtered,
    )
