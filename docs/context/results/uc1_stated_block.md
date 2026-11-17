# UC1 stated block: how the UC1 signals are condensed (as built, bundle 26)

How bundle 26 (`crx_<p>_uc1_stated`) turns UC1's call-transcript signals into two stated states and
a few flags, which signals it keeps and leaves out, how it sits beside A1–A4, and what has to be
thought through when the full UC1 delivery lands. As of 2026-11-17; nothing has run in PROD yet.

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
| `legacy_only` | only legacy-format extractions, which UC1's customer table does not read |
| `extracted` | at least one current-format extracted conversation: the only case with states |

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
| agent remarks, legacy extractions | UC1's customer table ignores them; legacy-only shows as `legacy_only` |
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
