"""Build the A1 ability model document (business-facing).

    python build_a1_workbook.py [--out a1_ability_reference.xlsx]

The rules follow ``workplace_mirror/specs/A1_ability_spec.md``. Every worked example is run
through the reference rules below and the build FAILS if an example no longer gets the level
or state it illustrates. Results are entry cells (pale yellow) for 31 Aug 2026: the 61–180 states
and Unknown reasons from the bundle 14 check, everything else from the bundle 12 check (income
and liquidity are unchanged by bundle 14; 180+ was not re-checked). Shares are formulas.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import DataBarRule
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "locatability"))
from build_a2_workbook import (  # noqa: E402
    CENTER, INPUT_FILL, MID, MUTED, NAVY, TONE, WINDOW_FILL, WINDOW_HEAD, Sheet, _fill, _fit, _font,
)

# --- rules (reference implementation, monthly granularity) ---------------------------------
W = 3  # months, the scoring month included (61–180 DPD)
OFFSETS = range(1 - 2 * W, 1)  # the prior window and the window, 0 = the scoring month
F_INC, K_INC, F_CASA, K_CASA, F_PAY, K_PAY, DEMIN = 3000, 2, 3000, 1, 500, 1, 1000
FLOORS_IN_TOTAL, D_INC, D_CASA, CASA_MONTHS = 2, 0.25, 0.50, 2


def in_window(k: int) -> bool:
    return k > -W


def income_months(internal: dict, pulls: dict) -> dict:
    """One amount per month: an AECB pull counts in its month and the next, the larger of
    internal and AECB wins."""
    aecb = {**{k + 1: v for k, v in pulls.items()}, **pulls}
    return {k: max(internal.get(k, 0), aecb.get(k, 0)) for k in OFFSETS}


def income_level(internal: dict, pulls: dict, anchor: float = 0) -> str:
    """With no internal salary in either window the 25% check compares the average of the
    months with a value: AECB alerts arrive only on a change."""
    amounts = income_months(internal, pulls)
    now = sum(v for k, v in amounts.items() if in_window(k))
    if any(internal.get(k, 0) >= DEMIN for k in OFFSETS):
        recent, prior = now / W, sum(v for k, v in amounts.items() if not in_window(k)) / W
    else:
        seen = set(internal) | set(pulls) | {k + 1 for k in pulls}
        level = [[amounts[k] for k in OFFSETS if k in seen and in_window(k) == w] for w in (True, False)]
        recent, prior = (sum(v) / len(v) if v else 0 for v in level)
    if now >= FLOORS_IN_TOTAL * max(F_INC, K_INC * anchor) and recent >= prior * (1 - D_INC):
        return "stable"
    return "weak" if any(v >= DEMIN for k, v in amounts.items() if in_window(k)) else "none"


def liquidity_level(casa: dict, payment: float = 0, anchor: float = 0) -> str:
    now = [v for k, v in casa.items() if in_window(k)]
    prior = [v for k, v in casa.items() if not in_window(k)]
    floor = max(F_CASA, K_CASA * anchor)
    holding = not prior or sum(now) / W >= sum(prior) / len(prior) * (1 - D_CASA)
    if (sum(v >= floor for v in now) >= CASA_MONTHS and holding) or payment >= max(F_PAY, K_PAY * anchor):
        return "adequate"
    return "weak" if any(v >= DEMIN for v in now) or payment >= DEMIN else "none"


def ability(income: str, liquidity: str, distress: bool, active: bool) -> str:
    points = {"stable": 2, "weak": 1}.get(income, 0) + {"adequate": 2, "weak": 1}.get(liquidity, 0)
    if points == 0 and not distress and not active:
        return "unknown"
    if points == 4:
        return "moderate" if distress else "high"
    return "moderate" if points >= 2 and not distress else "low"


# --- design ---------------------------------------------------------------------------------
STATES = ["high", "moderate", "low", "unknown"]
LABEL = {"high": "High", "moderate": "Moderate", "low": "Low", "unknown": "Unknown",
         "stable": "Stable", "weak": "Weak", "none": "None",
         "adequate": "Adequate"}
FILLS = {"high": ("A9D08E", "274E13"), "moderate": TONE["good"], "low": TONE["bad"],
         "unknown": TONE["unknown"]}
LEVEL_TONE = {"stable": "high", "adequate": "high", "weak": "moderate", "none": "unknown"}
SERIES = {"high": "2E7D32", "moderate": "8BC34A", "low": "D9652B", "unknown": "9E9E9E"}
BAR = "9DC3E6"  # share bars: structure, not a state
PULL, CARRIED, CLOSED = ("DDEBF7", "1F4E79"), ("EEF5FB", "1F4E79"), TONE["bad"]


def chip(s: Sheet, col: int, tone: str, label: str | None = None, span: int = 1):
    fill, ink = FILLS[tone]
    return s.text(col, label or LABEL[tone], span=span, bold=True, color=ink, fill=fill, align=MID)


# --- results (31 Aug 2026: 61–180 states from the bundle 14 check, the rest bundle 12) -----
RESULTS_DATE = "31 Aug 2026"
BOOKS = ["Credit cards 61–180", "Retail loans 61–180", "Credit cards 180+", "Retail loans 180+"]
TOTALS = (19292, 3985, 318663, 55371)  # accounts, in the order of BOOKS
RL_PRODUCTS = ["Personal Loans", "Personal Cash Loans", "Auto"]
STATE_TOTALS = {"61–180 DPD": (19292, 3985, 1397, 1224, 1364),
                "180+ DPD": (318663, 55371, 33862, 10306, 11203)}
STATE_BLOCKS = [  # (DPD, first row on the Results sheet, rows: state, cards, loans, loan products)
    ("61–180 DPD", 6, [  # bundle 14 logged only Unknown by product
        ("high", 45, 11, None, None, None), ("moderate", 2769, 354, None, None, None),
        ("low", 5568, 1783, None, None, None), ("unknown", 10910, 1837, 705, 492, 640),
    ]),
    ("180+ DPD", 14, [
        ("high", 111, 17, 11, 3, 3), ("moderate", 19907, 1987, 748, 781, 458),
        ("low", 19991, 3793, 1174, 1866, 753), ("unknown", 278654, 49574, 31929, 7656, 9989),
    ]),
]
DETAIL = [  # counts in the order of BOOKS; None = does not apply
    ("Income: who shows the salary, and the level it reaches", [
        ("Stable · internal salary only", "high", 190, 41, 335, 51),
        ("Stable · AECB salary only", "high", 2778, 317, 20827, 1927),
        ("Stable · both", "high", 28, 13, 75, 16),
        ("Weak · internal salary only", "moderate", 209, 143, 176, 71),
        ("Weak · AECB salary only", "moderate", 1758, 229, 10096, 1217),
        ("Weak · both", "moderate", 13, 8, 27, 11),
        ("None · no salary of AED 1,000 or more in the window", "unknown", 14316, 3234, 287127, 52078),
    ]),
    ("Income with an AECB salary in the window: why it is Stable or Weak", [
        ("Stable · 1 AECB month in the window", "high", 459, 46, 807, 68),
        ("Stable · 2 AECB months", "high", 1286, 165, 4495, 449),
        ("Stable · 3 AECB months", "high", 1061, 119, 4325, 392),
        ("Stable · 4–6 AECB months (180+ only)", "high", None, None, 11275, 1034),
        ("Weak · window total reached, but more than 25% below the prior window", "moderate",
         848, 80, 4691, 430),
        ("Weak · window total not reached", "moderate", 923, 157, 5432, 798),
    ]),
    ("Liquidity: the arm that fired", [
        ("Adequate · CASA balance (no external card payment)", "high", 142, 46, 583, 255),
        ("Adequate · with an external card payment (card or CASA arm)", "high", 54, 11, 72, 10),
        ("Weak · CASA balance of AED 1,000 or more (no card payment)", "moderate", 327, 291, 760, 408),
        ("Weak · with an external card payment", "moderate", 15, 14, 3, 18),
        ("None · a card payment below AED 1,000", "unknown", 49, 14, 19, 9),
        ("None · no CASA balance or card payment", "unknown", 18705, 3609, 317226, 54671),
    ]),
    ("Distress in the window (61–180: bundle 14, loans ≈; 180+: bundle 12)", [
        ("No distress", "moderate", 17497, 3224, 310349, 53383),
        ("A cheque return, direct-debit return or bureau bounce", "low", 1795, 761, 8314, 1988),
    ]),
    ("High and Moderate: the combination that gave the state (bundle 12)", [
        ("High · Stable income, Adequate liquidity", "high", 46, 10, 111, 17),
        ("Moderate · Stable income, no liquidity", "moderate", 2597, 273, 19197, 1664),
        ("Moderate · no income, Adequate liquidity", "moderate", 89, 23, 436, 193),
        ("Moderate · Stable income, Weak liquidity", "moderate", 46, 19, 156, 47),
        ("Moderate · Weak income, Weak liquidity", "moderate", 29, 39, 66, 62),
        ("Moderate · Weak income, Adequate liquidity", "moderate", 21, 4, 30, 13),
        ("Moderate · 4 points with distress", "moderate", 16, 4, 22, 8),
    ]),
    ("Low: why (bundle 12)", [
        ("1 point (mostly Weak income, nothing else)", "low", 2164, 557, 10672, 1496),
        ("0 points, an active CASA where money does not stay", "low", 2049, 649, 1937, 572),
        ("0 points with distress", "low", 1153, 539, 5560, 1417),
        ("2–3 points with distress", "low", 322, 90, 1822, 308),
    ]),
    ("Unknown: why (61–180: bundle 14; 180+: bundle 12)", [
        ("Dormant CASA: no customer money movement in the window", "unknown", 5993, 1313, 38743, 13542),
        ("No CASA with us (no transaction or positive balance in 12 months)", "unknown",
         4917, 524, 239911, 36032),
    ]),
]
SUMMARIES = [
    ("Internal salary: latest month with AED 1,000 or more", [
        ("In the window", "high", 440, 205, 613, 149),
        ("4–6 months ago (in the window at 180+)", "moderate", 3094, 1146, None, None),
        ("7–12 months ago", "moderate", 3599, 888, 3172, 1273),
        ("13–24 months ago", "moderate", 1941, 528, 11280, 3963),
        ("No salary in 24 months (the history available)", "unknown", 10218, 1218, 303598, 49986),
    ]),
    ("Latest AECB salary alert of AED 1,000 or more", [
        ("In the window", "high", 3820, 472, 29248, 2981),
        ("4–6 months ago (in the window at 180+)", "moderate", 2319, 257, None, None),
        ("7–12 months ago", "moderate", 2077, 229, 9812, 1045),
        ("13–24 months ago", "moderate", 1346, 274, 12432, 1181),
        ("25 or more months ago", "moderate", 899, 284, 27234, 2248),
        ("Alert rows, never a salary", "unknown", 7693, 2325, 150930, 21760),
        ("No alert row", "unknown", 1138, 144, 89007, 26156),
    ]),
    ("Salary stopped: internal salary in the prior window, none in the window", [
        ("Stopped · no income in the window", "low", 2673, 1019, 2480, 1059),
        ("Stopped · Weak on AECB salary", "moderate", 208, 76, 347, 119),
        ("Stopped · Stable on AECB salary", "high", 213, 51, 345, 95),
        ("Not stopped", "unknown", 16198, 2839, 315491, 54098),
    ]),
    ("Highest monthly CASA balance in the window", [
        ("AED 3,000 or more", "high", 242, 158, 776, 407),
        ("AED 1,000–3,000", "moderate", 254, 193, 596, 274),
        ("Under AED 1,000", "low", 4775, 1410, 23929, 7237),
        ("No balance", "unknown", 14021, 2224, 293362, 47453),
    ]),
]
CROSS_COLS = ["AECB in window", "AECB 4–6 m", "AECB 7–12 m", "AECB 13+ m", "Never"]
CROSS = {  # internal salary (rows) x latest AECB salary alert; None = inside the 180+ window
    "Credit cards 61–180": [
        ("Internal in window", 37, 15, 14, 79, 295),
        ("Internal 4–6 m", 356, 120, 88, 297, 2233),
        ("Internal 7–12 m", 443, 264, 196, 309, 2387),
        ("Internal 13–24 m", 280, 163, 186, 212, 1100),
        ("No internal in 24 m", 2704, 1757, 1593, 1348, 2816),
    ],
    "Retail loans 61–180": [
        ("Internal in window", 21, 1, 4, 29, 150),
        ("Internal 4–6 m", 99, 46, 41, 177, 783),
        ("Internal 7–12 m", 109, 61, 42, 136, 540),
        ("Internal 13–24 m", 93, 48, 40, 76, 271),
        ("No internal in 24 m", 150, 101, 102, 140, 725),
    ],
    "Credit cards 180+ (6-month window)": [
        ("Internal in window", 97, None, 30, 127, 359),
        ("Internal 7–12 m", 637, None, 237, 300, 1998),
        ("Internal 13–24 m", 2012, None, 838, 1642, 6788),
        ("No internal in 24 m", 26502, None, 8707, 37597, 230792),
    ],
    "Retail loans 180+ (6-month window)": [
        ("Internal in window", 25, None, 5, 13, 106),
        ("Internal 7–12 m", 191, None, 81, 179, 822),
        ("Internal 13–24 m", 643, None, 272, 642, 2406),
        ("No internal in 24 m", 2122, None, 687, 2595, 44582),
    ],
}
TREND = {  # month: (accounts, high, moderate, low, unknown %)
    "Credit cards 61–180": {
        "Jan": (14664, 0.44, 19.94, 27.73, 51.90), "Feb": (14576, 0.41, 19.47, 27.35, 52.77),
        "Mar": (14455, 0.33, 18.71, 27.76, 53.21), "Apr": (14671, 0.31, 18.68, 27.39, 53.62),
        "May": (15890, 0.34, 18.02, 30.20, 51.44), "Jun": (16982, 0.28, 17.57, 30.76, 51.39),
        "Jul": (18397, 0.29, 15.59, 31.92, 52.19), "Aug": (19292, 0.24, 14.50, 29.48, 55.77),
    },
    "Retail loans 61–180": {
        "Jan": (2324, 0.04, 12.61, 46.13, 41.22), "Feb": (2213, 0.09, 10.85, 44.33, 44.74),
        "Mar": (2218, 0.14, 11.09, 46.03, 42.74), "Apr": (2661, 0.15, 12.14, 47.50, 40.21),
        "May": (3096, 0.10, 11.82, 48.80, 39.28), "Jun": (3514, 0.17, 10.36, 48.78, 40.69),
        "Jul": (3728, 0.08, 9.68, 47.37, 42.86), "Aug": (3985, 0.25, 9.08, 46.05, 44.62),
    },
    "Credit cards 180+": {
        "Jan": (305257, 0.03, 6.19, 6.51, 87.27), "Feb": (306854, 0.02, 6.22, 6.53, 87.23),
        "Mar": (308742, 0.03, 6.29, 6.46, 87.22), "Apr": (310709, 0.03, 6.35, 6.43, 87.20),
        "May": (312626, 0.03, 6.35, 6.36, 87.26), "Jun": (314827, 0.03, 6.43, 6.03, 87.50),
        "Jul": (316738, 0.03, 6.33, 6.34, 87.30), "Aug": (318663, 0.03, 6.25, 6.27, 87.44),
    },
    "Retail loans 180+": {
        "Jan": (52657, 0.02, 3.30, 6.73, 89.96), "Feb": (52882, 0.03, 3.33, 6.65, 89.98),
        "Mar": (53270, 0.04, 3.46, 6.68, 89.83), "Apr": (53615, 0.03, 3.45, 6.74, 89.78),
        "May": (54006, 0.03, 3.47, 6.74, 89.76), "Jun": (54383, 0.03, 3.53, 6.40, 90.04),
        "Jul": (54819, 0.03, 3.54, 6.68, 89.75), "Aug": (55371, 0.03, 3.59, 6.85, 89.53),
    },
}
NOTES = [
    "The state rests almost entirely on income, and income mostly on AECB salary alerts: "
    "'Weaknesses'.",
    "CASA = current and savings accounts only (WM's 49 scheme codes). Loan accounts, term "
    "deposits and other schemes do not count, so 524 loan Unknowns at 61–180 now have no CASA "
    "with us (413 of them Auto).",
    "Cards 61–180: Moderate falls from 19.9% in January to 14.5% in August while the book grows by "
    "a third. The raw alert feed misses 6 and 31 August and is thin on 24 August.",
    "At 180+ about 9 in 10 accounts are Unknown: most no longer hold a CASA with us. Cards at 180+ "
    "have no amount due, so the floors are flat (Stable needs AED 9,000 over six months).",
    "Loan thresholds are higher: one instalment (median AED 2,389) against the card's oldest "
    "overdue amount (median AED 837).",
    "Loan products at 61–180: the bundle 14 check gave only Unknown by product (blank cells).",
]
WEAK_BLOCKS = [  # counts in the order of BOOKS (bundle 12, except where named)
    ("Liquidity: almost never confirmed", [
        ("Adequate", "high", 196, 57, 655, 265),
        ("Weak", "moderate", 342, 305, 763, 426),
        ("None", "unknown", 18754, 3623, 317245, 54680),
        ("Highest monthly CASA balance in the window AED 3,000 or more", "high", 242, 158, 776, 407),
    ]),
    ("Income: Stable, and where it comes from", [
        ("Stable income", "high", 2996, 371, 21237, 1994),
        ("Stable on an AECB salary alone", "moderate", 2778, 317, 20827, 1927),
        ("Stable with an internal salary", "high", 218, 54, 410, 67),
        ("Any internal salary of AED 1,000 or more in the window", "high", 440, 205, 613, 149),
    ]),
    ("What the states rest on", [
        ("High (61–180: bundle 14)", "high", 45, 11, 111, 17),
        ("Moderate · Stable income, no liquidity", "moderate", 2597, 273, 19197, 1664),
        ("Moderate · resting on an AECB salary alone", "moderate", 2525, 268, 19113, 1708),
        ("Unknown · no CASA with us (61–180: bundle 14)", "unknown", 4917, 524, 239911, 36032),
    ]),
]
WEAK_FINDINGS = [
    ("Liquidity is dry", "Liquidity is Adequate for 1.0% of card and 1.4% of loan accounts at 61–180, "
     "and 0.2–0.5% at 180+. The bank sweeps CASA balances against overdue amounts (GRR), so a "
     "balance shows whether a sweep happened, not whether the customer can pay. External card "
     "payments are rare (118 card, 39 loan accounts)."),
    ("High is rare by construction", "High needs Stable income and Adequate liquidity. With "
     "liquidity dry, High is 0.2–0.3% of the books at 61–180 and 0.03% at 180+, whatever the "
     "customer's income."),
    ("The state is an income signal", "93% of card and 75% of loan Moderate at 61–180 is Stable "
     "income with no liquidity at all. Low is mostly Weak income, or distress. The two-dimension map "
     "works as one dimension."),
    ("Income is mainly bureau", "93% of card and 85% of loan Stable income at 61–180 comes from an "
     "AECB salary alone (97–98% at 180+). Only 2.3% of card and 5.1% of loan accounts had an "
     "internal salary in the window."),
    ("And the bureau source is thin", "The alert table sends a row only when the salary changes; "
     "a pull counts for its month and the next. A steady salary often never alerts, a stop is "
     "mostly an empty closure alert. AECB Stable cards cure 14.4% against 33.0% for internal "
     "Stable ('Validation'). The richer AECB tables cannot yet be linked to our customers."),
    ("No CASA means a ceiling", "Without a CASA with us there is no internal salary and no "
     "liquidity, so the best state is Moderate, on an AECB salary. That is 4,917 card and 524 loan "
     "Unknowns at 61–180 (loans mostly Auto)."),
    ("The scale itself works", "States rank payment and cure in order; High cures 33.6% against "
     "16.3% for Moderate, and internal Stable customers cure like High. The weakness is coverage, "
     "not the ranking."),
]
WEAK_DIRECTIONS = [
    ("Liquidity from flows", "Money moving through the account (credits, own spending) survives "
     "a sweep; a balance does not."),
    ("Independent evidence", "Score income, inflows, spending and other products with us as "
     "separate families, so High needs agreement between them rather than one salary signal. "
     "Signals only from windows ending at the scoring date (GRR)."),
    ("Frequent bureau salary", "GRR's feed of AECB pulls every 2 months, with the last level "
     "carried until the next pull or a stop ('AECB coverage')."),
    ("Bureau link", "Linking the AECB report tables to our customers would add obligations "
     "elsewhere and the customer's standing with other lenders."),
]
AECB_BLOCKS = [  # counts in the order of BOOKS
    ("Accounts whose state rests on an AECB salary alone (no internal salary in the window)", [
        ("High", "high", 8, 0, 44, 5),
        ("Moderate", "moderate", 2525, 268, 19113, 1708),
        ("Low", "low", 2003, 278, 11766, 1431),
    ]),
    ("Coverage gap: latest AECB salary alert of AED 1,000 or more, when it is not in the window", [
        ("4–12 months ago: known, but too old to count (7–12 at 180+)", "moderate",
         4396, 486, 9812, 1045),
        ("13–24 months ago", "moderate", 1346, 274, 12432, 1181),
        ("25 or more months ago", "unknown", 899, 284, 27234, 2248),
        ("Alert rows, never a salary alert (a steady salary never alerts)", "unknown",
         7693, 2325, 150930, 21760),
        ("No alert row: not in the alert feed", "unknown", 1138, 144, 89007, 26156),
    ]),
    ("What-if: the last AECB salary still holds (cards only)", [
        ("Unknown today (S0)", "unknown", 10760, 1778, 278654, 49574),
        ("Unknown if an AECB salary of the last 6 months held (S6)", "unknown",
         9456, None, 275373, None),
        ("Unknown if an AECB salary of the last 12 months held (S12)", "unknown",
         9047, None, 273861, None),
        ("High + Moderate today (S0)", "moderate", 2844, 372, 20018, 2004),
        ("High + Moderate (S6)", "moderate", 3902, None, 23983, None),
        ("High + Moderate (S12)", "moderate", 4265, None, 25824, None),
    ]),
]
AECB_TODAY_VS_FREQUENT = [  # topic, today, with pulls every 2 months
    ("Source", "AECB alert table: a row only when something changes (salary changed, salary "
     "account added or closed).", "A pull for every customer every 2 months."),
    ("When a salary counts", "The pull's month and the next one; never earlier.",
     "The same rule: consecutive pulls fill 2–3 months of the 3-month window (all 6 at 180+)."),
    ("Steady salary", "Often never alerts, so it is invisible: 'Alert rows, never a salary alert'.",
     "Seen on every pull; at or above the threshold it reaches Stable with no rule change."),
    ("Stopped salary", "Seen only as a closure alert, a lower amount, or the end of an internal "
     "salary; silence says nothing.", "A pull with no salary shows the stop within 2 months."),
    ("25% rule", "The level check stops fewer alerts looking like a fall.",
     "Monthly values make the total and the level agree; the rule works as designed."),
    ("Quality", "AECB Stable cures 14.4% against 33.0% for internal Stable (cards, 'Validation'): "
     "alerts are partly stale.", "Expected closer to internal salary; to be re-validated."),
    ("Expected effect", "Unknown 55.8% of cards and 44.6% of loans at 61–180; 87.4% of cards at "
     "180+.", "Cards: Unknown to 49.0–46.9% at 61–180 (S6–S12), 86.4–85.9% at 180+; almost all "
     "moves are Unknown or Low to Moderate or Low. More may come from customers never on a salary "
     "alert, which no what-if can show."),
    ("Where the gain is", "At 61–180, 56% of card Unknowns never had an AECB salary; 70% of the "
     "never-alerted card group has an internal salary in 24 months.", "The 2-monthly pull is the "
     "only way to see them. At 180+, 84% never had one and few have any salary with us: Unknown "
     "there is coverage, not freshness."),
]
VALIDATION_DATE = "cohort months Jan–May 2026, outcomes over the next 3 months"
VALIDATION = [  # (book, [(state, cure, roll, pay any)] in %)
    ("Credit cards 61–180", [("high", 33.6, 51.7, 53.5), ("moderate", 16.3, 72.4, 42.2),
                             ("low", 12.1, 80.4, 32.5), ("unknown", 7.9, 87.5, 19.1)]),
    ("Retail loans 61–180", [("moderate", 14.9, 70.3, 63.1), ("low", 10.8, 80.3, 47.8),
                             ("unknown", 8.2, 86.3, 34.4)]),
]
VALIDATION_FINDINGS = [
    ("States rank", "Every state cures and pays more, and rolls less, than the one below it, "
                    "on cards and loans. One exception: card charge-off, Moderate 43.9% against "
                    "Low 42.2%. Loan High has under 10 accounts."),
    ("AECB salary helps", "Among customers who would otherwise be Unknown, AECB Stable pays within "
                          "3 months 17.7 points (cards) and 23.5 points (loans) more often and rolls "
                          "10.7 and 14.0 points less. AECB Weak gives about half of that."),
    ("AECB is weaker than internal", "Card Stable on internal salary cures 33.0% and pays 61.0%; "
                                     "Stable on AECB salary cures 14.4% and pays 40.7%."),
    ("Stopped salary", "Stopped internal salary cures 10 points less and pays 15 points less. The "
                       "AECB salary often outlasts the stop."),
    ("25% check", "Accounts failing it only on fewer alert months behaved like Stable, real "
                  "falls in level like Weak; the rule now treats them so."),
]
RULE_25 = [  # pooled Jan–May rows, cards 61–180 unless named
    ("Fewer alert months, same level (Stable since the level check)", "2,793", "–", "–",
     "−1.8 (ns)"),
    ("Real fall in level, cards (Weak under the rule)", "774", "−5.5", "+8.3", "−11.8"),
    ("Real fall in level, loans", "83", "ns", "ns", "ns"),
]
RULE_25_OPTIONS = [
    ("What the rule still does", "It holds at Weak an account whose salary reached the window "
     "total but fell by more than 25%: a lower AECB amount, or an internal salary that stopped "
     "and was replaced by one AECB pull."),
    ("Keep (current choice)", "On cards the real falls pay 11.8 points less and roll 8.3 "
     "points more than Stable: they are not Stable customers. The part of the rule that was wrong "
     "(fewer alert months) is already fixed by the level check."),
    ("Remove", "Simpler rule: Stable = the window total alone. 848 card and 80 loan accounts at "
     "61–180 (4,691 and 430 at 180+) become Stable and gain one point, so up to that many move up "
     "one state, mostly Low to Moderate."),
    ("Evidence gaps", "Loans: 83 rows, no difference shown either way. 180+: not validated. "
     "Accounts with internal salary only that fail the rule are not counted in the check."),
]


# --- sheets ---------------------------------------------------------------------------------
def overview(wb: Workbook) -> None:
    s = Sheet(wb.active, [31, 31, 31, 31])
    s.ws.title = "Overview"
    s.title("A1 Ability", "Can the customer pay? Income and liquidity give points, payment distress "
                          "lowers the state, and Unknown marks customers whose money we cannot see.")
    for k, v in [
        ("Scope", "Credit cards and retail loans (Personal Loans, Personal Cash Loans, Auto) at "
                  "61–180 DPD (3-month window) and 180+ DPD (6-month window)."),
        ("Customer level", "Salary, CASA, card payments and distress are read across all accounts "
                           "of the customer (CIF)."),
        ("Principle", "The state reflects only money we can see. Unknown is absence of data, not "
                      "evidence of no ability."),
    ]:
        s.text(1, k, bold=True, color=NAVY, border=False)
        s.text(2, v, span=3, border=False)
        _fit(s.ws, s.r, [(v, s.width(2, 4))], floor=18)
        s.r += 1

    s.section(f"At a glance, {RESULTS_DATE}")
    for j, st in enumerate(STATES, 1):
        chip(s, j, st).alignment = CENTER
    s.ws.row_dimensions[s.r].height = 20
    s.r += 1
    glance = [(f"{book} {dpd.split()[0]}", count, share, first)
              for dpd, first, _ in STATE_BLOCKS
              for book, count, share in (("credit cards", "B", "C"), ("retail loans", "D", "E"))]
    for name, count, share, first in glance:
        for j, _ in enumerate(STATES):
            cell = s.text(j + 1, f"=Results!{share}{first + j}", align=CENTER)
            cell.font, cell.number_format = _font(size=20, bold=True, color=NAVY), "0.0%"
        s.ws.row_dimensions[s.r].height = 34
        s.r += 1
        for j, _ in enumerate(STATES):
            ref = f"Results!{count}{first + j}"
            s.text(j + 1, f'=TEXT({ref},"#,##0")&" {name}"', color=MUTED, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("States")
    s.header(["State", "Rule", "In plain words"], [1, 2, 1])
    for st, rule, plain in [
        ("high", "4 points and no distress", "Regular income and a buffer, both confirmed."),
        ("moderate", "2–3 points and no distress, or 4 points with distress",
         "One side confirmed, or both partly; or everything in place but a payment just failed."),
        ("low", "0–1 points, or under 4 points with distress",
         "What we can see shows little or nothing to pay with."),
        ("unknown", "0 points, no distress, and no CASA with us or a dormant one",
         "We cannot see the customer's money."),
    ]:
        chip(s, 1, st)
        s.text(2, rule, span=2, align=MID)
        s.text(4, plain, align=MID)
        _fit(s.ws, s.r, [(rule, s.width(2, 3)), (plain, s.widths[3])])
        s.r += 1

    s.section("State map: income points + liquidity points, then distress")
    for distress in (False, True):
        s.text(1, "With distress" if distress else "No distress", bold=True, color="FFFFFF",
               fill=NAVY, align=CENTER)
        for j, liq in enumerate(("adequate", "weak", "none"), 2):
            s.text(j, f"Liquidity {LABEL[liq]}", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
        for inc in ("stable", "weak", "none"):
            s.text(1, f"Income {LABEL[inc]}", bold=True, align=MID)
            for j, liq in enumerate(("adequate", "weak", "none"), 2):
                st = ability(inc, liq, distress, True)
                label = LABEL[st]
                if inc == liq == "none" and not distress:
                    label += " (Unknown if CASA dormant or absent)"
                chip(s, j, st, label).alignment = CENTER
            s.ws.row_dimensions[s.r].height = 22
            s.r += 1
        s.r += 1
    s.note("Rules: 'Logic'. Why High is rare and the state is mostly a bureau-salary signal: "
           "'Weaknesses'. Which rule gave each state: 'Results detail'.")
    s.ws.freeze_panes = "A4"


def thresholds(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Thresholds"), [58, 16])
    s.title("Thresholds", "Starting values, not yet tuned on results.")
    s.header(["Threshold", "Value"])
    for name, value in [
        ("Window (the scoring month included), 61–180 DPD / 180+ DPD", "3 / 6 months"),
        ("Months of the window at the CASA floor", "2 of 3"),
        ("Salary floor, internal and AECB", "AED 3,000"),
        ("Income: multiple of the amount due", "2.0"),
        ("Stable: window total, multiples of the income threshold (3 at 180+)", "2"),
        ("Income weakening: fall of the window total vs the prior window", "25%"),
        ("AECB salary: months counted after the extract month", "1"),
        ("CASA average balance floor", "AED 3,000"),
        ("CASA: multiple of the amount due", "1.0"),
        ("CASA weakening: fall of the average vs the prior window", "50%"),
        ("External card payment floor", "AED 500"),
        ("External card payment: multiple of the amount due", "1.0"),
        ("Smallest amount that counts as evidence", "AED 1,000"),
        ("Distress events in the window that count", "1"),
        ("Points needed for High / Moderate", "4 / 2"),
        ("CASA held: months of history for a leg or positive balance", "12"),
    ]:
        s.text(1, name, align=MID)
        s.text(2, value, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.r += 1
    s.note("The amount due: the oldest overdue bucket on cards (none at 180+), one instalment on loans.")
    s.ws.freeze_panes = "A4"


def logic(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Logic"), [26, 62, 30])
    s.title("Logic", "What the model computes for each account at the end of the scoring month. The "
                     "window is the scoring month and the 2 before it; the prior window is the 3 "
                     "months before that.")

    def table(title: str, heads: list[str], rows: list, gap: int = 1) -> None:
        s.section(title, gap=gap)
        s.header(heads)
        for row in rows:
            for j, v in enumerate(row, 1):
                s.text(j, v, bold=j == 1, align=MID)
            _fit(s.ws, s.r, [(v, s.widths[j]) for j, v in enumerate(row)])
            s.r += 1

    table("Points", ["Consideration", "Rule", "Result"], [
        ("Income: Stable", "One salary amount per month. The window's total at least 2 × the "
                           "threshold, and no more than 25% below the prior window. Threshold = "
                           "max(AED 3,000, 2 × the amount due). With no salary with us in either "
                           "window, the 25% compares the average of the months with an AECB value: "
                           "alerts arrive only on a change.", "2 points"),
        ("Income: Weak", "Not Stable, but AED 1,000 or more in any month of the window.", "1 point"),
        ("Income: None", "Nothing of AED 1,000 or more in the window.", "0 points"),
        ("Liquidity: Adequate", "CASA average balance at least max(AED 3,000, the amount due) in 2 of 3 "
                                "months and no more than 50% below the prior window; or an external "
                                "card payment of at least max(AED 500, the amount due).", "2 points"),
        ("Liquidity: Weak", "Not Adequate, but a balance or card payment of AED 1,000 or more.", "1 point"),
        ("Liquidity: None", "Neither.", "0 points"),
        ("Distress", "A cheque bounce, DDS return or new bureau bounce in the window.", "Down one level"),
        ("Activity gate", "0 points, no distress and no customer money movement in the window.",
         "Unknown instead of Low"),
    ], gap=0)
    table("Salary per month", ["Source", "Rule", "Timing"], [
        ("Internal salary", "The month's salary-flagged credits with us, bonuses included.",
         "The month of the credit."),
        ("AECB salary", "The reported average salary on a salary alert (average salary changed, "
                        "salary account added), accurate on the pull date.",
         "The pull's month and the next one, never earlier and no later."),
        ("Salary account closed", "An AECB closure alert ends the AECB salary.", "From the alert."),
        ("One amount per month", "The larger of internal and AECB, never the sum.", "Each month."),
    ])
    table("Distress", ["Source", "Rule", "Timing"], [
        ("Cheque / DDS return", "A returned cheque or direct debit on any current or savings "
                                "account of the customer.", "The month of the return."),
        ("Bureau bounce", "A bounced cheque reported by AECB; one per day, the largest amount.",
         "The day it was returned."),
    ])
    table("Customer money movement (the activity gate)", ["", "Transactions", ""], [
        ("Counts", "Transfers in and out, remittances, cash, clearing, bill payments, card spend, "
                   "paying their own credit card.", ""),
        ("Does not count", "The bank recovering the customer's loan instalment, transfers between "
                           "their own accounts, fees, interest, reversals.", ""),
        ("Which accounts", "Current and savings accounts only (WM's 49 scheme codes); loan "
                           "accounts, term deposits and other schemes do not count.", ""),
    ])
    s.ws.freeze_panes = "A4"


INCOME_EXAMPLES = [  # level, internal, AECB pulls, anchor, why
    ("stable", {-1: 5000, 0: 5000}, {}, 0, "Two salaries with us, 10,000 against 6,000."),
    ("stable", {-1: 10000}, {}, 0, "Employer paid two salaries in one month: the total counts."),
    ("stable", {-2: 2000, -1: 2000, 0: 2000}, {}, 0, "Three salaries of 2,000 reach the 6,000 total."),
    ("stable", {}, {-2: 3000}, 0, "AECB pull in the window's first month: counts for 2 months."),
    ("stable", {}, {0: 6000}, 0, "AECB pull this month: one month, but 6,000 reaches the total."),
    ("stable", {}, {-2: 3000, 0: 3000}, 0, "Pulls every 2 months fill the window."),
    ("stable", {}, {-3: 6000}, 0, "Pull just before the window carries into its first month."),
    ("stable", {}, {-5: 5000, -4: 5000, 0: 7000}, 0,
     "Fewer alerts, same level: 7,000 against an average of 5,000. No salary with us, so the "
     "level is compared, not the totals (7,000 against 15,000)."),
    ("weak", {}, {0: 3000}, 0, "AECB pull this month at 3,000: one month, 3,000 against 6,000."),
    ("weak", {-2: 1200, 0: 4000}, {}, 0, "Salary, but 5,200 against the 6,000 total."),
    ("weak", {-1: 5000, 0: 5000}, {}, 3000, "AED 3,000 overdue lifts the total needed to 12,000."),
    ("weak", {-5: 10000, -4: 10000, -3: 10000}, {-1: 10000}, 0,
     "Salary with us stopped; one AECB pull gives 20,000 against 30,000: more than 25% below."),
    ("weak", {}, {-4: 7000, -1: 4000}, 0, "AECB level fell: 8,000 against 14,000."),
    ("weak", {}, {-2: 3000, -1: 0}, 0, "Salary account closed: the AECB amount does not carry."),
    ("none", {0: 800}, {}, 0, "Below AED 1,000."),
    ("none", {}, {-4: 9000}, 0, "AECB pull and its carry are both before the window."),
    ("none", {}, {}, 0, "No salary from either source."),
]
STATE_EXAMPLES = [  # state, internal, pulls, CASA, payment, distress, active, why
    ("high", {-1: 5000, 0: 5000}, {}, {-1: 4000, 0: 4000}, 0, False, True,
     "Salary and balance both confirmed."),
    ("moderate", {}, {-2: 3000}, {}, 0, False, False, "AECB salary, nothing with us."),
    ("moderate", {}, {}, {}, 1500, False, False, "No salary seen, but paying an external card."),
    ("moderate", {-1: 5000, 0: 5000}, {}, {-1: 4000, 0: 4000}, 0, True, True,
     "Everything in place, but a payment just failed."),
    ("low", {}, {0: 3000}, {}, 0, False, False, "Some reported income, nothing else."),
    ("low", {}, {}, {0: 400}, 0, False, True, "Uses the account, but money does not stay."),
    ("low", {-1: 5000, 0: 5000}, {}, {}, 0, True, True, "Stable income, but a cheque bounced."),
    ("low", {}, {}, {}, 0, True, False, "A bureau bounce is all we see."),
    ("unknown", {}, {}, {}, 0, False, False, "No CASA with us, or a dormant one: we cannot see their money."),
]
MONTHS = len(OFFSETS)


def examples(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Examples"), [12] + [10] * MONTHS + [62])
    why = MONTHS + 2
    s.title("Examples (61–180 DPD, 3-month window)",
            "One customer per row, oldest month on the left; the blue columns are the window. "
            "Threshold AED 3,000 unless the row says otherwise, so Stable needs a total of 6,000.")
    s.section("Income", gap=0)
    s.text(1, "Cells", bold=True, color=MUTED, border=False, align=MID)
    for col, span, tone, text in ((2, 2, TONE["good"], "5,000  internal salary"),
                                  (4, 2, PULL, "A 3,000  AECB pull"),
                                  (6, 1, CARRIED, "→ carried"), (7, 1, CLOSED, "× closed")):
        s.text(col, text, span=span, color=tone[1], fill=tone[0], align=CENTER)
    s.ws.row_dimensions[s.r].height = 28
    s.r += 1
    s.header(["Income"] + [("Now" if k == 0 else str(k)) for k in OFFSETS] + ["Why"])
    for k in OFFSETS:
        if in_window(k):
            s.ws.cell(row=s.r - 1, column=MONTHS + 1 + k).fill = _fill(WINDOW_HEAD)
    for level, internal, pulls, anchor, text in INCOME_EXAMPLES:
        got = income_level(internal, pulls, anchor)
        if got != level:
            raise SystemExit(f"example '{text}' gives {got}, expected {level}")
        chip(s, 1, LEVEL_TONE[level], LABEL[level])
        for k in OFFSETS:
            col, value, tone = MONTHS + 1 + k, None, None
            if k in pulls:
                value, tone = (f"A {pulls[k]:,}", PULL) if pulls[k] else ("×", CLOSED)
            elif pulls.get(k - 1):
                value, tone = f"→ {pulls[k - 1]:,}", CARRIED
            if internal.get(k, 0) >= (pulls.get(k) or pulls.get(k - 1) or 0) and k in internal:
                value, tone = f"{internal[k]:,}", TONE["good"]
            fill = tone[0] if tone else (WINDOW_FILL if in_window(k) else None)
            s.text(col, value, bold=True, color=tone[1] if tone else "000000", fill=fill, align=CENTER)
        s.text(why, text, align=MID)
        _fit(s.ws, s.r, [(text, s.widths[-1])])
        s.r += 1
    s.section("State")
    s.header(["State", "Income", "Liquidity", "Distress", "Customer money movement", "Why"],
             [1, 2, 1, 1, 2, 1], height=30)
    for state, internal, pulls, casa, payment, distress, active, text in STATE_EXAMPLES:
        inc, liq = income_level(internal, pulls), liquidity_level(casa, payment)
        got = ability(inc, liq, distress, active)
        if got != state:
            raise SystemExit(f"example '{text}' gives {got}, expected {state}")
        chip(s, 1, state)
        chip(s, 2, LEVEL_TONE[inc], LABEL[inc], span=2)
        chip(s, 4, LEVEL_TONE[liq], LABEL[liq])
        s.text(5, "Yes" if distress else "No", align=CENTER)
        s.text(6, "Yes" if active else "No", span=2, align=CENTER)
        s.text(why, text, align=MID)
        _fit(s.ws, s.r, [(text, s.widths[-1])])
        s.r += 1
    s.r += 1
    s.note("At 180+ DPD the window is 6 months and Stable needs 3 × the threshold; the rules are the same.")
    s.ws.freeze_panes = "B4"


def _accounts(s: Sheet, totals: tuple) -> int:
    """An 'Accounts' row, the denominator of the sheet's shares; returns its row."""
    s.text(1, "Accounts", bold=True)
    for j, n in enumerate(totals):
        s.text(2 + 2 * j, n, color="0000FF", fill=INPUT_FILL).number_format = "#,##0"
        s.text(3 + 2 * j, None)
    row = s.r
    s.r += 1
    return row


def _rows(s: Sheet, rows: list, base: int) -> None:
    for label, tone, *counts in rows:
        chip(s, 1, tone, label)
        for j, n in enumerate(counts):
            L = get_column_letter(2 + 2 * j)
            fill = INPUT_FILL if n is not None else None
            s.text(2 + 2 * j, n, color="0000FF", fill=fill).number_format = "#,##0"
            share = f'=IF(OR({L}{s.r}="",N({L}${base})=0),"",{L}{s.r}/{L}${base})'
            s.text(3 + 2 * j, share, color=MUTED).number_format = "0.0%"
        _fit(s.ws, s.r, [(label, s.widths[0])], floor=18)
        s.r += 1
    for j in range(len(BOOKS)):
        col = get_column_letter(3 + 2 * j)
        s.ws.conditional_formatting.add(
            f"{col}{s.r - len(rows)}:{col}{s.r - 1}",
            DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=BAR),
        )


def _blocks(wb: Workbook, name: str, lead: str, blocks: list) -> Sheet:
    s = Sheet(wb.create_sheet(name), [58] + [11, 8] * len(BOOKS))
    s.title(name, lead)
    base = None
    for i, (title, rows) in enumerate(blocks):
        s.section(title, gap=0 if i == 0 else 1)
        s.header([""] + [x for b in BOOKS for x in (b, "share")], height=30)
        if base is None:
            base = _accounts(s, TOTALS)
        _rows(s, rows, base)
    s.ws.freeze_panes = "B4"
    return s


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [28] + [11, 8] * 5)
    s.title("Results", f"Accounts per state, {RESULTS_DATE}.")
    heads = ["Credit cards", "Retail loans"] + RL_PRODUCTS
    for i, (dpd, row, rows) in enumerate(STATE_BLOCKS):
        s.section(f"Ability state, {dpd}", gap=0 if i == 0 else 1)
        s.text(1, "State", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, h in enumerate(heads):
            s.text(2 + 2 * j, h, span=2, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.ws.row_dimensions[s.r].height = 30
        s.r += 1
        first, total = s.r, s.r + len(rows)
        if first != row:
            raise SystemExit(f"Overview reads Results row {row} for {dpd}, the states start at {first}")
        for st, *counts in rows:
            chip(s, 1, st)
            for j, n in enumerate(counts):
                L = get_column_letter(2 + 2 * j)
                s.text(2 + 2 * j, n, color="0000FF", fill=INPUT_FILL).number_format = "#,##0"
                share = f'=IF(OR({L}{s.r}="",N({L}${total})=0),"",{L}{s.r}/{L}${total})'
                s.text(3 + 2 * j, share, color=MUTED).number_format = "0.0%"
            s.r += 1
        s.text(1, "Total", bold=True)
        for j, n in enumerate(STATE_TOTALS[dpd]):
            counts = [r[1 + j] for r in rows]
            if None not in counts and sum(counts) != n:
                raise SystemExit(f"{dpd} {heads[j]}: states add to {sum(counts)}, total {n}")
            s.text(2 + 2 * j, n, bold=True, color="0000FF", fill=INPUT_FILL).number_format = "#,##0"
            s.text(3 + 2 * j, None)
        s.r += 1
    s.section("Reading the results")
    for n in NOTES:
        s.text(1, n, span=s.last, border=False)
        _fit(s.ws, s.r, [(n, s.width(1, s.last))], floor=18)
        s.r += 1
    s.r += 1
    s.note("Which rule gave each state: 'Results detail'. Coverage of salary, CASA and bureau: "
           "'Results summaries'. How the states pay and cure: 'Validation'.")
    s.ws.freeze_panes = "B4"


def weaknesses(wb: Workbook) -> None:
    s = _blocks(wb, "Weaknesses", f"Why High is rare and the state is mostly a bureau-salary signal, "
                                  f"{RESULTS_DATE}. Shares are of all accounts of the book.",
                WEAK_BLOCKS)
    for title, rows in (("Findings", WEAK_FINDINGS), ("Directions being explored", WEAK_DIRECTIONS)):
        s.section(title)
        s.header(["", "Finding" if rows is WEAK_FINDINGS else "Idea"], [1, s.last - 1])
        for k, v in rows:
            s.text(1, k, bold=True, align=MID)
            s.text(2, v, span=s.last - 1, align=MID)
            _fit(s.ws, s.r, [(v, s.width(2, s.last))])
            s.r += 1
    s.r += 1
    s.note("Bundle 12 counts unless a row says bundle 14; income and liquidity did not change in "
           "bundle 14. Payment and cure rates: 'Validation'.")


def detail(wb: Workbook) -> None:
    s = _blocks(wb, "Results detail", f"Which rules fire and why, {RESULTS_DATE}. Shares are of all "
                                      "accounts of the book.", DETAIL)
    s.r += 1
    s.note("The AECB Stable and Weak rows include accounts with internal salary too; on loans AECB "
           "also includes the salary on the loan's own bureau pull. A card payment can sit beside a "
           "sufficient balance, so the arms overlap in the second Adequate row. Blank = does not apply.")


def summaries(wb: Workbook) -> None:
    s = _blocks(wb, "Results summaries", f"What we can see of the customer, {RESULTS_DATE}. Shares are "
                                         "of all accounts of the book. At 180+ the window is 6 months.",
                SUMMARIES)
    x = Sheet(wb.create_sheet("Salary sources"), [24] + [13] * len(CROSS_COLS))
    x.title("Salary sources", f"Accounts by the latest internal salary and the latest AECB salary "
                              f"alert, {RESULTS_DATE}.")
    for i, (name, rows) in enumerate(CROSS.items()):
        x.section(name, gap=0 if i == 0 else 1)
        x.header([""] + CROSS_COLS, height=30)
        for label, *counts in rows:
            x.text(1, label, bold=True, align=MID)
            for j, n in enumerate(counts, 2):
                fill = INPUT_FILL if n is not None else None
                x.text(j, n, color="0000FF", fill=fill).number_format = "#,##0"
            x.r += 1
    x.r += 1
    x.note("'Never' = no AECB salary alert of AED 1,000 or more, with or without alert rows. "
           "Before the 1-month carry. At 180+ the window covers months 1–6, so there is no 4–6 row "
           "or column.")
    s.r += 1
    s.note("Internal salary against AECB salary: 'Salary sources'.")


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [34, 16, 16, 16, 16])
    s.title("Validation", f"Do the states separate customers who pay? 61–180 DPD, {VALIDATION_DATE}, "
                          "DPD band controlled. Measured on the rules before the level check, which "
                          "moved 3% of card and 1% of loan accounts.")
    for i, (book, rows) in enumerate(VALIDATION):
        s.section(book, gap=0 if i == 0 else 1)
        s.header(["State", "Cure in 3 months", "Roll in 3 months", "Any payment in 3 months"],
                 height=30)
        for st, *shares in rows:
            chip(s, 1, st)
            for j, v in enumerate(shares, 2):
                s.text(j, v / 100, color="0000FF", fill=INPUT_FILL, align=CENTER).number_format = "0.0%"
            s.r += 1
    s.section("Findings")
    s.header(["", "Finding"], [1, 4])
    for k, v in VALIDATION_FINDINGS:
        s.text(1, k, bold=True, align=MID)
        s.text(2, v, span=4, align=MID)
        _fit(s.ws, s.r, [(v, s.width(2, 5))])
        s.r += 1
    s.section("The 25% rule: kept for now, to review with GRR")
    s.header(["Accounts failing only the 25% rule", "Rows", "Cure vs Stable", "Roll vs Stable",
              "Payment vs Stable"], height=30)
    for label, *cells in RULE_25:
        s.text(1, label, bold=True, align=MID)
        for j, v in enumerate(cells, 2):
            s.text(j, v, align=CENTER)
        _fit(s.ws, s.r, [(label, s.widths[0])])
        s.r += 1
    for k, v in RULE_25_OPTIONS:
        s.text(1, k, bold=True, align=MID)
        s.text(2, v, span=4, align=MID)
        _fit(s.ws, s.r, [(v, s.width(2, 5))])
        s.r += 1
    s.r += 1
    s.note("Association, not cause. Cure = back to current; roll = a worse bucket; differences in "
           "percentage points, DPD band controlled, ns = not significant. 180+ is not validated: "
           "few of its accounts pay or cure. Latest-month counts: 'Results detail'.")
    s.ws.freeze_panes = "A4"


def aecb(wb: Workbook) -> None:
    s = _blocks(wb, "AECB coverage", f"How thin AECB data shapes the result, and what frequent pulls "
                                     f"would change, {RESULTS_DATE} (bundle 12). Shares are of all accounts of "
                                     "the book.", AECB_BLOCKS)
    s.section("Today against pulls every 2 months")
    s.header(["", "Today (alerts)", "With pulls every 2 months"], [1, 4, 4])
    for topic, today, frequent in AECB_TODAY_VS_FREQUENT:
        s.text(1, topic, bold=True, align=MID)
        s.text(2, today, span=4, align=MID)
        s.text(6, frequent, span=4, align=MID)
        _fit(s.ws, s.r, [(today, s.width(2, 5)), (frequent, s.width(6, 9))])
        s.r += 1
    s.r += 1
    s.note("The what-if keeps every rule and only lets the last AECB salary count for 6 or 12 months "
           "instead of 1 (never backwards, a closure stops it): a ceiling for customers who already "
           "had a salary alert. Card results: workplace_mirror/bundle_helpers/a1_final/"
           "aecb_whatif_results_cc.md. Not run for loans: blank.")


def _chart(s: Sheet, title: str, head: int, months: int) -> None:
    """100% stacked bars of the states by month, beside the table."""
    chart = BarChart()
    chart.type, chart.grouping, chart.overlap, chart.gapWidth = "col", "percentStacked", 100, 40
    chart.title = f"{title}: share of accounts by state"
    chart.height, chart.width = 6.2, 15
    chart.legend.position = "b"
    chart.y_axis.number_format, chart.y_axis.majorUnit = "0%", 0.25
    chart.x_axis.delete = chart.y_axis.delete = False
    for j, st in enumerate(STATES):
        chart.add_data(Reference(s.ws, min_col=3 + j, min_row=head, max_row=head + months),
                       titles_from_data=True)
        chart.series[j].graphicalProperties.solidFill = SERIES[st]
        chart.series[j].graphicalProperties.line.solidFill = "FFFFFF"
    chart.set_categories(Reference(s.ws, min_col=1, min_row=head + 1, max_row=head + months))
    s.ws.add_chart(chart, f"H{head}")


def trend(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results trend"), [12, 12] + [11] * len(STATES))
    s.title("Results trend", "Share of accounts per state by month, Jan–Aug 2026 (month ends), "
                             "bundle 12: before bundle 14, which moved 2–3% of 61–180 accounts.")
    first_rows = []
    for i, (title, months) in enumerate(TREND.items()):
        s.section(title, gap=0 if i == 0 else 4)
        first_rows.append(s.r)
        s.text(1, "Month", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.text(2, "Accounts", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, st in enumerate(STATES):
            chip(s, 3 + j, st).alignment = CENTER
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
        for month, (n, *shares) in months.items():
            s.text(1, f"{month} 2026", bold=True)
            s.text(2, n, color="0000FF", fill=INPUT_FILL).number_format = "#,##0"
            for j, v in enumerate(shares):
                cell = s.text(3 + j, None if v is None else v / 100, color="0000FF", fill=INPUT_FILL)
                cell.number_format = "0.0%"
            s.r += 1
    s.r += 1
    for title, head in zip(TREND, first_rows):
        _chart(s, title, head, len(TREND[title]))
    s.note("At 61–180 both books grow from April–May while Moderate falls and Unknown rises from June; "
           "the August alert gaps may add to it ('Results'). 180+ is flat. High is too small to read "
           "on the charts.")
    s.ws.freeze_panes = "A4"


def build(out: pathlib.Path) -> pathlib.Path:
    wb = Workbook()
    overview(wb)
    logic(wb)
    thresholds(wb)
    examples(wb)
    results(wb)
    weaknesses(wb)
    detail(wb)
    summaries(wb)
    trend(wb)
    validation(wb)
    aecb(wb)
    order = ["Overview", "Logic", "Thresholds", "Examples", "Results", "Weaknesses", "Results detail",
             "Results summaries", "Salary sources", "AECB coverage", "Results trend", "Validation"]
    wb._sheets = [wb[name] for name in order]  # pylint: disable=protected-access
    wb.calculation.fullCalcOnLoad = True
    for ws in wb:
        ws.sheet_properties.tabColor = NAVY if ws.title in order[:4] else "2E75B6"
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(pathlib.Path(__file__).with_name("a1_ability_reference.xlsx")))
    print(build(pathlib.Path(ap.parse_args().out)))


if __name__ == "__main__":
    main()
