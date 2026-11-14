# R-O (Owner), round 1, run 2 (A3 + A1)

Reviewed: `git diff d24114a a6a0b95 -- workplace_mirror/src workplace_mirror/specs` (stages S7 B, S1, S3, S2,
S4, S5), the proposals, `merge_log.md`, `gates.md`, `questions.md` §B, `decisions.md`, run 1's decisions and
FINAL_REPORT §3–4. Frozen rubric: `rubrics/owner.md`. I read "O5 Fits A3 easily" as "fits the pending A3 / A1
rule changes" (promise points, deadline, 180+ cut-offs, RL dispute codes, A1 bureau carry and closure rule).
I did not read R-E.md or R-I.md. Gates were run by the Master (all green); I ran nothing.

Overall: a good round. A3 now has the target shape (sources, promises, signals, classify, constants holding
every threshold with its D-A3 ID), A1 lost four Spark actions, and the code that bundle 25's follow-ups will
rewrite (promise points / deadline in `promises.py`, the carry in `_with_carry` + `BUREAU_CARRY_MONTHS`) each
sits in one place. Two items need a revise before bundle 25 is built: **S2-11** (an explicit broadcast of the
whole obs base on the 180+ books) and **S3-04** (a required-columns check on columns that only the unmirrored
`prm_cc` reads). One more is a docstring fix (S2-10 tie rule).

## Proposals

### Applied

S7 B-01: accept (blocking: no) criteria: O7, O2
  An unused constant. Listed for the test owner.

S7 B-02: accept (blocking: no) criteria: O7, O5
  `pit_latest(anchor=)` had no caller. A3 gets its anchor from `episode_start`, not from this hook, so O5 loses
  nothing. The mirror cannot see workplace-only callers: add `pit_latest(anchor=` to the workplace grep (N-2).

S7 B-03: accept (blocking: no) criteria: O7
  A dead `None` branch. The 24-month cap stays a named constant (`DCORE_MAX_MONTHS`, Q-30).

S7 B-05: accept (blocking: no) criteria: O3
  README now names the real constant.

S1-01: accept (blocking: no) criteria: O1, O4, O5
  This closes run 1 D-2-5 as planned (four `.first()` jobs per A1 run gone, one floor rule for primaries,
  features and A1). The extra `params:crx_persona` node inputs are params only: no dataset, path or registry
  name changes. The guard difference (Q-R-08) only fires when the obs base has no row in the persona start
  month, and then its message is the honest one. Keep in bundle 25.

S1-02: accept (blocking: no) criteria: O1, O3
  The second `_cutoff` pass is gone. The value is the same, because a follow-up's cutoff depends only on its
  date and a plan's on the plan date. This is the code that Q-S6-01 is about: the user's answer on it may
  change it again in bundle 25's behaviour step.

S1-03: accept (blocking: no) criteria: O3, O5
  The override is resolved in one place. The extension point for the pending deadline decision is one dict
  (`PROMISE_DEADLINE`) plus `DEADLINES`.

S1-04: accept (blocking: no) criteria: O5, O3, O2
  This is the most valuable item for the pending A3 work: points and deadline changes now touch one 262-line
  module. Bundle cost: a new file, plus a move that tests importing from `.sources` must follow. That is
  listed in `gates.md`, and the package `__init__` keeps `build_promise_events` importable.

S1-05: accept (blocking: no) criteria: O3, O5, O2
  The CC read window is now tied to the dimension windows (`HISTORY_MONTHS` derived from them), so a future
  window change cannot leave the extract short. Node name, dataset and pipeline membership are unchanged.
  The import direction (tier K pipeline → CC A3 wrapper) is acceptable: the window is an A3 rule. The
  function move and parameter rename are listed for the tests.

S1-06: accept (blocking: no) criteria: O5, O3
  This is the "one constant" switch the family rule spec promises for the 3-month carry. `_with_carry` with
  `BUREAU_CARRY_MONTHS = 1` is the old coalesce. The closure rule ("> 0 that month only, 0 stops") will need
  a per-row flag, but it lands in this function and nowhere else.

S1-07: accept (blocking: no) criteria: O4, O6
  Same message text as before (frames' format), one helper.

S1-08: accept (blocking: no) criteria: O7
  A one-caller indirection is gone.

S1-09: accept (blocking: no) criteria: O4
  One scoping idiom in the shared layer.

S3-02: accept (blocking: no) criteria: O6, O1
  Rule 4: every A3 builder now fails loud on the tables it receives, naming the dataset. The line growth is
  the allowed kind (`require_columns`). `INSTALMENTS` keeps `due_amount` / `payment_amount` (B-06 held).

S3-04: revise (blocking: yes) criteria: O1, O2, O6
  The transactions and billing checks list only columns the visible code reads: good. The `raw_stg_balance`
  check also requires `account_group_id` and `balance`, and only `prm_cc.derive_billing_amounts` /
  `derive_overdue_buckets` read those. `prm_cc` is not in the mirror, and the oracle runs a stand-in for it
  (`harness_coverage.md`, "Not covered"), so no gate verifies those two names. If either is wrong, bundle 25
  stops a PROD pipeline that runs today: a behaviour change (blocking 1 / 3).
  What to change: drop `account_group_id` and `balance` from the `raw_stg_balance` list (keep
  `contract_idt`, `banking_date`, `edp_load_date`). Alternatively keep them, but only if the UAT step of
  bundle 25 greps `prm_cc.derive_*` and confirms both names before the PROD run. I prefer dropping them: a
  check on columns another module reads belongs in that module.

S3-09: accept (blocking: no) criteria: O6, O4
  Dict inputs, as run 1 R-3 ruled (rename-safe beats line count). Dataset names are unchanged.

S3-10: accept (blocking: no) criteria: O7
  Trivial.

S2-01: accept (blocking: no) criteria: O1, O7
  One pass over the largest A3 input; the same-day tie rule (Q-28) is still readable in the struct order.

S2-02: accept (blocking: no) criteria: O1
  The events subplan is built once. `groupBy(*events.columns)` is safe because the event rows are unique on
  that key (the oracle confirms).

S2-04: accept (blocking: no) criteria: O1
  This is the established broadcast-of-distinct-keys pattern (`scoped`).

S2-05: accept (blocking: no) criteria: O1
  One aggregate and one join fewer, times three consumers.

S2-07: accept (blocking: no) criteria: O1, O4
  This matches `dcore_account_events` (scope first, then broadcast the scoped agreements). The broadcast side
  is the agreements of the base's CIFs. On cc_180_plus that is the largest broadcast in A1, so the bundle
  check should log the EOSB node's run time for cc_180_plus (N-9).

S2-08: accept (blocking: no) criteria: O1
  Broadcast of the distinct refusal accounts: small by construction.

S2-09: accept (blocking: no) criteria: O1, O7
  The episode self-join is gone, and S1-03's resolution is kept.

S2-10: revise (blocking: no) criteria: O1, O3, O2
  Kept (see ruling D-1-3). What to change: `_latest_in_month`'s docstring must state the tie rule ("on a tie
  of ``day``, the largest ``value``"), because that rule is now part of the behaviour a PROD reader may see
  in the check. No code change.

S2-11: revise (blocking: no, but a must-do before bundle 25 is built) criteria: O1
  `F.broadcast(obs)` broadcasts every `(account_id, observation_date, cif_id)` row of the obs base, not
  distinct keys. With `persona_start..end` = 8 months and cc_180_plus at ~300k rows a month, that is ~2.4M
  rows collected on the driver per run. The hint also switches off AQE's own choice. The oracle cannot see
  this.
  What to change: either drop the hint, or pre-filter the products with
  `scoped(products, obs, "cif_id")` (a broadcast of distinct CIFs, the pattern already decided in
  `_common`) and leave the join to the planner. The second keeps the intended gain without the risk.

S4-01: accept (blocking: no) criteria: O7, O3
  Each helper names one D-A3-19/-20 concept; the refusal rule stays in the builder.

S4-02: accept (blocking: no) criteria: O7, O5
  `_with_due` / `_with_paid` are where the pending points (Q-S6-10) and deadline decisions will land.

S4-03: accept (blocking: no) criteria: O6, O7
  The source checks are grouped and the nested plan reader is hoisted; the check block's line growth is the
  allowed kind.

S4-05: accept (blocking: no) criteria: O4
  This follows run 1 R-2 / S4-02 (file-level F401 ignore over `__all__`).

S4-07: accept (blocking: no) criteria: O7, O3
  Two diagnostics get spec-like names and the pylint disables are gone. `labels` comes from `DISPLAY_NAMES`
  keys (same four).

S4-08: accept (blocking: no) criteria: O4, O6
  One home for the product-type contract between feature and consumer.

S4-10: accept (blocking: no) criteria: O7
  The partial re-base is fine.

S4-11: accept (blocking: no) criteria: O7
  One ladder expression.

S4-13: accept (blocking: no) criteria: O7
  Ruff leftovers.

S4-14: accept (blocking: no) criteria: O3, O5
  The D-A3-29 fold now has a name and a typed accumulator. If the user picks Q-S6-01 (b), this is the one
  place to change.

S4-15: accept (blocking: no) criteria: O7
  Builder under 50 lines; the level ladder stays visible.

S5: accept (blocking: no) criteria: O3, O2
  Rule 8 is now met in tier L and in `cc_raw_extract`. The tier K docstring rewrite is larger than I would
  normally allow in a module we only edit "when an A3 proposal needs it" (it is the biggest hunk in the
  bundle, in a file the mirror cannot even import). I accept it anyway: it removes history and wrong
  references, which a hard rule requires, and the file was opened for S1-05 / S3-04. The bundle's UAT step
  must list `cc_raw_extract/nodes.py` under `MERGED` review explicitly (N-7). Q-S5-3: no action unless
  pylint flags it.

### Held, reverted, skipped

S3-01: accept, apply in round 2 (blocking: no) criteria: O4, O6
  One helper, implemented in `frames` (the lower layer) and re-exported by `_common`. Keep `_common`'s wording
  and column order ("is missing required columns [...]"). D2 names `_common.require_columns`, and the
  A1–A4 workplace tests are the likelier ones to assert the text. The feature-layer message text changes
  instead; list it for the test owner. (Q-R-05.)

S3-11: reject / drop (blocking: no) criteria: O7, O2
  +30 lines of window-dependent column lists for a failure that already raises an AnalysisException naming
  the column, on persisted tables written per model_id.

S2-12: drop for bundle 25 (blocking: no) criteria: O2, O1
  This is tier K, the gain is unmeasured, and it also hints the dead `build_cc_limits` windows. Re-raise it
  in the `prm_cc_*` bundle (Q-R-06 (b)), where the extract is rewritten anyway.

S4-06: drop for bundle 25 (blocking: no) criteria: O2, O5
  It sits next to the A1 carry / closure change, which will rewrite this area; take it there.

S4-16: reject (blocking: no) criteria: O2
  This is a rename of a shared-engine symbol across A2 and A4 for wording only: churn for tests and three
  axes. It follows run 1 D-3-1 ("renaming a shared-engine symbol for spelling is churn").

S4-04 (reverted): revise, apply in round 2 narrowed (blocking: no) criteria: O6, O2
  The real gain is rename safety: three signal-output dataset names are typed twice (in the producer and in
  the state node). Round 2: add locals only for those three names (`commitments`, `dlq`, `pre_dlq`,
  `contacts` outputs as needed). That keeps `create_a3_pipeline` under pylint's 15 locals (11 today). Leave
  the remaining E501 dataset strings alone.

S3-03 (skipped): agree with the Master, drop (blocking: no) criteria: O4
  After S1-01, every A1 source node takes `params:crx_persona`; uniformity wins.

S3-07 (skipped): agree, drop. S1-05 made it moot.

S7 A-01 (held for the user): delete once the workplace grep is clean (Q-R-01). My advice: ship it as its own
  bundle after 25, as run 1 did (R-A before R-B), so the dead-code removal and the refactor roll back
  separately.

S7 B-04: keep, option (b) (Q-R-02) criteria: O5, O2
  Run 1 D-2-3 kept the modes for the A1 redesign and A3. Both shipped without using them, but the two cases
  they were kept for are still undecided: A3 promise points / Broken overrides (bundle 25 list) and A1's
  "internal Stable → High" option. Removing them now and re-adding later touches the shared engine twice.
  Re-decide when those two are settled; if neither uses them, remove them in that bundle.

S7 B-06: keep, option (b) (Q-R-03) criteria: O2
  These are output columns of a persisted dataset (hard rule 5), and they are the DCORE promised amounts the
  open promise-amount question (Q-S6-10) may need.

S2-03: option (a), conditional (Q-R-04) criteria: O1, O2
  This is the biggest remaining A3 cost in PROD, and it does not change values. Rule 6 applies: first a UAT
  listing of `crx_*_a3_dues` / `_payments` in the workplace `catalog_crx.yml`. Include it in bundle 25 only if
  that listing is back before the build. Otherwise put it in the next A3 bundle; do not hold bundle 25 for it.

## Files (merged tree)

Weights O1 18 · O2 18 · O3 16 · O4 14 · O5 14 · O6 10 · O7 10.

| File | O1 | O2 | O3 | O4 | O5 | O6 | O7 | Weighted | Note |
|---|---|---|---|---|---|---|---|---|---|
| `a3_credibility/promises.py` (new) | 4 | 4 | 5 | 4 | 5 | 5 | 4 | **4.40** | the pending points / deadline work lands here only; tests must follow the move |
| `a3_credibility/sources.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | product-neutral ledgers, contracts named; pylint dilution only (D-1-2) |
| `a3_credibility/signals.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | one builder per dimension, contact helpers named; 470 lines but straight |
| `a3_credibility/constants.py` | 5 | 4 | 5 | 4 | 5 | 5 | 5 | **4.68** | every threshold with its D-A3 / row id; `HISTORY_MONTHS` derived |
| `a3_credibility/classify.py` | 3 | 4 | 4 | 4 | 4 | 5 | 5 | **4.02** | state log label lacks the model_id, unlike A1 / A2 (N-1) |
| `a3_credibility/pipeline.py` | 5 | 4 | 4 | 4 | 4 | 4 | 4 | **4.18** | three output names typed twice (S4-04 narrowed) |
| `a3_credibility/__init__.py` | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 4.82 | |
| `cc_a3_payment_credibility/nodes.py` | 4 | 3 | 4 | 4 | 4 | 5 | 4 | **3.92** | gains `build_cc_acct_windows` from tier K (move + param rename for tests) |
| `a1_ability/signals.py` | 3 | 3 | 4 | 4 | 5 | 4 | 4 | **3.78** | S2-11 broadcast; many reflow hunks; `crx_persona` keyword-only in 3 builders, positional in CASA |
| `a1_ability/classify.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | diagnostics named; builder still long but one select |
| `a1_ability/pipeline.py` | 5 | 4 | 4 | 5 | 4 | 5 | 4 | **4.42** | still the target shape |
| `rl_a1_ability/nodes.py`, `pipeline.py` | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 4.38 | action gone |
| `cc_a1_ability/nodes.py` | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 4.38 | comment only |
| `scoring_engine.py` | 4 | 5 | 4 | 4 | 4 | 5 | 4 | 4.28 | docstring only; modes kept (B-04) |
| `_common.py` (tier S) | 4 | 4 | 4 | 5 | 4 | 5 | 4 | 4.24 | action gone; removed public symbols need the workplace grep (N-2) |
| `nodes/utils/frames.py` | 5 | 4 | 4 | 3 | 4 | 5 | 5 | 4.24 | second `require_columns` until S3-01 |
| `prm_products.py` | 4 | 3 | 3 | 4 | 4 | 4 | 4 | **3.66** | tie rule unstated and visible in the PROD check (S2-10) |
| `feat_cif_cross_product.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 4.10 | type contract exported |
| `pipelines/products/features.py` | 5 | 4 | 4 | 5 | 4 | 5 | 5 | 4.52 | |
| `feat_cif_bureau_salary_monthly.py` | 4 | 5 | 5 | 4 | 5 | 5 | 5 | 4.68 | docstring names the carry constant |
| `feat_cif_bureau_bounces_monthly.py` | 5 | 4 | 5 | 4 | 4 | 5 | 5 | 4.54 | same message as before |
| `pipelines/bureau/salary_bounces.py` | 5 | 5 | 4 | 5 | 4 | 5 | 5 | 4.70 | |
| `cc_raw_extract/nodes.py` (tier K, O1–O3 only) | 3 | 2 | 4 | – | – | – | – | – | 345-line diff on a module the mirror cannot import; S3-04 revise; pre-existing 3 `.first()` in `prune_by_edp_load_date` |
| `cc_raw_extract/pipeline.py` (tier K) | 4 | 3 | 4 | – | – | – | – | – | dict inputs; imports the window node from CC A3 |

Weighted by lines over tier L, my averages are about: O1 3.9, O2 3.8, O3 4.2, O4 4.1, O5 4.3, O6 4.8, O7 4.3;
overall ≈ 4.15. O1 and O2 are below 4 because of S2-11, S3-04, the S2-10 docstring and the missing bundle
plan. No tier-L file is below 3 on O1–O3.

## Rulings

**D-1-2 (pylint reading): upheld, narrowly.** For a file whose pylint messages are all E0401 / E0611 on
modules the mirror lacks (plus that file's baseline C0411), the gate reads "no new message" instead of "score
≥ baseline". Fewer statements raise the weight of a fixed penalty; reverting S1-04 / S1-05 / S2-10 to
restore that dilution would remove no defect. Conditions: `gates.md` records the exact message set per such
file at baseline, and any message outside it, of any code, fails the gate as before. This is consistent with
run 1's treatment of E0402 as mirror noise.

**D-1-3 (S2-10 tie-break): keep S2-10.** The old `row_number` pick on a tied latest day was arbitrary. A rerun
of the old code could differ from itself, so a 0-diff old-vs-new check on those keys was never reproducible.
The new rule is deterministic and inside the old rule's possible outputs. That is a gain I want in PROD.
Conditions: (1) the docstring states the tie rule (S2-10 revise); (2) the bundle 25 check counts, per
model_id, the `(contract_id, month_end)` keys with two or more rows on the latest day in
`prm_card_month_end`. Any A1 difference must fall only on CIFs holding such a card. A difference elsewhere
fails the check. (3) Q-R-09 goes to the user as (a), with this check.

**Foreseeable R-E vs R-I disputes in this tree (my tie-break, decided now so round 2 does not reopen them):**
- Single-use helpers that name a spec concept stay: `_income_source`, `_salary_stopped` (A1 diagnostics in
  the family rule's words), `_with_due`, `_with_paid`, `_run_step` / `_no_runs` (D-A3-25 / -29),
  `_commitment_counts`, `_contact_summary`, `_plan_after_refusal`, `_require_plan_sources` (allowed
  `require_columns` growth). Helpers that shorten 2+ call sites stay: `_floor` (4), `_history_floor` (2),
  `_load_bound` (2). Nothing in this round is a forwarding-only one-liner worth inlining.
- `HISTORY_MONTHS` as a derived expression, not the literal 13: R-I wins, because it encodes a date bound,
  and the derivation is what keeps the extract wide enough when a window changes.
- Contract lists (`DUES`, `PAYMENTS`, `EPISODE`, `CYCLE_LEDGER`, `INSTALMENTS`, `EVENTS`, `ASSET_TYPES`,
  `CREDIT_TYPES`): keep. They are the named data contracts between nodes (O6), even where used twice.
- `promises.py` as its own module versus folding it back into `sources.py`: keep it separate (O5 beats one
  file fewer).
- Docstrings on private helpers (S5 added one-liners to `_months`, `_count_at_least`, `_base`): accepted,
  because each fixes a NULL meaning or a grain. No more one-liners on helpers whose signature already says
  it.
- Line growth from `require_columns` (S3-02, S4-03): allowed by the scorecard; R-E's line count does not
  block it.

## Questions §B: my recommendation

| Q | Recommendation |
|---|---|
| Q-R-01 | Delete once the workplace grep is clean. Extend that grep to `lookback_floor`, `pit_latest(` with `anchor=`, `cc_raw_extract.nodes import build_cc_acct_windows`, `PRODUCT_TYPES`, and the two CASA features of Q-R-07. Ship as its own bundle after 25. |
| Q-R-02 | (b) keep until promise points and A1 High options are decided. |
| Q-R-03 | (b) keep. |
| Q-R-04 | (a) after the UAT catalog listing; in bundle 25 only if the listing is back before the build. |
| Q-R-05 | (a) one helper (S3-01), `_common`'s wording kept, feature-layer text change listed for tests. |
| Q-R-06 | (a) now; (b) as its own bundle (it also absorbs S2-12 and the three `.first()` of `prune_by_edp_load_date`). |
| Q-R-07 | Add to the Q-R-01 grep; if no reader, stop building them through the Sonnet handoff. |
| Q-R-08 | (a) keep. |
| Q-R-09 | (a) keep, with the tie-key count in the bundle check (D-1-3). |

## S6 findings: advice to the user (inside bundle 25 vs later)

S6 §0 (stale specs) is resolved on the branch: both spec files arrived with the round (`specs/` diff).

Inside bundle 25 (decide before building; none is a council code change):
- **Q-S6-01** (D-A3-29 fold vs plan match): decide first. D-A3-29 is the behaviour step of bundle 25
  itself, so if the answer is (b), the fix and its spec case belong in that same step, not a later bundle.
- **Q-S6-08**: (a), plus the boundary spec cases (cutoff day, 7 vs 8 days, same day two names) in the A3
  spec test. That is a test-only change.
- **Q-S6-02, -12, -13**: (a), each with one spec line. These are look-ahead in history months only; the
  latest scored month is right.
- **Q-S6-07, -09, -16, Q-01**: (a), with spec text lines only.
- **Q-S6-05, -11, -14** (data checks): add the aggregates to the bundle 25 check or one Sonnet prompt run in
  the same PROD window. That is cheaper than a separate round trip, and they do not touch the 0-diff check.

Later:
- **Q-S6-03** (RL anchor at 180+) and **Q-S6-06** (sweepable flag): user decision, fix in the A1 bundle
  that brings the carry / closure change.
- **Q-S6-04**: `casa_handoff.md` item, after the workplace confirms lines 438–487.
- **Q-S6-10**: with the promise-points work.
- **Q-S6-15** (`string_key` across A1): a later A1 refactor. It is not round 2: if a PROD key is a double,
  `string_key` changes the value and the refactor step would no longer be 0-diff, and the oracle's fixture
  types cannot rule that out.

## Round 2 brief (ordered, one specialist after another)

1. **S2**: S2-11 revise: drop `F.broadcast(obs)` in `build_cross_product_signals`, or replace it with
   `scoped(products, obs, "cif_id")`. Gate: oracle.
2. **S3**: S3-04 revise (drop `account_group_id` / `balance` from the `raw_stg_balance` check); S3-01
   (one `require_columns`, `_common` wording); N-1 (A3 state log label with the model_id, listed as a PROD
   log change).
3. **S4**: S4-04 narrowed (locals only for the signal-output names typed twice; stay under 15 locals).
4. **S5**: `_latest_in_month` tie rule (S2-10); docstrings of anything steps 1–3 touched.
5. **Master** (no specialist): the bundle 25 plan. Base and rebase head; `--exclude` (`_dcore_codes.py`,
   other sessions' files). The renamed / moved / removed list from `gates.md` plus round 2's. The check in
   two steps (persisted → D-A3-29, D4 crosstab; D-A3-29 → refactor, 0 differing rows on A3 and A1 for all
   four model_ids), with the S2-10 tie-key split and run times for A1 EOSB / cross-product on cc_180_plus.
   UAT: list `MERGED` files, top-level catalog keys before and after, the extended grep (N-2).

Convergence: yes, I expect my criteria at 4 or above after round 2. O1 rises with S2-11 and S3-04, and O2
with S3-04, the S2-10 docstring and a complete bundle plan. The rest are already at 4 or above. If R-E and
R-I raise nothing new, I see no need for round 3. A tier K exception (cc_raw_extract O2 2) would be recorded,
not fixed: polishing it further only adds bundle risk.

## New issues

N-1 [`a3_credibility/classify.py:89`] The state log label is `"A3 credibility"`; A1 and A2 use
`f"<axis> [{model_id}]"`. A PROD reader of the four model_id runs cannot tell the blocks apart. Use
`f"a3_credibility [{model_id}]"` and list it as a log change. No bundle check parses this block. → S3

N-2 [`_common.py` (removed `lookback_floor`, `pit_latest(anchor=)`), `cc_raw_extract/nodes.py`
(`build_cc_acct_windows` moved), `feat_cif_cross_product.py` (`PRODUCT_TYPES`)] Public symbols removed or
moved in modules that workplace-only code (checks, `tmp_validation`, `casa_windows*`) could import. Add them
to the workplace grep before the apply. An import error at UAT is cheap; one at PROD is not. → Master

N-3 [`a1_ability/signals.py` `build_income_signals`, `build_distress_signals`, `build_eosb_signals` vs
`build_casa_signals`] `crx_persona` is keyword-only in three builders and positional in the fourth. Leave it:
Kedro passes dicts, and changing CASA's signature only costs the workplace tests. List the three new
keyword-only parameters for the test owner (already in `gates.md`). → none

N-4 [`prm_products.py` `_latest_in_month`] The tie rule is unstated (see S2-10). → S5

N-5 [`cc_raw_extract/pipeline.py` tags `"t04c"`] A ticket name used as a run tag. Leave it: tags are what
the workplace selects runs by (run 1 Q-15). → none

N-6 [`cc_raw_extract/_window_utils.py:18-20`] `prune_by_edp_load_date` runs a `.first()` per extract (three
per run). This is pre-existing, tier K, and not for bundle 25; it belongs with Q-R-06 (b). → later bundle

N-7 [bundle 25 UAT] `cc_raw_extract/nodes.py` carries a large docstring rewrite on a file the mirror cannot
import. The UAT step must review it as `MERGED` explicitly and confirm the workplace copy has no local edits
in those docstrings. → Master

N-8 [bundle 25 PROD check] Log stage run times for A1 EOSB and cross-product on cc_180_plus (S2-07 and,
after the revise, S2-11), so a broadcast regression shows in the check, not in a later run. → Master
