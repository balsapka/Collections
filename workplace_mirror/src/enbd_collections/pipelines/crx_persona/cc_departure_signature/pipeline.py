"""Kedro pipeline: T06 — CC departure signature & history shape features.

Modular 15-node pipeline replacing the former single-node monolith.
Each pass is cached independently — fix Pass K, only re-run:
    kedro run --pipeline=crx_cc_departure_signature --from-nodes=build_crx_departure_pass_k

Input wiring note:
    Fourteen raw inputs cover three categories:
      1. CC tables: crx_cc_transactions (T04c intermediate — replaces prm_transaction;
         departure + fee txns), prm_turnovers (lifetime fee totals),
         prm_contract (tenure + cif bridge),
         prm_client (CIF bridge — maps Way4 client_idt to bank CIF number)
      2. CRX persona tables: crx_cc_spell_table (spell anchor + history),
         crx_cc_payment_trajectory (w_pre truncation columns from T04b)
      3. Cross-domain tables: int_bureau_pull_monthly (AECB leverage slope — T21 DROP confirmed),
         feat_product_holding (relationship breadth),
         comp_financial_tran_repos_dly (CASA inflow signals — R20 scoped),
         fea_monthly_aecb_alerts (AECB alert signals — REUSE from retail.feature_space;
           R2 PASS + R7 PASS confirmed 2026-08-21),
         feat_fx_leakage (cross-border FX leakage — fea_monthly_agg_fx_leakage),
         feat_cc_txns_rfs (CC travel+tours MCC — retail.feature_space),
         feat_payroll_indicator (payroll presence — retail.feature_space primary),
         prm_digital_login_monthly (OMB login monthly grain — digital_login pipeline)

    comp_financial_tran_repos_dly is the raw 2.4B-row CASA table (R20). Pass B
    scopes it via CIF-level leftsemi join before any date filtering. Pass B has
    an inline schema guard and emits NULL features if required columns are absent.

Node graph summary:
    Node 1  build_crx_departure_spell_base     → crx_cc_departure_spell_base
    Node 2  build_crx_departure_contract_cif   → crx_cc_departure_contract_cif
    Node 3  build_crx_departure_pass_a         → crx_cc_departure_pass_a
    Node 4  build_crx_departure_pass_b         → crx_cc_departure_pass_b
    Node 5  build_crx_departure_pass_c         → crx_cc_departure_pass_c
    Node 6  build_crx_departure_pass_d         → crx_cc_departure_pass_d
    Node 7  build_crx_departure_pass_e         → crx_cc_departure_pass_e
    Node 8  build_crx_departure_pass_f         → crx_cc_departure_pass_f
    Node 9  build_crx_departure_pass_g         → crx_cc_departure_pass_g
    Node 10 build_crx_departure_pass_h         → crx_cc_departure_pass_h
    Node 11 build_crx_departure_pass_h2        → crx_cc_departure_pass_h2
    Node 12 build_crx_departure_pass_i         → crx_cc_departure_pass_i
    Node 13 build_crx_departure_pass_j         → crx_cc_departure_pass_j
    Node 14 build_crx_departure_pass_k         → crx_cc_departure_pass_k
    Node 15 build_crx_departure_final          → crx_cc_departure_signature

Run with:
    kedro run --pipeline=crx_cc_departure_signature
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_departure_contract_cif,
    build_departure_final,
    build_departure_pass_a,
    build_departure_pass_b,
    build_departure_pass_c,
    build_departure_pass_d,
    build_departure_pass_e,
    build_departure_pass_f,
    build_departure_pass_g,
    build_departure_pass_h,
    build_departure_pass_h2,
    build_departure_pass_i,
    build_departure_pass_j,
    build_departure_pass_k,
    build_departure_spell_base,
)

_TAGS = ["crx", "departure_signature", "t06"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """15-node pipeline: build CC departure signature & history shape features."""
    return Pipeline(
        [
            # ── Node 1: spell base ─────────────────────────────────────────────
            node(
                func=build_departure_spell_base,
                inputs=[
                    "crx_cc_spell_table",
                    "crx_cc_payment_trajectory",
                    "cc_spine",  # adds spine_obs_date + block_date
                ],
                outputs="crx_cc_departure_spell_base",
                name="build_crx_departure_spell_base",
                tags=_TAGS,
            ),
            # ── Node 2: contract → CIF bridge ─────────────────────────────────
            node(
                func=build_departure_contract_cif,
                inputs=[
                    "prm_contract",
                    "prm_client",
                ],
                outputs="crx_cc_departure_contract_cif",
                name="build_crx_departure_contract_cif",
                tags=_TAGS,
            ),
            # ── Node 3: Pass A — CC departure + fee signals ─────────────────
            node(
                func=build_departure_pass_a,
                inputs=[
                    "crx_cc_transactions",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_a",
                name="build_crx_departure_pass_a",
                tags=_TAGS,
            ),
            # ── Node 4: Pass B — CASA inflow stop (2.4B row, R20) ───────────
            node(
                func=build_departure_pass_b,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_b",
                name="build_crx_departure_pass_b",
                tags=_TAGS,
            ),
            # ── Node 5: Pass C — history shape self-window ──────────────────
            node(
                func=build_departure_pass_c,
                inputs=[
                    "crx_cc_spell_table",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_c",
                name="build_crx_departure_pass_c",
                tags=_TAGS,
            ),
            # ── Node 6: Pass D — tenure + lifetime fees ─────────────────────
            node(
                func=build_departure_pass_d,
                inputs=[
                    "prm_contract",
                    "prm_turnovers",
                    "crx_cc_departure_spell_base",
                    "crx_cc_departure_pass_a",
                ],
                outputs="crx_cc_departure_pass_d",
                name="build_crx_departure_pass_d",
                tags=_TAGS,
            ),
            # ── Node 7: Pass E — AECB leverage slope (T21 DROP) ─────────────
            node(
                func=build_departure_pass_e,
                inputs=[
                    "int_bureau_pull_monthly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_e",
                name="build_crx_departure_pass_e",
                tags=_TAGS,
            ),
            # ── Node 8: Pass F — relationship breadth ───────────────────────
            node(
                func=build_departure_pass_f,
                inputs=[
                    "feat_product_holding",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_f",
                name="build_crx_departure_pass_f",
                tags=_TAGS,
            ),
            # ── Node 9: Pass G — AECB alert signals ─────────────────────────
            node(
                func=build_departure_pass_g,
                inputs=[
                    "fea_monthly_aecb_alerts",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_g",
                name="build_crx_departure_pass_g",
                tags=_TAGS,
            ),
            # ── Node 10: Pass H — cross-border CASA outflow ─────────────────
            node(
                func=build_departure_pass_h,
                inputs=[
                    "feat_fx_leakage",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_h",
                name="build_crx_departure_pass_h",
                tags=_TAGS,
            ),
            # ── Node 11: Pass H2 — retail.feature_space CC travel MCC ───────
            node(
                func=build_departure_pass_h2,
                inputs=[
                    "feat_cc_txns_rfs",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_h2",
                name="build_crx_departure_pass_h2",
                tags=_TAGS,
            ),
            # ── Node 12: Pass I — payroll indicator ─────────────────────────
            node(
                func=build_departure_pass_i,
                inputs=[
                    "feat_payroll_indicator",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_i",
                name="build_crx_departure_pass_i",
                tags=_TAGS,
            ),
            # ── Node 13: Pass J — foreign login detection ───────────────────
            node(
                func=build_departure_pass_j,
                inputs=[
                    "prm_digital_login_monthly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_j",
                name="build_crx_departure_pass_j",
                tags=_TAGS,
            ),
            # ── Node 14: Pass K — bust-out utilisation signals ──────────────
            node(
                func=build_departure_pass_k,
                inputs=[
                    "crx_cc_transactions",
                    "prm_contract",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_k",
                name="build_crx_departure_pass_k",
                tags=_TAGS,
            ),
            # ── Node 15: final assembly ─────────────────────────────────────
            node(
                func=build_departure_final,
                inputs=[
                    "crx_cc_departure_spell_base",
                    "crx_cc_departure_pass_a",
                    "crx_cc_departure_pass_b",
                    "crx_cc_departure_pass_c",
                    "crx_cc_departure_pass_d",
                    "crx_cc_departure_pass_e",
                    "crx_cc_departure_pass_f",
                    "crx_cc_departure_pass_g",
                    "crx_cc_departure_pass_h",
                    "crx_cc_departure_pass_h2",
                    "crx_cc_departure_pass_i",
                    "crx_cc_departure_pass_j",
                    "crx_cc_departure_pass_k",
                ],
                outputs="crx_cc_departure_signature",
                name="build_crx_departure_final",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
