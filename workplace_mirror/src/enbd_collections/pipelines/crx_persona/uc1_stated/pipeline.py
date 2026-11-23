"""The UC1 stated-block pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ conversations, DCORE promises ──► crx_<p>_uc1_conversation_signals
                      │  (crx_uc1_metadata, crx_<p>_a3_promise_events)          │
                      └─ stated block ◄─────────────────────────────────────────┘
                         (crx_uc1_customer_signal_export, crx_<p>_a1_ability) ──► crx_<p>_uc1_stated

UC1's outputs are read as they are, from the shared file store (``catalog_crx.yml``).
Scored month: ``uc1_month_end``, else ``crx_persona.persona_end_date``.
Needs, for the model_id: the observation base, A1 ability and A3 promise events.
"""

from kedro.pipeline import Pipeline, node

from .classify import build_uc1_stated
from .signals import build_uc1_conversation_signals

TAGS = ["crx_persona", "crx", "uc1", "stated"]


def create_uc1_pipeline(product: str, output: str) -> Pipeline:
    """The conversation node and the state node of ``product``'s UC1 stated block,
    written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_uc1"
    dates = {
        "persona_end_date": "params:crx_persona.persona_end_date",
        "uc1_month_end": "params:uc1_month_end",
    }
    return Pipeline(
        [
            node(
                func=build_uc1_conversation_signals,
                inputs={
                    "obs_base": obs,
                    "metadata": "crx_uc1_metadata",
                    "promise_events": f"crx_{product}_a3_promise_events",
                    **dates,
                },
                outputs=f"{prefix}_conversation_signals",
                name=f"build_{prefix}_conversation_signals",
                tags=TAGS,
            ),
            node(
                func=build_uc1_stated,
                inputs={
                    "obs_base": obs,
                    "export": "crx_uc1_customer_signal_export",
                    "conversations": f"{prefix}_conversation_signals",
                    "a1_ability": f"crx_{product}_a1_ability",
                    "model_id": "params:model_id",
                    **dates,
                },
                outputs=output,
                name=f"build_{prefix}_stated",
                tags=TAGS,
            ),
        ],
    )
