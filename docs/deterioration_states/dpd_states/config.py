"""Workplace configuration — the ONLY file that needs editing to run on real data.

Every <<FILL-IN>> must be replaced with a name discovered in the workplace repo / Kedro
catalog. Never guess a dataset or column name: if it cannot be found, ask the user.
`model_id` is NOT configured here — the Spark snippet resolves it from the caller or globals.

Two ways to run:
  * FILE mode (methodology sign-off, no Spark):  python docs/deterioration_states/run.py validate
    reads INPUT_FILE / COL_DPD below.
  * SPARK mode (PROD, later):  snippets/dpd_states_validate.py  main(catalog)
    reads DS_STRINGS_TMPL / KEY / COL_DPD.
"""

# --- file mode -------------------------------------------------------------------------
# Path relative to the repo root (or absolute). One row per account, today's snapshot.
INPUT_FILE = "data/input/dpd_synthetic_data.xlsx"   # CC 60–180 DPD segment, Aug 2026

# --- the DPD string (both modes) --------------------------------------------------------
# Must be read as TEXT: a numeric column drops digits (Excel keeps only 15 significant
# digits; leading zeros vanish). The first billed month is the OLDEST (rightmost) digit.
COL_DPD = "dpd_history_str"

# --- Spark mode dataset ----------------------------------------------------------------
# One row per credit-card account with its DPD bucket-history string AS OF THE LATEST
# MONTH. For the backtest it must contain ALL card accounts that were in buckets 4–7
# `BACKTEST_MONTHS` ago — including those that have since rolled to 8+ or closed — and
# every string must end in the same (latest) month. If only today's spine is available,
# set DS_STRINGS_HAS_EXITED = False: outcome checks are skipped, stability checks run on
# the survivors.
DS_STRINGS_TMPL = "{model_id}.<<FILL-IN: dataset with one DPD-history string per card account>>"
DS_STRINGS_HAS_EXITED = True
KEY = "<<FILL-IN: account key column>>"          # used only for counting distinct accounts

# Several snapshots per account? Name the snapshot column; the latest snapshot is used.
COL_SNAPSHOT = None
# Date the string was last updated, if it can lag the snapshot (strings frozen at
# charge-off / closure). Rows whose string is older than the latest are excluded from the
# backtest, because their newest digit is not "today". None = all strings are current.
COL_STRING_AS_OF = None
# Optional Spark SQL filter applied first (scope), e.g. "product_type = 'CREDIT_CARD'".
ROW_FILTER = None

# --- reliable history window --------------------------------------------------------------
# DPD history is only reliable from RELIABLE_FROM onwards. Every string is cropped to the
# months from RELIABLE_FROM to SNAPSHOT_MONTH (the month of the leftmost digit), inclusive;
# older (rightmost) digits are dropped. A cropped string's oldest digit is NOT the first
# billed month, so a cropped account can never be EPD, and a spell that started before
# the window is not a data-quality case. Set RELIABLE_FROM = None to keep full strings.
SNAPSHOT_MONTH = "2026-08"
RELIABLE_FROM = "2024-01"


def _months_between(first: str, last: str) -> int:
    y0, m0 = map(int, first.split("-"))
    y1, m1 = map(int, last.split("-"))
    return (y1 - y0) * 12 + (m1 - m0) + 1


# The source may itself be a fixed-length extract (the sign-off file pivots every account
# onto a fixed grid). A string that fills the whole window may have older history, so
# it is treated as cropped (never EPD, never "history starts delinquent"). None = full history.
SOURCE_WINDOW_MONTHS = None          # the sign-off file now carries full history

_reliable = _months_between(RELIABLE_FROM, SNAPSHOT_MONTH) if RELIABLE_FROM else None   # 32
MAX_HISTORY_MONTHS = min(x for x in (_reliable, SOURCE_WINDOW_MONTHS) if x) if (_reliable or SOURCE_WINDOW_MONTHS) else None   # 24

# --- string conventions ------------------------------------------------------------------
LEFTMOST_IS_CURRENT = True    # '54320002000': leftmost digit = current month's bucket
CHAR_MAP = {}                 # non-digit BUCKET codes -> digit, e.g. a write-off letter {"W": "9"}.
                              # Never map a pre-opening / padding character to a bucket.
STRIP_CHARS = " "             # removed from the two ENDS only (padding); never mid-string
SPINE_BUCKETS = (4, 5, 6, 7)  # today's spine
EXIT_BUCKET = 8               # 8+ is a different category (leaves the spine)
BACKTEST_MONTHS = 6           # outcomes are read from the newest k digits

# --- optional columns on the same dataset / file (None = not available) -------------------
# Other persona axes, at the latest month. Used only to MEASURE overlap with the
# deterioration states (orthogonality), never to assign states.
AXIS_COLS = {
    "credibility_score": None,      # 0–5 total
    "cred_ptp_points": None,        # 0–2  payment promises kept
    "cred_money_in_points": None,   # 0–2  money coming in, last 3 months
    "cred_clean_point": None,       # 0–1  pre-delinquency history clean
    "ability_score": None,          # salary / inflow / CASA score
    "reachable_flag": None,         # locatability
    "in_country_flag": None,        # locatability
}
# The bank's existing implementations of the two known states, if they exist as columns
# (1/0, Y/N or True/False). Used to measure agreement with this package's
# early_payment_default (the bank's "bust-out") and stabilized.
EXISTING_RULE_COLS = {
    "existing_bust_out": None,
    "existing_stabilized": None,
}
# Data-quality flags that change how a hold should be read (frozen bucket, not paid).
FLAG_COLS = {
    "payment_holiday_flag": None,
    "restructured_flag": None,
}
