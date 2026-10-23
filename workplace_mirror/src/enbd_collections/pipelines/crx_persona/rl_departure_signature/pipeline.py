"""Kedro pipeline: RL-A2-2 — RL Departure Signature (standalone, no A4 dependency).

# pylint: disable=line-too-long

5-node pipeline that derives all departure-trail signals for RL accounts.
Runs BEFORE rl_a1_ability; Node 5 (build_rl_a1_classify) depends on
crx_rl_departure_signature for eosb_like_flag.

    build_rl_depart_spine            → crx_rl_depart_spine            [Node 0]
    build_rl_depart_casa_signals     → crx_rl_depart_casa_signals     [Node 1]
    build_rl_depart_travel_mcc       → crx_rl_depart_travel_mcc       [Node 2]
    build_rl_depart_foreign_signals  → crx_rl_depart_foreign_signals  [Node 3]
    build_rl_departure_final         → crx_rl_departure_signature     [Node 4]

Node 0: spell-scoped spine — mirrors build_rl_a4_spine_projection steps 1–4
    without the A4 label join. Produces (cif_id, account_id, observation_date,
    spell_id, t0) at obs-date grain scoped to persona window.

Node 1: CASA salary inflow stop (Pass B) + payroll stop (Pass I).
    R20 CIF scope applied before date filter.
    Same logic as former rl_a4_class Node 1 (build_rl_a4_casa_signals).

Node 2: comp_financial_tran_repos_dly.merchant_category → travel_mcc_flag_h2.
    MCC list + keyword regex imported from cc_departure_signature.nodes.

Node 3: feat_fx_leakage → last_txn_foreign_flag.
        prm_digital_login_monthly → foreign_login_flag (PIT per observation_date).

Node 4: assembles all 4 signal groups into crx_rl_departure_signature.
    CASA signals sourced from Node 1 (no A4 dependency).

Run with:
    kedro run --pipeline=crx_rl_departure_signature
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_depart_casa_signals,
    build_rl_depart_foreign_signals,
    build_rl_depart_spine,
    build_rl_depart_travel_mcc,
    build_rl_departure_final,
)

_TAGS = ["crx", "rl_departure_signature", "rl_a2"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 5-node RL departure signature pipeline."""
    return Pipeline(
        [
            # ── Node 0: spell-scoped spine (no A4 dependency) ───────────────
            node(
                func=build_rl_depart_spine,
                inputs=[
                    "rl_spine",
                    "crx_rl_spell_table",
                    "params:crx_persona",
                ],
                outputs="crx_rl_depart_spine",
                name="build_rl_depart_spine",
                tags=_TAGS,
            ),
            # ── Node 1: CASA salary + payroll signals (R20: 2.4B row scope) ─
            node(
                func=build_rl_depart_casa_signals,
                inputs=[
                    "crx_rl_depart_spine",
                    "comp_financial_tran_repos_dly",
                    "feat_payroll_indicator",
                    "params:crx_persona",
                ],
                outputs="crx_rl_depart_casa_signals",
                name="build_rl_depart_casa_signals",
                tags=_TAGS,
            ),
            # ── Node 2: travel MCC from CASA debit transactions ─────────────
            node(
                func=build_rl_depart_travel_mcc,
                inputs=[
                    "crx_rl_depart_spine",
                    "comp_financial_tran_repos_dly",
                ],
                outputs="crx_rl_depart_travel_mcc",
                name="build_rl_depart_travel_mcc",
                tags=_TAGS,
            ),
            # ── Node 3: FX leakage + digital login foreign flag ─────────────
            node(
                func=build_rl_depart_foreign_signals,
                inputs=[
                    "crx_rl_depart_spine",
                    "feat_fx_leakage",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_rl_depart_foreign_signals",
                name="build_rl_depart_foreign_signals",
                tags=_TAGS,
            ),
            # ── Node 4: assemble final departure signature ──────────────────
            node(
                func=build_rl_departure_final,
                inputs=[
                    "crx_rl_depart_spine",
                    "crx_rl_depart_travel_mcc",
                    "crx_rl_depart_foreign_signals",
                    "crx_rl_depart_casa_signals",
                ],
                outputs="crx_rl_departure_signature",
                name="build_rl_departure_final",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
