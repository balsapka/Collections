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
    "kept": 3, "partly": 2, "promised": 1, "no_promise": 0,
    "regular": 2, "some": 1, "none": 0,
    "clean": 1, "not_clean": 0, "no_record": 0,
}  # fmt: skip
A_LEVELS = ["kept", "partly", "promised", "no_promise"]
B_LEVELS = ["regular", "some", "none"]
C_LEVELS = ["clean", "not_clean", "no_record"]
MIN_AED = 100  # smallest payment that counts as a payment
MIN_CONCLUDED, KEPT_RATE = 2, 0.80
NEXT_STATEMENT_MAX_DAYS = 31  # a card deadline is never later than this after the promise
WINDOW = {S61: 3, S180: 6}  # months of payments in delinquency
REGULAR_FROM = {S61: 2, S180: 3}  # months with a qualifying payment
SOME_WINDOW = {S61: 3, S180: 12}
RECORD_MONTHS, RECORD_MIN_DUE, CLEAN_SHARE = 12, 3, 0.80
KEPT, NOT_KEPT, PENDING = "K", "X", "P"  # one promise
QUALIFYING, SMALL, NOTHING, BEFORE = "Q", "s", "–", " "  # one month of the delinquency
AS_BILLED, MISSED, NO_DUE = "✓", "✗", "·"  # one month before the delinquency


def promises(history: str) -> str:
    """Level A from the promise events of the last 12 months, oldest first (pending ones
    count only for Promised)."""
    done = [p == KEPT for p in history if p != PENDING]
    n, kept = len(done), sum(done)
    if n >= MIN_CONCLUDED and kept / n >= KEPT_RATE:
        return "kept"
    if kept:
        return "partly"
    return "promised" if history else "no_promise"


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


def state(a: str, b: str, c: str, refusal: bool = False) -> str:
    pts = POINTS[a] + POINTS[b] + POINTS[c]
    if pts >= HIGH_FROM:
        return "moderate" if refusal else "high"
    return "moderate" if pts >= MODERATE_FROM and not refusal else "low"


def state_of_points(pts: int) -> str:
    """The state of a points total without a refusal."""
    return "high" if pts >= HIGH_FROM else "moderate" if pts >= MODERATE_FROM else "low"


def month_end(day: dt.date) -> dt.date:
    return (day.replace(day=1) + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)


def deadline(product: str, seg: str, day: dt.date, statement: dt.date | None = None) -> dt.date:
    """The last day a payment still counts for a promise made on ``day``."""
    if product == CARD and seg == S61:
        cap = day + dt.timedelta(days=NEXT_STATEMENT_MAX_DAYS)
        return min(statement, cap) if statement else cap
    return month_end(day)


def _paid(product, day, end, pays) -> float:
    """Payments from the event day up to ``end``; loans: the event month's cash counts."""
    start = day.replace(day=1) if product == LOAN else day
    return sum(amount for d, amount in pays if start <= d <= end)


def outcome(product, seg, day, due, pays, statement=None) -> str:
    """One event judged by the payments ``[(date, amount)]`` that followed its first day."""
    paid = _paid(product, day, deadline(product, seg, day, statement), pays)
    return "paid" if paid >= max(due, MIN_AED) else "partial" if paid >= MIN_AED else "unpaid"


def events(product, promise_days, due, pays, statement=None) -> list[dt.date]:
    """The event start days (61–180) that a stream of promise days amounts to: an event is
    alive until its deadline passes or the payments since its day reach the amount to pay;
    every promise meanwhile belongs to it."""
    starts: list[dt.date] = []
    for day in sorted(promise_days):
        if starts:
            start = starts[-1]
            paid = _paid(product, start, day - dt.timedelta(days=1), pays)
            if day <= deadline(product, S61, start, statement) and paid < max(due, MIN_AED):
                continue
        starts.append(day)
    return starts


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
    "kept": "good", "partly": "good", "promised": "mid", "no_promise": "unknown",
    "regular": "good", "some": "mid", "none": "bad",
    "clean": "good", "not_clean": "bad", "no_record": "unknown",
    "paid": "good", "partial": "bad", "unpaid": "bad", "refusal": "bad",
}  # fmt: skip
LABEL = {
    "high": "High", "moderate": "Moderate", "low": "Low",
    "kept": "Kept", "partly": "Partly kept", "broken": "Broken", "promised": "Promised",
    "no_promise": "No promise",
    "regular": "Regular", "some": "Some", "none": "None",
    "clean": "Clean", "not_clean": "Not clean", "no_record": "No record",
    "paid": "Kept", "partial": "Not kept (partial)", "unpaid": "Not kept", "refusal": "Refusal",
}  # fmt: skip
CODE_TONE = {KEPT: "good", NOT_KEPT: "bad", PENDING: "unknown", QUALIFYING: "good",
             SMALL: "mid", NOTHING: "bad", AS_BILLED: "good", MISSED: "bad"}  # fmt: skip
STATES = ["high", "moderate", "low"]
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
    s = Sheet(wb.active, [24, 19, 19, 19, 19, 19])
    s.ws.title = "Overview"
    s.title(
        "A3 Payment Credibility",
        "How far can we believe this customer will pay this debt? Three scored dimensions and a "
        "refusal override; every account in scope gets exactly one state.",
    )
    for k, v in [
        ("Scope", "Credit cards and retail loans (Personal Loans, Personal Cash Loans, Auto) at "
                  "61–180 DPD and 180+ DPD, scored at each month end."),
        ("A. Promises", "Does the customer commit, and keep to it? Promises of the last 12 "
                        "months, each judged by the payments that followed it. Any promise "
                        "counts: customers who promise pay more than those who never do."),
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
        s.text(2, v, span=5, border=False)
        s.fit([(v, s.width(2, 6))], floor=18)
        s.r += 1
    s.section("States")
    s.header(["State", "Rule", "Meaning"], [1, 2, 3])
    for st, rule, meaning in [
        ("high", "4 points or more, no refusal.",
         "Has promised and money is coming in."),
        ("moderate", "2 or 3 points, no refusal. Or 4 or more with a refusal.",
         "Some evidence to rely on, not yet consistent; or a strong record with a fresh refusal."),
        ("low", "Fewer than 2 points. Or fewer than 4 with a refusal.",
         "Little or nothing positive on record, or it is outweighed by a refusal."),
    ]:  # fmt: skip
        s.chip(1, st)
        s.text(2, rule, span=2, align=MID)
        s.text(4, meaning, span=3, align=MID)
        s.fit([(rule, s.width(2, 3)), (meaning, s.width(4, 6))])
        s.r += 1
    s.section("Dimensions and points")
    s.header(["Dimension", "Levels", "", "", "", ""])
    s.ws.merge_cells(start_row=s.r - 1, start_column=2, end_row=s.r - 1, end_column=6)
    for name, levels in [("A. Promises kept", A_LEVELS), ("B. Payments in delinquency", B_LEVELS),
                         ("C. Record before delinquency", C_LEVELS)]:  # fmt: skip
        s.text(1, name, bold=True, align=MID)
        for col in range(2, 7):
            lev = levels[col - 2] if col - 2 < len(levels) else None
            s.chip(col, lev, _points(lev), align=CENTER) if lev else s.text(col, None)
        s.ws.row_dimensions[s.r].height = 30
        s.r += 1
    s.r += 1
    s.note("Rules: 'Logic'. Every combination of levels: 'State map'. Shares: 'Results'. "
           "What each state goes on to pay: 'Validation'.")  # fmt: skip
    s.ws.freeze_panes = "A4"


# --- logic ----------------------------------------------------------------------------------
TERMS = [
    ("Account", "Promises, payments, amounts due and conversations are those of the scored "
                "account only."),
    ("Payment", "Card: a payment posted to the card account, by its posting date. Loan: the "
                "payments received on the loan in a month (known by month, not by day)."),
    ("Delinquency", "The current continuous run of months at 1+ DPD; a return to 0 DPD ends "
                    "it. It starts on the first day of its first month."),
    ("Month", "Card: a statement cycle, from one statement to the next. Loan: a calendar month."),
    ("One month's due", "Card: the oldest unpaid monthly amount on the statement, or the minimum "
                        "due when nothing is overdue. On a statement where the 210+ DPD bucket "
                        "holds money: the average of that amount over the latest 12 months before "
                        "the bucket first held money (none: no due). Loan: the monthly "
                        "instalment, the last known one when the month has none."),
    ("Qualifying payment", "The payments of a month reach one month's due and at least 100 AED."),
    ("Paid as billed", "The payments of a month reach the amount due, before the next statement "
                       "(loans: within the month). Paying the minimum counts, whatever its size."),
    ("Conversation", "A contact in which the account holder was reached in person."),
]  # fmt: skip
PROMISE_RULES = [
    ("Promise", "A promise-to-pay or settlement plan recorded in the collections system and not "
                "cancelled, or a collector note of a promise: promise to pay (full, partial or "
                "scheduled), digital collect subscribed, will pay at salary. Not a promise: a "
                "soft or re-affirmed promise, a payment the customer reports."),
    ("Event", "Plans (dated at their start) and collector notes (dated at the call) are one "
              "stream. An event starts with a promise and stays alive until its deadline passes "
              "or the payments since its first day reach the amount to pay; every promise "
              "meanwhile belongs to it, also one on the deadline day. The next promise starts a "
              "new event. Loans: cash is known by month, so all promises of a month are one "
              "event."),
    ("Window", "Promises dated in the 12 months up to the scoring date, earlier delinquencies "
               "included."),
    ("Deadline", "Set by the event's first day, whatever date was promised. Cards at 61–180 "
                 "DPD: the next statement, at most 31 days later. Loans, and every account at "
                 "180+ DPD: the last day of that month. A payment on the deadline day counts."),
    ("Amount to pay", "One month's due on the event's first day, at least 100 AED."),
    ("Kept", "The payments from the event's first day (a payment that day counts), up to the "
             "deadline, reach the amount to pay. Less is not kept, a partial payment included. Loans: the payments of the "
             "event month count in full."),
    ("Concluded", "The deadline is on or before the scoring date, also for an event paid "
                  "early. Pending events count only for Promised."),
]  # fmt: skip
PARAMETERS = [  # (parameter, value, why)
    ("Promises: window", "12 months, earlier delinquencies included.",
     "Trust is a track record."),
    ("Promises: deadline", "Cards at 61–180: next statement (at most 31 days). Loans and "
                           "180+: end of the promise month.",
     "Set by GRR; one rule whatever date was promised."),
    ("Promises: amount to pay", "One month's due, at least 100 AED.",
     "What a customer can be asked for in a month; a token payment keeps no promise."),
    ("Promises: one event", "Alive until the deadline or until paid.",
     "Repeated promises on one debt are one commitment."),
    ("Promises: points", "Kept 3, Partly kept 2, Promised 1, No promise 0.",
     "Promising is engagement even when missed; keeping it is stronger."),
    ("Promises: concluded needed", "2, for Kept.",
     "One promise is not a pattern."),
    ("Promises: Kept", "From 80% kept.", "A clear record; any kept promise short of it is "
                                         "Partly kept."),
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
     "Payment rates step up at 2 points; High needs a promise and payments."),
    ("Refusal: look-back", "The current delinquency, at most 24 months.",
     "A refusal belongs to this delinquency."),
    ("Refusal: lifted", "A plan, or 100 AED paid, on or after the refusal day (loans: in the "
                        "refusal month or later).", "Counted only when nothing followed it."),
]  # fmt: skip
OTHER_COLUMNS = [
    ("Dispute", "The latest conversation was a dispute of the debt. Contesting is not refusing."),
    ("No pickup after contact", "After the latest conversation, 3 days (6 at 180+) of calls "
                                "that rang out, went unanswered or left a message, with no dead "
                                "line in between."),
    ("Hung up", "The customer hung up on the latest conversation."),
    ("Inputs", "Every count behind the state: promise events, concluded, kept and partial, months with "
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
    s.section("Terms", gap=0)
    table(TERMS)

    s.section("A. Promises kept: counting and judging a promise")
    table(PROMISE_RULES)
    flow("A. Promises kept: level", [
        ("At least 2 concluded and 80% or more of them kept.", "kept"),
        ("At least one kept.", "partly"),
        ("Any other event in the 12 months: none concluded yet, or none kept.", "promised"),
        ("Otherwise: no promise in the 12 months.", "no_promise"),
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
         "a refusal (refuse to pay, rewrite not agreed), and no plan started and no 100 AED or "
         "more was paid on or after its day (loans: in its month or later). Several "
         "conversations on one day: the strongest is the latest: promise, payment reported, "
         "refusal, dispute, contact, hung up.", "refusal"),
    ], label=lambda _: "One level down")  # fmt: skip
    flow("State: total points = A + B + C", [
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
    s.title("State map", "Every combination of levels and the state it gets.")  # fmt: skip
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
        ("partly", "regular", "no_record", False): "high",
        ("no_promise", "regular", "clean", False): "moderate",
        ("no_promise", "some", "clean", True): "low",
        ("no_promise", "none", "clean", False): "low",
        ("promised", "none", "clean", False): "moderate",
        ("promised", "regular", "clean", False): "high",
        ("promised", "regular", "not_clean", False): "moderate",
    }.items():
        assert state(a, b, c, refusal) == want, (a, b, c, refusal)


# --- examples -------------------------------------------------------------------------------
GRID = 12  # cells per example row
D = dt.date
ONE_PROMISE = [  # (outcome, product, segment, promise day, due, payments, next statement, why)
    ("paid", CARD, S61, D(2026, 3, 10), 800, [(D(2026, 3, 20), 800)], D(2026, 3, 25),
     "One month's due paid before the next statement."),
    ("paid", CARD, S61, D(2026, 3, 10), 800, [(D(2026, 3, 10), 800)], D(2026, 3, 25),
     "Paid on the promise day: it counts."),
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
COUNTING = [  # (events, product, promise days, payments, why); due 800, statement 25 Mar
    (1, CARD, [D(2026, 3, 3), D(2026, 3, 14), D(2026, 3, 20)], [],
     "Nothing paid: every promise up to the 25 Mar deadline joins the first."),
    (2, CARD, [D(2026, 3, 3), D(2026, 3, 14)], [(D(2026, 3, 10), 800)],
     "Paid in full on 10 Mar: the event ends, 14 Mar starts a new one."),
    (1, CARD, [D(2026, 3, 3), D(2026, 3, 14)], [(D(2026, 3, 10), 300)],
     "A partial payment does not end the event."),
    (2, CARD, [D(2026, 3, 20), D(2026, 3, 27)], [],
     "27 Mar is after the 25 Mar deadline: a new event."),
    (1, LOAN, [D(2026, 3, 5), D(2026, 3, 28)], [(D(2026, 3, 31), 800)],
     "Loan cash is known by month: all promises of March are one event."),
]  # fmt: skip
STATEMENT = D(2026, 3, 25)
A_EXAMPLES = [
    ("kept", "KKKKK", "5 concluded, all kept."),
    ("kept", "KXKKKK", "5 of 6 kept (83%)."),
    ("partly", "KXKK", "3 of 4 kept (75%): under 80%."),
    ("partly", "K", "A single promise, kept: one is not a pattern."),
    ("partly", "KKXXP", "2 of 4 kept; the pending event is not counted."),
    ("partly", "XXKXX", "1 of 5 kept: any kept promise counts."),
    ("promised", "X", "A single event, not kept."),
    ("promised", "XX", "2 concluded, none kept."),
    ("promised", "P", "One event, still pending."),
    ("no_promise", "", "No promise in 12 months."),
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
STATE_EXAMPLES = [  # (state, A, B, C, refusal, why)
    ("high", "kept", "regular", "clean", False, "Keeps promises, pays, clean before: 6 points."),
    ("high", "promised", "regular", "clean", False, "Promised and pays: a missed promise still counts."),
    ("moderate", "kept", "regular", "no_record", True, "5 points, one level down for a refusal."),
    ("moderate", "no_promise", "regular", "clean", False, "Pays without promising: 3 points."),
    ("moderate", "promised", "none", "clean", False, "Promised, nothing kept yet, clean before."),
    ("low", "no_promise", "none", "clean", False, "A clean past alone is 1 point."),
    ("low", "no_promise", "some", "clean", True, "2 points, one level down for a refusal."),
    ("low", "no_promise", "none", "no_record", False, "Delinquent with nothing positive on record."),
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

    s.section("A. One event: kept or not", gap=0)
    cases(["Outcome", "Account", "Promise → deadline", "Due", "Paid by the deadline"], [3, 4, 2, 3])
    for want, product, seg, day, due, pays, statement, text in ONE_PROMISE:
        _check(outcome(product, seg, day, due, pays, statement), want, text)
        end = deadline(product, seg, day, statement)
        paid = _paid(product, day, end, pays)
        s.chip(1, want)
        s.text(2, f"{product}, {seg.replace(' DPD', '')}", span=3, align=MID)
        s.text(5, f"{_day(day)} → {_day(end)}", span=4, align=MID)
        s.text(9, due, span=2, align=CENTER, fmt="#,##0")
        s.text(11, paid, span=3, align=CENTER, fmt="#,##0")
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("A. Promises into events (61–180 DPD, due 800, cards' statement 25 Mar)")
    cases(["Events", "Account", "Promises (plans or notes)", "Payments"], [2, 6, 4])
    for want, product, days, pays, text in COUNTING:
        _check(len(events(product, days, 800, pays, STATEMENT)), want, text)
        s.text(1, want, bold=True, align=CENTER)
        s.text(2, product, span=2, align=MID)
        s.text(4, ", ".join(_day(d) for d in days), span=6, align=MID)
        s.text(10, ", ".join(f"{a:,} on {_day(d)}" for d, a in pays) or "–", span=4, align=MID)
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1

    s.section("A. Promises kept: level")
    legend([(KEPT, "kept"), (NOT_KEPT, "not kept"), (PENDING, "pending")])
    for want, cells, text in A_EXAMPLES:
        _check(promises(cells), want, text)
    grid("Level", [str(k) for k in range(1, GRID + 1)], A_EXAMPLES)
    s.note("One cell per event of the last 12 months, oldest first.")

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
    for want, a, b, c, refusal, text in STATE_EXAMPLES:
        _check(state(a, b, c, refusal), want, text)
        s.chip(1, want)
        for col, lev in zip((2, 5, 8), (a, b, c)):
            s.chip(col, lev, _points(lev), span=3)
        s.chip(11, "refusal", "Yes", span=2) if refusal else s.text(11, "–", span=2, align=MID)
        s.text(13, POINTS[a] + POINTS[b] + POINTS[c], align=CENTER)
        s.text(why, text, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.ws.freeze_panes = "B4"


# --- results --------------------------------------------------------------------------------
# Production numbers from the A3 results prompt (bundle_helpers/a3_final/sonnet_a3_results_prompt.md):
# run 2, the persisted tables of the final rules (bundle 28), PROD 2026-11-19.
RESULTS_DATE = "31 August 2026"
PRODUCTS = ["Personal Loans", "Personal Cash Loans", "Auto"]
VARIANTS = (["CC\n61–180", "CC\n180+"]
            + [f"RL 61–180\n{p}" for p in PRODUCTS] + ["RL 61–180\ntotal"]
            + [f"RL 180+\n{p}" for p in PRODUCTS] + ["RL 180+\ntotal"])  # fmt: skip
SEGMENTS = ["CC\n61–180", "CC\n180+", "RL\n61–180", "RL\n180+"]
VINTAGES = [f"{prod}\n{v}" for prod in ("CC 180+", "RL 180+")
            for v in ("early-stage\ncharge-off", "late-stage\ncharge-off")]  # fmt: skip
ACCOUNTS = [19_292, 318_663, 1_397, 1_224, 1_364, 3_985, 33_862, 10_306, 11_203, 55_371]
STATE_COUNTS = {  # variant index -> [High, Moderate, Low]
    0: [2_215, 5_861, 11_216], 1: [2_125, 13_099, 303_439],
    2: [64, 362, 971], 3: [107, 392, 725], 4: [198, 522, 644], 5: [369, 1_276, 2_340],
    6: [150, 904, 32_808], 7: [221, 1_127, 8_958], 8: [147, 732, 10_324],
    9: [518, 2_763, 52_090],
}  # fmt: skip
VINTAGE_ACCOUNTS = [61_112, 257_551, 10_050, 45_321]
VINTAGE_COUNTS = {0: [1_907, 10_601, 48_604], 1: [218, 2_498, 254_835],
                  2: [319, 2_081, 7_650], 3: [199, 682, 44_440]}  # fmt: skip
SEGMENT_ACCOUNTS = [19_292, 318_663, 3_985, 55_371]
POINT_VALUES = range(0, 7)
DETAIL = [  # (section, [(label, tone key)], {segment index: counts})
    ("A. Promises kept", [(_points(k), k) for k in A_LEVELS],
     {0: [620, 4_568, 2_998, 11_106], 1: [227, 4_957, 10_950, 302_529],
      2: [134, 684, 571, 2_596], 3: [73, 858, 1_369, 53_071]}),
    ("B. Payments in delinquency", [(_points(k), k) for k in B_LEVELS],
     {0: [1_445, 3_388, 14_459], 1: [1_150, 17_732, 299_781],
      2: [434, 1_290, 2_261], 3: [548, 3_987, 50_836]}),
    ("C. Record before delinquency",
     [(_points("clean"), "clean"), (_points("not_clean"), "not_clean"),
      ("No record: fewer than 3 months with an amount due", "no_record"),
      ("No record: delinquent since before the history we hold", "no_record")],
     {0: [12_447, 3_864, 2_976, 5], 1: [33_316, 12_605, 99_024, 173_718],
      2: [1_767, 1_777, 441, 0], 3: [10_576, 8_515, 4_096, 32_184]}),
    ("Points total",
     [(f"{p} points", "low" if p < 2 else "moderate" if p < 4 else "high") for p in POINT_VALUES],
     {0: [3_171, 7_668, 3_431, 2_752, 1_534, 619, 117],
      1: [268_919, 34_052, 8_730, 4_747, 1_942, 266, 7],
      2: [804, 1_483, 822, 504, 255, 95, 22],
      3: [41_662, 10_381, 2_049, 752, 417, 100, 10]}),
    ("Refusal and other columns",
     [("Refusal (not lifted)", "bad"),
      ("Refusal that lowers the state (2+ points; under 2 the account is Low anyway)", "bad"),
      ("Refusal lifted by a later plan or payment", "unknown"), ("Dispute", "unknown"),
      ("No pickup after contact", "unknown"), ("Hung up", "unknown")],
     {0: [865, 432, 70, 75, 1_344, 442], 1: [6_514, 558, 447, 570, 2_901, 4_562],
      2: [170, 56, 42, 0, 329, 41], 3: [1_000, 56, 102, 58, 403, 615]}),
]  # fmt: skip
BANDS = {  # (segment, DPD band) -> (High, Moderate, Low)
    ("Credit cards 61–180", "61–90"): (1_032, 1_801, 3_026),
    ("Credit cards 61–180", "91–120"): (609, 1_503, 3_148),
    ("Credit cards 61–180", "121–150"): (345, 1_399, 2_657),
    ("Credit cards 61–180", "151–180"): (229, 1_158, 2_385),
    ("Retail loans 61–180", "61–90"): (202, 505, 694),
    ("Retail loans 61–180", "91–120"): (87, 387, 632),
    ("Retail loans 61–180", "121–150"): (59, 266, 646),
    ("Retail loans 61–180", "151–180"): (21, 118, 368),
    ("Credit cards 180+", "181–360"): (1_086, 5_511, 10_226),
    ("Credit cards 180+", "361–720"): (626, 4_069, 25_017),
    ("Credit cards 180+", "720+"): (413, 3_519, 268_196),
    ("Retail loans 180+", "181–360"): (301, 1_539, 2_086),
    ("Retail loans 180+", "361–720"): (77, 631, 4_140),
    ("Retail loans 180+", "720+"): (140, 593, 45_864),
}
TREND_SEGMENTS = ["Credit cards 61–180", "Retail loans 61–180", "Credit cards 180+",
                  "Retail loans 180+"]  # fmt: skip
TREND_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]  # 2026
TREND = {  # segment -> one (High, Moderate, Low) per month in TREND_MONTHS
    "Credit cards 61–180": [(2_386, 4_571, 7_707), (2_378, 4_454, 7_744), (2_347, 4_413, 7_695),
                            (2_250, 4_656, 7_765), (2_270, 5_244, 8_376), (2_315, 5_512, 9_155),
                            (2_230, 5_805, 10_362), (2_215, 5_861, 11_216)],
    "Retail loans 61–180": [(293, 799, 1_232), (284, 717, 1_212), (293, 731, 1_194),
                            (328, 924, 1_409), (285, 1_080, 1_731), (299, 1_161, 2_054),
                            (326, 1_184, 2_218), (369, 1_276, 2_340)],
    "Credit cards 180+": [(1_776, 12_262, 291_219), (1_843, 12_326, 292_685),
                          (1_899, 12_337, 294_506), (1_954, 12_384, 296_371),
                          (1_986, 12_361, 298_279), (2_070, 12_652, 300_105),
                          (2_099, 12_867, 301_772), (2_125, 13_099, 303_439)],
    "Retail loans 180+": [(458, 2_363, 49_836), (457, 2_359, 50_066), (449, 2_348, 50_473),
                          (460, 2_308, 50_847), (485, 2_408, 51_113), (509, 2_556, 51_318),
                          (515, 2_626, 51_678), (518, 2_763, 52_090)],
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


def _bands(s: Sheet) -> None:
    s.header(["", "Accounts", "", "High", "share", "Moderate", "share", "Low", "share"])
    s.ws.merge_cells(start_row=s.r - 1, start_column=2, end_row=s.r - 1, end_column=3)
    for (seg, band), counts in BANDS.items():
        s.text(1, f"{seg} · {band} DPD")
        s.text(2, f"=D{s.r}+F{s.r}+H{s.r}", span=2, bold=True, fmt="#,##0")
        for col, n in zip((4, 6, 8), counts):
            _pair(s, col, count=n, base=f"$B{s.r}")
        s.r += 1


def trend(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results trend"), [10, 10] + [10, 7] * len(STATES))
    s.title("Results trend", "Accounts per state at every month end of 2026. Shares are of the "
                             "month's accounts.")  # fmt: skip
    for i, seg in enumerate(TREND_SEGMENTS):
        s.section(seg, gap=0 if i == 0 else 1)
        s.text(1, "Month", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.text(2, "Accounts", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, st in enumerate(STATES):
            s.chip(3 + 2 * j, st, span=2, align=CENTER)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
        for month, counts in zip(TREND_MONTHS, TREND[seg]):
            s.text(1, f"{month} 2026", bold=True)
            s.text(2, "=" + "+".join(f"{get_column_letter(3 + 2 * j)}{s.r}" for j in range(3)),
                   bold=True, fmt="#,##0")  # fmt: skip
            for j, n in enumerate(counts):
                _pair(s, 3 + 2 * j, count=n, base=f"$B{s.r}")
            s.r += 1
    s.r += 1
    s.note("High holds steady in count while the 61–180 buckets fill from May (loans: 2,218 "
           "accounts in March, 3,985 in August), so its share falls: new entrants have no "
           "promise or payment record in this delinquency yet. Loans 61–180 High: 13.2% in March, "
           "9.3% in August.")  # fmt: skip
    s.ws.freeze_panes = "A4"


def vintage(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results 180+ vintage"), [16] + [12, 7] * len(VINTAGES))
    s.title("Results 180+ by vintage",
            "Early-stage charge-off = charged off less than 2 years ago; late-stage = 2 years or "
            f"more; {RESULTS_DATE}. Shares are within each vintage.")  # fmt: skip
    s.section("Credibility state", gap=0)
    _state_table(s, VINTAGES, VINTAGE_ACCOUNTS, VINTAGE_COUNTS, {})
    s.ws.freeze_panes = "B6"


def results(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results"), [30] + [11, 7] * len(VARIANTS))
    s.title("Results", f"Accounts per state, {RESULTS_DATE} (production, final rules). Pale yellow = "
                       "from the run; shares and totals are calculated.")  # fmt: skip
    s.section("State by product", gap=0)
    _state_table(s, VARIANTS, ACCOUNTS, STATE_COUNTS, {})
    s.section("State by DPD band (shares of the band)")
    _bands(s)
    s.note("Cards at 180+: the DPD band is taken from the charge-off age.")
    s.ws.freeze_panes = "B4"


def detail(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results detail"), [44] + [11, 7] * len(SEGMENTS))
    s.title("Results detail", f"What sits behind the states, {RESULTS_DATE}. Shares are "
                              "of all accounts in the segment.")  # fmt: skip
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
                L = get_column_letter(2 + 2 * b)
                _pair(s, 2 + 2 * b, count=data[b][i] if b in data else None, base=f"{L}${base}")
            s.r += 1
    s.r += 1
    s.note("At 180+ most accounts have no promise, no payment and no record (0 points: 84% of "
           "cards, 75% of loans); most of them were delinquent before the history we hold. The "
           "dispute count on loans at 61–180 is 0: the loan dispute code is being checked.")  # fmt: skip
    s.ws.freeze_panes = "B5"


# --- validation -----------------------------------------------------------------------------
BOOKS = ["Cards 61–180", "Loans 61–180", "Cards 180+", "Loans 180+"]
# Run 2: month ends January to May 2026 pooled, outcomes over the 3 months after each.
OUTCOME_MONTHS = "January to May 2026"
OUTCOMES = {  # book -> (n H, n M, n L, paid a due H, M, L, any payment H, M, L)
    "Cards 61–180": (11_631, 23_338, 39_287, 54.9, 22.7, 6.3, 57.0, 25.0, 6.9),
    "Loans 61–180": (1_483, 4_251, 6_778, 64.5, 48.2, 18.6, 71.5, 58.6, 26.1),
    "Cards 180+": (9_458, 61_670, 1_473_060, 36.8, 22.3, 1.2, 40.3, 27.6, 1.6),
    "Loans 180+": (2_309, 11_786, 252_335, 53.4, 24.7, 1.0, 57.2, 31.1, 1.6),
}
BY_GROUP = {  # (book, split, group) -> paid a due H, M, L
    ("Cards 61–180", "DPD", "61–90"): (56.8, 31.4, 11.4),
    ("Cards 61–180", "DPD", "91–120"): (60.3, 24.6, 7.2),
    ("Cards 61–180", "DPD", "121–150"): (52.2, 19.0, 4.5),
    ("Cards 61–180", "DPD", "151–180"): (31.8, 8.8, 1.5),
    ("Loans 61–180", "DPD", "61–90"): (70.8, 56.2, 28.3),
    ("Loans 61–180", "DPD", "91–120"): (62.9, 50.0, 16.8),
    ("Loans 61–180", "DPD", "121–150"): (55.3, 36.5, 11.2),
    ("Loans 61–180", "DPD", "151–180"): (44.7, 30.7, 12.3),
    ("Loans 61–180", "Product", "Personal Loans"): (64.5, 35.8, 12.0),
    ("Loans 61–180", "Product", "Personal Cash Loans"): (67.7, 47.1, 16.3),
    ("Loans 61–180", "Product", "Auto"): (62.3, 59.4, 35.9),
    ("Cards 180+", "DPD", "181–360"): (13.5, 9.2, 3.1),
    ("Cards 180+", "DPD", "361–720"): (53.7, 22.6, 2.6),
    ("Cards 180+", "DPD", "720+"): (66.8, 44.3, 1.0),
    ("Loans 180+", "DPD", "181–360"): (44.6, 18.6, 5.8),
    ("Loans 180+", "DPD", "361–720"): (59.3, 22.9, 3.1),
    ("Loans 180+", "DPD", "720+"): (68.0, 41.2, 0.6),
    ("Loans 180+", "Product", "Personal Loans"): (59.5, 30.6, 0.7),
    ("Loans 180+", "Product", "Personal Cash Loans"): (51.1, 23.4, 2.1),
    ("Loans 180+", "Product", "Auto"): (50.4, 19.0, 1.2),
    ("Cards 180+", "Vintage", "Early-stage charge-off"): (33.6, 16.6, 2.5),
    ("Cards 180+", "Vintage", "Late-stage charge-off"): (67.1, 45.9, 0.9),
    ("Loans 180+", "Vintage", "Early-stage charge-off"): (45.2, 18.0, 3.5),
    ("Loans 180+", "Vintage", "Late-stage charge-off"): (68.4, 44.4, 0.6),
}
GROUPS = list(BY_GROUP)
AUC = {  # book -> (state, lowest DPD band, highest DPD band, points)
    "Cards 61–180": ("0.771", "0.732", "0.791", "0.783"),
    "Loans 61–180": ("0.701", "0.655", "0.715", "0.730"),
    "Cards 180+": ("0.728", "0.657", "0.769", "0.861"),
    "Loans 180+": ("0.790", "0.713", "0.755", "0.890"),
}
POINTS_PAID = {  # points -> paid a due % per book (BOOKS order)
    0: (4.9, 9.5, 0.5, 0.4), 1: (6.6, 23.6, 8.0, 3.9), 2: (19.0, 42.4, 17.0, 19.7),
    3: (26.1, 54.9, 30.2, 35.9), 4: (46.8, 61.5, 33.9, 48.1), 5: (64.5, 66.6, 53.4, 70.9),
    6: (70.3, 89.5, 60.5, 74.1),
}  # fmt: skip
STABILITY = {  # book -> same, up, down, High stays, Moderate stays (%)
    "Cards 61–180": (88.3, 5.1, 6.6, 80.7, 80.4),
    "Loans 61–180": (86.7, 6.0, 7.3, 77.9, 79.4),
    "Cards 180+": (99.2, 0.3, 0.4, 85.9, 88.8),
    "Loans 180+": (99.1, 0.4, 0.5, 87.1, 89.3),
}
OVERLAP = {  # book -> Cramér's V with ability, reachability, location, deterioration
    "Cards 61–180": (0.163, 0.244, 0.214, 0.457),
    "Loans 61–180": (0.099, 0.209, 0.210, 0.405),
    "Cards 180+": (0.198, 0.283, 0.237, 0.293),
    "Loans 180+": (0.256, 0.313, 0.245, 0.235),
}
HML = {2: "good", 3: "mid", 4: "bad"}


def _pc(x: float | None) -> str | None:
    return None if x is None else f"{x:.1f}%"


def _blank(n: int) -> tuple:
    return (None,) * n


def validation(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Validation"), [20, 22, 15, 15, 15, 15, 15, 15])
    s.title("Validation", f"What each state goes on to do: month ends {OUTCOME_MONTHS or '…'}, "
                          "outcomes over the following 3 months. Paid a due = payments reach one "
                          "month's due; any payment = 100 AED or more.")  # fmt: skip
    for i, (book, v) in enumerate(OUTCOMES.items()):
        s.section(f"Outcome by state, {book}", gap=0 if i == 0 else 1)
        s.header(["State", "Account-months", "Paid a due", "Any payment"])
        for j, st in enumerate(STATES):
            s.chip(1, st)
            s.text(2, v[j], align=MID, fmt="#,##0")
            s.text(3, v[3 + j] / 100, align=MID, fmt="0.0%")
            s.text(4, v[6 + j] / 100, align=MID, fmt="0.0%")
            s.r += 1
    s.note("High pays a due 3 to 9 times as often as Low at 61–180 and 20 to 50 times at 180+; "
           "Moderate sits in between in every book.")  # fmt: skip
    s.section("Paid a due by group")
    s.header(["Book", "Group", "High", "Moderate", "Low"], [1, 1, 1, 1, 1])
    for key in GROUPS:
        book, split, group = key
        s.row([book, f"{split}: {group}", *map(_pc, BY_GROUP.get(key, _blank(3)))], align=MID,
              tones=HML)  # fmt: skip

    s.note("High > Moderate > Low in every group. Thin gaps: Auto loans at 61–180 (High 62.3%, "
           "Moderate 59.4%) and cards at 181–360 DPD, where the band comes from the charge-off "
           "age.")  # fmt: skip
    s.section("Ranking power (AUC on paid a due; 0.5 = chance)")
    s.header(["Book", "State", "State, weakest\nDPD band", "State, strongest\nDPD band",
              "Points total"], [1, 1, 2, 2, 2], height=30)  # fmt: skip
    for book in BOOKS:
        s.row([book, *AUC.get(book, _blank(4))], [1, 1, 2, 2, 2], align=MID)

    s.section("Paid a due by points total")
    s.header(["Points", "State (no refusal)", *BOOKS])
    for pts in POINT_VALUES:
        s.text(1, pts, bold=True, align=CENTER)
        s.chip(2, state_of_points(pts))
        for col, v in enumerate(POINTS_PAID.get(pts, _blank(len(BOOKS))), 3):
            s.text(col, _pc(v), align=MID)
        s.r += 1

    s.note("Each extra point pays more. At 180+ 0 and 1 point are both Low but pay 0.5% and 8.0% "
           "(cards), 0.4% and 3.9% (loans): the points total ranks better than the state there "
           "(AUC 0.861 / 0.890 against 0.728 / 0.790). 6 points at 180+ and on loans: under 80 "
           "accounts.")  # fmt: skip
    s.section("Stability, one month to the next")
    s.header(["Book", "Same state", "Up", "Down", "High stays", "Moderate stays"])
    for book in BOOKS:
        s.row([book, *map(_pc, STABILITY.get(book, _blank(5)))], align=MID)

    s.section("Overlap with the other axes (Cramér's V; 0 = unrelated, 1 = the same axis)")
    s.header(["Book", "Ability", "Reachability", "Location", "Deterioration"])
    for book in BOOKS:
        vals = OVERLAP.get(book, _blank(4))
        s.row([book, *(None if v is None else f"{v:.2f}" for v in vals)], align=MID)
    s.note("A3 overlaps deterioration most (it shares the payment history) and ability least: "
           "each axis adds its own view.")  # fmt: skip
    s.ws.freeze_panes = "A4"


# --- sensitivity ----------------------------------------------------------------------------
# Back-tests on month ends March–May 2026 (outcome: paid a due in the next 3 months), run on
# the promise counting before the event rule; they chose the points and the deadline.
POINT_SCHEMES = [  # book, state AUC earlier / model points, mix H / M / L earlier, model (61–180)
    ("Cards 61–180", 0.692, 0.751, (4.0, 21.7, 74.3), (11.8, 32.9, 55.3)),
    ("Loans 61–180", 0.643, 0.688, (3.8, 26.4, 69.8), (11.0, 33.7, 55.3)),
    ("Cards 180+", 0.665, 0.748, None, None),
    ("Loans 180+", 0.736, 0.783, None, None),
]
DEADLINES = [  # book, state AUC with the model points: model deadline, 30 days
    ("Cards 61–180", "Next statement", 0.751, 0.756),
    ("Loans 61–180", "End of the promise month", 0.688, 0.692),
    ("Cards 180+", "End of the promise month", 0.748, 0.748),
    ("Loans 180+", "End of the promise month", 0.783, 0.783),
]
PROMISE_PAID = [  # book, paid a due %: Kept, Partly, Broken, Promised (one not kept), No promise
    ("Cards 61–180", 38.4, 32.9, 28.5, 24.0, 8.2),
    ("Loans 61–180", 58.0, 53.9, 47.9, 42.9, 25.3),
    ("Cards 180+", 21.1, 30.5, 17.6, 21.0, 1.3),
    ("Loans 180+", 36.6, 43.5, 19.8, 20.4, 1.6),
]
BROKEN = [  # book, paid a due %: Broken with a kept promise, Partly kept; difference pp, 95% interval; AUC with, without
    ("Cards 61–180", 34.8, 34.1, "+0.6", "−1.0 to +2.3", "0.763", "0.769"),
    ("Loans 61–180", 53.0, 52.7, "+0.3", "−5.1 to +5.7", "0.698", "0.701"),
    ("Cards 180+", 17.5, 29.5, "−12.0", "−13.6 to −10.3", "0.724", "0.725"),
    ("Loans 180+", 22.0, 41.1, "−19.0", "−23.6 to −13.8", "0.790", "0.790"),
]
SAME_DAY = [  # book, promises kept by a payment on the promise day, share of not kept, rows up, their paid a due
    ("Cards 61–180", "777", "8.6%", "1,745", "33.5%"),
    ("Cards 180+", "1,329", "17.9%", "3,561", "41.8%"),
    ("Loans 61–180", "<10", "–", "<10", "–"),
    ("Loans 180+", "<10", "–", "14", "–"),
]
NO_EVIDENCE = [  # book, share of accounts, paid a due %: no evidence, rest of Low, Moderate
    ("Cards 61–180", 12.2, 3.9, 12.4, 35.2),
    ("Loans 61–180", 7.0, 9.2, 28.1, 54.2),
    ("Cards 180+", 83.0, 0.5, 7.6, 30.6),
    ("Loans 180+", 65.1, 0.2, 3.9, 32.5),
]


def sensitivity(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Sensitivity"), [20, 26, 16, 16, 16, 16, 16])
    s.title("Sensitivity", "Why the promise points and the deadline are what they are. Back-tests "
                           "on month ends March to May 2026, outcome: paid a due in the following "
                           "3 months.")  # fmt: skip
    s.section("Paid a due by promise level", gap=0)
    s.header(["Book", *(LABEL[k] for k in ("kept", "partly", "broken", "promised", "no_promise"))],
             [2, 1, 1, 1, 1, 1])  # fmt: skip
    for book, *vals in PROMISE_PAID:
        s.row([book, *map(_pc, vals)], [2, 1, 1, 1, 1, 1], align=MID)
    s.note("Customers who never promised pay least by far. A broken record pays like a single "
           "promise not kept: what separates is promising at all, so every promise earns a "
           "point and keeping it earns more. Broken is no longer a level (2026-11-18): Broken "
           "accounts with a kept promise pay like Partly kept at 61–180 (below).")  # fmt: skip

    s.section("Promise points")
    s.header(["Book", "State AUC:\nearlier points", "State AUC:\nmodel points"], [2, 1, 1],
             height=30)  # fmt: skip
    for book, a, b, _, _ in POINT_SCHEMES:
        s.row([book, f"{a:.3f}", f"{b:.3f}"], [2, 1, 1], align=MID)
    s.note("Earlier points: Kept 2, Partly kept 1, Broken −1.")
    s.r += 1
    s.header(["Book", "Points", "High", "Moderate", "Low"], [2, 1, 1, 1, 1])
    for book, _, _, m0, m1 in POINT_SCHEMES:
        for name, mix in (("Earlier", m0), ("Model", m1)):
            if mix:
                s.row([book, name, *map(_pc, mix)], [2, 1, 1, 1, 1], align=MID,
                      tones={2: "good", 3: "mid", 4: "bad"})  # fmt: skip
    s.note("The model points rank customers better in every book; at 61–180 also in every "
           "month, DPD band and loan product. High and Moderate then hold 78% of the money "
           "collected from cards at 61–180, against 53%.")  # fmt: skip

    s.section("Promise deadline (model points)")
    s.header(["Book", "Model deadline", "State AUC:\nmodel deadline", "State AUC:\n30 days"],
             [2, 1, 1, 1], height=30)  # fmt: skip
    for book, name, a, b in DEADLINES:
        s.row([book, name, f"{a:.3f}", f"{b:.3f}"], [2, 1, 1, 1], align=MID)
    s.note("With the model points the deadline barely matters (at most 0.005), so GRR's rule "
           "stays.")  # fmt: skip

    s.section("Broken as a level (run 1, 18 Nov 2026)")
    s.header(["Book", "Paid a due:\nBroken, kept one", "Paid a due:\nPartly kept",
              "Difference\n(pp)", "95% interval\n(pp)", "State AUC:\nwith Broken",
              "State AUC:\nwithout"], height=44)  # fmt: skip
    for book, a, b, d, ci, w, wo in BROKEN:
        s.row([book, _pc(a), _pc(b), d, ci, w, wo], align=MID)
    s.note("At 61–180 a broken record with a kept promise pays like Partly kept; at 180+ it pays "
           "less, but dropping Broken ranks no worse in any book. One rule for all: no Broken "
           "level.")  # fmt: skip

    s.section("A payment on the promise day (run 1)")
    s.header(["Book", "Promises it keeps", "Share of the\nnot-kept ones", "Rows that move up",
              "Paid a due:\nrows that move"], [2, 1, 1, 1, 1], height=30)  # fmt: skip
    for row in SAME_DAY:
        s.row(list(row), [2, 1, 1, 1, 1], align=MID)
    s.note("The rows it moves up pay like Moderate and High do, so a payment on the promise day "
           "counts. Loans are known by month, so they barely change.")  # fmt: skip

    s.section("Low with no evidence in any dimension")
    s.header(["Book", "Share of accounts", "Paid a due:\nno evidence",
              "Paid a due:\nrest of Low", "Paid a due:\nModerate"], [2, 1, 1, 1, 1],
             height=30)  # fmt: skip
    for book, *vals in NO_EVIDENCE:
        s.row([book, *map(_pc, vals)], [2, 1, 1, 1, 1], align=MID)
    s.note("No promise, no payment and no record: they pay least, so they are Low.")  # fmt: skip
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
