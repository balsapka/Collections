"""DPD-journey deterioration states: one engine for credit cards (CC) and loans (RL).

Spark gathers each account's monthly buckets into an array in ONE shuffle; the journey
logic then runs per account as a plain-Python port of the numpy reference
(docs/deterioration_states/dpd_states: features.py, states.py option B), with parity
tested by docs/deterioration_states/spark/tests/test_parity.py (outside src/: it needs
pandas and numpy). Rules: docs/deterioration_states/METHODOLOGY.md; where the code
differs: specs/A4_deterioration_conformance.md (D1-D6).

Run: the product wrappers call ``build_dpd_sequences`` (long history -> one row per
account: gap-filled monthly bucket array + audit, a ``build_status`` for every account)
and ``build_deterioration`` (sequences + spine -> one row per spine observation in the
segment, ``det_state`` and the journey features):
    kedro run --pipeline=crx_cc_a4_deterioration   (cc_60_180 / cc_180_plus)
    kedro run --pipeline=crx_rl_a4_deterioration   (rl_60_180 / rl_180_plus)

Every rule is written once on the CC scale ("canonical" = max(native + offset, 1); CC
offset 0, RL offset 1, so 0 and 1 are both "clean"): the 60-180 DPD spine is canonical
4-7 for both products, 180+ is canonical 8+. Outputs carry NATIVE buckets.

Modules:
    constants.py  BucketScheme, CC, RL (MODEL_ID_SEGMENT lives in _common)
    params.py     PARAM_DEFAULTS, JourneyParams, journey_params()
    _dates.py     _month_idx, _month_col
    core.py       the numpy-reference-mirroring per-account engine (journey_features etc.)
    states.py     the state tree (assign_state) + classify()
    history.py    Stage 1: build_history (not reference-constrained, free to decompose)
    spark.py      Stage 1/2 Spark orchestration (build_dpd_sequences, build_deterioration)
    logging.py    the state-distribution log and the opt-in sequence stats
    anchor.py     episode_start: the current episode's start per observation (D-A3-2)
"""

# ruff: noqa: F401

from __future__ import annotations

# Public: what the wrappers and the checks import.
from .._common import MODEL_ID_SEGMENT
from .anchor import episode_start
from .constants import CC, RL, BucketScheme
from .core import NO_PRIOR, encode, journey_features
from .logging import LOG, log_state_stats
from .params import PARAM_DEFAULTS, JourneyParams, journey_params
from .spark import build_deterioration, build_dpd_sequences
from .states import DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify

# isort: split

# Re-exported for the parity tests: H, N, P, R are the numpy reference's names.
from ._dates import _month_idx
from .core import H, N, P, R, _glitches, _mean, _repair, _runs
from .history import _legacy_drop, build_history
from .logging import _log_sequence_stats
from .spark import (
    _CLASSIFY_SCHEMA,
    _FEATURES,
    _HISTORY_SCHEMA,
    _idx_to_month_end,
    _month_col,
    _ship_by_value,
)
