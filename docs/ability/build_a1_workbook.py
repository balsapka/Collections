"""Build the A1 ability model document (business-facing).

    python build_a1_workbook.py [--out a1_ability_reference.xlsx]

The rules follow ``workplace_mirror/specs/A1_ability_family_rule.md`` (income:
``A1_ability_spec.md``). Every worked example is run through the reference rules below and the
build FAILS if an example no longer gets the level or state it illustrates. Results are entry
cells (pale yellow) holding production numbers, blank where a split has not run; shares and
totals are formulas.

Design: one colour meaning everywhere — green favourable, amber in between, red adverse, grey
no evidence; navy is structure only.
"""

from __future__ import annotations

import argparse
import math
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# --- rules (reference implementation, 61–180 DPD window unless ``w`` is given) --------------
WINDOW = {"61–180 DPD": 3, "180+ DPD": 6}  # months, the scoring month included
MIN_MONTHS = {3: 2, 6: 3}  # months of the window a flow or balance must reach its floor
STABLE_FLOORS = {3: 2, 6: 3}  # the window's salary covers this many monthly floors
INCOME_FLOOR, INCOME_ANCHOR, INCOME_MAX_FALL = 3000, 2, 0.25
MIN_SALARY = 1000  # smallest monthly salary that counts as evidence
FLOW_FLOOR, MONEY_IN_SOME, MONEY_OUT_SOME = 1000, 1000, 500
BALANCE_FLOOR, BALANCE_MAX_FALL = 3000, 0.50
ASSET_FLOOR, ASSET_ANCHOR, INSTALMENT_FLOOR = 10000, 3, 1000
W = 3


def _mean(months: list, missing_is_zero: bool) -> float | None:
    if missing_is_zero:
        return sum(m or 0 for m in months) / len(months)
    present = [m for m in months if m is not None]
    return sum(present) / len(present) if present else None


def _holding(months: list, max_fall: float, missing_is_zero: bool, w: int) -> bool:
    """The window's average is not more than ``max_fall`` below the prior window's."""
    recent = _mean(months[-w:], missing_is_zero)
    prior = _mean(months[-2 * w : -w], missing_is_zero)
    return True if not prior or recent is None else recent >= prior * (1 - max_fall)


def salary_months(internal: list, bureau: list) -> list:
    """Salary per month, oldest first: the larger of the internal and the bureau figure, a
    bureau figure counting in its own month and the next unless that month has its own."""
    carried = [b if b is not None else (bureau[k - 1] if k else None) for k, b in enumerate(bureau)]
    both = zip(internal, carried)
    return [None if i is None and b is None else max(i or 0, b or 0) for i, b in both]


def income(internal: list, bureau: list, anchor: float = 0, w: int = W) -> str:
    months = salary_months(internal, bureau)
    floor = max(INCOME_FLOOR, INCOME_ANCHOR * anchor)
    has_internal = any((m or 0) >= MIN_SALARY for m in internal[-2 * w :])
    total = sum(m or 0 for m in months[-w:])
    if total >= STABLE_FLOORS[w] * floor and _holding(months, INCOME_MAX_FALL, has_internal, w):
        return "stable"
    return "weak" if any((m or 0) >= MIN_SALARY for m in months[-w:]) else "none"


def flow(months: list, some_floor: float, anchor: float = 0, w: int = W) -> str:
    """Money in or money out over the window, oldest first."""
    floor = max(FLOW_FLOOR, anchor)
    if sum((m or 0) >= floor for m in months[-w:]) >= MIN_MONTHS[w]:
        return "strong"
    return "some" if any((m or 0) >= some_floor for m in months[-w:]) else "none"


def balance_held(months: list, anchor: float = 0, w: int = W) -> bool:
    floor = max(BALANCE_FLOOR, anchor)
    enough = sum((m or 0) >= floor for m in months[-w:]) >= MIN_MONTHS[w]
    return enough and _holding(months, BALANCE_MAX_FALL, False, w)


def other_products(assets: float, current: bool, instalment: float, anchor: float = 0) -> str:
    if assets >= max(ASSET_FLOOR, ASSET_ANCHOR * anchor) or (
        current and instalment >= max(INSTALMENT_FLOOR, anchor)
    ):
        return "strong"
    return "some" if current or assets > 0 else "none"


def state(levels: list[str], distress: bool = False, movement: bool = False) -> str:
    """``levels`` of the four families; ``movement`` = a counted account movement in the window."""
    strong = sum(lev in ("stable", "strong") for lev in levels)
    if all(lev == "none" for lev in levels) and not distress and not movement:
        return "unknown"
    rung = min(strong, 2) - distress
    return "high" if rung == 2 else "moderate" if rung == 1 else "low"


# --- design system --------------------------------------------------------------------------
FONT = "Arial"
NAVY, INK, MUTED, RULE, PANEL = "1F3864", "262626", "7F7F7F", "D9D9D9", "F2F2F2"
TONE = {  # (fill, text)
    "good": ("E2EFDA", "375623"),
    "mid": ("FFE699", "7F6000"),
    "bad": ("FBE2D5", "9C2B12"),
    "unknown": ("EDEDED", "595959"),
}
KEY_TONE = {
    "high": "good", "moderate": "mid", "low": "bad",
    "stable": "good", "weak": "mid", "strong": "good", "some": "mid", "none": "unknown",
    "distress": "bad",
}  # fmt: skip
LABEL = {
    "high": "High", "moderate": "Moderate", "low": "Low", "unknown": "Unknown",
    "stable": "Stable", "weak": "Weak", "strong": "Strong", "some": "Some", "none": "None",
    "distress": "Distress",
}  # fmt: skip
STATES = ["high", "moderate", "low", "unknown"]
FAMILIES = ["F1 Income", "F2 Money in or held", "F3 Money out", "F4 Other products"]
WINDOW_HEAD, WINDOW_FILL, INPUT_FILL = "2E75B6", "DDEBF7", "FFF2CC"
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

    def fit(self, texts: list[tuple[str, float]], floor: float = 20) -> None:
        """Row height for wrapped ``(text, column width)`` pairs."""
        lines = max(
            sum(math.ceil(max(len(p), 1) / max(w * 1.1, 1)) for p in str(t or "").split("\n"))
            for t, w in texts
        )
        self.ws.row_dimensions[self.r].height = max(floor, 13.5 * lines + 6)

    def merge(self, c1: int, c2: int) -> None:
        if c2 > c1:
            self.ws.merge_cells(start_row=self.r, start_column=c1, end_row=self.r, end_column=c2)

    def title(self, text: str, lead: str) -> None:
        self.ws["A1"] = text
        self.ws["A1"].font = _font(size=16, bold=True, color=NAVY)
        self.r = 2
        self.text(1, lead, span=self.last, border=False)
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

    def header(self, labels: list, spans: list[int] | None = None, height: float = 20) -> None:
        col = 1
        for lab, span in zip(labels, spans or [1] * len(labels)):
            self.text(col, lab, span=span, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
            col += span
        self.ws.row_dimensions[self.r].height = height
        self.r += 1

    def text(self, col: int, value, *, span: int = 1, bold: bool = False, color: str = INK,
             fill: str | None = None, align: Alignment = TOP, border: bool = True,
             fmt: str | None = None):  # fmt: skip
        c = self.ws.cell(row=self.r, column=col, value=value)
        c.font = _font(bold=bold, color=color)
        c.alignment = align
        if fmt:
            c.number_format = fmt
        for k in range(col, col + span):
            cell = self.ws.cell(row=self.r, column=k)
            if fill:
                cell.fill = _fill(fill)
            if border:
                cell.border = BOX
        self.merge(col, col + span - 1)
        return c

    def chip(self, col: int, key: str, label: str | None = None, span: int = 1, align=MID):
        fill, ink = TONE[KEY_TONE.get(key, key)]
        return self.text(col, label or LABEL[key], span=span, bold=True, color=ink, fill=fill,
                         align=align)  # fmt: skip

    def row(self, values: list, spans: list[int] | None = None, *, bold_first: bool = True,
            align: Alignment = TOP, tones: dict | None = None) -> None:  # fmt: skip
        """One table row; ``tones`` = {value index: tone} fills a cell."""
        col, texts = 1, []
        for i, (v, span) in enumerate(zip(values, spans or [1] * len(values))):
            tone = (tones or {}).get(i)
            self.text(col, v, span=span, bold=bold_first and i == 0, align=align,
                      fill=TONE[tone][0] if tone else None)  # fmt: skip
            texts.append((v, self.width(col, col + span - 1)))
            col += span
        self.fit(texts)
        self.r += 1

    def note(self, text: str) -> None:
        self.text(1, text, span=self.last, border=False)
        self.ws.cell(row=self.r, column=1).font = _font(color=MUTED, italic=True)
        self.fit([(text, self.width(1, self.last))], floor=16)
        self.r += 1


# --- overview -------------------------------------------------------------------------------
STATE_MAP = [  # (strong families, state without distress, state with distress)
    ("2 or more", "high", "moderate"),
    ("1", "moderate", "low"),
    ("None, but some evidence", "low", "low"),
    ("None, and no evidence", "unknown", "low"),
]


def overview(wb: Workbook) -> None:
    s = Sheet(wb.active, [26, 26, 26, 26, 26])
    s.ws.title = "Overview"
    s.title(
        "A1 Ability",
        "Can the customer pay? Four families of evidence about the customer's money and a "
        "distress override; every account in scope gets exactly one state.",
    )
    for k, v in [
        ("Scope", "Credit cards and retail loans (Personal Loans, Personal Cash Loans, Auto) at "
                  "61–180 DPD and 180+ DPD, scored at each month end."),
        ("F1 Income", "Salary received: credited to an account with us, or reported by the "
                      "credit bureau."),
        ("F2 Money in or held", "Other money coming into the customer's current and savings "
                                "accounts, or a balance held there."),
        ("F3 Money out", "Money the customer chooses to spend or move out of those accounts."),
        ("F4 Other products", "Deposits, investments or wealth assets with us, or another credit "
                              "product kept current."),
        ("Distress", "A returned cheque or direct debit takes the state one level down."),
        ("Principle", "Customer level: every signal covers all the customer's accounts with us. "
                      "Only the months up to the scoring date are read, nothing from before the "
                      "delinquency. Thresholds scale with what the customer must pay now."),
        ("Unknown", "We cannot see the customer's money: absence of data, not evidence of no "
                    "ability."),
    ]:  # fmt: skip
        s.text(1, k, bold=True, color=NAVY, border=False)
        s.text(2, v, span=4, border=False)
        s.fit([(v, s.width(2, 5))], floor=18)
        s.r += 1
    s.section("States")
    s.header(["State", "Rule", "Meaning"], [1, 2, 2])
    for st, rule, meaning in [
        ("high", "2 or more families strong, no distress.",
         "Money confirmed from two independent sides."),
        ("moderate", "1 family strong, no distress. Or 2 or more with distress.",
         "One side confirmed; or more, but a payment has just failed."),
        ("low", "No family strong, but some evidence. Or 1 strong with distress.",
         "What we can see shows little to pay with."),
        ("unknown", "No evidence in any family, no distress and no account movement.",
         "Nothing visible: no account with us, or a dormant one."),
    ]:  # fmt: skip
        s.chip(1, st)
        s.text(2, rule, span=2, align=MID)
        s.text(4, meaning, span=2, align=MID)
        s.fit([(rule, s.width(2, 3)), (meaning, s.width(4, 5))])
        s.r += 1
    s.section("Families and levels")
    s.header(["Family", "Counts towards the state", "Evidence only", "No evidence", ""])
    s.ws.merge_cells(start_row=s.r - 1, start_column=4, end_row=s.r - 1, end_column=5)
    for name, levels in zip(FAMILIES, [("stable", "weak", "none")] + [("strong", "some", "none")] * 3):
        s.text(1, name, bold=True, align=MID)
        for col, lev in zip((2, 3, 4), levels):
            s.chip(col, lev, span=2 if col == 4 else 1, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.section("State map")
    s.header(["Strong families", "", "No distress", "Distress", ""])
    s.ws.merge_cells(start_row=s.r - 1, start_column=1, end_row=s.r - 1, end_column=2)
    s.ws.merge_cells(start_row=s.r - 1, start_column=4, end_row=s.r - 1, end_column=5)
    for label, calm, distressed in STATE_MAP:
        s.text(1, label, span=2, bold=True, align=MID)
        s.chip(3, calm, align=CENTER)
        s.chip(4, distressed, span=2, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.r += 1
    s.note("Rules: 'Logic'. Shares: 'Results'. What each state goes on to do: 'Validation'.")
    s.ws.freeze_panes = "A4"
    assert state(["stable", "strong", "none", "none"]) == "high"
    assert state(["stable", "strong", "strong", "none"], distress=True) == "moderate"
    assert state(["stable", "some", "none", "none"], distress=True) == "low"
    assert state(["none"] * 4, distress=True) == "low"
    assert state(["none"] * 4) == "unknown"


# --- logic ----------------------------------------------------------------------------------
TERMS = [
    ("Customer", "Every signal is read across all the customer's accounts with us, not only "
                 "the scored account."),
    ("Window", "The scoring month and the months before it: 3 months at 61–180 DPD, 6 at 180+. "
               "The prior window is the same number of months before that."),
    ("Anchor", "What the customer must pay now. Cards at 61–180 DPD: the amount in the oldest "
               "overdue bucket (up to 151–180 DPD) on the scoring month's statement. Loans: one "
               "monthly instalment. Cards at 180+ DPD, or when missing: no anchor, the flat "
               "floors apply."),
    ("Current and savings accounts", "The customer's accounts of the bank's 49 current and "
                                     "savings account types. Term deposits and loan accounts "
                                     "are not among them."),
    ("Salary of a month", "The larger of two figures. Internal: the salary credits to an "
                          "account with us in the month (an end-of-service payment is not "
                          "salary). Bureau: the salary reported by the credit bureau; a figure "
                          "counts in its own month and in the next month unless that month has "
                          "its own, and a figure of 0 (salary account closed) ends it."),
]  # fmt: skip
MOVEMENTS = [  # (movement, counts as, tone)
    ("Transfers in from other people or companies, remittances, salary-like credits not flagged "
     "as salary", "Money in", "good"),
    ("Cash deposits", "Money in", "good"),
    ("Transfers in from the customer's own account at another bank", "Money in", "good"),
    ("Card and ATM spend, bill payments, transfers to other people", "Money out", "good"),
    ("Transfers out to the customer's own account at another bank", "Money out", "good"),
    ("Salary credits", "F1 Income", "unknown"),
    ("Transfers between the customer's own accounts with us, auto-save", "Not counted", "unknown"),
    ("Reversals, refunds, returned cheques and direct debits, and the item they undo",
     "Not counted", "unknown"),
    ("Bank-initiated: sweeps, fees, interest, loan disbursements, recoveries",
     "Not counted", "unknown"),
    ("Payments to the customer's own card or loan with us (credibility), payments to other "
     "lenders, anything not positively identified", "Not counted", "unknown"),
]  # fmt: skip
PARAMETERS = [  # (parameter, value, why)
    ("Window", "3 months at 61–180 DPD, 6 at 180+ (scoring month included).",
     "Same as the other axes; activity is thinner at 180+."),
    ("Months needed", "2 of the 3 months, 3 of the 6 at 180+ (money in, money out, balance).",
     "Most months, not one."),
    ("Income: monthly floor", "max(AED 3,000, 2 × anchor).",
     "A salary that leaves room for the amount due."),
    ("Income: Stable", "Window salary of 2 monthly floors (3 at 180+), not more than 25% below "
                       "the prior window.",
     "The total, not the months: an employer may pay early. A falling salary is not stable."),
    ("Income: smallest salary", "AED 1,000 in a month.", "Below it is not evidence of income."),
    ("Bureau salary: carried", "1 month.", "Bureau figures arrive on a change, not monthly."),
    ("Money in / out: Strong", "max(AED 1,000, 1 × anchor) a month.",
     "Covers what is due."),
    ("Money in / out: Some", "AED 1,000 in / AED 500 out in any month.",
     "The account is in use."),
    ("Balance held", "Average balance of max(AED 3,000, 1 × anchor) a month, not more than 50% "
                     "below the prior window.", "Money that stays, not money passing through."),
    ("Other products: assets", "max(AED 10,000, 3 × anchor).", "A real cushion."),
    ("Other products: credit", "Current, with an instalment or minimum due of max(AED 1,000, "
                               "1 × anchor).", "The customer is paying another product on time."),
    ("Netting", "Opposite movement of the same amount (±1%) within 3 days.",
     "A round trip is not money in or out."),
    ("Distress", "1 event in the window.", "A failed payment is recent and direct."),
    ("No account", "No movement and no positive balance in 12 months.",
     "Separates no account from a dormant one."),
]  # fmt: skip
OTHER_COLUMNS = [
    ("Reason", "The distress, or else the first strong family."),
    ("Why Unknown", "No account: no movement and no positive balance on a current or savings "
                    "account in 12 months. Dormant account: otherwise."),
    ("Money held", "The balance rule of F2 holds at the scoring date: a delinquent customer "
                   "holding money above the floor."),
    ("Salary source", "Who shows a salary of AED 1,000 or more in the window: internal, bureau, "
                      "both or none."),
    ("Salary stopped", "Internal salary in the prior window, none in the window."),
    ("End of service", "A collector note of an end-of-service payment expected or received in "
                       "the window."),
    ("Inputs", "The four levels, the anchor and the distress flag."),
]  # fmt: skip


def logic(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Logic"), [24, 56, 16, 26])

    def flow_(title: str, steps: list[tuple[str, str]], label=LABEL.get) -> None:
        s.section(title)
        for i, (rule, key) in enumerate(steps, 1):
            s.text(1, f"Rule {i}", bold=True, color=NAVY, fill=PANEL, align=CENTER)
            s.text(2, rule, span=2, fill=PANEL, align=MID)
            s.chip(4, key, label(key))
            s.fit([(rule, s.width(2, 3))], floor=22)
            s.r += 1

    def table(rows: list[tuple[str, str]]) -> None:
        for name, text in rows:
            s.text(1, name, bold=True)
            s.text(2, text, span=3)
            s.fit([(text, s.width(2, 4)), (name, s.widths[0])])
            s.r += 1

    s.title("Logic", "What the model computes for each account at the scoring date, and the "
                     "rules that turn it into a state. Within a family, the first rule that "
                     "holds decides.")  # fmt: skip
    s.section("Terms", gap=0)
    table(TERMS)
    flow_("F1 Income", [
        ("The salary received in the window is at least 2 monthly floors (3 at 180+), the floor "
         "being max(AED 3,000, 2 × anchor); and it is not more than 25% below the prior window. "
         "The fall compares the window totals. When neither window has an internal salary, it "
         "compares the average of the months that have a figure.", "stable"),
        ("A salary of AED 1,000 or more in any month of the window.", "weak"),
        ("Otherwise.", "none"),
    ])  # fmt: skip
    flow_("F2 Money in or held", [
        ("Money in of max(AED 1,000, 1 × anchor) or more in 2 of the 3 months (3 of the 6 at "
         "180+). Or balance held: an average balance on the current and savings accounts of "
         "max(AED 3,000, 1 × anchor) or more in as many months, with the window average not "
         "more than 50% below the prior window's.", "strong"),
        ("Money in of AED 1,000 or more in any month of the window.", "some"),
        ("Otherwise. A balance below the rule above is not evidence.", "none"),
    ])  # fmt: skip
    flow_("F3 Money out", [
        ("Money out of max(AED 1,000, 1 × anchor) or more in 2 of the 3 months (3 of the 6 at "
         "180+).", "strong"),
        ("Money out of AED 500 or more in any month of the window.", "some"),
        ("Otherwise.", "none"),
    ])  # fmt: skip
    s.section("F2 and F3: which movements on the current and savings accounts count")
    for movement, counts_as, tone in MOVEMENTS:
        s.text(1, movement, span=3, align=MID)
        s.chip(4, tone, counts_as)
        s.fit([(movement, s.width(1, 3))])
        s.r += 1
    s.note("A movement mirrored by an opposite movement of the same amount (±1%) within 3 days, "
           "on any of the customer's accounts, is dropped together with its mirror.")  # fmt: skip
    flow_("F4 Other products (at the end of the scoring month, the scored account left out)", [
        ("Deposits, investments and wealth assets of max(AED 10,000, 3 × anchor) or more. Or "
         "another card or loan with us that is current, with an instalment or minimum due of "
         "max(AED 1,000, 1 × anchor) or more.", "strong"),
        ("Any other card or loan with us that is current, or any such asset above 0.", "some"),
        ("Otherwise.", "none"),
    ])  # fmt: skip
    flow_("Distress", [
        ("In the window: a returned cheque or a returned direct debit on the customer's current "
         "and savings accounts, or a bounced cheque reported by the credit bureau (dated by its "
         "return date; several on one day are one).", "distress"),
    ], label=lambda _: "One level down")  # fmt: skip
    flow_("State", [
        ("No evidence in any family (all four None), no distress, and no counted movement on a "
         "current or savings account in the window.", "unknown"),
        ("2 or more families Strong (income: Stable), and no distress.", "high"),
        ("1 family Strong and no distress; or 2 or more with distress.", "moderate"),
        ("Otherwise.", "low"),
    ])  # fmt: skip
    s.section("Parameters")
    s.header(["Parameter", "Value", "Why"], [1, 2, 1])
    for p, v, why in PARAMETERS:
        s.text(1, p, bold=True)
        s.text(2, v, span=2)
        s.text(4, why, color=MUTED)
        s.fit([(v, s.width(2, 3)), (why, s.widths[3])])
        s.r += 1
    s.section("Other output columns (not in the state)")
    table(OTHER_COLUMNS)
    s.ws.freeze_panes = "A4"


# --- examples -------------------------------------------------------------------------------
GRID = 2 * W  # months per example row: the prior window and the window
N = None
INCOME_EXAMPLES = [  # (level, internal, bureau, anchor, why)
    ("stable", [8000] * 6, [N] * 6, 0, "Salary every month."),
    ("stable", [8000, 8000, 8000, 16000, N, 8000], [N] * 6, 0,
     "Employer paid early: two salaries in one month. The window total counts."),
    ("stable", [8000, 8000, 8000, N, N, N], [N, N, N, 8000, N, 8000], 0,
     "Salary moved to another bank; the bureau still reports it."),
    ("stable", [N] * 6, [N, 9000, N, N, 9000, N], 0,
     "Bureau only: each figure counts in its month and the next."),
    ("weak", [N] * 6, [N, 9000, N, N, 5000, N], 0,
     "Bureau salary fell from 9,000 to 5,000: more than 25%."),
    ("weak", [8000, 8000, 8000, 8000, N, N], [N] * 6, 0,
     "Salary stopped: the window total is far below the prior window."),
    ("weak", [5000] * 6, [N] * 6, 4000,
     "Anchor 4,000: floor 8,000 a month, 16,000 needed, 15,000 received."),
    ("weak", [N, N, N, N, 2500, N], [N] * 6, 0, "Some salary, under two floors of 3,000."),
    ("none", [N] * 6, [N] * 6, 0, "No salary of 1,000 or more."),
]  # fmt: skip
MONEY_IN_EXAMPLES = [  # (level, money in per month of the window, anchor, why)
    ("strong", [2000, 0, 1500], 0, "1,000 or more in 2 of the 3 months."),
    ("some", [0, 5000, 300], 0, "Only one month of 1,000 or more."),
    ("some", [2000, 2600, 1500], 2500, "Anchor 2,500: one month reaches it."),
    ("none", [200, 0, 400], 0, "Movement, never 1,000 in a month."),
]  # fmt: skip
BALANCE_EXAMPLES = [  # (held, average balance per month, why)
    (True, [4000, 4000, 4000, 3500, 500, 3200], "3,000 or more in 2 of the 3 months; holding."),
    (False, [20000, 20000, 20000, 3500, 3200, 3100],
     "Above the floor, but more than 50% below the prior window: draining."),
    (False, [N, N, N, 5000, 0, 0], "Above the floor in one month only."),
]  # fmt: skip
PRODUCT_EXAMPLES = [  # (level, assets, another credit product current, its instalment, why)
    ("strong", 25000, False, 0, "Term deposit of 25,000."),
    ("strong", 0, True, 1200, "Another card kept current, minimum due 1,200."),
    ("some", 0, True, 600, "Another loan kept current, instalment under 1,000."),
    ("some", 2000, False, 0, "A small investment."),
    ("none", 0, False, 0, "No other product, or none that is current."),
]  # fmt: skip
STATE_EXAMPLES = [  # (state, F1, F2, F3, F4, distress, counted movement, why)
    ("high", "stable", "strong", "none", "none", False, True, "Salary and regular money in."),
    ("moderate", "stable", "some", "some", "none", False, True, "One family strong."),
    ("moderate", "stable", "strong", "none", "none", True, True,
     "Two strong, one level down for a returned cheque."),
    ("low", "weak", "none", "none", "some", False, False, "Evidence, nothing strong."),
    ("low", "stable", "none", "none", "none", True, False, "One strong, one level down."),
    ("low", "none", "none", "none", "none", False, True,
     "Uses the account, amounts too small for any level."),
    ("low", "none", "none", "none", "none", True, False, "A returned cheque is evidence."),
    ("unknown", "none", "none", "none", "none", False, False,
     "No salary, no movement, no other product."),
]  # fmt: skip


def _check(got, want, text: str) -> None:
    if got != want:
        raise SystemExit(f"example '{text}' gives {got}, expected {want}")


def examples(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Examples"), [16] + [10] * GRID + [60])
    why = GRID + 2
    months = [("Now" if k == 0 else str(k)) for k in range(1 - GRID, 1)]
    s.title("Examples (61–180 DPD, 3-month window)",
            "One customer per row, amounts in AED per month, oldest on the left. Blue columns "
            "are the window; the three before it are the prior window.")  # fmt: skip

    def grid(head: str, rows: list[tuple[str, str, list, str]]) -> None:
        """Rows of (tone key, chip label, GRID monthly amounts, why)."""
        s.header([head, *months, "Why"])
        for k in range(W, GRID):
            s.ws.cell(row=s.r - 1, column=2 + k).fill = _fill(WINDOW_HEAD)
        for key, label, cells, text in rows:
            s.chip(1, key, label)
            for k, v in enumerate(cells):
                s.text(2 + k, v, align=CENTER, fmt="#,##0", fill=WINDOW_FILL if k >= W else None)
            s.text(why, text, align=MID)
            s.ws.row_dimensions[s.r].height = 20
            s.r += 1

    s.section("F1 Income: salary of each month", gap=0)
    rows = []
    for want, internal, bureau, anchor, text in INCOME_EXAMPLES:
        _check(income(internal, bureau, anchor), want, text)
        rows.append((want, LABEL[want], salary_months(internal, bureau), text))
    grid("Level", rows)
    s.note("Each cell is the salary of the month: the larger of the internal and the bureau "
           "figure, a bureau figure carried one month.")  # fmt: skip

    s.section("F2 Money in")
    rows = []
    for want, cells, anchor, text in MONEY_IN_EXAMPLES:
        _check(flow([N] * W + cells, MONEY_IN_SOME, anchor), want, text)
        rows.append((want, LABEL[want], [N] * W + cells, text))
    grid("Level", rows)
    s.note("Money out reads the same way, with AED 500 in any month for Some.")

    s.section("F2 Balance held: average balance of each month")
    rows = []
    for want, cells, text in BALANCE_EXAMPLES:
        _check(balance_held(cells), want, text)
        rows.append(("strong" if want else "none", "Strong" if want else "Not evidence", cells, text))
    grid("Level", rows)

    def cases(head: list[str], spans: list[int]) -> None:
        s.header([*head, "Why"], [1, *spans, 1], height=30)

    s.section("F4 Other products")
    cases(["Level", "Assets", "Another card or loan, current", "Its instalment"], [2, 2, 2])
    for want, assets, current, instalment, text in PRODUCT_EXAMPLES:
        _check(other_products(assets, current, instalment), want, text)
        s.chip(1, want)
        s.text(2, assets or "–", span=2, align=CENTER, fmt="#,##0")
        s.text(4, "Yes" if current else "–", span=2, align=CENTER)
        s.text(6, instalment or "–", span=2, align=CENTER, fmt="#,##0")
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("State")
    s.header(["State", "F1\nIncome", "F2\nMoney in", "F3\nMoney out", "F4 Other\nproducts",
              "Distress", "Account\nmovement", "Why"], height=30)  # fmt: skip
    for want, f1, f2, f3, f4, distress, movement, text in STATE_EXAMPLES:
        _check(state([f1, f2, f3, f4], distress, movement), want, text)
        s.chip(1, want)
        for col, lev in enumerate((f1, f2, f3, f4), 2):
            s.chip(col, lev, align=CENTER)
        s.chip(6, "distress", "Yes", align=CENTER) if distress else s.text(6, "–", align=CENTER)
        s.text(7, "Yes" if movement else "–", align=CENTER)
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.ws.freeze_panes = "B4"


# --- results --------------------------------------------------------------------------------
RESULTS_DATE = "31 Aug 2026"
PRODUCTS = ["Personal Loans", "Personal Cash Loans", "Auto"]
VARIANTS = (["CC\n61–180", "CC\n180+"]
            + [f"RL 61–180\n{p}" for p in PRODUCTS] + ["RL 61–180\ntotal"]
            + [f"RL 180+\n{p}" for p in PRODUCTS] + ["RL 180+\ntotal"])  # fmt: skip
SEGMENTS = ["CC\n61–180", "CC\n180+", "RL\n61–180", "RL\n180+"]
VINTAGES = [f"{prod}\n{v}" for prod in ("CC 180+", "RL 180+")
            for v in ("early-stage\ncharge-off", "late-stage\ncharge-off")]  # fmt: skip
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
# Production run, month end 31 Aug 2026; counts in STATES order. Splits not run yet are blank.
ACCOUNTS = {0: 19292, 1: 318663, 2: 1397, 3: 1224, 4: 1364, 5: 3985, 6: 33862, 7: 10306,
            8: 11203, 9: 55371}  # fmt: skip
STATE_COUNTS = {0: [312, 2681, 5263, 11036], 1: [845, 19268, 27470, 271080],
                5: [47, 351, 1965, 1622], 9: [66, 1914, 6115, 47276]}  # fmt: skip
SEGMENT_ACCOUNTS = [19292, 318663, 3985, 55371]
_LEVELS3 = [("Strong", "strong"), ("Some", "some"), ("None", "none")]
DETAIL = [  # (section, [(label, tone key)], {segment: counts in row order})
    ("F1 Income", [("Stable", "stable"), ("Weak", "weak"), ("None", "none")],
     {0: [2801, 2367, 14124], 1: [20906, 11056, 286701],
      2: [370, 400, 3215], 3: [2000, 1354, 52017]}),
    ("F2 Money in or held", _LEVELS3,
     {0: [378, 659, 18255], 1: [1221, 925, 316517], 2: [88, 380, 3517], 3: [296, 390, 54685]}),
    ("F3 Money out", _LEVELS3,
     {0: [303, 606, 18383], 1: [835, 692, 317136], 2: [50, 275, 3660], 3: [76, 211, 55084]}),
    ("F4 Other products", _LEVELS3,
     {0: [368, 1071, 17853], 1: [618, 9075, 308970], 2: [63, 951, 2971], 3: [47, 3437, 51887]}),
    ("Distress and money held",
     [("Distress in the window", "distress"), ("Money held at the scoring date", "strong")],
     {0: [1795, 146], 1: [9094, 588], 2: [760, 48], 3: [2085, 257]}),
    ("Why Unknown", [("No account with us", "unknown"), ("Dormant account", "unknown")],
     {0: [4656, 6527], 1: [235821, 35594], 2: [430, 1203], 3: [36853, 10456]}),
]  # fmt: skip
ENTRY = {"color": "0000FF", "fill": INPUT_FILL}


def _pair(s: Sheet, col: int, count, base: str) -> None:
    """An entered count (blank until run) and its share of cell ``base``."""
    L = get_column_letter(col)
    s.text(col, count, fmt="#,##0", **ENTRY)
    s.text(col + 1, f'=IF(OR({L}{s.r}="",N({base})=0),"",{L}{s.r}/{base})', color=MUTED,
           fmt="0.0%")  # fmt: skip


def _state_table(s: Sheet, cols: list[str], accounts: dict, counts: dict) -> None:
    """States x columns (count + share), Total, Accounts in scope and Coverage."""
    s.header(["State"] + [x for name in cols for x in (name, "share")], height=58)
    first, total = s.r, s.r + len(STATES)
    for i, st in enumerate(STATES):
        s.chip(1, st)
        for b in range(len(cols)):
            L = get_column_letter(2 + 2 * b)
            _pair(s, 2 + 2 * b, counts[b][i] if b in counts else None, f"{L}${total}")
        s.r += 1
    for label, bold in (("Total", True), ("Accounts in scope", False), ("Coverage", True)):
        s.text(1, label, bold=bold)
        for b in range(len(cols)):
            col = 2 + 2 * b
            L = get_column_letter(col)
            rng = f"{L}{first}:{L}{total - 1}"
            if label == "Accounts in scope":
                s.text(col, accounts.get(b), fmt="#,##0", **ENTRY)
            elif label == "Total":
                s.text(col, f'=IF(COUNT({rng})=0,"",SUM({rng}))', bold=True, fmt="#,##0")
            else:
                s.text(col, f'=IF(N({L}{total + 1})*COUNT({rng})=0,"",{L}{total}/{L}{total + 1})',
                       bold=True, fmt="0.0%")  # fmt: skip
            s.text(col + 1, None)
        s.r += 1


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [16] + [11, 7] * len(VARIANTS))
    s.title("Results", f"Accounts per state and model variant, {RESULTS_DATE} (production run). "
                       "Pale yellow = from the run, blank until that split has run; shares and "
                       "totals are calculated.")  # fmt: skip
    s.section("Ability state", gap=0)
    _state_table(s, VARIANTS, ACCOUNTS, STATE_COUNTS)
    s.r += 1
    s.note("Aggregates only.")
    s.ws.freeze_panes = "B6"


def detail(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results detail"), [40] + [11, 7] * len(SEGMENTS))
    s.title("Results detail", f"What sits behind the states, {RESULTS_DATE}. Shares are of all "
                              "accounts in the segment.")  # fmt: skip
    s.header([""] + [x for name in SEGMENTS for x in (name, "share")], height=30)
    s.text(1, "Accounts", bold=True)
    base = s.r
    for b, n in enumerate(SEGMENT_ACCOUNTS):
        s.text(2 + 2 * b, n, fmt="#,##0", **ENTRY)
        s.text(3 + 2 * b, None)
    s.r += 1
    for title, labels, data in DETAIL:
        s.section(title)
        for i, (label, tone) in enumerate(labels):
            s.chip(1, tone, label)
            for b in range(len(SEGMENTS)):
                _pair(s, 2 + 2 * b, data[b][i], f"{get_column_letter(2 + 2 * b)}${base}")
            s.r += 1
    s.r += 1
    s.note("None includes customers with no current or savings account. Why Unknown is from "
           "the run before the latest bureau salary source, when Unknown was 147 (cards 61–180), "
           "335 (cards 180+), 11 and 33 (loans) accounts higher.")  # fmt: skip
    s.ws.freeze_panes = "B6"


def trend(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results trend"), [10, 10] + [10, 7] * len(STATES))
    s.title("Results trend", "Accounts per state by month, Jan–Aug 2026 (month ends). Shares are "
                             "of the month's accounts.")  # fmt: skip
    for i, title in enumerate(["Credit cards 61–180", "Retail loans 61–180", "Credit cards 180+",
                               "Retail loans 180+"]):  # fmt: skip
        s.section(title, gap=0 if i == 0 else 1)
        s.text(1, "Month", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.text(2, "Accounts", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, st in enumerate(STATES):
            s.chip(3 + 2 * j, st, span=2, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
        for month in MONTHS:
            cells = "+".join(f"N({get_column_letter(3 + 2 * j)}{s.r})" for j in range(len(STATES)))
            s.text(1, f"{month} 2026", bold=True)
            s.text(2, f'=IF(({cells})=0,"",{cells})', bold=True, fmt="#,##0")
            for j in range(len(STATES)):
                _pair(s, 3 + 2 * j, None, f"$B{s.r}")
            s.r += 1
    s.ws.freeze_panes = "A4"


def vintage(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results 180+ vintage"), [16] + [12, 7] * len(VINTAGES))
    s.title("Results 180+ by vintage",
            "Early-stage charge-off = charged off less than 2 years ago; late-stage = 2 years or "
            f"more; {RESULTS_DATE}. Shares are within each vintage.")  # fmt: skip
    s.section("Ability state", gap=0)
    _state_table(s, VINTAGES, {}, {})
    s.ws.freeze_panes = "B6"


# --- validation -----------------------------------------------------------------------------
# Month ends Jan–May 2026 pooled, 61–180 DPD, outcomes over the next 3 months (%).
OUTCOMES = {  # book: [(state, accounts, cured, paid, rolled)]
    "Credit cards 61–180": [("high", 2045, 31.3, 58.5, 52.8), ("moderate", 13945, 15.9, 41.3, 73.2),
                            ("low", 18670, 10.9, 29.1, 82.3), ("unknown", 39596, 7.8, 19.9, 87.5)],
    "Retail loans 61–180": [("high", 124, 27.6, 75.2, 59.0), ("moderate", 1423, 15.4, 64.8, 68.9),
                            ("low", 6163, 9.9, 44.7, 82.0), ("unknown", 4802, 8.6, 36.4, 85.3)],
}  # fmt: skip
GAPS = [  # book, gap, cured, paid, rolled: percentage points [95% interval]
    ("Credit cards 61–180", "High − Moderate", "+14.7 [12.0, 17.3]", "+16.3 [13.0, 19.5]",
     "−19.6 [−22.9, −16.3]"),
    ("Credit cards 61–180", "Moderate − Low", "+5.1 [4.2, 6.0]", "+12.4 [11.1, 13.8]",
     "−9.3 [−10.5, −8.1]"),
    ("Retail loans 61–180", "High − Moderate", "+10.9 [−2.5, 24.3]", "+9.1 [−1.7, 19.8]",
     "−8.6 [−23.4, 6.1]"),
    ("Retail loans 61–180", "Moderate − Low", "+5.8 [3.3, 8.3]", "+20.4 [16.4, 24.3]",
     "−13.3 [−16.9, −9.6]"),
]  # fmt: skip


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [24, 20, 22, 22, 22])
    s.title("Validation", "What each state goes on to do at 61–180 DPD: month ends January to May "
                          "2026, outcomes over the following 3 months. Cured = back to current; "
                          "paid = any payment; rolled = a worse DPD bucket.")  # fmt: skip
    for i, (book, rows) in enumerate(OUTCOMES.items()):
        s.section(f"Outcome by state, {book.lower()}", gap=0 if i == 0 else 1)
        s.header(["State", "Account-months", "Cured", "Paid", "Rolled"])
        for st, n, *rates in rows:
            s.chip(1, st)
            s.text(2, n, align=MID, fmt="#,##0")
            for col, v in enumerate(rates, 3):
                s.text(col, v / 100, align=MID, fmt="0.0%")
            s.r += 1
    s.section("Gap between neighbouring states (percentage points, same DPD-band mix)")
    s.header(["Book", "Gap", "Cured", "Paid", "Rolled"])
    for row in GAPS:
        s.row(list(row), align=MID)
    s.note("Every state cures and pays more, and rolls less, than the one below it. On loans "
           "High has 124 account-months, so its gap to Moderate is not significant. 180+ has "
           "no outcome test.")  # fmt: skip
    s.ws.freeze_panes = "A4"


def build(out: pathlib.Path) -> pathlib.Path:
    wb = Workbook()
    overview(wb)
    logic(wb)
    examples(wb)
    results(wb)
    detail(wb)
    trend(wb)
    vintage(wb)
    validation(wb)
    wb.calculation.fullCalcOnLoad = True
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--out", default=str(pathlib.Path(__file__).with_name("a1_ability_reference.xlsx"))
    )
    print(build(pathlib.Path(ap.parse_args().out)))


if __name__ == "__main__":
    main()
