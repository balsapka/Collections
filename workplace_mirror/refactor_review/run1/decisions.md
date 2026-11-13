# Decisions

Format: `D-<round>-<n> | what | why | who decided | proposal ids`

## Round 1

D-1-1 | Merge S7 in full: apply `S7.patch` and the 12-file delete list (tier D, 7,028 lines), move `build_rl_depart_spine` unchanged into `rl_a4_spine/nodes.py`, delete the dead tier-L symbols (`parse_yyyymmdd`, `priority_reason`, `SEGMENTS`) | tier D confirmed dead by import and dataset search; the move must precede deleting `cc_departure_signature` (PLAN §2) | Master | S7

D-1-2 | Merge S1-01, 03, 02, 04, 05, 06, 07, 08 from S1's combined diff in its order; S1-07 (`episode_start`) and S1-08 (`window_agg(start=)`) go in now although no tier-L pipeline calls them yet; S1-06's A4 log text change is recorded under "PROD log changes" | PLAN §2 asks this refactor to put A3's shared helpers in the shared layer; the reviewers judge them | Master | S1-01 … S1-08

D-1-3 | Merge S3-01, 02, 03, 05, 06, 07; hold S3-04 (tag normalisation) | tags are what the workplace runs with; waits for the user (Q-15 [Q-S3-1]) | Master | S3-01 … S3-07

D-1-4 | Merge S2-01 … S2-07; output column order stays exactly as at baseline: where a change reorders columns, end with a select in the original order | hard rule 1 (identical outputs, columns included) | Master | S2-02 (liquidity select), S2-03 (aggregate order)

D-1-5 | Merge all of S4 re-based onto the S1 helpers, except: drop S4-08 `label_column` (duplicate of S1-04, the earlier stage wins; S4-01/S4-03 use `scoring_engine.state_label`), drop the window-start part of S4-04 (S1-03 did it); S4-01's constant renames update spec cells S2, S4, S10, S12 of `specs/A1_ability_spec.md` in the same commit | merge-order rule; spec cells must name the code's constants | Master | S4-01, S4-04, S4-08

D-1-6 | Re-base S2-03 onto S1-05: `_dcore_days` aggregates the rows of `_common.dcore_account_events` instead of reading followup / agreements itself | both intents survive (one shared DCORE reader for A2/A3; account-day reduction before the observation join); golden and A2 spec unchanged | Master (merge) | S1-05, S2-03

D-1-7 | Skip the DCORE part of S4-04 (`_call_days`, `_last_call_days`); keep its location split and `_cif_rows` | S2-03 (earlier stage) rewrote `build_dcore_signals` as one aggregate; the split's shape no longer exists | Master (merge, overlap rule) | S4-04, S2-03

D-1-8 | Re-base S4-10: `SEG_60_180` / `SEG_180_PLUS` defined in `_common` beside `MODEL_ID_SEGMENT`, not in `_dpd_journey/constants.py` | S1-01 made the shared layer own the segment map; constants in `_dpd_journey` would make `_common` import the engine again (the cycle S1-01 removed) | Master (merge) | S4-10, S1-01

D-1-9 | Revert S4-03 (split of `build_dpd_sequences` / `build_deterioration`, type hints) | gate 2: `_dpd_journey/_dates.py` gains a ruff finding (E501, new 89-char docstring); the rule is revert, not patch; re-submit in round 2 with the line wrapped | Master (gate) | S4-03

D-1-10 | Revert S4-09 (A4 wrapper steps `_original_loan_months`, `_restructure_blind_spot`) | gate 2: `rl_a4_deterioration/nodes.py` gains a ruff finding (E501, new 90-char docstring line); re-submit in round 2 | Master (gate) | S4-09

D-1-11 | Revert S2-06 (CC A4 restructure flag as one aggregate) | gate 2: `cc_a4_deterioration/nodes.py` gains a ruff finding (E501, new 89-char comment); re-submit in round 2 | Master (gate) | S2-06

D-1-12 | S4-05 keeps S2-05's pruning: `_distress_events` takes `since`; S4-09's CC part had been re-based onto S2-06 before both were reverted | earlier stage wins; intent of both kept | Master (merge) | S4-05, S2-05

D-2-1 | Round 2 runs specialists sequentially, each editing the branch directly and committing after the gates, in stage order S1 → S3 → S2 → S4 → S5; no merge agent | items are small and overlap in files; saves the merge pass and avoids parallel Spark load | Master | —
D-2-2 | A1 gets structure only in round 2 (Scorecard rewrite, FAMILIES table, label constants); no line-level polish of A1 rules (A1 redesign in flight) | axis stability (user, 2026-11-05) | Master | R-O triage A1 items
D-2-3 | Keep the full `Scorecard` (CAP, FORCE, High gate, `silent`, `to`); R-E's blocking 3 waived; fix the silent-FORCE default on a bad mode in round 3 | one tested edit of the shared engine for two named callers (A1 redesign families need the High gate and CAP; A3 needs CAP for BROKEN_OVERRIDE and per-dimension `silent`) beats removing and re-adding across two bundles; user asked for one scoring utility | R-O | S1-R2-01, R-E N-R2-2
D-2-4 | `black -C` compaction allowed: only in files a bundle changes anyway, not in A1 files before the A1 redesign bundle, never repo-wide; line counts include it (R-E's −14 recorded) | plain `black` in the workplace keeps joined calls joined, so no three-way-merge churn; the hunks are in signed-off A4 files | R-O | S4 line target
D-2-5 | `lookback_floor` → `crx_persona` param floor moves to the A1 redesign bundle; delete `lookback_floor` there | its four callers are A1; the change adds node inputs to a moving axis (D-2-2); keeping a decided action breaks no rule (PLAN §3.6 bans new ones) | R-O | R-E N-R2-1
D-2-6 | Keep `F.forall` in the A2 DCORE rule; the A2 UAT apply step prints `pyspark.__version__` | the workplace already runs ≥ 3.3 in PROD (`unionByName(allowMissingColumns)`, `DataFrame.withColumns` in transcribed code); the `array_contains` form is a double negative | R-O | S2 N-3
D-2-7 | Round 3 = S4 only (≤ +10 lines: Scorecard mode/rungs, A1 `HIGH_FROM`/`MODERATE_FROM` + labels comment, `**signals` order comment, `spark.py` closure contracts, A2 `_reachable`, RL generator unpack + anchor comment) + Master bundle plan + delta reviews; dropped: `score` split, `_last_call_days`, bucket import, `_rows_before_chain`, `build_history` split, N-10/N-11 | small final round (user); rule lines get names, mechanism stays | R-O | R-I R3-1…R3-7, R-E N-R2-2…4
D-2-8 | Round 2: 21 keep, 0 revise, 0 revert; convergence not met (R-O O1 3.94, O3 3.87, O7 3.60; R-E < 3.5; bundle plan); O1 and O7 will be signed off as recorded exceptions (A4 UDF parity engine, D-2-2, R-4) if O3 ≥ 4, R-E ≥ 3.5 and the bundle plan is complete | raising O1/O7 further needs edits to signed-off or moving code, which bundle risk ranks above my score | R-O | round 2

## Round 3

D-3-1 | Round 3: 6 items keep, 0 revise, 0 revert; `_reachable` (R3-4) kept although +4 against its ≤ +3 item budget; `MOD` / `MODERATE_FROM` spelling left as is | the extra line is a black-mandated blank line and the round total is +10, at budget; the line encodes a signed-off rule (D-A2-7), so R-I wins over R-E's single-caller score; renaming a shared-engine symbol for spelling is churn | R-O | S4 R3-1 … R3-6
D-3-2 | Accept `BUNDLE_PLAN.md` (R-A dead code, then R-B one refactor bundle with a 0-diff RF check per axis, A4 → A2 → A1) in place of the four-bundle sketch; build conditions: C1 pin `98e0338` to a named branch; C2 rollback = revert the whole R-B apply, step 8 only after all RF checks show 0 differing rows; C3 `RF KEYS` also on `cc_180_plus`; C4 whichever of R-B / A1 redesign / A3 lands second rebases and re-runs every gate, bundle 13 cleanup confirmed first; Master fixes `a3_handoff.md` lines 11-12 (`StateLadder`) | the couplings (Scorecard in A1, reversed `_common` → `_dpd_journey` import, A2 on shared helpers) mean four bundles would ship trees the golden harness never ran; per-axis checks keep the isolation | R-O | BUNDLE_PLAN
D-3-3 | Sign-off: **signed off with recorded exceptions** E1–E4 (D-3-4 … D-3-7) on code `aed15fd` | gates green, golden identical, no blocking objection, R-O O2–O6 ≥ 4 (O3 4.14), R-I 3.99, bundle plan complete, all questions answered; the remaining gaps are capped by decisions, not defects | R-O | round 3
D-3-4 | Exception E1: R-O O1 3.94 < 4 | `spark.py` per-row Python UDFs are the signed-off A4 parity engine; rewriting is bundle risk on signed-off code. Clears when the A4 fix bundle (Q-01, Q-05) is scored and `spark.py` reaches O1 4; meanwhile the R-B A4 check logs stage run time per model_id | R-O | D-2-8
D-3-5 | Exception E2: R-O O7 3.69 < 4 | A1 builders frozen until the A1 redesign (D-2-2); A4 engine functions and `Scorecard.score` kept whole (R-4, D-2-7). Clears with the A1 redesign bundle, then the A4 fix bundle and the D-2-3 check | R-O | D-2-8
D-3-6 | Exception E3: R-E tier average 3.41 < 3.5 | structural: +204 tier-L lines for A3 design-in and Scorecard modes with no caller yet; R-E does not object. Clears at the A3 bundle (first callers) and the A1 redesign bundle (D-2-3 mode removal check, D-2-5 `lookback_floor` deletion); R-E re-scores at the post-A3 pass | R-O | R-E round 3
D-3-7 | Exception E4: smoke gate at its baseline failure (`crx_cc_billing`) | present at baseline, not a regression (Q-23). Clears with the Q-23 workplace catalog check and a CC A3 standalone run | R-O | Q-23
