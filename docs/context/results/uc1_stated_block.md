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

**Assessment (Claude, for the user to confirm):** §12.3 row "adds nothing" applies. Keep the stated block as display
only (collector context, dispute / relief flags), no tier effect. Re-test on the full run with the same snippet; the
bar for an overlay rule = within-state AUC gain ≥ +0.02 on rows with a reading, holding in both products. The
contact effect (conversation present) is the stronger signal and belongs to the parked Genesys-as-contact question
for A2 / A3 (user / GRR), not to UC1. Carry: drop `legacy_only` (coded, `cd698c8`) in the next UC1 bundle.
