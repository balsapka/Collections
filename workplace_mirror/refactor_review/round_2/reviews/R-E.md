# R-E review, run 2 round 2 (efficiency engineer)

Frozen rubric `rubrics/efficiency.md`, blind to R-I and R-O. Input `a6a0b95`; round 2 stages `faa744b..e3bb65e` (the
behaviour steps `8b3d969`, `faa744b` are the user's rules; I scored only their code shape). Gates not re-run.

Measured: round 2 stages alone, `src/` 237 added, 256 deleted, **net -19**; `promises.py` 312 -> 289. Against `d24114a`
(round 1 +65) the tree is roughly +46 `src` lines, with the behaviour steps (new event grouping, one strong amount)
inside that figure; they replaced `_followup_promises`, `_consolidate`, `_run_step`, `_no_runs` and ten A1 constants.
Spark actions: unchanged from round 1 (none added).

## Items

1 S2-11 (`build_cross_product_signals`: `scoped(products, obs, "cif_id")`, planner picks the join): accept (blocking: no)  E2, E4
  Replaces an unbounded `F.broadcast(obs)` of every obs row with the distinct-CIF semi-join the shared layer already
  uses; same rows. Removes the N-4 risk.
1b promises performance: accept (no)  E2 (5), E1
  Dues: two range joins + one aggregate become one left join + one `groupBy` with conditional aggregates (`_with_terms`).
  Payments: two joins + two aggregates become one join up to the day's cutoff giving three sums (`_with_payments`), and
  the per-event `_with_paid` join is gone because an event takes its start day's terms. Passes over the two largest A3
  inputs roughly halve. The shape is the idiomatic one (`F.sum(F.when(...))`).
2 S3-04 (shorter `raw_stg_balance` check): accept (no)  E1
  -6 lines; checks only what the node reads.
3 S3-01 reverted: accept the revert (no)  gate
  Right call: the spec-test stub, not the code, is the obstacle. See open point 1.
4 R-E N-3 skipped: accept (no)  E1
  Fair: each public builder is called directly by the A3 spec with a hand-built episode, so each keeps its own check;
  I miscounted the ledger twin. Withdrawn.
5 R-O N-1 (log label `a3_credibility [<model_id>]`): accept (no)  E6
  Log string only; matches A1 / A2.
6 S1-06 (`_with_carry`, no age-0 branch, one comment): accept (no)  E1, E7
  -3 lines; the carry change is now one constant plus this one expression. Closure rule still needs a rewrite (N-7
  stands, unchanged).
7 R-E N-1 (`persona_floor` in the A1 engine, RL anchor imports it): accept (no)  E5
  The RL anchor loses its own `history_floor(...).isoformat()` copy. Kept out of `_common` for the A3 stub reason; the
  import `rl_a1_ability -> a1_ability.signals` is wrapper-to-engine, the intended direction. A3 will use
  `history_floor` directly (it needs a date, not a string).
8 S4-04 narrowed (four locals for names typed twice): accept (no)  E1, E6
  -3 typed strings x2, +4 locals, pylint clean (15 locals). Neutral lines; removes the drift risk of two spellings.
9 `_contact_summary` same-day order: accept (no)  E3, E1 (2)
  `_SAME_DAY_ORDER` plus a six-step `when` loop replaces a one-line `later` flag: +4 lines, but it names the Q-28 rule
  and the order is data, not an accident of label strings. Per the triage ruling (helpers that name a spec concept
  stay). Not blocking.
10 `PROMISE_MIN_AED = MIN_PAYMENT_AED`: accept with reservation (no)  E1 (2), E3
  A second name for the same 100 AED "kept apart so the two can move separately" is a constant for a later change no
  decision asks for; it adds a concept and 3 lines. It is two uses in one module and named in the spec, and the triage
  brief asked for it, so I do not block. If A3's promise points never separate them, delete the alias and use
  `MIN_PAYMENT_AED`.
11 `_cutoff` options as one table `CUTOFFS` (+ `DEADLINES = tuple(CUTOFFS)`): accept (no)  E1, E3, E7
  Option list, cutoff and validation were three places, now one dict and one `if deadline not in CUTOFFS`; -9 lines in
  `constants.py`. The pending deadline decision touches `constants.PROMISE_DEADLINE` and `CUTOFFS`, both in the A3
  package, one line each.
11b readability (`promises.py` helper order, `_TERMS` / `_DAY_TERMS`; A1 `_instalment_amount`, `strong`): accept (no)  E3, E6, E4
  `build_promise_events` is now a six-step chain whose names are the rule (`_with_terms`, `_with_payments`,
  `_with_event_start`, `_events`, `_judged`). `_instalment_amount` beside `_strong_amount` is two helpers with 1 and 2
  callers; the second is single-caller (E3 2) but names F4's other threshold. Neutral. One small thing in A1
  `classify.py`: `STABLE_INCOME_FLOORS = {3: 2, 6: 3}` was split over four lines with a trailing comment; put the
  comment above and the dict back on one line (-3 lines). Not blocking.
12 S5 docstrings: accept (no)  E6
  Shorter and true to the new rule; README thresholds updated to the single strong amount.

## Open points

1. S3-01 stub change: **allow**, in the narrow form (keep the real `enbd_collections.nodes` packages, stub only the two
   DCORE modules the spec needs). It removes the last duplicate helper in the shared layer (-5 lines, E5 3 -> 5 for
   `_common`) and makes the spec harness closer to the real import graph. If the stub edit grows past a few lines, or
   `golden_inputs.py` needs more than the same change, drop it and note the two copies for the test owner; I would not
   spend more than that on it.
2. N-3: withdrawn (item 4).
3. `DEADLINES` / `CUTOFFS` in `promises.py`: fine. Lambdas in `constants.py` would pull Spark imports into a constants
   module; the table belongs with the code that evaluates it. The one cost is that the deadline decision edits two
   files; the comment in `constants.py` points to the table.
4. Last-digit float difference in `promise_paid_amount`: accept the risk. Sums of AED amounts (two decimals) over the
   same rows; Spark's partial-aggregation order is not fixed in the old plan either, so exact-bit equality was never
   guaranteed. The bundle check should compare `promise_paid_amount` within 0.01 and the outcome exactly, not bit-for-bit.

## Files (changed tier L), updated

pipelines/crx_persona/a3_credibility/promises.py  E1 3 · E2 5 · E3 4 · E4 4 · E5 4 · E6 4 · E7 5  weighted 4.1  — 312 -> 289; 2 passes over dues / payments each become 1 (:96-165); `CUTOFFS` one table (:48); alias `PROMISE_MIN_AED` is the only noise.
pipelines/crx_persona/a3_credibility/constants.py  E1 4 · E2 3 · E3 4 · E4 3 · E5 4 · E6 4 · E7 5  weighted 3.75  — two constants and the `DEADLINES` tuple gone; `promise_deadline` still the single resolver.
pipelines/crx_persona/a3_credibility/signals.py  E1 2 · E2 5 · E3 3 · E4 4 · E5 3 · E6 4 · E7 4  weighted 3.45  — +4 for `_SAME_DAY_ORDER`; unchanged otherwise.
pipelines/crx_persona/a3_credibility/pipeline.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 4 · E6 4 · E7 4  weighted 3.3  — dataset names typed once.
pipelines/crx_persona/a3_credibility/classify.py  E1 3 · E2 5 · E3 4 · E4 4 · E5 3 · E6 4 · E7 4  weighted 3.85  — unchanged except the log label.
pipelines/crx_persona/a1_ability/classify.py  E1 4 · E2 3 · E3 3 · E4 4 · E5 5 · E6 4 · E7 4  weighted 3.7  — ten constants and four near-identical `greatest(...)` lines gone for `_strong_amount` (:~150); one stray reflowed dict (:29).
pipelines/crx_persona/a1_ability/signals.py  E1 3 · E2 5 · E3 3 · E4 4 · E5 4 · E6 4 · E7 5  weighted 3.9  — +14/-13 then -3 in `_with_carry`; `persona_floor` public; no broadcast of obs rows.
pipelines/crx_persona/rl_a1_ability/nodes.py  E1 4 · E2 5 · E3 3 · E4 3 · E5 4 · E6 4 · E7 3  weighted 3.8  — local floor copy removed.
pipelines/crx_persona/cc_raw_extract/nodes.py  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 5 · E7 3  weighted 3.4  — shorter check.
nodes/primary/products/prm_products.py  E1 3 · E2 5 · E3 4 · E4 5 · E5 4 · E6 4 · E7 3  weighted 4.0  — docstring only this round.

Weighted average, changed tier-L files this round: **3.8** (round 1: 3.5). Shared layer and engines
(`promises` 4.1, A1 `signals` 3.9, A3 `classify` 3.85, A1 `classify` 3.7; with round 1's `_common` 4.1, `sources` 3.85,
`frames` 3.65): **3.9**, just under my 4.0 target; the gap is E1 (net lines vs `d24114a` still above zero).

## Blocking objections

None remain. S4-06 stays rejected from round 1 (not applied).

## Remaining revise items (all non-blocking)

- Item 10: delete `PROMISE_MIN_AED` if A3's promise points do not separate it from `MIN_PAYMENT_AED`.
- A1 `classify.py:29`: restore `STABLE_INCOME_FLOORS` to one line, comment above.
- Open point 1: S3-01 with the narrow stub change, else document the two copies.
- Carried from round 1 and held for the user, still the largest removals: S7 group A (about -1,060 lines), B-04, B-06,
  and persisting dues / payments (D-U1-5).

## New issues that matter for sign-off

None. For the bundle check, compare `promise_paid_amount` with a 0.01 tolerance and `promise_outcome` exactly (open point 4).
