# Questions for the user (round 1)

25 entries. They cover the 25 questions of S1 (4), S2 (2), S3 (7) and S6 (12): Q-S1-4 and Q-S3-5
ask the same thing as S6-Q05 and are folded into Q-05, and two decisions raised inside S6 handoff
items are added (Q-22 from S6-H02, Q-25 from S6-H03). The original id is in brackets; the full text
is in `round_1/proposals/S<k>.md`. None is applied: every answer that asks for a behaviour
change goes to a fix bundle after the matching refactor bundle (PLAN §8).

**Blocks** names what waits for the answer. "none" = the refactor bundles can ship without it.

| Group | Questions | Block a bundle |
|---|---|---|
| Behaviour bugs | Q-01 – Q-04 | A4 fix bundle (Q-01, Q-03, Q-04), shared fix bundle (Q-02) |
| Spec ambiguities / design decisions | Q-05 – Q-22 | A3 bundle (Q-11 – Q-13, Q-20, Q-22), A4 fix bundle (Q-05), S3-04 (Q-15) |
| Process / data | Q-23 – Q-25 | CC A3 standalone run (Q-23), A3 bundle (Q-25) |

## Behaviour bugs

```
Q-01 [A4 · _dpd_journey/history.py:60-64, spark.py (Stage 2 truncation)] (S6-Q01, M) A later unresolvable gap removes the A4 state of earlier spine rows.
Now: the gap cut moves first_month past the gap; spine rows before it get no A4 row (with `drop`, the account loses all rows). | Spec/expected: point-in-time (METHODOLOGY §2, D5/D6): a future gap must not change a past state.
Options: (a) keep, document it (b) resolve the history per spine row (apply only cuts at or before the row's month), in the A4 fix bundle.
Recommendation: (b). | Impact: past persona months only (trend / vintage sheets, A3 anchor); rows of accounts with n_months_truncated > 0 before first_month. Blocks: A4 fix bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-02 [shared · _common.py `_obs_base`, RL path] (S6-Q02, M) RL obs base keeps an arbitrary cif_id (possibly NULL) for a duplicated grain row; CC takes max(cif_id).
Now: dropDuplicates(GRAIN) picks any row. | Spec/expected: CIF-level signals, one rule for CC and RL, deterministic reruns.
Options: (a) keep (b) RL takes max(cif_id) per grain like CC (c) fail loud on >1 non-NULL cif_id.
Recommendation: (b), a no-op on a clean spine. | Impact: rl_spine rows with >1 cif_id per grain (one aggregate in the shared bundle check). Blocks: shared fix bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-03 [A4 CC · cc_a4_deterioration/nodes.py (restructure flag), cc_full_history/nodes.py] (S6-Q03, L) Restructure flag counts an out-of-range first bucket (> 9); an invalid row also wins its date.
Now: earliest non-NULL dlq_bucket >= 4 sets the blind-spot flag, with no 0..9 range; the per-date max keeps a 10+ row. | Spec/expected: the flag means "opened mid-delinquency"; an invalid value is not evidence.
Options: (a) keep (b) apply the engine's validity range in both places.
Recommendation: (b), A4 fix bundle. | Impact: likely tiny; upper bound n_invalid_rows > 0 in crx_cc_dpd_sequences. Blocks: A4 fix bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-04 [A4 RL · rl_a4_deterioration/chains.py:65,72, nodes.py:65-70] (S6-Q04, L) A NULL `known` date or candidate_count on a link row crashes resolve_chains or silently disables the before-chain rule.
Now: Python max() over NULLs: TypeError, or chain_known_date NULL. | Spec/expected: D6 (later of flag and closure); D2 fail loud naming the table.
Options: (a) keep (b) ValueError naming int_loan_restructure_link (c) NULL known = row stays on own history.
Recommendation: (b). | Impact: 0 rows in PROD today; protects a link refresh. Blocks: A4 fix bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

## Spec ambiguities / design decisions

```
Q-05 [A4 grain · cc_a4_deterioration/nodes.py, rl_a4_deterioration/nodes.py] (S6-Q05, M; same issue as Q-S1-4 and Q-S3-5) A4 is keyed on the raw spines (CC mid-month billing dates, RL all months, long vs string account_id), not the obs base A1/A2/A3 use.
Now: an equality join with the obs base matches nothing in PROD for CC. | Spec/expected: D5 "axes keyed via the obs base"; D-A3-2 needs A4 per obs-base row.
Options: (a) keep; consumers join on (account_id, last_day(date)) and cast (b) A4 classifies the obs base (own fix bundle; CC dates change, RL rows outside persona months go) (c) A4 stays on spines, A3 gets its own engine call.
Recommendation: S6: (b) as the A4 bundle's main change; S1 and S3: (a) for this refactor, (b) decided later with the persona master. Round 1 bridges with a same-month lookup (`episode_start`). | Impact: every CC A4 row's date; check = old vs new crosstab on (account_id, last_day). Blocks: A4 fix bundle (and the persona master).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-06 [A2 · a2_locatability/signals.py `build_demographics_deceased`] (S6-Q06, L) Demographics deceased has no point-in-time bound; spec §5 and §9 disagree.
Now: max ft_deceased_flag per CIF over the whole table. | Spec: §5 "max per CIF, death is permanent" vs §9 "latest snapshot on or before the observation date".
Options: (a) keep, amend §9 (b) bound by a snapshot date if the table has one.
Recommendation: (a) unless the table carries a snapshot date. | Impact: past persona months only. Blocks: none (spec text).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-07 [A2 · a2_locatability/signals.py `_location_rule` (L2)] (S6-Q07, L) "1 month" / "3 months" in the travel rule are add_months day offsets (28–31 days), not calendar months.
Now: Spark does not snap month ends (add_months('2026-09-30', -1) = 2026-08-30). | Spec: §3/§7 "at least 1 month", "at most 3 months".
Options: (a) keep, say "same day of month" in §7 (b) calendar months.
Recommendation: (a) unless GRR reads "1 month" as "the observation month". | Impact: a few days; ~3% of L2 rows at most. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-08 [A4 RL · rl_a4_deterioration/nodes.py (restructure flag)] (S6-Q08, L) RL blind-spot flag reads has_restructured_loan_flag from rows after the observation date; CC's is point-in-time.
Options: (a) keep (flag constant per account) (b) read it as of each row's date.
Recommendation: (a) after one aggregate check (first flagged row later than first spine month); B13 suggests 0. | Impact: likely 0 rows. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-09 [A1 · a1_ability/signals.py `_with_next_month`, `_loan_bureau_salary`] (S6-Q09, L) A zero bureau salary does not always end the carry (loan-feature zeros are filtered; a same-month positive pull wins).
Spec: S14 "type 43 gives 0 and ends the carry".
Options: (a) keep, write in S14 that the closure rule is the alert table's only (b) any zero in the month wins.
Recommendation: (a). | Impact: RL CIFs with a closure and a same-month loan pull; ~0. Blocks: none (spec text).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-10 [A1 · a1_ability/signals.py `_require_returns_from`] (S6-Q10, L) Only the returns table has a start-of-coverage guard; a late-starting activity / bounce / salary / CASA feature gives Unknown or no distress silently.
Options: (a) keep (b) same guard on every monthly feature (one new Spark action per source; needs your consent under PLAN rule 6) (c) log only.
Recommendation: (a) for this refactor. | Impact: first W–2W persona months only. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-11 [A3 · _dpd_journey/anchor.py `episode_start` (S1-07)] (Q-S1-1) Which date is the episode anchor?
Now: A3's t0 = first delinquent observation date of the spell; A4 has month indices only, so episode_start = first day of the spell's first month. | Spec: D-A3-2 "latest spell start", no day.
Options: (a) first day of the month (b) last day of that month (c) the exact first delinquent statement date (one more join).
Recommendation: (a). | Impact: DCORE / payment rows in the first episode month; A3 bundle crosstab old t0 vs new anchor. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-12 [A3 · _dpd_journey/anchor.py (S1-07)] (Q-S1-2) Obs-base rows A4 does not score get no anchor (history not ok, outside A4 window, left-censored at the CC floor).
Options: (a) A3 Unknown with reason no_episode (b) fall back to window_start(window_months) (c) fall back to the A4 history's first month.
Recommendation: (a), visible and counted. | Impact: A4 build_status != 'ok' share per model_id. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-13 [A3 · windows] (Q-S1-3; related: S6-H01) Day-based vs calendar-month window bounds in A3.
Now: A3 writes windows as observation_date − N months; the inclusive commitments window (D-A3-9) includes one extra day. | Spec: D-A3-9 [max(spell start, obs − 12 m), obs].
Options: (a) _common.window_start everywhere (calendar months, as A1/A2) (b) keep day arithmetic for commitments.
Recommendation: (a). | Impact: instalments due exactly on that day; tiny. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-14 [A1 · a1_ability/signals.py `build_liquidity_signals`] (Q-S2-1) CASA / card-payment sources are read without a partition floor.
Now: income, distress and EOSB floor with lookback_floor; liquidity scans the three sources' whole history. | Expected: 12 months at most can count.
Options: (a) lookback_floor + month_end filter (+1 small Spark action: needs your consent, PLAN rule 6) (b) pass crx_persona and floor at the persona start (new node input, no action) (c) leave.
Recommendation: (b) if a new node input is acceptable, else (a). | Impact: no rows; PROD scan size of 3 monthly tables. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-15 [Kedro tags · A4 and full-history pipeline.py] (Q-S3-1) Tag sets differ from A1/A2/A3. S3-04 is held on this answer.
Now: A4 [crx, cc|rl, cc_a4_deterioration|rl_a4_deterioration]; full histories [crx, cc|rl, full_history|rl_b1]; A1/A2/A3 [crx_persona, crx, <axis>, <name>, persona_axis].
Options: (a) switch to the A1/A2/A3 set (S3-04) (b) keep the values.
Recommendation: (a), if nobody runs `kedro run --tags cc_a4_deterioration|rl_a4_deterioration|rl_b1`. | Impact: run selection only, no data. Blocks: S3-04 (and the tag part of S3-A3-H1).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-16 [layer rule · cc_full_history/pipeline.py] (Q-S3-3) A tier-L node reads raw_stg_billing.
Options: (a) documented exception until a billing primary exists (b) a prm_billing primary with the parsed bucket.
Recommendation: (a) now, (b) in the A3 shared-layer work. | Impact: none until (b). Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-17 [catalog · catalog_crx.yml] (Q-S3-4) Every entry repeats type / file_format / save_args and the filepath.
Options: (a) leave (b) a YAML anchor + one directory interpolation (−300 lines; needs a PROD check that the loader resolves `<<`). A dataset factory is not an option (memory-only outputs would persist).
Recommendation: (a). | Impact: names and paths unchanged either way. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-18 [layering · _common.py, _dpd_journey] (Q-S3-6) `_common` imported `_dpd_journey.constants`, so the A4 engine could not use shared helpers.
Status: resolved by the round-1 merge (S1-01: MODEL_ID_SEGMENT and `segment()` live in `_common`; A4 now imports `_common`). Left here for the record.
Recommendation: no answer needed; the inline missing-column check in build_dpd_sequences can move to require_columns in round 2 (error text changes). | Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-19 [obs base · _common.py `_obs_base`] (Q-S2-2) The month-end guard is a Spark action (limit(1).count()).
Options: (a) keep (b) in-plan raise_error (no job; exception type changes from ValueError, tests need an update).
Recommendation: (a). | Impact: none. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-20 [A3 · cc_a3_payment_credibility/nodes.py:104-196] (Q-S3-7) A3 schema guards (dcore_feat_ptp, dcore_feat_settlement, observation spine) null the signals instead of failing.
Options: (a) keep (PROD-tolerant) (b) require_columns, explicit optional input for sources not in PROD.
Recommendation: (b) in the A3 rebuild, for the sources in PROD today. | Impact: a PROD run with a missing column stops instead of producing Unknown. Blocks: A3 bundle (handoff S3-A3-H2).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-21 [shared keys · _common.py `_obs_base`, a2_locatability/signals.py] (S6-Q11, L) Join keys are normalised differently (plain cast("string") vs string_key; cif_id cast in A1, not in A2; DCORE account_id uncast).
Options: (a) keep (b) one key helper (`_common.string_key`, now shared) on every axis, proven by the golden harness.
Recommendation: (b) as a round-2 refactor; flag any type where it would change a value. | Impact: none expected; protects a source type change. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-22 [A3 · DCORE window] (S6-H02 question) A3 reads DCORE `< observation_date`; A2 and the A1 EOSB diagnostic read `<=`. Was the exclusive bound intended?
Options: (a) inclusive on both axes (as A2), stated in D-A3-2 (b) keep exclusive for A3.
Recommendation: (a). | Impact: events on the last day of each month. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

## Process / data

```
Q-23 [catalog · catalog_crx.yml, cc_raw_extract/pipeline.py] (Q-S3-2) crx_cc_billing and crx_cc_acct_windows have no catalog entry, but CC A3 reads crx_cc_billing (the baseline smoke FAIL).
Options: (a) the workplace catalog has the entries; mirror them (b) add them in the A3 bundle.
Recommendation: check the workplace catalog first. | Impact: CC A3 cannot run standalone. Blocks: CC A3 standalone run (smoke gate stays at its baseline failure until then).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-24 [A2 · _dcore_codes.py RIGHT_PARTY_CONTACT (tier X)] (S6-Q12, L) Some right-party names may not be the account holder (KSA/CONNECT AND DROP, KSA/CALLBACK, DEMAND FOR HUMAN AGENT, E MAIL RECEIVED, FIELD VISIT DONE / REJECTED, NEW SECURITY CHEQUE COLLECTED, POST DATED CHEQUE AVAILABLE); each makes a row Reachable and breaks a gone-dark streak.
Options: (a) keep (b) a PROD aggregate (Sonnet prompt): per name, the share of rows where it is the only contact in W; drop the ones that decide many rows.
Recommendation: (b) only if the A2 report shows a large Reachable share decided by them. | Impact: unknown. Blocks: none.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-25 [A4 → A3 · _dpd_journey/core.py (months_before_spell)] (S6-H03, M; handoff item with a decision) The A4 anchor on cropped histories that start delinquent is the first kept month, not the real spell start.
Options: (a) A3 treats the anchor as unknown for history_cropped & starts_delinquent (Dimension C no_record flagged "censored", windows from the observation lookback only) (b) use it as is.
Recommendation: (a), counted separately in D-A3-10; needs Q-05 settled first. | Impact: A4 unknown rows (large at 180+) and CC spells that began before 2024-01. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

## Added at round 1 triage (R-O)

```
Q-26 [A1, A4 outputs · a1_ability/classify.py `build_a1_ability`, _dpd_journey/states.py `assign_state`] (R-I N-16) A1 and A4 outputs carry no column saying which rule decided the state; A2 has `location_rule`.
Now: A1 has `a1_unknown_reason` only (Unknown rows); A4 has the state only. An auditor must recompute the rule from the signal columns. | Expected: one `*_rule` idiom on every axis (A2 today, A3 planned).
Options: (a) keep (b) add `a1_rule` (S-id of the points / distress / unknown path) and `det_rule` (Q0–Q4) in a fix bundle after the refactor bundles (new output columns: catalog schema, GRR workbook, tests change) (c) A4 only, since its tree is the hardest to recompute.
Recommendation: (b), designed together with A3's rule column so the four axes match. | Impact: two new columns, no value changes; check = column present and its crosstab with the state. Blocks: none (not refactor work; PLAN §3 rule 1 and 5).
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-27 [shared · _common.py `window_agg(start=)`, A3] (S6-H02, restated for the shared helper) The shared window helper is inclusive at both ends (`start <= date <= observation_date`); A3 today reads DCORE `< observation_date`.
Now: A2, A1 and `window_agg` are inclusive; A3's code is exclusive; D-A3-2 writes `[anchor, observation_date)`. | Expected: one convention for every axis.
Options: (a) inclusive everywhere; D-A3-2 text changed to `[anchor, observation_date]` (b) exclusive for A3 only, as a private filter in A3 (no switch in the shared helper).
Recommendation: (a). The same answer settles Q-22: answer once. | Impact: events on the last day of each month in A3. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-28 [A3 · cc_a3_payment_credibility/nodes.py `_aggregate_disposition` (handoff S2-H-01)] Same-day, same-flag right-party contacts: which disposition wins?
Now: `row_number()` over (date desc, refusal flag) leaves a tie on both undefined (any row; reruns can differ). The handoff's `max(struct(...))` picks the largest disposition string. | Spec: D-A3-19 says a refusal sorts first on the same day; no rule for two non-refusal or two refusal dispositions.
Options: (a) accept the largest string (deterministic, arbitrary) (b) a named priority list of dispositions (c) keep the window as is.
Recommendation: (a) for the A3 bundle, with the tie rule written in D-A3-19; (b) only if GRR names a priority. | Impact: rows with two dispositions of the same kind on the latest contact day; count it in the A3 bundle check. Blocks: A3 bundle (handoff S2-H-01).
Answer: recommendation accepted (user, 2026-11-05).
```

## Added by S1, A3 design-in (between rounds 1 and 2)

From `a3_target_shape.md` §4. Each answer edits one named place in the A3 engine; none changes the
shared layer. Q-20 is answered by the spec ("Open": all A3 sources are required, D2), so the A3
rebuild uses `require_columns` everywhere.

```
Q-29 [A3 · a3_credibility/signals._paid_after (refusal, D-A3-5 / -14 / -20)] What is "a payment of at least 100 AED after the refusal"?
Now: CC sums all card payments after the refusal day and, at 180+ only, compares the sum with 100 AED; RL uses Dimension B's any-payment flag. | Spec: D-A3-5 "a cycle with at least 100 AED"; D-A3-14 RL "total_paid >= 100 in a month after the refusal month"; D-A3-20 "no payment >= 100 AED followed it".
Options: (a) payments dated after the refusal, summed per cycle (CC) / month (RL), one cycle or month >= 100 (b) all payments since the refusal summed, >= 100 (c) one single payment >= 100.
Recommendation: (a), the D-A3-5 unit on both products. | Impact: refusal rows with several small payments after the refusal (4.4% fire today); count in the A3 bundle check. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-30 [A3 · a3_credibility/signals._in_episode, constants.DCORE_MAX_MONTHS] Is the DCORE look-back capped at 180+?
Now: CC reads all follow-up history from t0; RL floors it at persona_start − 24 months (O69, a performance guard). | Spec: D-A3-2 "[anchor, observation_date)" with no cap; at 180+ the anchor can be years back.
Options: (a) no cap; the CC read stays unpruned (b) cap at N months (24 as RL today) for both products, which also gives a literal partition floor from params (no Spark action).
Recommendation: (b) N = 24 if the bundle check shows few latest right-party contacts older than 24 months; otherwise (a). | Impact: 180+ refusals and plans older than N months. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-31 [A3 · a3_credibility/signals._onset_bounds] Where does the onset cycle count, now that the anchor is a month?
Now: the statement dated t0 (the cycle that made the account delinquent) is in neither dimension: Dimension B takes evidence > t0, Dimension C < t0. | Spec: DE sheet row 6 "split at onset"; D-A3-2 says nothing on the boundary cycle.
Options: (a) in neither (Dim B from the month after the episode month, Dim C before it): today's result (b) in Dimension C (it is the last pre-onset payment) (c) in Dimension B.
Recommendation: (a), no change. | Impact: one cycle per row at the boundary. Blocks: A3 bundle.
Answer: recommendation accepted (user, 2026-11-05).
```

```
Q-32 [A3 · node build_crx_<p>_a3_instalments; spec V1 "decide the layer"] Which layer feeds Dimension A?
Now: A3 joins dcore_int_ptp / dcore_int_settlement (intermediate) with dcore_prm_promise_instalments / dcore_prm_settlement_schedule_instalments (primary) in one node, against "one layer per node". | Spec: V1 left the layer open.
Options: (a) an A3 source node that mixes the two (D-A3-18 style, documented exception) (b) a DCORE primary (`dcore_prm_commitment_instalments`: agreement, plan type, plan start, due date, due / paid amount, status) in the DE-owned DCORE pipeline, read by A3.
Recommendation: (b) if the DE can add it; (a) for this bundle otherwise. | Impact: none on values. Blocks: A3 bundle (wiring only).
Answer: recommendation accepted (user, 2026-11-05).
```
