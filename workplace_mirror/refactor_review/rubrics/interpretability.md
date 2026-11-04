# Rubric R-I: Interpretability advocate

Lens: the analyst who joins next year and the auditor who must trace a state back to a rule.
Behaviour preservation is a gate (PLAN §3), not a criterion here. I accept extra lines when they
make a business rule visible; I do not ask for history (D3) or for comments that repeat code.

## Criteria (weights sum to 100)

| ID | Criterion | W |
|---|---|---|
| I1 | Rule traceability | 22 |
| I2 | Named constants and thresholds | 14 |
| I3 | One idea per function, straight-line flow | 16 |
| I4 | Names say the business meaning | 12 |
| I5 | Docstring at every boundary | 12 |
| I6 | Fits A3 easily | 16 |
| I7 | Same pattern on every axis | 8 |

### I1 Rule traceability (22)
Each spec rule (A1 S1-S15, A2 D-A2-n / §4-6, A3 D-A3-n, A4 states) maps to one named place in code,
and that place names the rule.
- 1: a rule is spread over several expressions or nodes, or only exists as an inline boolean; the
  auditor must run the data to find which rule fired.
- 3: rule has a named function or constant, but the spec ID is missing or the rule is split across
  two functions.
- 5: one function or constant per rule, spec ID in its docstring or name, and the output carries the
  reason (`*_rule`, `*_reason`, `*_source`) so a state is traceable from the data alone.

### I2 Named constants and thresholds (14)
Every business number or label sits in a module constant with its unit and spec link.
- 1: literals in expressions (`{"stable": 2, "weak": 1}`, `4`, `2`, `100`, `"D"`).
- 3: constants exist but are bare (`F_INC`, `K_PAY`) or sit away from the rule that uses them.
- 5: constants grouped at the top of the module with unit, spec ID and meaning
  (`GONE_DARK_DAYS` per segment is the model); one definition per number across the package.

### I3 One idea per function, straight-line flow (16)
- 1: a function builds, joins, scores and logs; more than ~40 lines; flags switched by arguments;
  pylint disables for too many arguments or locals.
- 3: mostly one purpose, but one mixed block, or a helper that needs the caller's column names.
- 5: reading top to bottom gives: join, level per dimension, points, override, ladder, output
  columns. Each step is a small named function with a one-line contract. No switches that choose a
  method (D-A3-3).

### I4 Names say the business meaning (12)
- 1: positional or cryptic names (`d`, `w`, `f`, `K_CASA`, `_m1.._m6` used without explanation),
  names that describe the mechanism (`agg2`, `_join_signals_pair`).
- 3: clear in context but not outside it.
- 5: a reader of the output table understands the column; function names are verbs on a business
  object (`income_level`, `gone_dark_days`); same word, same meaning across axes.

### I5 Docstring at every boundary (12)
Boundary = node function, engine entry, public helper, module.
- 1: missing, or a ticket history (D3), or `[CONFIRM: ...]` notes, or stale (describes removed
  methods).
- 3: says what, not the contract (input columns, grain, output columns, nulls).
- 5: states the contract and the non-obvious reason in 2-6 lines; the module docstring names the
  spec, the inputs and the run command. Nothing narrates the next line.

### I6 Fits A3 easily (16)
A change to the shared layer or the engine pattern makes the planned A3 engine simpler to build:
obs-base grain, episode anchor from `_dpd_journey`, one method per dimension, thin CC/RL wrappers.
Score through the reader's eyes: can they see that A3 follows A1, A2 and A4?
- 1: the change adds a switch, a layer or a convention A3 would have to work around; or A3's inputs
  (anchor, DCORE window, cycle ledger) have no named home.
- 3: neutral; A3 can use it, but must re-explain a pattern the other axes state differently.
- 5: the shared helper is named for the A3 need (episode anchor, `window_months`, DCORE window,
  `StateLadder`, `require_columns`), A3 would be `signals.py` + `classify.py` + `pipeline.py` with
  the same function names and block order as A2, and its spec decisions (D-A3-2, -3, -6) point at
  exactly one helper each.

### I7 Same pattern on every axis (8)
- 1: the same thing is written three ways (labels map, ladder, window months, unknown reason).
- 3: same shape, different spelling.
- 5: identical module layout (`signals`, `classify`, `pipeline`), identical output idioms
  (`*_state`, `*_state_label`, `*_unknown_reason`), shared helpers only.

## Blocking objections (any one rejects the change)
1. A spec rule is no longer traceable to a named place (merged into a generic helper, or into a
   dict-driven loop that hides which rule is which).
2. A clever one-liner or comprehension hides a business rule or a threshold.
3. A business number or label moves from a named constant into a literal.
4. A docstring that states history, or one that no longer matches the code (stale after the change).
5. The output loses a reason or provenance column that lets a state be traced (renames of output
   columns are also barred by PLAN §3).
6. A shared-layer change that makes A3 harder: a switch for A3's alternatives, an anchor or window
   helper that A3 cannot call, or an A3 name that differs from A1/A2/A4 for the same idea.
7. Fewer lines bought by merging two ideas into one function or by parameterising away the rule
   (generic `rule_fn(df, spec)` over named rules).

## Examples from this code
1. **Inline points, `a1_ability/classify.py:154-155`** (score 2 on I2/I1). Points and the unknown
   gate are literals in `build_a1_ability`, which also builds labels and diagnostics (~60 lines).
   ```python
   # now
   points_from_level(income, {"stable": 2, "weak": 1}) + points_from_level(liq, {"adequate": 2, "weak": 1})
   # 5
   INCOME_POINTS = {"stable": 2, "weak": 1}      # S3
   LIQUIDITY_POINTS = {"adequate": 2, "weak": 1} # S3
   def a1_points(income, liquidity) -> Column: ...
   def a1_unknown(points, distress, casa_active) -> Column:  # S11, 3 inputs, 1 rule
   ```
2. **Cryptic constants, `a1_ability/classify.py:25-36`** (I4/I2). `F_INC`, `K_INC`, `D_CASA`,
   `DEMIN` need the workbook to decode. A 5 names them by meaning, e.g. `SALARY_FLOOR_AED`,
   `SALARY_ANCHOR_MULTIPLE`, `CASA_MAX_DROP`, `MIN_EVIDENCE_AED`, each with its S-number.
3. **A3 `cc_a3_payment_credibility/nodes.py:1442`** (I3/I5/I6 = 1). The entry takes 5 optional
   method tables, two method switches, three pylint disables and a `[CONFIRM]` docstring; `nodes.py`
   is 1,570 lines. A 5 is the `a2_locatability/classify.py` shape: `build_a3_credibility(obs_base,
   commitments, payments_dlq, payments_pre, negatives, model_id, persona_end_date)`; one
   `_dimension_*` function per dimension; the D-A3-2 anchor from one `episode_anchor()` helper in
   the shared layer.
   Good reference points: `a2_locatability/classify.py` (state, label, reason on every row) and
   `a2_locatability/signals.py:39-42` (constants with comments tied to the rule).

## How I score
- **Proposal:** accept = no blocking objection and it raises or keeps a weighted criterion; revise
  = a fixable objection (I quote it and the rule it hides); reject = it removes traceability or
  hides a rule and the gain is only line count. A pure line-count win with no I-effect is
  *accept, neutral*. Behaviour change = not mine, flagged to the gate and S6.
- **File:** 1-5 per criterion, then the weighted mean. I report the lowest criterion with
  file:line and one fix. Convergence: average at least 3.5 (PLAN §5); no blocking objection open.
- **Disputes with R-E:** I yield when the lines removed carry no rule; I hold when they carry one.
  R-O decides the rest.
