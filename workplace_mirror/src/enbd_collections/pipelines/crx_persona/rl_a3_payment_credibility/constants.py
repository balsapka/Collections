"""Constants for RL A3 Payment Credibility's Dimension B and C, grouped by section.

RL has the same three approaches as CC, built on RL-native primitives (see nodes.py):
  - single_payment_cycle_count (default): each month judged on its own, cash vs EMI.
  - payment_sum_waterfall (Dimension B): floor(window cash / EMI); RL has no bucket
    ladder to walk, so it is a division.
  - dpd_bucket_movement: payment inferred from month-over-month bucket movement.

These are RL-local copies of cc_a3_payment_credibility/constants.py, deliberately not
imported (a CC retune must not move RL). RL has its own switches,
rl_a3_dlq_payment_evidence_method / rl_a3_pre_dlq_payment_evidence_method; the
constants below are their defaults. Values tagged [CONFIRM] are inherited from CC
pending RL business validation.
"""

from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
)

# ── Evidence-method defaults (same as CC; the params override them) ──────────
_DLQ_PAYMENT_EVIDENCE_METHOD_RL = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT
_PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT

# ── Bucket-scale translations (CC scale 0-9, delinquency from 2; RL 0-7, from 1) –
# Cross-checked against _dpd_journey/constants.py (RL: offset 1, top 7).
_DLQ_LEVEL_SATURATED_RL = 7  # RL's highest bucket (CC: 9)
_DLQ_WINDOW_SPLIT_THRESHOLD_RL = 7  # the 180+ band is the single bucket 7 (CC: >= 8)
_PRE_DLQ_NOT_DELINQUENT_MAX_RL = 0  # "not in any overdue bucket" (CC: <= 1)

# ── Dimension B: payments while delinquent ───────────────────────────────
# Windows after onset, in months, by band: MID = RL 60-180 (dlq 3-6), DEEP = 180+ (dlq 7).
_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID = 3  # [CONFIRM] "Regular" and any-payment window
_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP = 6  # [CONFIRM] "Regular" window
# Any-payment window: Some vs None and the refusal / no_response strong negatives.
# MID uses 3 for both tests.
_TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP = 12  # [CONFIRM]

# "Regular" = qualifying months in the window.
_TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID = 2  # [CONFIRM] 2 of 3
_TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP = 3  # [CONFIRM] 3 of 6

# What qualifies a month: cash >= max(share x EMI, minimum cash).
_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE = 1.0  # [CONFIRM] full EMI
# AED floor in the DEEP band for a qualifying month and for the any-payment flag (and
# the EMI-month sum); none in the MID band.
_TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP = 100.0  # [CONFIRM]

# dpd_bucket_movement credits the RAW bucket delta on an improvement (no CC-style "+1
# unless cured"); [CONFIRM] – no partially-cured RL account has been hand-traced yet.

# ── Dimension C: record before delinquency ───────────────────────────────
_TAU_RL_A3V2_PRE_DLQ_WINDOW_M = 12  # [CONFIRM] months before onset (T0)
_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE = 3  # [CONFIRM] fewer billed months = "no_record"
# Share of billed months paid as billed for "clean".
_TAU_RL_A3V2_PRE_DLQ_CLEAN_SHARE = 0.8  # [CONFIRM]
# Cash needed for "paid as billed": >= this x EMI. Strict 100% since 2026-10-30 (was
# 0.85, inherited from CC); set below 1.0 to relax again.
_TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE = 1.0  # [CONFIRM]
