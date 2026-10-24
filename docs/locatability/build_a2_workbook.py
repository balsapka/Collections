"""Build the business-facing model document for the A2 locatability axis.

    python build_a2_workbook.py [--out a2_locatability_reference.xlsx] [--scoring-date "Nov 2026"]

The rules are those signed off in ``workplace_mirror/specs/A2_locatability_spec.md``. Every
worked example is run through the reference rules below (``location`` / ``reachability``) and
the build FAILS if an example no longer gets the state it illustrates. Results are left for
entry (yellow cells) until the pipelines have run for every model variant; shares, totals and
coverage are Excel formulas. Same look as the deterioration workbook.
"""
from __future__ import annotations

import argparse
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# --- rules (reference implementation of the spec, monthly granularity) --------------------
WINDOW = {"60_180": 3, "180_plus": 6}  # months, the observation month included
TRAVEL_MONTHS = 12
GONE_DARK_DATES = 3
DOMESTIC, FOREIGN, TRAVEL, EXIT = "U", "F", "T", "X"
ANSWERED, INBOUND, RINGING, DEAD = "A", "I", "R", "D"


def _in_last(offset: int, months: int) -> bool:
    """``offset`` 0 = the observation month, -1 the month before, …"""
    return offset > -months


def location(events: list[tuple[int, str]], w: int) -> tuple[str, str | None]:
    """(state, unknown reason) from dated location evidence, oldest first."""
    seq = [(o, k) for o, k in events if k != TRAVEL or _in_last(o, TRAVEL_MONTHS)]
    if not seq:
        return "unknown", "no_evidence"
    offset, kind = seq[-1]
    if kind != DOMESTIC:
        return "skip", None
    if _in_last(offset, w):
        return "in_country", None
    return "unknown", "domestic_before_window"


def reachability(calls: list[tuple[int, str]], w: int) -> tuple[str, str | None]:
    """(state, unknown reason) from call-date outcomes, oldest first: A answered, I inbound,
    R ringing / no answer, D dead line (one entry per date; a day with any answer is A)."""
    if not calls:
        return "unknown", "no_dcore_record"
    attempts = [i for i, (_, k) in enumerate(calls) if k != INBOUND]
    last = attempts[-GONE_DARK_DATES:]
    if len(last) == GONE_DARK_DATES and all(calls[i][1] in (RINGING, DEAD) for i in last):
        oldest = last[0]
        contact_after = any(k in (ANSWERED, INBOUND) for _, k in calls[oldest + 1:])
        if _in_last(calls[oldest][0], w) and not contact_after:
            return "non_reachable", None
    if any(k in (ANSWERED, INBOUND) and _in_last(o, w) for o, k in calls):
        return "reachable", None
    return "unknown", "no_contact_in_window"


# --- look ----------------------------------------------------------------------------------
FONT = "Arial"
NAVY, GREY, LIGHT, RULE = "1F3864", "595959", "F2F2F2", "BFBFBF"
STATE_COLOUR = {
    "in_country": "548235",
    "skip": "C00000",
    "reachable": "2F5597",
    "non_reachable": "C55A11",
    "unknown": "A6A6A6",
    "deceased": "262626",
}
LABEL = {
    "in_country": "In Country",
    "skip": "Skip",
    "reachable": "Reachable",
    "non_reachable": "Non-Reachable",
    "unknown": "Unknown",
    "deceased": "Deceased",
}
EVENT_COLOUR = {DOMESTIC: "A9D08E", FOREIGN: "FF7C80", TRAVEL: "F4B183", EXIT: "C00000",
                ANSWERED: "8EA9DB", INBOUND: "BDD7EE", RINGING: "FFE699", DEAD: "F8CBAD"}
INPUT_FILL = "FFFF00"
THIN = Side(style="thin", color=RULE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _font(**kw) -> Font:
    return Font(name=FONT, size=kw.pop("size", 10), **kw)


def _fill(hex_: str) -> PatternFill:
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def _text_on(hex_: str) -> str:
    r, g, b = (int(hex_[i:i + 2], 16) for i in (0, 2, 4))
    return "FFFFFF" if (0.299 * r + 0.587 * g + 0.114 * b) < 150 else "000000"


def _title(ws: Worksheet, title: str, subtitle: str, width_cols: int) -> int:
    ws["A1"] = title
    ws["A1"].font = _font(size=16, bold=True, color=NAVY)
    ws["A2"] = subtitle
    ws["A2"].font = _font(italic=True, color=GREY)
    ws["A2"].alignment = WRAP
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width_cols)
    ws.row_dimensions[2].height = 30
    ws.sheet_view.showGridLines = False
    return 4


def _section(ws: Worksheet, row: int, text: str, width_cols: int) -> int:
    ws.cell(row=row, column=1, value=text).font = _font(size=12, bold=True, color=NAVY)
    for col in range(1, width_cols + 1):
        ws.cell(row=row, column=col).border = Border(bottom=Side(style="medium", color=NAVY))
    return row + 1


def _header(ws: Worksheet, row: int, labels: list, start_col: int = 1) -> int:
    for i, lab in enumerate(labels, start_col):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = _font(bold=True, color="FFFFFF")
        c.fill = _fill(NAVY)
        c.alignment = CENTER
        c.border = BOX
    return row + 1


def _row(ws: Worksheet, row: int, values: list, bold_first: bool = False,
         height: float | None = None) -> int:
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = _font(bold=bold_first and i == 1)
        c.alignment = WRAP
        c.border = BOX
    if height:
        ws.row_dimensions[row].height = height
    return row + 1


def _chip(cell, state: str, label: str | None = None) -> None:
    cell.value = label or LABEL[state]
    cell.fill = _fill(STATE_COLOUR[state])
    cell.font = _font(bold=True, color=_text_on(STATE_COLOUR[state]))
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    cell.border = BOX


def _merge_row(ws: Worksheet, row: int, c1: int, c2: int) -> None:
    ws.merge_cells(start_row=row, start_column=c1, end_row=row, end_column=c2)


def _note(ws: Worksheet, row: int, text: str, width_cols: int, height: float = 15) -> int:
    c = ws.cell(row=row, column=1, value=text)
    c.font = _font(italic=True, color=GREY)
    c.alignment = WRAP
    _merge_row(ws, row, 1, width_cols)
    ws.row_dimensions[row].height = height
    return row + 1


def _widths(ws: Worksheet, widths: list[float]) -> None:
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _print(ws: Worksheet) -> None:
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def _key_values(ws: Worksheet, r: int, pairs: list[tuple[str, str]], last_col: int) -> int:
    for k, v in pairs:
        lab = ws.cell(row=r, column=1, value=k)
        lab.font = _font(bold=True, color=NAVY)
        lab.alignment = WRAP
        c = ws.cell(row=r, column=2, value=v)
        c.font = _font()
        c.alignment = WRAP
        _merge_row(ws, r, 2, last_col)
        ws.row_dimensions[r].height = 26
        r += 1
    return r


# --- content -------------------------------------------------------------------------------
LOC_STATES = ["in_country", "skip", "unknown"]
REACH_STATES = ["reachable", "non_reachable", "unknown"]
A2_STATES = ["deceased"] + [(lo, re) for lo in LOC_STATES for re in REACH_STATES]
ACTIONS = {
    ("in_country", "reachable"): "Negotiate: settle, restructure or pressure (ability and credibility axes decide).",
    ("in_country", "non_reachable"): "In the UAE but not answering or a dead number: skip-trace the number, field visit.",
    ("in_country", "unknown"): "Keep calling; not enough call evidence yet.",
    ("skip", "reachable"): "Abroad but answering: remote settlement, international payment route.",
    ("skip", "non_reachable"): "Left and unreachable: international recovery agency, legal.",
    ("skip", "unknown"): "Signs of leaving, no call evidence: verify the departure.",
    ("unknown", "reachable"): "Answering, location not evidenced: negotiate and ask.",
    ("unknown", "non_reachable"): "Not answering, no location evidence: skip-trace both.",
    ("unknown", "unknown"): "Data gap: treat on the other persona axes.",
}


def _on(scoring_date: str) -> str:
    return f" ({scoring_date})" if scoring_date else ""


def _a2_label(state) -> str:
    return LABEL["deceased"] if state == "deceased" else f"{LABEL[state[0]]} – {LABEL[state[1]]}"


def _a2_chip(cell, state) -> None:
    _chip(cell, "deceased" if state == "deceased" else state[0], _a2_label(state))


def _overview(wb: Workbook, scoring_date: str) -> None:
    ws = wb.active
    ws.title = "Overview"
    r = _title(ws, "A2 Locatability",
               "One of the persona axes: can we find the customer, and can we reach them? Two "
               "independent dimensions plus a deceased override; every account in scope gets "
               "one value on each.", 5)
    r = _key_values(ws, r, [
        ("Scope", "Credit cards (CC) and retail loans (RL: Personal Loans, Personal Cash Loans, "
                  f"Auto) at 61–180 DPD and at 180+ DPD on the scoring date{_on(scoring_date)}."),
        ("Location", "Where the customer is, from what they do: digital-banking logins, card "
                     "and current/savings (CASA) spending on all the customer's accounts, travel "
                     "purchases, and a collector's note that the customer left the country."),
        ("Reachability", "Whether our calls get through, from the collections contact history "
                         "(DCORE)."),
        ("Principle", "On both dimensions the latest evidence wins. Location never reads a call "
                      "outcome (except the collector's departure note); reachability never "
                      "reads location."),
        ("Deceased", "Overrides both dimensions: collector's deceased note (a relative's claim "
                     "included), card block code D, or the customer's deceased flag."),
        ("How", "See 'How states are assigned'; examples in 'Worked examples'; thresholds in "
                "'Thresholds'; sources in 'Evidence & sources'."),
    ], 5)
    r = _section(ws, r + 1, "The states of each dimension", 5)
    r = _header(ws, r, ["State", "Dimension", "In one sentence", "", ""])
    _merge_row(ws, r - 1, 3, 5)
    for st, dim, text in [
        ("in_country", "Location", "The latest evidence of where the customer is points to the UAE, and it is recent."),
        ("skip", "Location", "The latest evidence points abroad (however old): a foreign login or spend, a recent travel purchase, or a collector's departure note."),
        ("unknown", "Location", "No evidence, or the latest evidence is in the UAE but too old to rely on."),
        ("reachable", "Reachability", "We spoke to the customer recently (they answered, or they called us)."),
        ("non_reachable", "Reachability", "The last 3 days we called, every call rang out or hit a dead line, and the customer has not been in touch since."),
        ("unknown", "Reachability", "Not enough recent call evidence either way."),
        ("deceased", "Override", "The customer is reported deceased."),
    ]:
        _row(ws, r, [None, dim, text, None, None], height=30)
        _merge_row(ws, r, 3, 5)
        _chip(ws.cell(row=r, column=1), st)
        r += 1
    r = _section(ws, r + 1, "Combined: location × reachability (and the action it points to)", 5)
    r = _header(ws, r, ["Location \\ Reachability"] + [LABEL[s] for s in REACH_STATES])
    for lo in LOC_STATES:
        _chip(ws.cell(row=r, column=1), lo)
        for j, re in enumerate(REACH_STATES, 2):
            c = ws.cell(row=r, column=j, value=ACTIONS[(lo, re)])
            c.font = _font()
            c.alignment = WRAP
            c.border = BOX
        ws.row_dimensions[r].height = 44
        r += 1
    _chip(ws.cell(row=r, column=1), "deceased")
    c = ws.cell(row=r, column=2, value="Estate / insurance process (both dimensions are still "
                                       "computed and reported).")
    c.font = _font()
    c.border = BOX
    _merge_row(ws, r, 2, 4)
    r += 2
    _note(ws, r, "3 × 3 combinations + Deceased = 10 values of the combined state. Shares: see "
                 "'Results' and 'Results 180+ vintage'.", 5)
    _widths(ws, [26, 40, 40, 40, 4])
    ws.freeze_panes = "A4"
    _print(ws)


def _assignment(wb: Workbook) -> None:
    ws = wb.create_sheet("How states are assigned")
    last = 4
    r = _title(ws, "How states are assigned",
               "Each dimension is decided on its own; inside a dimension the questions are asked "
               "top to bottom and the first 'yes' decides.", last)

    def flow(r: int, title: str, steps: list[tuple[str, str, str]]) -> int:
        r = _section(ws, r, title, last)
        for i, (q, st, label) in enumerate(steps):
            c = ws.cell(row=r, column=1, value=f"Step {i + 1}")
            c.font = _font(bold=True, color="FFFFFF")
            c.fill = _fill(NAVY)
            c.alignment = CENTER
            q_cell = ws.cell(row=r, column=2, value=q)
            q_cell.font = _font(bold=True)
            q_cell.fill = _fill(LIGHT)
            q_cell.border = BOX
            q_cell.alignment = Alignment(vertical="center", wrap_text=True)
            final = i == len(steps) - 1
            arrow = ws.cell(row=r, column=3, value="▶" if final else "yes  ▶")
            arrow.font = _font(bold=True, color=GREY)
            arrow.alignment = CENTER
            _chip(ws.cell(row=r, column=4), st, label)
            ws.row_dimensions[r].height = 30
            r += 1
            if not final:
                down = ws.cell(row=r, column=2, value="no  ▼")
                down.font = _font(color=GREY)
                down.alignment = Alignment(horizontal="center")
                r += 1
        return r + 1

    r = flow(r, "Deceased (checked for every account)", [
        ("Reported deceased by any source?", "deceased", "Deceased  (combined state)"),
    ])
    r = flow(r, "Location", [
        ("Is the latest evidence foreign?", "skip", None),
        ("Is the latest evidence in the UAE and within the window?", "in_country", None),
        ("Otherwise (no evidence, or UAE evidence older than the window)", "unknown", None),
    ])
    r = flow(r, "Reachability", [
        ("Gone dark: the last 3 call days all failed, recently, with no contact since?",
         "non_reachable", None),
        ("A confirmed contact within the window?", "reachable", None),
        ("Otherwise", "unknown", None),
    ])
    r = _section(ws, r, "The exact tests", last)
    r = _header(ws, r, ["Dimension", "State", "Exact test", ""])
    _merge_row(ws, r - 1, 3, 4)
    for dim, st, test, h in [
        ("Deceased", "deceased", "Any of, at any age up to the scoring date: a collector's deceased result "
         "(DECEASED, DECEASED CLAIMED, DECEASED OR EXPIRED, …); card block code D on the latest "
         "contract snapshot (cards only); the deceased flag on the customer's latest demographics record.", 44),
        ("Location", "skip", "The latest foreign evidence is later than the latest UAE evidence, or there "
         "is no UAE evidence. Foreign evidence = a login from abroad, card or CASA spending abroad, a "
         "collector's departure note (any age), or a travel purchase in the last 12 months.", 44),
        ("Location", "in_country", "The latest evidence is a UAE login or UAE spending (not a travel "
         "purchase), dated within the window. Same day as foreign evidence: the UAE evidence wins.", 30),
        ("Location", "unknown", "No evidence at all, or the latest evidence is in the UAE but older than "
         "the window.", 30),
        ("Reachability", "non_reachable", "The last 3 call days (days with at least one outbound call) "
         "were all failed days — every call rang out or hit a dead line, none answered — the oldest of "
         "them is within the window, and the customer was not reached and did not call in after it.", 44),
        ("Reachability", "reachable", "A confirmed contact within the window: the customer called in, a "
         "call was answered (successful outcome), or a right-party result was recorded. No minimum number "
         "of calls.", 44),
        ("Reachability", "unknown", "No contact history, or calls exist but neither rule above applies "
         "(e.g. only 1–2 failed days, or all evidence older than the window).", 30),
    ]:
        _row(ws, r, [dim, None, test, None], bold_first=True, height=h)
        _merge_row(ws, r, 3, 4)
        _chip(ws.cell(row=r, column=2), st)
        r += 1
    r = _section(ws, r + 1, "Terms", last)
    for term, meaning in [
        ("Window", "The scoring month and the months before it: 3 months at 61–180 DPD, 6 months at "
                   "180+ DPD (activity is thinner in the late buckets)."),
        ("Customer level", "Location evidence is read across all the customer's cards and CASA "
                           "accounts, not only the account being scored."),
        ("Latest evidence wins", "A trip followed by UAE activity means the customer came back; "
                                 "a run of failed calls after an answered one means they went dark."),
        ("Contact history", "Starts when the account enters collections, so the whole history "
                            "up to the scoring date is used."),
        ("Failed call day", "A day with at least one outbound call where every call rang out "
                            "(no answer) or hit a dead line (wrong / invalid number, switched off)."),
        ("Unknown reasons", "Location: no evidence / UAE evidence older than the window. "
                            "Reachability: no contact history / no contact in the window."),
    ]:
        lab = ws.cell(row=r, column=1, value=term)
        lab.font = _font(bold=True)
        lab.alignment = WRAP
        c = ws.cell(row=r, column=2, value=meaning)
        c.font = _font()
        c.alignment = WRAP
        _merge_row(ws, r, 2, last)
        ws.row_dimensions[r].height = 30
        r += 1
    _widths(ws, [16, 44, 14, 46])
    _print(ws)


LOC_EXAMPLES = [
    ("in_country", [(-8, FOREIGN), (-1, DOMESTIC)], "Spent abroad 8 months ago, UAE spending last month."),
    ("in_country", [(-6, TRAVEL), (-5, FOREIGN), (-1, DOMESTIC)], "Bought a ticket, spent abroad, came back: UAE login last month."),
    ("in_country", [(-4, EXIT), (0, DOMESTIC)], "Collector noted 'left the country'; the customer has since logged in from the UAE."),
    ("skip", [(-3, DOMESTIC), (-1, FOREIGN)], "Latest login is from abroad."),
    ("skip", [(-14, DOMESTIC), (-10, FOREIGN)], "Last seen abroad 10 months ago, nothing since: still Skip."),
    ("skip", [(-9, DOMESTIC), (-4, TRAVEL)], "Bought a ticket 4 months ago, no UAE activity since."),
    ("skip", [(-5, DOMESTIC), (-2, EXIT)], "Collector recorded a final exit visa."),
    ("unknown", [(-5, DOMESTIC)], "Last UAE activity is older than the 3-month window."),
    ("unknown", [(-15, TRAVEL)], "Only a travel purchase older than 12 months: no evidence."),
    ("unknown", [], "No logins and no card or CASA activity on record."),
]
REACH_EXAMPLES = [
    ("reachable", [(-1, ANSWERED)], "Answered last month."),
    ("reachable", [(-2, INBOUND)], "Called us 2 months ago; no outbound calls needed."),
    ("reachable", [(-2, RINGING), (-1, RINGING), (0, RINGING), (0, INBOUND)], "3 failed days, then the customer called in."),
    ("reachable", [(-1, DEAD), (0, ANSWERED), (0, RINGING), (0, RINGING)], "Answered this month; only 2 failed days since."),
    ("non_reachable", [(-2, ANSWERED), (-1, RINGING), (-1, DEAD), (0, RINGING)], "Answered once, then 3 failed days."),
    ("non_reachable", [(-5, ANSWERED), (-2, DEAD), (-1, DEAD), (0, DEAD)], "Number dead on the last 3 call days."),
    ("unknown", [(-4, ANSWERED), (-1, RINGING), (0, DEAD)], "Last contact is older than the window; only 2 failed days."),
    ("unknown", [(-6, RINGING), (-5, RINGING), (-4, RINGING)], "Failed days, but all older than the window."),
    ("unknown", [], "No contact history."),
]
TIMELINE = 12  # months shown, the scoring month included


def _examples(wb: Workbook) -> None:
    ws = wb.create_sheet("Worked examples")
    lead, w = 1, WINDOW["60_180"]
    why_col = lead + TIMELINE + 1
    last = why_col
    r = _title(ws, "Worked examples (61–180 DPD, 3-month window)",
               "One customer per row: what we observed each month, oldest on the left, the "
               "scoring month on the right. The shaded months are the window.", last)

    def grid_header(r: int) -> int:
        labels = ["State"] + [("Now" if k == 0 else str(k)) for k in range(1 - TIMELINE, 1)] + ["Why"]
        r = _header(ws, r, labels)
        for k in range(1 - TIMELINE, 1):
            if _in_last(k, w):
                ws.cell(row=r - 1, column=lead + TIMELINE + k).fill = _fill("2F5597")
        return r

    def legend(r: int, items: list[tuple[str, str]]) -> int:
        ws.cell(row=r, column=1, value="Codes").font = _font(bold=True)
        col = 2
        for code, text in items:
            c = ws.cell(row=r, column=col, value=f"{code}: {text}")
            c.fill = _fill(EVENT_COLOUR[code])
            c.font = _font(size=9)
            c.alignment = CENTER
            ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + 2)
            col += 3
        return r + 2

    def rows(r: int, examples, rule) -> int:
        for state, events, why in examples:
            got, _ = rule(events, w)
            if got != state:
                raise SystemExit(f"example '{why}' gives {got}, expected {state}")
            _chip(ws.cell(row=r, column=1), state)
            for k in range(1 - TIMELINE, 1):
                codes = [code for o, code in events if o == k]
                c = ws.cell(row=r, column=lead + TIMELINE + k, value=" ".join(codes) or None)
                c.alignment = CENTER
                c.border = BOX
                c.font = _font(bold=True, size=9)
                if codes:
                    c.fill = _fill(EVENT_COLOUR[codes[-1]])
                elif _in_last(k, w):
                    c.fill = _fill(LIGHT)
            older = [e for e in events if e[0] <= -TIMELINE]
            text = why + (" (" + ", ".join(f"{c} at {o}" for o, c in older) + " not shown)" if older else "")
            c = ws.cell(row=r, column=why_col, value=text)
            c.font = _font()
            c.alignment = WRAP
            c.border = BOX
            ws.row_dimensions[r].height = 30
            r += 1
        return r + 1

    r = _section(ws, r, "Location — the latest evidence decides", last)
    r = legend(r, [(DOMESTIC, "UAE login / spend"), (FOREIGN, "abroad login / spend"),
                   (TRAVEL, "travel purchase"), (EXIT, "collector: left the country")])
    r = grid_header(r)
    r = rows(r, LOC_EXAMPLES, location)
    r = _section(ws, r, "Reachability — one code per call day, oldest first within a month", last)
    r = legend(r, [(ANSWERED, "answered"), (INBOUND, "customer called in"),
                   (RINGING, "rang out, no answer"), (DEAD, "dead line")])
    r = grid_header(r)
    r = rows(r, REACH_EXAMPLES, reachability)
    _note(ws, r, "At 180+ DPD the window is 6 months; the rules are otherwise the same.", last)
    _widths(ws, [16] + [6.5] * TIMELINE + [52])
    ws.freeze_panes = "B4"
    _print(ws)


def _evidence(wb: Workbook) -> None:
    ws = wb.create_sheet("Evidence & sources")
    last = 6
    r = _title(ws, "Evidence & sources",
               "What each dimension reads, at which level, and how far back. Customer level = "
               "all the customer's accounts.", last)
    r = _header(ws, r, ["Evidence", "Used for", "Counts as", "Level", "Age limit", "Source"])
    for row in [
        ("Digital-banking login", "Location", "UAE or foreign, by login country", "Customer", "UAE: window; foreign: none", "Digital-banking login history"),
        ("Card spending", "Location", "UAE or foreign, by merchant country", "Customer (all cards)", "UAE: window; foreign: none", "Card transactions"),
        ("CASA spending (debit card, ATM, transfers)", "Location", "UAE or foreign", "Customer (all CASA accounts)", "UAE: window; foreign: none", "CASA transactions"),
        ("Travel purchase (airline, cruise, travel agency)", "Location", "Foreign", "Customer", "12 months", "Card and CASA transactions (merchant category)"),
        ("Collector note: left the country / final exit visa", "Location", "Foreign, on the note's date", "Account", "None", "Collections contact history (DCORE)"),
        ("Call outcomes (answered, rang out, dead line)", "Reachability", "Confirmed contact or failed day", "Account", "Window", "Collections contact history (DCORE)"),
        ("Customer called in", "Reachability", "Confirmed contact", "Account", "Window", "Collections contact history (DCORE)"),
        ("Collector note: deceased (incl. claimed)", "Deceased", "Deceased", "Account", "None", "Collections contact history (DCORE)"),
        ("Card block code D", "Deceased", "Deceased", "Card account", "Latest snapshot", "Card system (Way4)"),
        ("Customer deceased flag", "Deceased", "Deceased", "Customer", "Latest record", "Customer demographics"),
    ]:
        _row(ws, r, list(row), bold_first=True, height=30)
        r += 1
    _widths(ws, [34, 14, 28, 22, 22, 40])
    ws.freeze_panes = "A5"
    _print(ws)


def _thresholds(wb: Workbook) -> None:
    ws = wb.create_sheet("Thresholds")
    r = _title(ws, "Thresholds", "The values the model uses.", 4)
    r = _header(ws, r, ["Applies to", "Threshold", "Value", "Why"])
    for row in [
        ("Window", "Months used for recent UAE evidence and recent contact, 61–180 DPD", "3 months", "The same window as the other persona axes."),
        ("Window", "Same, 180+ DPD", "6 months", "Logins, spending and calls are thinner in the late buckets."),
        ("Location", "Age of foreign evidence that still gives Skip", "No limit", "Accounts stay in collections for years; a customer last seen abroad has not shown they came back."),
        ("Location", "Age of a travel purchase that counts as foreign", "12 months", "A ticket bought long ago says little about where the customer is now."),
        ("Reachability", "Failed call days in a row for Non-Reachable", "3", "Fewer is not yet a pattern."),
        ("Reachability", "Minimum calls for Reachable", "None", "One recent contact is enough evidence that the customer can be reached."),
    ]:
        _row(ws, r, list(row), bold_first=True, height=30)
        ws.cell(row=r, column=3).alignment = CENTER
        r += 1
    _widths(ws, [16, 48, 14, 60])
    ws.freeze_panes = "A5"
    _print(ws)


# --- results -------------------------------------------------------------------------------
RL_PRODUCTS = ["Personal Loans", "Personal Cash Loans", "Auto"]
VARIANTS = (
    [("CC 61–180", None), ("CC 180+", None)]
    + [(f"RL 61–180\n{p}", None) for p in RL_PRODUCTS] + [("RL 61–180\nall", "rl_60_180")]
    + [(f"RL 180+\n{p}", None) for p in RL_PRODUCTS] + [("RL 180+\nall", "rl_180_plus")]
)
VINTAGES = ["< 6 months", "6–12 months", "1–2 years", "2–3 years", "3+ years"]


def _label(cell, text: str) -> None:
    cell.value = text
    cell.font = _font(bold=True)
    cell.fill = _fill(LIGHT)
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    cell.border = BOX


def _input(cell) -> None:
    cell.fill = _fill(INPUT_FILL)
    cell.font = _font(color="0000FF")
    cell.number_format = "#,##0"
    cell.border = BOX


def _count_table(ws: Worksheet, r: int, title: str, row_items: list, chip, columns: list,
                 last_col: int, total_label: str = "Total", first_label: str = "State") -> tuple[int, int, int]:
    """A count + share block per column. ``columns`` are (label, sum_of) where sum_of is None
    for an input column or a list of column indexes the total adds up. Returns (next row,
    first row, total row)."""
    r = _section(ws, r, title, last_col)
    head = [first_label]
    for label, _ in columns:
        head += [f"{label}\naccounts", "share"]
    r = _header(ws, r, head)
    ws.row_dimensions[r - 1].height = 58
    first, total = r, r + len(row_items)
    for item in row_items:
        chip(ws.cell(row=r, column=1), item)
        for b, (_, sum_of) in enumerate(columns):
            col = 2 + 2 * b
            c = ws.cell(row=r, column=col)
            if sum_of is None:
                _input(c)
            else:
                c.value = "=" + "+".join(f"{get_column_letter(2 + 2 * i)}{r}" for i in sum_of)
                c.font = _font()
                c.number_format = "#,##0"
                c.border = BOX
            L = get_column_letter(col)
            s = ws.cell(row=r, column=col + 1, value=f'=IF(${L}${total}=0,"",{L}{r}/${L}${total})')
            s.number_format = "0.0%"
            s.font = _font()
            s.border = BOX
        r += 1
    ws.cell(row=r, column=1, value=total_label).font = _font(bold=True)
    for b in range(len(columns)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b, value=f"=SUM({L}{first}:{L}{r - 1})")
        c.number_format = "#,##0"
        c.font = _font(bold=True)
        c.border = Border(top=Side(style="medium", color=NAVY))
    return r + 2, first, total


def _results(wb: Workbook, scoring_date: str) -> None:
    ws = wb.create_sheet("Results")
    last_col = 1 + 2 * len(VARIANTS)
    columns = []
    for i, (label, total_of) in enumerate(VARIANTS):
        columns.append((label, None if total_of is None else [i - 3, i - 2, i - 1]))
    r = _title(ws, "Results",
               f"Accounts per state and model variant{_on(scoring_date)}. Yellow = to fill "
               "from the scoring run (blue figures); RL 'all' columns, totals and shares are "
               "calculated.", min(last_col, 11))
    r, a2_first, a2_total = _count_table(ws, r, "Combined state", A2_STATES, _a2_chip, columns, last_col)
    r, *_ = _count_table(ws, r, "Location (all accounts, deceased included)", LOC_STATES, _chip, columns, last_col)
    r, *_ = _count_table(ws, r, "Reachability (all accounts, deceased included)", REACH_STATES, _chip, columns, last_col)

    for title, items, total_label in [
        ("Why Skip: the latest evidence", ["Login from abroad", "Card spending abroad", "CASA spending abroad",
                                          "Travel purchase", "Collector departure note"], "Skip"),
        ("Why In Country: the latest evidence", ["UAE login", "UAE card spending", "UAE CASA spending"], "In Country"),
        ("Why Location is Unknown", ["No evidence", "UAE evidence older than the window"], "Location Unknown"),
        ("Why Reachability is Unknown", ["No contact history", "No contact in the window"], "Reachability Unknown"),
    ]:
        r, *_ = _count_table(ws, r, title, items, _label, columns, last_col, total_label, "Reason")
    r = _section(ws, r, "Coverage", last_col)
    ws.cell(row=r, column=1, value="Accounts in scope").font = _font()
    for b, (_, sum_of) in enumerate(columns):
        c = ws.cell(row=r, column=2 + 2 * b)
        if sum_of is None:
            _input(c)
        else:
            c.value = "=" + "+".join(f"{get_column_letter(2 + 2 * i)}{r}" for i in sum_of)
            c.number_format = "#,##0"
            c.font = _font()
    r += 1
    ws.cell(row=r, column=1, value="Coverage (target 100%)").font = _font(bold=True)
    for b in range(len(columns)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b, value=f'=IF({L}{r - 1}=0,"",{L}{a2_total}/{L}{r - 1})')
        c.number_format = "0.0%"
        c.font = _font(bold=True)
    r += 2
    for note in [
        "Every account in scope gets one value on each dimension, so each table adds up to the accounts in scope.",
        "Example of the expected format: CC 61–180 Combined state 'In Country – Reachable' = 12,345 accounts.",
        "Aggregates only; no account-level data.",
    ]:
        r = _note(ws, r, note, min(last_col, 11))
    _widths(ws, [34] + [13, 8] * len(VARIANTS))
    ws.freeze_panes = ws.cell(row=a2_first, column=2)
    _print(ws)


def _vintage(wb: Workbook, scoring_date: str) -> None:
    ws = wb.create_sheet("Results 180+ vintage")
    cols = [(f"CC 180+\n{v}", None) for v in VINTAGES] + [(f"RL 180+\n{v}", None) for v in VINTAGES]
    last_col = 1 + 2 * len(cols)
    r = _title(ws, "Results 180+ by vintage",
               f"Combined state by vintage at 180+ DPD{_on(scoring_date)}. Vintage = time "
               "since the account first reached 180+ DPD. Yellow = to "
               "fill; shares are within each vintage.", min(last_col, 11))
    r, first, _ = _count_table(ws, r, "Combined state", A2_STATES, _a2_chip, cols, last_col)
    r, *_ = _count_table(ws, r, "Location", LOC_STATES, _chip, cols, last_col)
    r, *_ = _count_table(ws, r, "Reachability", REACH_STATES, _chip, cols, last_col)
    for note in [
        "RL vintages cover all three products together; split by product if GRR needs it.",
        "Vintage bands can be changed in the column headers; the formulas do not depend on them.",
    ]:
        r = _note(ws, r, note, min(last_col, 11))
    _widths(ws, [34] + [13, 8] * len(cols))
    ws.freeze_panes = ws.cell(row=first, column=2)
    _print(ws)


def build(out: pathlib.Path, scoring_date: str) -> pathlib.Path:
    wb = Workbook()
    _overview(wb, scoring_date)
    _assignment(wb)
    _examples(wb)
    _evidence(wb)
    _thresholds(wb)
    _results(wb, scoring_date)
    _vintage(wb, scoring_date)
    wb.calculation.fullCalcOnLoad = True
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(pathlib.Path(__file__).with_name("a2_locatability_reference.xlsx")))
    ap.add_argument("--scoring-date", dest="scoring_date", default="")
    a = ap.parse_args()
    print(build(pathlib.Path(a.out), a.scoring_date))


if __name__ == "__main__":
    main()
