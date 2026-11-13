"""Build the A3 payment credibility model document (business-facing).

    python build_a3_workbook.py [--out a3_credibility_reference.xlsx]

Starts from the DE's "A3 framework" sheet (A3_credibility_shared_Nov3.xlsx, transcribed in
``workplace_mirror/bundle_helpers/a3_final/a3_framework_sheet.md``) and applies the decisions in
``workplace_mirror/specs/A3_credibility_spec.md``. The map is generated from the reference rules
below; the build FAILS if a cell is claimed by more or fewer than one state or a check cell moves.

Colours: green favourable, red adverse, grey unknown, amber = proposed / open; navy is structure.
"""

from __future__ import annotations

import argparse
import math
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# --- rules (reference implementation) -------------------------------------------------------
HIGH_FROM, MODERATE_FROM = 4, 2
POINTS_A = {"Kept": 2, "Partly kept": 1, "Thin": 0, "Broken": -1}
POINTS_B = {"Regular": 2, "Some": 1, "None": 0}
POINTS_C = {"Clean": 1, "Not clean": 0, "No record": 0}
DE_MODERATE_FROM = 1


def state(a: str, b: str, c: str, refusal: bool) -> str:
    """The ladder: summed points, refusal the only strong negative. A row reaches this map only
    when a delinquency episode is observed; Unknown is the row with no episode (not in the map)."""
    pts = POINTS_A[a] + POINTS_B[b] + POINTS_C[c]
    if pts >= HIGH_FROM:
        return "Moderate" if refusal else "High"
    if pts >= MODERATE_FROM and not refusal:
        return "Moderate"
    return "Low"


def state_de(a: str, b: str, c: str, negative: bool) -> str:
    """The DE sheet: Broken = 0 points and a strong negative, Moderate from 1, Unknown when no
    dimension has evidence."""
    negative = negative or a == "Broken"
    if (a, b, c, negative) == ("Thin", "None", "No record", False):
        return "Unknown"
    pts = {**POINTS_A, "Broken": 0}[a] + POINTS_B[b] + POINTS_C[c]
    if pts >= HIGH_FROM:
        return "Moderate" if negative else "High"
    return "Moderate" if pts >= DE_MODERATE_FROM and not negative else "Low"


def _claims(a: str, b: str, c: str, refusal: bool) -> int:
    """Number of state rules that claim the cell (the MECE proof: must be 1)."""
    pts = POINTS_A[a] + POINTS_B[b] + POINTS_C[c]
    rules = [
        pts >= HIGH_FROM and not refusal,
        (MODERATE_FROM <= pts < HIGH_FROM and not refusal) or (pts >= HIGH_FROM and refusal),
        pts < MODERATE_FROM or (pts < HIGH_FROM and refusal),
    ]
    return sum(rules)


# --- design system --------------------------------------------------------------------------
FONT = "Arial"
NAVY, INK, MUTED, RULE = "1F3864", "262626", "7F7F7F", "D9D9D9"
TONE = {
    "High": ("E2EFDA", "375623"),
    "Moderate": ("FFF2CC", "7F6000"),
    "Low": ("FBE2D5", "9C2B12"),
    "Unknown": ("EDEDED", "595959"),
}
AMBER_FILL, AMBER_INK = "FCE4D6", "843C0C"
HAIR = Side(style="thin", color=RULE)
BOX = Border(left=HAIR, right=HAIR, top=HAIR, bottom=HAIR)
TOP = Alignment(wrap_text=True, vertical="top")
MID = Alignment(wrap_text=True, vertical="center")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _font(**kw) -> Font:
    return Font(name=FONT, size=kw.pop("size", 10), color=kw.pop("color", INK), **kw)


def _fill(hex_: str) -> PatternFill:
    return PatternFill("solid", start_color=hex_, end_color=hex_)


class Sheet:
    """A worksheet with a write cursor (``r``) and the document's styles."""

    def __init__(self, ws: Worksheet, widths: list[float]):
        self.ws, self.widths, self.r = ws, widths, 1
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    @property
    def last(self) -> int:
        return len(self.widths)

    def width(self, c1: int, c2: int) -> float:
        return sum(self.widths[c1 - 1 : c2])

    def fit(self, texts: list[tuple[str, float]], floor: float = 18) -> None:
        lines = (
            max(
                sum(math.ceil(max(len(p), 1) / max(w * 1.05, 1)) for p in str(t or "").split("\n"))
                for t, w in texts
            )
            or 1
        )
        self.ws.row_dimensions[self.r].height = max(floor, 13.5 * lines + 5)

    def merge(self, c1: int, c2: int) -> None:
        if c2 > c1:
            self.ws.merge_cells(start_row=self.r, start_column=c1, end_row=self.r, end_column=c2)

    def title(self, text: str, lead: str) -> None:
        self.ws["A1"] = text
        self.ws["A1"].font = _font(size=16, bold=True, color=NAVY)
        self.r = 2
        self.text(1, lead, span=self.last, color=MUTED, border=False)
        self.ws["A2"].font = _font(color=MUTED, italic=True)
        self.fit([(lead, self.width(1, self.last))])
        self.r = 4

    def section(self, text: str, gap: int = 1) -> None:
        self.r += gap
        self.ws.cell(row=self.r, column=1, value=text).font = _font(size=11, bold=True, color=NAVY)
        for col in range(1, self.last + 1):
            self.ws.cell(row=self.r, column=col).border = Border(
                bottom=Side(style="medium", color=NAVY)
            )
        self.ws.row_dimensions[self.r].height = 20
        self.r += 1

    def header(self, labels: list[str], spans: list[int] | None = None) -> None:
        col = 1
        for lab, span in zip(labels, spans or [1] * len(labels)):
            self.text(col, lab, span=span, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
            col += span
        self.ws.row_dimensions[self.r].height = 30 if any("\n" in x for x in labels) else 20
        self.r += 1

    def text(
        self,
        col: int,
        value,
        *,
        span: int = 1,
        bold: bool = False,
        color: str = INK,
        fill: str | None = None,
        align: Alignment = TOP,
        border: bool = True,
    ):
        c = self.ws.cell(row=self.r, column=col, value=value)
        c.font = _font(bold=bold, color=color)
        c.alignment = align
        for k in range(col, col + span):
            cell = self.ws.cell(row=self.r, column=k)
            if fill:
                cell.fill = _fill(fill)
            if border:
                cell.border = BOX
        self.merge(col, col + span - 1)
        return c

    def chip(self, col: int, st: str, span: int = 1, mark: str = ""):
        fill, ink = TONE[st]
        return self.text(col, st + mark, span=span, bold=True, color=ink, fill=fill, align=CENTER)

    def row(
        self, values: list, spans: list[int], *, bold_first: bool = True, amber: bool = False
    ) -> None:
        col, texts = 1, []
        for i, (v, span) in enumerate(zip(values, spans)):
            self.text(
                col,
                v,
                span=span,
                bold=bold_first and i == 0,
                fill=AMBER_FILL if amber else None,
                color=AMBER_INK if amber and i == 0 else INK,
            )
            texts.append((v, self.width(col, col + span - 1)))
            col += span
        self.fit(texts)
        self.r += 1

    def note(self, text: str) -> None:
        self.text(1, text, span=self.last, color=MUTED, border=False)
        self.ws.cell(row=self.r, column=1).font = _font(color=MUTED, italic=True)
        self.fit([(text, self.width(1, self.last))], floor=16)
        self.r += 1


# --- framework ------------------------------------------------------------------------------
HEAD = [
    (
        "Scope",
        "Accounts at 60+ DPD under active collection, credit cards and retail loans. "
        "Separate models for 61–180 DPD and 180+ DPD; the model decides which rules apply.",
    ),
    (
        "Question",
        "How far can we believe this customer will pay this debt? Two kinds of evidence: "
        "trust (do they do what they say: promises kept, stated refusal) and flow (is money "
        "coming in now, and did it before delinquency).",
    ),
    (
        "Not A3",
        "Capacity to pay (ability), whether we can find and reach the customer "
        "(locatability), the DPD path itself (deterioration). A weak flow can mean "
        "inability, not unwillingness: read credibility together with ability.",
    ),
    (
        "Time frame",
        "Promises: the last 12 months, earlier delinquency episodes included (trust is a "
        "track record). Payments: the most recent months (recency). Record before "
        "delinquency: the 12 months before the current episode started (a cure back to "
        "current ends an episode). A refusal is read inside the current episode.",
    ),
    (
        "This debt",
        "Promises, contacts and payments are those of the scored account only (ability looks "
        "across all the customer's accounts; credibility is about this debt).",
    ),
    (
        "How to read",
        "Score the three dimensions (block 2) and add the points; Broken promises count "
        "against. A refusal (block 3) takes one level off. Read the state in block 1.",
    ),
    (
        "Basis",
        "Production month ends, credit cards and retail loans, 61–180 and 180+ DPD. State mix: "
        "January–August 2026 ('Results'). Outcomes: back-tests on the month ends of January–May "
        "2026 with the next 3 months ('Validation', 'Back-tests').",
    ),
    (
        "Status",
        "Amber rows are still under review: the promise deadline and the weight of Broken "
        "promises ('Changes', Still open).",
    ),
]

STATES = [
    ("High", "Total of 4 or more, and no refusal.", "Keeps promises and money is coming in."),
    (
        "Moderate",
        "Total of 2 or 3, and no refusal. Or 4 or more with a refusal.",
        "Some evidence to rely on, not yet consistent. Or a strong record with a fresh refusal.",
    ),
    (
        "Low",
        "Total below 2. Or below 4 with a refusal.",
        "Little or nothing positive on record, or what there is has been outweighed by broken "
        "promises or a refusal. Includes delinquent accounts with no evidence at all (mostly "
        "accounts that defaulted early, with no history to judge).",
    ),
    (
        "Unknown",
        "No delinquency episode can be observed for the account.",
        "Nothing to judge the account on. Rare: almost every scored account has an episode.",
    ),
]

DIMENSIONS = [
    (
        "A. Promises kept. Does the customer do what they commit to?",
        [
            (
                "Promises",
                "",
                "Every promise to pay and settlement plan in the collections system, plus every "
                "promise a collector recorded in a follow-up note (promise to pay, scheduled, "
                "digital collect, pay at salary) that no plan already covers. Notes less than "
                "8 days apart are one promise. Last 12 months.",
                False,
            ),
            (
                "Kept or broken",
                "",
                "A promise is kept when the customer's payments after the promise day reach "
                "the due of that cycle (at least 100 AED) by the deadline; 100 AED or more but "
                "less is partial (not kept). Deadline today: cards at 61–180 the next statement; "
                "loans, and all accounts at 180+, the end of the month of the promise. A 30-day "
                "window ranks customers better and is under review ('Back-tests').",
                True,
            ),
            ("Kept", "2", "Not Broken, at least 2 concluded, and 80% or more of them kept.", False),
            ("Partly kept", "1", "Not Broken, not Kept, and at least one kept.", False),
            (
                "Thin",
                "0",
                "No promise concluded, or one concluded and broken. No evidence either way.",
                False,
            ),
            (
                "Broken",
                "−1",
                "The last 3 concluded were all broken, or at least 2 concluded and fewer than "
                "40% kept. Checked first. Counts against the customer today. Under review: "
                "Broken customers pay more often than Thin ones, and +1 ranks better than −1 "
                "in every book ('Back-tests').",
                True,
            ),
        ],
    ),
    (
        "B. Payments in delinquency. Is money coming in now?",
        [
            (
                "Window",
                "",
                "The last 3 months (61–180 DPD) or 6 months (180+ DPD), inside the current "
                "delinquency. Promised or not.",
                False,
            ),
            (
                "Regular",
                "2",
                "A qualifying payment in 2 or more months of the window (61–180), or 3 or "
                "more (180+). Qualifying: at least one month's due amount and at least "
                "100 AED.",
                False,
            ),
            (
                "Some",
                "1",
                "Not Regular, and a month with at least 100 AED paid in the last 3 months "
                "(61–180) or 12 months (180+).",
                False,
            ),
            (
                "None",
                "0",
                "Nothing of 100 AED or more. This is evidence (nothing paid while delinquent), "
                "not a gap.",
                False,
            ),
        ],
    ),
    (
        "C. Record before delinquency. Did they pay as billed before it started?",
        [
            ("Window", "", "The 12 months before the current delinquency started.", False),
            (
                "Clean",
                "1",
                "Paid as billed in 80% or more of the months with an amount due. As billed: at "
                "least the amount due, before the next statement (loans: the month's "
                "instalment). Paying the minimum counts.",
                False,
            ),
            ("Not clean", "0", "Below 80%. Partial and missed months both count against.", False),
            (
                "No record",
                "0",
                "Fewer than 3 months with an amount due, or the history does not reach back "
                "to the episode start. No evidence either way.",
                False,
            ),
        ],
    ),
]

NEGATIVES = [
    (
        "Refusal",
        "The latest conversation with the customer in this delinquency ended in a refusal "
        "(refuse to pay, refused to pay, KSA refuse to pay, rewrite not agreed), and no "
        "promise, arrangement or payment of 100 AED or more has followed it.",
        "Takes the state one level down. About 4.4% of accounts at 61–180.",
    ),
]
DIAGNOSTICS = [
    ("Dispute", "The latest conversation was a dispute of the debt. Contesting is not refusing."),
    (
        "No pickup after contact",
        "3 days (61–180) or 6 days (180+) of ringing, no answer or left "
        "message after we had reached the customer earlier, with no dead "
        "line in between.",
    ),
    ("Hung up", "The customer hung up on the latest conversation."),
]

CUTOFFS = [  # (parameter, value, source, amber)
    ("State: High from (total points)", "4", "DE proposal", False),
    ("State: Moderate from (total points)", "2", "Decided from the threshold test", False),
    ("Promises: window", "last 12 months", "Decided (track record)", False),
    ("Promises: concluded needed before a rate counts", "2", "DE proposal", False),
    ("Promises: Kept from (share kept)", "80%", "DE proposal", False),
    ("Promises: Broken below (share kept)", "40%", "DE proposal", False),
    ("Promises: Broken when the last N concluded were all broken", "3", "DE proposal", False),
    (
        "Promises: deadline to pay",
        "cards 61–180: next statement; loans and 180+: end of the promise month",
        "GRR; 30 days under review",
        True,
    ),
    ("Promises: points for Broken", "−1", "Decided; +1 tested better, with GRR", True),
    ("Payments in delinquency: window in months (61–180 / 180+)", "3 / 6", "DE proposal", False),
    (
        "Payments in delinquency: qualifying payment",
        "100% of one month's due, min 100 AED",
        "DE proposal + 100 AED minimum in every band",
        False,
    ),
    (
        "Payments in delinquency: Regular from (qualifying months, 61–180 / 180+)",
        "2 / 3",
        "DE proposal",
        False,
    ),
    (
        "Payments in delinquency: Some window in months (61–180 / 180+)",
        "3 / 12",
        "DE proposal",
        False,
    ),
    ("Record before: window in months before the delinquency", "12", "Redesign ask", False),
    ("Record before: months with an amount due needed", "3", "DE proposal", False),
    ("Record before: Clean from (share of months paid as billed)", "80%", "DE proposal", False),
    ("Record before: paid as billed by", "the next statement", "Decided", False),
    ("Diagnostics: failed call days (61–180 / 180+)", "3 / 6", "As locatability", False),
]


def framework(wb: Workbook) -> None:
    s = Sheet(wb.active, [30, 9, 62, 44])
    s.ws.title = "A3 framework"
    s.title(
        "A3 Payment Credibility: framework",
        "Accounts at 60+ DPD under active collection, credit card and retail loan. Three scored "
        "dimensions and one strong negative. Updated 13 Nov 2026 from the DE's framework with "
        "every decision taken since (what changed: 'Changes').",
    )
    for k, v in HEAD:
        s.text(1, k, bold=True, color=NAVY, border=False)
        s.text(2, v, span=3, border=False, fill=AMBER_FILL if k == "Status" else None)
        s.fit([(v, s.width(2, 4))])
        s.r += 1

    s.section("1. State: add the points, take one level off for a refusal")
    s.header(["State", "Rule (total points)", "In plain words"], [1, 2, 1])
    for st, rule, plain in STATES:
        s.chip(1, st)
        s.text(2, rule, span=2, align=MID)
        s.text(4, plain, align=MID)
        s.fit([(rule, s.width(2, 3)), (plain, s.widths[3])])
        s.r += 1

    s.section("2. Dimensions: three questions, scored separately")
    s.header(["Level", "Points", "Rule", ""], [1, 1, 2])
    for head, levels in DIMENSIONS:
        s.text(1, head, span=4, bold=True, color=NAVY, fill="EEF3FA")
        s.r += 1
        for lev, pts, rule, amber in levels:
            fill = AMBER_FILL if amber else None
            s.text(1, lev, bold=True, fill=fill, color=AMBER_INK if amber else INK)
            s.text(2, pts, fill=fill, align=CENTER, bold=True)
            s.text(3, rule, span=2, fill=fill)
            s.fit([(rule, s.width(3, 4))])
            s.r += 1

    s.section("3. Strong negative: takes the state down one level")
    s.header(["Strong negative", "Rule", "Effect"], [1, 2, 1])
    for name, rule, eff in NEGATIVES:
        s.row([name, rule, eff], [1, 2, 1])
    s.note(
        "Broken promises are not a strong negative: they count −1 in the points. 'No "
        "response' is removed: it repeated locatability's Non-Reachable."
    )
    s.r += 1
    s.text(
        1,
        "Diagnostic columns (in the output, not in the state)",
        span=4,
        bold=True,
        color=NAVY,
        fill="EEF3FA",
    )
    s.r += 1
    for name, rule in DIAGNOSTICS:
        s.row([name, rule], [1, 3])

    s.section("4. Cut-offs and windows")
    s.header(["Parameter", "Value", "Source"], [2, 1, 1])
    for name, val, src, amber in CUTOFFS:
        s.row([name, val, src], [2, 1, 1], amber=amber)
    s.note("Every combination of levels and the state it gets: 'Map'.")
    s.ws.freeze_panes = "A4"


# --- map ------------------------------------------------------------------------------------
def map_sheet(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Map"), [14, 12, 11] + [13] * 6)
    s.title(
        "Map: every combination of levels, and the one state it gets",
        "72 combinations for an account with a delinquency episode, each claimed by exactly one "
        "state rule (checked when the workbook is built). * = a different state from the DE's "
        "map. Unknown (no episode) is outside the map.",
    )
    s.header(
        [
            "A. Promises",
            "B. Payments",
            "Points\nA + B",
            "No refusal\nClean (1)",
            "No refusal\nNot clean (0)",
            "No refusal\nNo record (0)",
            "Refusal\nClean (1)",
            "Refusal\nNot clean (0)",
            "Refusal\nNo record (0)",
        ]
    )
    changed = 0
    for a in POINTS_A:
        for b in POINTS_B:
            amber = a == "Broken"
            s.text(1, a, bold=True, fill=AMBER_FILL if amber else None, align=MID)
            s.text(2, b, align=MID)
            s.text(3, POINTS_A[a] + POINTS_B[b], align=CENTER)
            col = 4
            for refusal in (False, True):
                for c in POINTS_C:
                    assert _claims(a, b, c, refusal) == 1, (a, b, c, refusal)
                    new, old = state(a, b, c, refusal), state_de(a, b, c, refusal)
                    changed += new != old
                    s.chip(col, new, mark=" *" if new != old else "")
                    col += 1
            s.ws.row_dimensions[s.r].height = 20
            s.r += 1
    s.r += 1
    s.note(
        f"{changed} of 72 cells differ from the DE's map, for three reasons. Moderate starts at 2 "
        "points, so 1 point alone (some payment, or a clean record only) is Low. Broken counts −1 "
        "instead of forcing Low, so a Broken record with regular payments and a clean record is "
        "Moderate. No evidence in any dimension is Low, not Unknown: the account is delinquent "
        "and has paid nothing."
    )
    s.ws.freeze_panes = "D5"
    # checks: the cells the narrative relies on
    assert state("Broken", "Regular", "Clean", False) == "Moderate"
    assert state("Broken", "Regular", "Not clean", False) == "Low"
    assert state("Thin", "None", "No record", False) == "Low"
    assert state("Thin", "Some", "No record", False) == "Low"
    assert state("Thin", "Regular", "No record", False) == "Moderate"
    assert state("Kept", "Regular", "No record", False) == "High"
    assert state("Kept", "Regular", "No record", True) == "Moderate"


# --- results --------------------------------------------------------------------------------
BOOKS = ["Cards 61–180", "Loans 61–180", "Cards 180+", "Loans 180+"]
# August 2026 month end, the rules in 'A3 framework' (GRR's deadline); counts.
RESULTS = {  # book: (n, High, Moderate, Low)
    "Cards 61–180": (19292, 490, 3750, 15052),
    "Loans 61–180": (3985, 126, 980, 2879),
    "Cards 180+": (318663, 159, 8288, 310216),
    "Loans 180+": (55371, 120, 2289, 52962),
}
# The same month with the earlier deadline (cards: next statement; loans: end of next month).
RESULTS_PREV = {
    "Cards 61–180": (19292, 491, 3748, 15053),
    "Loans 61–180": (3985, 196, 1113, 2676),
    "Cards 180+": (318663, 222, 8616, 309825),
    "Loans 180+": (55371, 171, 2386, 52814),
}
# The same month with 30 days after the promise.
RESULTS_LEN = {
    "Cards 61–180": (19292, 765, 4382, 14145),
    "Loans 61–180": (3985, 197, 1112, 2676),
    "Cards 180+": (318663, 473, 9211, 308979),
    "Loans 180+": (55371, 171, 2386, 52814),
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
TREND = {  # book: (High %, Moderate %, Low %) per month end 2026
    "Cards 61–180": [
        (4.1, 23.1, 72.7),
        (4.2, 22.6, 73.1),
        (4.2, 22.4, 73.4),
        (4.0, 21.9, 74.2),
        (3.8, 21.0, 75.2),
        (3.2, 20.9, 75.9),
        (2.8, 20.3, 76.9),
        (2.5, 19.4, 78.0),
    ],
    "Loans 61–180": [
        (4.6, 28.2, 67.2),
        (4.5, 26.6, 68.9),
        (4.6, 27.2, 68.2),
        (3.9, 27.7, 68.4),
        (3.1, 24.8, 72.1),
        (2.7, 24.5, 72.9),
        (2.7, 23.5, 73.7),
        (3.2, 24.6, 72.2),
    ],
    "Cards 180+": [
        (0.0, 2.5, 97.5),
        (0.0, 2.5, 97.5),
        (0.0, 2.6, 97.4),
        (0.0, 2.6, 97.4),
        (0.0, 2.6, 97.4),
        (0.1, 2.6, 97.4),
        (0.1, 2.6, 97.3),
        (0.0, 2.6, 97.3),
    ],
    "Loans 180+": [
        (0.2, 3.7, 96.1),
        (0.2, 3.7, 96.1),
        (0.2, 3.6, 96.2),
        (0.2, 3.5, 96.3),
        (0.2, 3.7, 96.1),
        (0.2, 4.0, 95.8),
        (0.2, 4.0, 95.8),
        (0.2, 4.1, 95.6),
    ],
}
LEVELS = [  # book, A: Kept / Partly / Thin / Broken, B: Regular / Some / None,
    # C: Clean / Not clean / No record (history too short) / No record (too few months due)
    (
        "Cards 61–180",
        ("2.3%", "13.9%", "70.2%", "13.6%"),
        ("7.5%", "17.6%", "74.9%"),
        ("64.5%", "20.0%", "<0.1%", "15.4%"),
    ),
    (
        "Loans 61–180",
        ("4.8%", "12.0%", "74.5%", "8.6%"),
        ("10.9%", "32.4%", "56.7%"),
        ("44.3%", "44.6%", "0.0%", "11.1%"),
    ),
    (
        "Cards 180+",
        ("0.0%", "0.8%", "97.9%", "1.2%"),
        ("0.7%", "5.2%", "94.1%"),
        ("10.5%", "4.0%", "54.5%", "31.1%"),
    ),
    (
        "Loans 180+",
        ("0.2%", "1.3%", "97.7%", "0.8%"),
        ("1.0%", "7.2%", "91.8%"),
        ("19.1%", "15.4%", "58.1%", "7.4%"),
    ),
]
NEGATIVE_RATES = [  # book, refusal, refusal that lowers the state, dispute, no pickup, hung up
    ("Cards 61–180", "4.4%", "0.8%", "0.4%", "7.0%", "2.3%"),
    ("Loans 61–180", "4.6%", "0.7%", "0.0%", "8.3%", "1.0%"),
    ("Cards 180+", "2.0%", "0.1%", "0.2%", "0.9%", "1.4%"),
    ("Loans 180+", "1.8%", "0.1%", "0.1%", "0.7%", "1.1%"),
]
SPLITS = [  # book, split, value, accounts, High, Moderate, Low (August 2026, row %)
    ("Loans 61–180", "Loan type", "Personal", "1,397", "1.1%", "18.8%", "80.0%"),
    ("Loans 61–180", "Loan type", "Personal Cash", "1,224", "2.5%", "24.5%", "73.0%"),
    ("Loans 61–180", "Loan type", "Auto", "1,364", "5.8%", "30.6%", "63.6%"),
    ("Loans 180+", "Loan type", "Personal", "33,862", "0.1%", "2.2%", "97.7%"),
    ("Loans 180+", "Loan type", "Personal Cash", "10,306", "0.5%", "8.7%", "90.8%"),
    ("Loans 180+", "Loan type", "Auto", "11,203", "0.4%", "5.8%", "93.8%"),
    ("Cards 180+", "Charge-off age", "under 24 months", "61,112", "0.2%", "10.9%", "88.9%"),
    ("Cards 180+", "Charge-off age", "24 months or more", "257,551", "<0.1%", "0.6%", "99.4%"),
    ("Loans 180+", "Charge-off age", "under 24 months", "10,050", "0.6%", "16.4%", "83.0%"),
    ("Loans 180+", "Charge-off age", "24 months or more", "45,321", "0.1%", "1.4%", "98.5%"),
    ("Cards 61–180", "DPD", "61–90", "5,859", "4.8%", "25.4%", "69.8%"),
    ("Cards 61–180", "DPD", "91–120", "5,260", "2.3%", "19.2%", "78.5%"),
    ("Cards 61–180", "DPD", "121–150", "4,401", "1.4%", "16.8%", "81.8%"),
    ("Cards 61–180", "DPD", "151–180", "3,772", "0.7%", "13.7%", "85.7%"),
    ("Loans 61–180", "DPD", "61–90", "1,401", "5.7%", "30.7%", "63.6%"),
    ("Loans 61–180", "DPD", "91–120", "1,106", "2.4%", "26.9%", "70.7%"),
    ("Loans 61–180", "DPD", "121–150", "971", "1.8%", "18.0%", "80.2%"),
    ("Loans 61–180", "DPD", "151–180", "507", "0.6%", "15.2%", "84.2%"),
    ("Loans 180+", "DPD", "181–360", "3,926", "1.8%", "33.0%", "65.2%"),
    ("Loans 180+", "DPD", "361–720", "4,848", "0.4%", "10.2%", "89.4%"),
    ("Loans 180+", "DPD", "720+", "46,597", "0.1%", "1.1%", "98.9%"),
]


def _pct(x: int, n: int) -> str:
    return f"{100 * x / n:.1f}%"


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [22, 16, 16, 16, 16, 16, 16, 16, 16])
    s.title(
        "Results: the state mix",
        "Share of accounts in each state under the rules in 'A3 framework'. Unknown is empty in "
        "every book and month: every account scored has an observed delinquency episode.",
    )
    s.section("1. State mix, August 2026")
    s.header(
        ["Book", "Accounts", "High", "Moderate", "Low", "Unknown", "", "", ""],
        [1, 1, 1, 1, 1, 1, 3],
    )
    for book in BOOKS:
        n, hi, mo, lo = RESULTS[book]
        assert hi + mo + lo == n, book
        s.text(1, book, bold=True)
        s.text(2, f"{n:,}", align=CENTER)
        for col, (st, x) in enumerate(zip(("High", "Moderate", "Low"), (hi, mo, lo)), 3):
            s.text(col, f"{_pct(x, n)} ({x:,})", align=CENTER, fill=TONE[st][0])
        s.text(6, "0%", align=CENTER, fill=TONE["Unknown"][0])
        s.text(7, "", span=3, border=False)
        s.r += 1
    s.note(
        "180+ is almost all Low by construction: little is paid, few promises are made, and the "
        "history before a long charge-off is often too short to judge. The few High and Moderate "
        "accounts at 180+ are the positive signal the strategy looks for."
    )

    s.section("2. Month by month, 2026 (High / Moderate / Low)")
    s.header(["Book"] + MONTHS)
    for book in BOOKS:
        s.text(1, book, bold=True)
        for col, (hi, mo, lo) in enumerate(TREND[book], 2):
            s.text(col, f"{hi} / {mo} / {lo}", align=CENTER)
        s.r += 1
    s.note(
        "At 61–180 the books grew through the year (cards 14.7k to 19.3k accounts) and the new "
        "accounts are mostly Low, so High and Moderate fall a little. 180+ is flat. Each account "
        "keeps its state from one month to the next 88–90% of the time at 61–180 and 99% at 180+ "
        "('Validation', block 6)."
    )

    s.section("3. Effect of the promise deadline on August 2026")
    s.header(
        ["Book", "Deadline", "High", "Moderate", "Low", "States changed", "", "", ""],
        [1, 1, 1, 1, 1, 1, 3],
    )
    moved = {
        "Cards 61–180": "0.0%",
        "Loans 61–180": "7.2%",
        "Cards 180+": "0.4%",
        "Loans 180+": "0.5%",
    }
    for book in BOOKS:
        n = RESULTS[book][0]
        for label, vals, mv in (
            ("Earlier rule", RESULTS_PREV[book][1:], ""),
            ("Today (GRR)", RESULTS[book][1:], moved[book]),
            ("30 days", RESULTS_LEN[book][1:], ""),
        ):
            s.text(1, book, bold=label == "Earlier rule")
            s.text(2, label)
            for col, x in enumerate(vals, 3):
                s.text(col, _pct(x, n), align=CENTER)
            s.text(6, mv, align=CENTER)
            s.text(7, "", span=3, border=False)
            s.r += 1
    s.note(
        "Earlier rule: cards the next statement, loans the end of the following month. Today "
        "(GRR): loans and all 180+ by the end of the month of the promise. 30 days: 30 days after "
        "the promise (loans: to that month's end). Loans at 61–180 move down under GRR's rule: "
        "about a quarter of loan promises are paid in the following month. 30 days lifts High "
        "and Moderate in every book."
    )

    s.section("4. Dimension levels, August 2026 (share of accounts)")
    s.header(
        ["Book", "A Kept", "A Partly", "A Thin", "A Broken", "B Regular", "B Some", "B None", ""]
    )
    for book, a, b, _ in LEVELS:
        s.row([book, *a, *b, ""], [1] * 9)
    s.header(
        [
            "Book",
            "C Clean",
            "C Not clean",
            "C No record:\nhistory short",
            "C No record:\nfew months due",
            "",
            "",
            "",
            "",
        ]
    )
    for book, _, _, c in LEVELS:
        s.row([book, *c, "", "", "", ""], [1] * 9)
    s.note(
        "Most accounts have no concluded promise in 12 months (Thin) and paid nothing in the "
        "payments window, so the record before delinquency carries most of the evidence at "
        "61–180. At 180+ the record is often out of reach: the history does not go back to the "
        "episode start for more than half of the accounts."
    )

    s.section("5. Refusal and diagnostic columns, August 2026 (share of accounts)")
    s.header(
        [
            "Book",
            "Refusal",
            "Refusal that\nlowers the state",
            "Dispute",
            "No pickup\nafter contact",
            "Hung up",
            "",
            "",
            "",
        ],
        [1, 1, 1, 1, 1, 1, 3],
    )
    for row in NEGATIVE_RATES:
        s.row([*row, ""], [1, 1, 1, 1, 1, 1, 3])
    s.note(
        "Most refusals change nothing: the account is already Low. Dispute is 0 for loans at "
        "61–180 (58 accounts at 180+); the dispute codes for that book are being checked."
    )

    s.section("6. State mix by group, August 2026")
    s.header(
        ["Book", "Split", "Group", "Accounts", "High", "Moderate", "Low", "", ""],
        [1, 1, 1, 1, 1, 1, 1, 2],
    )
    for row in SPLITS:
        s.row([*row, ""], [1, 1, 1, 1, 1, 1, 1, 2])
    s.note(
        "Credibility falls with every DPD bucket and with charge-off age, and Auto loans are the "
        "most credible loan product. Cards 180+ DPD bands follow charge-off age (85% of accounts "
        "are past 720 days), so only the age split is shown."
    )


# --- validation -----------------------------------------------------------------------------
# Back-test: month ends January–May 2026 pooled; outcomes over the next 3 months.
OUTCOMES = [  # book, accounts H/M/L, paid a due H/M/L, any payment H/M/L
    ("Cards 61–180", "3,009 / 16,473 / 54,774", (65.4, 37.6, 10.9), (67.0, 40.1, 12.0)),
    ("Loans 61–180", "508 / 3,353 / 8,651", (69.3, 54.0, 24.3), (74.2, 63.2, 32.7)),
    ("Cards 180+", "656 / 39,190 / 1,504,342", (51.8, 30.7, 1.5), (53.5, 35.4, 2.0)),
    ("Loans 180+", "554 / 9,675 / 256,201", (67.1, 31.6, 1.3), (70.2, 37.5, 1.9)),
]
BY_GROUP = [  # book, split, group, paid a due H / M / L
    ("Cards 61–180", "DPD", "61–90", "64.6 / 42.1 / 18.9"),
    ("Cards 61–180", "DPD", "91–120", "71.3 / 41.8 / 12.0"),
    ("Cards 61–180", "DPD", "121–150", "63.2 / 35.2 / 8.0"),
    ("Cards 61–180", "DPD", "151–180", "50.6 / 18.4 / 2.9"),
    ("Loans 61–180", "Loan type", "Personal", "75.2 / 42.5 / 15.2"),
    ("Loans 61–180", "Loan type", "Personal Cash", "71.0 / 53.5 / 22.3"),
    ("Loans 61–180", "Loan type", "Auto", "65.1 / 62.0 / 42.2"),
    ("Loans 61–180", "DPD", "61–90", "72.2 / 60.0 / 35.2"),
    ("Loans 61–180", "DPD", "91–120", "68.2 / 54.5 / 23.1"),
    ("Loans 61–180", "DPD", "121–150", "62.5 / 44.0 / 15.5"),
    ("Loans 61–180", "DPD", "151–180", "68.2 / 36.1 / 15.0"),
    ("Cards 180+", "Charge-off age", "under 24 months", "50.6 / 21.6 / 4.0"),
    ("Cards 180+", "Charge-off age", "24 months or more", "69.8 / 64.6 / 1.0"),
    ("Loans 180+", "Loan type", "Personal", "75.2 / 38.7 / 0.9"),
    ("Loans 180+", "Loan type", "Personal Cash", "60.6 / 31.7 / 2.8"),
    ("Loans 180+", "Loan type", "Auto", "68.8 / 23.1 / 1.4"),
    ("Loans 180+", "Charge-off age", "under 24 months", "61.4 / 22.7 / 4.4"),
    ("Loans 180+", "Charge-off age", "24 months or more", "76.3 / 53.8 / 0.7"),
]
AUC = [  # book, all, per DPD bucket, points total
    ("Cards 61–180", "0.702", "61–90 0.666 · 91–120 0.712 · 121–150 0.708 · 151–180 0.722", "0.70"),
    ("Loans 61–180", "0.654", "61–90 0.630 · 91–120 0.668 · 121–150 0.664 · 151–180 0.608", "0.70"),
    ("Cards 180+", "0.665", "181–360 0.576 · 361–720 0.684 · 720+ 0.653", "0.82"),
    ("Loans 180+", "0.742", "181–360 0.683 · 361–720 0.709 · 720+ 0.713", "0.86"),
]
POINTS = [  # points total, then paid a due % per book (cards 61–180, loans 61–180, cards 180+,
    # loans 180+), and the state the value lands in
    ("−1", "15.6%", "28.4%", "8.6%", "8.0%", "Low"),
    ("0", "9.8%", "18.4%", "0.7%", "0.5%", "Low"),
    ("1", "11.1%", "28.2%", "9.5%", "4.5%", "Low"),
    ("2", "30.3%", "47.6%", "27.7%", "24.5%", "Moderate"),
    ("3", "50.3%", "66.0%", "42.8%", "54.9%", "Moderate"),
    ("4", "64.5%", "65.2%", "49.5%", "66.6%", "High"),
    ("5", "66.7%", "87.9%", "55.2%", "73.0%", "High"),
]
PROMISE_LEVELS = [  # book, paid a due %: Kept, Partly, Broken, Thin never promised,
    # Thin promised not yet due, Thin one failed
    ("Cards 61–180", "38.4%", "32.9%", "28.5%", "8.2%", "33.3%", "24.0%"),
    ("Loans 61–180", "58.0%", "53.9%", "47.9%", "25.3%", "–", "42.9%"),
    ("Cards 180+", "21.1%", "30.5%", "17.6%", "1.3%", "–", "21.0%"),
    ("Loans 180+", "36.6%", "43.5%", "19.8%", "1.6%", "–", "20.4%"),
]
NO_RECORD = [  # book, share of rows, paid a due %: no evidence / rest of Low / Moderate
    ("Cards 61–180", "12.2%", "3.9%", "12.4%", "35.2%"),
    ("Loans 61–180", "7.0%", "9.2%", "28.1%", "54.2%"),
    ("Cards 180+", "83.0%", "0.5%", "7.6%", "30.6%"),
    ("Loans 180+", "65.1%", "0.2%", "3.9%", "32.5%"),
]
OVERLAP = [  # book, Cramér's V with ability, reachability, location, deterioration
    ("Cards 61–180", "0.11", "0.19", "0.14", "0.41"),
    ("Loans 61–180", "0.06", "0.16", "0.15", "0.36"),
    ("Cards 180+", "0.14", "0.19", "0.17", "0.22"),
    ("Loans 180+", "0.22", "0.24", "0.18", "0.20"),
]
STABILITY = [  # book, unchanged, up, down, High stays, Moderate stays
    ("Cards 61–180", "90.2%", "4.3%", "5.6%", "77.8%", "75.3%"),
    ("Loans 61–180", "88.2%", "5.3%", "6.6%", "72.0%", "75.9%"),
    ("Cards 180+", "99.5%", "0.2%", "0.3%", "78.8%", "89.3%"),
    ("Loans 180+", "99.3%", "0.3%", "0.3%", "81.7%", "91.0%"),
]


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [22, 18, 18, 15, 15, 16, 15, 15])
    s.title(
        "Validation: what each state goes on to do",
        "Back-test on the month ends of January to May 2026 (pooled), today's rules, outcomes "
        "over the following 3 months. Paid a due: payments reach at least one month's due. Any "
        "payment: 100 AED or more.",
    )
    s.section("1. Outcome rates by state")
    s.text(1, "", border=False)
    s.text(2, "", border=False)
    s.text(3, "Paid a due in 3 months", span=3, bold=True, align=CENTER, fill="EEF3FA")
    s.text(6, "Any payment in 3 months", span=3, bold=True, align=CENTER, fill="EEF3FA")
    s.r += 1
    s.header(["Book", "Accounts\nH / M / L", "High", "Moderate", "Low", "High", "Moderate", "Low"])
    for book, n, paid, anyp in OUTCOMES:
        s.text(1, book, bold=True)
        s.text(2, n, align=CENTER)
        for col, (st, x) in enumerate(zip(("High", "Moderate", "Low") * 2, paid + anyp), 3):
            s.text(col, f"{x:.1f}%", align=CENTER, fill=TONE[st][0])
        s.fit([(n, s.widths[1])])
        s.r += 1
    s.note(
        "High pays most in every book, every month and every group below; nowhere does the "
        "order break on payment. Cure and roll are not used at cards 61–180: cards leave billing "
        "at charge-off, so 43% of Low (97% at 151–180 DPD) have no level at month 3. Loans cure "
        "similarly in every state (11–18%), so cure does not separate them either."
    )

    s.section("2. Paid a due by group (High / Moderate / Low)")
    s.header(["Book", "Split", "Group", "Paid a due", "", "", "", ""], [1, 1, 1, 2, 3])
    for row in BY_GROUP:
        s.row([*row, ""], [1, 1, 1, 2, 3])
    s.note(
        "The order holds inside every DPD bucket, loan type and charge-off age. Auto loans in Low "
        "still pay 42%: Low there is not a group that does not pay. At 180+ Moderate pays more the "
        "longer ago the charge-off: these are the customers who keep paying for years."
    )

    s.section("3. Ranking power (AUC on paid a due; 0.5 = chance)")
    s.header(
        ["Book", "State, all", "State by DPD bucket", "", "", "Points total", "", ""],
        [1, 1, 4, 1, 1],
    )
    for book, allv, bucket, pts in AUC:
        s.row([book, allv, bucket, pts, ""], [1, 1, 4, 1, 1])
    s.note(
        "The state ranks customers inside every DPD bucket, not only across buckets. The points "
        "total ranks better than the three states, most of all at 180+, where 96–97% of accounts "
        "sit in Low (points-total AUC from the March–May back-test)."
    )

    s.section("4. Points total: paid a due in 3 months")
    s.header(
        [
            "Points",
            "Cards 61–180",
            "Loans 61–180",
            "Cards 180+",
            "Loans 180+",
            "State (no refusal)",
            "",
            "",
        ],
        [1, 1, 1, 1, 1, 1, 2],
    )
    for row in POINTS:
        s.row([*row, ""], [1, 1, 1, 1, 1, 1, 2])
    s.note(
        "The step comes between 1 and 2 points in every book, which is where Moderate starts. "
        "At 180+ High (4 or more) adds little over 3 points and holds very few accounts. −1 point "
        "(Broken promises) pays more than 0 or 1 in every book: see block 5."
    )

    s.section("5. Promises: paid a due by level (March–May 2026)")
    s.header(
        [
            "Book",
            "Kept",
            "Partly kept",
            "Broken",
            "Thin: never\npromised",
            "Thin: promised,\nnot yet due",
            "Thin: one\nfailed",
            "",
        ]
    )
    for row in PROMISE_LEVELS:
        s.row([*row, ""], [1] * 8)
    s.note(
        "Customers who never promised pay least (1–25%); any promise, even a broken one, goes "
        "with paying more. The gap stays inside reachable and contacted accounts, so it is not "
        "only reachability. A broken record pays like a single failed promise. Scoring Broken +1 "
        "instead of −1 ranks better in every book, under both deadlines and in every month "
        "(cards 61–180 AUC +0.045, loans +0.030, 180+ +0.02 to +0.03): see 'Back-tests'. With "
        "today's month-end deadline no loan or 180+ promise is still pending."
    )

    s.section("6. Accounts with no evidence at all (now Low)")
    s.header(
        [
            "Book",
            "Share of rows",
            "Paid a due:\nno evidence",
            "Rest of Low",
            "Moderate",
            "",
            "",
            "",
        ],
        [1, 1, 1, 1, 1, 3],
    )
    for row in NO_RECORD:
        s.row([*row, ""], [1, 1, 1, 1, 1, 3])
    s.note(
        "They pay less than the rest of Low in every book, so Low is the right place for them. "
        "At 61–180 most are young accounts (cards: 71% under 6 months on book: early payment "
        "default) plus old cards with no bill; at 180+ mostly accounts charged off long ago."
    )

    s.section("7. Stability and overlap with the other axes")
    s.header(
        ["Book", "Same state\nnext month", "Up", "Down", "High stays", "Moderate\nstays", "", ""],
        [1, 1, 1, 1, 1, 1, 2],
    )
    for row in STABILITY:
        s.row([*row, ""], [1, 1, 1, 1, 1, 1, 2])
    s.header(
        ["Book", "Ability", "Reachability", "Location", "Deterioration", "", "", ""],
        [1, 1, 1, 1, 1, 3],
    )
    for row in OVERLAP:
        s.row([*row, ""], [1, 1, 1, 1, 1, 3])
    s.note(
        "States are stable: two-step moves are 0.2% or fewer; High mostly drops to Moderate, not "
        "Low. The overlap with each other axis is partial (Cramér's V 0.06–0.41; 1 would be the "
        "same axis): most with deterioration at 61–180, since payments drive the DPD path, least "
        "with ability. Credibility adds what the other axes do not carry."
    )


# --- back-tests -----------------------------------------------------------------------------
DEADLINE_AUC = [  # rule, label, values per book, best/worst marks
    (
        "Next statement · loans: end of next month",
        "Earlier rule",
        ["0.692", "0.666", "0.670", "0.746"],
    ),
    ("End of the month of the promise", "Today (GRR)", ["same", "0.643", "0.665", "0.736"]),
    ("30 days after the promise", "Lenient", ["0.714", "0.666", "0.690", "0.746"]),
]
BACKTESTS = [  # (question, what we tested, result, what we did)
    (
        "Who decides a promise was kept",
        "The collection system's instalment status vs the payments actually received.",
        "When the system says paid, a card payment backs only 52% of promises and 22% of "
        "settlement instalments; its 'paid' is often premature. The two give the same state for "
        "96–97% of accounts, but the system's status credits twice the kept instalments on cards.",
        "Payments decide.",
    ),
    (
        "Which promises count",
        "Plans in the promise and settlement tables only, vs adding promises collectors record "
        "in follow-up notes.",
        "Notes lift the accounts with promise evidence from 23% to 34% (cards) and 14% to 27% "
        "(loans). Promises found only in notes are paid as often as table plans: real promises "
        "the tables miss.",
        "Both count; notes within 8 days are one promise.",
    ),
    (
        "Moderate from 1 or 2 points",
        "State mix and outcomes with each cut-off.",
        "Moderate from 1 put half of all accounts in Moderate on a clean record alone; 85% of "
        "them (cards) made no promise and paid nothing while delinquent, the group that rolls "
        "most (94% vs 47% for Kept).",
        "Moderate from 2.",
    ),
    (
        "Promise window: this episode or 12 months",
        "Promises in the current episode only vs the last 12 months.",
        "About a third of concluded promises fall before the current episode, and they are "
        "paid more often (cards 49% vs 29%). 6–7% of states change, mostly up.",
        "Last 12 months: trust is a track record.",
    ),
    (
        "Promise deadline",
        "Earlier rule vs GRR's month end vs 30 days, AUC on paying a due (table below).",
        "30 days ranks best or equal in every book. GRR's month end ranks worst for loans and at "
        "180+. Loan promises paid in the following month are followed by the same payment rate "
        "as on-time ones (58% vs 58%; unpaid 46%), and the accounts it moves down keep paying "
        "like the state they left.",
        "Open, for GRR: today GRR's rule; the data favour 30 days.",
    ),
    (
        "No evidence: Unknown or Low",
        "Outcomes of delinquent accounts with no evidence in any dimension.",
        "They pay less than every other group (Validation, block 4).",
        "Low.",
    ),
    (
        "Broken vs Thin promises",
        "Broken against the three kinds of Thin (never promised; promised, not yet due; one "
        "failed), inside the same reachability, contact, payments and DPD bucket; Broken at −1, "
        "0, +1, and Thin at −1, under both deadlines.",
        "Never promising is what separates: those customers pay least (1–25%), also among "
        "reachable and contacted ones. A broken record pays like a single failed promise. Broken "
        "+1 ranks best in every book, deadline and month (cards 61–180 +0.045 AUC, loans +0.030, "
        "180+ +0.02 to +0.03) and moves 12% (cards) / 8% (loans) of 61–180 accounts from Low to "
        "Moderate; they pay like Moderate. Thin −1 hurts the state.",
        "Open, for GRR: Broken +1 (or 0); keep Thin at 0.",
    ),
    (
        "Strong negatives",
        "Refusal, dispute, avoidance (no response, no pickup, hang-ups).",
        "No response fired on 36% (cards) and was 84% locatability's Non-Reachable: a repeat. "
        "A dispute contests the debt and is rare (0.3%). Explicit refusal adds what the points "
        "do not carry (4.4%).",
        "Refusal only; the others are diagnostic columns.",
    ),
    (
        "Thresholds one step either way",
        "Every cut-off moved one step, one at a time.",
        "Only the Moderate cut-off moves many accounts; every other moves 4% or fewer.",
        "Cut-offs kept as proposed, Moderate from 2.",
    ),
]


UPCOMING = [  # (question, what it tests, why it matters, status)
    (
        "Promise points, final shape",
        "Broken and a single failed promise raised together; Broken +1 with Partly +2, so that "
        "Kept > Partly > Broken holds.",
        "Broken +1 ties Broken with Partly, yet Partly customers pay more; a single failed "
        "promise pays like Broken but stays at 0.",
        "Next, once GRR has seen the Broken vs Thin result.",
    ),
    (
        "180+ cut-offs",
        "Cut-offs on the points total at 180+ instead of the 61–180 ladder.",
        "96–97% of 180+ accounts are Low; the points rank them far better than the states "
        "(AUC 0.82–0.86 vs 0.67–0.74).",
        "With GRR.",
    ),
    (
        "Promise deadline",
        "GRR's decision between the month end and 30 days.",
        "30 days ranks best in every book and is the most lenient for the customer.",
        "Evidence ready; with GRR.",
    ),
    (
        "Dispute codes for loans",
        "Why no loan account at 61–180 shows a dispute (58 at 180+).",
        "A diagnostic column, not in the state; a mapping gap would hide disputes.",
        "To check.",
    ),
]


def backtests(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Back-tests"), [26, 32, 46, 28])
    s.title(
        "Back-tests: the questions tested and what they decided",
        "Each design choice was tested on production data before it was taken. Outcomes are over "
        "the 3 months after the scoring date.",
    )
    s.header(["Question", "What we tested", "Result", "Decision"])
    for row in BACKTESTS:
        s.row(list(row), [1, 1, 1, 1], amber=row[3].startswith("Open"))
    s.section("Promise deadline: ranking power (AUC on paying a due in 3 months)", gap=2)
    s.header(["Deadline", "Cards 61–180 · Loans 61–180", "Cards 180+ · Loans 180+", ""])
    best = {(2, 0), (0, 1), (2, 1), (2, 2), (0, 3), (2, 3)}
    worst = {(1, 1), (1, 2), (1, 3)}
    for i, (rule, label, vals) in enumerate(DEADLINE_AUC):

        def cell(j: int) -> str:
            v = vals[j]
            mark = " (best)" if (i, j) in best else " (worst)" if (i, j) in worst else ""
            return "same rule" if v == "same" else v + mark

        s.row(
            [f"{rule} ({label})", f"{cell(0)} · {cell(1)}", f"{cell(2)} · {cell(3)}", ""],
            [1, 1, 1, 1],
        )
    s.note(
        "Month ends March–May 2026, every book. Gaps of 0.01 or more are outside the 95% "
        "interval and hold in each of the three months. At cards 61–180 GRR's rule is the next "
        "statement, the same as the earlier rule."
    )
    s.section("Upcoming analyses", gap=2)
    s.header(["Question", "What it tests", "Why it matters", "Status"])
    for row in UPCOMING:
        s.row(list(row), [1, 1, 1, 1], amber=True)


# --- changes --------------------------------------------------------------------------------
CHANGES = [  # (area, before, now, why, effect)
    (
        "No response",
        "A strong negative: 3 call days without reaching the customer forced the state down.",
        "Removed from the state. Two avoidance signals stay as columns for "
        "analysis (no pickup after an earlier contact; hung up).",
        "84% (cards) / 78% (loans) of these customers were already Non-Reachable in "
        "locatability, mostly dead lines. Credibility was repeating locatability's verdict.",
        "37% of card and 20% of loan states moved up from Low (measured before the other "
        "changes).",
    ),
    (
        "Refusal",
        "Refusal list included hang-ups and 'customer misbehaved'.",
        "Only explicit refusals: refuse to pay, refused to pay, KSA refuse to pay, rewrite not "
        "agreed, with nothing (promise, arrangement, payment of 100 AED or more) after it. The "
        "only strong negative.",
        "Stated intent is evidence the points do not carry. A hang-up is avoidance, not a "
        "refusal.",
        "Fires for 4.4% of card and loan accounts.",
    ),
    (
        "Dispute",
        "Treated like a refusal.",
        "A column for analysis, not a negative.",
        "Contesting the debt is not unwillingness to pay.",
        "0.3% of cards, none on loans.",
    ),
    (
        "Broken promises",
        "0 points and a strong negative: always Low, even for a customer paying regularly.",
        "−1 point, no override. Broken promises count against the customer; the payments still "
        "count.",
        "Thin (no promises) and Broken scored the same 0; the override ignored regular payers.",
        "A Broken record with regular payments and a clean record is Moderate. Weight under "
        "review.",
    ),
    (
        "Moderate cut-off",
        "Moderate from 1 point.",
        "Moderate from 2 points.",
        "1 point alone was mostly a clean record with no promise and no payment while "
        "delinquent: the group that rolls most.",
        "About half of 61–180 accounts move from Moderate to Low.",
    ),
    (
        "Which promises count",
        "Promise and settlement plans from the tables, instalment by instalment.",
        "Every plan plus promises collectors record in follow-up notes, each judged once.",
        "The notes hold real promises the tables miss.",
        "Accounts with promise evidence: cards 23% to 34%, loans 14% to 27%.",
    ),
    (
        "Kept or broken",
        "The collection system's instalment status.",
        "The payments received after the promise, by the deadline.",
        "The system's 'paid' is often not backed by a payment.",
        "Same state for 96–97% of accounts; fewer false Kept.",
    ),
    (
        "Promise deadline",
        "The instalment's due date.",
        "Cards 61–180: next statement; loans and 180+: end of the month of the promise (GRR).",
        "One fixed deadline, whatever date was promised.",
        "Loans 61–180: 7.2% of states move down. Under review: 30 days ranks better.",
    ),
    (
        "Time frame",
        "Windows hung on the old spell logic.",
        "Promises: last 12 months, earlier episodes included. Payments: recent months. "
        "Record before: 12 months before the current episode.",
        "Trust is a track record; payments now are about recency; a repeat delinquent's earlier "
        "misses fall in the record on purpose.",
        "The 12-month promise window moves 6–7% of states, mostly up.",
    ),
    (
        "Unknown",
        "No evidence in any dimension (no promise, no payment, no record before).",
        "Only accounts with no observable delinquency episode.",
        "Paying nothing while delinquent is evidence, not a gap; these accounts pay least.",
        "Unknown is empty; cards 61–180 11.5% and 180+ 81% move to Low.",
    ),
    (
        "61–180 vs 180+ rules",
        "Chosen per account from its own bucket.",
        "Chosen by the model (segment), as ability and locatability do.",
        "An account at 181–210 DPD inside the 61–180 model got the 180+ windows.",
        "Consistent windows within each model.",
    ),
    (
        "Smallest payment",
        "100 AED minimum at 180+ only.",
        "100 AED minimum in every band for payments in delinquency.",
        "A token payment is not evidence of paying.",
        "Fewer 'Some' from token amounts at 61–180.",
    ),
    (
        "Paid as billed",
        "DE sheet: the amount due, by the due date.",
        "The amount due, before the next statement.",
        "A few days' lateness within the cycle is not a credibility signal.",
        "Applies to the record before delinquency.",
    ),
    (
        "Output",
        "State with a confidence score and a provenance flag.",
        "State plus every input behind it (levels, points, counts, the refusal and diagnostic "
        "columns).",
        "The confidence was a fixed number per state and told nothing; the inputs let anyone "
        "trace a state.",
        "No effect on states.",
    ),
]
UNCHANGED = [
    (
        "Structure",
        "Three dimensions (promises, payments now, record before), summed points, one strong "
        "negative.",
    ),
    ("Points", "Kept 2, Partly kept 1, Thin 0; Regular 2, Some 1, None 0; Clean 1."),
    (
        "Thresholds",
        "The DE's cut-offs: High from 4, 80% / 40% / 2 concluded / 3 in a row, 2 of 3 and 3 of "
        "6 months, 12-month record, 3 months due, 80% clean.",
    ),
]
OPEN = [
    (
        "Promise deadline",
        "GRR's month end (today), the earlier next-statement / next-month-end rule, or 30 days "
        "after the promise.",
        "30 days ranks best or equal in every book (cards +0.02 AUC); the month end ranks worst "
        "for loans and at 180+ ('Back-tests'). The choice is GRR's.",
    ),
    (
        "Weight of Broken promises",
        "−1 (today), 0 or +1.",
        "Never promising separates, not breaking: Broken pays like a single failed promise and far "
        "above never promised. Broken +1 ranks best in every book, deadline and month; 0 gets "
        "about half the gain. Thin −1 hurts the state ('Back-tests').",
    ),
    (
        "180+ cut-offs",
        "Keep the three states, or set 180+ cut-offs on the points.",
        "96–97% of 180+ accounts are Low; the points total ranks them far better (AUC "
        "0.82–0.86 vs 0.67–0.74). The step in payment comes at 2 points in every book.",
    ),
]


def changes(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Changes"), [20, 34, 38, 38, 30])
    s.title(
        "Changes",
        "What changed against the DE's framework (A3_credibility_shared_Nov3), why, and the "
        "effect measured on production. Business rules only.",
    )
    s.header(["Area", "Before", "Now", "Why", "Effect"])
    for row in CHANGES:
        s.row(list(row), [1] * 5, amber=row[0] in ("Promise deadline", "Broken promises"))
    s.section("Unchanged")
    s.header(["Area", "What stays"], [1, 4])
    for row in UNCHANGED:
        s.row(list(row), [1, 4])
    s.section("Still open")
    s.header(["Question", "Options", "Evidence so far"], [1, 2, 2])
    for row in OPEN:
        s.row(list(row), [1, 2, 2], amber=True)
    s.ws.freeze_panes = "A5"


def build(out: pathlib.Path) -> pathlib.Path:
    wb = Workbook()
    framework(wb)
    map_sheet(wb)
    results(wb)
    validation(wb)
    backtests(wb)
    changes(wb)
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--out", default=str(pathlib.Path(__file__).with_name("a3_credibility_reference.xlsx"))
    )
    print(build(pathlib.Path(ap.parse_args().out)))


if __name__ == "__main__":
    main()
