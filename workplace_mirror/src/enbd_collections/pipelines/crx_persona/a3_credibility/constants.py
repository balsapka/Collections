"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS, segment
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
# The deadline a promise is judged by, whatever date was promised (D-A3-28): at 60-180 a
# card promise by the next statement after the promise day, however close; a loan
# promise, and every promise at 180+, by the end of the promise month. The options and
# their cutoffs: promises.CUTOFFS.
PROMISE_DEADLINE = {
    SEG_60_180: {"cc": "next_statement", "rl": "month_end"},
    SEG_180_PLUS: {"cc": "month_end", "rl": "month_end"},
}
# next-statement deadline: at most 31 days after the promise (no statement on record by
# then: statements are missing from the history) (D-A3-29)
NEXT_STATEMENT_MAX_DAYS = 31
PROMISE_DAYS = 30  # the "30_days" options: 30 days after the promise


def promise_deadline(product: str, model_id: str, override: str | None = None) -> str:
    """``override`` if given, else the ``PROMISE_DEADLINE`` of ``product`` in
    ``model_id``'s segment."""
    return override or PROMISE_DEADLINE[segment(model_id)][product]


# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
# Dimension A: the smallest promised amount and a partial payment (D-A3-29); the same
# 100 AED today, kept apart so the two can move separately.
PROMISE_MIN_AED = MIN_PAYMENT_AED
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20, -32; Q-29, Q-30) ──────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── Source history ────────────────────────────────────────────────────────────
# Months of payment history read before the earliest window a dimension opens (the
# episode start, or the first observation month): the longest window and one cycle.
HISTORY_MONTHS = (
    max(PRE_DLQ_MONTHS, COMMITMENT_MONTHS, *ANY_PAYMENT_MONTHS.values()) + 1
)

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────
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
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
