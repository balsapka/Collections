"""Kedro pipeline: A2 Locatability axis (location x reachability).

# pylint: disable=line-too-long

Four-node pipeline that derives the full A2 locatability axis and emits the
shipped persona column ``a2_state`` at (account_id, observation_date) grain.
Node 4 is T29's location x reachability redesign, promoted 2026-10-22 to
replace T12's original 7-state waterfall (see ``RESULTS.md``).

Architecture:
    build_a2_base                → crx_cc_a2_base
    build_a2_login_presence      → crx_cc_a2_login_presence
    build_a2_contact_signals     → crx_cc_a2_contact_signals
    build_a2_locatability        → crx_cc_a2_locatability   ← shipped axis

Inputs:
    cc_spine                        Model-id-scoped spine (anchor grain)
    crx_cc_spell_table              T03b — t0 + spell_end per spell
    crx_cc_departure_signature      T06 — departure trail columns (R14 reuse)
    prm_digital_login_monthly       Obs-anchored digital presence + H2 departure login
    dcore_observation_spine         account→agreement mapping (contract_id, observation_date, agreement_id, cif_id)
    dcore_prm_followup_outcomes     DCORE contact attempt log (carries result_name directly)
    params:model_id                 Selects the segment-aware recency/staleness thresholds
    prm_contract                    Way4 block_code_1/block_code_2 deceased corroboration (T34)
    prm_client                      CIF bridge pair for prm_contract (T34)
    feat_demographics_cif           ft_deceased_flag deceased corroboration (T34)

Output:
    crx_cc_a2_locatability — A2 axis for every (account_id, observation_date)
    pair in cc_spine; a2_state ∈ {Deceased, Skip - Reachable,
    Skip - Non-Reachable, Skip - Unknown, In Country - Reachable,
    In Country - Non-Reachable, In Country - Unknown, Unknown - Reachable,
    Unknown - Non-Reachable, Unknown - Unknown}.

Run with:
    kedro run --pipeline=crx_cc_a2_locatability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a2_base,
    build_a2_contact_signals,
    build_a2_locatability,
    build_a2_login_presence,
)

_TAGS = ["crx", "a2", "locatability", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node A2 Locatability pipeline."""
    return Pipeline(
        [
            node(
                func=build_a2_base,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "crx_cc_departure_signature",
                ],
                outputs="crx_cc_a2_base",
                name="build_crx_a2_base",
                tags=_TAGS,
            ),
            node(
                func=build_a2_login_presence,
                inputs=[
                    "crx_cc_a2_base",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_cc_a2_login_presence",
                name="build_crx_a2_login_presence",
                tags=_TAGS,
            ),
            node(
                func=build_a2_contact_signals,
                inputs=[
                    "crx_cc_a2_base",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                ],
                outputs="crx_cc_a2_contact_signals",
                name="build_crx_a2_contact_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "base": "crx_cc_a2_base",
                    "login_presence": "crx_cc_a2_login_presence",
                    "contact_signals": "crx_cc_a2_contact_signals",
                    "model_id": "params:model_id",
                    "prm_contract": "prm_contract",
                    "prm_client": "prm_client",
                    "feat_demographics_cif": "feat_demographics_cif",
                },
                outputs="crx_cc_a2_locatability",
                name="build_crx_a2_locatability",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
