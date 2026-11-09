"""The persona master for one product: the four axis outputs and the exposure on the
observation base, with the persona layer on top.

    crx_<p>_obs_base ─┬─ exposure ───────────────┐  crx_cc_balance | crx_rl_full_history
                      ├─ crx_<p>_a1_ability ─────┤
                      ├─ crx_<p>_a2_locatability ┼─► crx_<p>_persona_master
                      ├─ crx_<p>_a3_payment_credibility
                      └─ crx_<p>_a4_deterioration┘

kedro run --pipeline=crx_cc_persona_master   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_persona_master   (rl_60_180 / rl_180_plus)

Needs the four axis outputs of the model_id; it runs no axis itself.
"""

from kedro.pipeline import Pipeline, node

from .build import build_cc_exposure, build_persona_master, build_rl_exposure

TAGS = ["crx_persona", "crx", "persona_master"]
_EXPOSURE = {
    "cc": (build_cc_exposure, {"balance": "crx_cc_balance"}),
    "rl": (build_rl_exposure, {"full_history": "crx_rl_full_history"}),
}


def _create(product: str) -> Pipeline:
    prefix = f"crx_{product}"
    func, sources = _EXPOSURE[product]
    return Pipeline(
        [
            node(
                func=func,
                inputs={"obs_base": f"{prefix}_obs_base", **sources},
                outputs=f"{prefix}_persona_exposure",
                name=f"build_{prefix}_persona_exposure",
                tags=TAGS,
            ),
            node(
                func=build_persona_master,
                inputs={
                    "obs_base": f"{prefix}_obs_base",
                    "exposure": f"{prefix}_persona_exposure",
                    "a1": f"{prefix}_a1_ability",
                    "a2": f"{prefix}_a2_locatability",
                    "a3": f"{prefix}_a3_payment_credibility",
                    "a4": f"{prefix}_a4_deterioration",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=f"{prefix}_persona_master",
                name=f"build_{prefix}_persona_master",
                tags=TAGS,
            ),
        ]
    )


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_cc_persona_master."""
    return _create("cc")


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_rl_persona_master."""
    return _create("rl")
