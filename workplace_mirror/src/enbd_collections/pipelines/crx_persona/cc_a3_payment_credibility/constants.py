"""Constants for the cc_a3_payment_credibility pipeline, grouped by section.

State = points from Dimension A (commitments kept), B (payments while delinquent) and
C (record before delinquency), demoted one level by a strong negative. Every threshold
tagged [CONFIRM] is a proposal from logs/A3_credibility_shared.xlsx ("A3 framework",
block 5), not yet measured on PROD. The DCORE call codes and result-name sets live in
``crx_persona/_dcore_codes.py`` (shared with A2, which A3 does not import).
"""

# ── Evidence-method switches (params:a3_dlq_/a3_pre_dlq_payment_evidence_method) ─
# Canonical values; parameters_crx_persona.yml must match one of these exactly.
# Dimension B accepts all three; Dimension C only single_payment_cycle_count and
# dpd_bucket_movement.
_METHOD_SINGLE_PAYMENT_CYCLE_COUNT = "single_payment_cycle_count"  # default
_METHOD_PAYMENT_SUM_WATERFALL = "payment_sum_waterfall"
_METHOD_DPD_BUCKET_MOVEMENT = "dpd_bucket_movement"

# ── State: points cut-offs and confidence ─────────────────────────────────
# Total points (A+B+C), with no strong negative.
_TAU_A3V2_HIGH_FROM_POINTS = 4  # [CONFIRM] High
_TAU_A3V2_MODERATE_FROM_POINTS = 1  # [CONFIRM] at least Moderate
# Fixed confidence per state: evidence quality of the typical path, not a probability.
_CONF_HIGH = 0.90
_CONF_MODERATE = 0.75
_CONF_LOW = 0.60
_CONF_UNKNOWN = 0.00

# ── Strong negatives (each demotes the state by one level; they do not stack) ──
# Distinct contact dates needed before "no_response" fires (3 calls on one day are
# weaker evidence than 3 separate days).
_TAU_MIN_CONTACT_DATES = 3  # [CONFIRM]
# Tie-break when more than one fires on the same row.
_SB_PRIORITY = ("broken_commitments", "refusal", "no_response")  # [CONFIRM]

# ── Dimension A: commitments kept (PTP / settlement instalments) ──────────
_TAU_A3V2_COMMITMENTS_WINDOW_M = 12  # [CONFIRM] months of instalments considered
_TAU_A3V2_COMMITMENTS_MIN_CONCLUDED = 2  # [CONFIRM] concluded instalments for a pattern
_TAU_A3V2_COMMITMENTS_KEPT_RATE = 0.8  # [CONFIRM] paid share for "Kept"
# Kept-rate below this (with >= MIN_CONCLUDED), or the last N concluded all broken -> "Broken".
_TAU_A3V2_COMMITMENTS_BROKEN_RATE = 0.4  # [CONFIRM]
_TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N = 3  # [CONFIRM]

# ── Dimension B: payments while delinquent ────────────────────────────────
# Due amount per cycle = first non-zero of overdue_bucket_07..01, then minimum_due (see
# _signals_common.resolve_due_amount_m). [CONFIRM – the highest-impact assumption]

# Windows after onset, in months, chosen by the row's DLQ bucket (>= 8 is 180+).
_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180 = 3  # [CONFIRM] "Regular" and any-payment window
_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS = 6  # [CONFIRM] "Regular" window
# Any-payment window (Some vs None, and the refusal / no_response strong negatives);
# 61-180 uses 3 for both tests.
_TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS = 12  # [CONFIRM]

# "Regular" = qualifying months in the window.
_TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180 = 2  # [CONFIRM] 2 of 3
_TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS = 3  # [CONFIRM] 3 of 6

# When only overdue_bucket_08 is left, the cycle has no due amount; the default method uses
# the account's frozen baseline instead: the average minimum_due of its last N months with
# a positive minimum_due before it stagnated (_signals_common.resolve_bucket08_fallback_due).
_TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS = 12  # [CONFIRM]

# What qualifies a month: payment >= max(share x due_amount_m, minimum payment).
_TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE = 1.0  # [CONFIRM] full due amount
# AED floor at 180+ for a qualifying month and for the any-payment flag. 61-180 has none;
# bucket-movement credits carry no amount, so only amount-based parts use it.
_TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS = 100.0  # [CONFIRM]

# Billing-cycle sanity (build_a3_payment_cycles). A cycle runs to the next statement that
# exists, so missing statements (2021-2023 gap, 2024-11-12 run) make one long cycle.
# Keep cycles starting up to this many days before the floor; drop cycles longer than the max
# (a normal cycle is 26-35 days).
_PAYMENT_CYCLE_FLOOR_LOOKBACK_D = 35  # [CONFIRM]
_PAYMENT_CYCLE_MAX_LENGTH_D = 62  # [CONFIRM]

# dpd_bucket_movement: the highest DLQ bucket (max overdue bucket + 1; only 8 exist). A flat
# bucket at the cap is ambiguous, so it defers to the waterfall count for that cycle.
_DLQ_LEVEL_SATURATED = 9

# payment_sum_waterfall: overdue_bucket_08 is the multi-month accumulator, so it is split
# into synthetic "one month" slices sized off the account's trailing minimum_due average.
_TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M = 24  # [CONFIRM] prior rows averaged
# Maximum slices (one payment cannot credit more months than the longest window).
_TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP = _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS

# ── Dimension C: record before delinquency ────────────────────────────────
_TAU_A3V2_PRE_DLQ_WINDOW_M = 12  # [CONFIRM] months before onset (T0)
_TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE = 3  # [CONFIRM] fewer billed months = "No record"
_TAU_A3V2_PRE_DLQ_CLEAN_SHARE = 0.8  # [CONFIRM] share of billed months paid for "Clean"
# Per-cycle amount for "paid as billed": payment >= this x due_amount_m (single_payment_
# cycle_count only; dpd_bucket_movement has no amount check). Strict 100% since 2026-10-30;
# it was 0.85 (2026-10-22). Set below 1.0 to relax again.
_TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE = 1.0  # [CONFIRM]
