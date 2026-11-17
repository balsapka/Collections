# R-I review, council run 2, round 2 (interpretability advocate)

Frozen rubric `rubrics/interpretability.md`, blind to R-E / R-O. Reviewed `git diff a6a0b95 e3bb65e -- workplace_mirror/src workplace_mirror/specs`
(behaviour steps `8b3d969`, `faa744b`; stages `9fbc5d1` S2, `8982a26` S3, `4690b0f` S1, `4003afa` S4, `e3bb65e` S5), read
`round_1/triage.md`, `round_2/merge_log.md`, `decisions.md` D-U1-1..7, D-B-1/2. No source edited, nothing run.

Blocking objections: **none**. Remaining revise items: four small, all non-blocking (end of file).

## Round 2 items

1 S2-11 (cross-product `scoped(...)`, no `F.broadcast(obs)`): accept (blocking: no)  I7
  Uses the `_common` scoping idiom the other A1 nodes use; the inner join already did the pruning, so the rule is unchanged and the read is plainer.
1b promises performance (`_with_terms` one pass over dues, `_with_payments` one pass over payments): accept (no)  I1, I3
  The performance rewrite did not cost readability, because the same change coded the user's new rule. `build_promise_events` is now a ten-line straight flow
  (promise rows, day terms, payments, event start, events, judgement) and every step has a one-line contract. One thing I accept only with a note: the three sums
  in `_with_payments` (`_paid_before`, `_paid_by`, `promise_paid_amount`) are the whole subtlety of "an event never counts the payments of its own start day twice";
  the docstring explains it, but `_paid_by` is a poor name (see revise R-1).
2 S3-04 (`raw_stg_balance` check lists only columns the mirror reads): accept (no)  I5
  A contract that lists only what the code reads; removing the unverifiable names removes a false promise.
3 S3-01 (reverted, A3 spec package stub): accept the revert (no)  I7
  Two `require_columns` stay; I accept it. A check-script stub is not a reason to bend the shared layer. Re-raise with the stub change, not before.
4 R-E N-3 (episode check once): accept the skip (no)  I5
  A boundary check per public builder is the contract at the boundary the spec test calls. Fewer checks would hide the contract.
5 A3 state log label with model_id: accept (no)  I7
  Same label shape as A1 / A2; a log reader can tell the model_id apart.
6 S1-06 (`_with_carry` without the `age == 0` branch, one comment): accept (no)  I1
  Met. The comment says why the 0 row hides older rows. The closure rule is now a single `where` in that union step.
7 persona floor in one helper (`persona_floor`, RL anchor imports it): accept (no)  I7
  Met (N-13). Public name in the A1 signals module; the RL wrapper imports the engine, which is the intended direction.
8 S4-04 narrowed (four locals for the signal output names): accept (no)  I2
  Met. The persisted names are typed once; the pylint locals limit holds. The names still say little (`..._single_payment_cycle_count`), but they are
  fixed by the workplace catalog.
9 `_SAME_DAY_ORDER` / `same_day_rank`: accept (no)  I1, I2
  Met (my S2-01 revise). The Q-28 tie rule is a tuple at module level with a comment, the struct field says what it is, and the order equals the old one.
  Building the rank in a `for` loop inside `_contact_summary` is fine at four lines; a one-line `_same_day_rank()` helper would be nicer but I do not ask for it.
10 `PROMISE_MIN_AED = MIN_PAYMENT_AED`: accept (no)  I2
  Met (N-2). The promise floor and the partial limit have their own name and a comment saying why it is separate. A decision change moves one line.
11 `CUTOFFS` + `DEADLINES = tuple(CUTOFFS)`, `PROMISE_DAYS`: accept (no)  I2, I6
  Met (N-4) in substance. One table, the option names cannot drift from the code that implements them, the 30 is named. My view on placement below.
11b readability (`_TERMS`, `_event_step`, `_with_event_start`, A1 `_strong_amount`): accept (no)  I1, I3
  See the traceability section; the rule order in the file follows the rule order in the spec.
12 docstrings (`_latest_in_month`, `build_contact_signals`, README): accept (no)  I5
  The docstrings state the tie rule, D-A3-30 and the single strong amount; nothing narrates history. Checked against the merged code, no stale text found.

## Round 1 revise items

| Item | Met? |
|---|---|
| S1-06 redundant branch and comment | yes (item 6) |
| S2-01 tie order named, not by label spelling | yes (item 9) |
| S4-04 names typed once | yes (item 8), the dataset names stay as the workplace fixed them |
| N-2 own constant for the promise floor | yes (item 10) |
| N-4 deadline options in one place, 30 named | yes (item 11); `STATEMENT_FALLBACK_D` is still the cryptic name (now also a cap, see R-4) |
| N-5 generic matching loop, N-6 `MATCH_DAYS` ID | gone with the matching rule (D-U1-1 replaced it by one event stream) |
| S4-06, S4-16 | R-O dropped them; I accept the ruling |

## Can each decided rule be found in one place, with its spec ID?

- **Event alive until deadline or paid (D-U1-1, D-A3-29):** `promises._event_step` (docstring cites D-A3-29 and states both end conditions) with `build_promise_events`
  stating the whole flow. One place, ID present. `_TERMS` / `_DAY_TERMS` name what a promise day decides; `paid_since_start` names the "paid" condition.
- **Promised amount = latest non-empty due (D-U1-6):** `promises._with_terms`, `promise_amount`. One place; the docstring states "latest due on or before the day, cycles
  without a due amount skipped, at least PROMISE_MIN_AED". The docstring does not cite an ID (D-U1-6 is a decision-log ID; the spec ID for it should appear, R-2).
- **Next-statement cap of 31 days (D-B-2 (1)):** `promises._next_statement` and `STATEMENT_FALLBACK_D`. One place, but neither cites D-A3-28 and the constant name "fallback"
  no longer says it is also a cap (R-4). The user has still to confirm this detail, so the code should say it is a decision under confirmation.
- **Refusal lifted when a payment may have come after it (D-U1-7, D-A3-30):** `signals._paid_after_refusal` (`pay_date >= last_rpc_date`) and the `build_contact_signals`
  docstring, which cites D-A3-30. The helper's own docstring still cites only Q-29 (R-3). The cards / loans difference is a comparison on dates, not an `if product`,
  which is the right shape: the RL month-end dating does the work, and the docstring says so.
- **One strong amount (D-U1-3, family rule §2):** `a1_ability.classify._strong_amount`, used by income, money in / out, the balance and assets; `STRONG_FLOOR`,
  `STRONG_ANCHOR_MULT`, `FLOW_SOME` grouped with a comment citing the family rule §2. One place per number. The instalment rule is separately named
  (`_instalment_amount`), correctly, since it did not unify. Auditor path from a state: `a1_reason` (family), then `_strong_amount`, then the constants.

## DEADLINES / CUTOFFS in `promises.py`

Acceptable. The decision (which deadline per segment and product, `PROMISE_DEADLINE`) stays in `constants.py` with the other numbers; the options (what each deadline
means as a date) sit next to the single function that applies them, so a new option is one entry in one dict. The cost is that A3's settings are in two modules; the
`constants.py` comment points at `promises.CUTOFFS`, which is enough. The invalid-option error is raised in `build_promise_events` with the option list from the same table.
I would not move it to `constants.py` with lambdas (Spark imports there). The dict of lambdas with `lambda day, _:` is a small readability cost (I4); it is not a switch that chooses
a method per D-A3-3, because the 30-day option is the user's built-in alternative, not a branch in the engine.

## Files (changed tier L)

Criteria I1 22 · I2 14 · I3 16 · I4 12 · I5 12 · I6 16 · I7 8.

| File | I1 | I2 | I3 | I4 | I5 | I6 | I7 | Weighted | Note |
|---|---|---|---|---|---|---|---|---|---|
| `a3_credibility/promises.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.28** | straight flow, rule order = spec order; lowest: promised-amount and cap rules lack spec IDs, `_paid_by` name, `# pylint: disable` on the entry (:253) |
| `a3_credibility/constants.py` | 4 | 4 | 5 | 4 | 4 | 5 | 4 | **4.32** | `PROMISE_MIN_AED`, `PROMISE_DAYS`; lowest: `STATEMENT_FALLBACK_D` (:22) says fallback, is also a cap |
| `a3_credibility/signals.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.38** | `_SAME_DAY_ORDER`, D-A3-30 in the contact builder; `_paid_after_refusal` docstring cites Q-29 only |
| `a3_credibility/pipeline.py` | 4 | 4 | 4 | 3 | 4 | 5 | 4 | **4.04** | names typed once; the persisted names still do not say the content |
| `a3_credibility/classify.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.38** | one log line |
| `a1_ability/classify.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.38** | `_strong_amount` is the one home of the unified rule; lowest: `STABLE_INCOME_FLOORS` (:28-31) keeps the "floors" name after the floors became strong amounts and black split the dict over four lines with a trailing comment |
| `a1_ability/signals.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | `persona_floor` shared with RL, carry branch gone; `build_income_signals` is still the longest A1 builder (S4-06 left for the carry bundle) |
| `rl_a1_ability/nodes.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | one floor helper |
| `prm_products.py`, `cc_raw_extract/nodes.py`, `a1_ability/README.md` | 4 | 4 | 4 | 4 | 5 | 4 | 4 | **4.10** | docstring tie rule, narrower contract, README states one strong amount |

Mean of the changed tier-L rows: **4.20** (round 1: 4.05 over its files). Whole tier L with round 1's unchanged rows carried over: about **4.10**. Bar 3.5: met.
Lowest criterion in the changed files: I3 on A1 `build_income_signals` and the dense `_event_step` (justified by its docstring).

## Blocking objections

None. Checked the seven: no rule lost its named place (the new event rule is more traceable than the matching loop it replaced); no business number became a literal
(`PROMISE_MIN_AED`, `PROMISE_DAYS`, `STRONG_*`, `FLOW_SOME`); no stale docstring found; the output keeps its reason columns (`promise_outcome`, `event_kind`, `a3_reason`, `a1_reason`).
`a3_promise_deadline` still labels the rule used.

## Remaining revise items (non-blocking, for the bundle or the next round)

R-1 `promises.py:123,147` rename `_paid_by` to say what it is ("paid on or before the event day") and say once why an event starting that day never counts it.
R-2 `promises._with_terms` docstring: cite the spec ID that carries D-U1-6 (D-A3-29, if that is where the spec states it).
R-3 `signals._paid_after_refusal` docstring: add D-A3-30 next to Q-29.
R-4 `constants.STATEMENT_FALLBACK_D`: rename to say it is the cap on the next statement (for example `NEXT_STATEMENT_MAX_DAYS`) and add "D-B-2, to be confirmed by the user" to the comment.
Also small: `a1_ability/classify.py:28-31` rename `STABLE_INCOME_FLOORS` (for example `STABLE_INCOME_STRONG_AMOUNTS`) and put its comment above the line.

## New issues that matter for sign-off

None. The behaviour changes D-U1-1 / -3 / -6 / -7 are traceable from the code; the only open point is the user's confirmation of D-B-2 (1) and (2), which the code should keep visibly marked until answered.
