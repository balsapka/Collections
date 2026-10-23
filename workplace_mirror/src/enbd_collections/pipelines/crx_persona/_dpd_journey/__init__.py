"""DPD-journey deterioration states — one engine for credit cards (CC) and retail loans (RL).

Replaces the window-function port (resolve_gaps / encode_transitions / classify_from_grid).
Spark does what Spark is good at — scoping, the history floor, and ONE shuffle that gathers
each account's monthly buckets into an array. The journey logic then runs per account as a
plain-Python port of the signed-off numpy reference (docs/deterioration_states/dpd_states:
features.py, states.py option B). Sequential rules (glitch fix, +2 jump repair, runs
of months) are loops, exactly as in the reference — no lag/lead approximation, no cascade
divergence. Parity with the reference is proven by
docs/deterioration_states/spark/tests/test_parity.py (recoverable from BUNDLE.md) — not a
file under src/tests/, since it needs pandas/numpy and is deliberately not a src/ runtime dep.

Bucket numbering
----------------
Every rule is written once, on the CC scale ("canonical"):
    CC  0 = no due, 1 = current, 2 = 1-30 DPD, 3 = 31-60, 4 = 61-90 ... 7 = 151-180,
        8 = 181-210, 9 = 210+ (cap)
    RL  0 = 0 DPD,  1 = 1-30 DPD, 2 = 31-60 ... 6 = 151-180, 7 = 180+ (cap)
canonical = max(native + offset, 1): CC offset 0, RL offset 1 (0 and 1 are both "clean").
So the 60-180 DPD spine is canonical 4-7 for both (CC native 4-7, RL native 3-6), and the
180+ segment is canonical 8+ (CC native 8-9, RL native 7). Outputs carry NATIVE buckets.

One state tree and one vocabulary for both segments (7 states): unknown, early_payment_default,
stabilized, repeat_delinquent, straight_roller_seasoned, straight_roller_early_life,
slow_roller. Stabilized only up to 151-180 DPD (never at 180+); holds at the ceiling bucket
are not payments. The segment only decides which accounts are classified.

Two stages (two Kedro nodes per product)
----------------------------------------
build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features

Nothing is dropped silently: every account in the history gets a sequences row with a
`build_status`; the classifier keeps only status 'ok' and the segment's current buckets.

Package layout (readability split of the former flat _dpd_journey.py; no behavior change):
    constants.py  BucketScheme, CC, RL, SEGMENTS, MODEL_ID_SEGMENT
    params.py     PARAM_DEFAULTS, JourneyParams, journey_params()
    _dates.py     _month_idx, _month_label, _month_col — shared by spark.py and logging.py
                  so those two never need to import each other
    core.py       the numpy-reference-mirroring per-account engine (journey_features etc.)
    states.py     the state tree (assign_state) + classify()
    history.py    Stage 1: build_history (not reference-constrained, free to decompose)
    spark.py      Stage 1/2 Spark orchestration (build_dpd_sequences, build_deterioration)
    logging.py    the two stats logs
This module re-exports everything reachable on the old flat module — no caller/test import
needs to change.
"""

from __future__ import annotations

# This module's whole job is re-exporting the package's submodules under the old flat
# module's name, so every caller/test import keeps working unchanged.
# pylint: disable=unused-import
from ._dates import _month_idx, _month_label
from .constants import CC, MODEL_ID_SEGMENT, RL, SEGMENTS, BucketScheme
from .core import (
    H,
    N,
    NO_PRIOR,
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
from .logging import LOG, _log_sequence_stats, _log_state_stats
from .params import PARAM_DEFAULTS, JourneyParams, journey_params
from .spark import (
    _CLASSIFY_SCHEMA,
    _FEATURES,
    _HISTORY_SCHEMA,
    _idx_to_month_end,
    _month_col,
    _ship_by_value,
    _string_key,
    build_deterioration,
    build_dpd_sequences,
)
from .states import DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify
