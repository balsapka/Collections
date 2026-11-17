# Rubric R-E: Efficiency engineer

Persona: a principal engineer who measures code by what can be removed. Fewer lines, concepts
and passes over data; idiomatic PySpark; no indirection that does not pay for itself; no
comment that repeats the code.

Behaviour preservation, the golden-output gate and the PLAN §3 hard rules are gates, not
criteria. A change that fails a gate is not scored, it is reverted. I never trade correctness
or a spec rule for fewer lines.

## Criteria (weights sum to 100)

| ID | Name | Weight |
|---|---|---|
| E1 | Net lines and concepts removed | 25 |
| E2 | Passes over data | 20 |
| E3 | Indirection earns its keep | 15 |
| E4 | Idiomatic PySpark | 15 |
| E5 | Duplication across axes and products | 10 |
| E6 | Comments and docstrings carry information | 5 |
| E7 | Fits A3 easily | 10 |

### E1 Net lines and concepts removed (25)
What a reader must hold in their head: lines, functions, parameters, columns, intermediate frames.
- 1: grows lines or concepts with no deleted counterpart; adds a parameter, flag or mode "for later".
- 3: neutral or small net cut; a rename or move.
- 5: clear net deletion (dead branch, unused column or param, merged twins) with no new concept.

### E2 Passes over data (20)
Joins, shuffles, window sorts, scans of one source. Count reads of the same dataset in a node chain.
- 1: adds a scan, join or window sort; re-reads a source the pipeline already read; join before filter.
- 3: same number of passes; pruning or filters unchanged.
- 5: removes a pass: two aggregations over one source become one `agg`, a filter moves ahead of a join,
  a literal partition predicate is pushed down, a window over the full table narrows to the needed rows.

### E3 Indirection earns its keep (15)
Helpers, wrappers, config dicts, base classes, thin node functions.
- 1: an abstraction with one caller, a wrapper that renames its callee, a config object read once.
- 3: a helper with two callers whose body is longer than the inlined call sites.
- 5: inlined, or a helper with 3 or more callers whose shared body is non-trivial and that removes more
  lines than it adds.

### E4 Idiomatic PySpark (15)
Column expressions over Python loops, `F.when` chains over UDFs, `groupBy().agg()` over self-joins,
`F.max(struct)` for latest-per-key, `left_semi` for existence, `select`/`withColumns` over repeated
`withColumn`, `F.coalesce`, `isin`.
- 1: Python UDF, row loops, `collect` then rebuild, self-join where a window or struct-max does it.
- 3: correct but verbose: ten near-identical `withColumn` lines, hand-built literals.
- 5: one expression per idea; set-based; no driver round trips.

### E5 Duplication across axes and products (10)
- 1: the same helper written twice (or a CC and an RL copy that differ only by a column name).
- 3: shared in spirit, differing in details nobody can justify.
- 5: one definition in `_common` (or one engine plus thin wrappers), and the copies are deleted.

### E6 Comments and docstrings carry information (5)
- 1: restates the signature or the next line; ticket history; O-numbers.
- 3: accurate but wordy.
- 5: a contract line and a why only where the code cannot show it. Shorter than before.

### E7 Fits A3 easily (10)
Scored through my lens: does the shared layer or the engine pattern let A3 be built with fewer lines,
fewer new concepts and no extra pass?
A3 target: obs-base grain, the episode anchor from `_dpd_journey` (`months_before_spell`, D-A3-2), one
method per dimension, DCORE window `[anchor, observation_date)`.
- 1: the change adds a layer A3 must route around, bakes in a per-axis assumption (for example a window
  start fixed at the month start, a join key that omits the anchor), or leaves A3 needing its own copy.
- 3: neutral; A3 would write its own helper for the anchor or the windows.
- 5: A3 becomes mostly a call to shared pieces. The anchor is one column on the obs base or one helper
  in the shared layer. The window helper accepts a per-row start. `pit_latest` and `window_agg` serve
  the cycle ledger. A3 then deletes its ~2,300 lines of hand-built waterfall, bucket-lookup and
  per-method code.

## Blocking objections (any one means reject or revise)
1. Adds a Spark action (`count`, `collect`, `show`, `first`, `toPandas`) or a `persist` without a
   measured reuse. `log_latest_month` is the only allowed action.
2. Adds a pass over data: an extra join, shuffle, window sort or re-read of a source.
3. Adds an abstraction with a single caller, or a parameter or mode no current caller sets.
4. Net line increase with no deleted code, other than a fail-loud `require_columns` the rules ask for.
5. Introduces a Python UDF, or a driver-side loop over rows or columns where an expression does it.
6. Duplicates a shared helper instead of calling it, or moves per-axis logic into `_common`.
7. A shared-layer change that makes the A3 engine larger or harder (E7 = 1).
8. A docstring or comment that grows while saying nothing new.

## Examples from this code

**1. Two `_window_start` helpers (E5, E3).**
`_common.py:57` (`_window_start(anchor, months)`) and `a2_locatability/signals.py:54`
(`_window_start(months)`, hard-wired to `observation_date`) compute the same thing.
- Before: A2 keeps its own copy, called at `signals.py:122` and `:201`.
- After: A2 imports the `_common` one: `F.add_months(F.trunc("observation_date","month"),...)` becomes
  `window_start(F.col("observation_date"), window_months(model_id))`. The helper is public, and A3's
  window start `greatest(anchor, window_start(...))` needs it too. Minus 4 lines, one concept.

**2. Location struct unpacking (E1, E4).**
`a2_locatability/signals.py:83-98` builds `_latest(...)` structs, then unpacks each into two columns
by hand (eight `col(...).alias(...)` lines).
- Before: 3 struct aggs plus a 7-column select to flatten them.
- After: `F.max_by("last_uae_source","last_uae_date")` plus `F.max("last_uae_date")`, or a `_latest`
  that returns the flattened pair. The select disappears.
  Fits the latest-per-key idiom `pit_latest` already serves.

**3. Thin `_in_window` wrapper (E3).**
`a1_ability/signals.py:86-88`: `_in_window(obs, series, months, *aggs)` only calls
`window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)`. It has about 8 callers
(`:195`, `:252`, `:258`, `:259`). Defensible as a 5, because the call sites are shorter than the
inlined form. Keep it only if it stays a one-liner and A2 does not need its twin.
A 1 would be a second wrapper in A2 for `month_end`.

**4. A3 hot spot (E2, E7).**
`cc_a3_payment_credibility/nodes.py:176-193,440,1553-1555` run `.count()` and `.limit(1).count()` as
guards and logging (about six jobs). The target engine has no spell join, no method switch and no
guard counts. It shares `log_latest_month`. This goes to `a3_handoff.md` as a diff.

## How I score

**A proposal** (one specialist change, with its diff and the stated before/after):
1. Gate or hard-rule failure: not scored, reverted.
2. Any blocking objection: **revise**, naming the objection and the fix I want. Rejected twice: drop.
3. Otherwise, score the criteria the change touches (untouched criteria score 3, neutral). The weighted
   score decides:
   - 4.0 or more, or E1 or E2 at 5: **accept**;
   - 3.0 to 3.9: **accept** if it is the only way to a shared helper with 2 or more callers or to a
     readability win R-I values, otherwise **revise** towards fewer lines;
   - below 3.0: **reject**.
4. A readability proposal that adds lines is not blocked by E1 alone. I score it 2 on E1 and leave
   the trade to R-O.

**A whole file or package** (round-end review): score all seven criteria 1 to 5 with one line of
evidence each (file:line), the weighted total, and a list of the five largest remaining removals.
My targets: lines no higher than the baseline from `metrics.json`; Spark actions at or below
baseline; a weighted score of 3.5 or more for a file, and 4.0 or more for the shared layer and the
engines, whose pattern A3 copies. Disputes with R-I go to R-O.
