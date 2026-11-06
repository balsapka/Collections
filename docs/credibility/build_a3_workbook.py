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
HIGH_FROM, MODERATE_FROM = 4, 1
POINTS_A = {"Kept": 2, "Partly kept": 1, "Thin": 0, "Broken": -1}  # Broken −1: proposed (V1e)
POINTS_B = {"Regular": 2, "Some": 1, "None": 0}
POINTS_C = {"Clean": 1, "Not clean": 0, "No record": 0}


def state(a: str, b: str, c: str, refusal: bool) -> str:
    """Proposed ladder: summed points, refusal the only strong negative."""
    if (a, b, c, refusal) == ("Thin", "None", "No record", False):
        return "Unknown"
    pts = POINTS_A[a] + POINTS_B[b] + POINTS_C[c]
    if pts >= HIGH_FROM:
        return "Moderate" if refusal else "High"
    if pts >= MODERATE_FROM and not refusal:
        return "Moderate"
    return "Low"


def state_de(a: str, b: str, c: str, negative: bool) -> str:
    """The DE sheet: Broken = 0 points and a strong negative; refusal or no response."""
    negative = negative or a == "Broken"
    if (a, b, c, negative) == ("Thin", "None", "No record", False):
        return "Unknown"
    pts = {**POINTS_A, "Broken": 0}[a] + POINTS_B[b] + POINTS_C[c]
    if pts >= HIGH_FROM:
        return "Moderate" if negative else "High"
    return "Moderate" if pts >= MODERATE_FROM and not negative else "Low"


def _claims(a: str, b: str, c: str, refusal: bool) -> int:
    """Number of state rules that claim the cell (the MECE proof: must be 1)."""
    unknown = (a, b, c, refusal) == ("Thin", "None", "No record", False)
    pts = POINTS_A[a] + POINTS_B[b] + POINTS_C[c]
    rules = [
        unknown,
        not unknown and pts >= HIGH_FROM and not refusal,
        not unknown
        and ((MODERATE_FROM <= pts < HIGH_FROM and not refusal) or (pts >= HIGH_FROM and refusal)),
        not unknown and (pts < MODERATE_FROM or (pts < HIGH_FROM and refusal)),
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
        "Capacity to pay (A1 ability), whether we can find and reach the customer (A2 "
        "locatability), the DPD path itself (A4 deterioration). A weak flow can mean "
        "inability, not unwillingness: read A3 together with A1.",
    ),
    (
        "Time frame",
        "Everything is read inside the current delinquency episode: it starts when the "
        "account last became delinquent (a cure back to current ends an episode). The "
        "record before delinquency is the 12 months before that start.",
    ),
    (
        "This debt",
        "Promises, contacts and payments are those of the scored account only (A1 looks "
        "across all the customer's accounts; credibility is about this debt).",
    ),
    (
        "How to read",
        "Score the three dimensions (block 2) and add the points; Broken promises count "
        "against. A refusal (block 3) takes one level off. Read the state in block 1.",
    ),
    (
        "Basis",
        "Validated on production, credit cards and retail loans 61–180 DPD, Aug 2026 (19,292 "
        "card and 3,985 loan accounts). Thresholds are the DE's proposals; only the Moderate "
        "cut-off moves more than 6% of accounts when shifted one step.",
    ),
    ("Status", "Amber rows are proposals still being validated (see 'Changes', Still open)."),
]

STATES = [
    ("High", "Total of 4 or more, and no refusal.", "Keeps promises and money is coming in."),
    (
        "Moderate",
        "Total from 1 to below 4, and no refusal. Or 4 or more with a refusal.",
        "Some evidence to rely on, not yet consistent. Or a strong record with a fresh refusal.",
    ),
    (
        "Low",
        "Total below 1. Or below 4 with a refusal.",
        "Nothing positive on record, or what there is has been outweighed by broken promises or a "
        "refusal.",
    ),
    (
        "Unknown",
        "No evidence in any dimension: promises Thin, payments None, no record before, "
        "and no refusal.",
        "Nothing observed either way. Not the same as Low.",
    ),
]

DIMENSIONS = [
    (
        "A. Promises kept. Does the customer do what they commit to?",
        [
            (
                "Window",
                "",
                "Instalments of promises to pay and settlement arrangements on this account that "
                "fell due in the last 12 months, inside the current delinquency. Pending ones "
                "do not count.",
                False,
            ),
            (
                "Kept or broken",
                "",
                "An instalment is kept when it was paid. Whether DCORE's status or the "
                "payment received decides, and how much grace after the due date, "
                "is being validated.",
                True,
            ),
            ("Kept", "2", "Not Broken, at least 2 concluded, and 80% or more of them kept.", False),
            ("Partly kept", "1", "Not Broken, not Kept, and at least one kept.", False),
            (
                "Thin",
                "0",
                "None concluded, or one concluded and broken. No evidence either way.",
                False,
            ),
            (
                "Broken",
                "−1",
                "The last 3 concluded were all broken, or at least 2 concluded and fewer than "
                "40% kept. Checked first. Counts against the customer (proposed; the weight "
                "is being validated).",
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
            ("None", "0", "Nothing of 100 AED or more in the window.", False),
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
                "Fewer than 3 months with an amount due. No evidence either way.",
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
        "Takes the state one level down. About 4.4% of accounts.",
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
    ("State: Moderate from (total points)", "1", "DE proposal; GRR calibration point", False),
    ("Promises: window in months, inside this delinquency", "12", "DE proposal", False),
    ("Promises: concluded needed before a rate counts", "2", "Waterfall", False),
    ("Promises: Kept from (share kept)", "80%", "Waterfall", False),
    ("Promises: Broken below (share kept)", "40%", "Waterfall", False),
    ("Promises: Broken when the last N concluded were all broken", "3", "Waterfall", False),
    ("Promises: points for Broken", "−1", "Proposed, being validated", True),
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
    (
        "Payments in delinquency: smallest payment that counts",
        "100 AED",
        "Decided, every band",
        False,
    ),
    ("Record before: window in months before the delinquency", "12", "Redesign ask", False),
    ("Record before: months with an amount due needed", "3", "DE proposal", False),
    ("Record before: Clean from (share of months paid as billed)", "80%", "DE proposal", False),
    (
        "Record before: paid as billed by",
        "the next statement",
        "Decided (DE sheet: due date)",
        False,
    ),
    ("Diagnostics: failed call days (61–180 / 180+)", "3 / 6", "As A2", False),
]


def framework(wb: Workbook) -> None:
    s = Sheet(wb.active, [30, 9, 62, 44])
    s.ws.title = "A3 framework"
    s.title(
        "A3 Payment Credibility: framework",
        "Accounts at 60+ DPD under active collection, credit card and retail loan. Three scored "
        "dimensions and one strong negative. Updated 5 Nov 2026 from the DE's framework with the "
        "decisions taken since (what changed: 'Changes').",
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
        "Broken promises are no longer a strong negative: they count −1 in the points. 'No "
        "response' is removed: it repeated A2's Non-Reachable."
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
        "72 combinations, each claimed by exactly one state rule (checked when the workbook is "
        "built). * = a different state from the DE's map: Broken now counts −1 instead of forcing "
        "Low, and the strong-negative column is refusal only (no response removed).",
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
        f"{changed} of 72 cells differ from the DE's map, all in the Broken rows: a Broken record "
        "with regular payments, or some payment and a clean record, is now Moderate instead of "
        "Low. Amber: Broken's weight (−1) is a proposal being validated."
    )
    s.ws.freeze_panes = "D5"
    # checks: the cells the narrative relies on
    assert state("Broken", "Regular", "Clean", False) == "Moderate"
    assert state("Broken", "Some", "Not clean", False) == "Low"
    assert state("Broken", "None", "Clean", False) == "Low"
    assert state("Thin", "None", "No record", False) == "Unknown"
    assert state("Kept", "Regular", "No record", True) == "Moderate"


# --- changes --------------------------------------------------------------------------------
CHANGES = [  # (area, before, now, why, effect)
    (
        "No response",
        "A strong negative: 3 call days without reaching the customer forced the state " "down.",
        "Removed from the state. Two avoidance signals stay as columns for "
        "analysis (no pickup after an earlier contact; hung up).",
        "84% (cards) / 78% (loans) of these customers were already Non-Reachable in A2, mostly dead "
        "lines. A3 was repeating A2's verdict.",
        "The largest change: 37% of card and 20% of loan states move, all up from Low.",
    ),
    (
        "Refusal",
        "Refusal list included hang-ups and 'customer misbehaved'.",
        "Only explicit refusals: refuse to pay, refused to pay, KSA refuse to pay, rewrite not agreed, "
        "with nothing (promise, arrangement, payment of 100 AED or more) after it. The only strong "
        "negative.",
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
        "Broken promises (proposed)",
        "0 points and a strong negative: always Low, even for a " "customer paying regularly.",
        "−1 point, no override. Broken promises count against the customer; the payments still count.",
        "Thin (no promises) and Broken scored the same 0; the override ignored regular payers.",
        "4 of 72 map cells move from Low to Moderate. Weight (−1 or −2) being validated.",
    ),
    (
        "Time frame",
        "Windows hung on the old spell logic; promises counted over the last 12 months "
        "regardless of when the delinquency began.",
        "Everything is read inside the current delinquency episode; the record before is the 12 "
        "months before it began.",
        "Promises from an earlier, cured episode are old news. A repeat "
        "delinquent's earlier misses fall in the record on purpose.",
        "Promise counts change for 16% of card and 7.5% of loan agreements.",
    ),
    (
        "61–180 vs 180+ rules",
        "Chosen per account from its own bucket.",
        "Chosen by the model (segment), as A1 and A2 do.",
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
        "State plus every input behind it (levels, points, counts, the refusal and diagnostic columns).",
        "The confidence was a fixed number per state and told nothing; the inputs let anyone trace "
        "a state.",
        "No effect on states.",
    ),
]
UNCHANGED = [
    (
        "Structure",
        "Three dimensions (promises, payments now, record before), summed points, four "
        "states including Unknown.",
    ),
    ("Points", "Kept 2, Partly kept 1, Thin 0; Regular 2, Some 1, None 0; Clean 1."),
    (
        "Thresholds",
        "All the DE's cut-offs: High from 4, Moderate from 1, 80% / 40% / 2 concluded / "
        "3 in a row, 2 of 3 and 3 of 6 months, 12-month record, 3 months due, 80% clean.",
    ),
]
OPEN = [
    (
        "Who decides a promise was kept",
        "DCORE's instalment status, or the payment actually received; "
        "and how much grace after the due date.",
        "When DCORE says overdue it is right (almost never a payment behind it). When it says paid, a "
        "card payment backs 52% of promises and 22% of settlement instalments (69% / 35% with 5 days' "
        "grace); loans 94% / 53%. A check of where that money goes (other accounts, other forms, late "
        "payment) is running.",
    ),
    (
        "Weight of Broken promises",
        "−1 (proposed), −2, or 0 (scores like Thin).",
        "A check compares what Broken customers paid and how they rolled over the next 3 months with "
        "Thin customers who have the same payments and record.",
    ),
    (
        "Calibration with GRR",
        "Moderate from 1 point or 2; High from 4 or 3.",
        "Moderate from 2 moves 19% of card and 29% of loan accounts. High from 3 would open High to "
        "regular payers with a clean record and no promises (moves 2–6%).",
    ),
]


def changes(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Changes"), [20, 34, 38, 38, 30])
    s.title(
        "Changes",
        "What changed against the DE's framework (A3_credibility_shared_Nov3), why, and "
        "the effect measured on production (61–180 DPD, Aug 2026). Business rules only.",
    )
    s.header(["Area", "Before", "Now", "Why", "Effect"])
    for row in CHANGES:
        s.row(list(row), [1] * 5, amber=row[0].endswith("(proposed)"))
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
