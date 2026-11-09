"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
FOLLOWUP_RUN_DAYS = 7  # follow-up promises less than 8 days apart are one event
MATCH_DAYS = 7  # a follow-up promise within 7 days of a DCORE plan is that plan
# The deadline a promise is judged by (GRR): CC the next statement after the promise
# day, however close; RL the end of the next month (RL cash is known by month only).
# The alternative is 30 days from the promise ("30_days"; RL "30_days_month_end").
DEADLINES = ("next_statement", "next_month_end", "30_days", "30_days_month_end")
PROMISE_DEADLINE = {"cc": "next_statement", "rl": "next_month_end"}
STATEMENT_FALLBACK_D = 31  # no statement after the promise day yet: 31 days

# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20; Q-28, Q-29, Q-30) ─────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of positive minimum due averaged (D-A3-12)

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, ("thin",)),
        Dimension(
            "dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ("none",)
        ),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
