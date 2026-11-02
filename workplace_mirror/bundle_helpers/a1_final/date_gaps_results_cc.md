# Handoff 28: `tmp_validation/a1_date_gaps/summary.md` (1 photo), 2026-11-02

## Context for Claude Code
- Source: 1 phone photo of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-11-02 ~14:47 Dubai. Tabs: `pipeline_registry.py`, `11_a4_rl_restructure_chains.md`, `summary.md` (U = untracked, active). Path: `tmp_validation > a1_date_gaps > summary.md`. Status bar: Ln 1, Col 1, Spaces: 4, UTF-8.
- Title: "A1 date gaps - cc_60_180 (rl_60_180 pending)". Date-coverage check of the A1 input sources (alerts, WM, comp, DCORE, balances): which extract dates are missing or thin, whether they fall in the A1 window, and whether a reload or rebuild fixes them. Relates to the stale-alert finding (H7) in handoff 25 and the alert-salary work in handoffs 19, 23 and 24. Follows handoffs 1-27.
- The whole file (lines 1-23) is visible in this photo. RL is pending (RL sources `int_loan_master` and `feature_retail_loans` not run yet).
- Transcribed by Claude (chat) from the image, not copied from the file. Verify dates and counts against the file.

---

## `summary.md` (lines 1-23)

````
1   # A1 date gaps - cc_60_180 (rl_60_180 pending)
2
3   A1 window = Nov 2025-Aug 2026. Gaps checked from 2025-01-01.
4
5   | Source | Status | Missing / thin | In window | Fix |
6   |---|---|---|---|---|
7   | Raw alerts | GAPS | miss 05-23, 06-26, 08-06, 08-31; 05-15 has 11 rows | Yes | Reload raw |
8   | stg / prm alerts | GAPS | end 08-27; miss 05-15, 05-23, 06-26, 08-06 | Yes | Rebuild stg+prm |
9   | Alerts thin days | GAPS | 2026-03-09 15%, 01-05 27%, 08-24 18-34%, 07-07 35% | Yes | Reload raw |
10  | WM salary, inflow | OK | none; last week 20260804 | - | - |
11  | WM eod balance | OK | none; last week 20260904 | - | - |
12  | comp_financial_tran | OK | none, 2025-01-01..2026-10-31 | - | - |
13  | prm_casa_transactions | OK | starts 2025-02-01, ends 2026-10-27 | No | - |
14  | prm_casa_return_events | OK | starts 2025-08-01; no missing days | No | - |
15  | wm_pri_labelled | OK | none, to 2026-09-30 | - | - |
16  | DCORE followup | GAPS | 2025-11-15..18, 2026-07-06, 2026-08-07 | Yes | Reload raw, rebuild |
17  | prm_balance (CC) | OK | 21 of 21 months | - | - |
18
19  - Alert salary Jun-Oct 2026: 86 of 153 extract dates; absent 06-26, 08-06 and 08-28 onward.
20  - DCORE holes are the same 32 days in raw, stg and prm, so the source is short.
21  - Alerts copies hold about 3.6% of raw (CIF scope); no collapsed days.
22  - RL sources (int_loan_master, feature_retail_loans) not run yet.
23
````

## Notes on specific spots
- Line 3: the A1 window is Nov 2025 to Aug 2026; the gap check starts at 2025-01-01. Dates in the table are written month-day (MM-DD) without the year, so the year in rows 7-9 is not stated in the photo. Row 9's first entry gives the year (`2026-03-09`); the rest read as 2026 by the context of the window, but that is my reading, not file text.
- Line 7: "05-15 has 11 rows" is a thin day, not a missing day.
- Line 10-11: "last week 20260804" and "last week 20260904" are written as yyyymmdd as shown. The balance table's last week (20260904) is a month later than the salary/inflow table's (20260804).
- Line 16: "2025-11-15..18" is a range of four days; the other two are single days (2026-07-06 and 2026-08-07). Line 20 says the same 32 days are missing in raw, stg and prm; four plus two does not equal 32, so the 32 is read as the number of absent days in some wider range, not the three listed. Copied as printed; check the file for the full list.
- Line 19: "86 of 153 extract dates" is read as printed.
- The photo shows an office background behind the laptop; nothing to transcribe from it.
