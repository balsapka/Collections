# UC1 stated block: how the UC1 signals are condensed (as built, bundle 26)

How bundle 26 (`crx_<p>_uc1_stated`) turns UC1's call-transcript signals into two stated states and
a few flags, which signals it keeps and leaves out, how it sits beside A1–A4, what the first PROD run
showed (§11) and how the integration with the UC2 states should progress (§12). As of 2026-11-18.

Code: `workplace_mirror/src/enbd_collections/pipelines/crx_persona/uc1_stated/` (`signals.py`,
`classify.py`), spec test `workplace_mirror/checks/uc1_stated_spec.py`. Data facts:
`reference/uc1_data_kb.md`, `workplace_mirror/bundle_helpers/uc1/uc1_timelines_handoff.md` and its
review (decisions D1–D5). The earlier design note `uc1_integration_proposal.md` was written before
the handoff and assumed a delivery table with confidence; where the two differ, this file is the
built logic.

## 1. Principles (user decisions, 2026-11-16 / 17)

- **A1–A4 are fixed.** UC1 does not change their rules or states for now.
- **UC1 is condensed into its own block** beside them: A5 stated ability, A6 stated intent, plus
  open-issue flags.
- **UC1's outputs are taken as they are.** Extraction, conflict resolution and the handling of a
  customer's signals over time belong to the UC1 team. We map and count; we never re-parse or
  re-resolve.

The block therefore has very little logic of its own: tell "silent" from "never heard", map
levels to states, count the calls behind each level, choose which signals to keep.

## 2. What UC1 delivers today

Per conversation, the LLM detects up to 8 signals over 22 slots:

| Signal | Levels |
|---|---|
| `payment_capacity` | none / partial / full |
| `payment_intent` | no_payment / with_delay / partial / payback_full |
| `delinquency_reason` | lost_employment / reduced_employment / has_employment / increased_obligations |
| `payment_period` | weeks / salary_cycle_dependent / months_or_longer |
| `dispute` | system_problem / customer_scammed / other |
| `request` | detected |
| `fraudulent_customer` | detected |
| `repayment_specifics` | amount_mentioned / date_specific / plan_structure_mentioned (with the value named) |

Tables read (shared store copy, read only):

| Table | Grain | Used for |
|---|---|---|
| `timelines/simple_signal_aggregation` | one row per `cif_id` | **the states**: per signal the modal level over all the customer's extracted conversations, ties to the latest; no date, confidence, count or request type |
| `timelines/signal_level_conflicts` | conversation × slot, detected / not-detected | counting support only |
| `metadata` | every conversation, with date and `cif_id` | evidence status, dates |
| `extracted_signals` | extraction ledger (`model_version` only) | extracted or not, current vs legacy format |

## 3. Step 1: evidence status (silent vs never heard)

"Signal not detected" means something only when an extracted conversation exists. Reach is low
(cc_60_180, 2026-08: 69% no conversation, 25% not extracted, 3.6% with a capacity level), so every
row first gets `uc1_evidence`, counting conversations strictly before the observation date:

| `uc1_evidence` | Meaning |
|---|---|
| `no_cif` | no customer id to join on |
| `no_conversation` | no conversation before the observation date |
| `not_extracted` | conversations exist, none extracted by UC1 |
| `extracted` | at least one extracted conversation: the only case with states |

Legacy-format extractions are not used at all (user, 2026-11-18): a conversation extracted only in
the legacy format is dropped, as if it did not exist (UC1's customer table reads no level from it).
Bundle 26 still had a `legacy_only` status (21–82 rows per model_id); the change is coded
(`cd698c8`) and ships with the next UC1 bundle.

## 4. Step 2: levels → states

**A5 stated ability**, from `payment_capacity`: full → `able`, partial → `partly_able`, none →
`unable`.

**A6 stated intent**, from `payment_intent` (D3, four levels collapsed to three): payback_full →
`pays_in_full`, partial / with_delay → `partly_or_later`, no_payment → `refuses`. The raw level is
kept in `a6_intent_level`.

Both axes: evidence `extracted` but the signal not detected → `not_stated`; any other evidence →
`no_evidence`. Keeping the two apart matters: a customer who talked and never mentioned capacity is
not the same as one we never heard.

An unknown level in UC1's table stops the run (a schema change on their side, to be looked at, not
guessed).

## 5. Step 3: support

UC1's modal level carries no count, so one call and twelve calls look alike. From the per-call grid
(conversations before the observation date):

- `a5_conversations_n` / `a6_conversations_n`: conversations that detected any capacity / intent
  level;
- `a5_agree_n` / `a6_agree_n`: of those, how many detected the level UC1 published.

E.g. 2 capacity conversations with 1 agreeing = a split history. We count; we do not override
UC1's choice.

## 6. Signals kept as details and flags

| Source | Column | Why |
|---|---|---|
| `delinquency_reason` | `a5_reason` | explains A5 (lost job vs employed) |
| `payment_period` | `a6_period` | how long the customer says they need; qualifies A6 |
| `repayment_specifics` amount / date | `a6_amount_named_flag`, `a6_date_named_flag` | a named amount or date makes stated intent concrete |
| `dispute` | `stated_dispute` (level or `none`) | an open issue changes the treatment before ability / intent |
| `request` | `stated_request_flag` (D4) | customer asked for relief; UC1 publishes no request type |
| ledger + metadata | `uc1_conversations_n`, `uc1_extracted_n`, `uc1_last_conversation_date`, `uc1_last_extracted_date` | amount and recency of evidence |
| metadata | `uc1_after_obs_flag` | 1 = the published level may rest on a conversation on or after the observation date |

## 7. Left out, and why

| Left out | Why |
|---|---|
| `fraudulent_customer` | 0 detections in transcript rows (user, 2026-11-17: leave out; add as a pass-through if UC1 starts detecting it) |
| `plan_structure_mentioned` | mostly fires alongside period or request; little on top |
| the amounts and dates named | free text; using the values means parsing their output |
| confidence (high / low) | not in their customer table; rebuilding it from per-call rows = our own conflict rule |
| agent remarks | UC1's customer table ignores them |
| legacy-format extractions | dropped with their conversations (user, 2026-11-18) |
| `latest_flags`, `time_weighted_*` | per conversation / never run |
| UC1's prior-PTP features (`ptp_30d_*`) | promises are A3's, from our own data |
| `notes` free text | not a signal |

## 8. Time: latest month only (D1)

The customer table has no date: it is the modal level over all history, including conversations
after any past month. Past months cannot be rebuilt point in time, so only the month of
`persona_end_date` is scored and earlier months are NULL. Even in the latest month a level may lean
on a later conversation; `uc1_after_obs_flag` marks those rows.

## 9. Place in the framework (today)

```
A1 ability      (observed)   ←→  A5 stated ability   (what the customer said)
A2 locatability (observed)
A3 credibility  (observed)   ←→  A6 stated intent    (what the customer said)
A4 deterioration(observed)
                                 + dispute / request flags, evidence status, support
```

- Separate output, outside the persona key. Reasons: single-digit reach, no ground truth, 43% of
  capacity detections low confidence (KB, sample), and another team's evolving method.
- Read side by side: the interesting cells are disagreements ("A1 unable, A5 able"; "A3 low, A6
  pays in full") and agreements that strengthen a state.
- UC1 can only ever cover customers reached by phone (A2 `reachable`); the unreached never get a
  stated state. A4 and the observed axes are not a stopgap.

## 10. When the full UC1 delivery lands: what to think through

Final personas are defined by the UC2 states (A1–A4) and the UC1 states combined, and tiers are
assigned on that combination. Nothing below is decided; it is the agenda.

### 10.1 What is expected from UC1, and what it changes in the block

| Expected | Mechanical change in the block |
|---|---|
| dated / time-weighted customer table (their Phase 3.3; recency windows set in a business workshop) | past months buildable point in time; `uc1_after_obs_flag` goes away; the backtest in 10.3 becomes possible |
| confidence per level | support becomes confidence-aware (strong / weak) instead of call counts only |
| `request_type` | `stated_request_flag` splits by type (plan, waiver, deferral, …) |
| delivery-table persona / `collection_action` value sets (due 2026-12-11) | decide whether we read their persona fields or keep mapping raw levels |
| remarks vs transcripts precedence (their Phase 2.2) | possibly more customers reach `extracted` |
| full coverage beyond the 8% purposive sample | real reach per model_id; decides whether UC1 can sit in the key at all |

### 10.2 How to combine UC1 with A1–A4 (options, not choices)

1. **Overlay.** A1–A4 stay the persona; A5 / A6 / flags modify the treatment inside a tier
   (agree → reinforce; conflict → review or a softer action; dispute → resolve first). Least
   disruption; works when most rows have no UC1.
2. **Fill.** Stated evidence fills an observed Unknown only (e.g. A1 Unknown + A5 able). Raises
   coverage where it is weakest, but mixes said and observed in one state.
3. **Joint axis.** Observed and stated merged into one ability and one willingness state with an
   explicit agreement rule. Cleanest persona, hardest to validate, and the most dependent on UC1's
   coverage and stability.
4. **Separate key dimension.** A stated dimension in the persona key. Only sensible if reach
   becomes large; otherwise it splits every persona on a mostly empty column.

The parked ideas for feeding the axes (A6 plan as an A3 promise event, A6 refuses beside A3's
refusal rule, A5 for A1 Unknown, `stated_dispute` for A3's dispute column, a Genesys conversation
as an A2 contact) are listed in `uc1_integration_proposal.md` §10.

### 10.3 Questions to answer with data before choosing

- **Does stated add information beyond observed?** Outcomes (cure, payment, roll) by observed ×
  stated cells, e.g. within A1 Moderate, do A5 able and A5 unable cure differently? Needs the dated
  table, otherwise the stated level leaks the future.
- **Agreement rate** between A1 and A5, and between A3 and A6, among `extracted` customers.
- **Who is covered**: UC1 reach by A2 / A4 state and by bucket; selection bias of who gets called
  and extracted.
- **Stability**: how often a customer's stated level changes month to month once dated.
- **Circularity**: UC1's corroboration check reads our A1 state, so A1–A5 agreement is partly built
  in; validate against outcomes, not against each other.

### 10.4 Tiers

- GRR owns the collection strategy and the tier assignment; we deliver the states and the evidence
  for each combination.
- The full persona is kept; the tier-stability work is parked, with G3 (pooled 6-month FRN, capped)
  as the tested candidate if it reopens.
- Whatever combination is chosen must give every customer a tier with UC1 missing (most of the
  book), so tiers are anchored on A1–A4 and UC1 can at most move a customer within or one step
  across tiers, or that has to be an explicit decision.
- GRR deck framing applies: the goal is allocation before the collector, and at 180+ finding the
  5–10% with positive signals, where a stated able / pays-in-full could be one of those signals.

## 11. First PROD run (bundle 26, 2026-08-31, all four model_ids)

Summary: `workplace_mirror/bundle_helpers/b26_uc1/b26_run_summary.md`. All checks pass.

| model_id | accounts | extracted | not_extracted | no conversation | A5 stated (able / partly / unable) | A6 stated (full / partly-later / refuses) |
|---|---|---|---|---|---|---|
| cc_60_180 | 19,292 | 991 (5.1%) | 25.1% | 69.4% | 690: 18% / 61% / 21% | 772: 25% / 70% / 5% |
| rl_60_180 | 3,985 | 364 (9.1%) | 18.9% | 71.3% | 239: 14% / 65% / 21% | 290: 26% / 72% / 2% |
| cc_180_plus | 318,663 | 184 (0.1%) | 0.1% | 99.8% | 98 | 118 |
| rl_180_plus | 55,371 | 145 (0.3%) | 0.3% | 99.4% | 76 | 85 |

What it says:

- **60–180 only.** About 30% of 60–180 accounts have had a call in the transcript window; at 180+
  under 1%. UC1 is a 60–180 instrument.
- **Projected reach after the full run** (if the extracted sample is representative, see below):
  roughly 30% have a conversation × 70% state capacity ≈ **21% of cc_60_180 accounts with an A5
  state, ≈ 24% with an A6 state** (rl ≈ 18% / 22%).
- **The middle dominates.** 61–65% of stated ability is partly_able, 70–72% of stated intent is
  partly_or_later: what most delinquent customers say. The decision value sits in the tails
  (able / pays in full, unable / refuses), about 30–40% of stated rows, so after the full run only
  ≈ 8% of 60–180 accounts would carry a tail stated signal.
- **`not_stated` is large** (30% of extracted on A5, 22% on A6): the customer talked but said
  nothing on the topic. Whether that predicts anything is open (validation Part A7).
- **Every signal is old at the latest month.** Calls in the store end 2026-07-16, so at 2026-08-31
  the newest signal is 46 days old and most are 2–6 months old (the KB measured 0.2% of rows with a
  call in the last 30 days, 1.4% in 90, 2.2% in 180).
- **Reach crosses A2's Non-Reachable** (KB, sample): 42% of rows with a usable call are A2
  Non-Reachable, because A2 reads DCORE contact outcomes and the transcripts come from Genesys.
  Either the call predates the failed-call streak (a stale signal), or A2 misses real contacts.
- **Sampling.** The current extractions were drawn by stratified sampling on the 60–180 population
  (user, 2026-11-18), so the 60–180 distributions are taken as broadly representative. One caution
  from the KB: extraction rates differed by prior promise history (7.4% vs 2.3%), repayment
  behaviour (11.9% vs 4.0%) and call month (July 22%, March–May ~3%), so customers with a promise
  history may be over-represented; validation Part C measures whether a reweighting changes
  anything.

## 12. Assessment: how the final personas will turn out, and what to do differently

### 12.1 What the final persona will look like

- **The persona key stays UC2 (A1–A4) for everyone.** UC1 can at best describe about a fifth to a
  quarter of 60–180 accounts and almost none at 180+. A key that needs UC1 would be empty for most
  of the book, and at 180+ for nearly all of it.
- **UC1 becomes an overlay at 60–180**, not a fifth or sixth key axis: per ability and intent pair,
  stated *confirms* / *contradicts* / *silent* (not stated or no evidence), plus the open-issue
  flags (dispute, request). Tiers come from UC2. Whether UC1 may move a customer within or across a
  tier is decided from the validation (B4), and only for the tails.
- **At 180+ the persona is UC2 only.** Finding the 5–10% with positive signals there stays an
  observed-data job (A1 / A3 / A4); UC1 is not part of the 180+ design unless the transcript feed
  starts covering those customers.

Proposed (Claude, for the user to confirm): this drops options 3 and 4 of §10.2 (joint axis, key
dimension) as the working assumption, and narrows option 2 (fill) to a question for the validation: does a stated level help where A1 or A3
is Unknown?

### 12.2 What to do differently

1. **Validate at conversation level, point in time, not on the customer table.** UC1's customer
   table is undated (modal level over all history), so it cannot be backtested. The per-conversation
   grid plus the call dates can: at month ends 2026-03..07, the level of the latest conversation
   before the month end, its age, and the payment that followed. That is our validation; it changes
   neither UC1's rule nor our production block. Prompt:
   `workplace_mirror/bundle_helpers/uc1/sonnet_uc1_uc2_validation_prompt.md` (Parts A–C).
2. **Measure decay and hand it over as evidence.** Paid rate by stated level × signal age (B3)
   shows how fast a statement loses value. That is the input UC1's recency workshop needs; it stays
   their decision.
3. **Judge UC1 by what it adds to UC2, not on its own.** The test is whether a stated level
   separates payers *within* an A1 or A3 state (B2, B4). A signal that only repeats A1 / A3 adds
   nothing to the persona, however plausible it reads.
4. **Watch the A2 seam.** If many UC1 conversations come after A2's failed-call streak started
   (A6), A2 Non-Reachable is overstated and a Genesys conversation should count as contact (parked
   idea, §10.2). A2 is accepted by GRR, so that would go to the user / GRR as a decision, not into a
   UC1 bundle.
5. **Make freshness a production requirement.** The block is only useful if the transcript store and
   UC1 extraction are refreshed before each scoring month; today the store ends 2026-07-16. Ask
   (a request, not a change to their work) for the refresh cadence and the full-run date. The
   25% `not_extracted` share at cc_60_180 is the largest coverage lever.
6. **Keep the block thin until the validation is back.** No new states or rules in the stated block;
   the legacy removal is the only pending change and can ride with whatever the validation asks for.

### 12.3 Decision points after the validation

| Result | Then |
|---|---|
| B4: stated level adds AUC inside A1 / A3 | define the overlay (confirms / contradicts / silent) and a GRR rule for tails |
| B4: adds nothing | keep the block as display only (collector context); no tier effect |
| B3: value drops fast with age | overlay counts only signals younger than the cut-off; tell UC1 |
| A6: calls after the failed streak | raise the Genesys-as-contact question for A2 with the user / GRR |
| C: reweighting changes the paid rates | report reweighted numbers until the full run |
| Fill (A1 / A3 Unknown) adds | candidate rule for A1 Unknown customers, for the user to decide |

## 13. Validation result (2026-11-19) and what to expect from the full transcript run

Source: `workplace_mirror/bundle_helpers/uc1/uc1_uc2_validation_summary.md` (60-180 only; 180+ not covered by the
sample). Calls in the store run 2026-03-06..2026-07-16 and ramp up (cc month ends with a conversation: 70 in Mar,
4,834 in Jul); UC1 extracted only a sample of them.

**Read as:** UC1 levels are what the customer *said* on the call, picked out of the transcript, not facts. Whether
they are true is a separate question; the only test we can run is whether what they say lines up with what they do
(paid_due) and with the observed UC2 states. All numbers below are that test.

**On the sample:** no defect in UC1 inputs or bundle 26. Stated levels order sensibly overall (cc able 22% /
partly 19% / unable 14% paid_due) but add almost nothing inside an A1 or A3 state: AUC gain on rows with a reading
+0.00 to +0.02, on all rows +0.001 to +0.008. No decay with age is visible (weak test). L and M readings agree ~95%.
What does separate payers is *having a conversation at all*: inside A3 Low, cc pays 7.0% with an extracted
conversation vs 3.2% with none (rl 22.3% vs 9.7%). That is a contact effect, not the stated level.

**Extrapolation to the full run** (all conversations extracted, July as the reference month):

| | cc_60_180 | rl_60_180 |
|---|---|---|
| accounts with an extracted conversation now | 879 / 18,397 (5%) | 369 / 3,728 (10%) |
| expected after the full run (all conversations) | ~4,800 (~26%) | ~960 (~26%) |
| of which a stated level (not `not_stated`, ~70%) | ~18% of accounts | ~18% of accounts |
| expected AUC gain, all rows (within-reading gain × coverage, upper end) | ≤ +0.01 | ≤ +0.02 |

- The not-yet-extracted conversations pay less (cc 11.9% vs 16.9%) and are less often Reachable; reweighting moved
  level rates by ≤ 2 pp and kept their order, so the level pattern should hold, slightly lower.
- Coverage, not signal strength, is what grows. A within-state gain of ~0.01 stays ~0.01 per reading; spread over a
  quarter of accounts it is still below what would justify a tier rule.
- Freshness: at scoring (month end) the newest reading was 1-6 months old because the store stops mid-July. A
  refreshed store gives fresh readings, which could matter more than coverage, but the sample showed no decay, so
  expect a modest gain at best.
- 180+: still no coverage expected; persona stays UC2 only.

**Correction (2026-11-19, same day):** the "adds nothing" read above came from pooling all A1 / A3 states. Inside the
states where UC2 has no evidence the stated level does separate payers: cc A1 Unknown able 21.4% (84) / partly 17.0%
(264) / not stated 15.6% (256) / unable 12.0% (100) vs no reading 8.2%; cc A3 Low partly_or_later 9.5% (274) vs not
stated 4.3% (235) vs no reading 3.4% (z ≈ 2.3). Small cells and repeated account-months, so directional, but it is the
pattern a fill would need. Also untested so far: reason, period, repayment specifics, request, dispute; outcomes
aligned to the statement (with_delay / partial pay late or below the due, the 1-month paid_due misses them);
high-confidence detections only (43% of capacity detections are low confidence); consistency with observed data.
Prompt: `sonnet_uc1_signals_prompt.md` (run 2026-11-19 / 20, removed; last version in git `d7ef094`, reuse it for the
full-run retest).

## 14. Integration design (proposed, Claude, 2026-11-19; settle after the signals prompt)

UC2 measures what customers do, UC1 what they say. They answer different questions, so UC1 is not judged only by
whether it out-ranks UC2. Four jobs, each with its own test:

| Job | What UC1 gives | Test (signals prompt) | Where it lands |
|---|---|---|---|
| **Fill** where UC2 is blind | stated ability inside A1 Unknown (57% of cc_60_180 rows), stated intent / transcript promises inside A3 no_promise | D1–D3, E5 | sub-split of A1 Unknown and A3 no_promise in the tiering; `a1_state` / `a3_state` themselves unchanged (A1–A4 stay fixed) |
| **Cross-check** | stated vs observed: says employed but salary stopped with us (salary may have moved to another bank), says job lost but income continues, says unable but holds ≥ one due in CASA, promise on the call but none logged in DCORE | C, E | discrepancy flags for the collector ("verify"); E5 also tells A3 / DCORE whether promises go unlogged |
| **Treat** | reason, request (restructure 990, settlement 570, waiver 506, deferral 481 on the sample), payment period (salary cycle), dispute (system_problem 1,413) | B, F | treatment hints next to the tier: offer type, call timing, dispute routing; demand sizing for GRR's programmes; feeds UC1's `collection_action` (value sets due Dec 11) |
| **Context** | last stated stance and call date for Non-Reachable customers (they talked, then went silent: A6.2) | (first validation) | collector view only |

- The persona key stays A1–A4; UC2 sets priority and tier, UC1 adds fill, flags and the treatment hint.
- Having a genuine conversation is itself a strong signal (cc A3 Low 7.0% with an extracted conversation vs 3.2% with
  none). It needs only call metadata, so it covers every call today; it belongs to the parked Genesys-as-contact
  question for A2 / A3 (user / GRR), not to UC1's extraction.
- Do not force it: a fill or a flag ships only if it holds on the full run (bar: ≥ 5 pp paid difference or ≥ +0.02 AUC
  inside the target state, in both products, n ≥ 100 per cell); the treatment and context jobs need no AUC bar.
- 180+: depends on whether 180+ customers have calls at all (A3); A1 is 85% Unknown there, so a fill would matter most
  there if they do.

## 15. Signals test result (2026-11-19, 60-180 only)

Source: `workplace_mirror/bundle_helpers/uc1/uc1_signals_summary.md`. 180+ not run yet. Call-anchored sample is small:
643 card pairs (333 accounts), 358 loan pairs (148 accounts), because most extracted calls reached customers before
they were at 61+ DPD. Read as direction unless stated.

**Coverage, revised.** Account-months with any conversation in the 90 days before the month end: cards 10–13%, loans
12–19% (June–July); with an extracted one: cards ~3%, loans 5–8%. A full run therefore reaches ~10–13% / 12–19% of
61–180 account-months, not the ~26% estimated in §13 (that counted any earlier conversation, not the last 90 days).
Extraction is already 50–78% for calls made at 61+ DPD; the gap is the calls made at 1–60 DPD.

**What holds:**
- **Transcript promises go unlogged.** 79% of card and 91% of loan transcript promises have no DCORE promise on the
  account within ±3 days. Those customers pay more than customers with no promise at all (30-day paid a due: loans
  48.5% vs 29.4%; cards 17.9% vs 13.6%). This is evidence A3 does not see today. To check first: a DCORE promise on
  another account of the same CIF (UC1 is CIF-level, DCORE per account).
- **Stated disputes are not in A3's dispute flag.** Almost every stated dispute (cards 72 pairs, loans 37) has the A3
  flag false; card disputes (mostly system problems) pay less (19.4% vs 31.4% paid a due at the next month end).
- **Specific statements go with payment, both products:** says employed (loans 55.8% vs 33.5% for no reason given;
  cards 23.9% vs 15.4%), a named salary-cycle period, a named amount or date (loans), restructure / settlement /
  waiver requests (loans 52–65%). Card settlement requests are the exception (13.2%).
- **A1 Unknown, month-end view:** stated readings pay about twice no reading (cards 13–22% vs 7.8%, loans 26–29% vs
  16%); cards able 22.2% > partly 16.6% / not stated 17.6% > unable 12.8%. Call-anchored AUC inside Unknown only 0.51–0.57.

**What does not hold (yet):** able vs partly vs full and the intent levels look alike; job / income claims are only
loosely consistent with our income data (loans lost_employment: 45% income stopped, 37% never visible; cards
has_employment: 56% income continues, 22% stopped) and consistency does not change payment in a stable direction;
the discrepancy flags E1–E4 and E7 are too thin; F3 (restructure after a request) is blocked by restructure data
ending 2026-05-31.

**Effect on §14:** fill inside A1 Unknown stays a candidate, below the n bar. Cross-check gains two concrete gaps for
A3 (unlogged promises, unlogged disputes): the strongest case for using transcripts, subject to the CIF check.
Treatment hints hold (specific content, requests). Next: 180+ Part A, and E5 / E6 at CIF level.

## 16. Follow-up result (2026-11-20, 60-180 only): CIF matching, transcript promises as A3 events

Source: `workplace_mirror/bundle_helpers/uc1/uc1_signals_followup_summary.md`. 180+ not run: 180+ customers are not in
the UC1 sample yet. The what-if rebuild reproduces the persisted A3 exactly (0 differences), so its numbers hold.

- **Unlogged promises are real, not a CIF artefact.** Looking at every account of the CIF within ±7 days, 60% of card
  and 85% of loan transcript promises still have no DCORE promise. Loans: those customers pay 48% within 30 days vs
  30–34% with no promise at all; cards: 18–21% vs 17–18% (not adjusted for state). Where a DCORE promise does sit
  next to the call, it pays no better.
- **Stated disputes stay outside A3's flag at CIF level too**; loans carry no dispute flag at all.
- **DCORE promises with a call in the store pay far less than those without** (cards 14.6% vs 41.2%), inside every
  promise source and follow-up code. The calls in the store are a selected group (harder customers); the sampling
  rule is unknown, which is why we ask UC1 for it.
- **As A3 promise events they change nothing today.** Adding the unlogged transcript promises as events moves
  Dimension A on 42 card and 64 loan account-months (≈ 5 per 10,000 / 4 per 1,000) and the state AUC by at most
  +0.001 (loans, interval touching 0). They would be 0.8% / 3.0% of A3's promise events, 2.1% / 4.2% if every call in
  the store were extracted. The moved loan rows pay above both neighbouring levels (n 17–26, a selected group).

**§14 provisional reading (2026-11-20); nothing is locked or built until the full transcript run (user).** Not into
A3 on today's sample: too few events to move the state. Cross-check: "promise on the
call, none logged" and "dispute stated, not flagged" are candidates for stated-block flags for the collector and as a
data-quality finding for collections operations / DCORE. Treat and context as in §14. Fill inside A1 Unknown stays
a candidate. All re-tested on the full transcript run with the §14 bars, where reach may be much larger: the store
holds a call for only ~6% of DCORE promise events today, so "every call extracted" here still undercounts a full run.

## 17. Signal export, quick coverage check (2026-11-23, 60-180 only)

Source: `workplace_mirror/bundle_helpers/uc1/uc1_coverage_summary.md` (prompt removed; last version in git `47e3af1`).
The delivered export still covers only about 10k conversations; a refresh is due.

- **Size.** 5,038 CIFs, 11,043 customer-days; transcript observations dated 2026-03 .. 07 only (none in August),
  remarks earlier and later. 28,022 conversations of these CIFs are in the metadata. The export (latest snapshot
  2026-10-31) has the same CIFs as the 08-31 evidence: no growth after July.
- **Who.** 30% of the CIFs are in the cc 60-180 base, 10% in rl; at least 60% in neither (mostly card holders,
  about 40% of them delinquent outside 60-180). No product is strongly selected.
- **Coverage.** Aug-end 5.5% of cc / 8.5% of rl account-months; pooled Jan-Aug 2.6% / 5.7%. Projection if every
  stored call were extracted: 13% / 16%. **Read against the reachable pool** (user, 2026-11-23): only about
  20% of the book is A2 reachable (August) and a transcript needs a conversation, so ~20% is the realistic
  ceiling; a full extraction would reach about two thirds of it on cards and four fifths on loans. Covered
  customers being reachable is the design, not a bias; selection is judged within reachable.
- **Quality.** Every capacity / intent estimate is LOW confidence (HIGH only for request); no repayment rows in
  the evidence and none usable in the export.
- **Personas.** 0 of 660 cc / 470 rl personas reach 100 covered account-months; after a full extraction 43 cc
  personas (46% of the book) and 2 rl. Persona-level calls are out of reach; single-state fills are not.
- **Selection.** Covered customers are reachable, in-country, early DPD, fewer no_promise / Low / Unknown, and pay
  more (cc +5.6 pp, rl +10.1 pp; inside A1 Unknown 17.2% vs 8.7% cc).
- **Readiness against the bar (both products, n ≥ 100).** A1 Unknown fill: cc cells ≥ 100, rl 61–142: not yet.
  Unlogged-promise flag: n ≥ 100 in both (intent only, an upper bound: 81% / 87% unmatched). A3 no_promise fill,
  dispute flag, treatment by A1 × A3: wait.

**How we use it now (Claude, 2026-11-23).** The export is timeless, flat in confidence and without repayment data, so
the interim analysis reads the dated evidence table with our own point-in-time reading (latest transcript level in
the 90 days before the month end, with a modal and a support-count variant), month ends 2026-04 .. 07 pooled and
July as the headline month (freshest with an outcome; Aug-end has neither new calls nor an outcome). Fills and flags
are judged inside the covered group and within A3 level × DPD band (the selection does not bias a rule that only
applies to covered customers, but the covered mix will change after a full extraction); covered vs not is used only
to size the contact effect within A1 × A3 × DPD cells. Same code reruns on the refresh. Prompt: interim section of
`workplace_mirror/bundle_helpers/uc1/sonnet_uc1_full_data_prompt.md`. Nothing is decided until the refresh. The interim run is best effort (user, 2026-11-23): no n ≥ 100 gate; every test is read as
direction and size with bootstrap intervals and n, cards and loans also pooled where small. The §14 bar applies to
the final decision on the refreshed data.

## 18. Interim exploration on the current export (2026-11-23, 60-180 only)

Source: `workplace_mirror/bundle_helpers/uc1/uc1_full_interim_summary.md` (prompt `sonnet_uc1_full_data_prompt.md` +
its interim section, kept for the rerun on the refresh). Best effort: strength = strong (interval excludes 0 and
≥ 5 pp / +0.02 AUC), suggestive, no signal. Covered group only, month ends 2026-04 .. 07.

**What the delivery is.** Not the full run: 16% of cards' and 35% of loans' calls are extracted, and the call store
itself ends 2026-07-16 (no later calls to extract). UC1's settings (half-life 30 days, remark weight 3.0) differ from their
description; taken as generated. Bundle 26 does not break (columns and levels unchanged; A5 / A6 agree
89-95% with the persisted block). Point in time works from the dated evidence (08-31 and 10-31 partitions identical
up to July; 09-30 is a smaller cut, not to be used), not from the export.

**Remarks are DCORE notes.** 92% of card remark days have a DCORE follow-up the same day; remark intent agrees with the
transcript on only 36-39% of days, and remark-only readings order payers weakly (cards) or not at all (loans).
Remarks are our own data re-read, not independent evidence, and the export weighs them as much as transcripts.

**Reading rule.** `latest` transcript level within 90 days is as good as modal or 180-day rules; no fade with age
inside 90 days; `support ≥ 2` helps only loan intent (a strength flag, not a requirement). Capacity AUC ~0.57,
intent 0.55 (cards) / 0.58 (loans) among covered customers: stated levels are weak on their own.

**Selection and contact.** Cards: covered reachable customers pay 7 pp less than uncovered reachable ones, in every A3
level, and having a call lowers payment by 11 pp standardised: extracted calls go to harder customers. Loans: no
difference. The earlier "a conversation is a positive signal" (§13, §14) was the reachable-vs-not effect A2 already
holds; it does not survive inside reachable.

**Decisions, best current reading:**

| # | Reading | Strength |
|---|---|---|
| D1 transcript promises as A3 events | 0.2 / 2.5 state changes per 1,000 rows, AUC ±0.000 | no signal: drop |
| D2 unlogged promise | loans +13 pp over no promise (+31 inside A3 promised, n 81); cards +3.5; unlogged never pay less than logged | loans suggestive, cards none |
| D3 unflagged dispute | 99.9% of stated disputes unflagged, but no payment difference | no signal (ops note only) |
| D4 A1 Unknown fill | able 23.5 / partly 17.7 / not stated 23.9 / unable 12.3% (cards), AUC 0.53; only "unable" stands out | suggestive (weak); the 2× "reading vs none" ratio mixes in reachability |
| D5 A3 no_promise fill | loans: pays in full 34% / partly 18% / refuses <10, AUC 0.61 (0.71 at 3 months); cards none | loans strong, cards none |
| D6 discrepancy flags | says able / pays in full while A1 Low: ~25 pp below its comparison (cards, small n); others weak | suggestive to strong (cards only) |
| D7 treatment | lost employment pays about half of has employment (both); requests (untyped) and period do not separate | descriptive |

**Logging gaps.** 60% (cards) / 81% (loans) of transcript promises have no DCORE promise on the CIF within ±7 days.
The gap grows with DPD, call length and partial / with-delay promises; logged amounts match the stated amount in 29%
of cases and dates in 12%; and agents' own DCORE notes name a promise that never becomes a promise event (55% / 84%
of remark promises unlogged). That points to logging practice, not a feed loss.

**Provisional reading (Claude, 2026-11-23; nothing decided until the refresh).** The candidates worth carrying are
loan-side and narrow: stated intent inside A3 no_promise and the unlogged promise (both "said they will pay, DCORE
has no promise"), the delinquency reason as a treatment hint in both products, and "says able while A1 Low" as a
verify flag on cards. Card fills, D1, the dispute flag as a payment signal, requests (untyped), UC1's confidence,
`supporting_data` and remarks as evidence are not worth carrying on this data. UC1's outputs are taken as generated (user, 2026-11-23): no questions on their settings, and no extra fields will be
added (no request types, repayment values in the evidence, or agent / team / queue fields), so the analysis works with
the fields there are. What the refresh can still change is coverage: more stored calls extracted and calls after
2026-07-16.

**Decision (user and manager, 2026-11-23), replaces the reading rule above.** The state value per signal is UC1's
`estimated_value`, their final verdict: read as is at the scoring month, rebuilt the way UC1 builds it for past months
(validation) until UC1 delivers it dated. Agent remarks stay in as UC1 data (UC2 derives no such signals from DCORE notes).
Our `latest` transcript reading served the interim exploration only.

## 19. As built, bundle 31 (2026-11-23): the block on UC1's signal export

Replaces §2–§8 where they differ (code: `crx_persona/uc1_stated/`; spec test `checks/uc1_stated_spec.py`).

- **Source:** `customer_signal_export` as is; `estimated_value` = the state value per signal (transcripts and remarks).
  Call metadata only for the evidence status. `simple_signal_aggregation`, `signal_level_conflicts` and
  `extracted_signals` are no longer read by the pipeline.
- **Month:** parameter `uc1_month_end` (2026-07-31; null = `persona_end_date`); other months NULL. No point-in-time
  correction (user, 2026-11-23).
- **States:** A5 / A6 mapping unchanged; a tie takes the more cautious level (raw value kept); `not-detected` →
  `not_stated`; not in the export → `no_evidence` with `uc1_evidence` no_cif / no_conversation / not_extracted.
- **Pass-through:** confidence, latest transcript and remark values (A5 / A6), `supporting_data` (capacity), reason
  (+ confidence), period, dispute, request, fraudulent customer, amount / date / plan mentioned, snapshot date.
- **Flags:** `stated_promise_unlogged_flag` (paying intent + amount or date mentioned, no A3 promise event of the
  customer's accounts alive within ±7 days of the last call; NULL without a dated call); `verify_stated_ability_flag`
  (able or pays in full while A1 low). Inputs added: `crx_<p>_a1_ability`, `crx_<p>_a3_promise_events`.
- **Check (temporary):** distributions, old × new, paid_due over August by state and flag at July end; results feed
  the workshop doc's findings table.

## 20. Bundle 31 results (2026-11-24): UC1's estimate at the July month end

Source: `workplace_mirror/bundle_helpers/b31_uc1/b31_results_summary.md` (all four model_ids; outcome = August
payments; one month end, so cells are small and read as direction).

- **Coverage (July end):** UC1 reading for 4.8% of cc_60_180 and 9.0% of rl_60_180 accounts; 21.8% / 17.4% more had
  a call UC1 has not read. 180+: 107 cc / 68 rl accounts reached through their CIF (0.0-0.1%).
- **A1 Unknown fill, cards: holds and orders.** able 27.3% (33) / partly 15.7% (108) / not stated 13.9% (101) /
  unable 6.9% (72) vs no reading 6.5%; AUC 0.613 (n 314; interim 0.528). Loans: no order (AUC 0.47, n 98).
- **Promise said, not logged: holds.** Loans inside A3 promised: unlogged 60.6% (33) vs logged 28.0% (25) vs no UC1
  29.0%; inside no_promise 25.0% (60) vs 13.9% without UC1. Cards smaller: no_promise 8.7% vs 4.1%, partly kept 23.3%
  vs logged 18.4%. Overall unlogged promises pay as well as logged ones (cc 18.0 vs 16.9; rl 36.5 vs 39.0). Of
  stated promises with an amount or date, 41% (cards) / 70% (loans) have no A3 promise event near the last call.
- **Reason: holds on loans** (has employment 43.9% vs lost 23.3%), weaker on cards (17.3 vs 14.1; inside A1 Unknown
  14.9 vs 10.8, reduced employment 4.3%).
- **Did not hold at July:** stated intent inside A3 no_promise on loans (pays in full 22.2% vs partly 23.7%, AUC
  0.52; interim 0.61 pooled); verify flag (cc 20.0 vs 19.4, rl 32.6 vs 33.1; interim -25 pp). Dispute and request:
  no payment signal.
- **180+:** accounts with any UC1 conversation pay 5-9x the rest (cc 4.7-7.2% vs 1.1%; rl 8.8-12.3% vs 1.3%), n 107-
  329: a contact effect at 180+, relevant to finding the few positive 180+ customers.
- A3 still separates far more than A5 / A6 (hi vs lo 35.2 vs 3.0 cc_60 without UC1); UC1 is read within states.

## 21. Bundle 31 follow-up (2026-11-24): transcript vs remark, money at stake, reasons in A1 Unknown

Source: `workplace_mirror/bundle_helpers/b31_uc1/b31_followup_summary.md` (60-180, July month end; prompt removed, last
version in git `60adabb`). Limits: cc DPD band unmapped in the snippet; cc outstanding = latest July balance snapshot,
not the month end.

- **Transcript vs remark:** the transcript reading orders payers better in 5 of 6 comparisons (AUC 0.51-0.61 vs
  0.44-0.55), every interval includes 0; the remark reading is mostly not detected (A5: 826 of 891 cc rows).
- **Money:** unlogged promise cc 239 accounts / 349k due / 8.1M outstanding / 28% of due paid in August; rl 137 /
  531k / 14.4M / 57% (inside A3 promised 93%). A1 Unknown = 54% of cc outstanding (283M, 13% paid) and 35% of rl
  (148M, 30%); UC1 reaches 4% / 6% of its due. Cards A1 Unknown: says able 66% of due paid vs unable 5%.
- **Reasons in A1 Unknown (cards):** lost employment 38% (27% in A1 Low, 16% in Moderate), lost + reduced 46%; they
  pay least (reduced 4%, lost 11%, no reason stated 17%). Loans: lost employment 31-34%.

## 22. Raw-data check of "promises said on calls are not logged" (2026-11-24, 60-180)

Source: `workplace_mirror/bundle_helpers/uc1/uc1_unlogged_validation_summary.md` (raw DCORE: col_his_followup,
col_mst_result, col_trn_agreement, ptp_trn_promise*, rps_cur_*; case review not done yet). The user's suspicion of a data
issue was right for most of the gap.

- **The 60% / 81% headline was a matching artefact** (A3 event date within ±7 days, one model's agreements). With A3's
  own rule (event alive) it is 33% / 69%; matched at CIF level on every DCORE agreement with A3's promise codes 25% (cc)
  / 30% (rl); counting broad result names (settlement, callback, "already paid", deferment) 9% / 11%.
- **Main cause = data linking:** A3 matches inside one model's agreement map; the promise is often entered on another
  product of the same customer (loans: 194 days on a card agreement). Ruled out: time zone / date column (≤4%), not a
  collections call (a same-day DCORE follow-up exists on >97% of days), load gaps (except 2026-07-06: zero follow-ups
  that day). Extraction error untested (case review open).
- **Bundle 31 flag overstates:** model-scoped match, and the anchor call (last call before the month end) is itself a
  promise day for only 42% (cc) / 51% (rl) of flagged customers. The payment results of the flag (§20) are not usable as
  "not logged"; re-measure after a fix.
- **DCORE data points:** promise-coded follow-ups fall from March to July while total follow-ups stay flat (cc 5,612 →
  1,887; rl 799 → 579): a possible coding change that would also thin A3's promise events. No follow-ups on 2026-07-06.
- UC1 agrees with DCORE where both exist: on DCORE promise days with an extracted call, UC1 found a paying intent in 73%.
- **User 2026-11-24 (decisions for the case review):** "logged" = a promise in the PTP / settlement / instalment tables
  or under A3's promise codes, on any agreement of the customer, ±7 days; a same-day non-promise code does not count:
  a call promise missing from the promise tables is a DCORE recording / data issue. The "loan promises are entered on
  the card" reading is not accepted: ~15% of customers hold more than one product, yet an agreement outside the model
  map was found for 74% (cc) / 99% (rl) of promise customers, which points at our agreement map or customer link.
  Case review prompt (agreement check first, then transcript + full DCORE log per case, classes a-d):
  `bundle_helpers/uc1/sonnet_uc1_unlogged_validation_prompt.md`.

## 23. Case review of promises with no DCORE promise (2026-11-24, first read)

Summary: `workplace_mirror/bundle_helpers/uc1/uc1_case_review_summary.md` (Sonnet's reading of 20 rl cases; the user's
classes, the cc cases and rl 21-100 are still to do).
- **Agreement link is sound.** <10 CIFs fan out to two DCORE customers, <10 agreements re-key one account. The outside
  agreements are other accounts of the same customer: these delinquent customers hold more products than the book
  (card and loan: 24% cc, 68% rl; plus overdrafts and closed accounts). Agents' follow-ups are often copied to every
  agreement of the customer.
- **Case set** (PTP / settlement / instalment rows or A3 promise codes, any agreement, ±7 days, all date columns):
  318 days (21.3%) cc, 149 (26.8%) rl; entry dates only 25.4% / 29.9%. By month flat for cc (19-23%), rl 18-36%.
- **20 rl cases:** a UC1 misread 8 (past payments, deferment / settlement requests, "I will try", amounts or dates
  taken from the agent's turn, two impossible dates); b DCORE has it in the dialer feedback table
  (`col_trn_atdfeedback`) 1; c promise noted in the remark under another code (LEFT_MSG, FOLLOW UP, SETTLEMENT,
  JOB LOST) 11, five of them hedged; d nothing in DCORE 0. Hedged cases decide the split: a 30-70%, c 25-65%.
- **Reading:** "UC1 promises are missing from DCORE" is not supported. UC1 over-reads promises, and DCORE records most
  of the real ones in remark text outside the promise codes (SETTLEMENT is not an A3 promise code).
- Open: user classes + cc cases; the dialer table as promise evidence on all days; SETTLEMENT and remark-only promises;
  UC1 extraction feedback (agent turns, past payments, hedged language, impossible dates).
