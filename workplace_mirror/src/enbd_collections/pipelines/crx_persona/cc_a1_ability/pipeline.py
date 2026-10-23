"""Kedro pipeline: T26 — A1 Ability axis v1.

# pylint: disable=line-too-long

Nine-node modular pipeline that derives the A1 income-ability axis and emits
the shipped persona column ``a1_state`` at (account_id, observation_date) grain.

Architecture:
    build_a1_base                  → crx_cc_a1_base                  [Node 1]
    build_a1_cif_bridge            → crx_cc_a1_cif_enriched          [Node 2]
    build_a1_group_b_income        → crx_cc_a1_group_b_income        [Node 3] ┐
    build_a1_group_b_bureau        → crx_cc_a1_group_b_bureau        [Node 4] ┤ parallel
    build_a1_group_c               → crx_cc_a1_group_c               [Node 5] ┤ (T0-anchored)
    build_a1_group_b_income_recent → crx_cc_a1_group_b_income_recent [Node 3r] ┤
    build_a1_group_b_bureau_recent → crx_cc_a1_group_b_bureau_recent [Node 4r] ┤ parallel
    build_a1_group_c_recent        → crx_cc_a1_group_c_recent        [Node 5r] ┘ (obs-date)
    build_a1_classify              → crx_cc_a1_ability               [Node 6]  ← shipped axis

Inputs:
    cc_spine                          Model-id-scoped spine (account_id, observation_date)
    crx_cc_spell_table                T03b — spell grain (account_id, spell_id, t0)
    crx_cc_departure_signature        T06  — Group A income signals (R14 reuse)
    prm_contract / prm_client         CIF bridge (contract_id → cif_id)
    feat_payroll_indicator            retail.feature_space — monthly payroll flag
    feat_casa_eod_balance             retail.feature_space — monthly CASA balance
    wm_fea_salary_days_since_increment WM — weekly salary recency + amount
    wm_fea_casa_weekly_repeated_inflow WM — weekly recurring non-salary inflow
    wm_fea_casa_cc_inflow_outflow     WM — weekly generic CASA inflow/outflow (all types)
    stg_aecb_salary_history           AECB — bureau salary history (6m window)
    prm_bureau_alert_enriched         AECB — bureau alerts (90d window)
    prm_bureau_cif_bridge             bureau file UUID → cif_id bridge
    fea_monthly_aecb_alerts           retail.feature_space — pre-engineered alert features
                                      (secondary source for a1_new_salary_acct_flag)
    crx_cc_payment_trajectory         T04b — payment trajectory (spell grain)
    crx_cc_utilisation_features       T05  — utilisation features (spell grain)
    prm_balance                       primary — CC outstanding balance (PIT at T0)

Output:
    crx_cc_a1_ability — A1 axis for every (account_id, observation_date) in cc_spine.
    a1_state ∈ {ability_high, ability_moderate, ability_limited, ability_unknown}.

    ⚠ All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.
    ⚠ WM feature coverage on delinquent CC population is UNPROVEN until T26 CHK-6.
    ⚠ Group B/C sibling-repo columns are NULL where schema guard fires.

Run with:
    kedro run --pipeline=crx_cc_a1_ability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a1_base,
    build_a1_cif_bridge,
    build_a1_classify,
    build_a1_group_b_bureau,
    build_a1_group_b_bureau_recent,
    build_a1_group_b_income,
    build_a1_group_b_income_recent,
    build_a1_group_c,
    build_a1_group_c_recent,
)

_TAGS = ["crx", "a1", "ability", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node A1 Ability pipeline."""
    return Pipeline(
        [
            # ── Node 1: spine→spell window join + Group A departure signals ──
            node(
                func=build_a1_base,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "crx_cc_departure_signature",
                ],
                outputs="crx_cc_a1_base",
                name="build_crx_a1_base",
                tags=_TAGS,
            ),
            # ── Node 2: resolve CIF; emit CIF-keyed subset ──────────────────
            node(
                func=build_a1_cif_bridge,
                inputs=[
                    "crx_cc_a1_base",
                    "prm_contract",
                    "prm_client",
                ],
                outputs="crx_cc_a1_cif_enriched",
                name="build_crx_a1_cif_bridge",
                tags=_TAGS,
            ),
            # ── Node 3: WM + feature_space income signals (parallel) ────────
            node(
                func=build_a1_group_b_income,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1_group_b_income",
                name="build_crx_a1_group_b_income",
                tags=_TAGS,
            ),
            # ── Node 4: AECB bureau + WM recurring signals (parallel) ───────
            node(
                func=build_a1_group_b_bureau,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                ],
                outputs="crx_cc_a1_group_b_bureau",
                name="build_crx_a1_group_b_bureau",
                tags=_TAGS,
            ),
            # ── Node 3r: observation_date-anchored income signals (parallel) ─
            node(
                func=build_a1_group_b_income_recent,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1_group_b_income_recent",
                name="build_crx_a1_group_b_income_recent",
                tags=_TAGS,
            ),
            # ── Node 4r: observation_date-anchored bureau signals (parallel) ─
            node(
                func=build_a1_group_b_bureau_recent,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                ],
                outputs="crx_cc_a1_group_b_bureau_recent",
                name="build_crx_a1_group_b_bureau_recent",
                tags=_TAGS,
            ),
            # ── Node 5: payment trajectory + utilisation + balance (parallel) ─
            node(
                func=build_a1_group_c,
                inputs=[
                    "crx_cc_a1_base",
                    "crx_cc_payment_trajectory",
                    "crx_cc_utilisation_features",
                    "prm_balance",
                ],
                outputs="crx_cc_a1_group_c",
                name="build_crx_a1_group_c",
                tags=_TAGS,
            ),
            # ── Node 5r: obs-date-anchored balance (parallel with Node 5) ────
            node(
                func=build_a1_group_c_recent,
                inputs=["crx_cc_a1_base", "prm_balance"],
                outputs="crx_cc_a1_group_c_recent",
                name="build_crx_a1_group_c_recent",
                tags=_TAGS,
            ),
            # ── Node 6: assemble + classify → shipped persona axis ──────────
            node(
                func=build_a1_classify,
                inputs=[
                    "crx_cc_a1_base",
                    "crx_cc_a1_group_b_income",
                    "crx_cc_a1_group_b_bureau",
                    "crx_cc_a1_group_c",
                    "crx_cc_a1_group_b_income_recent",
                    "crx_cc_a1_group_b_bureau_recent",
                    "crx_cc_a1_group_c_recent",
                ],
                outputs="crx_cc_a1_ability",
                name="build_crx_a1_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
