# Round 2 triage = round 3 brief

Input to round 3: HEAD `7ae2a08` (round 2 tree, gates green). R-O's verdict decides (`reviews/R-O.md`,
rulings D-2-3 … D-2-7). Hard rules (PLAN §3) unchanged. Round 3 is the **last** round and is kept
small (user is watching token use).

## Round 2 outcome

- 21 items **keep**, 0 revise, 0 revert. R-E's blocking objection on S1-R2-01 waived (D-2-3).
- Carried over, not done in round 2: triage #6 (A1 ladder thresholds named).
- Convergence **not met**: R-O O1 3.94, O3 3.87, O7 3.60; R-E tier average below 3.5; bundle plan
  incomplete. O1 and O7 are capped by decisions (A4 UDF parity engine signed off; D-2-2 for A1; R-4)
  and will be signed off as recorded exceptions if O3 ≥ 4, R-E ≥ 3.5 and the bundle plan is complete.
- Not cut to sign-off only: two items are audit defects (silent FORCE on a bad override mode; bare A1
  thresholds) and the bundle plan is a sign-off condition.

## Round 3 roster

| Who | Job | Budget |
|---|---|---|
| **S4** (one run; absorbs S1's cross-axis role, since the remaining cross-axis items are declaration names) | the six items below, one commit per axis (shared / A4 / A2 / A1), gates per PLAN §6 | tier L net **≤ +10** lines; any item over its own budget is dropped, not trimmed elsewhere |
| **Master** | gates; the bundle plan (below); handoff text | no code |
| **R-E, R-I** | **delta review only**: the round 3 diff, a rescore of the files it touches, and their tier average (unchanged files keep their round 2 / round 1 scores). No new issues except blocking ones | short |
| **R-O** | final review + sign-off section | — |

S1, S2, S3, S5, S6, S7: not run. S4 writes its own comment text (no S5 pass).

## S4 items (round 3)

| # | File | Change | Budget |
|---|---|---|---|
| 1 | `scoring_engine.py:78-88` | Mode lookup that raises on an unknown mode: `{DEMOTE: …, CAP: …, FORCE: to}[o.mode]` (no `.get` default). Rung indices named from `RUNGS` instead of the digits `2` / `1` in `rung` and the label loop. No split of `score` (D-2-7) | ≤ +1 |
| 2 | `a1_ability/classify.py:135-142` | `HIGH_FROM = 4`, `MODERATE_FROM = 2` as module constants citing S3 (round 2 triage #6); `SCORECARD` uses them; one comment line on the identity `labels` map (state ids = rung names; display text is `DISPLAY_NAMES`). Update the spec cell of `specs/A1_ability_spec.md` if it names the literal | ≤ +3 |
| 3 | `a1_ability/classify.py` `build_a1_ability` | one comment: the `signals` join order follows the node inputs and does not affect the output (left joins on `GRAIN`, distinct columns) (R-E N-R2-4) | ≤ +1 |
| 4 | `_dpd_journey/spark.py` | one-line contract comment on each `_udf` closure (columns in, struct out); first docstring line of each `build_*` names its stage order (R-I R3-3). No code change | ≤ +4 |
| 5 | `a2_locatability/signals.py` | `_reachable(w_start)` for the D-A2-7 contact rule beside `_gone_dark`; `reachability_state` reads `when(_gone_dark…).when(_reachable…)`. No `_last_call_days` | ≤ +3 |
| 6 | `rl_a4_deterioration/nodes.py` `_original_loan_months`; `_dpd_journey/anchor.py:41` | generator unpack → two plain lines (R-I R3-5); reword the arithmetic comment to "months from the episode's first month to the row's month, counted back from the history end" (R-I R3-6) | ≤ +1 |

Rules for S4: no `black -C` outside the lines these items touch (D-2-4); no A1 rule-line edits beyond
items 2–3 (D-2-2); golden + all three spec tests after each commit; list any renamed symbol (none
expected; `HIGH_FROM` / `MODERATE_FROM` are new).

## Master (no agent)

1. **A3 text** (`a3_target_shape.md` §5): name the three points maps (`COMMITMENT_POINTS`,
   `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS`, each with its D-A3-16 row), `HIGH_FROM` / `MODERATE_FROM` as
   A1, label map `DISPLAY_NAMES`; "Dim A / B / C" comment on the dimensions.
2. **Bundle plan (PLAN §8), a sign-off condition.** For bundles 1–4: base, slug, `--exclude` set
   (`_dcore_codes.py`, A3 modules, other-axis work), the renamed / removed public symbols (S1 and S4
   round 1–3 logs), and the PROD check. Carry in:
   - shared bundle: `kedro registry list`, obs-base runs, and the `string_key` site check (one aggregate
     per key: `sum(cast(k as string) != trim(cast(k as string)))` and the type; R-I R3-7);
   - A4 bundle: 0-diff crosstab; notes: S1-06 log format change, `build_dpd_sequences` error text,
     removed tags (`cc`, `rl`, `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`), `--tags
     full_history` now selects both histories;
   - A2 bundle: 0-diff crosstab, N-3 safety measurement (`_attempt` share, spill), N-4 key counts and
     broadcast size with the drop-the-hint rule, `pyspark.__version__` printed in the UAT apply step
     (D-2-6);
   - A1 bundle (with or before the redesign): 0-diff crosstab, N-4 as A2; brief carries D-2-5
     (`lookback_floor` → `crx_persona` floor, then delete `lookback_floor`) and the D-2-3 check (remove
     CAP / FORCE / the High gate if neither A1 nor A3 uses them by then).
3. Gates on the final commit; `round_3/gates.md`.

## Dropped / logged (not proposed again)

- R-I R3-1 split of `Scorecard.score` (D-2-7).
- R-I R3-4 `_last_call_days`; R-I R3-5 restructure bucket import (R-12) and `_rows_before_chain`.
- R-I N-15 `build_history` split; R-I N-10, N-11 / R-E N-11 (covered by item 2 / N-R2-3).
- R-E N-R2-2 (waived, D-2-3); N-R2-3 (no action, recheck in the A3 bundle).
- R-E N-R2-1 moves to the A1 redesign bundle (D-2-5), not dropped.

## Sign-off conditions for round 3 (R-O)

Gates green and golden identical on the final commit; no blocking objection; R-O O3 ≥ 4 and O2, O4,
O5, O6 ≥ 4, with O1 and O7 below 4 accepted only as the recorded exceptions above; R-E and R-I tier
averages ≥ 3.5; bundle plan complete; all questions answered in `questions.md`.
