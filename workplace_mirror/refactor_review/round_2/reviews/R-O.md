# R-O (Owner), round 2, run 2 (A3 + A1): review and sign-off decision

Head `ac50e2b`. Read: `decisions.md` (D-U1-1..7, D-B-1/2, D-2-1/2), `round_2/merge_log.md`, `round_2/gates.md`,
`round_2/S6_behaviour_check.md`, `questions.md` §B (Q-R-10..12) and §C, R-E.md (3.8) and R-I.md (4.20). Code
read: `a3_credibility/promises.py`, `constants.py`, the round 2 hunks of `a3_credibility/signals.py`,
`classify.py` and `pipeline.py`, A1 `classify.py` / `signals.py`, `rl_a1_ability/nodes.py`, `cc_raw_extract/nodes.py`, and
the D-A3-29 / D-A3-30 spec text. No edits, no commits, no Spark. The rubric is frozen (`rubrics/owner.md`),
and the tie-break policy is as written there.

**Result: converged. Signed off with four recorded exceptions (E1–E4).** A short naming and docstring
clean-up (C1–C7) is to be applied and gated by the Master before the build. Bundle 25 has delivery
conditions (§5) that the user and the workplace must meet before the build.

## 1. Round 2 items

1 S2-11: accept (blocking: no) criteria: O1
  Met. `build_cross_product_signals` pre-filters the products with `scoped(products, obs, "cif_id")`, and the
  join is left to the planner. No obs rows are broadcast. The one remaining explicit broadcast in A1
  (`signals.py:480`, EOSB scoped agreements) is the pattern I accepted in round 1 (S2-07). The bundle check
  logs its run time on cc_180_plus (§5).

1b promises: one pass over dues and one over payments per promise day: accept (blocking: no) criteria: O1, O7
  The plan is roughly halved over the two largest A3 inputs, and the flow reads as the rule (`_with_terms` →
  `_with_payments` → `_with_event_start` → `_events` → `_judged`). Two things I note without asking for a
  change:
  - `_with_payments` sums each day's payments from the start of the history (needed by the
    `_paid_before − _paid_by` difference). Payment history is already bounded by the wrappers'
    `HISTORY_MONTHS` floor, so the join stays small per account.
  - The equivalences 1b relies on (conditional aggregates = the old range joins; an event's paid amount =
    its start day's) are confirmed by the oracle and argued line by line in S6 §2.1. Floats are handled by
    ruling (e).

2 S3-04: accept (blocking: no) criteria: O1, O2, O6
  My round 1 blocking item is met: the `raw_stg_balance` check names only `contract_idt`, `banking_date`,
  `edp_load_date`, which this node reads itself.

3 S3-01 reverted: accept the revert (blocking: no). Ruled below (a): drop it for this bundle.

4 R-E N-3 skipped: accept the skip (blocking: no) criteria: O6
  There is one boundary check per public builder, and each builder is called directly by the A3 spec. R-E
  withdrew the item.

5 A3 state log label (my round 1 N-1): accept (blocking: no) criteria: O1, O4
  Met (`classify.py:89`, `a3_credibility [<model_id>]`), the same shape as A1 / A2. It is a log line only.
  List it under "PROD log changes" in the bundle.

6 S1-06: accept (blocking: no) criteria: O5
  The carry is one constant plus one expression. The closure rule ("> 0 that month only, 0 stops") will
  still need a per-row flag in the same union step, which is the right place.

7 `persona_floor`: accept (blocking: no) criteria: O4
  The RL wrapper imports from the engine (the intended direction). Keeping it out of `_common` follows from
  ruling (a). `_floor` → `persona_floor` (now public) goes on the test list.

8 S4-04 narrowed: accept (blocking: no) criteria: O6, O2
  Four signal-output names are typed once. Pylint 10.00 at exactly 15 locals: the next local added to
  `create_a3_pipeline` will trip R0914, so the A3 bundles that follow should know.

9 `_SAME_DAY_ORDER` / `same_day_rank`: accept (blocking: no) criteria: O3
  The Q-28 order is now data, and S6 confirmed it equals the old order (answers Q-R-10's concern). The +4
  lines are allowed: they name a rule.

10 `PROMISE_MIN_AED`: accept (blocking: no) criteria: O3. Ruled below (c): keep it.

11 `CUTOFFS` / `DEADLINES = tuple(CUTOFFS)` / `PROMISE_DAYS`: accept (blocking: no) criteria: O5, O3
  The option list and its implementation cannot drift apart. The unknown-option error is raised before any
  Spark work. Placement is ruled below (b). `constants.DEADLINES` → `promises.DEADLINES` is a public move:
  test list.

11b readability (promises order, `_TERMS` / `_DAY_TERMS`, A1 `_strong_amount` / `_instalment_amount`):
accept (blocking: no) criteria: O3, O7
  `_strong_amount` is the single home of D-U1-3 (family rule §2), and the instalment rule is kept apart,
  correctly, because it did not unify. The dated "user 2026-11-14" comment is gone (rule 8).

12 S5 docstrings: accept (blocking: no) criteria: O3
  `_latest_in_month` states the tie rule (my round 1 S2-10 revise, met), the contact builder states D-A3-30,
  and the README has the new thresholds.

### The behaviour steps' code shape (8b3d969, faa744b, fix ac50e2b): accept (blocking: no) criteria: O1, O3, O4, O5

The rules are the user's. I judge only their shape:
- **Event fold.** `_event_step` is a per-account `F.aggregate` over distinct promise days: deterministic
  ordering, no Python UDF, and the state is a typed struct. The terms come from the start day, so no later
  row can re-date an earlier event (S6 §2.1, no look-ahead). The fold is the one place the pending "points"
  and "concluded when paid" questions (Q-S6-18) would touch.
- **Product differences are carried by dates, not by `if product`.** RL cash is dated at the month end, so
  loans never end an event mid-month and the refusal month's cash lifts a refusal. This is the shape O4 asks
  for.
- **Cent rounding (Q-S6-17, ac50e2b).** It is the right fix, in the one place a difference of two sums is
  compared. One adjacent comparison stays unrounded: `_judged` (`paid >= promise_amount`, a single sum,
  D-A3-25 code from before this bundle). Making it consistent is a behaviour change, so it goes to the user
  (N-1). It does not block sign-off.
- **A1.** One `_strong_amount`, constants grouped under the family rule §2, no leftover old threshold names
  in `src/` (S6 §2.3).

## 2. Rulings on the open points

**(a) S3-01: drop it for bundle 25; recorded as exception E1.** The obstacle is the check harness itself.
`a3_engine_spec.py` and `golden_inputs.py` stub `enbd_collections.nodes*` as empty packages. Changing the
oracle's stub layer in the last round, to land a five-line dedupe whose only effect is the text of a failing
run, trades gate integrity for nothing a PROD reader sees. The merge logs say "no oracle or spec-check file
was edited", and I want that sentence to stay true for the bundle that carries three behaviour steps. Take
it up when the DCORE helpers are mirrored or the harness is next opened for its own reasons. Then do it the
narrow way R-E describes: keep the real `enbd_collections.nodes` packages and stub only the two DCORE
modules. Q-R-05: tell the user it is deferred, not answered (b).

**(b) `DEADLINES` / `CUTOFFS` in `promises.py`: keep them there.** All three reviewers agree. The decision
(`PROMISE_DEADLINE`, which option per segment and product) stays in `constants.py` with the other decided
numbers. The options (what each deadline means as a date) sit beside the one function that evaluates them.
Lambdas in `constants.py` would bring Spark into the constants module. The constants comment points to
`promises.CUTOFFS`, which is enough.

**(c) `PROMISE_MIN_AED` alias: keep it (R-I over R-E).** By my tie-break, a line that encodes a business
threshold goes to R-I. D-A3-29 names the promise floor and the partial limit separately from Dimension B's
"any payment" (D-A3-5), and the open promise-points work (Q-S6-19, Broken +1) is exactly where they may
part. It costs 3 lines and one concept. R-E's condition stands as a note for the promise-points bundle: if
that bundle does not separate them, delete the alias there.

**(d) R-I R-1..R-4 and `STABLE_INCOME_FLOORS`:**
- R-1: accept. Rename `_paid_by` to `_paid_not_after` (it is `~_after(day)`), and say once in
  `_with_payments` why an event starting that day never counts it. Private, one module: clean-up C1.
- R-2: accept. The `_with_terms` docstring cites D-A3-29, which is where the spec states the promised
  amount and the 31-day cap. C3.
- R-3: accept. The `_paid_after_refusal` docstring cites D-A3-30 beside Q-29. C3.
- R-4: accept the rename, reject the marker. Rename `STATEMENT_FALLBACK_D` to `NEXT_STATEMENT_MAX_DAYS`
  with the comment "the first statement after the promise, at most 31 days after it (D-A3-29)". Do not
  write "D-B-2, to be confirmed": rule 8 says the code says what it does now, and such a note goes stale
  the day the user answers. Q-R-11 is a build condition instead (§5). If the user answers (b) "no cap", the
  code changes anyway and C2 is moot. C2, applied only after Q-R-11 is answered.
- `STABLE_INCOME_FLOORS`: fix the layout (one line, comment above: "S12: the window's salary is this many
  strong amounts"). Keep the name: spec S12 cites it, and renaming a spec-cited constant for wording is the
  churn I ruled out in run 1 D-3-1. C4.

**(e) Float tolerance in the PROD check: |old − new| < 0.005 on double amount columns; everything else
exact.** Sums of AED amounts over the same rows in a possibly different order can differ in the last bits.
Spark's partial-aggregation order was never fixed in the old plan either, so bit equality was never a real
claim. Half a cent cannot hide a real difference in a two-decimal currency. Everything else is compared
exactly: keys, dates, strings, flags, levels, counts, states, `promise_outcome`, `event_kind`. Any
difference there fails the step. The tolerance applies to `promise_paid_amount`, `promise_amount`,
`paid_amount`, the A1 monthly amount columns and `liquidity_anchor_amt`. The check reports the largest
absolute difference per column, so a near-miss is visible.

**(f) My round 1 conditions:**
- S3-04 (blocking): **met**.
- S2-11 (must-do before the build): **met**.
- S2-10 docstring: **met**.
- N-1 (log label): **met**.

The D-1-3 bundle-check condition (count the tie keys; A1 differences only on their CIFs) is carried into
§5.

## 3. Scores

### Changed tier-L files this round (weights O1 18 · O2 18 · O3 16 · O4 14 · O5 14 · O6 10 · O7 10)

| File | O1 | O2 | O3 | O4 | O5 | O6 | O7 | Weighted | Note |
|---|---|---|---|---|---|---|---|---|---|
| `a3_credibility/promises.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.24** | one pass per input; fold deterministic; C1–C3, C5 pending |
| `a3_credibility/constants.py` | 5 | 4 | 5 | 4 | 5 | 5 | 4 | **4.58** | every number with its D-A3 id; C2 pending |
| `a3_credibility/signals.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | same-day order named; C3 pending |
| `a3_credibility/pipeline.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.28** | names typed once; at the locals limit |
| `a3_credibility/classify.py` | 5 | 4 | 4 | 5 | 4 | 5 | 5 | **4.52** | log label as A1 / A2 |
| `a1_ability/classify.py` | 4 | 4 | 5 | 4 | 5 | 5 | 4 | **4.40** | one strong amount; C4 pending |
| `a1_ability/signals.py` | 4 | 4 | 4 | 4 | 5 | 4 | 4 | **4.14** | no obs broadcast; carry one constant; income builder still long (S4-06 to the carry bundle) |
| `rl_a1_ability/nodes.py` | 5 | 4 | 4 | 5 | 4 | 5 | 5 | **4.52** | one floor helper |
| `prm_products.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | tie rule stated |
| `cc_raw_extract/nodes.py` (tier K, O1–O3) | 3 | 3 | 4 | – | – | – | – | – | check narrowed; still a large diff on an unimportable module (E2) |

### Tree-wide (tier L, line-weighted, round 1 rows carried where unchanged)

| O1 | O2 | O3 | O4 | O5 | O6 | O7 | Overall |
|---|---|---|---|---|---|---|---|
| 4.1 | 4.0 | 4.3 | 4.1 | 4.4 | 4.8 | 4.2 | **≈ 4.25** |

- **O2 at 4.0** depends on the bundle plan listing the round 2 symbols (C7) and on the §5 check design;
  without those it is 3.8.
- **O4 at 4.1** carries E1 (two `require_columns`).
- No tier-L file is below 3 on O1–O3.

### Convergence (workflow rule)

| Condition | State |
|---|---|
| Gates green on the final commit | yes (`round_2/gates.md`; oracle re-run on `ac50e2b`: pass, 188 datasets; A3 spec pass; A1 91/91) |
| No open blocking objection | yes (R-E none, R-I none, R-O none) |
| R-O ≥ 4 on every criterion | yes (lowest O2 4.0, conditional on C7 / §5) |
| R-E and R-I ≥ 3.5 | yes (3.8; 4.20) |
| No new revise item that needs a round | yes: what remains is naming / docstring only (C1–C7) or user questions |

**Converged. No round 3.**

## 4. Sign-off

**SIGNED OFF, with recorded exceptions, on code `ac50e2b` plus clean-up C1–C7** (Master applies, all gates
re-run green, nothing else changes). Behaviour questions stay with the user. The bundle is built only when
§5 holds.

Recorded exceptions:
- **E1. Two `require_columns` helpers** (`_common`, `frames`). O4 is held at 4.1. The cause is the check
  harness's package stubs (ruling (a)). Clears when the harness stubs only the DCORE modules.
- **E2. Tier K `cc_raw_extract/nodes.py` O2 3** (large docstring rewrite, module not importable in the
  mirror). Mitigated by the UAT `MERGED` review in §5.
- **E3. R-E shared-layer / engine average 3.9 < its 4.0 target.** E1 net lines are positive because the
  behaviour steps and the D-A3-29 fold are inside the count. R-E does not object. Re-score at the
  promise-points bundle (alias, Scorecard modes B-04).
- **E4. Smoke at its baseline** (six `cc_raw_extract` import lines; `config.EDP_LOAD_DATE_BUFFER_MONTHS`
  missing in the mirror). Pre-existing, not a regression.

Not exceptions but still with the user: S7 group A (dead code, after the workplace grep; its own bundle),
B-04, B-06, and the §C questions.

### Clean-up before the build (no round; Master applies, then all gates)

- **C1** `promises.py`: `_paid_by` → `_paid_not_after`, plus one sentence in `_with_payments` on why an event
  starting that day never counts it.
- **C2** `constants.py`: `STATEMENT_FALLBACK_D` → `NEXT_STATEMENT_MAX_DAYS`, comment "the first statement
  after the promise, at most 31 days after it (D-A3-29)". Only after Q-R-11 is answered (a). No "to be
  confirmed" text.
- **C3** Spec ids: `_with_terms` docstring cites D-A3-29; `_paid_after_refusal` docstring cites D-A3-30 next
  to Q-29.
- **C4** `a1_ability/classify.py`: `STABLE_INCOME_FLOORS = {3: 2, 6: 3}` on one line, the S12 comment above
  it, name kept.
- **C5** `promises.py` (`EVENTS` or `build_promise_events` docstring): one line that `promise_paid_amount`
  is the payments after the event day up to its cutoff and is not to be summed across events (Q-S6-21 (a)).
- **C6** Spec only: the D-A3-29 promised-amount sentence made to match the code's floor ("at least 100 AED;
  100 AED when no due exists"), per Q-S6-19 (a). If the user picks (b), that is a code change and goes to
  the A3 behaviour step instead.
- **C7** Bundle plan: the test-update list adds round 2's symbols:
  - `_floor` → public `persona_floor`;
  - `constants.DEADLINES` → `promises.DEADLINES`;
  - new `CUTOFFS`, `PROMISE_DAYS`, `PROMISE_MIN_AED`, `_SAME_DAY_ORDER`, `_strong_amount`,
    `_instalment_amount`;
  - removed `FOLLOWUP_RUN_DAYS`, `MATCH_DAYS`, `_followup_promises`, `_consolidate`, `_run_step`,
    `_no_runs`, `_cutoff`, `_with_due`, `_with_paid`, and the old A1 threshold constants;
  - C1 / C2 renames;
  - the log label change.

## 5. Bundle 25 delivery conditions

### Scope

One bundle, number 25, with four parts:
- **A3-1** promise events: D-A3-29 as decided 2026-11-14, promised amount D-U1-6, 31-day cap;
- **A3-2** refusal: D-A3-30;
- **A1-1** one strong amount and `FLOW_SOME` (D-U1-3 / -4);
- **R** the refactor (rounds 1–2).

D-U1-5 (persisted dues / payments) is in it only if the UAT listing is back before the build.

### PROD check design

The reference is the persisted outputs, produced by today's workplace code. The new tree runs in temporary
Kedro nodes writing temporary catalog entries, for all four model_ids, with a cleanup prompt at the end.

**Layer R: must be exactly 0 differing rows** (exact on every non-amount column; amounts within 0.005,
ruling (e)). It covers every table the behaviour steps do not touch:
- `product_primary`. `prm_card_contracts` and `prm_loan_month_end` are exact. `prm_card_month_end` is
  exact except on keys with two or more rows on their latest day (S2-10, D-1-3). The check counts those
  keys, and differences are allowed only there.
- `product_features`: exact, except rows of tie-key contracts.
- `bureau_salary_bounces`: both features exact.
- A1 signal tables (income, CASA, cross-product, distress, EOSB, liquidity anchor): exact (cross-product:
  tie-key rows excepted).
- **A1 state under the old thresholds.** The check module carries a temporary copy of the workplace's
  current `a1_ability/classify.py` (old constants) and runs it on the new signal tables. The result is
  compared with the persisted `crx_<p>_a1_ability`: exactly 0, except CIFs holding a tie-key card. This
  isolates the A1 refactor from A1-1.
- A3: episode, cycle ledger (`crx_cc_a3_payment_cycles` / `crx_rl_a3_dlq_cycles`), instalments, Dimension B
  and Dimension C signals: exact. Contact signals: every column except `a3_refusal_flag` and
  `refusal_followed_by_payment` exact. A3-2 changes only those two.
- Regression guard for the shared layer (`_common` changed): A2 and A4 final outputs exact.
- What layer R cannot isolate is the refactor of `promises.py` and the commitments signals, because A3-1
  rewrites them. Their behaviour-preservation claim rests on the oracle (188 datasets) and the A3 spec
  test, run on the rounds' trees. The bundle summary must say so in one sentence.

**Layers A3-1, A3-2, A1-1: D4 distribution plus old-vs-new crosstab**, reviewed before step 8:
- **A3-1** (persisted events → new), per model_id:
  - event counts by `event_kind`, and the outcome distribution;
  - events whose amount changed because a NULL due was skipped (D-U1-6) and events whose amount is the
    100 AED floor over a known due under 100 (Q-S6-19);
  - events capped at 31 days (Q-R-11), and events ended early by full payment;
  - `paid` events holding a promise day after their last payment (Q-S6-17 guard);
  - `a3_commitments_level` crosstab.
- **A3-2**: `a3_refusal_flag` crosstab, refusals lifted by RL refusal-month cash and by a CC same-day
  payment (Q-R-12), counted separately.
- **A3 state**: persisted → new crosstab, with moved rows split into commitments-level change only, refusal
  change only, and both.
- **A1-1**: the old-threshold state (layer R) → the new state. Crosstab, rows moved by family, payment and
  cure per level (D-U1-3), four model_ids.
- Run times of the A1 EOSB and cross-product nodes and of `build_promise_events` on cc_180_plus (the
  broadcast and the fold on the largest book).

### Confirmed before the build

1. **Q-R-11** (31-day next-statement cap) and **Q-R-12** (CC same-day payment lifts a refusal), with
   **Q-S6-20** decided together with Q-R-12 (same-day plan, `>` vs `>=`). The spec already states both
   choices as decided, so if the user says otherwise, code and spec change in A3-1 / A3-2. C2 waits on
   Q-R-11.
2. **Q-S6-19** (100 AED floor over a known small due): (a) → spec fix C6; (b) → code change in A3-1.
   Recommended with them: Q-R-10 (a), Q-S6-18 (a), Q-S6-21 (a), and **N-1** (round `_judged`'s comparison to
   the cent, so it matches the early-end test; it fits inside A3-1's check).
3. **UAT catalog listing** of the workplace A3 entries: `crx_*_a3_dues` / `_payments` (D-U1-5), plus the 12
   A3 names the mirror lacks. Persisted dues / payments go in bundle 25 only if the listing is back before
   the build. Otherwise they go in the next A3 bundle, and bundle 25 stays without catalog edits. Any catalog
   edit is compared with `workplace_reference.md` first, and UAT lists the top-level keys before and after
   the apply.
4. **Workplace grep** (UAT, before the apply) for every removed or moved public symbol:
   - `_common.lookback_floor`; `pit_latest(` with `anchor=`; `cc_raw_extract.nodes.build_cc_acct_windows`;
     `PRODUCT_TYPES`;
   - `a3_credibility.sources.build_promise_events` / `EVENTS`; `a3_credibility.constants.CYCLE_MAX_DAYS` /
     `FLOOR_LOOKBACK_DAYS` / `BUCKET08_BASELINE_MONTHS` / `DEADLINES` / `FOLLOWUP_RUN_DAYS` /
     `MATCH_DAYS` / `STATEMENT_FALLBACK_D`;
   - `_with_next_month`, the old A1 threshold constants;
   - in the same grep, the Q-R-01 dead-code names and the two CASA features of Q-R-07.

   A hit in a workplace test module goes on the Sonnet's test list. A hit in a non-test module holds the
   build.
5. **Build mechanics.**
   - Rebase onto the workplace-equivalent head (`refactor/a1_products` `4536d52` plus handoff 8 `cf84f89`
     as mirrored) and re-run every gate.
   - `--exclude` `_dcore_codes.py` and other sessions' files; read the manifest.
   - No registry edit.
   - The UAT `MERGED` review names `cc_raw_extract/nodes.py` explicitly (E2).
   - The UAT step prints `pyspark.__version__` (`F.aggregate` with a Python lambda, `arrays_zip`).
   - S7 group A is not in bundle 25.
6. After the check is back: update the A1 workbook text to the new thresholds (Q-S6-22), outside the bundle.

## New issues

N-1 [`a3_credibility/promises.py` `_judged`] The early-end test rounds "paid since start" to the cent
(Q-S6-17 fix), but the outcome test `paid >= promise_amount` compares an unrounded double sum. A sum of
several payments equal to the amount can read `partial` while the fold treated the event as paid in full.
Comparing at the cent (`F.round(paid, 2) >= amount`) is a behaviour change to a D-A3-25 comparison, so it is
for the user. It fits inside A3-1, which is not yet in PROD, and its check absorbs it. The older `>=` money
comparisons (Dimension B qualifying, Dimension C paid-as-billed) are a separate, later L. → user (Master
adds it to `questions.md` §C)

N-2 [`a3_credibility/pipeline.py` `create_a3_pipeline`] Exactly 15 locals after S4-04: the next A3 input
will trip pylint R0914. Not for now. Whoever adds the next A3 dataset should fold the DCORE source names
into a dict rather than add a local or a disable. → note for the next A3 bundle
