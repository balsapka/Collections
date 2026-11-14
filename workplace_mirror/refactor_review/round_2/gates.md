# Round 2 gates

Run from `workplace_mirror/` after each stage, one Spark job at a time (`JAVA_HOME=/opt/homebrew/opt/openjdk@17`,
same machine and tools as round 1). Lint baselines were taken on `faa744b` for every file the round could touch;
ruff and pylint compare each changed file with its own `faa744b` copy. The oracle was never run with `--record`;
`refactor_golden.py`, `golden_inputs.py` and the spec checks are unchanged.

## Summary

| Gate | S2 (`9fbc5d1`) | S3 (`8982a26`) | S1 (`4690b0f`) | S4 (`4003afa`) | S5 (final) |
|---|---|---|---|---|---|
| a. py_compile | pass (2 files) | pass (2) | pass (2) | pass (5) | pass (2) |
| a. black -l 88 | pass | pass | pass | pass | pass |
| a. ruff F,E,W,I,B,SIM,UP | no new finding | no new | no new | no new; `a3_credibility/pipeline.py` 3 -> 1 | no new |
| a. pylint | 10.00 both | `classify.py` 10.00; `cc_raw_extract/nodes.py` 7.87, baseline messages only | 10.00 both | 10.00 all five (`create_a3_pipeline` 15 locals, no R0914) | `signals.py` 10.00; `prm_products.py` 7.22, baseline messages only |
| b. A1 spec | 91/91 | 91/91 | 91/91 | 91/91 | 91/91 |
| b. A3 spec | all checks pass | pass (after the S3-01 revert) | pass | pass | pass |
| b. A2 spec | not needed | 36/36 | not needed | not needed | 36/36 |
| b. A4 chain spec | not needed | pass | not needed | not needed | pass |
| c. oracle | **pass**, 188 datasets, 207 s | pass, 188, 203 s | pass, 188, 203 s | pass, 188, 202 s | pass, 188, 208 s |
| d. smoke | the 6 baseline lines | same 6 | same 6 | same 6 | same 6 |
| e. grep rules | pass | pass | pass | pass | pass |

S5 is docstrings / comments / README only: AST of the two changed .py files equal to S4 apart from docstrings; A2 and A4 ran because `prm_products.py` is outside A1 / A3.

Failures on the way (both reverted or fixed before the stage commit):

- S3: with S3-01 applied, `checks/a3_engine_spec.py` failed at import (`No module named
  'enbd_collections.nodes.utils.frames'`): the spec stubs `enbd_collections.nodes*` as empty packages. S3-01
  reverted; gates re-run green (the row above).
- S4: the first `_contact_summary` version used `F.array_position(array, column)`; the installed PySpark takes
  only a literal value there (`NOT_ITERABLE`), so the A3 spec and the oracle failed. My slip: rewritten as a
  `when` chain (same ranks), gates re-run green.

Per file, ruff `faa744b` -> final: `a1_ability/signals.py` 0 -> 0, `a1_ability/classify.py` 0 -> 0,
`a3_credibility/promises.py` 0 -> 0, `constants.py` 0 -> 0, `signals.py` 0 -> 0, `classify.py` 0 -> 0,
`pipeline.py` 3 -> 1, `cc_raw_extract/nodes.py` 1 -> 1, `rl_a1_ability/nodes.py` 0 -> 0, `prm_products.py` 1 -> 1.
Pylint baseline message sets kept (D-1-2 files): `cc_raw_extract/nodes.py` {E0401, E0611}, `prm_products.py`
{E0401, E0611}; `a3_credibility/sources.py` not touched.

## Gate d: smoke (every stage, identical)

The six `cc_raw_extract` lines of round 1 (`EDP_LOAD_DATE_BUFFER_MONTHS` missing from the mirror's `config`):
four import failures, `crx_cc_raw_extract: empty pipeline`, `mirrored module stubbed`.

## Gate e: grep rules (lines added vs `faa744b`)

`spark.read` 0, hard-coded model_id 0, `.count()` / `.collect()` 0 added. No `node(` call added or changed (the
A3 `step()` helper still passes all five keywords). No `raw_` / `stg_` input added (the only touched `raw_` line
is S3-04's shorter `raw_stg_balance` check). No `conf/`, `pipeline_registry.py`, tier A, `_dcore_codes.py` or
check-script file changed.

## For the test owner: changes since `d24114a`

Round 1's list (`round_1/gates.md`) still holds, with these updates. Paths under
`src/enbd_collections/pipelines/crx_persona/` unless they start with `nodes/`.

### Behaviour steps (`8b3d969`, `faa744b`, D-B-1)

Removed
- `a3_credibility/promises.py`: `_followup_promises`, `_consolidate`, `_run_step`, `_no_runs` (the 7-day chaining
  and plan matching)
- `a3_credibility/constants.py`: `FOLLOWUP_RUN_DAYS`, `MATCH_DAYS`
- `a1_ability/classify.py`: `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`, `FLOW_FLOOR`, `FLOW_ANCHOR_MULT`,
  `BALANCE_FLOOR`, `BALANCE_ANCHOR_MULT`, `ASSET_FLOOR`, `ASSET_ANCHOR_MULT`, `MONEY_IN_SOME`, `MONEY_OUT_SOME`

Added
- `a3_credibility/promises.py`: `_promise_rows`, `_event_step`, `_no_event`, `_events`, `_after`
- `a1_ability/classify.py`: `STRONG_FLOOR`, `STRONG_ANCHOR_MULT`, `FLOW_SOME`, `_strong_amount`

### Round 2

Removed / renamed
- `a3_credibility/promises.py`: `_cutoff(events, dues, deadline)` -> the table `CUTOFFS` (deadline -> function of
  the promise day and the next cycle end) and `_next_statement(day, next_cycle_end)`; `_with_due(events, dues)` ->
  `_with_terms(days, dues, deadline)` (adds `promise_cutoff` and `promise_amount` in one pass);
  `_with_paid_by(days, payments)` and `_with_paid(events, payments)` -> `_with_payments(days, payments)` (adds
  `_paid_before`, `_paid_by`, `promise_paid_amount`); `_event_starts(days)` -> `_with_event_start(days)` (now also
  carries the day terms); `_events(rows, starts)` -> `_events(promises, days)` (also returns `promise_cutoff`,
  `promise_amount`, `promise_paid_amount`)
- `a3_credibility/constants.py`: `DEADLINES` moved to `a3_credibility/promises.py` (`DEADLINES = tuple(CUTOFFS)`,
  same values and order)
- `a1_ability/signals.py`: `_floor(crx_persona, months)` -> `persona_floor(crx_persona, months)` (public; the RL
  anchor imports it)
- `a1_ability/classify.py`: `_strong_months(prefix, floor, w)` -> `_strong_months(prefix, anchor, w)`

Added
- `a3_credibility/promises.py`: `CUTOFFS`, `DEADLINES`, `_TERMS`, `_DAY_TERMS`, `_next_statement`, `_judged`
- `a3_credibility/constants.py`: `PROMISE_DAYS` (30), `PROMISE_MIN_AED` (= `MIN_PAYMENT_AED`)
- `a3_credibility/signals.py`: `_SAME_DAY_ORDER`
- `a1_ability/classify.py`: `_instalment_amount`

Changed log and error texts
- A3 state log label: `A3 credibility` -> `a3_credibility [<model_id>]` (the line `<label> — a3_state, month of
  <date> (n=...)`).
- Unknown promise deadline: the same `ValueError` text (`promise deadline must be one of (...), got ...`), now
  raised at the top of `build_promise_events` instead of inside the cutoff step.
- `cc_raw_extract.build_cc_balance`: a `raw_stg_balance` without `account_group_id` or `balance` no longer fails
  at the check (it fails later in the unmirrored `prm_cc` if those are read there).
- No `require_columns` wording change (S3-01 reverted).

Unchanged on purpose
- The four `require_columns(episode, EPISODE, "A3 episode")` checks (R-E N-3 skipped).
