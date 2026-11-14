# Round 2 merge log

Branch `refactor/council_a1_a3`, worktree `.worktrees/council_a1_a3`. Round input: `faa744b` (round 1
merge + behaviour steps D-B-1, oracle re-recorded). Specialists ran one after another on the branch, items
in the brief's order, gates green before each stage commit (`gates.md`). No catalog, parameter, registry,
tier A, `_dcore_codes.py`, oracle or spec-check file was edited.

| Stage | Commit |
|---|---|
| S2 | `9fbc5d1` |
| S3 | `8982a26` |
| S1 | `4690b0f` |
| S4 | `4003afa` |
| S5 | the commit that also adds this file |

Paths below are under `src/enbd_collections/pipelines/crx_persona/` unless they start with `nodes/`.

## S2

| # | Item | Result | Files | Lines +/- | What changed |
|---|---|---|---|---|---|
| 1 | S2-11 | done | `a1_ability/signals.py` | +14 / -13 | `build_cross_product_signals` no longer broadcasts the obs rows. The products are pre-filtered with `scoped(products, obs, "cif_id")` (a broadcast of the distinct obs CIFs, the `_common` pattern R-O named) and the join on `(cif_id, observation_date)` is left to the planner. Same rows: the inner join already dropped every product of another CIF. |
| 1b | promises performance | done | `a3_credibility/promises.py` | +70 / -86 | Dues and payments are each read once per promise day instead of twice. (a) One dues join gives both the next cycle end (cutoff) and the latest known due (promised amount): the range conditions became conditional aggregates over the account's cycles (`min(when(cycle_end > day))`, `max(when(cycle_start <= day and due not null, struct))`), which return exactly what the two range joins returned, NULL included. (b) One payments join up to the day's `promise_cutoff` gives `_paid_before`, `_paid_by` and the start day's `promise_paid_amount` (payments `_after(day)` up to the cutoff). The per-event `_with_paid` join is gone: an event's day, cutoff and amount are its start day's, so its paid amount is that day's figure. (c) The day facts travel through the fold (`_event_starts` returns them), and `_events` takes the start day's terms with `max(when(event_date == event_start, struct))`, so `days` is no longer joined back. Plan: 2 range joins + 1 aggregate on dues -> 1; 2 range joins + 2 aggregates on payments -> 1 + 1. Not done: scoping dues / payments to promise accounts before the joins (the equi part of the join already drops other accounts; a semi-join would add a pass). The event rule is unchanged. |

## S3

| # | Item | Result | Files | Lines +/- | What changed |
|---|---|---|---|---|---|
| 2 | S3-04 | done | `cc_raw_extract/nodes.py` | +1 / -7 | `raw_stg_balance` check lists `contract_idt`, `banking_date`, `edp_load_date` only. |
| 3 | S3-01 | **reverted** | (`_common.py`, `nodes/utils/frames.py`) | 0 | Coded as asked (`frames.require_columns` with `_common`'s wording and column order, `_common` importing it). `checks/a3_engine_spec.py` then fails at import: it stubs `enbd_collections.nodes`, `.nodes.features`, `.nodes.utils` as empty packages (`__path__ = []`) to fake the unmirrored DCORE helpers, so `_common` can no longer import `nodes.utils.frames` there. `golden_inputs.py` has the same stub pattern. Making it pass needs an edit to the spec stub (not forced by a signature, so outside this round's rules). **For the Master:** either allow the stub change (keep the real `enbd_collections.nodes` packages and stub only the two DCORE modules), or keep two copies. |
| 4 | R-E N-3 | **skipped** | `a3_credibility/signals.py` | 0 | There is exactly one episode check per public builder (four: commitments, Dim B, Dim C, contacts), and all four are called directly by `checks/a3_engine_spec.py` with a hand-built episode, which is the case the brief says to keep. R-E's "five" counted the ledger twin. Checking the episode inside `build_a3_episode` would check that function's own output (its columns are `EPISODE` by construction). Kept all four; nothing to remove. |
| 5 | R-O N-1 | done | `a3_credibility/classify.py` | +1 / -1 | Log label `A3 credibility` -> `a3_credibility [<model_id>]`, as A1 (`a1_ability [<model_id>]`) and A2. Log line only. |

## S1

| # | Item | Result | Files | Lines +/- | What changed |
|---|---|---|---|---|---|
| 6 | S1-06 | done | `a1_ability/signals.py` | +4 / -7 | `_with_carry` uses `last_day(add_months(month_end, age))` for every age. Verified: its only input is `feat_cif_bureau_salary_monthly`, whose `month_end` is `F.last_day(salary_month_end)` (a date), so age 0 gives the same date. One comment on the `coalesce`: the newest non-NULL amount wins, a 0 row is a value and hides the older rows. |
| 7 | R-E N-1 | done | `a1_ability/signals.py`, `rl_a1_ability/nodes.py` | +6 / -9 | `_floor` became `a1_ability.signals.persona_floor(crx_persona, months) -> str`; the RL anchor imports it (`F.lit(persona_floor(crx_persona, _LOAN_MAX_AGE_M))`, the same ISO string as before). Kept in the A1 engine, not in `_common`: `_common` importing `nodes.utils.frames` breaks the A3 spec's package stub (item 3). |

## S4

| # | Item | Result | Files | Lines +/- | What changed |
|---|---|---|---|---|---|
| 8 | S4-04 narrowed | done | `a3_credibility/pipeline.py` | +13 / -9 | Locals `commitments`, `dlq`, `pre_dlq`, `contacts` for the four signal outputs typed twice (the brief said three; the contacts table `{p}_strong_negative_signals` is also typed twice). 15 locals, pylint 10.00. |
| 9 | `_contact_summary` | done | `a3_credibility/signals.py` | +10 / -6 | `_SAME_DAY_ORDER = ("refusal", "dispute", "hung_up", "paid", "ptp", "success")`; the struct field is `same_day_rank` (position in that tuple), replacing `later` plus the string order of the labels. Same order as before: refusal lowest (old `later = 0`), then the others in their old string order. `F.array_position` cannot take a column value in the installed PySpark, so the rank is a `when` chain. |
| 10 | Promise floor | done | `a3_credibility/constants.py`, `promises.py` | +3 / 0 (constants) | `PROMISE_MIN_AED = MIN_PAYMENT_AED` (Dimension B section, where `MIN_PAYMENT_AED` is defined), used for the promised-amount floor and the partial test. |
| 11 | `_cutoff` options | done | `a3_credibility/constants.py`, `promises.py` | constants -9 | One table: `promises.CUTOFFS` (deadline -> cutoff from the promise day and the next cycle end) and `DEADLINES = tuple(CUTOFFS)` beside it; `constants.DEADLINES` removed (only promises.py read it), its comment points to `CUTOFFS`. The literal 30 is `constants.PROMISE_DAYS`. The unknown-deadline `ValueError` (same text, same option order) is raised at the top of `build_promise_events`. |
| 11b | readability | done | `a3_credibility/promises.py`, `a1_ability/classify.py` | promises +139 / -146 (with 10, 11), classify +23 / -17 | promises.py: helpers in the order the rule uses them; `build_promise_events` is now promise rows -> day terms (`_with_terms`) -> payments (`_with_payments`) -> fold (`_with_event_start`) -> events (`_events`) -> outcome (`_judged`); `_TERMS` / `_DAY_TERMS` name what a promise day decides; `paid_since_start` in `_event_step`; docstring states the D-A3-28 / -29 terms. classify.py: `_instalment_amount(anchor)` beside `_strong_amount` (F4's other threshold, family rule §2), `_strong_months` takes the anchor, `strong` instead of `floor` in `income_level`, the dated "user 2026-11-14" comment replaced by "family rule §2". No pylint disable added. |

## S5

| # | Item | Result | Files | Lines +/- | What changed |
|---|---|---|---|---|---|
| 12 | docstrings | done | `nodes/primary/products/prm_products.py`, `a3_credibility/signals.py`, `a1_ability/README.md` | +15 / -13 | `_latest_in_month`: "two rows on that day: the larger ``value``". `build_contact_signals`: the same-day rule by `_SAME_DAY_ORDER` and the D-A3-30 refusal wording (a payment that may have come after it). README §1 / §3 / §4: one strong amount max(AED 3,000, 2 × anchor) for income, money in, money out, the balance and assets, `FLOW_SOME` 1,000 for money in and out (was 1,000 / 1 ×, 3,000 / 1 ×, 10,000 / 3 ×, 500); the instalment threshold max(1,000, 1 ×) unchanged. Module docstrings and the A3 pipeline diagram checked: still true. AST of the two .py files equal to S4 apart from docstrings. |

## For the Master / owner reviewer

1. **S3-01 is blocked by the A3 spec's package stub** (item 3): allow a stub change in `checks/a3_engine_spec.py`
   (and check `golden_inputs.py`'s stub), or drop S3-01.
2. **R-E N-3 skipped** (item 4): the four episode checks are one per public builder and each builder is called
   by the spec test without the episode node.
3. Item 1b relies on two equivalences the oracle confirms on its data: conditional aggregates over the account's
   cycles = the old range joins, and the event's paid amount = its start day's. Sums of doubles are taken over
   the same rows, possibly in a different order; PROD zero-difference on `promise_paid_amount` is expected but
   a last-digit float difference is theoretically possible.
4. Item 11 moved `DEADLINES` from `constants.py` to `promises.py` (next to the cutoffs, as asked). If R-O prefers
   all A3 settings in `constants.py`, the alternative is lambdas in `constants.py` (Spark imports there).
