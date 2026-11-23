# UC1 full transcript run: what to analyse when it lands

Prepared 2026-11-20. Nothing about UC1 is decided until this run (user). The sample results (logic doc
`uc1_stated_block.md` §13, §15, §16) give the hypotheses and the bars below; this run decides.

## 0. Intake (before any analysis)

**Delivery received 2026-11-23** (`workplace_mirror/bundle_helpers/uc1/uc1_signal_export_datasets.md`): six tables in
the shared store; official = `customer_signal_export` (primary: one row per CIF × signal at one `snapshot_date`,
time-weighted `estimated_value` with HIGH / MEDIUM / LOW confidence, `latest_value`, `average_value`, agent-remark
value, UC2-based `supporting_data`) and `proposer_level_observations` (evidence per customer-day, transcript and
remark, one partition per snapshot). New against bundle 26: agent remarks count, confidence exists, a dated evidence
table (point in time possible), bank corroboration built from our data (circular with A1). `simple_signal_aggregation`
and `signal_level_conflicts` were overwritten at the paths bundle 26 reads. Exploration / validation prompt:
`workplace_mirror/bundle_helpers/uc1/sonnet_uc1_full_data_prompt.md` (covers §0–§2b; Part 0 says whether it is the
full transcript run).
Quick coverage result and the interim approach: logic doc §17; the prompt's interim section applies until the refresh.

1. **Schema map.** Map the clean schema to bundle 26's four inputs (`metadata`, `extracted_signals`,
   `simple_signal_aggregation`, `signal_level_conflicts`): CIF key, conversation id and date, slot / level, detected
   vs published level, confidence. List what is new, renamed or gone. The next UC1 bundle carries the map plus the
   legacy-format drop (`cd698c8`).
2. **Shape checks.** Date range of calls; calls per month; share extracted; legacy rows; CIFs that match our obs
   base; 180+ customers present or not; one row per conversation (no duplicates across refreshes).
3. **Point in time.** When is each conversation available (extraction date vs call date) and what is the refresh
   cadence? A signal only counts at a month end if it was available before it.

## 1. Coverage and selection

- Account-months with a conversation / an extracted one in the 90 days before each month end, by model_id, DPD
  band, A1 state, A3 level (sample: cards 10–13%, loans 12–19% with a conversation; 3% / 5–8% extracted).
- Is the stored set still selected? Sample: DCORE promise events with a stored call paid 15% vs 41% without
  (cards). If the gap stays on the full run, results must be read within comparable groups (or weighted).
- 180+: coverage at all; A1 is ~85% Unknown there, so a fill would matter most there.

## 2. Decisions and their tests

Bar for any fill or flag (set 2026-11-19, logic doc §14): **≥ 5 pp paid difference or ≥ +0.02 AUC inside the
target state, in both products, n ≥ 100 per cell**. Outcomes: pay30 / pay45 (due and any) after the call; paid_due
1 and 3 months after the month end.

| # | Decision | Test | Ships if |
|---|---|---|---|
| D1 | Transcript promises as A3 promise events | rebuild A3 with unlogged transcript promises (call date = event day, A3's deadline and judging); level / state moves, moved rows' pay vs the level left / joined, state AUC with account bootstrap | state AUC up with an interval above 0 in both 61–180 books, moved rows pay like the level they join, and enough reach to matter (sample: 4 per 1,000 rows, AUC +0.001) |
| D2 | Flag: promise on the call, none logged on the CIF (±7 days) | pay vs no promise and vs matched promise, within A3 level | the bar |
| D3 | Flag: dispute stated, A3 dispute flag false | pay vs no stated dispute, within A3 level; loans have no dispute flag at all | the bar |
| D4 | Fill: stated ability inside A1 Unknown | able > partly > not stated > unable ordering, AUC inside Unknown, month-end view | the bar |
| D5 | Fill: stated intent / named amount or date inside A3 no_promise | the same inside no_promise | the bar |
| D6 | Discrepancy flags E1–E4, E7 (says able while A1 Low, says unable with CASA ≥ one due, job claims vs income) | pay vs concordant group | the bar (thin on the sample) |
| D7 | Treatment hints: reason, request, payment period | demand by A1 × A3; pay after each request type | descriptive, no bar |
| D8 | 180+ | Part A coverage, then D2–D5 if n allows | the bar |

## 2a. Logging gaps: re-assessed on the full data (user, 2026-11-20)

Whatever D1–D3 decide, re-measure the gaps between what customers say on calls and what DCORE records, and find
out whether they come from logging (agents) or from the data (DCORE feed / codes):

- **Unlogged promises.** Share of transcript promises (amount or date named) with no DCORE promise on the account /
  the CIF within ±3 and ±7 days (sample: 60% cards / 85% loans unlogged on the CIF within a week). Also the reverse:
  DCORE promises next to a call where no intent was stated.
- **Where the gap sits.** The same share by month, product, DPD band, call direction, campaign / queue, agent team
  (aggregated, no agent ids), call length, and by promise type (full / partial / with delay, amount vs date named).
  A gap spread evenly points to the feed; one concentrated in teams or queues points to logging practice.
- **Timing.** For promises that are logged: days between the call and the DCORE entry, and whether the logged date
  and amount match the stated ones.
- **Disputes.** Share of stated disputes with no A3 dispute flag at the next month end (account and CIF), by
  dispute type (system problem, amount, fraud, …); loans carry no dispute flag at all, so check the loan dispute
  codes in DCORE.
- **Requests.** Restructure, settlement and waiver requests stated on calls vs any matching DCORE record or
  restructure within 90 days.
- **Does it matter.** Payment of unlogged vs logged promises vs no promise, within A3 level.

Output: a short note for collections operations / DCORE with the rates, where they concentrate, and the likely
cause.

## 2b. Every sample statement is re-checked (user, 2026-11-20)

Each finding below was read on the sample and is re-tested on the full run; the result note says for each one
whether it holds, changes or fails.

| # | Sample statement | Re-test |
|---|---|---|
| S1 | UC1's counts, support and aggregation match our recomputation | recompute the customer-level levels from the per-conversation rows |
| S2 | Coverage 10–13% cards / 12–19% loans (any call, 90 days), 3% / 5–8% extracted; no 180+ | §1 |
| S3 | Stored calls are a selected group (DCORE promises with a call pay 15% vs 41% without, cards) | §1 selection check |
| S4 | 60% / 85% of transcript promises unlogged on the CIF within a week; unlogged ones pay more than no promise on loans | §2a, D2 |
| S5 | Stated disputes are almost never in A3's dispute flag; loans have no dispute flag | §2a, D3 |
| S6 | Specific statements go with payment (employed, salary-date period, amount or date named, restructure / settlement / waiver requests); card settlement requests the exception | Part B: each level vs not detected, overall and within A1 / A3 states |
| S7 | Inside A1 Unknown a stated reading pays about twice no reading; able > unable on cards | D4 |
| S8 | Able vs partly able and the intent levels barely separate | D4, D5 and Part B3 level orderings |
| S9 | Job and income claims only loosely match our income data, and the match does not change payment | Part C (claim × income class, payment by class), D6 |
| S10 | Transcript promises as A3 events move almost nothing | D1 |
| S11 | Calls at 61+ DPD are mostly extracted; the gap is calls at 1–60 DPD | §1 extraction by DPD at the call |

## 3. Prompts to reuse (git history)

- `sonnet_uc1_uc2_validation_prompt.md` (`3b53168^`): stated levels vs UC2 states and payment.
- `sonnet_uc1_signals_prompt.md` (`d553c62^`): Parts A–F plus the follow-up (CIF matching, promise source split,
  A3 what-if = D1).
- Merge them into one full-run prompt: all four model_ids, the new schema's column names, high-confidence-only
  versions of every table, and the selection check of §1.
