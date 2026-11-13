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
        "August 2026 ('Results'). Outcomes: back-tests on March–May 2026 with the next 3 months "
        "('Validation', 'Back-tests').",
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
                "40% kept. Checked first. Counts against the customer. Under review: Broken "
                "customers pay more often than Thin ones ('Validation').",
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
    ("Promises: points for Broken", "−1", "Decided; Broken vs Thin under review", True),
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
    "Cards 61–180": (19292, 490, 3748, 15054),
    "Loans 61–180": (3985, 126, 980, 2879),
    "Cards 180+": (318663, 159, 8290, 310214),
    "Loans 180+": (55371, 120, 2289, 52962),
}
# The same month with the earlier deadline (cards: next statement; loans: end of next month).
RESULTS_PREV = {
    "Cards 61–180": (19292, 491, 3748, 15053),
    "Loans 61–180": (3985, 196, 1113, 2676),
    "Cards 180+": (318663, 222, 8616, 309825),
    "Loans 180+": (55371, 171, 2386, 52814),
}
LEVELS_A = {  # book: (Kept, Partly kept, Thin, Broken) counts, August 2026
    "Cards 61–180": (441, 2686, 13544, 2621),
    "Loans 61–180": (192, 480, 2970, 343),
    "Cards 180+": (146, 2483, 312052, 3982),
    "Loans 180+": (100, 734, 54100, 437),
}


def _pct(x: int, n: int) -> str:
    return f"{100 * x / n:.1f}%"


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [22, 12, 14, 14, 14, 14])
    s.title(
        "Results: the state mix, August 2026",
        "Share of accounts in each state at the August 2026 month end, under the rules in 'A3 "
        "framework'. Unknown is empty: every account scored has an observed delinquency episode.",
    )
    s.section("1. State mix")
    s.header(["Book", "Accounts", "High", "Moderate", "Low", "Unknown"])
    for book in BOOKS:
        n, hi, mo, lo = RESULTS[book]
        assert hi + mo + lo == n, book
        s.text(1, book, bold=True)
        s.text(2, f"{n:,}", align=CENTER)
        for col, (st, x) in enumerate(zip(("High", "Moderate", "Low"), (hi, mo, lo)), 3):
            s.text(col, f"{_pct(x, n)} ({x:,})", align=CENTER, fill=TONE[st][0])
        s.text(6, "0%", align=CENTER, fill=TONE["Unknown"][0])
        s.r += 1
    s.note(
        "180+ is almost all Low by construction: little is paid, few promises are made, and the "
        "history before a long charge-off is often too short to judge. The few High and Moderate "
        "accounts at 180+ are the positive signal the strategy looks for."
    )
    s.section("2. Effect of the promise deadline on the same month")
    s.header(["Book", "Deadline", "High", "Moderate", "Low", "States changed"])
    for book in BOOKS:
        n, *now = RESULTS[book]
        _, *prev = RESULTS_PREV[book]
        for label, vals in (("Earlier rule", prev), ("Today's rule", now)):
            s.text(1, book, bold=label == "Earlier rule")
            s.text(2, label)
            for col, x in enumerate(vals, 3):
                s.text(col, _pct(x, n), align=CENTER)
            moved = {
                "Cards 61–180": "0.0%",
                "Loans 61–180": "7.2%",
                "Cards 180+": "0.4%",
                "Loans 180+": "0.5%",
            }[book]
            s.text(6, moved if label == "Today's rule" else "", align=CENTER)
            s.r += 1
    s.note(
        "Earlier rule: cards the next statement, loans the end of the following month. Today's "
        "rule (GRR): loans and all 180+ by the end of the month of the promise. Loans at 61–180 "
        "move down: about a quarter of loan promises are paid in the following month, and paid "
        "promises fall from 70.5% to 46.8%. Cards at 61–180 keep the statement, so nothing moves."
    )
    s.section("3. Promises (Dimension A)")
    s.header(["Book", "Accounts", "Kept", "Partly kept", "Thin", "Broken"])
    for book in BOOKS:
        n = RESULTS[book][0]
        vals = LEVELS_A[book]
        assert sum(vals) == n, book
        s.text(1, book, bold=True)
        s.text(2, f"{n:,}", align=CENTER)
        for col, x in enumerate(vals, 3):
            s.text(col, _pct(x, n), align=CENTER)
        s.r += 1
    s.note(
        "Most accounts have no concluded promise in 12 months (Thin): their credibility rests on "
        "payments and the record before delinquency. Collector follow-up notes are what lift "
        "coverage (see 'Back-tests')."
    )


# --- validation -----------------------------------------------------------------------------
# Back-test: month ends March, April, May 2026 pooled; outcomes over the next 3 months.
OUTCOMES = [  # book, (High, Moderate, Low) paid a due %, (High, Moderate, Low) rolled %, mix
    ("Cards 61–180", (64.9, 35.2, 11.0), (47, 73, 93), (4.0, 21.7, 74.3)),
    ("Loans 61–180", (71.5, 54.2, 26.2), (54, 67, 83), (3.8, 26.4, 69.8)),
    ("Cards 180+", (50.2, 30.6, 1.6), None, (0.0, 2.6, 97.4)),
    ("Loans 180+", (67.2, 32.5, 1.4), None, (0.2, 3.6, 96.2)),
]
AUC = [  # book, state AUC on paid a due, points-total AUC on paid a due
    ("Cards 61–180", "0.692", "0.70"),
    ("Loans 61–180", "0.643", "0.70"),
    ("Cards 180+", "0.665", "0.82"),
    ("Loans 180+", "0.736", "0.86"),
]
NO_RECORD = [  # book, share of rows, paid a due %: no evidence / rest of Low / Moderate
    ("Cards 61–180", "12.2%", "3.9%", "12.4%", "35.2%"),
    ("Loans 61–180", "7.0%", "9.2%", "28.1%", "54.2%"),
    ("Cards 180+", "83.0%", "0.5%", "7.6%", "30.6%"),
    ("Loans 180+", "65.1%", "0.2%", "3.9%", "32.5%"),
]


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [22, 13, 13, 13, 13, 13, 13])
    s.title(
        "Validation: what each state goes on to do",
        "Back-test on the month ends of March, April and May 2026 (pooled), today's rules, "
        "outcomes over the following 3 months. Paid a due: payments reach at least one month's "
        "due. Rolled: a worse DPD bucket at month 3 (61–180 only).",
    )
    s.section("1. Outcome rates by state")
    s.text(1, "", border=False)
    s.text(2, "Paid a due in 3 months", span=3, bold=True, align=CENTER, fill="EEF3FA")
    s.text(5, "Rolled to a worse bucket", span=3, bold=True, align=CENTER, fill="EEF3FA")
    s.r += 1
    s.header(["Book", "High", "Moderate", "Low", "High", "Moderate", "Low"])
    for book, paid, rolled, _ in OUTCOMES:
        s.text(1, book, bold=True)
        for col, (st, x) in enumerate(zip(("High", "Moderate", "Low"), paid), 2):
            s.text(col, f"{x:.1f}%", align=CENTER, fill=TONE[st][0])
        for col in range(5, 8):
            x = rolled[col - 5] if rolled else None
            s.text(col, f"{x}%" if x is not None else "n/a", align=CENTER)
        s.r += 1
    s.note(
        "Every book orders the states in the right direction: High pays most and rolls least. "
        "Cure (back to current) is too rare at 61–180 cards (0.2%) to separate states; read "
        "payment and roll. At 180+ cure and roll are near zero by construction."
    )
    s.section("2. Ranking power (AUC on paid a due; 0.5 = chance)")
    s.header(["Book", "State (3 levels)", "Points total", "", "", "", ""], [1, 1, 1, 4])
    for book, st_auc, pts_auc in AUC:
        s.row([book, st_auc, pts_auc, ""], [1, 1, 1, 4])
    s.note(
        "The points total ranks better than the three states, most of all at 180+, where 96–97% "
        "of accounts sit in Low. The cut-offs at 180+ lose most of the ordering: a 180+ cut-off "
        "review is open."
    )
    s.section("3. Promises: outcome by level (paid a due in 3 months, 61–180)")
    s.header(["Book", "Kept", "Partly kept", "Broken", "Thin", "", ""], [1, 1, 1, 1, 1, 2])
    s.row(["Cards 61–180", "38.4%", "32.9%", "28.5%", "11.6%", ""], [1, 1, 1, 1, 1, 2])
    s.row(["Loans 61–180", "", "", "40.5%", "27.7%", ""], [1, 1, 1, 1, 1, 2])
    s.note(
        "Broken customers pay more often than Thin ones, the opposite of the points (Broken −1, "
        "Thin 0). A broken promise still means the customer engaged; most Thin accounts never "
        "promised. A test of whether this is credibility or engagement, and of the right "
        "weights, is running (all four books)."
    )
    s.section("4. Accounts with no evidence at all (now Low)")
    s.header(
        ["Book", "Share of rows", "Paid a due:\nno evidence", "Rest of Low", "Moderate", "", ""],
        [1, 1, 1, 1, 1, 2],
    )
    for row in NO_RECORD:
        s.row(list(row) + [""], [1, 1, 1, 1, 1, 2])
    s.note(
        "They pay less than the rest of Low in every book, so Low is the right place for them, "
        "not a separate state. At 61–180 most are young accounts (cards: 71% under 6 months on "
        "book: early payment default) plus old cards with no bill; at 180+ mostly accounts "
        "charged off long ago, or whose history does not reach back far enough."
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
        "Broken vs Thin promises",
        "Outcomes of Broken vs Thin within the same reachability, recent contact, payments and "
        "DPD bucket; Thin split into never promised / promised, nothing concluded / one broken; "
        "point weights re-scored (Broken −1, 0, +1; Thin −1), under both deadlines.",
        "Broken customers pay more often than Thin ones: either the weights are in the wrong "
        "order, or the gap is engagement that locatability already counts.",
        "Running, all four books.",
    ),
    (
        "Detailed results",
        "State mix by month (trend), by loan product, by 180+ charge-off age and by DPD bucket; "
        "outcome rates by state within each; refusal and diagnostics.",
        "Shows the states hold within products and buckets, not only on the book total.",
        "Prompt ready; results fill the 'Results' and 'Validation' sheets.",
    ),
    (
        "180+ cut-offs",
        "Cut-offs on the points total at 180+ instead of the 61–180 ladder.",
        "96–97% of 180+ accounts are Low; the points rank them far better than the states.",
        "After the two above, for GRR.",
    ),
    (
        "Promise deadline",
        "GRR's decision between the month end and 30 days.",
        "30 days ranks best in every book and is the most lenient for the customer.",
        "Evidence ready ('Back-tests'); with GRR.",
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
        "−1 (today), 0, +1; or Thin −1; or Thin split (never promised / promised but nothing "
        "concluded / one broken).",
        "Broken customers pay more often than Thin ones at 61–180 (cards 28.5% vs 11.6%). A test "
        "across all four books, within the same reachability and payments, is running.",
    ),
    (
        "180+ cut-offs",
        "Keep the three states, or set 180+ cut-offs on the points.",
        "96–97% of 180+ accounts are Low; the points total ranks them far better (AUC "
        "0.82–0.86 vs 0.67–0.75).",
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
