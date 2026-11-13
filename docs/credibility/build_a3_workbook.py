"""Build the A3 payment credibility model document (business-facing).

    python build_a3_workbook.py [--out a3_credibility_reference.xlsx]

The rules follow ``workplace_mirror/specs/A3_credibility_spec.md``. Every worked example and
every cell of the state map is run through the reference rules below and the build FAILS if an
example no longer gets the level or state it illustrates. Results are entry cells (pale yellow)
holding production numbers; shares of entered counts and totals are formulas.

Design: one colour meaning everywhere — green favourable, amber in between, red adverse, grey
no evidence; navy is structure only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# --- rules (reference implementation) -------------------------------------------------------
S61, S180 = "61–180 DPD", "180+ DPD"
CARD, LOAN = "Card", "Loan"
HIGH_FROM, MODERATE_FROM = 4, 2
POINTS = {
    "kept": 2, "partly": 1, "thin": 0, "broken": -1,
    "regular": 2, "some": 1, "none": 0,
    "clean": 1, "not_clean": 0, "no_record": 0,
}  # fmt: skip
A_LEVELS = ["kept", "partly", "thin", "broken"]
B_LEVELS = ["regular", "some", "none"]
C_LEVELS = ["clean", "not_clean", "no_record"]
MIN_AED = 100  # smallest payment that counts as a payment
MIN_CONCLUDED, KEPT_RATE, BROKEN_RATE, BROKEN_STREAK = 2, 0.80, 0.40, 3
NOTE_RUN_DAYS = 7  # notes at most this far apart are one promise; a plan absorbs a note this near
WINDOW = {S61: 3, S180: 6}  # months of payments in delinquency
REGULAR_FROM = {S61: 2, S180: 3}  # months with a qualifying payment
SOME_WINDOW = {S61: 3, S180: 12}
RECORD_MONTHS, RECORD_MIN_DUE, CLEAN_SHARE = 12, 3, 0.80
KEPT, NOT_KEPT, PENDING = "K", "X", "P"  # one promise
QUALIFYING, SMALL, NOTHING, BEFORE = "Q", "s", "–", " "  # one month of the delinquency
AS_BILLED, MISSED, NO_DUE = "✓", "✗", "·"  # one month before the delinquency


def promises(history: str) -> str:
    """Level A from the promises of the last 12 months, oldest first (pending ones ignored)."""
    done = [p == KEPT for p in history if p != PENDING]
    n, kept = len(done), sum(done)
    if (n >= BROKEN_STREAK and not any(done[-BROKEN_STREAK:])) or (
        n >= MIN_CONCLUDED and kept / n < BROKEN_RATE
    ):
        return "broken"
    if n >= MIN_CONCLUDED and kept / n >= KEPT_RATE:
        return "kept"
    return "partly" if kept else "thin"


def payments(months: str, seg: str) -> str:
    """Level B from the months of the delinquency, oldest first, the scoring month last."""
    if months[-WINDOW[seg] :].count(QUALIFYING) >= REGULAR_FROM[seg]:
        return "regular"
    paid = any(m in (QUALIFYING, SMALL) for m in months[-SOME_WINDOW[seg] :])
    return "some" if paid else "none"


def record(months: str, reaches: bool = True) -> str:
    """Level C from the 12 months before the delinquency; ``reaches`` = the history we hold
    goes back to the start of the delinquency."""
    due = [m == AS_BILLED for m in months if m != NO_DUE]
    if not reaches or len(due) < RECORD_MIN_DUE:
        return "no_record"
    return "clean" if sum(due) / len(due) >= CLEAN_SHARE else "not_clean"


def state(a: str, b: str, c: str, refusal: bool = False, episode: bool = True) -> str:
    if not episode:
        return "unknown"
    pts = POINTS[a] + POINTS[b] + POINTS[c]
    if pts >= HIGH_FROM:
        return "moderate" if refusal else "high"
    return "moderate" if pts >= MODERATE_FROM and not refusal else "low"


def month_end(day: dt.date) -> dt.date:
    return (day.replace(day=1) + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)


def deadline(product: str, seg: str, day: dt.date, statement: dt.date | None = None) -> dt.date:
    """The last day a payment still counts for a promise made on ``day``."""
    if product == CARD and seg == S61:
        return statement or day + dt.timedelta(days=31)
    return month_end(day)


def outcome(product, seg, day, due, pays, statement=None) -> str:
    """One promise judged by the payments ``[(date, amount)]`` that followed it."""
    start = day.replace(day=1) - dt.timedelta(days=1) if product == LOAN else day
    end = deadline(product, seg, day, statement)
    paid = sum(amount for d, amount in pays if start < d <= end)
    return "paid" if paid >= max(due, MIN_AED) else "partial" if paid >= MIN_AED else "unpaid"


def promise_days(notes: list[dt.date], plans: list[dt.date], cutoff) -> list[dt.date]:
    """The promises (dated) that collector notes and plans amount to."""
    runs, prev = [], None
    for d in sorted(notes):
        if not runs or (d - prev).days > NOTE_RUN_DAYS or d > cutoff(runs[-1]):
            runs.append(d)
        prev = d
    for plan in sorted(plans):
        near = [r for r in runs if abs((r - plan).days) <= NOTE_RUN_DAYS]
        if near:
            runs.remove(min(near, key=lambda r: abs((r - plan).days)))
    return sorted([*plans, *runs])


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
    "high": "good", "moderate": "mid", "low": "bad", "unknown": "unknown",
    "kept": "good", "partly": "mid", "thin": "unknown", "broken": "bad",
    "regular": "good", "some": "mid", "none": "bad",
    "clean": "good", "not_clean": "bad", "no_record": "unknown",
    "paid": "good", "partial": "bad", "unpaid": "bad", "refusal": "bad",
}  # fmt: skip
LABEL = {
    "high": "High", "moderate": "Moderate", "low": "Low", "unknown": "Unknown",
    "kept": "Kept", "partly": "Partly kept", "thin": "Thin", "broken": "Broken",
    "regular": "Regular", "some": "Some", "none": "None",
    "clean": "Clean", "not_clean": "Not clean", "no_record": "No record",
    "paid": "Kept", "partial": "Not kept (partial)", "unpaid": "Not kept", "refusal": "Refusal",
}  # fmt: skip
CODE_TONE = {KEPT: "good", NOT_KEPT: "bad", PENDING: "unknown", QUALIFYING: "good",
             SMALL: "mid", NOTHING: "bad", AS_BILLED: "good", MISSED: "bad"}  # fmt: skip
STATES = ["high", "moderate", "low", "unknown"]
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


def _points(level: str) -> str:
    return f"{LABEL[level]}  {POINTS[level]:+d}".replace("-", "−").replace("+0", "0")


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
def overview(wb: Workbook) -> None:
    s = Sheet(wb.active, [24, 24, 24, 24, 24])
    s.ws.title = "Overview"
    s.title(
        "A3 Payment Credibility",
        "How far can we believe this customer will pay this debt? Three scored dimensions and a "
        "refusal override; every account in scope gets exactly one state.",
    )
    for k, v in [
        ("Scope", "Credit cards and retail loans (Personal Loans, Personal Cash Loans, Auto) at "
                  "61–180 DPD and 180+ DPD, scored at each month end."),
        ("A. Promises", "Does the customer do what they commit to? Promises of the last 12 "
                        "months, each judged by the payments that followed it."),
        ("B. Payments", "Is money coming in now? Payments in the recent months of the current "
                        "delinquency."),
        ("C. Record", "Did they pay as billed before? The 12 months before the delinquency "
                      "started."),
        ("Refusal", "An explicit refusal to pay, with nothing after it, takes the state one "
                    "level down."),
        ("Principle", "The evidence is that of the scored account only: credibility is about "
                      "this debt. Add the points of the three dimensions."),
        ("Read with", "Ability: no payment can mean inability, not unwillingness."),
    ]:  # fmt: skip
        s.text(1, k, bold=True, color=NAVY, border=False)
        s.text(2, v, span=4, border=False)
        s.fit([(v, s.width(2, 5))], floor=18)
        s.r += 1
    s.section("States")
    s.header(["State", "Rule", "Meaning"], [1, 2, 2])
    for st, rule, meaning in [
        ("high", "4 points or more, no refusal.",
         "Keeps promises and money is coming in."),
        ("moderate", "2 or 3 points, no refusal. Or 4 or more with a refusal.",
         "Some evidence to rely on, not yet consistent; or a strong record with a fresh refusal."),
        ("low", "Fewer than 2 points. Or fewer than 4 with a refusal.",
         "Little or nothing positive on record, or it is outweighed by broken promises or a "
         "refusal."),
        ("unknown", "No delinquency can be observed for the account.", "Nothing to judge on."),
    ]:  # fmt: skip
        s.chip(1, st)
        s.text(2, rule, span=2, align=MID)
        s.text(4, meaning, span=2, align=MID)
        s.fit([(rule, s.width(2, 3)), (meaning, s.width(4, 5))])
        s.r += 1
    s.section("Dimensions and points")
    s.header(["Dimension", "Levels", "", "", ""])
    s.ws.merge_cells(start_row=s.r - 1, start_column=2, end_row=s.r - 1, end_column=5)
    for name, levels in [("A. Promises kept", A_LEVELS), ("B. Payments in delinquency", B_LEVELS),
                         ("C. Record before delinquency", C_LEVELS)]:  # fmt: skip
        s.text(1, name, bold=True, align=MID)
        for col in range(2, 6):
            lev = levels[col - 2] if col - 2 < len(levels) else None
            s.chip(col, lev, _points(lev), align=CENTER) if lev else s.text(col, None)
        s.ws.row_dimensions[s.r].height = 30
        s.r += 1
    s.r += 1
    s.note("Rules: 'Logic'. Every combination of levels: 'State map'. Shares: 'Results'. "
           "What each state goes on to pay: 'Validation'.")  # fmt: skip
    s.ws.freeze_panes = "A4"


# --- logic ----------------------------------------------------------------------------------
EVIDENCE = [  # (event, counts as, tone, dimension)
    ("Promise-to-pay or settlement plan recorded in the collections system, not cancelled",
     "Promise", "good", "A"),
    ("Collector note of a promise: promise to pay (full, partial or scheduled), digital collect "
     "subscribed, will pay at salary",
     "Promise", "good", "A"),
    ("Card: a payment posted to the card account, by its posting date. Loan: the payments "
     "received on the loan in a month (known by month, not by day)",
     "Payment", "good", "A, B, C"),
    ("Card: a statement with an amount due. Loan: a month with an instalment due",
     "Month with an amount due", "unknown", "B, C"),
    ("The latest conversation with the customer ended in a refusal: refuse to pay, rewrite not "
     "agreed",
     "Refusal", "bad", "Override"),
]  # fmt: skip
TERMS = [
    ("Delinquency", "The current continuous run of months at 1+ DPD; a return to 0 DPD ends "
                    "it. It starts on the first day of its first month."),
    ("Month", "Card: a statement cycle, from one statement to the next. Loan: a calendar month."),
    ("One month's due", "Card: the oldest unpaid monthly amount on the statement, or the minimum "
                        "due when nothing is overdue. Once the whole overdue amount is "
                        "accumulated at 210+ DPD: the average minimum due of the last 12 months "
                        "that had one. Loan: the monthly instalment, the last known one when the "
                        "month has none."),
    ("Qualifying payment", "The payments of a month reach one month's due and at least 100 AED."),
    ("Paid as billed", "The payments of a month reach the amount due, before the next statement "
                       "(loans: within the month). Paying the minimum counts, whatever its size."),
    ("Conversation", "A contact in which the account holder was reached in person."),
]  # fmt: skip
PROMISE_RULES = [
    ("One promise", "Every plan is one promise, dated at its start. A collector note is the "
                    "same promise as the note before it when it comes at most 7 days later and "
                    "not after that promise's deadline; otherwise it is a new promise, dated at "
                    "its first note. A plan absorbs the nearest note-promise within 7 days."),
    ("Window", "Promises dated in the 12 months up to the scoring date, earlier delinquencies "
               "included."),
    ("Deadline", "Fixed, whatever date was promised. Cards at 61–180 DPD: the next statement "
                 "after the promise day (31 days when there is none yet). Loans, and every "
                 "account at 180+ DPD: the last day of the month of the promise. A payment on "
                 "the deadline day counts."),
    ("Kept", "The payments after the promise day, up to the deadline, reach one month's due as "
             "of the promise day (at least 100 AED). Less is not kept, a partial payment "
             "included. Loans: the payments of the promise month count in full."),
    ("Concluded", "The deadline is on or before the scoring date. Pending promises are not "
                  "counted."),
]  # fmt: skip
PARAMETERS = [  # (parameter, value, why)
    ("Promises: window", "12 months, earlier delinquencies included.",
     "Trust is a track record."),
    ("Promises: deadline", "Cards at 61–180: next statement. Loans and 180+: end of the promise "
                           "month.", "Set by GRR; one rule whatever date was promised."),
    ("Promises: amount to pay", "One month's due, at least 100 AED.",
     "What a customer can be asked for in a month; a token payment keeps no promise."),
    ("Promises: notes joined", "At most 7 days apart and within the deadline.",
     "Repeated notes on one promise; a note after the deadline is a new promise."),
    ("Promises: concluded needed", "2, for Kept and for Broken by share.",
     "One promise is not a pattern."),
    ("Promises: Kept / Broken", "Kept from 80% kept. Broken under 40% kept, or the last 3 all "
                                "not kept.", "A clear record either way; in between is Partly "
                                             "kept."),
    ("Payments: window", "3 months at 61–180 DPD, 6 at 180+ (scoring month included).",
     "Same as the other axes; activity is thinner at 180+."),
    ("Payments: Regular", "A qualifying payment in 2 of the 3 months, 3 of the 6 at 180+.",
     "Most months paid; one payment is not a habit."),
    ("Payments: Some", "100 AED or more in a month of the last 3 months, 12 at 180+.",
     "At 180+ any payment in a year is a signal."),
    ("Record: window", "The 12 months before the delinquency started.",
     "Behaviour before the trouble began."),
    ("Record: months needed", "3 with an amount due.", "Fewer cannot show a habit."),
    ("Record: Clean", "Paid as billed in 80% of the months with an amount due.",
     "Allows an occasional miss."),
    ("State: High / Moderate", "High from 4 points, Moderate from 2.",
     "Payment rates step up at 2 points; High cannot be reached without a kept promise."),
    ("Refusal: look-back", "The current delinquency, at most 24 months.",
     "A refusal belongs to this delinquency."),
]  # fmt: skip
OTHER_COLUMNS = [
    ("Dispute", "The latest conversation was a dispute of the debt. Contesting is not refusing."),
    ("No pickup after contact", "After the latest conversation, 3 days (6 at 180+) of calls "
                                "that rang out, went unanswered or left a message, with no dead "
                                "line in between."),
    ("Hung up", "The customer hung up on the latest conversation."),
    ("Inputs", "Every count behind the state: promises concluded, kept and partial, months with "
               "a qualifying payment, months due and paid as billed, the levels and the points."),
]  # fmt: skip


def logic(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Logic"), [24, 56, 16, 26])

    def flow(title: str, steps: list[tuple[str, str]], label=_points) -> None:
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
            s.fit([(text, s.width(2, 4))])
            s.r += 1

    s.title("Logic", "What the model computes for each account at the scoring date, and the "
                     "rules that turn it into a state. Within a dimension, the first rule that "
                     "holds decides.")  # fmt: skip
    s.section("Evidence", gap=0)
    s.header(["Event", "", "Counts as", "Dimension"])
    s.ws.merge_cells(start_row=s.r - 1, start_column=1, end_row=s.r - 1, end_column=2)
    for event, counts_as, tone, dim in EVIDENCE:
        s.text(1, event, span=2, align=MID)
        s.chip(3, tone, counts_as)
        s.text(4, dim, color=MUTED, align=MID)
        s.fit([(event, s.width(1, 2)), (counts_as, s.widths[2])])
        s.r += 1
    s.note("All evidence is that of the scored account. Not a promise: soft or re-affirmed "
           "promises, a payment the customer reports, a cancelled plan. Not a refusal: a "
           "dispute, a hang-up.")  # fmt: skip
    s.section("Terms")
    table(TERMS)

    s.section("A. Promises kept: counting and judging a promise")
    table(PROMISE_RULES)
    flow("A. Promises kept: level", [
        ("The last 3 concluded promises were all not kept, or at least 2 are concluded and "
         "fewer than 40% of them kept.", "broken"),
        ("At least 2 concluded and 80% or more of them kept.", "kept"),
        ("At least one kept.", "partly"),
        ("Otherwise: no concluded promise, or a single one, not kept.", "thin"),
    ])  # fmt: skip
    flow("B. Payments in delinquency: level", [
        ("A qualifying payment in 2 or more of the last 3 months (3 or more of the last 6 at "
         "180+).", "regular"),
        ("100 AED or more paid in a month of the last 3 months (12 at 180+).", "some"),
        ("Otherwise: nothing paid. This is evidence, not a gap.", "none"),
    ])  # fmt: skip
    s.note("Only months after the month the delinquency started count.")
    flow("C. Record before delinquency: level", [
        ("Fewer than 3 months with an amount due in the 12 months before the delinquency "
         "started, or the history we hold does not reach back to its start.", "no_record"),
        ("Paid as billed in 80% or more of the months with an amount due.", "clean"),
        ("Otherwise.", "not_clean"),
    ])  # fmt: skip
    flow("Refusal", [
        ("The latest conversation in the current delinquency (at most 24 months back) ended in "
         "a refusal, and since then no plan has started and no month has 100 AED or more paid. "
         "On the same day, any other conversation counts as later than the refusal.", "refusal"),
    ], label=lambda _: "One level down")  # fmt: skip
    flow("State: total points = A + B + C", [
        ("No delinquency can be observed for the account.", "unknown"),
        ("4 points or more, and no refusal.", "high"),
        ("2 or 3 points and no refusal; or 4 points or more with a refusal.", "moderate"),
        ("Otherwise: fewer than 2 points, or fewer than 4 with a refusal.", "low"),
    ], label=LABEL.get)  # fmt: skip
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


# --- state map ------------------------------------------------------------------------------
def state_map(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("State map"), [16, 16, 10] + [14] * 6)
    s.title("State map", "Every combination of levels and the state it gets, for an account "
                         "with an observed delinquency.")  # fmt: skip
    s.text(1, None, span=3, border=False)
    s.text(4, "No refusal", span=3, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
    s.text(7, "Refusal", span=3, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
    s.r += 1
    s.header(["A. Promises", "B. Payments", "Points\nA + B"]
             + [f"C. {_points(c)}" for c in C_LEVELS] * 2, height=30)  # fmt: skip
    for a in A_LEVELS:
        for b in B_LEVELS:
            s.chip(1, a)
            s.chip(2, b)
            s.text(3, POINTS[a] + POINTS[b], align=CENTER)
            for i, (refusal, c) in enumerate((r, c) for r in (False, True) for c in C_LEVELS):
                s.chip(4 + i, state(a, b, c, refusal), align=CENTER)
            s.ws.row_dimensions[s.r].height = 20
            s.r += 1
    s.ws.freeze_panes = "D6"
    for (a, b, c, refusal), want in {
        ("kept", "regular", "no_record", False): "high",
        ("kept", "regular", "no_record", True): "moderate",
        ("partly", "regular", "clean", False): "high",
        ("thin", "regular", "clean", False): "moderate",
        ("thin", "some", "clean", True): "low",
        ("thin", "none", "clean", False): "low",
        ("broken", "regular", "clean", False): "moderate",
        ("broken", "regular", "not_clean", False): "low",
    }.items():
        assert state(a, b, c, refusal) == want, (a, b, c, refusal)


# --- examples -------------------------------------------------------------------------------
GRID = 12  # cells per example row
D = dt.date
ONE_PROMISE = [  # (outcome, product, segment, promise day, due, payments, next statement, why)
    ("paid", CARD, S61, D(2026, 3, 10), 800, [(D(2026, 3, 20), 800)], D(2026, 3, 25),
     "One month's due paid before the next statement."),
    ("partial", CARD, S61, D(2026, 3, 10), 800, [(D(2026, 3, 20), 300)], D(2026, 3, 25),
     "A payment, but less than one month's due."),
    ("unpaid", CARD, S61, D(2026, 3, 10), 800, [(D(2026, 3, 28), 800)], D(2026, 3, 25),
     "Paid after the statement: too late for this promise."),
    ("paid", CARD, S61, D(2026, 3, 10), 60, [(D(2026, 3, 12), 100)], D(2026, 3, 25),
     "A due under 100 AED still needs 100 AED."),
    ("paid", LOAN, S61, D(2026, 3, 20), 2500, [(D(2026, 3, 27), 2500)], None,
     "Instalment paid within the promise month."),
    ("unpaid", LOAN, S61, D(2026, 3, 28), 2500, [(D(2026, 4, 5), 2500)], None,
     "Paid in the following month."),
    ("paid", CARD, S180, D(2026, 3, 12), 600, [(D(2026, 3, 30), 400), (D(2026, 3, 31), 200)],
     None, "At 180+ the deadline is the month end; payments add up."),
]  # fmt: skip
COUNTING = [  # (promises, product, notes, plans, next statement, why)
    (1, CARD, [D(2026, 3, 3), D(2026, 3, 6), D(2026, 3, 9)], [], D(2026, 3, 25),
     "Notes at most 7 days apart are one promise, dated 3 Mar."),
    (2, CARD, [D(2026, 3, 3), D(2026, 3, 14)], [], D(2026, 3, 25),
     "11 days apart: two promises."),
    (2, LOAN, [D(2026, 3, 28), D(2026, 4, 2)], [], None,
     "5 days apart, but the second note is after the first promise's deadline (31 Mar)."),
    (1, CARD, [D(2026, 3, 7)], [D(2026, 3, 5)], D(2026, 3, 25),
     "The plan absorbs the note 2 days later."),
    (2, CARD, [D(2026, 3, 20)], [D(2026, 3, 5)], D(2026, 3, 25),
     "The note is 15 days from the plan: a promise of its own."),
]  # fmt: skip
A_EXAMPLES = [
    ("kept", "KKKKK", "5 concluded, all kept."),
    ("kept", "KXKKKK", "5 of 6 kept (83%)."),
    ("partly", "KXKK", "3 of 4 kept (75%): under 80%."),
    ("partly", "K", "A single promise, kept: one is not a pattern."),
    ("partly", "KKXXP", "2 of 4 kept; the pending promise is not counted."),
    ("broken", "KKKXXX", "The last 3 were all not kept, whatever came before."),
    ("broken", "XX", "2 concluded, none kept."),
    ("broken", "XXKXX", "1 of 5 kept (20%): under 40%."),
    ("thin", "X", "A single promise, not kept."),
    ("thin", "P", "One promise, still pending."),
    ("thin", "", "No promise in 12 months."),
]  # fmt: skip
B_EXAMPLES = {
    S61: [
        ("regular", "–QQ–Q", "Qualifying payment in 2 of the last 3 months."),
        ("some", "QQ–sQ", "Only 1 qualifying month in the last 3; earlier ones are out."),
        ("some", "–s–", "100 AED or more once, below one month's due."),
        ("none", "sQ–––", "Nothing in the last 3 months."),
    ],
    S180: [
        ("regular", "––––––Q–QsQ–", "Qualifying payment in 3 of the last 6 months."),
        ("some", "––––––Q––sQ–", "2 qualifying months in the last 6: not Regular."),
        ("some", "–s––––––––––", "One payment 11 months ago: within the 12 months."),
        ("none", "––––––––––––", "Nothing paid in 12 months."),
    ],
}  # fmt: skip
C_EXAMPLES = [
    ("clean", "✓✓✓✓✓✗✓✓✓✓✓✓", True, "11 of 12 months paid as billed (92%)."),
    ("clean", "···✓✓✓✓✗✓✓✓✓", True, "8 of 9 months with an amount due (89%)."),
    ("not_clean", "✓✓✗✓✓✗✓✓✗✓✓✓", True, "9 of 12 (75%): under 80%."),
    ("not_clean", "·········✓✗✗", True, "3 months due, 1 paid as billed."),
    ("no_record", "··········✓✓", True, "Only 2 months with an amount due."),
    ("no_record", "✓✓✓✓✓✓✓✓✓✓✓✓", False, "Delinquent since before the history we hold."),
]  # fmt: skip
STATE_EXAMPLES = [  # (state, A, B, C, refusal, delinquency observed, why)
    ("high", "kept", "regular", "clean", False, True, "Keeps promises, pays, clean before."),
    ("high", "partly", "regular", "clean", False, True, "4 points with a mixed promise record."),
    ("moderate", "kept", "regular", "no_record", True, True, "4 points, one level down for a refusal."),
    ("moderate", "thin", "regular", "clean", False, True, "Pays without promising: 3 points."),
    ("moderate", "broken", "regular", "clean", False, True, "Broken promises cost a point; the payments still count."),
    ("low", "thin", "none", "clean", False, True, "A clean past alone is 1 point."),
    ("low", "thin", "some", "clean", True, True, "2 points, one level down for a refusal."),
    ("low", "thin", "none", "no_record", False, True, "Delinquent with nothing positive on record."),
    ("unknown", "thin", "none", "no_record", False, False, "No delinquency observed."),
]  # fmt: skip


def _day(d: dt.date) -> str:
    return f"{d.day} {d:%b}"


def _check(got, want, text: str) -> None:
    if got != want:
        raise SystemExit(f"example '{text}' gives {got}, expected {want}")


def examples(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Examples"), [18] + [5] * GRID + [52])
    why = GRID + 2
    s.title("Examples", "One case per row, oldest on the left. Green = favourable, red = adverse. "
                        "Blue columns are the window the rule reads.")  # fmt: skip

    def legend(items: list[tuple[str, str]]) -> None:
        s.text(1, "Codes", bold=True, color=MUTED, border=False, align=MID)
        col, span = 2, GRID // len(items)
        for code, text in items:
            fill, ink = TONE[CODE_TONE[code]]
            s.text(col, f"{code}  {text}", span=span, color=ink, fill=fill, align=CENTER)
            col += span
        s.ws.row_dimensions[s.r].height = 28
        s.r += 1

    def grid(head: str, labels: list[str], rows: list[tuple[str, str, str]], window: int = 0,
             label=_points) -> None:  # fmt: skip
        s.header([head, *labels, "Why"])
        for k in range(GRID - window, GRID):
            s.ws.cell(row=s.r - 1, column=2 + k).fill = _fill(WINDOW_HEAD)
        for key, cells, text in rows:
            s.chip(1, key, label(key))
            for k, code in enumerate(cells.ljust(GRID) if window == 0 else cells.rjust(GRID)):
                tone = TONE[CODE_TONE[code]] if code in CODE_TONE else None
                fill = tone[0] if tone else (WINDOW_FILL if k >= GRID - window else None)
                s.text(2 + k, code.strip() or None, bold=True, color=tone[1] if tone else MUTED,
                       fill=fill, align=CENTER)  # fmt: skip
            s.text(why, text, align=MID)
            s.ws.row_dimensions[s.r].height = 20
            s.r += 1

    def cases(head: list[str], spans: list[int]) -> None:
        s.header([head[0], *head[1:], "Why"], [1, *spans, 1], height=30)

    s.section("A. One promise: kept or not", gap=0)
    cases(["Outcome", "Account", "Promise → deadline", "Due", "Paid by the deadline"], [3, 4, 2, 3])
    for want, product, seg, day, due, pays, statement, text in ONE_PROMISE:
        _check(outcome(product, seg, day, due, pays, statement), want, text)
        end = deadline(product, seg, day, statement)
        start = day.replace(day=1) - dt.timedelta(days=1) if product == LOAN else day
        paid = sum(a for d, a in pays if start < d <= end)
        s.chip(1, want)
        s.text(2, f"{product}, {seg.replace(' DPD', '')}", span=3, align=MID)
        s.text(5, f"{_day(day)} → {_day(end)}", span=4, align=MID)
        s.text(9, due, span=2, align=CENTER, fmt="#,##0")
        s.text(11, paid, span=3, align=CENTER, fmt="#,##0")
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("A. Counting promises (61–180 DPD)")
    cases(["Promises", "Account", "Collector notes", "Plan"], [2, 6, 4])
    for want, product, notes, plans, statement, text in COUNTING:
        got = promise_days(notes, plans, lambda d, p=product, st=statement: deadline(p, S61, d, st))
        _check(len(got), want, text)
        s.text(1, want, bold=True, align=CENTER)
        s.text(2, product, span=2, align=MID)
        s.text(4, ", ".join(_day(d) for d in notes), span=6, align=MID)
        s.text(10, ", ".join(_day(d) for d in plans) or "–", span=4, align=MID)
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("A. Promises kept: level")
    legend([(KEPT, "kept"), (NOT_KEPT, "not kept"), (PENDING, "pending")])
    for want, cells, text in A_EXAMPLES:
        _check(promises(cells), want, text)
    grid("Level", [str(k) for k in range(1, GRID + 1)], A_EXAMPLES)
    s.note("One cell per promise of the last 12 months, oldest first.")

    months = [("Now" if k == 0 else str(k)) for k in range(1 - GRID, 1)]
    legend_b = [(QUALIFYING, "qualifying payment"), (SMALL, "100 AED or more"), (NOTHING, "nothing")]
    for seg, rows in B_EXAMPLES.items():
        s.section(f"B. Payments in delinquency: level, {seg}")
        legend(legend_b)
        for want, cells, text in rows:
            _check(payments(cells.rjust(GRID), seg), want, text)
        grid("Level", months, rows, window=WINDOW[seg])
    s.note("One cell per month, the scoring month on the right; blank = before the delinquency. "
           "Regular reads the blue months; Some reads the last 3 months (12 at 180+).")  # fmt: skip

    s.section("C. Record before delinquency: level")
    legend([(AS_BILLED, "paid as billed"), (MISSED, "not paid as billed")])
    for want, cells, reaches, text in C_EXAMPLES:
        _check(record(cells, reaches), want, text)
    grid("Level", [str(k) for k in range(-GRID, 0)], [(w, c, t) for w, c, _, t in C_EXAMPLES],
         window=GRID)  # fmt: skip
    s.note("The 12 months before the delinquency started, the last one on the right; "
           "· = no amount due.")  # fmt: skip

    s.section("State")
    cases(["State", "A. Promises", "B. Payments", "C. Record", "Refusal", "Pts"], [3, 3, 3, 2, 1])
    for want, a, b, c, refusal, episode, text in STATE_EXAMPLES:
        _check(state(a, b, c, refusal, episode), want, text)
        s.chip(1, want)
        if episode:
            for col, lev in zip((2, 5, 8), (a, b, c)):
                s.chip(col, lev, _points(lev), span=3)
            s.chip(11, "refusal", "Yes", span=2) if refusal else s.text(11, "–", span=2, align=MID)
            s.text(13, POINTS[a] + POINTS[b] + POINTS[c], align=CENTER)
        else:
            s.text(2, "–", span=12, align=MID)
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
# Production run, month end 31 Aug 2026. Counts where the run kept them, else shares (%).
ACCOUNTS = [19292, 318663, 1397, 1224, 1364, 3985, 33862, 10306, 11203, 55371]
STATE_COUNTS = {0: [490, 3750, 15052, 0], 1: [159, 8288, 310216, 0],
                5: [126, 980, 2879, 0], 9: [120, 2289, 52962, 0]}  # fmt: skip
STATE_SHARES = {2: [1.1, 18.8, 80.0, 0], 3: [2.5, 24.5, 73.0, 0], 4: [5.8, 30.6, 63.6, 0],
                6: [0.1, 2.2, 97.7, 0], 7: [0.5, 8.7, 90.8, 0], 8: [0.4, 5.8, 93.8, 0]}  # fmt: skip
VINTAGE_ACCOUNTS = [61112, 257551, 10050, 45321]
VINTAGE_SHARES = {0: [0.2, 10.9, 88.9, 0], 1: [0.0, 0.6, 99.4, 0],
                  2: [0.6, 16.4, 83.0, 0], 3: [0.1, 1.4, 98.5, 0]}  # fmt: skip
SEGMENT_ACCOUNTS = [19292, 318663, 3985, 55371]
DETAIL = [  # (section, [(label, tone key)], {segment: values}, values are counts?)
    ("A. Promises kept", [(_points(k), k) for k in A_LEVELS],
     {0: [2.3, 13.9, 70.2, 13.6], 1: [0.0, 0.8, 97.9, 1.2],
      2: [4.8, 12.0, 74.5, 8.6], 3: [0.2, 1.3, 97.7, 0.8]}, False),
    ("B. Payments in delinquency", [(_points(k), k) for k in B_LEVELS],
     {0: [7.5, 17.6, 74.9], 1: [0.7, 5.2, 94.1], 2: [10.9, 32.4, 56.7], 3: [1.0, 7.2, 91.8]},
     False),
    ("C. Record before delinquency",
     [(_points("clean"), "clean"), (_points("not_clean"), "not_clean"),
      ("No record: fewer than 3 months with an amount due", "no_record"),
      ("No record: delinquent since before the history we hold", "no_record")],
     {0: [64.5, 20.0, 15.4, 0.0], 1: [10.5, 4.0, 31.1, 54.5],
      2: [44.3, 44.6, 11.1, 0.0], 3: [19.1, 15.4, 7.4, 58.1]}, False),
    ("Points total",
     [(f"{p} points".replace("-", "−"), "low" if p < 2 else "moderate" if p < 4 else "high")
      for p in range(-1, 6)],
     {0: [631, 4873, 9403, 2825, 1066, 416, 78], 1: [817, 274168, 34993, 7191, 1327, 161, 6],
      2: [80, 1085, 1687, 729, 276, 87, 41], 3: [82, 42228, 10617, 1842, 482, 109, 11]}, True),
    ("Refusal and other columns",
     [("Refusal", "bad"), ("Refusal that lowers the state", "bad"), ("Dispute", "unknown"),
      ("No pickup after contact", "unknown"), ("Hung up", "unknown")],
     {0: [844, 149, 74, 1344, 443], 1: [6480, 246, 565, 2901, 4569],
      2: [185, 29, 0, 329, 41], 3: [1007, 35, 58, 403, 615]}, True),
]  # fmt: skip
BANDS = [  # (segment, band, accounts, High %, Moderate %, Low %)
    ("Credit cards 61–180", "61–90 DPD", 5859, 4.8, 25.4, 69.8),
    ("Credit cards 61–180", "91–120 DPD", 5260, 2.3, 19.2, 78.5),
    ("Credit cards 61–180", "121–150 DPD", 4401, 1.4, 16.8, 81.8),
    ("Credit cards 61–180", "151–180 DPD", 3772, 0.7, 13.7, 85.7),
    ("Retail loans 61–180", "61–90 DPD", 1401, 5.7, 30.7, 63.6),
    ("Retail loans 61–180", "91–120 DPD", 1106, 2.4, 26.9, 70.7),
    ("Retail loans 61–180", "121–150 DPD", 971, 1.8, 18.0, 80.2),
    ("Retail loans 61–180", "151–180 DPD", 507, 0.6, 15.2, 84.2),
    ("Credit cards 180+", "181–360 DPD", 16823, 0.3, 19.3, 80.5),
    ("Credit cards 180+", "361–720 DPD", 29712, 0.3, 9.2, 90.5),
    ("Credit cards 180+", "720+ DPD", 272128, 0.0, 0.8, 99.1),
    ("Retail loans 180+", "181–360 DPD", 3926, 1.8, 33.0, 65.2),
    ("Retail loans 180+", "361–720 DPD", 4848, 0.4, 10.2, 89.4),
    ("Retail loans 180+", "720+ DPD", 46597, 0.1, 1.1, 98.9),
]  # fmt: skip
TREND = {  # month end 2026: (High, Moderate, Low)
    "Credit cards 61–180": {
        "Jan": (608, 3392, 10664), "Feb": (615, 3299, 10662), "Mar": (607, 3241, 10607),
        "Apr": (581, 3206, 10884), "May": (598, 3335, 11957), "Jun": (544, 3556, 12882),
        "Jul": (518, 3728, 14151), "Aug": (490, 3750, 15052)},
    "Retail loans 61–180": {
        "Jan": (106, 656, 1562), "Feb": (100, 588, 1525), "Mar": (102, 604, 1512),
        "Apr": (105, 736, 1820), "May": (95, 769, 2232), "Jun": (94, 860, 2560),
        "Jul": (102, 877, 2749), "Aug": (126, 980, 2879)},
    "Credit cards 180+": {
        "Jan": (118, 7483, 297656), "Feb": (119, 7695, 299040), "Mar": (128, 7948, 300666),
        "Apr": (145, 8007, 302557), "May": (146, 8057, 304423), "Jun": (164, 8161, 306502),
        "Jul": (160, 8241, 308337), "Aug": (159, 8288, 310216)},
    "Retail loans 180+": {
        "Jan": (105, 1927, 50625), "Feb": (105, 1950, 50827), "Mar": (103, 1927, 51240),
        "Apr": (113, 1895, 51607), "May": (128, 1976, 51902), "Jun": (111, 2157, 52115),
        "Jul": (115, 2207, 52497), "Aug": (120, 2289, 52962)},
}  # fmt: skip
ENTRY = {"color": "0000FF", "fill": INPUT_FILL}


def _pair(s: Sheet, col: int, *, count=None, share=None, base: str | None = None) -> None:
    """A count and its share. An entered count gets a share formula of cell ``base``; where
    only the share is known it is entered and the count stays blank."""
    L = get_column_letter(col)
    s.text(col, count, fmt="#,##0", **(ENTRY if count is not None else {}))
    if count is not None and base:
        s.text(col + 1, f'=IF(N({base})=0,"",{L}{s.r}/{base})', color=MUTED, fmt="0.0%")
    elif share is not None:
        s.text(col + 1, share / 100, fmt="0.0%", **ENTRY)
    else:
        s.text(col + 1, None)


def _state_table(s: Sheet, cols: list[str], accounts: list[int], counts: dict, shares: dict) -> None:
    """States x columns (count + share), Total, Accounts in scope and Coverage."""
    s.header(["State"] + [x for name in cols for x in (name, "share")], height=58)
    first, total = s.r, s.r + len(STATES)
    for i, st in enumerate(STATES):
        s.chip(1, st)
        for b in range(len(cols)):
            L = get_column_letter(2 + 2 * b)
            _pair(s, 2 + 2 * b, count=counts[b][i] if b in counts else None,
                  share=shares[b][i] if b in shares else None, base=f"{L}${total}")  # fmt: skip
        s.r += 1
    for label, bold in (("Total", True), ("Accounts in scope", False), ("Coverage", True)):
        s.text(1, label, bold=bold)
        for b in range(len(cols)):
            col = 2 + 2 * b
            L = get_column_letter(col)
            if label == "Accounts in scope":
                s.text(col, accounts[b], fmt="#,##0", **ENTRY)
            elif b not in counts:
                s.text(col, None)
            elif label == "Total":
                s.text(col, f"=SUM({L}{first}:{L}{total - 1})", bold=True, fmt="#,##0")
            else:
                s.text(col, f"={L}{total}/{L}{total + 1}", bold=True, fmt="0.0%")
            s.text(col + 1, None)
        s.r += 1


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [16] + [11, 7] * len(VARIANTS))
    s.title("Results", f"Accounts per state and model variant, {RESULTS_DATE} (production run). "
                       "Pale yellow = from the run; other shares and totals are calculated.")  # fmt: skip
    s.section("Credibility state", gap=0)
    _state_table(s, VARIANTS, ACCOUNTS, STATE_COUNTS, STATE_SHARES)
    s.r += 1
    s.note("Loans by product: the run kept shares, not counts. Every scored account has an "
           "observed delinquency, so Unknown is empty. Aggregates only.")  # fmt: skip
    s.ws.freeze_panes = "B6"


def detail(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results detail"), [50] + [11, 7] * len(SEGMENTS))
    s.title("Results detail", f"What sits behind the states, {RESULTS_DATE}. Shares are of all "
                              "accounts in the segment.")  # fmt: skip
    s.header([""] + [x for name in SEGMENTS for x in (name, "share")], height=30)
    s.text(1, "Accounts", bold=True)
    base = s.r
    for b, n in enumerate(SEGMENT_ACCOUNTS):
        s.text(2 + 2 * b, n, fmt="#,##0", **ENTRY)
        s.text(3 + 2 * b, None)
    s.r += 1
    for title, labels, data, counted in DETAIL:
        s.section(title)
        for i, (label, tone) in enumerate(labels):
            s.chip(1, tone, label)
            for b in range(len(SEGMENTS)):
                L = get_column_letter(2 + 2 * b)
                v = data[b][i]
                _pair(s, 2 + 2 * b, count=v if counted else None, share=None if counted else v,
                      base=f"{L}${base}")  # fmt: skip
            s.r += 1
    s.section("State by DPD band")
    s.header(["", "Accounts", "", "High", "", "Moderate", "", "Low", ""])
    for c in (2, 4, 6, 8):
        s.ws.merge_cells(start_row=s.r - 1, start_column=c, end_row=s.r - 1, end_column=c + 1)
    for seg, band, n, *shares in BANDS:
        s.text(1, f"{seg} · {band}")
        s.text(2, n, span=2, fmt="#,##0", **ENTRY)
        for col, v in zip((4, 6, 8), shares):
            s.text(col, v / 100, span=2, fmt="0.0%", **ENTRY)
        s.r += 1
    s.r += 1
    s.note("Levels: the run kept shares, not counts. Most refusals do not change the state: the "
           "account is already Low. Cards at 180+: the DPD band is taken from the charge-off "
           "age.")  # fmt: skip
    s.ws.freeze_panes = "B6"


def trend(wb: Workbook) -> None:
    states = STATES[:3]
    s = Sheet(wb.create_sheet("Results trend"), [10, 10] + [10, 7] * len(states))
    s.title("Results trend", "Accounts per state by month, Jan–Aug 2026 (month ends). Shares are "
                             "of the month's accounts.")  # fmt: skip
    for i, (title, months) in enumerate(TREND.items()):
        s.section(title, gap=0 if i == 0 else 1)
        s.text(1, "Month", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.text(2, "Accounts", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, st in enumerate(states):
            s.chip(3 + 2 * j, st, span=2, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
        for month, counts in months.items():
            s.text(1, f"{month} 2026", bold=True)
            s.text(2, "=" + "+".join(f"{get_column_letter(3 + 2 * j)}{s.r}" for j in range(3)),
                   bold=True, fmt="#,##0")  # fmt: skip
            for j, n in enumerate(counts):
                _pair(s, 3 + 2 * j, count=n, base=f"$B{s.r}")
            s.r += 1
    s.r += 1
    s.note("At 61–180 the books grew through the year and the new accounts are mostly Low. "
           "180+ is flat.")  # fmt: skip
    s.ws.freeze_panes = "A4"


def vintage(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results 180+ vintage"), [16] + [12, 7] * len(VINTAGES))
    s.title("Results 180+ by vintage",
            "Early-stage charge-off = charged off less than 2 years ago; late-stage = 2 years or "
            f"more; {RESULTS_DATE}. Shares are within each vintage.")  # fmt: skip
    s.section("Credibility state", gap=0)
    _state_table(s, VINTAGES, VINTAGE_ACCOUNTS, {}, VINTAGE_SHARES)
    s.ws.freeze_panes = "B6"


# --- validation -----------------------------------------------------------------------------
BOOKS = ["Cards 61–180", "Loans 61–180", "Cards 180+", "Loans 180+"]
# Month ends Jan–May 2026 pooled, outcomes over the next 3 months (% of accounts).
OUTCOMES = [  # book, accounts H / M / L, paid a due H, M, L, any payment H, M, L
    ("Cards 61–180", "3,009 / 16,473 / 54,774", (65.4, 37.6, 10.9), (67.0, 40.1, 12.0)),
    ("Loans 61–180", "508 / 3,353 / 8,651", (69.3, 54.0, 24.3), (74.2, 63.2, 32.7)),
    ("Cards 180+", "656 / 39,190 / 1,504,342", (51.8, 30.7, 1.5), (53.5, 35.4, 2.0)),
    ("Loans 180+", "554 / 9,675 / 256,201", (67.1, 31.6, 1.3), (70.2, 37.5, 1.9)),
]
BY_GROUP = [  # book, split, group, paid a due H, M, L
    ("Cards 61–180", "DPD", "61–90", 64.6, 42.1, 18.9),
    ("Cards 61–180", "DPD", "91–120", 71.3, 41.8, 12.0),
    ("Cards 61–180", "DPD", "121–150", 63.2, 35.2, 8.0),
    ("Cards 61–180", "DPD", "151–180", 50.6, 18.4, 2.9),
    ("Loans 61–180", "Product", "Personal Loans", 75.2, 42.5, 15.2),
    ("Loans 61–180", "Product", "Personal Cash Loans", 71.0, 53.5, 22.3),
    ("Loans 61–180", "Product", "Auto", 65.1, 62.0, 42.2),
    ("Loans 61–180", "DPD", "61–90", 72.2, 60.0, 35.2),
    ("Loans 61–180", "DPD", "91–120", 68.2, 54.5, 23.1),
    ("Loans 61–180", "DPD", "121–150", 62.5, 44.0, 15.5),
    ("Loans 61–180", "DPD", "151–180", 68.2, 36.1, 15.0),
    ("Cards 180+", "Vintage", "Early-stage charge-off", 50.6, 21.6, 4.0),
    ("Cards 180+", "Vintage", "Late-stage charge-off", 69.8, 64.6, 1.0),
    ("Loans 180+", "Product", "Personal Loans", 75.2, 38.7, 0.9),
    ("Loans 180+", "Product", "Personal Cash Loans", 60.6, 31.7, 2.8),
    ("Loans 180+", "Product", "Auto", 68.8, 23.1, 1.4),
    ("Loans 180+", "Vintage", "Early-stage charge-off", 61.4, 22.7, 4.4),
    ("Loans 180+", "Vintage", "Late-stage charge-off", 76.3, 53.8, 0.7),
]
AUC = [  # book, state: all accounts, state within DPD band, points total
    ("Cards 61–180", "0.70", "61–90 0.67 · 91–120 0.71 · 121–150 0.71 · 151–180 0.72", "0.70"),
    ("Loans 61–180", "0.65", "61–90 0.63 · 91–120 0.67 · 121–150 0.66 · 151–180 0.61", "0.70"),
    ("Cards 180+", "0.67", "181–360 0.58 · 361–720 0.68 · 720+ 0.65", "0.82"),
    ("Loans 180+", "0.74", "181–360 0.68 · 361–720 0.71 · 720+ 0.71", "0.86"),
]
POINTS_PAID = [  # points total, paid a due % per book, state without a refusal
    ("−1", 15.6, 28.4, 8.6, 8.0, "low"),
    ("0", 9.8, 18.4, 0.7, 0.5, "low"),
    ("1", 11.1, 28.2, 9.5, 4.5, "low"),
    ("2", 30.3, 47.6, 27.7, 24.5, "moderate"),
    ("3", 50.3, 66.0, 42.8, 54.9, "moderate"),
    ("4", 64.5, 65.2, 49.5, 66.6, "high"),
    ("5", 66.7, 87.9, 55.2, 73.0, "high"),
]
STABILITY = [  # book, same state next month, up, down, High stays, Moderate stays (%)
    ("Cards 61–180", 90.2, 4.3, 5.6, 77.8, 75.3),
    ("Loans 61–180", 88.2, 5.3, 6.6, 72.0, 75.9),
    ("Cards 180+", 99.5, 0.2, 0.3, 78.8, 89.3),
    ("Loans 180+", 99.3, 0.3, 0.3, 81.7, 91.0),
]
OVERLAP = [  # book, Cramér's V with ability, reachability, location, deterioration
    ("Cards 61–180", 0.11, 0.19, 0.14, 0.41),
    ("Loans 61–180", 0.06, 0.16, 0.15, 0.36),
    ("Cards 180+", 0.14, 0.19, 0.17, 0.22),
    ("Loans 180+", 0.22, 0.24, 0.18, 0.20),
]
HML = {2: "good", 3: "mid", 4: "bad"}


def _pc(x: float) -> str:
    return f"{x:.1f}%"


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [20, 22, 15, 15, 15, 15, 15, 15])
    s.title("Validation", "What each state goes on to do: month ends January to May 2026, "
                          "outcomes over the following 3 months. Paid a due = payments reach one "
                          "month's due; any payment = 100 AED or more.")  # fmt: skip
    s.section("Outcome by state", gap=0)
    s.text(1, None, span=2, border=False)
    s.text(3, "Paid a due", span=3, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
    s.text(6, "Any payment", span=3, bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
    s.r += 1
    s.header(["Book", "Accounts\nH / M / L"] + ["High", "Moderate", "Low"] * 2, height=30)
    for book, n, paid, anyp in OUTCOMES:
        s.row([book, n, *map(_pc, paid + anyp)], align=MID,
              tones={2: "good", 3: "mid", 4: "bad", 5: "good", 6: "mid", 7: "bad"})  # fmt: skip
    s.note("High pays most and Low least in every book, month and group. Cure and roll do not "
           "separate the states: cards leave billing at charge-off, loans cure alike in every "
           "state.")  # fmt: skip

    s.section("Paid a due by group")
    s.header(["Book", "Group", "High", "Moderate", "Low"], [1, 1, 1, 1, 1])
    for book, split, group, *vals in BY_GROUP:
        s.row([book, f"{split}: {group}", *map(_pc, vals)], align=MID, tones=HML)

    s.section("Ranking power (AUC on paid a due; 0.5 = chance)")
    s.header(["Book", "State", "State within DPD band", "", "", "", "Points total", ""])
    for c1, c2 in ((3, 6), (7, 8)):
        s.ws.merge_cells(start_row=s.r - 1, start_column=c1, end_row=s.r - 1, end_column=c2)
    for row in AUC:
        s.row(list(row), [1, 1, 4, 2], align=MID)
    s.note("The state ranks customers inside every DPD band. At 180+, where almost all accounts "
           "are Low, the points total ranks far better than the three states.")  # fmt: skip

    s.section("Paid a due by points total")
    s.header(["Points", "State (no refusal)", *BOOKS])
    for pts, *vals, st in POINTS_PAID:
        s.text(1, pts, bold=True, align=CENTER)
        s.chip(2, st)
        for col, v in enumerate(vals, 3):
            s.text(col, _pc(v), align=MID)
        s.r += 1
    s.note("The step comes at 2 points in every book, where Moderate starts. −1 (Broken) pays "
           "more than 0: see 'Sensitivity'.")  # fmt: skip

    s.section("Stability, one month to the next")
    s.header(["Book", "Same state", "Up", "Down", "High stays", "Moderate stays"])
    for book, *vals in STABILITY:
        s.row([book, *map(_pc, vals)], align=MID)

    s.section("Overlap with the other axes (Cramér's V; 0 = unrelated, 1 = the same axis)")
    s.header(["Book", "Ability", "Reachability", "Location", "Deterioration"])
    for book, *vals in OVERLAP:
        s.row([book, *(f"{v:.2f}" for v in vals)], align=MID)
    s.note("Highest with deterioration at 61–180: payments drive the DPD path.")
    s.ws.freeze_panes = "A4"


# --- sensitivity ----------------------------------------------------------------------------
# Month end 31 Aug 2026 state mix (%) and state AUC on paid a due (month ends Mar–May 2026).
DEADLINES = [  # book, [(deadline, High, Moderate, Low, AUC)]
    ("Cards 61–180", [("Next statement (model)", 2.5, 19.4, 78.0, 0.692),
                      ("30 days", 4.0, 22.7, 73.3, 0.714)]),
    ("Loans 61–180", [("End of the promise month (model)", 3.2, 24.6, 72.2, 0.643),
                      ("30 days, to that month's end", 4.9, 27.9, 67.2, 0.666)]),
    ("Cards 180+", [("End of the promise month (model)", 0.0, 2.6, 97.3, 0.665),
                    ("30 days", 0.1, 2.9, 97.0, 0.690)]),
    ("Loans 180+", [("End of the promise month (model)", 0.2, 4.1, 95.6, 0.736),
                    ("30 days, to that month's end", 0.3, 4.3, 95.4, 0.746)]),
]  # fmt: skip
PROMISE_PAID = [  # book, paid a due %: Kept, Partly, Broken, Thin: one not kept, Thin: none
    ("Cards 61–180", 38.4, 32.9, 28.5, 24.0, 8.2),
    ("Loans 61–180", 58.0, 53.9, 47.9, 42.9, 25.3),
    ("Cards 180+", 21.1, 30.5, 17.6, 21.0, 1.3),
    ("Loans 180+", 36.6, 43.5, 19.8, 20.4, 1.6),
]
BROKEN_POINTS = [  # book, state AUC with Broken at −1 (model), 0, +1; accounts moving up at +1 (%)
    ("Cards 61–180", 0.692, 0.722, 0.737, 11.7),
    ("Loans 61–180", 0.643, 0.655, 0.673, 7.6),
    ("Cards 180+", 0.665, 0.680, 0.697, 0.8),
    ("Loans 180+", 0.736, 0.742, 0.756, 0.6),
]
NO_EVIDENCE = [  # book, share of accounts, paid a due %: no evidence, rest of Low, Moderate
    ("Cards 61–180", 12.2, 3.9, 12.4, 35.2),
    ("Loans 61–180", 7.0, 9.2, 28.1, 54.2),
    ("Cards 180+", 83.0, 0.5, 7.6, 30.6),
    ("Loans 180+", 65.1, 0.2, 3.9, 32.5),
]


def sensitivity(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Sensitivity"), [20, 26, 16, 16, 16, 16, 16])
    s.title("Sensitivity", "How the states react to the two promise parameters, and who sits in "
                           "Low with no evidence. Outcomes: paid a due in the following 3 months, "
                           "month ends March to May 2026.")  # fmt: skip
    s.section("Promise deadline", gap=0)
    s.header(["Book", "Deadline", "High", "Moderate", "Low", "State AUC"])
    for book, rows in DEADLINES:
        for name, hi, mo, lo, auc in rows:
            s.row([book, name, _pc(hi), _pc(mo), _pc(lo), f"{auc:.3f}"], align=MID, tones=HML)
    s.note(f"State mix at {RESULTS_DATE}. A 30-day deadline counts more promises as kept and "
           "ranks customers a little better in every book.")  # fmt: skip

    s.section("Paid a due by promise level")
    s.header(["Book", *(LABEL[k] for k in ("kept", "partly", "broken")),
              "Thin: one,\nnot kept", "Thin: no\npromise"], [2, 1, 1, 1, 1, 1],
             height=30)  # fmt: skip
    for book, *vals in PROMISE_PAID:
        s.row([book, *map(_pc, vals)], [2, 1, 1, 1, 1, 1], align=MID)
    s.note("Customers who never promised pay least. A Broken record pays like a single promise "
           "not kept, and more than no promise.")  # fmt: skip

    s.section("Points for Broken")
    s.header(["Book", "State AUC:\n−1 (model)", "State AUC:\n0", "State AUC:\n+1",
              "Low → Moderate\nat +1"], [2, 1, 1, 1, 1], height=30)  # fmt: skip
    for book, a, b, c, moved in BROKEN_POINTS:
        s.row([book, f"{a:.3f}", f"{b:.3f}", f"{c:.3f}", _pc(moved)], [2, 1, 1, 1, 1], align=MID)
    s.note("Scoring Broken higher ranks customers better in every book; the accounts it moves "
           "to Moderate pay like Moderate at 61–180.")  # fmt: skip

    s.section("Low with no evidence in any dimension")
    s.header(["Book", "Share of accounts", "Paid a due:\nno evidence",
              "Paid a due:\nrest of Low", "Paid a due:\nModerate"], [2, 1, 1, 1, 1],
             height=30)  # fmt: skip
    for book, *vals in NO_EVIDENCE:
        s.row([book, *map(_pc, vals)], [2, 1, 1, 1, 1], align=MID)
    s.note("No promise, no payment and no record: they pay least, so they are Low. At 61–180 "
           "mostly accounts that defaulted within months of opening; at 180+ accounts charged "
           "off long ago.")  # fmt: skip
    s.ws.freeze_panes = "A4"


def build(out: pathlib.Path) -> pathlib.Path:
    wb = Workbook()
    overview(wb)
    logic(wb)
    state_map(wb)
    examples(wb)
    results(wb)
    detail(wb)
    trend(wb)
    vintage(wb)
    validation(wb)
    sensitivity(wb)
    wb.calculation.fullCalcOnLoad = True
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
