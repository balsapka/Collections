"""The UC1 stated-block pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ conversation evidence ──► crx_<p>_uc1_conversation_signals
                      │  (crx_uc1_metadata, crx_uc1_extracted_signals,       │
                      │   crx_uc1_signal_level_conflicts)                    │
                      └─ stated block ◄──────────────────────────────────────┘
                         (crx_uc1_simple_signal_aggregation) ──► crx_<p>_uc1_stated

UC1's outputs are read as they are, from the shared file store (``catalog_crx.yml``).
Needs, for the model_id: the observation base.
"""

from kedro.pipeline import Pipeline, node

from .classify import build_uc1_stated
from .signals import build_uc1_conversation_signals

TAGS = ["crx_persona", "crx", "uc1", "stated"]


def create_uc1_pipeline(product: str, output: str) -> Pipeline:
    """The conversation-evidence node and the state node of ``product``'s UC1 stated
    block, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_uc1"
    end_date = "params:crx_persona.persona_end_date"
    return Pipeline(
        [
            node(
                func=build_uc1_conversation_signals,
                inputs={
                    "obs_base": obs,
                    "metadata": "crx_uc1_metadata",
                    "extracted_signals": "crx_uc1_extracted_signals",
                    "signal_level_conflicts": "crx_uc1_signal_level_conflicts",
                    "persona_end_date": end_date,
                },
                outputs=f"{prefix}_conversation_signals",
                name=f"build_{prefix}_conversation_signals",
                tags=TAGS,
            ),
            node(
                func=build_uc1_stated,
                inputs={
                    "obs_base": obs,
                    "aggregation": "crx_uc1_simple_signal_aggregation",
                    "conversations": f"{prefix}_conversation_signals",
                    "model_id": "params:model_id",
                    "persona_end_date": end_date,
                },
                outputs=output,
                name=f"build_{prefix}_stated",
                tags=TAGS,
            ),
        ],
    )
