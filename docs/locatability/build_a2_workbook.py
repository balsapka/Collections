"""Build the A2 locatability model document (business-facing).

    python build_a2_workbook.py [--out a2_locatability_reference.xlsx] [--scoring-date "Nov 2026"]

The rules follow ``workplace_mirror/specs/A2_locatability_spec.md``. Every worked example is
run through the reference rules below and the build FAILS if an example no longer gets the
state it illustrates. Results are entry cells (pale yellow) until the pipelines have run;
shares, totals and coverage are formulas.

Design: one colour meaning everywhere — green favourable, red adverse, grey unknown,
charcoal deceased; navy is structure only.
"""
from __future__ import annotations

import argparse
import math
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# --- rules (reference implementation, monthly granularity) ---------------------------------
WINDOW = {"61–180 DPD": 3, "180+ DPD": 6}  # months, the scoring month included
TRAVEL_GAP = 3  # months: last UAE evidence at most this long after the last ticket
SILENCE = 1  # months without UAE evidence before the travel rule fires
GONE_DARK_DAYS = 3
UAE, ABROAD, TRAVEL, EXIT = "U", "F", "T", "X"
ANSWERED, CALLED_IN, RANG_OUT, DEAD_LINE, CONNECTED = "A", "I", "R", "D", "C"


def _recent(offset: int, months: int) -> bool:
    """``offset`` 0 = the scoring month, -1 the month before, …"""
    return offset > -months


def _last(events: list[tuple[int, str]], kinds: tuple[str, ...]) -> int | None:
    return max((o for o, k in events if k in kinds), default=None)


def location(events: list[tuple[int, str]], w: int) -> str:
    uae, foreign, travel = _last(events, (UAE,)), _last(events, (ABROAD, EXIT)), _last(events, (TRAVEL,))
    if foreign is not None and (uae is None or foreign >= uae):
        return "skip"
    if travel is not None and (uae is None or (uae <= travel + TRAVEL_GAP and uae <= -SILENCE)):
        return "skip"
    return "in_country" if uae is not None and _recent(uae, w) else "unknown"


def reachability(calls: list[tuple[int, str]], w: int) -> str:
    """One entry per call day, oldest first (a day with any answer is A)."""
    attempts = [i for i, (_, k) in enumerate(calls) if k != CALLED_IN]
    last = attempts[-GONE_DARK_DAYS:]
    if len(last) == GONE_DARK_DAYS and all(calls[i][1] in (RANG_OUT, DEAD_LINE) for i in last):
        first = last[0]
        contact_after = any(k in (ANSWERED, CALLED_IN) for _, k in calls[first + 1:])
        if _recent(calls[first][0], w) and not contact_after:
            return "non_reachable"
    if any(k in (ANSWERED, CALLED_IN) and _recent(o, w) for o, k in calls):
        return "reachable"
    return "unknown"


# --- design system -------------------------------------------------------------------------
FONT = "Arial"
NAVY, INK, MUTED, RULE, PANEL = "1F3864", "262626", "7F7F7F", "D9D9D9", "F2F2F2"
TONE = {  # (fill, text)
    "good": ("E2EFDA", "375623"),
    "bad": ("FBE2D5", "9C2B12"),
    "unknown": ("EDEDED", "595959"),
    "deceased": ("404040", "FFFFFF"),
}
STATE_TONE = {"in_country": "good", "reachable": "good", "skip": "bad",
              "non_reachable": "bad", "unknown": "unknown", "deceased": "deceased"}
LABEL = {"in_country": "In Country", "skip": "Skip", "reachable": "Reachable",
         "non_reachable": "Non-Reachable", "unknown": "Unknown", "deceased": "Deceased"}
CODE_TONE = {UAE: "good", ANSWERED: "good", CALLED_IN: "good", CONNECTED: "unknown",
             ABROAD: "bad", TRAVEL: "bad", EXIT: "bad", RANG_OUT: "bad", DEAD_LINE: "bad"}
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


def _fit(ws: Worksheet, row: int, texts: list[tuple[str, float]], floor: float = 20) -> None:
    """Row height for wrapped ``(text, column width)`` pairs."""
    lines = max(math.ceil(len(str(t or "")) / max(w * 1.1, 1)) for t, w in texts) or 1
    ws.row_dimensions[row].height = max(floor, 13.5 * lines + 6)


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
        return sum(self.widths[c1 - 1:c2])

    def merge(self, c1: int, c2: int, row: int | None = None) -> None:
        if c2 > c1:
            row = row or self.r
            self.ws.merge_cells(start_row=row, start_column=c1, end_row=row, end_column=c2)

    def title(self, text: str, lead: str) -> None:
        self.ws["A1"] = text
        self.ws["A1"].font = _font(size=16, bold=True, color=NAVY)
        self.ws["A2"] = lead
        self.ws["A2"].font = _font(color=MUTED, italic=True)
        self.ws["A2"].alignment = TOP
        self.merge(1, self.last, 2)
        _fit(self.ws, 2, [(lead, self.width(1, self.last))])
        self.r = 4

    def section(self, text: str, gap: int = 1) -> None:
        self.r += gap
        self.ws.cell(row=self.r, column=1, value=text).font = _font(size=11, bold=True, color=NAVY)
        for col in range(1, self.last + 1):
            self.ws.cell(row=self.r, column=col).border = Border(bottom=Side(style="medium", color=NAVY))
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
             fill: str | None = None, align: Alignment = TOP, border: bool = True):
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

    def chip(self, col: int, state: str, label: str | None = None, span: int = 1):
        fill, ink = TONE[STATE_TONE[state]]
        return self.text(col, label or LABEL[state], span=span, bold=True, color=ink,
                         fill=fill, align=MID)

    def note(self, text: str) -> None:
        self.text(1, text, span=self.last, color=MUTED, border=False)
        self.ws.cell(row=self.r, column=1).font = _font(color=MUTED, italic=True)
        _fit(self.ws, self.r, [(text, self.width(1, self.last))], floor=16)
        self.r += 1


# --- content -------------------------------------------------------------------------------
LOC = ["in_country", "skip", "unknown"]
REACH = ["reachable", "non_reachable", "unknown"]
COMBINED = [(lo, re) for lo in LOC for re in REACH]
ACTION = {
    ("in_country", "reachable"): "Negotiate; ability and credibility set the offer.",
    ("in_country", "non_reachable"): "Skip-trace the number; field visit.",
    ("in_country", "unknown"): "Keep calling.",
    ("skip", "reachable"): "Remote settlement; international payment route.",
    ("skip", "non_reachable"): "International recovery agency; legal.",
    ("skip", "unknown"): "Verify the departure.",
    ("unknown", "reachable"): "Negotiate and confirm where they are.",
    ("unknown", "non_reachable"): "Skip-trace the customer and the number.",
    ("unknown", "unknown"): "Data gap: act on the other persona axes.",
}


def overview(wb: Workbook, scoring: str) -> None:
    s = Sheet(wb.active, [24, 32, 32, 32])
    s.ws.title = "Overview"
    s.title("A2 Locatability",
            "Can we find the customer, and can we reach them? Two independent dimensions and a "
            "deceased override; every account in scope gets a value on each.")
    for k, v in [
        ("Scope", "Credit cards and retail loans (Personal Loans, Personal Cash Loans, Auto) at "
                  f"61–180 DPD and 180+ DPD{f', {scoring}' if scoring else ''}."),
        ("Location", "Where the customer is, from what they do: logins, in-person card use, "
                     "travel purchases and collector notes."),
        ("Reachability", "Whether our calls get through, from the collections call log."),
        ("Principle", "On both dimensions the latest evidence wins."),
    ]:
        s.text(1, k, bold=True, color=NAVY, border=False)
        s.text(2, v, span=3, border=False)
        _fit(s.ws, s.r, [(v, s.width(2, 4))], floor=18)
        s.r += 1
    s.section("States")
    s.header(["State", "Dimension", "Meaning"], [1, 1, 2])
    for st, dim, meaning in [
        ("in_country", "Location", "The latest evidence places the customer in the UAE, recently."),
        ("skip", "Location", "The latest evidence places the customer abroad (however old), or they went silent soon after buying a ticket."),
        ("unknown", "Location", "No evidence, or the latest UAE evidence is older than the window."),
        ("reachable", "Reachability", "We were in contact with the customer recently."),
        ("non_reachable", "Reachability", "The last 3 days we called all failed, with no confirmed contact since."),
        ("unknown", "Reachability", "Not enough recent call evidence either way."),
        ("deceased", "Override", "Reported deceased. Overrides both dimensions."),
    ]:
        s.chip(1, st)
        s.text(2, dim, color=MUTED, align=MID)
        s.text(3, meaning, span=2, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    s.section("Combined state and the action it points to")
    s.text(1, "Location \\ Reachability", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
    for j, re in enumerate(REACH, 2):
        s.chip(j, re).alignment = CENTER
    s.ws.row_dimensions[s.r].height = 20
    s.r += 1
    for lo in LOC:
        s.chip(1, lo)
        for j, re in enumerate(REACH, 2):
            s.text(j, ACTION[(lo, re)], align=MID)
        s.ws.row_dimensions[s.r].height = 30
        s.r += 1
    s.chip(1, "deceased")
    s.text(2, "Estate or insurance process.", span=3, align=MID)
    s.ws.row_dimensions[s.r].height = 20
    s.r += 2
    s.note("9 combinations + Deceased = 10 combined states. Rules: 'Logic'. Shares: 'Results'.")
    s.ws.freeze_panes = "A4"


def logic(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Logic"), [24, 56, 16, 26])

    def flow(title: str, steps: list[tuple[str, str]]) -> None:
        s.section(title)
        for i, (rule, st) in enumerate(steps, 1):
            s.text(1, f"Rule {i}", bold=True, color=NAVY, fill=PANEL, align=CENTER)
            s.text(2, rule, span=2, fill=PANEL, align=MID)
            s.chip(4, st)
            _fit(s.ws, s.r, [(rule, s.width(2, 3))], floor=22)
            s.r += 1

    s.title("Logic", "What the model computes for each account at the scoring date, and the rules "
                     "that turn it into states. Within a dimension, the first rule that holds decides.")
    s.section("Evidence", gap=0)
    s.header(["Event", "", "Counts as", "Dimension"], [1, 1, 1, 1])
    s.merge(1, 2, s.r - 1)
    for event, counts_as, tone, dim in [
        ("Login from the UAE (digital banking)", "UAE evidence", "good", "Location"),
        ("In-person card use in the UAE, on any of the customer's cards and accounts: credit card "
         "cash / ATM or a purchase at a grocery, fuel, restaurant, pharmacy, transport or "
         "department store; debit card shop-terminal payment or ATM withdrawal",
         "UAE evidence", "good", "Location"),
        ("Login from abroad", "Foreign evidence", "bad", "Location"),
        ("The same in-person card use, abroad", "Foreign evidence", "bad", "Location"),
        ("Collector note: customer left the country (final exit visa included)",
         "Foreign evidence", "bad", "Location"),
        ("Travel purchase (airline, cruise, travel agency), any channel, any card",
         "Departure signal", "bad", "Location"),
        ("Customer called us, a call marked successful, or a result only the customer can give "
         "(promise to pay, dispute, settlement request, …)", "Confirmed contact", "good",
         "Reachability"),
        ("A day we called and every call rang out, went unanswered (message left included) or "
         "hit a dead line (switched off, wrong or invalid number)", "Failed call day", "bad",
         "Reachability"),
        ("A call that connected but was not marked successful, or busy", "Neutral call day",
         "unknown", "Reachability"),
        ("Collector note of death (claims included), card blocked as deceased (Way4 block D), "
         "or customer record marked deceased", "Deceased", "deceased", "Override"),
    ]:
        s.text(1, event, span=2, align=MID)
        fill, ink = TONE[tone]
        s.text(3, counts_as, bold=True, color=ink, fill=fill, align=MID)
        s.text(4, dim, color=MUTED, align=MID)
        _fit(s.ws, s.r, [(event, s.width(1, 2))])
        s.r += 1
    s.note("Every event is dated and counts at any age; the rules decide how recent it must be. "
           "A ticket is bought weeks before the flight, so it is not compared with UAE activity by "
           "date: it is used only by the travel rule (Location, rule 2). Ignored: logins with no "
           "country, online purchases, transfers and remittances, incoming money, salary, and "
           "collector admin entries (result not found, follow up, e-mail sent, legal / "
           "repossession, skip-trace status).")
    s.section("Features")
    s.header(["Feature", "Definition", "", "Dimension"], [1, 1, 1, 1])
    s.merge(2, 3, s.r - 1)
    for feat, definition, dim in [
        ("Latest UAE evidence", "Date of the most recent UAE evidence.", "Location"),
        ("Latest foreign evidence", "Date of the most recent foreign evidence.", "Location"),
        ("Last travel purchase", "Date of the most recent departure signal.", "Location"),
        ("Last confirmed contact", "Date of the most recent confirmed contact with the customer.",
         "Reachability"),
        ("Last 3 call days", "The 3 most recent days we called, each failed or not.", "Reachability"),
        ("Deceased flag", "Any deceased evidence, at any date.", "Override"),
    ]:
        s.text(1, feat, bold=True, align=MID)
        s.text(2, definition, span=2, align=MID)
        s.text(4, dim, color=MUTED, align=MID)
        s.ws.row_dimensions[s.r].height = 20
        s.r += 1
    flow("Location", [
        ("There is foreign evidence, and it is on or after the date of the latest UAE "
         "evidence (on the same day, foreign wins).", "skip"),
        ("Travel rule: the latest UAE evidence is at most 3 months after the last travel purchase "
         "(or there is none), and no UAE evidence for at least 1 month since.", "skip"),
        ("The latest evidence is UAE evidence within the window.", "in_country"),
        ("Otherwise: no evidence at all, or the latest UAE evidence is older than the window.",
         "unknown"),
    ])
    flow("Reachability", [
        ("Last 3 call days all failed, the oldest within the window, and no confirmed contact since.",
         "non_reachable"),
        ("The last confirmed contact with the customer (they called us, a call marked successful, "
         "or a result only the customer can give) is within the window.", "reachable"),
        ("Otherwise.", "unknown"),
    ])
    flow("Deceased", [("Deceased flag is set, at any date. Overrides both dimensions.", "deceased")])
    s.section("Parameters")
    s.header(["Parameter", "Value", "Why"], [1, 2, 1])
    for p, v, why in [
        ("Window", "3 months at 61–180 DPD, 6 months at 180+ DPD (scoring month included).",
         "Same as the other axes; activity is thinner at 180+."),
        ("Foreign evidence", "No age limit.", "No sign of return means still abroad."),
        ("Travel rule: gap", "UAE activity ends at most 3 months after the ticket.",
         "Covers 82% (cards) / 84% (loans) of known leavers, about 5% of stayers."),
        ("Travel rule: silence", "At least 1 month without UAE evidence.",
         "Keeps a customer who just bought a ticket and is still active out of Skip."),
        ("Failed call days", "The last 3 call days.",
         "Fewer is not a pattern. 86% of accounts have 6+ call days in 3 months; sensitivity "
         "1–10 days under check."),
        ("Confirmed contacts for Reachable", "1 is enough.", "One recent confirmed contact shows they can be reached."),
    ]:
        s.text(1, p, bold=True)
        s.text(2, v, span=2)
        s.text(4, why, color=MUTED)
        _fit(s.ws, s.r, [(v, s.width(2, 3)), (why, s.width(4, 4))])
        s.r += 1
    s.ws.freeze_panes = "A4"


LOC_EXAMPLES = [
    ("in_country", [(-6, ABROAD), (-1, UAE)], "Abroad 6 months ago; card used in the UAE last month."),
    ("in_country", [(-4, EXIT), (0, UAE)], "Collector noted a departure; UAE login since."),
    ("in_country", [(0, TRAVEL), (0, UAE)], "Bought a flight this month and still active: not silent yet."),
    ("in_country", [(-7, TRAVEL), (-3, UAE), (-1, UAE)], "Flight bought, active for months after: back or never left."),
    ("skip", [(-3, UAE), (-1, ABROAD)], "Latest login is from abroad."),
    ("skip", [(-8, ABROAD)], "Last seen abroad 8 months ago, nothing since."),
    ("skip", [(-2, TRAVEL), (-1, UAE)], "Flight bought, UAE activity stopped a month later, silent since."),
    ("skip", [(-5, TRAVEL), (-3, UAE), (-2, UAE)], "UAE activity ran 3 months past the ticket, then stopped."),
    ("unknown", [(-10, TRAVEL), (-5, UAE)], "Active long after the flight, then quiet beyond the window."),
    ("unknown", [], "No evidence at all."),
]
REACH_EXAMPLES = [
    ("reachable", [(-1, ANSWERED)], "Answered last month."),
    ("reachable", [(-2, CALLED_IN)], "Called us; no outbound calls needed."),
    ("reachable", [(-2, RANG_OUT), (-1, RANG_OUT), (0, RANG_OUT), (0, CALLED_IN)],
     "3 failed days, then the customer called us."),
    ("non_reachable", [(-2, ANSWERED), (-1, RANG_OUT), (-1, DEAD_LINE), (0, RANG_OUT)],
     "Answered once, then 3 failed days."),
    ("unknown", [(-1, RANG_OUT), (-1, CONNECTED), (0, RANG_OUT), (0, DEAD_LINE)],
     "A connected call breaks the failed run; no contact on record."),
    ("unknown", [(-4, ANSWERED), (-1, RANG_OUT), (0, DEAD_LINE)],
     "Last contact older than the window; only 2 failed days."),
    ("unknown", [(-6, RANG_OUT), (-5, RANG_OUT), (-4, RANG_OUT)], "Failed days, all older than the window."),
    ("unknown", [], "No calls on record."),
]
MONTHS = 13  # timeline length, the scoring month included


def examples(wb: Workbook) -> None:
    w = WINDOW["61–180 DPD"]
    s = Sheet(wb.create_sheet("Examples"), [16] + [5] * MONTHS + [52])
    why = MONTHS + 2
    s.title("Examples (61–180 DPD, 3-month window)",
            "One customer per row, oldest month on the left. The blue columns are the window. "
            "Green = favourable evidence, red = adverse.")

    def legend(items: list[tuple[str, str]]) -> None:
        s.text(1, "Codes", bold=True, color=MUTED, border=False, align=MID)
        col, span = 2, MONTHS // len(items)
        for code, text in items:
            fill, ink = TONE[CODE_TONE[code]]
            s.text(col, f"{code}  {text}", span=span, color=ink, fill=fill, align=CENTER)
            col += span
        s.ws.row_dimensions[s.r].height = 28
        s.r += 1

    def grid(rows, rule) -> None:
        s.header(["State"] + [("Now" if k == 0 else str(k)) for k in range(1 - MONTHS, 1)] + ["Why"])
        for k in range(1 - MONTHS, 1):
            if _recent(k, w):
                s.ws.cell(row=s.r - 1, column=MONTHS + 1 + k).fill = _fill(WINDOW_HEAD)
        for state, events, text in rows:
            got = rule(events, w)
            if got != state:
                raise SystemExit(f"example '{text}' gives {got}, expected {state}")
            s.chip(1, state)
            for k in range(1 - MONTHS, 1):
                codes = [c for o, c in events if o == k]
                tone = TONE[CODE_TONE[codes[-1]]] if codes else None
                fill = tone[0] if tone else (WINDOW_FILL if _recent(k, w) else None)
                s.text(MONTHS + 1 + k, " ".join(codes) or None, bold=True,
                       color=tone[1] if tone else INK, fill=fill, align=CENTER)
            s.text(why, text, align=MID)
            s.ws.row_dimensions[s.r].height = 20
            s.r += 1

    s.section("Location", gap=0)
    legend([(UAE, "UAE"), (ABROAD, "abroad"), (TRAVEL, "travel"), (EXIT, "left UAE")])
    grid(LOC_EXAMPLES, location)
    s.section("Reachability")
    legend([(ANSWERED, "answered"), (CALLED_IN, "called us"), (RANG_OUT, "rang out"),
            (DEAD_LINE, "dead line"), (CONNECTED, "connected, not confirmed")])
    grid(REACH_EXAMPLES, reachability)
    s.r += 1
    s.note("One code per call (a day with an answer counts as a contact). At 180+ DPD the window "
           "is 6 months; the rules are the same.")
    s.ws.freeze_panes = "B4"


CHANGES = [  # (area, the model it replaces, now, effect on CC 61–180, 31 Aug 2026)
    ("Structure", "One state (gone, skip, avoiding, non-cooperative, reachable, unknown, "
     "deceased) from a departure spell.", "Two independent dimensions + deceased, every account "
     "and month end.", "Old gone 6,048 → Skip 5,158; old skip 3,855 → Skip 913, Unknown 2,172."),
    ("Location principle", "Any departure sign (travel, foreign card use or login, salary stop, "
     "collector note), cancelled by a UAE login within 90 / 180 days.", "The latest evidence "
     "wins; foreign at any age, UAE only within the window.", "Skip 44.0%, In Country 24.0%, "
     "Unknown 32.0%."),
    ("Credit card abroad", "Any foreign-merchant transaction, online included.", "In person only: "
     "cash / ATM and grocery, fuel, restaurant, pharmacy, transport, department-store purchases.",
     "Decides 551 Skip and 123 In Country."),
    ("Debit card", "Not used.", "Shop-terminal payments and ATM withdrawals, placed by the "
     "terminal's country.", "Decides 143 Skip and 148 In Country; rows fall sharply from May "
     "2026 (lag or behaviour: under check)."),
    ("Travel purchase", "Within 3 months before the card block, the scored card only.",
     "Travel rule on any card: UAE activity ends within 3 months of the ticket, then 1 month of "
     "silence.", "1,620 Skip (8.4%), mostly 3–7 months after the last UAE evidence."),
    ("Logins", "Logins with no country counted as foreign; monthly dates.", "No country = no "
     "evidence; daily dates; same day: foreign wins.", "A foreign login decides 5,772 Skip "
     "(29.9%); VPN check open."),
    ("Not evidence", "Salary stop and foreign online spend counted as departure.", "Salary, "
     "online purchases, transfers and incoming money are not location evidence.", "—"),
    ("Failed call", "Ringing only.", "Rang out, no answer, message left, or a dead line "
     "(switched off, wrong / invalid number); connected without success is neutral.",
     "Reachable −15.1 pt."),
    ("Admin entries", "Result not found, follow up, e-mail sent, legal / repossession counted "
     "and broke a run of failed calls.", "Ignored.", "Reachable −21.1 pt (the largest move)."),
    ("Reachable", "Any contact since the spell began; overruled only by 3 ringing events.",
     "A contact within the window; 3 failed call days after it still make Non-Reachable.",
     "Reachable −5.5 pt (1,065 → Unknown)."),
    ("Call minimum", "3 outbound attempts needed for any reachability state.", "Needed for "
     "Non-Reachable only.", "Reachable 62.7% → 21.0%, Non-Reachable 7.0% → 67.6% overall."),
    ("Call history", "From the spell start.", "All collections history up to the scoring date.",
     "—"),
    ("Deceased", "Collector note; card block joined on the exact date.", "Collector note "
     "(claims included), card block D on the latest snapshot, customer record flag.",
     "44 → 89; 33 of them have no collector note."),
    ("Dropped", "Routing flags (promise to pay, hardship, refusing, field visit), contact rates.",
     "Left to the other axes.", "—"),
]


def changes(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Changes"), [18, 40, 40, 34])
    s.title("Changes", "What changed against the model in use, and the effect on credit cards at "
                       "61–180 DPD, 31 Aug 2026 (production check, same accounts).")
    s.header(["Area", "Before", "Now", "Effect"])
    for row in CHANGES:
        for col, v in enumerate(row, 1):
            s.text(col, v, bold=col == 1, color=MUTED if col == 4 else INK)
        _fit(s.ws, s.r, [(v, s.widths[i]) for i, v in enumerate(row)])
        s.r += 1
    s.r += 1
    s.note("Loans: the old output had 111 extra rows from departure spells; the new one covers "
           "exactly the scored accounts (3,985).")
    s.ws.freeze_panes = "A5"


# --- results -------------------------------------------------------------------------------
RESULTS_DATE = "31 Aug 2026"
# Production check of bundle 07, latest month; {table: {variant column: counts in row order}}.
# Loans by product and 180+ have not run yet; a total given here replaces its sum formula.
RESULTS = {
    "Combined state": {0: [89, 1648, 2613, 369, 1186, 6114, 1155, 1203, 4290, 625],
                       5: [29, 407, 564, 107, 320, 1135, 260, 308, 592, 263]},
    "Accounts in scope": {0: [19292], 5: [3985]},
    "Location": {0: [4638, 8489, 6165], 5: [1080, 1728, 1177]},
    "Reachability": {0: [4043, 13038, 2211], 5: [1043, 2292, 650]},
    "Why Unknown": {0: [344, 5821, 273, 1938]},
}
TREND = {  # month: (in country, skip, unknown, reachable, non-reachable, unknown)
    "Credit cards 61–180": {
        "Jan": (4753, 5186, 4725, 4447, 8605, 1612), "Feb": (4531, 5187, 4858, 4440, 8494, 1642),
        "Mar": (4339, 5246, 4870, 4039, 9000, 1416), "Apr": (4316, 5396, 4959, 3873, 9386, 1412),
        "May": (4830, 5861, 5199, 4207, 10142, 1541), "Jun": (4967, 6520, 5495, 4260, 10745, 1977),
        "Jul": (4824, 7652, 5921, 4046, 12151, 2200), "Aug": (4638, 8489, 6165, 4043, 13038, 2211)},
    "Retail loans 61–180": {
        "Jan": (805, 898, 621, 791, 1099, 434), "Feb": (717, 882, 614, 755, 1043, 415),
        "Mar": (709, 888, 621, 729, 1161, 328), "Apr": (889, 1034, 738, 793, 1477, 391),
        "May": (962, 1159, 975, 945, 1697, 454), "Jun": (1059, 1344, 1111, 1000, 1939, 575),
        "Jul": (1014, 1577, 1137, 1064, 2031, 633), "Aug": (1080, 1728, 1177, 1043, 2292, 650)},
}
DETAIL = [  # (section, [(label, state tone, CC count, RL count)]); RL rules / reach still to come
    ("Location: rule and the evidence that decided it", [
        ("Skip · latest evidence a foreign login", "skip", 5772, None),
        ("Skip · latest evidence foreign credit-card use", "skip", 551, None),
        ("Skip · latest evidence foreign debit-card use", "skip", 143, None),
        ("Skip · latest evidence a departure note", "skip", 403, None),
        ("Skip · travel rule", "skip", 1620, None),
        ("In Country · UAE login", "in_country", 4367, None),
        ("In Country · UAE credit-card use", "in_country", 123, None),
        ("In Country · UAE debit-card use", "in_country", 148, None),
        ("Unknown · UAE evidence older than the window", "unknown", 5821, None),
        ("Unknown · no evidence", "unknown", 344, None)]),
    ("Reachability: last contact", [
        ("Non-Reachable · contact in the window, then 3 failed days", "non_reachable", 3386, None),
        ("Non-Reachable · contact before the window", "non_reachable", 4691, None),
        ("Non-Reachable · never a contact", "non_reachable", 4961, None),
        ("Reachable · contact in the window", "reachable", 4043, None),
        ("Unknown · contact before the window", "unknown", 1065, None),
        ("Unknown · never a contact (273 never called)", "unknown", 1146, None)]),
    ("Call days in the window", [
        ("None", "unknown", 743, None), ("1–2", "unknown", 446, None),
        ("3–5", "unknown", 1539, None), ("6 or more", "unknown", 16564, None)]),
    ("Deceased: source", [
        ("Collector note only", "deceased", 37, None), ("Card block only", "deceased", 17, None),
        ("Customer record only", "deceased", 3, None), ("More than one", "deceased", 32, None)]),
]
PRODUCTS =["Personal Loans", "Personal Cash Loans", "Auto"]
VARIANTS = ([("CC\n61–180", None), ("CC\n180+", None)]
            + [(f"RL 61–180\n{p}", None) for p in PRODUCTS] + [("RL 61–180\ntotal", (2, 3, 4))]
            + [(f"RL 180+\n{p}", None) for p in PRODUCTS] + [("RL 180+\ntotal", (6, 7, 8))])
VINTAGES = [(f"{prod}\n{v}", None) for prod in ("CC 180+", "RL 180+")
            for v in ("early-stage\ncharge-off", "late-stage\ncharge-off")]
LEAD = 2  # label columns before the counts


def _value_row(s: Sheet, cols: list, formula=None, bold: bool = False, fmt: str = "#,##0",
               values: dict | None = None) -> None:
    """One count per column: an entry cell (``values[b]`` when known), the sum of other
    columns, or ``formula(col_letter)``."""
    values = values or {}
    for b, (_, parts) in enumerate(cols):
        col = LEAD + 1 + 2 * b
        if formula:
            c = s.text(col, formula(get_column_letter(col)), bold=bold)
        elif parts is None or values.get(b) is not None:
            c = s.text(col, values.get(b), color="0000FF", fill=INPUT_FILL)
        else:
            cells = ",".join(f"{get_column_letter(LEAD + 1 + 2 * i)}{s.r}" for i in parts)
            c = s.text(col, f'=IF(COUNT({cells})=0,"",SUM({cells}))', bold=bold)
        c.number_format = fmt
        s.text(col + 1, None)


def _counts(s: Sheet, title: str, heads: list[tuple[str, int]], rows: list, label, cols: list,
            total: str | None = "Total", share_of: int | None = None, data: dict | None = None) -> int:
    """Count + share per column, shares of the table's own total or of row ``share_of``;
    ``data`` = {column: counts in row order}. Returns the total row."""
    data = data or {}
    s.section(title)
    s.header([h for h, _ in heads] + [x for name, _ in cols for x in (name, "share")],
             [n for _, n in heads] + [1] * (2 * len(cols)), height=58)
    first, tot = s.r, s.r + len(rows)
    base = share_of or tot
    for i, item in enumerate(rows):
        label(item)
        _value_row(s, cols, values={b: v[i] for b, v in data.items()})
        for b in range(len(cols)):
            L = get_column_letter(LEAD + 1 + 2 * b)
            sh = s.text(LEAD + 2 + 2 * b, f'=IF(OR({L}{s.r}="",N(${L}${base})=0),"",{L}{s.r}/${L}${base})',
                        color=MUTED)
            sh.number_format = "0.0%"
        s.r += 1
    if total:
        s.text(1, total, span=LEAD, bold=True)
        _value_row(s, cols, formula=lambda L: f'=IF(COUNT({L}{first}:{L}{tot - 1})=0,"",SUM({L}{first}:{L}{tot - 1}))', bold=True)
        s.r += 1
    return tot


def _combined(s: Sheet):
    def label(item) -> None:
        if item == "deceased":
            s.chip(1, "deceased", span=2)
        else:
            s.chip(1, item[0])
            s.chip(2, item[1])
    return label


COMBINED_HEADS = [("Location", 1), ("Reachability", 1)]


def results(wb: Workbook, scoring: str) -> None:
    s = Sheet(wb.create_sheet("Results"), [14, 14] + [11, 7] * len(VARIANTS))
    s.title("Results", f"Accounts per state and model variant, {RESULTS_DATE} (production check). "
                       "Pale yellow = from the run; shares are calculated. Loans by product and "
                       "180+ have not run yet; the loan total is entered until they do.")
    tot = _counts(s, "Combined state", COMBINED_HEADS, ["deceased"] + COMBINED, _combined(s), VARIANTS,
                  data=RESULTS["Combined state"])
    s.text(1, "Accounts in scope", span=LEAD)
    _value_row(s, VARIANTS, values={b: v[0] for b, v in RESULTS["Accounts in scope"].items()})
    s.r += 1
    s.text(1, "Coverage", span=LEAD, bold=True)
    _value_row(s, VARIANTS, formula=lambda L: f'=IF(N({L}{s.r - 1})=0,"",{L}{tot}/{L}{s.r - 1})',
               bold=True, fmt="0.0%")
    s.r += 1
    _counts(s, "Location", [("State", 2)], LOC, lambda st: s.chip(1, st, span=2), VARIANTS,
            data=RESULTS["Location"])
    _counts(s, "Reachability", [("State", 2)], REACH, lambda st: s.chip(1, st, span=2), VARIANTS,
            data=RESULTS["Reachability"])
    _counts(s, "Why Unknown", [("Reason", 2)],
            ["Location: no evidence", "Location: UAE evidence too old",
             "Reachability: no calls", "Reachability: no recent confirmed contact"],
            lambda t: s.chip(1, "unknown", t, span=2), VARIANTS, total=None, share_of=tot,
            data=RESULTS["Why Unknown"])
    s.note("Shares are of all accounts in the variant.")
    s.r += 1
    s.note("Location and reachability are computed on deceased accounts too, so their totals "
           "include them. Aggregates only.")
    s.ws.freeze_panes = s.ws.cell(row=7, column=LEAD + 1)


def vintage(wb: Workbook, scoring: str) -> None:
    s = Sheet(wb.create_sheet("Results 180+ vintage"), [14, 14] + [12, 7] * len(VINTAGES))
    s.title("Results 180+ by vintage",
            "Early-stage charge-off = charged off less than 2 years ago; late-stage = 2 years or "
            f"more{f'; {scoring}' if scoring else ''}. Shares are within each vintage.")
    _counts(s, "Combined state", COMBINED_HEADS, ["deceased"] + COMBINED, _combined(s), VINTAGES)
    s.ws.freeze_panes = s.ws.cell(row=7, column=LEAD + 1)


def detail(wb: Workbook) -> None:
    s = Sheet(wb.create_sheet("Results detail"), [52, 11, 7, 11, 7])
    s.title("Results detail", f"Which rules fire and why, 61–180 DPD, {RESULTS_DATE}. Loans: "
                              "rule and call blocks not run yet.")
    for i, (title, rows) in enumerate(DETAIL):
        s.section(title, gap=0 if i == 0 else 1)
        s.header(["", "Credit cards", "share", "Retail loans", "share"])
        for label, tone, *counts in rows:
            s.chip(1, tone, label)
            for j, (n, accounts) in enumerate(zip(counts, (19292, 3985))):
                c = s.text(2 + 2 * j, n, color="0000FF", fill=INPUT_FILL)
                c.number_format = "#,##0"
                L = get_column_letter(2 + 2 * j)
                sh = s.text(3 + 2 * j, f'=IF({L}{s.r}="","",{L}{s.r}/{accounts})', color=MUTED)
                sh.number_format = "0.0%"
            s.r += 1
    s.r += 1
    s.note("Shares are of all accounts (19,292 cards, 3,985 loans). The travel rule mostly "
           "fires 3–7 months after the last UAE evidence.")
    s.ws.freeze_panes = "A4"


def trend(wb: Workbook) -> None:
    states = LOC + REACH
    s = Sheet(wb.create_sheet("Results trend"), [10, 10] + [10, 7] * len(states))
    s.title("Results trend", "Accounts per state by month, Jan–Aug 2026 (month ends), "
                             "61–180 DPD. Shares are of the month's accounts.")
    for i, (title, months) in enumerate(TREND.items()):
        s.section(title, gap=0 if i == 0 else 1)
        s.text(1, "Month", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        s.text(2, "Accounts", bold=True, color="FFFFFF", fill=NAVY, align=CENTER)
        for j, st in enumerate(states):
            label = f"{LABEL[st]} ({'loc.' if j < 3 else 'reach.'})" if st == "unknown" else None
            s.chip(3 + 2 * j, st, label, span=2).alignment = CENTER
        s.ws.row_dimensions[s.r].height = 30
        s.r += 1
        for month, counts in months.items():
            s.text(1, f"{month} 2026", bold=True)
            s.text(2, "=" + "+".join(f"{get_column_letter(3 + 2 * j)}{s.r}" for j in range(3)),
                   bold=True).number_format = "#,##0"
            for j, n in enumerate(counts):
                L = get_column_letter(3 + 2 * j)
                s.text(3 + 2 * j, n, color="0000FF", fill=INPUT_FILL).number_format = "#,##0"
                s.text(4 + 2 * j, f"={L}{s.r}/$B{s.r}", color=MUTED).number_format = "0.0%"
            s.r += 1
    s.r += 1
    s.note("Skip is flat to May and rises from June, as debit-card rows thin out; Reachable "
           "counts stay flat, so a growing book adds Non-Reachable.")
    s.ws.freeze_panes = "A4"


def build(out: pathlib.Path, scoring: str) -> pathlib.Path:
    wb = Workbook()
    overview(wb, scoring)
    logic(wb)
    examples(wb)
    changes(wb)
    results(wb, scoring)
    detail(wb)
    trend(wb)
    vintage(wb, scoring)
    wb.calculation.fullCalcOnLoad = True
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(pathlib.Path(__file__).with_name("a2_locatability_reference.xlsx")))
    ap.add_argument("--scoring-date", dest="scoring", default="")
    a = ap.parse_args()
    print(build(pathlib.Path(a.out), a.scoring))


if __name__ == "__main__":
    main()
