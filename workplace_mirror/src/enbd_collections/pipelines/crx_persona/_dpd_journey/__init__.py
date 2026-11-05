"""DPD-journey deterioration states: one engine for credit cards (CC) and loans (RL).

Spark scopes the history and gathers each account's monthly buckets into an array in
ONE shuffle; the journey logic then runs per account as a plain-Python port of the
numpy reference (docs/deterioration_states/dpd_states: features.py, states.py option
B). Sequential rules (glitch fix, +2 jump repair, runs of months) are loops, exactly
as in the reference. Parity with the reference is tested by
docs/deterioration_states/spark/tests/test_parity.py, outside src/ because it needs
pandas and numpy.

Rules: docs/deterioration_states/METHODOLOGY.md. Where the code differs from it:
specs/A4_deterioration_conformance.md (D1-D6).

Run: the product wrappers call ``build_dpd_sequences`` and then ``build_deterioration``
on ``crx_<p>_full_history`` and the spine:
    kedro run --pipeline=crx_cc_a4_deterioration   (cc_60_180 / cc_180_plus)
    kedro run --pipeline=crx_rl_a4_deterioration   (rl_60_180 / rl_180_plus)
Output: one row per spine observation in the segment, with ``det_state`` and the
journey features.

Bucket numbering
----------------
Every rule is written once, on the CC scale ("canonical"):
    CC  0 = no due, 1 = current, 2 = 1-30 DPD, 3 = 31-60, 4 = 61-90 ... 7 = 151-180,
        8 = 181-210, 9 = 210+ (cap)
    RL  0 = 0 DPD,  1 = 1-30 DPD, 2 = 31-60 ... 6 = 151-180, 7 = 180+ (cap)
canonical = max(native + offset, 1): CC offset 0, RL offset 1 (0 and 1 are both "clean").
So the 60-180 DPD spine is canonical 4-7 for both (CC native 4-7, RL native 3-6), and the
180+ segment is canonical 8+ (CC native 8-9, RL native 7). Outputs carry NATIVE buckets.

One state tree and one vocabulary for both segments (7 states): unknown,
early_payment_default, stabilized, repeat_delinquent, straight_roller_seasoned,
straight_roller_early_life, slow_roller. Stabilized only up to 151-180 DPD (never at
180+); holds at the ceiling bucket are not payments. The segment only decides which
accounts are classified.

Two stages
----------
build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per spine observation in the segment:
                       state + features

Nothing is dropped silently: every account in the history gets a sequences row with a
`build_status`; the classifier keeps only status 'ok' and the segment's current buckets.

Modules:
    constants.py  BucketScheme, CC, RL (MODEL_ID_SEGMENT lives in _common)
    params.py     PARAM_DEFAULTS, JourneyParams, journey_params()
    _dates.py     _month_idx, _month_label, _month_col
    core.py       the numpy-reference-mirroring per-account engine (journey_features etc.)
    states.py     the state tree (assign_state) + classify()
    history.py    Stage 1: build_history (not reference-constrained, free to decompose)
    spark.py      Stage 1/2 Spark orchestration (build_dpd_sequences, build_deterioration)
    logging.py    the state-distribution log and the opt-in sequence stats
    anchor.py     episode_start: the current episode's start per observation (D-A3-2)
"""

from __future__ import annotations

# Re-exports (see ``__all__``): callers and tests import from the package alone.
from .._common import MODEL_ID_SEGMENT
from ._dates import _month_idx, _month_label
from .anchor import episode_start
from .constants import CC, RL, BucketScheme
from .core import (
    NO_PRIOR,
    H,
    N,
    P,
    R,
    _glitches,
    _mean,
    _repair,
    _runs,
    encode,
    journey_features,
)
from .history import _legacy_drop, build_history
from .logging import LOG, _log_sequence_stats, log_state_stats
from .params import PARAM_DEFAULTS, JourneyParams, journey_params
from .spark import (
    _CLASSIFY_SCHEMA,
    _FEATURES,
    _HISTORY_SCHEMA,
    _idx_to_month_end,
    _month_col,
    _ship_by_value,
    build_deterioration,
    build_dpd_sequences,
)
from .states import DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify

__all__ = [
    "BucketScheme",
    "CC",
    "DISPLAY_NAMES",
    "H",
    "JourneyParams",
    "LOG",
    "MODEL_ID_SEGMENT",
    "N",
    "NO_PRIOR",
    "P",
    "PARAM_DEFAULTS",
    "R",
    "RL",
    "STATES",
    "STATE_RULES",
    "_CLASSIFY_SCHEMA",
    "_FEATURES",
    "_HISTORY_SCHEMA",
    "_glitches",
    "_idx_to_month_end",
    "_legacy_drop",
    "_log_sequence_stats",
    "log_state_stats",
    "_mean",
    "_month_col",
    "_month_idx",
    "_month_label",
    "_repair",
    "_runs",
    "_ship_by_value",
    "assign_state",
    "build_deterioration",
    "build_dpd_sequences",
    "build_history",
    "classify",
    "encode",
    "episode_start",
    "journey_features",
    "journey_params",
]
