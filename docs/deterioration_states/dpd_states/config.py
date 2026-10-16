"""Workplace configuration — the ONLY file that needs editing to run on real data.

Every <<FILL-IN>> must be replaced with a name discovered in the workplace repo / Kedro
catalog. Never guess a dataset or column name: if it cannot be found, ask the user.
`model_id` is NOT configured here — the snippet resolves it from the caller or globals.
"""

# --- dataset -------------------------------------------------------------------
# One row per credit-card account with its DPD bucket-history string AS OF THE LATEST
# MONTH. For the backtest it must contain ALL card accounts that were in buckets 4–7
# `BACKTEST_MONTHS` ago — including those that have since rolled to 8+ or closed —
# not only today's spine. If only today's spine is available, the backtest is skipped
# (set DS_STRINGS_HAS_EXITED = False) and the outcome checks report SKIPPED.
DS_STRINGS_TMPL = "{model_id}.<<FILL-IN: dataset with one DPD-history string per card account>>"
DS_STRINGS_HAS_EXITED = True

KEY = "<<FILL-IN: account key column>>"          # used only for counting distinct accounts
COL_DPD = "<<FILL-IN: DPD bucket-history string column>>"

# If the dataset holds several snapshots per account, name the snapshot column; the
# latest snapshot is used. None = the dataset is already one row per account.
COL_SNAPSHOT = None
# Optional Spark SQL filter applied first (scope), e.g. "product_type = 'CREDIT_CARD'".
ROW_FILTER = None

# --- string conventions ----------------------------------------------------------
LEFTMOST_IS_CURRENT = True    # '54320002000': leftmost digit = current month's bucket
CHAR_MAP = {}                 # non-digit codes -> digit, e.g. {"X": "9", "W": "9"}
STRIP_CHARS = " "             # characters removed before parsing (padding, separators)
SPINE_BUCKETS = (4, 5, 6, 7)  # today's spine
EXIT_BUCKET = 8               # 8+ is a different category (leaves the spine)
BACKTEST_MONTHS = 6           # outcomes are read from the newest k digits

# --- optional columns on the same dataset (None = not available) -----------------
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
# (1/0). Used to measure agreement with this package's bust_out and holding.
EXISTING_RULE_COLS = {
    "existing_bust_out": None,
    "existing_stabilized": None,
}
# Data-quality flags that change how a hold should be read (frozen bucket, not paid).
FLAG_COLS = {
    "payment_holiday_flag": None,
    "restructured_flag": None,
}
