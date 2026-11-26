# UAT Sonnet prompt: UC1 coverage ceiling, UC1 signals vs reachability, and the tier effect

Paste everything below the line into the UAT Sonnet session. The deck is on 27 Nov: Q0 and Q2 for cc_60_180 matter most.
If a snippet from an earlier version of this prompt is already pushed, paste this and ask Sonnet to rebuild it to this
version.

---

Goal
Understand how far UC1 can reach and what its signals add where A2 says we cannot reach the customer, on UC1's August
refresh. The results feed three things: the GRR deck (coverage, and where UC1 fits), the hypotheses we retest on the
full UC1 data, and a reusable harness for the integration and pilot work. Four questions:
Q0 Coverage ceiling. What share of customers had a right-party contact since March (when the Genesys store starts), and
   how far down the chain (store → UC1 metadata → UC1 reading) does each step get? This is the upper bound of UC1's
   coverage; recency and month-end reachability are read against it.
Q1 Going dark. Which UC1 signals come before a customer goes from Reachable to Non-Reachable the next month?
Q2 Unreachable but talking. Which Non-Reachable or Unknown accounts had a recent conversation? Did UC1 read a positive
   signal in it? What do they owe, and do they pay?
Q3 Tier effect. Would a recent UC1 signal put a Non-Reachable or Unknown account in another in-house / agency tier than
   its segment gives it? (The tier works mostly on reachable customers, but not only.)
Data understanding and sizing only: no pipeline change, no A2 rule change, no tier rule change.

The question behind Q1-Q3: does the signal come from the UC1 reading, or just from having had a conversation (which
DCORE already shows)? On the latest run, 180+ accounts with a recorded call paid 5-14% vs about 1%, but calls UC1 never
read paid as well. So every comparison uses the four groups C1-C4 below. UC1 adds value only where a UC1 reading beats
"conversation, no UC1 reading".

Decided (do not reopen)
- Axis numbers: A1 deterioration, A2 locatability, A3 credibility, A4 ability (`crx_<p>_a1_ability` holds the A4
  states).
- A2 is fixed and signed off:
  - `reachability_state` = reachable / non_reachable / unknown (`reachability_unknown_reason`: no_dcore_record /
    no_contact_in_window).
  - Window W = the observation month + 2 months before (+ 5 at 180+).
  - Reachable = a contact in W. Non-Reachable = the last 3 attempt days (6 at 180+) all failed, the oldest in W, no
    contact since.
  - A2 reads DCORE on the account's own agreements. Use its `last_contact_date` and `last_attempt_date`.
- UC1 state = UC1's estimate as is:
  - the posteriors' top level on the month end (`signal_level_posteriors`), with values and levels mapped as in
    `crx_persona/uc1_stated/classify.py`;
  - amount / date named: from `customer_signal_export` at 07-31 only;
  - evidence dates: from `proposer_level_observations`, the 2026-08-31 snapshot partition only, split transcript /
    remark.
- Reuse the loaders of `tmp_validation/uc1_latest/` (readings, outcomes) and `tmp_validation/uc1_refresh/` (Genesys
  store to CIF, metadata, the right-party waterfall).
- Signal age decides how a signal is read (a customer's situation changes).
  - Age = days from the latest evidence naming that signal (on or before the month end) to the month end.
  - Never take the age from the posterior row: it carries old values forward.
  - Age bands: 0-30, 31-60, 61-90, 91-180, over 180 days. Every signal table is shown by age band.
- Age limit to test (the user's brainstorm idea, not a decision): in 60-180, stated ability and intent count only when
  under 90 days old; the reason may be older. Show ability / intent at under 90 days and at any age, and the reason at
  under 90, under 180 and any age, so the limit can be judged.
- Outcomes:
  - `paid_due` = next-month payments ≥ max(amount due, AED 100).
  - Money collected = as `tier_stability.py` defines it, next month and next 3 months.
  - Payments end 2026-08-31: next-month outcomes exist for t ≤ 07-31, 3-month outcomes for t ≤ 05-31.
- Reading results (user):
  - An effect "holds" only if all three are true: it is ≥ 5 pp (or ≥ 0.02 AUC) inside the target state; the 95%
    interval excludes 0; it beats C3 (conversation, no UC1 reading).
  - An AUC around 0.6 is not good enough to rank on.
  - Otherwise the verdict is "watch" (right direction, but too small or too noisy) or "no signal".
  - No minimum n. Put n beside every share. Intervals from 200 account resamples.

Shared definitions
- Store and metadata dates:
  - The Genesys store starts about 2026-03-06 (report the date used), so a 90-day look-back is complete only from 06-30.
  - UC1 metadata ends 2026-07-16, so UC1 readings under 30 days old at 08-31 are empty by construction.
  - State both beside the tables, not as findings.
- Right-party contact (RPC): a DCORE event with a code in `CALL_CODES` (OC / CB / IC) and a result in
  `RIGHT_PARTY_CONTACT` (`_dcore_codes.py`). Count it two ways:
  - CIF view: any agreement of the CIF (UC1 works per CIF);
  - account view: the account's own agreements (A2's view).
- UC1 signals:
  - Positive: ability able / partly_able; intent pays_in_full / partly_or_later; reason has_employment /
    increased_obligations; amount or date named; request detected.
  - Negative: intent refuses; ability unable; reason lost / reduced employment; dispute; fraud flag.
  - Report each level, "any positive" and "strong positive" (pays_in_full, able, has_employment, amount or date named).
    Most delinquent customers say partly_or_later, so "any positive" comes close to "any reading".
- Comparison groups at month end t (CIF view; look-back 90 days unless a table says 30 days or any age):
  - C1: UC1 reading with a positive signal;
  - C2: UC1 reading, no positive signal;
  - C3: a conversation (RPC or Genesys store call), but no UC1 reading;
  - C4: no conversation.
  - C1 vs C2 and C1 vs C3 are the UC1 tests. C3 vs C4 is the conversation effect.

Q0 Coverage ceiling (runs first; Q1-Q3 use its flags)
- Base: persona accounts at each month end 2026-03-31 .. 08-31, all four model_ids; count accounts and CIFs.
- The chain per t, in CIF view and account view:
  1. RPC since the store start;
  2. RPC in the 90 days before t;
  3. a Genesys store conversation (any direction; say how inbound calls without an RPC code show);
  4. in UC1 metadata;
  5. a UC1 transcript reading;
  6. a UC1 remark reading;
  7. any UC1 reading.
  Show each as % of the base and % of the step above. Also per customer over the fixed window store start .. 08-31
  ("ever since March").
- Recency × reachability matrix, per t:
  - rows: age of the latest RPC (none since March / 0-30 / 31-60 / 61-90 / 91-180);
  - columns: A2 state at t;
  - cells: accounts; share with a store conversation; share with any UC1 reading; share with a UC1 reading under 90
    days old.
- Reconcile with A2:
  - Reachable at t vs an RPC in W on the account's own agreements. They should almost coincide; explain the rest
    (gone-dark overrides, contact results outside the RPC list).
  - Among non_reachable and unknown: share with an RPC since March, in CIF and account view, and how old it is.
- UC1 coverage as a share of each ceiling, any age and under 90 days, by A2 state, A3 level, A4 state and DPD band.
- Monthly flow (for collector card and pilot sizing):
  - accounts with a new RPC, a new store conversation, or a new UC1 reading in each month;
  - how many accounts per month would have a UC1 reading under 30 / 90 days old if UC1 read every store conversation
    (store ceiling), and if every RPC had a transcript (RPC ceiling).
- Remark-only readings: share with a store conversation on the CIF the same day or the day before; whether UC1 read
  that call (in metadata / extracted); whether DCORE shows an RPC or only attempts that day. This says how much of
  "remark only" is unread calls vs notes with no call behind them.
- Known from the refresh check: only about 13% of card RPC days and 5% of loan RPC days have a transcript in the store.
  Keep the RPC ceiling and the store ceiling apart.

Q1 Going dark
- Unit: account-months reachable at t = 04-30 .. 07-31.
- Outcome = the state at t + 1: non_reachable / reachable / unknown / deceased (if flagged) / left the base (split:
  rolled into the 180+ model, other). No payments needed, so the 07-31 → 08-31 pair counts.
- Going-dark rate by UC1 signal level and age band, vs C2, C3 and C4:
  - stratify by the age of A2's `last_contact_date` (0-30 / 31-60 / 61-90): a recent contact alone predicts staying
    reachable, and it goes with a recent UC1 reading;
  - then within A3 level and within A4 state;
  - rate ratio and pp difference, with intervals.
- The last conversation before t: its stance, its source (transcript / remark), days from it to t.
- Context, no UC1: the same rate by A3 level, A4 state, DPD band, location_state.
- Scope: 60-180, both products; 180+ where n allows.

Q2 Unreachable but talking
- Unit: account-months non_reachable or unknown at t = 04-30 .. 08-31 (outcomes only for t ≤ 07-31). Split Unknown by
  `reachability_unknown_reason`.
- Groups C1-C4. Within C1 and C2, split by when the latest evidence falls:
  - (a) on or before A2's `last_contact_date`;
  - (b) after it, or no contact ever: a conversation A2 does not see.
  - Also days from the latest evidence to `last_attempt_date`: did the customer talk after the failed calls began?
- For (b), why A2 does not see it, on the evidence day:
  - an RPC on another account of the CIF (inside the persona base or not);
  - a DCORE follow-up on the CIF, but no RPC;
  - nothing in DCORE (Genesys only).
  - Inbound or outbound, if metadata or the store holds the direction (name the field).
- Per group: accounts, amount due, outstanding, location_state, each signal level, "any positive", "strong positive",
  by age band; paid_due and money collected next month.
- Scope: all four model_ids (Non-Reachable is common at 180+).

Q3 Tier effect
- How the tier code gets in: copy the G3 functions (mapping build, cap, relative cut, money at equal in-house share)
  from `tier_stability.py` / `inhouse_check.py` unchanged into `tmp_validation/uc1_reach/tier_g3.py`, with a header
  naming the source files and commit. The harness must not depend on another temp folder. Only the inputs change: the
  frame instead of their loaders. The third tier (the non-workable cut) is a config value. Tie-out: for one complete
  month (05-31, cards and loans) the copied code gives 0 tier differences against a run of `tier_stability.py` G3,
  and the same in-house share and money at equal in-house share as its saved results. If they differ, stop Q3 and
  report.
- 60-180: the G3 tier from the workplace `tier_stability.py` / `inhouse_check.py` (reuse them, do not rewrite):
  - segment = deterioration family × reachability × credible-or-able;
  - value = money collected per account in the next 3 months, pooled over up to 6 earlier months with complete
    outcomes, capped at the training p99, cut relative to the book level;
  - the mapping is built only on months before t;
  - three tiers: in-house / agency / non-workable pool (the bottom of the agency tier);
  - the deck shows cards at 17% / 54% / 29% of accounts and 48% / 46% / 6% of money. Use the cut-offs that give these
    shares (loans: the same rule), and say which.
- 180+: there is no tier rule. Use the 180+ positive-signal group instead:
  - `positive_signal` in `persona_deck_numbers.py` = payment in delinquency, promise kept or partly kept, reachable, or
    A4 able;
  - it holds 12% of card accounts; about 1 in 5 pays, vs under 3% of the rest;
  - the question: how many Non-Reachable / Unknown accounts with a recent positive UC1 signal sit outside that group,
    and do they pay like the group or like the rest?
- Unit: account-months non_reachable or unknown at t. 3-month money for t = 04-30, 05-31; next-month money and paid_due
  for t = 04-30 .. 07-31.
- Per group C1-C4 (also by "strong positive", age band, transcript vs remark, and Q2's (a) vs (b)):
  - accounts and tier as assigned;
  - money per account and paid_due vs C4 in the same segment, vs the segment's estimate, and vs the average of the tier
    above;
  - differences with intervals.
- What-if overrides, each at under 90 and under 30 days:
  - (i) a UC1 positive (and a strong positive) moves the account one tier up;
  - (ii) a conversation (C1 ∪ C2 ∪ C3) moves it one tier up;
  - (iii) a UC1 negative moves it one tier down.
  - For each: accounts and money that move; money captured at equal in-house share (as `tier_stability.py` defines it),
    with and without the override; how many in-house places it takes from reachable accounts, and what those accounts
    collected.
  - UC1 adds to the tier only if (i) beats (ii).
- The non-workable pool: how many accounts with a recent conversation, or a recent positive UC1 signal, it holds, and
  what they pay.
- Reverse check, short: reachable in-house accounts with a recent negative UC1 signal vs their segment.

Primary comparisons (first in the summary; everything else is descriptive)
- P1 (Q0): the ceilings at 07-31, cards and loans 60-180: RPC since March; RPC in 90 days; store; any UC1 reading; UC1
  reading under 90 days.
- P2 (Q1): going-dark rate, C1 negative under 90 days vs C2, within last-contact age, cards 60-180.
- P3 (Q2): paid_due, non_reachable C1 (b) any positive under 90 days vs C3, cards 60-180 and cards 180+.
- P4 (Q3): override (i) vs (ii), under 90 days: money at equal in-house share, cards 60-180.
- For each: n; difference [interval]; verdict (holds / watch / no signal); the smallest difference detectable at 80%
  power with today's n; the n expected at the store ceiling and at the RPC ceiling.

Tie-outs (print first; report any mismatch at the top of the summary; never adjust to match)
- Accounts at 07-31: cards 18,397 (A2 reachable 22.0%, 4,046); loans 3,728 (28.5%, 1,064); 180+ cards 316,738, loans
  54,819.
- UC1 reading at 07-31 from the posteriors: cards 3,525 (19.2%), of which 1,299 under 90 days (7.1%); loans 679
  (18.2%), of which 307 (8.2%). (The export at 07-31 gives 3,528 / 680.)
- Reachable with a reading at 07-31: cards 1,275 (export) and 600 under 90 days (posteriors); loans 265 and 130.

Rules
- Loading: `catalog.load` only; reuse the loaders above. Use persisted persona outputs as they are; do not re-run any
  engine.
- Catalog: temporary entries only in `conf/base/catalog/catalog_tmp_uc1_full.yml`, explicit ones (the workplace Kedro
  does not resolve dataset factories). No pipeline, other catalog or registry change.
- model_id = `catalog.load("params:model_id")`, in every output file name.
- Join persona rows to UC1 on `cif_id`.
- Aggregates only in results files and the summary: no account, CIF, agreement, conversation or agent ids; no
  transcript or remark text; cells under 10 shown as "<10".
- A part that fails records its error, and the rest still runs.
- New tracked folder `tmp_validation/uc1_reach/`; commit only that folder.

Deliverables
1. The harness, pushed from UAT, in `tmp_validation/uc1_reach/`:
   - One function builds the account-month frame that every part reads: account, month end, persona states, A2 fields,
     RPC and store flags with ages, UC1 level per signal with source and age, groups C1-C4, tier, outcomes. The README
     lists its columns.
   - The frame is saved to one explicit temp entry, `uc1_reach_frame` (path carrying model_id like the other entries
     in the temp file; HDFS only, never committed), so later checks (pilot sizing, the full-data rerun) load it instead
     of rebuilding it.
   - One config block at the top: month ends, age bands, age limits, parts to run (`q0,q1,q2,q3`).
   - One results file per model_id (`uc1_reach_<model_id>.json` + `.md`) with the tie-outs, every table and the primary
     comparisons. Keep table names stable so reruns can be diffed.
   - README:
     - one command per model_id; run cc_60_180 first;
     - when to rerun: UC1 reads more calls; payments are refreshed past 08-31 (this adds June / July 3-month
       outcomes); a new persona month end;
     - `uc1_reach_frame` is removed in the UC1 cleanup.
2. After the user commits the PROD results: `summary_uc1_reach.md` (under 250 lines), in this order:
   - a. Tie-out mismatches, or "all match".
   - b. Primary comparisons P1-P4, with verdicts.
   - c. Deck lines: 5-8 plain sentences with numbers, each pointing to its table. Cover the coverage ceiling and where
     UC1 stands against it, and whether a recent UC1 signal changes any tier (for how many accounts, and how much
     money).
   - d. Tables for Q0, Q1, Q2 and Q3 (by age band wherever a signal is involved).
   - e. Hypotheses for the full UC1 data and the pilot. For each: statement, metric, bar, today's value [interval], n
     today, n at the store ceiling and at the RPC ceiling, what would confirm it or drop it.
   - f. What could not be computed, and why.
