# pylint: disable=R0801
"""Kedro pipeline: RL-A1-1/9 — A1 Ability axis for Retail Loans (4-node).

# pylint: disable=line-too-long

Four-node modular pipeline (T0 nodes removed in RL-A1-5 cleanup;
Node 4b Group D removed in RL-A1-5 cleanup — feat_loan_application_risk pull_date unknown;
Group A departure removed in RL-A1-6 cleanup; Node 1 base join eliminated in
RL-A1-7 cleanup — crx_rl_a4_spine feeds enrichment nodes directly).
cif_id is carried directly in crx_rl_a4_spine — no separate CIF bridge node needed.

Architecture:
    build_rl_a1_group_b_income_recent → crx_rl_a1_group_b_income_recent  [Node 2r] ┐ parallel (obs-date)
    build_rl_a1_group_b_bureau_recent → crx_rl_a1_group_b_bureau_recent  [Node 3r] ┤
    build_rl_a1_group_c_recent        → crx_rl_a1_group_c_recent         [Node 4r] ┘
    build_rl_a1_classify              → crx_rl_a1_ability                [Node 5]  ← shipped axis

Node 5 inputs: crx_rl_a4_spine, crx_rl_departure_signature, crx_rl_spell_table,
    crx_rl_a1_group_b_income_recent, crx_rl_a1_group_b_bureau_recent,
    crx_rl_a1_group_c_recent.
    The eosb_like_flag / prior_spell_cnt_12m lookup (formerly from the superseded
    crx_rl_a4_class) is inlined in build_rl_a1_classify, read directly from
    crx_rl_departure_signature / crx_rl_spell_table.

Node 2r (RL-A1-23) also takes wm_fea_external_loan_payments — a weekly
PIT-joinable WM feature table (no R2 look-ahead flag) feeding High Arm 6b
(ext_loan_payment_amt_h2_recent), additive sibling to the existing Arm 6.

Run with:
    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a1_classify,
    build_rl_a1_group_b_bureau_recent,
    build_rl_a1_group_b_income_recent,
    build_rl_a1_group_c_recent,
)

_TAGS = ["crx", "a1", "ability", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node RL A1 Ability pipeline."""
    return Pipeline(
        [
            # ── Node 2r: obs-date-anchored income signals ─────────────────
            node(
                func=build_rl_a1_group_b_income_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_external_loan_payments",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_b_income_recent",
                name="build_rl_a1_group_b_income_recent",
                tags=_TAGS,
            ),
            # ── Node 3r: obs-date-anchored bureau + recurring signals ─────
            node(
                func=build_rl_a1_group_b_bureau_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                    "feature_retail_loans",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_b_bureau_recent",
                name="build_rl_a1_group_b_bureau_recent",
                tags=_TAGS,
            ),
            # ── Node 4r: obs-date-anchored EMI coverage window ────────────
            node(
                func=build_rl_a1_group_c_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "int_loan_master",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_c_recent",
                name="build_rl_a1_group_c_recent",
                tags=_TAGS,
            ),
            # ── Node 5: assemble + classify → shipped persona axis ────────
            node(
                func=build_rl_a1_classify,
                inputs=[
                    "crx_rl_a4_spine",
                    "crx_rl_departure_signature",
                    "crx_rl_spell_table",
                    "crx_rl_a1_group_b_income_recent",
                    "crx_rl_a1_group_b_bureau_recent",
                    "crx_rl_a1_group_c_recent",
                ],
                outputs="crx_rl_a1_ability",
                name="build_rl_a1_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
