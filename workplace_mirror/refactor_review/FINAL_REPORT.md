# Council run 2 (A3 credibility + A1 ability): final report

Branch `refactor/council_a1_a3` (worktree `.worktrees/council_a1_a3`), base `4536d52`, head `d959310`.
Two rounds. **Signed off by R-O on 2026-11-15 with four recorded exceptions**; no round 3. The tree
holds three user-decided behaviour steps and a no-output-change refactor; it ships as bundle 25.

## 1. What is in the tree

| Part | Commits | Output change |
|---|---|---|
| D-A3-29 first form (follow-up after the deadline = new event) | `995a212` | yes, superseded below |
| Round 1 refactor (39 proposals; S7, S1, S3, S2, S4, S5) | `e677655..a6a0b95` | none (oracle) |
| A3 behaviour: promise events alive until the deadline or paid in full; promised amount = latest non-empty due; 31-day cap on the next-statement deadline; refusal lifted by a payment that may have come after it | `8b3d969`, `ac50e2b`, `d959310` | yes (user D-U1-1, -6, -7; Master details Q-R-11, Q-R-12 open) |
| A1 behaviour: one strong amount max(3,000, 2 x anchor); `FLOW_SOME` 1,000 | `faa744b` | yes (user D-U1-3, -4) |
| Round 2 refactor (11 items) and clean-up | `9fbc5d1..e3bb65e`, `d959310` | none (oracle re-recorded after the behaviour steps) |

Source diff `4536d52..d959310`: 29 files, +1,097 / -969. New module `a3_credibility/promises.py`
(the promise-event rule); `sources.py` 372 -> about 150 lines; `cc_raw_extract` docstrings cut by
about 290 lines; `lookback_floor` and its Spark actions removed (4 fewer actions per A1 run).

## 2. Gates on the head

A1 spec 91/91 · A3 spec all checks pass · A2 spec 36/36 · A4 chain spec pass · oracle 188 datasets in 23
runs: pass · smoke: the six baseline `cc_raw_extract` import failures only · black clean · ruff: one E501
left in tier L (a dataset-name literal in `a3_credibility/pipeline.py`) · pylint: no new message.

## 3. Reviewer scores

| Reviewer | Round 1 | Round 2 | Bar |
|---|---|---|---|
| R-E efficiency | 3.5 | 3.8 | 3.5 |
| R-I interpretability | 4.05 | 4.20 (changed files) | 3.5 |
| R-O owner | ~4.15 (O1 3.9, O2 3.8) | ~4.25, every criterion >= 4 | 4 on every criterion |

## 4. Change log by theme

| Theme | What changed |
|---|---|
| Architecture (S1) | `promises.py` holds the promise rule; the CC read window lives in the CC A3 wrapper with named constants; A1 source floors from `params:crx_persona` (`frames.history_floor`, `persona_floor`); `BUREAU_CARRY_MONTHS`; one `promise_deadline(product, model_id, override)` |
| Performance (S2) | contact signals in one pass; promise events: one pass over dues and one over payments per promise day; instalments scoped before the bank-wide table; no broadcast of the obs base; product primaries as grouped max |
| Contracts (S3) | A3 builders check their inputs (`EPISODE`, `CYCLE_LEDGER`, `INSTALMENTS`, `DUES`, `PAYMENTS`); `cc_raw_extract` checks the columns it reads and uses dict inputs; A3 log label carries the model_id |
| Readability (S4) | long A3 builders split into helpers that name a rule; contact tie order as `_SAME_DAY_ORDER`; deadline options in one table (`CUTOFFS`); `PROMISE_MIN_AED`; one `_strong_amount` in A1 |
| Dead symbols (S7 B) | `PRODUCT_TYPES`, `pit_latest(anchor=)`, `build_contact_signals(max_months=)`, stale README name |
| Docstrings (S5) | history removed; 36 -> 1 over-long lines; specs' function names follow the code |

Renamed / moved / removed / new symbols and changed log or error texts for the test owner:
`round_2/gates.md`.

## 5. Disputes and rulings (R-O)

- Single-use helpers that name a spec concept stay (R-I over R-E); contract lists stay; `promises.py` stays its own module.
- S4-06 (income builder split) and S4-16 (rename of a shared symbol) dropped; S3-11, S2-12, S3-03, S3-07 dropped.
- S3-01 (one `require_columns`) dropped for bundle 25: it needs a change to the check harness's package stubs (E1).
- `PROMISE_MIN_AED` kept (R-I over R-E). `CUTOFFS` / `DEADLINES` stay in `promises.py`.
- S2-10 tie rule kept (deterministic), with a bundle-check condition.
- Pylint gate read by message set for files whose only messages are unmirrored imports.

Exceptions: E1 two `require_columns` helpers · E2 `cc_raw_extract/nodes.py` large docstring diff on a
module the mirror cannot import (UAT reviews it explicitly) · E3 R-E's shared-layer average 3.9 against
its 4.0 target · E4 smoke baseline failures.

## 6. Questions (`questions.md`)

Closed by the user: Q-S6-01, -03, -08, -10, Q-01, Q-R-04; moot: Q-S6-02. Defect found and fixed: Q-S6-17.
**Needed before the build:** Q-R-11 (31-day cap), Q-R-12 with Q-S6-20 (same-day card payment / plan
and a refusal), Q-S6-19 (100 AED floor over a small known due). Open, not blocking: the rest of
sections A-C; Q-R-01 (dead packages) waits on the workplace grep and ships as its own bundle.

## 7. Delivery: bundle 25 (R-O's conditions, `round_2/reviews/R-O.md` §5)

One bundle: A3-1 promise events, A3-2 refusal, A1-1 one strong amount, plus the refactor. Persisted
outputs are the reference; all four model_ids.

- **Exactly 0 differing rows (the refactor):** product primaries, product and bureau features (only
  card keys with two rows on their latest day may differ); all A1 signal tables; the A1 state under
  the old thresholds (a temporary copy of today's `classify.py` run on the new signals); A3 episode,
  cycle ledger, instalments, Dimension B and C signals; every contact column except the two refusal
  ones; A2 and A4 outputs. Double amounts within 0.005, everything else exact.
- **Not testable in PROD:** the refactor of the promise events and commitments, because A3-1
  rewrites them; that rests on the oracle and the A3 spec test.
- **Distribution + crosstab, reviewed before step 8:** A3-1 (event kinds, outcomes, events ended early,
  capped at 31 days, amount changed), A3-2 (refusal flag, loan month cash and card same-day lifts
  apart), A3 state moves split by cause, A1-1 (old vs new state, rows moved by family, payment and cure
  per level), run times on cc_180_plus.
- **Before the build:** the three answers above; the UAT listing of the workplace A3 catalog entries
  (persisted dues / payments go in only if it is back, else the next A3 bundle); the workplace grep for
  removed and moved symbols; rebase onto the workplace-equivalent head and re-run every gate;
  `--exclude _dcore_codes.py`; no registry edit.
- **Not in bundle 25:** the dead-package deletion (S7 group A), the CASA handoff prompt, S2-12.
