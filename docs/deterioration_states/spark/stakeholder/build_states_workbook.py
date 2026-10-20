"""Build the stakeholder workbook for the DPD deterioration states (the 'deterioration axis').

    python build_states_workbook.py --out dpd_deterioration_states_<date>.xlsx \
        [--results results_60_180.json --results results_180_plus.json] [--snapshot "Aug 2026"]

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
FLOOR_TXT = dt.date.fromisoformat(FLOOR).strftime("%b %Y") if FLOOR else "the start of the data"

STATE_TEXT = {   # state: (one sentence, typical action, fixed or current)
    "unknown": (
        "We cannot see how the account fell into delinquency: the oldest month we hold is "
        "already overdue.",
        "Treat on current behaviour and the other persona axes only.",
        "Fixed"),
    "early_payment_default": (
        f"Fell behind within its first {R['epd_max_history']} months on book and has never "
        "paid since — still getting worse every month.",
        "Early-risk / first-party fraud review, early legal; no restructuring.",
        "Current — ends the month the customer pays"),
    "stabilized": (
        "Paying about one month's due each month: the DPD bucket has stopped climbing. "
        "Only possible up to 151–180 DPD.",
        "Offer restructuring to break the hardship.",
        "Current — re-read every month"),
    "repeat_delinquent": (
        f"Was 31+ DPD before, caught up, and fell back in within {R['repeat_window_months']} "
        "months.",
        "Has shown they can catch up: firm promise-based plan; credibility decides the pressure.",
        "Fixed"),
    "straight_roller_seasoned": (
        f"On book {R['seasoned_min_months']}+ months, then missed every payment straight from "
        "current to 61+ DPD.",
        "Life event: read with the other axes (departed / income shock / won't pay); most "
        "likely to respond to a hardship route.",
        "Fixed"),
    "straight_roller_early_life": (
        f"Same straight roll, but in the first {R['seasoned_min_months']} months on book "
        "(after the EPD window).",
        "Same triage as seasoned; also an underwriting signal for acquisition.",
        "Fixed"),
    "slow_roller": (
        "Paid something on the way down to 61+ DPD but kept rolling.",
        "Over-indebted: longer-tenor restructure or settlement.",
        "Fixed"),
}

STEPS = [   # (step, short question, state on yes, exact test, why it sits here)
    ("0", "Can we see how the account fell in?",
     "unknown",
     "If the OLDEST month we hold is already 1+ DPD, the start of this delinquency is not "
     f"visible (CC history before {FLOOR_TXT} is not used; migrated, restructured or missing "
     "history). Such an account is Stabilized if the Step 2 test passes, otherwise Unknown.",
     "Every later step needs the start of the journey; Stabilized needs only the last 6 months."),
    ("1", "Early payment default?",
     "early_payment_default",
     f"All of: at most {R['epd_max_history']} months on book before first falling 1+ DPD "
     f"(one short slip that was paid off is allowed); no earlier delinquency; and NOT ONE "
     "payment since — every month one bucket worse (months held at the ceiling bucket, "
     "CC 210+ / RL 180+, do not count as payments).",
     "Checked before Stabilized so a brand-new non-payer is never read as stable."),
    ("2", "Stabilized?",
     "stabilized",
     f"Today at most 151–180 DPD (CC bucket ≤ {R['stabilized_max_bucket']}, RL ≤ "
     f"{R['stabilized_max_bucket'] - 1}) — never in 180+ — AND either "
     f"{R['stabilized_min_in_band']} of the last 6 months within one bucket of today's, or "
     f"{R['stabilized_long_run_months']}+ months since first reaching 61+ DPD and at most "
     f"{R['stabilized_long_run_max_rise']} bucket higher than 6 months ago.",
     "Current behaviour wins over how the account fell in: it points to the action."),
    ("3", "Repeat delinquent?",
     "repeat_delinquent",
     "An earlier delinquency reached 31+ DPD, was cured, and ended at most "
     f"{R['repeat_window_months']} months before this one started.",
     "Recent recovery is stronger evidence than the shape of the latest fall."),
    ("4", "Straight roller?",
     "straight_roller_seasoned",
     "Went 1–30 → 31–60 → 61–90 DPD in consecutive months (no payment on the way). "
     f"Seasoned if on book {R['seasoned_min_months']}+ months before the fall, or if its "
     f"history starts before {FLOOR_TXT} (so it is older than that); otherwise Early-life.",
     "Splits by tenure because the action differs (life event vs underwriting)."),
    ("5", "Otherwise",
     "slow_roller",
     "Paid at least once on the way down to 61+ DPD but kept rolling.",
     "Everything left: no account is unclassified."),
]
STEP_OF = {"unknown": "0", "early_payment_default": "1", "stabilized": "2", "repeat_delinquent": "3",
           "straight_roller_seasoned": "4", "straight_roller_early_life": "4", "slow_roller": "5"}

TERMS = [
    ("DPD bucket", "The account's days-past-due band at month end (see 'Buckets & segments'). "
                   "One value per month is all the states use."),
    ("Delinquency (spell)", "A continuous run of months at 1+ DPD. The current spell is the one "
                            "the account is in today."),
    ("Short slip (blip)", "An earlier 1–2 month spell that never passed 1–30 DPD and was paid "
                          "off. It is not counted as an earlier delinquency."),
    ("Month-to-month reading", "One bucket worse = nothing paid (roll). Same bucket = one "
                               "month's due paid (hold). Better = two or more months paid."),
    ("Months on book before the spell", "Months of history before the current spell started."),
    ("Ceiling bucket", "The highest bucket: CC 210+ DPD, RL 180+ DPD. It cannot rise, so staying "
                       "there is not a payment."),
    ("Cropped history", f"Older months exist but are not used (CC before {FLOOR_TXT}; a long gap "
                        "in the data). A cropped account is never EPD and counts as seasoned."),
]

EXAMPLES = [   # (product, buckets oldest -> newest, cropped, expected state, why)
    ("CC", [0, 0, 0, 2, 3, 4, 5], False, "early_payment_default",
     "3 clean months, then one bucket worse every month: never paid."),
    ("CC", [0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9], False, "early_payment_default",
     "Same story at 180+: the months held at the ceiling (9 9 9) are not payments."),
    ("CC", [0] * 8 + [2, 3, 4, 4, 5, 5, 5, 5, 5], False, "stabilized",
     "Holding at 91–120 DPD for 5 months: paying about one month's due."),
    ("CC", [int(c) for c in "00000000234443345433456554"], False, "stabilized",
     "Swings between 61–90 and 151–180 DPD but no worse than 6 months ago: pays on average."),
    ("CC", [5, 5, 5, 5, 5, 5], True, "stabilized",
     f"Journey start not visible (delinquent since before {FLOOR_TXT}), but clearly holding."),
    ("CC", [0, 2, 3, 4] + [0] * 8 + [2, 3, 4, 5], False, "repeat_delinquent",
     "Reached 61–90 DPD, caught up fully, fell back in 8 months later."),
    ("CC", [0] * 14 + [2, 3, 4, 5], False, "straight_roller_seasoned",
     "14 clean months, then missed every payment."),
    ("CC", [0, 0, 0, 2, 3, 4], True, "straight_roller_seasoned",
     f"Looks short, but its history starts before {FLOOR_TXT}: older than a year."),
    ("CC", [0] * 6 + [2, 3, 4, 5], False, "straight_roller_early_life",
     "6 clean months (past the EPD window), then a straight roll."),
    ("CC", [0] * 10 + [2, 2, 3, 3, 4, 5], False, "slow_roller",
     "Paid one month at 1–30 and at 31–60 DPD on the way down, still rolled."),
    ("CC", [0] * 12 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], False, "straight_roller_seasoned",
     "Holding at 181–210 DPD is NOT stabilized: Stabilized stops at 151–180 DPD."),
    ("CC", [6, 6, 7, 7, 8, 9], True, "unknown",
     "Already 121–150 DPD in the oldest month we hold: the fall is not visible."),
    ("RL", [0] * 14 + [1, 2, 3, 4], False, "straight_roller_seasoned",
     "Retail loan, RL numbering (1 = 1–30 DPD): reads exactly like the CC case above."),
]
TIMELINE = 18   # months shown per example


def _overview(wb: Workbook, snapshot: str) -> None:
    ws = wb.active
    ws.title = "Overview"
    r = _title(ws, "DPD deterioration states",
               "One of the persona axes: how a delinquent account got where it is, read only from "
               "its monthly DPD history. Every account in scope gets exactly one of seven states.", 5)
    for k, v in [
        ("Scope", "Credit cards (CC) and retail loans (RL) at 61–180 DPD and at 180+ DPD on the "
                  f"snapshot date ({snapshot}). Both segments use the same seven states."),
        ("Input", f"One DPD bucket per account per month. CC from {FLOOR_TXT} (older history has "
                  "known data-quality issues); RL full history."),
        ("How", "Six yes/no questions asked in a fixed order; the first 'yes' decides the state. "
                "See 'How states are assigned'."),
        ("Over time", "Stabilized and EPD describe current behaviour and can change month to "
                      "month. The others describe how the account fell in and stay fixed — "
                      "except that any account can move into Stabilized."),
    ]:
        lab = ws.cell(row=r, column=1, value=k)
        lab.font = _font(bold=True, color=NAVY)
        lab.alignment = WRAP
        c = ws.cell(row=r, column=2, value=v)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 30
        r += 1
    r = _section(ws, r + 1, "The seven states", 5)
    r = _header(ws, r, ["State", "In one sentence", "Typical action", "Changes over time?",
                        "Decided at step"])
    for st in J.STATES:
        sentence, action, moves = STATE_TEXT[st]
        _chip(ws.cell(row=r, column=1), st)
        _row(ws, r, [None, sentence, action, moves, STEP_OF[st]], height=42)
        _chip(ws.cell(row=r, column=1), st)
        ws.cell(row=r, column=5).alignment = CENTER
        r += 1
    ws.cell(row=r + 1, column=1, value="Shares by product and segment: see 'Results'. "
            "Thresholds: see 'Thresholds'.").font = _font(italic=True, color=GREY)
    _widths(ws, [30, 58, 52, 24, 12])
    ws.freeze_panes = "A4"
    _print(ws)


def _assignment(wb: Workbook) -> None:
    ws = wb.create_sheet("How states are assigned")
    r = _title(ws, "How states are assigned",
               "Questions are asked top to bottom. The first 'yes' decides the state, so every "
               "account lands in exactly one state. Read the flow first, then the exact tests.", 6)
    r = _section(ws, r, "The flow", 6)
    for i, (step, q, st, _, _) in enumerate(STEPS):
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
            _chip(ws.cell(row=r, column=4), "unknown",
                  "Unknown  (or Stabilized, if the Step 2 test passes)")
        elif step == "4":
            _chip(ws.cell(row=r, column=4), "straight_roller_seasoned",
                  f"Seasoned straight roller  ({R['seasoned_min_months']}+ months on book)")
            _chip(ws.cell(row=r, column=5), "straight_roller_early_life",
                  f"Early-life straight roller  (< {R['seasoned_min_months']} months)")
        else:
            _chip(ws.cell(row=r, column=4), st)
        ws.row_dimensions[r].height = 30
        r += 1
        if step != "5":
            down = ws.cell(row=r, column=2, value="no  ▼")
            down.font = _font(color=GREY)
            down.alignment = Alignment(horizontal="center")
            r += 1
    r = _section(ws, r + 1, "The exact tests", 6)
    r = _header(ws, r, ["Step", "Question", "State if yes", "Exact test", "", "Why at this point"])
    for step, q, st, test, why in STEPS:
        _row(ws, r, [step, q, None, test, None, why], height=66)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        _chip(ws.cell(row=r, column=3), st)
        ws.cell(row=r, column=1).alignment = CENTER
        r += 1
    r = _section(ws, r + 1, "Terms used above", 6)
    for term, meaning in TERMS:
        lab = ws.cell(row=r, column=1, value=term)
        lab.font = _font(bold=True)
        lab.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c = ws.cell(row=r, column=3, value=meaning)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
        ws.row_dimensions[r].height = 28
        r += 1
    _widths(ws, [9, 34, 26, 34, 34, 42])
    _print(ws)


def _examples(wb: Workbook) -> None:
    ws = wb.create_sheet("Worked examples")
    n_lead = 3
    last_col = n_lead + TIMELINE + 2
    r = _title(ws, "Worked examples",
               "Each row is one account's monthly DPD bucket, oldest on the left, this month on "
               "the right. Every example is run through the production rules when this workbook "
               "is built.", last_col)
    # legend
    ws.cell(row=r, column=1, value="Bucket colours (CC numbering)").font = _font(bold=True)
    labels = {0: "0", 1: "0", 2: "1–30", 3: "31–60", 4: "61–90", 5: "91–120", 6: "121–150",
              7: "151–180", 8: "181–210", 9: "210+"}
    for i, b in enumerate(range(1, 10)):
        col = n_lead + 1 + 2 * i
        c = ws.cell(row=r, column=col, value=f"{b}: {labels[b]}" if b > 1 else "0/1: 0 DPD")
        c.fill = _fill(BUCKET_FILL[b])
        c.font = _font(size=8, bold=True, color=_text_on(BUCKET_FILL[b]))
        c.alignment = CENTER
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + 1)
    r += 2
    head = ["State", "Product", "Decided at step"] + \
        [("Now" if k == TIMELINE - 1 else f"-{TIMELINE - 1 - k}") for k in range(TIMELINE)] + ["Why", ""]
    r = _header(ws, r, head)
    ws.merge_cells(start_row=r - 1, start_column=last_col - 1, end_row=r - 1, end_column=last_col)
    for product, buckets, cropped, want, why in EXAMPLES:
        offset, top = (0, 9) if product == "CC" else (1, 8)
        got = J.classify(buckets, cropped, offset, top)
        if got["det_state"] != want:
            raise SystemExit(f"example {buckets} ({product}) now gives {got['det_state']}, "
                             f"not {want}: update the example or its text")
        step = STEP_OF[want] if not (want == "stabilized" and got["starts_delinquent"]) else "0 → 2"
        _chip(ws.cell(row=r, column=1), want)
        for col, v in ((2, product), (3, step)):
            c = ws.cell(row=r, column=col, value=v)
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
                c.value = "·" if not cropped else ""
                c.font = _font(color=RULE)
                continue
            b = shown[k - pad]
            canon = max(b + offset, 1)
            c.value = b
            c.fill = _fill(BUCKET_FILL[canon])
            c.font = _font(bold=k == TIMELINE - 1, color=_text_on(BUCKET_FILL[canon]))
        note = why
        if len(buckets) > TIMELINE:
            note += f" ({len(buckets) - TIMELINE} earlier months not shown.)"
        if cropped:
            note += f" Older history exists but is not used."
        c = ws.cell(row=r, column=last_col - 1, value=note)
        c.font = _font()
        c.alignment = WRAP
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=last_col - 1, end_row=r, end_column=last_col)
        ws.row_dimensions[r].height = 30
        r += 1
    ws.cell(row=r + 1, column=1, value="'·' = no history yet (account not open). RL buckets: 0 = "
            "0 DPD, 1 = 1–30 … 6 = 151–180, 7 = 180+ — coloured like the CC bucket one higher."
            ).font = _font(italic=True, color=GREY)
    _widths(ws, [28, 9, 10] + [5.2] * TIMELINE + [48, 8])
    ws.freeze_panes = ws.cell(row=8, column=4)
    _print(ws)


def _thresholds(wb: Workbook) -> None:
    ws = wb.create_sheet("Thresholds")
    r = _title(ws, "Thresholds",
               "The numbers behind the rules, as used by the pipeline. Business thresholds change "
               "only with the business owner. Editing a cell here does NOT change the pipeline.", 6)
    rows = [
        ("Early payment default", "Months on book allowed before the first missed payment",
         R["epd_max_history"], "months", "A customer who never pays misses the 1st or 2nd bill: "
         "2–3 clean months at most.", "epd_max_history"),
        ("Early payment default", "Short paid-off slips allowed before the fall",
         R["epd_max_blips"], "slips", "One brief slip that was paid off does not show good "
         "behaviour was ever established.", "epd_max_blips"),
        ("Straight roller", "Months from current to 61–90 DPD to count as a straight roll",
         R["straight_max_runup"], "months", "1–30 → 31–60 → 61–90 in consecutive months = no "
         "payment on the way.", "straight_max_runup"),
        ("Stabilized", "Of the last 6 months, how many within one bucket of today's",
         R["stabilized_min_in_band"], "of 6", "The bank's existing stabilized rule.",
         "stabilized_min_in_band"),
        ("Stabilized", "Long-run clause: months since first reaching 61+ DPD",
         R["stabilized_long_run_months"], "months", "Gives an account two full up-down cycles "
         "before a plateau counts as stable.", "stabilized_long_run_months"),
        ("Stabilized", "Long-run clause: at most this many buckets higher than 6 months ago",
         R["stabilized_long_run_max_rise"], "bucket", "One bucket of drift is normal; more is "
         "still getting worse.", "stabilized_long_run_max_rise"),
        ("Stabilized", "Highest bucket at which an account can be Stabilized",
         f"CC {R['stabilized_max_bucket']} / RL {R['stabilized_max_bucket'] - 1}", "151–180 DPD",
         "At 180+ staying in the same bucket is not evidence of payment.", "stabilized_max_bucket"),
        ("Repeat delinquent", "Depth the earlier delinquency must have reached",
         "31–60 DPD", "bucket", "Cures from 61+ DPD are rare; 31+ DPD matches the bank's own "
         "re-default view.", "repeat_min_prior_peak"),
        ("Repeat delinquent", "Months between the earlier cure and the new fall",
         R["repeat_window_months"], "months", "The common re-default window.", "repeat_window_months"),
        ("Seasoned vs early-life", "Months on book before the fall to count as seasoned",
         R["seasoned_min_months"], "months", "Standard first-year early-life window; EPD already "
         "takes the first 3 months.", "seasoned_min_months"),
        ("Data (CC only)", "Billing history used from",
         FLOOR_TXT, "date", "Older CC history has known data-quality issues (temporary).",
         "cc_history_floor_date"),
        ("Data", "Missing months filled by inference if the gap is at most",
         J.PARAM_DEFAULTS["max_inferred_gap_months"], "months", "Longer gaps: history starts "
         "after the gap (see 'Data handling').", "max_inferred_gap_months"),
    ]
    r = _header(ws, r, ["Applies to", "Threshold", "Value", "Unit", "Why this value", "Name in code"])
    for row in rows:
        _row(ws, r, list(row), height=32)
        ws.cell(row=r, column=3).alignment = CENTER
        ws.cell(row=r, column=3).font = _font(bold=True)
        ws.cell(row=r, column=6).font = _font(size=8, color=GREY)
        r += 1
    _widths(ws, [22, 50, 12, 12, 52, 28])
    ws.freeze_panes = "A5"
    _print(ws)


def _buckets(wb: Workbook) -> None:
    ws = wb.create_sheet("Buckets & segments")
    r = _title(ws, "Buckets & segments",
               "CC and RL number their buckets differently; the rules are the same once both are "
               "read as DPD bands.", 5)
    r = _header(ws, r, ["DPD band", "CC bucket", "RL bucket", "Segment", "Note"])
    rows = [
        ("0 DPD", "0 (no due) / 1 (current)", "0", "—", "Clean."),
        ("1–30 DPD", "2", "1", "—", "Delinquency starts here."),
        ("31–60 DPD", "3", "2", "—", ""),
        ("61–90 DPD", "4", "3", "61–180 DPD", "Spine starts here."),
        ("91–120 DPD", "5", "4", "61–180 DPD", ""),
        ("121–150 DPD", "6", "5", "61–180 DPD", ""),
        ("151–180 DPD", "7", "6", "61–180 DPD", "Highest bucket at which Stabilized is possible."),
        ("181–210 DPD", "8", "7 (ceiling)", "180+ DPD", "RL ceiling: RL 7 covers all of 180+."),
        ("210+ DPD", "9 (ceiling)", "7 (ceiling)", "180+ DPD", "CC ceiling. Staying at the ceiling is not a payment."),
    ]
    for i, row in enumerate(rows):
        _row(ws, r, list(row), height=20)
        canon = max(i, 1) if i else 1
        for col in (2, 3):
            ws.cell(row=r, column=col).alignment = CENTER
        ws.cell(row=r, column=1).fill = _fill(BUCKET_FILL[canon + (1 if i else 0) if i else 1])
        ws.cell(row=r, column=1).font = _font(bold=True, color=_text_on(BUCKET_FILL[min(i + 1, 9) if i else 1]))
        r += 1
    r = _section(ws, r + 1, "Reading one month to the next", 5)
    r = _header(ws, r, ["Bucket this month vs last", "Meaning", "Months' due paid"])
    for row in [("One bucket worse", "Roll — nothing paid", "0"),
                ("Same bucket (below the ceiling)", "Hold — one month's due paid", "1"),
                ("k buckets better", "Paid k + 1 months at once", "k + 1"),
                ("Back to 0 DPD", "Cure — rare from 61+ DPD", "all"),
                ("Same bucket AT the ceiling", "Unknown — the bucket cannot rise; NOT a payment", "—")]:
        _row(ws, r, list(row), height=30)
        ws.cell(row=r, column=3).alignment = CENTER
        r += 1
    _widths(ws, [30, 34, 18, 16, 50])
    _print(ws)


def _data_handling(wb: Workbook) -> None:
    ws = wb.create_sheet("Data handling")
    r = _title(ws, "Data handling",
               "How the monthly history is prepared before the questions are asked. Nothing is "
               "dropped silently; every fix is counted per account.", 3)
    r = _header(ws, r, ["Situation", "What we do", "Effect on the states"])
    rows = [
        (f"CC history before {FLOOR_TXT}", "Not used (known data-quality issue, temporary).",
         "The account's history is 'cropped': never EPD; a straight roller counts as seasoned; "
         "if the oldest month we hold is overdue → Unknown (unless Stabilized)."),
        ("Two bills in one month, none in the next", "Billing-cycle shift: one bill is moved to "
         "the empty month.", "None — restores the true monthly sequence."),
        ("A missing month between two equal buckets", "Filled with that bucket.", "None."),
        ("A missing month where only a straight roll fits (3 _ 5)", "Filled as the roll (3 4 5).",
         "None."),
        (f"Other gaps of up to {J.PARAM_DEFAULTS['max_inferred_gap_months']} months",
         "Filled: last known bucket carried, rising as late as possible.",
         "Can read as a payment (hold); counted per account."),
        ("Longer gaps", "History starts after the gap.", "Treated like cropped history."),
        ("Impossible one-month blips (4 0 4, 0 3 0)", "Corrected to the neighbours.",
         "Prevents a false cure or a false earlier delinquency."),
        ("Billing-cycle jumps (3 3 5 / 3 5 5 for 3 4 5)", "Corrected to the straight roll.",
         "Prevents a false payment."),
        ("No bucket on any row / no bill in the window", "Account kept with a status, not "
         "classified.", "Reported as lost coverage (target: 99.9% classified)."),
        ("Last month older than the snapshot", "Flagged (months stale).", "Classified on the "
         "history we have."),
    ]
    for row in rows:
        _row(ws, r, list(row), bold_first=True, height=44)
        r += 1
    _widths(ws, [38, 48, 62])
    _print(ws)


def _results(wb: Workbook, results: dict | None, snapshot: str) -> None:
    ws = wb.create_sheet("Results")
    blocks = [("cc", "60_180", "CC 61–180 DPD"), ("cc", "180_plus", "CC 180+ DPD"),
              ("rl", "60_180", "RL 61–180 DPD"), ("rl", "180_plus", "RL 180+ DPD")]
    last_col = 1 + 2 * len(blocks)
    src = f"PROD run, snapshot {snapshot}" + (f", checked {results.get('generated')}" if results else "")
    r = _title(ws, "Results",
               f"Accounts per state ({src}). Blue numbers come from the PROD check "
               "(prod_check.report(catalog, save_json=...)); shares and coverage are formulas. "
               "Yellow = still to fill in.", last_col)
    head = ["State"]
    for _, _, label in blocks:
        head += [f"{label}\naccounts", "share"]
    r = _header(ws, r, head)
    ws.row_dimensions[r - 1].height = 44
    first = r
    total_row = first + len(J.STATES)
    for st in J.STATES:
        _chip(ws.cell(row=r, column=1), st)
        for b, (prod, seg, _) in enumerate(blocks):
            col = 2 + 2 * b
            seg_res = ((results or {}).get("products", {}).get(prod, {}).get("segments", {}).get(seg))
            c = ws.cell(row=r, column=col)
            if seg_res is not None:
                c.value = int(seg_res["state_counts"].get(st, 0))
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
        seg_res = ((results or {}).get("products", {}).get(prod, {}).get("segments", {}).get(seg))
        c = ws.cell(row=r, column=2 + 2 * b)
        if seg_res is not None:
            c.value = int(seg_res["in_segment_not_classified"])
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
        "Stabilized cannot occur at 180+ by design (Stabilized stops at 151–180 DPD).",
        "Roll rates are not shown: measured on the same months that define a state they are "
        "circular (EPD rolls 100% by definition). Forward-looking outcomes come from the backtest.",
        "Aggregates only: no account ids, no DPD histories.",
    ]:
        c = ws.cell(row=r, column=1, value=note)
        c.font = _font(italic=True, color=GREY)
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=last_col)
        ws.row_dimensions[r].height = 26
        r += 1
    _widths(ws, [34] + [14, 9] * len(blocks))
    ws.freeze_panes = ws.cell(row=first, column=2)
    _print(ws)


def _changes(wb: Workbook) -> None:
    ws = wb.create_sheet("What changed")
    r = _title(ws, "What changed since the 16 Oct 2026 version", "", 2)
    r = _header(ws, r, ["Change", "Why"])
    rows = [
        ("Retail loans and the 180+ segment added, with the same seven states as CC 61–180.",
         "One vocabulary for every product and segment."),
        ("'Not classified — history starts delinquent' is now 'Unknown' and also covers accounts "
         f"already overdue in the oldest month we hold (e.g. delinquent since before {FLOOR_TXT}).",
         "When the start of the journey is not visible, how the account fell in would be a guess."),
        ("Stabilized only up to 151–180 DPD; never at 180+.",
         "At 180+ staying in the same bucket is not evidence of payment."),
        ("Months held at the ceiling bucket (CC 210+, RL 180+) are not payments.",
         "Keeps EPD meaningful at 180+."),
        ("The live 'Rule tester' sheet is replaced by worked examples computed by the production "
         "rules.", "The formulas were a second copy of the rules and had drifted (no Unknown, no "
                   "180+ rule)."),
        ("Roll rate removed from the results.",
         "It was measured on the same months that define the states (EPD = 100% by definition)."),
        ("Thresholds shown with plain names; parameter names kept in a side column.",
         "Readable for the business; traceable to the code."),
    ]
    for row in rows:
        _row(ws, r, list(row), height=44)
        r += 1
    _widths(ws, [80, 70])
    _print(ws)


def build(out: pathlib.Path, results: dict | None, snapshot: str) -> pathlib.Path:
    wb = Workbook()
    _overview(wb, snapshot)
    _assignment(wb)
    _examples(wb)
    _thresholds(wb)
    _buckets(wb)
    _data_handling(wb)
    _results(wb, results, snapshot)
    _changes(wb)
    wb.calculation.fullCalcOnLoad = True      # Excel computes the share / coverage formulas on open
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=f"dpd_deterioration_states_{dt.date.today():%Y%m%d}.xlsx")
    ap.add_argument("--results", action="append", default=[],
                    help="JSON written by prod_check.report(..., save_json=...); repeat it for "
                         "each run (one per segment) — they are merged")
    ap.add_argument("--snapshot", default="(snapshot month)")
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
    print(build(pathlib.Path(a.out), res, a.snapshot))


if __name__ == "__main__":
    main()
