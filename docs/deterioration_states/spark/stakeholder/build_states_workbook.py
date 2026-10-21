"""Build the stakeholder workbook for the DPD deterioration states (the 'deterioration axis').

    python build_states_workbook.py --out dpd_deterioration_states_<date>.xlsx \
        [--results results_60_180.json --results results_180_plus.json] [--scoring-date "Aug 2026"]

Everything rule-related is read from the deployed engine, so the workbook cannot drift from
the pipeline: thresholds come from STATE_RULES / PARAM_DEFAULTS, and every worked example is
run through classify() — the build FAILS if an example no longer gets the state it
illustrates. Results (counts per product x segment x state) come from the JSON that
prod_check.report(catalog, save_json=...) writes in PROD (aggregates only); without it the
Results sheet is left for manual entry. Shares and coverage are Excel formulas.

The engine is imported from the repo package (enbd_collections.pipelines.crx_persona) or,
when run from the bundle, from ../crx_persona/_dpd_journey.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def _engine():
    try:
        from enbd_collections.pipelines.crx_persona import _dpd_journey as J  # noqa: N811
        return J
    except ImportError:
        path = pathlib.Path(__file__).resolve().parents[1] / "crx_persona" / "_dpd_journey.py"
        spec = importlib.util.spec_from_file_location("_dpd_journey", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_dpd_journey"] = mod          # dataclasses need the module registered
        spec.loader.exec_module(mod)
        return mod


J = _engine()

# --- look ----------------------------------------------------------------------------------
FONT = "Arial"
NAVY, GREY, LIGHT, RULE = "1F3864", "595959", "F2F2F2", "BFBFBF"
STATE_COLOUR = {                      # one colour per state, used on every sheet
    "unknown": "A6A6A6",
    "early_payment_default": "C00000",
    "stabilized": "548235",
    "repeat_delinquent": "C55A11",
    "straight_roller_seasoned": "2F5597",
    "straight_roller_early_life": "8FAADC",
    "slow_roller": "7030A0",
}
BUCKET_FILL = {0: "FFFFFF", 1: "FFFFFF", 2: "FFF2CC", 3: "FFE699", 4: "F8CBAD", 5: "F4B183",
               6: "ED7D31", 7: "C55A11", 8: "843C0C", 9: "3B1A06"}
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
    ws["A2"].font = _font(size=10, italic=True, color=GREY)
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width_cols)
    ws.row_dimensions[2].height = 30
    ws.sheet_view.showGridLines = False
    return 4


def _section(ws: Worksheet, row: int, text: str, width_cols: int) -> int:
    c = ws.cell(row=row, column=1, value=text)
    c.font = _font(size=12, bold=True, color=NAVY)
    for col in range(1, width_cols + 1):
        ws.cell(row=row, column=col).border = Border(bottom=Side(style="medium", color=NAVY))
    return row + 1


def _header(ws: Worksheet, row: int, labels: list[str]) -> int:
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = _font(bold=True, color="FFFFFF")
        c.fill = _fill(NAVY)
        c.alignment = CENTER
        c.border = BOX
    return row + 1


def _row(ws: Worksheet, row: int, values: list, bold_first: bool = False, height: float | None = None) -> int:
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = _font(bold=bold_first and i == 1)
        c.alignment = WRAP
        c.border = BOX
    if height:
        ws.row_dimensions[row].height = height
    return row + 1


def _chip(cell, state: str, label: str | None = None) -> None:
    cell.value = label or J.DISPLAY_NAMES[state]
    cell.fill = _fill(STATE_COLOUR[state])
    cell.font = _font(bold=True, color=_text_on(STATE_COLOUR[state]))
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    cell.border = BOX


def _widths(ws: Worksheet, widths: list[float]) -> None:
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _print(ws: Worksheet) -> None:
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# --- content -------------------------------------------------------------------------------
R = J.STATE_RULES
FLOOR = J.PARAM_DEFAULTS["cc_history_floor_date"]
CC_WINDOW = dt.date.fromisoformat(FLOOR).strftime("%b %Y") if FLOOR else "the start of the data"
RL_WINDOW = "Jan 2019"     # RL history window start (set in the workplace params, not the bundle defaults)
WINDOWS = f"CC {CC_WINDOW}, RL {RL_WINDOW}"

# Workbook labels: the engine's display names, with workbook-only overrides.
LABELS = {**J.DISPLAY_NAMES, "unknown": "Unknown", "repeat_delinquent": "Repeat delinquent"}

STATE_TEXT = {   # state: (one sentence, typical action, changes over time)
    "unknown": (
        "We cannot see how the account fell into delinquency: the start of this delinquency "
        "is not in the history we hold.",
        "Treat on current behaviour and the other persona axes.",
        "Fixed"),
    "early_payment_default": (
        f"Fell behind within {R['epd_max_history']} months of the start of its history and has "
        "not paid since.",
        "Early-risk / first-party fraud review; early legal; no restructuring.",
        "Current: ends when the customer pays"),
    "stabilized": (
        "Paying about one month's due each month: the bucket has stopped climbing. "
        "61–180 DPD only.",
        "Offer restructuring.",
        "Current: re-read monthly"),
    "repeat_delinquent": (
        f"Was 31+ DPD before, caught up, and fell back within {R['repeat_window_months']} months.",
        "Firm promise-based plan; credibility sets the pressure.",
        "Fixed"),
    "straight_roller_seasoned": (
        f"Rolled straight to 61+ DPD (no payment), {R['seasoned_min_months']}+ months after its "
        "history began.",
        "Likely a life event: read with the other axes; best fit for a hardship route.",
        "Fixed"),
    "straight_roller_early_life": (
        f"Rolled straight to 61+ DPD within its first {R['seasoned_min_months']} months (after "
        "the EPD window).",
        "As seasoned; also an underwriting signal.",
        "Fixed"),
    "slow_roller": (
        "Paid something on the way to 61+ DPD but kept rolling.",
        "Over-indebted: longer-tenor restructure or settlement.",
        "Fixed"),
}

STEPS = [   # (step, question, state on yes, exact test)
    ("0", "Is the start of this delinquency missing?", "unknown",
     "Oldest month we hold is already overdue (CC 1+ DPD; RL 31+ DPD). "
     "Stabilized if Step 2 passes, else Unknown."),
    ("1", "Early payment default?", "early_payment_default",
     f"Fell behind within {R['epd_max_history']} months of the start of its history, with no "
     "earlier delinquency (one short paid-off slip allowed), and has not paid since: one bucket "
     "worse every month."),
    ("2", "Stabilized?", "stabilized",
     "Today 61–180 DPD and no longer getting worse. Either:\n"
     f"• short-term: in {R['stabilized_min_in_band']} of the last 6 months the bucket was within "
     "one of today's; or\n"
     f"• long-term: {R['stabilized_long_run_months']}+ months after reaching 61+ DPD, today's "
     f"bucket is at most {R['stabilized_long_run_max_rise']} higher than 6 months ago."),
    ("3", "Repeat delinquent?", "repeat_delinquent",
     "An earlier delinquency reached 31+ DPD, was cured, and ended at most "
     f"{R['repeat_window_months']} months before this one began."),
    ("4", "Straight roller?", "straight_roller_seasoned",
     "0 → 1–30 → 31–60 → 61–90 DPD, one step a month (no payment). Seasoned if "
     f"{R['seasoned_min_months']}+ months of history before this delinquency (or history older "
     "than the window); otherwise Early-life."),
    ("5", "Otherwise", "slow_roller",
     "Everything else: paid at least once on the way to 61+ DPD."),
]
STEP_OF = {"unknown": "0", "early_payment_default": "1", "stabilized": "2", "repeat_delinquent": "3",
           "straight_roller_seasoned": "4", "straight_roller_early_life": "4", "slow_roller": "5"}

TERMS = [
    ("DPD bucket", "Days-past-due band at month end (see 'Buckets & segments')."),
    ("Delinquency", "A continuous run of months at 1+ DPD."),
    ("Short slip", "An earlier 1–2 month delinquency, never past 1–30 DPD, paid off. Not counted "
                   "as an earlier delinquency."),
    ("Month to month", "One bucket worse = nothing paid. Same bucket = one month's due paid. "
                       "Better = two or more months paid."),
    ("Months before this delinquency", "Months in the history before the current delinquency "
                                       "started."),
    ("Ceiling bucket", "CC 210+ / RL 180+ DPD. The bucket cannot rise, so staying there is not a "
                       "payment."),
    ("History window", f"{WINDOWS}. With older history an account is never EPD, and a straight "
                       "roller counts as seasoned."),
]

EXAMPLES = [   # (CC buckets oldest -> newest, history cropped by the window, expected state, why)
    ([0, 0, 0, 2, 3, 4, 5], False, "early_payment_default",
     "3 clean months, then one bucket worse every month."),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9], False, "early_payment_default",
     "Same at 180+: months at the ceiling (9 9 9) are not payments."),
    ([0] * 8 + [2, 3, 4, 4, 5, 5, 5, 5, 5], False, "stabilized",
     "Holding at 91–120 DPD for 5 months."),
    ([int(c) for c in "00000000234443345433456554"], False, "stabilized",
     "Swings between 61–90 and 151–180 DPD, no worse than 6 months ago."),
    ([5, 5, 5, 5, 5, 5], True, "stabilized",
     f"Overdue since before {CC_WINDOW}, but clearly holding."),
    ([0, 2, 3, 4] + [0] * 8 + [2, 3, 4, 5], False, "repeat_delinquent",
     "Reached 61–90 DPD, caught up, fell back 8 months later."),
    ([0] * 14 + [2, 3, 4, 5], False, "straight_roller_seasoned",
     "14 clean months, then missed every payment."),
    ([0] * 6 + [2, 3, 4, 5], False, "straight_roller_early_life",
     "6 clean months, then a straight roll."),
    ([0] * 10 + [2, 2, 3, 3, 4, 5], False, "slow_roller",
     "Paid one month at 1–30 and at 31–60 DPD, still rolled."),
    ([6, 6, 7, 7, 8, 9], True, "unknown",
     "Already 121–150 DPD in the oldest month we hold."),
]
TIMELINE = 18   # months shown per example


def _chip_l(cell, state: str, label: str | None = None) -> None:
    _chip(cell, state, label or LABELS[state])


def _overview(wb: Workbook, scoring_date: str) -> None:
    ws = wb.active
    ws.title = "Overview"
    r = _title(ws, "DPD deterioration states",
               "One of the persona axes: how a delinquent account got where it is, read from its "
               "monthly DPD history. Every account in scope gets exactly one state.", 5)
    for k, v in [
        ("Scope", "Credit cards (CC) and retail loans (RL) at 61–180 DPD and at 180+ DPD on the "
                  f"scoring date ({scoring_date})."),
        ("Input", f"One DPD bucket per account per month. CC from {CC_WINDOW} (older history has "
                  f"known data-quality issues); RL from {RL_WINDOW}."),
        ("How", "Six yes/no questions in a fixed order; the first 'yes' decides. See 'How states "
                "are assigned'."),
        ("Over time", "EPD and Stabilized can change month to month. The others are fixed once "
                      "set, except that an account can move into Stabilized."),
    ]:
        lab = ws.cell(row=r, column=1, value=k)
        lab.font = _font(bold=True, color=NAVY)
        lab.alignment = WRAP
        c = ws.cell(row=r, column=2, value=v)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 22
        r += 1
    r = _section(ws, r + 1, "The states", 5)
    r = _header(ws, r, ["State", "In one sentence", "Typical action", "Changes over time?",
                        "Decided at step"])
    for st in J.STATES:
        sentence, action, moves = STATE_TEXT[st]
        _row(ws, r, [None, sentence, action, moves, STEP_OF[st]], height=36)
        _chip_l(ws.cell(row=r, column=1), st)
        ws.cell(row=r, column=5).alignment = CENTER
        r += 1
    ws.cell(row=r + 1, column=1, value="Shares: see 'Results'. Thresholds: see 'Thresholds'."
            ).font = _font(italic=True, color=GREY)
    _widths(ws, [30, 58, 50, 24, 12])
    ws.freeze_panes = "A4"
    _print(ws)


def _assignment(wb: Workbook) -> None:
    ws = wb.create_sheet("How states are assigned")
    r = _title(ws, "How states are assigned",
               "Questions are asked top to bottom; the first 'yes' decides the state.", 5)
    r = _section(ws, r, "The flow", 5)
    for step, q, st, _ in STEPS:
        c = ws.cell(row=r, column=1, value=f"Step {step}")
        c.font = _font(bold=True, color="FFFFFF")
        c.fill = _fill(NAVY)
        c.alignment = CENTER
        q_cell = ws.cell(row=r, column=2, value=q)
        q_cell.font = _font(bold=True)
        q_cell.fill = _fill(LIGHT)
        q_cell.border = BOX
        q_cell.alignment = Alignment(vertical="center", wrap_text=True)
        arrow = ws.cell(row=r, column=3, value="yes  ▶" if step != "5" else "▶")
        arrow.font = _font(bold=True, color=GREY)
        arrow.alignment = CENTER
        if step == "0":
            _chip_l(ws.cell(row=r, column=4), "unknown", "Unknown  (Stabilized if Step 2 passes)")
        elif step == "4":
            _chip_l(ws.cell(row=r, column=4), "straight_roller_seasoned",
                    f"Seasoned straight roller  ({R['seasoned_min_months']}+ months)")
            _chip_l(ws.cell(row=r, column=5), "straight_roller_early_life",
                    f"Early-life straight roller  (< {R['seasoned_min_months']} months)")
        else:
            _chip_l(ws.cell(row=r, column=4), st)
        ws.row_dimensions[r].height = 30
        r += 1
        if step != "5":
            down = ws.cell(row=r, column=2, value="no  ▼")
            down.font = _font(color=GREY)
            down.alignment = Alignment(horizontal="center")
            r += 1
    r = _section(ws, r + 1, "The exact tests", 5)
    r = _header(ws, r, ["Step", "Question", "State if yes", "Exact test", ""])
    ws.merge_cells(start_row=r - 1, start_column=4, end_row=r - 1, end_column=5)
    for step, q, st, test in STEPS:
        _row(ws, r, [step, q, None, test, None], height=62 if step == "2" else 44)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        _chip_l(ws.cell(row=r, column=3), st)
        ws.cell(row=r, column=1).alignment = CENTER
        r += 1
    r = _section(ws, r + 1, "Terms", 5)
    for term, meaning in TERMS:
        lab = ws.cell(row=r, column=1, value=term)
        lab.font = _font(bold=True)
        lab.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c = ws.cell(row=r, column=3, value=meaning)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 22
        r += 1
    _widths(ws, [9, 36, 30, 48, 44])
    _print(ws)


def _examples(wb: Workbook) -> None:
    ws = wb.create_sheet("Worked examples")
    n_lead = 2
    last_col = n_lead + TIMELINE + 2
    r = _title(ws, "Worked examples (credit cards)",
               "One account per row: monthly DPD bucket, oldest on the left, this month on the "
               "right.", last_col)
    ws.cell(row=r, column=1, value="Bucket colours").font = _font(bold=True)
    labels = {2: "1–30", 3: "31–60", 4: "61–90", 5: "91–120", 6: "121–150", 7: "151–180",
              8: "181–210", 9: "210+"}
    for i, b in enumerate(range(1, 10)):
        col = n_lead + 1 + 2 * i
        c = ws.cell(row=r, column=col, value=f"{b}: {labels[b]}" if b > 1 else "0/1: 0 DPD")
        c.fill = _fill(BUCKET_FILL[b])
        c.font = _font(size=8, bold=True, color=_text_on(BUCKET_FILL[b]))
        c.alignment = CENTER
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + 1)
    r += 2
    head = ["State", "Decided at step"] + \
        [("Now" if k == TIMELINE - 1 else f"-{TIMELINE - 1 - k}") for k in range(TIMELINE)] + ["Why", ""]
    r = _header(ws, r, head)
    ws.merge_cells(start_row=r - 1, start_column=last_col - 1, end_row=r - 1, end_column=last_col)
    for buckets, cropped, want, why in EXAMPLES:
        got = J.classify(buckets, cropped, 0, 9)
        if got["det_state"] != want:
            raise SystemExit(f"example {buckets} now gives {got['det_state']}, not {want}: "
                             "update the example or its text")
        step = "0 → 2" if (want == "stabilized" and got["starts_delinquent"]) else STEP_OF[want]
        _chip_l(ws.cell(row=r, column=1), want)
        c = ws.cell(row=r, column=2, value=step)
        c.font = _font()
        c.alignment = CENTER
        c.border = BOX
        shown = buckets[-TIMELINE:]
        pad = TIMELINE - len(shown)
        for k in range(TIMELINE):
            c = ws.cell(row=r, column=n_lead + 1 + k)
            c.border = BOX
            c.alignment = CENTER
            if k < pad:
                continue
            b = shown[k - pad]
            canon = max(b, 1)
            c.value = b
            c.fill = _fill(BUCKET_FILL[canon])
            c.font = _font(bold=k == TIMELINE - 1, color=_text_on(BUCKET_FILL[canon]))
        note = why + (f" ({len(buckets) - TIMELINE} earlier months not shown.)"
                      if len(buckets) > TIMELINE else "")
        c = ws.cell(row=r, column=last_col - 1, value=note)
        c.font = _font()
        c.alignment = WRAP
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=last_col - 1, end_row=r, end_column=last_col)
        ws.row_dimensions[r].height = 28
        r += 1
    _widths(ws, [28, 10] + [5.2] * TIMELINE + [44, 6])
    ws.freeze_panes = ws.cell(row=8, column=3)
    _print(ws)


def _thresholds(wb: Workbook) -> None:
    ws = wb.create_sheet("Thresholds")
    ws["A1"] = "Thresholds"
    ws["A1"].font = _font(size=16, bold=True, color=NAVY)
    ws.sheet_view.showGridLines = False
    r = 3
    gap = J.PARAM_DEFAULTS["max_inferred_gap_months"]
    rows = [
        ("Early payment default", "Months before first falling behind",
         f"≤ {R['epd_max_history']}", "Someone who never pays misses the 1st or 2nd bill."),
        ("Early payment default", "Earlier short slips allowed (1–2 months, paid off)",
         str(R["epd_max_blips"]), "One quickly repaid late payment does not rule out EPD."),
        ("Straight roller", "Delinquent months to reach 61–90 DPD (1–30, 31–60, 61–90)",
         str(R["straight_max_runup"]), "One bucket a month: nothing paid on the way."),
        ("Stabilized", "Last 6 months within one bucket of today's",
         f"{R['stabilized_min_in_band']} of 6",
         "Staying near the same bucket means about one month's due is paid each month."),
        ("Stabilized (long-term)", "Months since reaching 61+ DPD",
         f"{R['stabilized_long_run_months']}+", "Gives uneven payers time before a plateau counts."),
        ("Stabilized (long-term)", "Rise vs 6 months ago",
         f"≤ {R['stabilized_long_run_max_rise']} bucket", "More than one bucket means still getting worse."),
        ("Stabilized", "Highest DPD", "151–180", "At 180+ a flat bucket is not evidence of payment."),
        ("Repeat delinquent", "Depth of the earlier delinquency", "31+ DPD",
         "A cure from 31+ DPD shows real ability to catch up."),
        ("Repeat delinquent", "Months since it ended", f"≤ {R['repeat_window_months']}",
         "A relapse within a year points to the same underlying problem."),
        ("Seasoned vs early-life", "Months before this delinquency",
         f"{R['seasoned_min_months']}+", "First-year defaults point to acquisition; later ones to a change in circumstances."),
        ("History window", "CC data used from", CC_WINDOW, "Older CC data has known quality issues."),
        ("History window", "RL data used from", RL_WINDOW, "Start of the RL window."),
        ("Missing months", "Filled if the gap is at most", f"{gap} months",
         "Longer gaps: history starts after the gap."),
    ]
    r = _header(ws, r, ["Applies to", "Threshold", "Value", "Why"])
    for row in rows:
        _row(ws, r, list(row), height=22)
        ws.cell(row=r, column=3).alignment = CENTER
        ws.cell(row=r, column=3).font = _font(bold=True)
        r += 1
    _widths(ws, [24, 42, 14, 54])
    ws.freeze_panes = "A4"
    _print(ws)


def _buckets(wb: Workbook) -> None:
    ws = wb.create_sheet("Buckets & segments")
    r = _title(ws, "Buckets & segments",
               "CC and RL number buckets differently; the rules read both as DPD bands.", 5)
    r = _header(ws, r, ["DPD band", "CC bucket", "RL bucket", "Segment", "Note"])
    rows = [   # (canonical colour, band, CC, RL, segment, note)
        (1, "0 DPD", "0 (no due) / 1 (current)", "0", "—", "Clean."),
        (2, "1–30 DPD", "2", "1", "—", "Delinquency starts."),
        (3, "31–60 DPD", "3", "2", "—", ""),
        (4, "61–90 DPD", "4", "3", "61–180 DPD", "Segment starts."),
        (5, "91–120 DPD", "5", "4", "61–180 DPD", ""),
        (6, "121–150 DPD", "6", "5", "61–180 DPD", ""),
        (7, "151–180 DPD", "7", "6", "61–180 DPD", "Highest bucket for Stabilized."),
        (8, "181–210 DPD", "8", "7 (ceiling)", "180+ DPD", "RL ceiling: RL 7 = all of 180+."),
        (9, "210+ DPD", "9 (ceiling)", "7 (ceiling)", "180+ DPD", "CC ceiling."),
    ]
    for canon, *vals in rows:
        _row(ws, r, vals, height=20)
        for col in (2, 3):
            ws.cell(row=r, column=col).alignment = CENTER
        ws.cell(row=r, column=1).fill = _fill(BUCKET_FILL[canon])
        ws.cell(row=r, column=1).font = _font(bold=True, color=_text_on(BUCKET_FILL[canon]))
        r += 1
    r = _section(ws, r + 1, "Reading one month to the next", 5)
    r = _header(ws, r, ["This month vs last", "Meaning", "Months' due paid"])
    for row in [("One bucket worse", "Nothing paid", "0"),
                ("Same bucket", "One month's due paid", "1"),
                ("k buckets better", "k + 1 months paid at once", "k + 1"),
                ("Back to 0 DPD", "Cured (rare from 61+ DPD)", "all"),
                ("Same bucket at the ceiling", "Not a payment: the bucket cannot rise", "—")]:
        _row(ws, r, list(row), height=20)
        ws.cell(row=r, column=3).alignment = CENTER
        r += 1
    _widths(ws, [28, 34, 18, 16, 36])
    _print(ws)


def _data_handling(wb: Workbook) -> None:
    ws = wb.create_sheet("Data handling")
    r = _title(ws, "Data handling",
               "How the monthly history is prepared before the questions are asked.", 3)
    gap = J.PARAM_DEFAULTS["max_inferred_gap_months"]
    r = _header(ws, r, ["Situation", "What we do", "Effect on states"])
    rows = [
        (f"History before the window start ({WINDOWS})", "Not used.",
         "Never EPD; a straight roller counts as seasoned."),
        ("History starts already overdue", "Start of the delinquency is missing.",
         "Unknown, unless Stabilized."),
        ("Missing month between two equal buckets", "Filled with that bucket.", "None."),
        ("Missing month where only a straight roll fits", "Filled as the roll.", "None."),
        (f"Other gaps of up to {gap} months", "Filled: last bucket carried, rising as late as "
         "possible.", "Can read as a payment."),
        ("Longer gaps", "History starts after the gap.", "As for history before the window start."),
        ("One-month data errors (4 0 4, 0 3 0)", "Corrected to the neighbours.",
         "No false cure or false earlier delinquency."),
        ("Billing-cycle jumps (3 3 5 for 3 4 5), CC", "Corrected to the roll.", "No false payment."),
    ]
    for row in rows:
        _row(ws, r, list(row), bold_first=True, height=30)
        r += 1
    _widths(ws, [40, 44, 44])
    _print(ws)


def _results(wb: Workbook, results: dict | None, scoring_date: str) -> None:
    ws = wb.create_sheet("Results")
    blocks = [("cc", "60_180", "CC 61–180 DPD"), ("cc", "180_plus", "CC 180+ DPD"),
              ("rl", "60_180", "RL 61–180 DPD"), ("rl", "180_plus", "RL 180+ DPD")]
    last_col = 1 + 2 * len(blocks)
    r = _title(ws, "Results",
               f"Accounts per state, scoring date {scoring_date}. Blue = counts from the scoring "
               "run; shares and coverage are calculated. Yellow = to fill in.", last_col)
    head = ["State"]
    for _, _, label in blocks:
        head += [f"{label}\naccounts", "share"]
    r = _header(ws, r, head)
    ws.row_dimensions[r - 1].height = 44
    first = r
    total_row = first + len(J.STATES)

    def seg_res(prod, seg):
        return (results or {}).get("products", {}).get(prod, {}).get("segments", {}).get(seg)

    for st in J.STATES:
        _chip_l(ws.cell(row=r, column=1), st)
        for b, (prod, seg, _) in enumerate(blocks):
            col = 2 + 2 * b
            res = seg_res(prod, seg)
            c = ws.cell(row=r, column=col)
            if res is not None:
                c.value = int(res["state_counts"].get(st, 0))
            else:
                c.fill = _fill("FFFF00")
            c.font = _font(color="0000FF")
            c.number_format = "#,##0"
            c.border = BOX
            L = get_column_letter(col)
            s = ws.cell(row=r, column=col + 1,
                        value=f'=IF(${L}${total_row}=0,"",{L}{r}/${L}${total_row})')
            s.number_format = "0.0%"
            s.font = _font()
            s.border = BOX
        r += 1
    ws.cell(row=r, column=1, value="Classified accounts").font = _font(bold=True)
    for b in range(len(blocks)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b, value=f"=SUM({L}{first}:{L}{r - 1})")
        c.number_format = "#,##0"
        c.font = _font(bold=True)
        c.border = Border(top=Side(style="medium", color=NAVY))
    r += 1
    lost_row = r
    ws.cell(row=r, column=1, value="In segment, not classified").font = _font()
    for b, (prod, seg, _) in enumerate(blocks):
        res = seg_res(prod, seg)
        c = ws.cell(row=r, column=2 + 2 * b)
        if res is not None:
            c.value = int(res["in_segment_not_classified"])
        else:
            c.fill = _fill("FFFF00")
        c.font = _font(color="0000FF")
        c.number_format = "#,##0"
    r += 1
    ws.cell(row=r, column=1, value="Coverage (target 99.9%)").font = _font(bold=True)
    for b in range(len(blocks)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b,
                    value=f'=IF(({L}{total_row}+{L}{lost_row})=0,"",{L}{total_row}/({L}{total_row}+{L}{lost_row}))')
        c.number_format = "0.00%"
        c.font = _font(bold=True)
    r += 2
    for note in [
        "Stabilized is not possible at 180+ (61–180 DPD only).",
        "Roll rates are not shown: they would be measured on the same months that define the states.",
        "No account-level data.",
    ]:
        c = ws.cell(row=r, column=1, value=note)
        c.font = _font(italic=True, color=GREY)
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=last_col)
        r += 1
    _widths(ws, [34] + [14, 9] * len(blocks))
    ws.freeze_panes = ws.cell(row=first, column=2)
    _print(ws)


def build(out: pathlib.Path, results: dict | None, scoring_date: str) -> pathlib.Path:
    wb = Workbook()
    _overview(wb, scoring_date)
    _assignment(wb)
    _examples(wb)
    _thresholds(wb)
    _buckets(wb)
    _data_handling(wb)
    _results(wb, results, scoring_date)
    wb.calculation.fullCalcOnLoad = True      # Excel computes the share / coverage formulas on open
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=f"dpd_deterioration_states_{dt.date.today():%Y%m%d}.xlsx")
    ap.add_argument("--results", action="append", default=[],
                    help="JSON written by prod_check.report(..., save_json=...); repeat it for "
                         "each run (one per segment) — they are merged")
    ap.add_argument("--scoring-date", dest="scoring_date", default="(scoring date)")
    a = ap.parse_args()
    res = None
    for path in a.results:
        part = json.loads(pathlib.Path(path).read_text())
        if res is None:
            res = {"generated": part.get("generated"), "products": {}}
        res["generated"] = max(filter(None, [res["generated"], part.get("generated")]), default=None)
        for prod, body in part.get("products", {}).items():
            tgt = res["products"].setdefault(prod, {"segments": {}})
            for seg, val in body.get("segments", {}).items():
                if seg in tgt["segments"]:
                    raise SystemExit(f"{prod} {seg} appears in more than one --results file")
                tgt["segments"][seg] = val
    print(build(pathlib.Path(a.out), res, a.scoring_date))


if __name__ == "__main__":
    main()
