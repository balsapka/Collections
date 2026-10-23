"""Kedro pipeline: RL-A2-1 — A2 Locatability axis for Retail Loans.

# pylint: disable=line-too-long

Four-node pipeline adapted from CC A2 locatability for monthly-grain RL accounts.
Reuses CC nodes via thin wrappers; Node 4 imports the CC function directly.
Node 4's underlying derivation is RL-A2-3's location x reachability redesign,
promoted 2026-10-22 to replace RL-A2-1's original 7-state waterfall (see
``RESULTS_RL.md``) — the import path is unchanged, only the implementation
behind ``build_a2_locatability`` changed.

Architecture:
    build_rl_a2_base              → crx_rl_a2_base              [Node 1]
    build_rl_a2_login_presence    → crx_rl_a2_login_presence    [Node 2]
    build_rl_a2_contact_signals   → crx_rl_a2_contact_signals   [Node 3]
    build_a2_locatability         → crx_rl_a2_locatability      [Node 4]  ← shipped axis

Node 1 inputs: crx_rl_a4_spine, crx_rl_departure_signature
    crx_rl_a4_spine already carries (account_id, observation_date, spell_id,
    t0, cif_id). Departure signals sourced from crx_rl_departure_signature
    (RL-A2-2 pre-computation pipeline — all 4 signals derived for real).

Node 2: obs_month_end=True — RL observation dates are month-end.

Node 3: dcore_observation_spine = RL-scoped DCORE spine (built by RL-D5 pipeline).
    Applies 24m partition floor on dcore_prm_followup_outcomes before calling
    build_a2_contact_signals (performance guard per TASKS_RL.md).

Node 4: build_a2_locatability imported directly from cc_a2_locatability.nodes.
    No RL-specific logic needed — a2_state derivation is domain-agnostic.
    RL has no Way4-equivalent block-code table, so `prm_contract`/`prm_client`
    are not supplied here (stay at their Python defaults, `None`) —
    `crx_rl_a2_base` already carries `cif_id` directly, so no CIF bridge is
    needed either; `feat_demographics_cif` is supplied for deceased
    corroboration (T34). This coverage is unvalidated — no RL PROD run has
    measured it yet (see `RESULTS_RL.md`).

Run with:
    kedro run --pipeline=crx_rl_a2_locatability
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.nodes import (
    build_a2_locatability,
)

from .nodes import (
    build_rl_a2_base,
    build_rl_a2_contact_signals,
    build_rl_a2_login_presence,
)

_TAGS = ["crx", "a2", "locatability", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node RL A2 Locatability pipeline."""
    return Pipeline(
        [
            # ── Node 1: spine + departure stub (FX leakage, no spell join) ──
            node(
                func=build_rl_a2_base,
                inputs=[
                    "crx_rl_a4_spine",
                    "crx_rl_departure_signature",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a2_base",
                name="build_rl_a2_base",
                tags=_TAGS,
            ),
            # ── Node 2: obs-date-anchored digital login presence ──────────
            node(
                func=build_rl_a2_login_presence,
                inputs=[
                    "crx_rl_a2_base",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_rl_a2_login_presence",
                name="build_rl_a2_login_presence",
                tags=_TAGS,
            ),
            # ── Node 3: DCORE contact signals (24m floor, RL-D5 spine) ─────
            node(
                func=build_rl_a2_contact_signals,
                inputs=[
                    "crx_rl_a2_base",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a2_contact_signals",
                name="build_rl_a2_contact_signals",
                tags=_TAGS,
            ),
            # ── Node 4: assemble + derive a2_state (CC function, no wrap) ──
            node(
                func=build_a2_locatability,
                inputs={
                    "base": "crx_rl_a2_base",
                    "login_presence": "crx_rl_a2_login_presence",
                    "contact_signals": "crx_rl_a2_contact_signals",
                    "model_id": "params:model_id",
                    "feat_demographics_cif": "feat_demographics_cif",
                },
                outputs="crx_rl_a2_locatability",
                name="build_rl_a2_locatability",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
