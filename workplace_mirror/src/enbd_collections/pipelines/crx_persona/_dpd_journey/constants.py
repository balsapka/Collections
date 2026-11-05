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
