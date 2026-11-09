"""The A3 payment credibility pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base, crx_<p>_a4_deterioration ─► episode ─┬───────────────────┐
    product dues + payments (wrapper nodes) ─► cycle ledger ┼─ Dim B, Dim C ────┤
    DCORE plans ─► instalments ┬─ promise events ───────────┼─ Dim A ───────────┼─► state
    dcore_prm_followup_outcomes┴────────────────────────────┴─ contacts ────────┘

Needs, for the model_id: the obs base, A4, the product's payment sources and the DCORE
tables. Promises are judged by ``PROMISE_DEADLINE`` (CC the next statement, RL the end of
the next month).
"""

from functools import partial

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a3_credibility
from .constants import PROMISE_DEADLINE
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import (
    build_a3_episode,
    build_cycle_ledger,
    build_instalments,
    build_promise_events,
)

TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
# Ledger names as in the workplace catalog.
LEDGER = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}


def create_a3_pipeline(
    product: str, output: str, dues: Node, payments: Node, deadline: str | None = None
) -> Pipeline:
    """The A3 axis for ``product``, written to ``output``. ``dues`` / ``payments`` are
    the product nodes writing ``crx_<p>_a3_dues`` / ``crx_<p>_a3_payments``.
    ``deadline`` overrides ``PROMISE_DEADLINE`` (the bundle check)."""
    p = f"crx_{product}_a3"
    deadline = deadline or PROMISE_DEADLINE[product]
    episode, ledger, inst = f"{p}_episode", LEDGER[product], f"{p}_instalments"
    events = f"{p}_promise_events"

    def step(func, inputs: dict, out: str, name: str) -> Node:
        return node(
            func=func, inputs=inputs, outputs=out, name=f"build_{name}", tags=TAGS
        )

    return Pipeline(
        [
            step(
                build_a3_episode,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "deterioration": f"crx_{product}_a4_deterioration",
                },
                episode,
                episode,
            ),
            dues,
            payments,
            step(
                build_cycle_ledger,
                {"dues": f"{p}_dues", "payments": f"{p}_payments"},
                ledger,
                ledger,
            ),
            step(
                build_instalments,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "agreements": "prm_dcore_account_agreements",
                    "int_ptp": "dcore_int_ptp",
                    "ptp_instalments": "dcore_prm_promise_instalments",
                    "int_settlement": "dcore_int_settlement",
                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
                },
                inst,
                inst,
            ),
            step(
                partial(build_promise_events, deadline=deadline),
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "dues": f"{p}_dues",
                    "payments": f"{p}_payments",
                },
                events,
                events,
            ),
            step(
                build_commitment_signals,
                {"episode": episode, "events": events},
                f"{p}_commitment_signals",
                f"{p}_commitment_signals",
            ),
            step(
                build_dlq_payment_signals,
                {"episode": episode, "ledger": ledger, "model_id": "params:model_id"},
                f"{p}_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_dlq_payment_signals",
            ),
            step(
                build_pre_dlq_payment_signals,
                {"episode": episode, "ledger": ledger},
                f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_pre_dlq_payment_signals",
            ),
            step(
                build_contact_signals,
                {
                    "episode": episode,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "payments": f"{p}_payments",
                    "dues": f"{p}_dues",
                    "model_id": "params:model_id",
                },
                f"{p}_strong_negative_signals",
                f"{p}_contact_signals",
            ),
            step(
                partial(build_a3_credibility, deadline=deadline),
                {
                    "episode": episode,
                    "commitments": f"{p}_commitment_signals",
                    "dlq_payments": f"{p}_dlq_payment_signals_single_payment_cycle_count",
                    "pre_dlq": f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                    "contacts": f"{p}_strong_negative_signals",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                output,
                f"{p}_payment_credibility",
            ),
        ]
    )
