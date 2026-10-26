# Bureau v01 — PROD summary (cc_60_180; rl_60_180 corroborates), 2026-10-26

Part C of the bureau v01 prompt (removed once absorbed), written by the workplace Sonnet from
`tmp_validation/bureau_v01/results_{cc,rl}_60_180.json`. Transcribed from a photo by a chat
session (`pics/claude_code_handoff_3.md`), so single digits may be misread. Part A is in
`sonnet_bureau_v01_inventory.md`.

## Summary (Sonnet, verbatim)

# Bureau v01 — summary (cc_60_180; rl_60_180 corroborates)

Source: `results_cc_60_180.json` (n=2,860,075 `stg_aecb_alert` rows, w1-w7 OK, w8 N/A,
`feature_retail_loans` doesn't exist under CC, expected); `results_rl_60_180.json`
cross-checked for w5/w8 (w7 N/A there, `crx_cc_obs_base` is CC-only, expected).

**B0 REJECTED — one extract only.** `(ALERT_PROCESS_ID, edp_load_date)` = exactly 1,680
distinct = `n_distinct_extract_dt` (1,680): `ALERT_PROCESS_ID` is a per-pull **batch id**
(~1,702 rows/batch), not a per-alert id; `(ALERT_PROCESS_ID, ALERT_REC_ID)` never repeats
across a pull. Only the business key `(cif_id, CONTRACT_TYPE, ALERT_DESC)` recurs: 4,812
bounced runs repeat median 2 pulls/109 days, p90 4/272 days, **max 19 pulls/1,630 days**
(~85% of the 2022-2026 history). A bounce is re-sent, not a one-off notification.

**B1 CONFIRMED, stronger than stated.** Same run-length evidence. 61.2% of (key,extract)
appearances are repeats, not new. The max run (1,630d) spans almost the whole observed
history with no sign of aging out — "ages out of a window" may not apply at all.

**B2 REJECTED on the clause that matters.** `DT_OF_RETURN`: 0% null on bounced rows,
100% null on non-bounced — confirmed bounce marker. On/before `EXTRACT_DT`: 0% negative,
98.96% within 0-30 days, median lag 2 days — confirmed. "Constant while the bounce
repeats": **rejected** — only **0.35%** of the 4,812 repeat runs hold it constant; it
moves with `EXTRACT_DT` on 99.65% of repeats (RL: 0.77%, same pattern). It re-dates
itself every pull — "most recently registered as of this pull," not the bounce date.
`CONTRACT_STATUS_DT` is 100% null on bounced rows — unrelated, ruled out.
**B3 CONFIRMED as the right model.** The one real bounce type (`ALERT_DESC`="New
Bounced Cheque", 31,352/32,988 bounced rows): 37.6% of its repeats are same-amount.
Transitions split cleanly: same_amount 0.49% (of all non-first transitions), rise
0.44%, fall 0.37% — a repeated amount is one continuing event, a rise is a new one.

**B4 REJECTED — not monthly.** Per-CIF gaps between extracts: 34.78% at 1-7 days,
33.36% at 8-27 days (**68.1% sub-monthly**) vs 12.43% in the 28-35-day monthly band,
19.4% longer. Book-wide loads are near-daily (1,680 `EXTRACT_DT` over ~1,700 days,
matching `bureau_partitions.md`'s 1,540 daily partitions); per-CIF pulls ride on top
irregularly — event/on-demand-shaped, not monthly-batch-shaped.

**Best dating column/derivation.** Neither raw column alone — `EXTRACT_DT` dates the
pull and restates a stale bounce for years; `DT_OF_RETURN` is close (median 2 days
before `EXTRACT_DT`) but re-dates itself every pull, so it doesn't fix staleness
either. What works: **dedup by `(cif_id, CONTRACT_TYPE, ALERT_DESC)`, take the first
`EXTRACT_DT` of each same/rising-amount run** (B3's rule). w7, CC obs base, last 6
months (n=99,687): `extract_date` flags 3,592 rows; `DT_OF_RETURN` flags 3,810 (a
~2-3 day shift, 408 reclassified, no staleness fix); **first-of-run flags 2,766 —
826 fewer (23% of 3,592)**, i.e. a quarter of today's "bounce in the last 3 months"
flags are stale restatements, not new events.

**Defect found (R19, not fixed).** `feature_retail_loans.aecb_direct_debit_returns_6m`
(declared in `feat_loan_application_risk.py`, traced in `inventory.md` A.4) is **NOT
FOUND** on the real `rl_60_180` table (w8). `aecb_bureau_pull_date` is present and
behaves as documented (1 distinct pull date/account, p50=p90=max=1).


## Review

- **What a bureau alert row is.** A pull re-sends every open bounce: a bounce repeats for a
  median of 2 pulls / 109 days and up to 19 pulls / 1,630 days. Dating by `extract_date` (today)
  therefore keeps old bounces alive; `DT_OF_RETURN` re-dates itself with every pull (constant on
  only 0.35% of runs), so it is no fix either. O58 is closed: exposing `DT_OF_RETURN` would not help.
- **Proposed dating: first report of each bounce.** Key `(cif_id, CONTRACT_TYPE, ALERT_DESC)`;
  a bounce event is dated by the key's first bounced extract, and again whenever the amount
  rises; a repeated amount is the same bounce. On the CC obs base (latest 6 months) this cuts
  the bureau-flagged rows from 3,592 to 2,766 (−23%): a quarter of today's bureau distress
  is a stale restatement.
- **B3 is the best available model, not a clean split.** Same / rise / fall are each under 0.5%
  of all transitions and only 37.6% of repeats keep the amount, so most repeats change amount.
  The rule for a *falling* amount (a part repayment?) and for a bounce that clears and comes back
  decides how many of those are new events.
- **Pulls are near-daily for the book and irregular per customer** (68% of per-CIF gaps under
  a month), so a key missing from one pull is not a clearance.
- **Where it goes.** A primary `prm_bureau_bounce_events` (one row per bounce event, built from
  `stg_aecb_alert` with the run rule; carries the key, first extract date, amount) and the
  monthly feature on top of it — in the CC finish bundle, which already touches the bureau
  primaries (R5 photos). It changes A1 states, so that bundle's check expects changes on bureau
  distress rows only.
- **Not used by A1:** `feature_retail_loans.aecb_direct_debit_returns_6m` is declared but
  missing from the PROD table (O60). `aecb_bureau_pull_date` has one pull per account, as the
  user said (RL salary dating, DESIGN_REVIEW).
