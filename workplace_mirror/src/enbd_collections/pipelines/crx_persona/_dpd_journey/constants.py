"""Bucket-numbering constants shared by both segments and both products (CC/RL)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BucketScheme:
    """Per-domain native-bucket constants (CC vs RL)."""

    name: str
    offset: int  # canonical = max(native + offset, 1)
    top: int  # highest native bucket (the cap)
    repair_jumps: bool = True  # CC only: undo +2 billing-cycle jumps (_repair
    # in core.py). RL has no such billing artifact (int_loan_master is one
    # row/account/month) — a +2 jump there is always a genuine DPD move.

    @property
    def canon_top(self) -> int:
        """Highest canonical bucket (the cap), native top + offset."""
        return self.top + self.offset


CC = BucketScheme("cc", offset=0, top=9, repair_jumps=True)
RL = BucketScheme("rl", offset=1, top=7, repair_jumps=False)

# Segments on the canonical scale.
SEGMENTS = {
    "60_180": (4, 5, 6, 7),  # CC native 4-7, RL native 3-6
    "180_plus": (8, 9),  # CC native 8-9, RL native 7
}

# segment is fully determined by model_id — never an independently-settable override.
MODEL_ID_SEGMENT = {
    "cc_60_180": "60_180",
    "cc_180_plus": "180_plus",
    "rl_60_180": "60_180",
    "rl_180_plus": "180_plus",
}
