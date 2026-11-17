# Round 1 merge log

Branch `refactor/council_a1_a3`, worktree `.worktrees/council_a1_a3`. Source tree before the merge:
`d24114a` (HEAD `c72bf13` had only docs / specs on top). Stage order and decisions: the Master's
brief. One commit per stage, gates green before each commit (`gates.md`). No catalog, parameter,
registry, tier A, `_dcore_codes.py` or oracle file was edited. Later-stage diffs were written
against `d24114a`; "re-based" says what differs from the written diff.

| Stage | Commit |
|---|---|
| 1. S7 group B | `e677655` |
| 2. S1 | `57c8b12` |
| 3. S3 | `8f31ec3` |
| 4. S2 | `c5d4d54` |
| 5. S4 | the commit that also adds this file |

## Stage 1: S7 group B

| Proposal | Result | Files | Reason |
|---|---|---|---|
| B-01 | applied | `feat_cif_cross_product.py` | unused `PRODUCT_TYPES` |
| B-02 | re-based (one line) | `_common.py` | as written, except the new `pit_latest` docstring summary line was 91 chars (E501 +1): "``observation_date``" → "observation date" |
| B-03 | applied | `a3_credibility/signals.py` | dead `max_months=None` branch |
| B-04 | held | — | user question (Scorecard modes, reopens run 1 D-2-3) |
| B-05 | applied | `a1_ability/README.md` | `D_INC` → `INCOME_MAX_FALL` |
| B-06 | held | — | user question (persisted `crx_<p>_a3_instalments` columns) |
| Group A (`S7_A_held.patch`) | held | — | waits for the workplace grep |

## Stage 2: S1

`S1.patch` applied as one set (`git apply --3way`, all hunks clean on top of stage 1).

| Proposal | Result | Files | Reason |
|---|---|---|---|
| S1-01 | applied | `_common.py`, `frames.py`, `a1_ability/{signals,pipeline}.py`, `rl_a1_ability/{nodes,pipeline}.py`, `prm_products.py`, `feat_cif_cross_product.py`, `checks/a1_engine_spec.py` | wins over S2-06; `lookback_floor` gone (−1 Spark action per call, 4 per A1 run) |
| S1-02 | applied | `a3_credibility/sources.py` (now `promises.py`) | cutoff computed once per event date |
| S1-03 | applied | `a3_credibility/{constants,classify}.py` | wins over S3-08 |
| S1-04 | applied | `a3_credibility/{sources,promises,__init__,pipeline}.py` | promise rule in `promises.py` |
| S1-05 | applied | `a3_credibility/constants.py`, `cc_a3_payment_credibility/nodes.py`, `cc_raw_extract/{nodes,pipeline}.py` | `build_cc_acct_windows` moved to the CC wrapper; `HISTORY_MONTHS` |
| S1-06 | applied | `a1_ability/signals.py` | `BUREAU_CARRY_MONTHS` |
| S1-07 | applied | `feat_cif_bureau_bounces_monthly.py` | wins over S3-05 and S4-09 |
| S1-08 | applied | `pipelines/products/features.py` | `_cross_product_node` inlined |
| S1-09 | applied | `_common.py` | `scoped()` in `dcore_account_events` |

Note: the S1-01 edit of `checks/a1_engine_spec.py` (the signature call sites, as the proposal's
diff wrote them) adds one E501 to that check script (114 → 115). The script was never black- or
ruff-clean (baseline: black would reformat it, 114 ruff findings); not reformatted here.

## Stage 3: S3

| Proposal | Result | Files | Reason |
|---|---|---|---|
| S3-01 | held | — | changes the failure text (reviewers rule) |
| S3-02 | re-based | `a3_credibility/{sources,signals,promises}.py` | S1-04 moved `build_promise_events` and `EVENTS` to `promises.py`: its three checks go there (imports `DUES` / `INSTALMENTS` / `PAYMENTS` from `.sources`), `signals.py` imports `EVENTS` from `.promises`; the `build_contact_signals` hunk sits on the post-B-03 code. `INSTALMENTS` keeps `due_amount` / `payment_amount` (B-06 held) |
| S3-03 | skipped | — | after S1-01 all four A1 signal nodes and the RL anchor take `params:crx_persona` (S1-01's `_floor(crx_persona, months)`); changing only the CASA node to `persona_start_date` would break that uniformity, the opposite of the proposal's gain, and re-basing it onto all five nodes rewrites S1-01's interface (earlier stage wins). Master / reviewers may re-raise it as "all A1 nodes take `persona_start_date`" |
| S3-04 | re-based | `cc_raw_extract/nodes.py` | same checks; inserted by hand (the import block and `build_cc_acct_windows` moved in S1-05). `_as_contract_windows` check kept |
| S3-05 | dropped | — | duplicate of S1-07 |
| S3-06 | dropped | — | run 1 ruled a file-level noqa (S4-05) |
| S3-07 | skipped | — | gain gone: S1-05 already replaced the `35` literal with `_history_floor` / `FLOOR_LOOKBACK_DAYS` in the CC wrapper, and `build_cc_acct_windows` no longer lives in `cc_raw_extract` |
| S3-08 | dropped | — | duplicate of S1-03 |
| S3-09 | re-based | `cc_raw_extract/pipeline.py` | dict inputs; the `build_cc_acct_windows` keys follow its post-S1-05 signature (`obs_base`, `deterioration`, `history_floor_date`, not `crx_cc_obs_base` / `crx_cc_a4_deterioration`). The `build_cc_limits` node is converted too (group A held) |
| S3-10 | re-based (partial) | `pipelines/bureau/salary_bounces.py` | the `products/features.py` hunk is S1-08 (already applied); only the `tags` binding in `salary_bounces.py` applied |
| S3-11 | held | — | low value, +30 lines (reviewers rule) |

## Stage 4: S2

| Proposal | Result | Files | Reason |
|---|---|---|---|
| S2-01 | applied | `a3_credibility/signals.py` | as written (clean on the stage 3 tree) |
| S2-02 | re-based | `a3_credibility/promises.py` | written for `sources.py` before S1-02: S1-02 removed the second `_cutoff`, so `events = _consolidate(plans, promises)`; the due / paid fold is the proposal's chain verbatim, starting from that `events` |
| S2-03 | held | — | needs a catalog entry (user question) |
| S2-04 | applied | `a3_credibility/sources.py` | as written |
| S2-05 | applied | `cc_a3_payment_credibility/nodes.py` | as written (clean after S1-05) |
| S2-06 | dropped | — | S1-01 |
| S2-07 | re-based | `a1_ability/signals.py` | written on top of S2-06 (`persona_floor`); the filter line keeps S1-01's `_floor(crx_persona, w)`; `scoped` added to the `_common` import |
| S2-08 | applied | `a3_credibility/signals.py` | as written |
| S2-09 | re-based | `a3_credibility/classify.py` | the `withColumn` keeps S1-03's `promise_deadline(product, model_id, deadline)` |
| S2-10 | re-based (by hand) | `prm_products.py` | the inline diff in `S2.md` is corrupt (hunk line counts); the same edit applied by hand: `_latest_in_month(df, key, day, value)` as a grouped `max(struct)`, `Window` import dropped |
| S2-11 | applied | `a1_ability/signals.py` | as written |
| S2-12 | held | — | not covered by the oracle |

## Stage 5: S4

| Proposal | Result | Files | Reason |
|---|---|---|---|
| S4-01 | re-based | `a3_credibility/signals.py` | S2-01 merged the latest-contact and quiet-after aggregates into one pass, and B-03 removed `max_months`: three helpers instead of four, `_contact_events(episode, followup, agreements)`, `_contact_summary(events)` (S2-01's single aggregate, replaces the proposal's `_latest_contact` + `_quiet_after_contact`), `_plan_after_refusal(refusals, instalments)`; `too-many-locals` disable dropped; S3-02's checks stay in the builder |
| S4-02 | re-based | `a3_credibility/promises.py` | after S2-02 there are no `due` / `paid` side tables to name: the two steps of S2-02's chain become `_with_due(events, dues)` and `_with_paid(events, payments)` (same expressions), the builder reads `judged = _with_paid(_with_due(_consolidate(plans, promises), dues), payments)`; `EVENT_KEY` not added (no longer used); `too-many-locals` disable dropped |
| S4-03 | re-based | `a3_credibility/sources.py` | `_require_plan_sources`, `_plan_instalments`, `_INSTALMENT_FIELDS` as proposed; `_plan_instalments` takes one more argument, `agreement_ids` (S2-04's broadcast `mine` semi-join, now inside the hoisted function) |
| S4-04 | **reverted** | `a3_credibility/pipeline.py` | gate a: pylint `R0914 too-many-locals (20/15)` on `create_a3_pipeline` (score 10.00 → 9.55, below baseline). Not a re-base slip: the proposal's diff applied alone to `d24114a`'s `pipeline.py` gives the same R0914. Outputs were not affected |
| S4-05 | re-based | `a3_credibility/__init__.py`, `a1_ability/__init__.py` | `# ruff: noqa: F401` in both; the A3 import list is S1-04's (with `.promises`); A1 `__all__` removed |
| S4-06 | held | — | next to the pending carry change |
| S4-07 | applied | `a1_ability/classify.py` | as written |
| S4-08 | re-based | `feat_cif_cross_product.py`, `a1_ability/signals.py` | `PRODUCT_TYPES` already gone (B-01); the EOSB `cif_column()` lands in S2-07's `mine` select; three `cif_column()` in all |
| S4-09 | dropped | — | S1-07 |
| S4-10 | re-based (partial) | `prm_products.py` | `frames.history_floor` exists (S1-01, reused, no second helper); only `_window` → `_load_bound(floor)` and its two callers. The proposal's `frames.py` and `feat_cif_cross_product.py` hunks are S1-01's |
| S4-11 | re-based | `cc_a3_payment_credibility/nodes.py` | `billed` reused for `_stagnated`, typed `_nonzero`, `start` / `end` on two lines; the floor line stays S1-05's `_history_floor(history_floor_date)` |
| S4-13 | re-based | `_common.py`, `a1_ability/signals.py`, `cc_a1_ability/nodes.py`, `rl_a1_ability/nodes.py` | UP035 on the post-S1-01 import block (`datetime` already gone); same message re-wrap and two comments |
| S4-14 | re-based | `a3_credibility/promises.py` | `_run_step` / `_no_runs` hoisted; the accumulator carries S1-02's third field (`promise_cutoff` in `firsts`), so its type is `array<struct<event_date,name,promise_cutoff>>` and the docstring says so |
| S4-15 | re-based | `a3_credibility/signals.py` | `_commitment_counts(base, events, lower)` as proposed; S3-02's two checks stay in the builder |
| S4-16 | held | — | rename touching A2 / A4 files (reviewers rule) |

## Not applied, in one list

- held (reviewers / user): S7 B-04, B-06, group A; S3-01, S3-11; S2-03, S2-12; S4-06, S4-16
- dropped as duplicates: S3-05, S3-06, S3-08, S2-06, S4-09
- skipped (gain gone after an earlier stage): S3-03, S3-07; parts of S3-10 and S4-10
- reverted on a gate: S4-04
