# Round 1 triage = round 2 brief

Input to round 2: HEAD `5c24553` (round 1 merged tree). R-O's verdict decides (`reviews/R-O.md`,
rulings R-1 … R-14). Round 2 is **targeted**: only the revise items and new issues below. Hard rules
(PLAN §3) unchanged: no output change, no new Spark action, tier K/A/X untouched, black / ruff /
pylint no worse per file.

**Round 2 line budget: tier L net ≤ −25 lines** (R-7). Each item has its own budget; the Master
rejects an item that exceeds it.

## Keep (no further work)

S7 · S1-01, S1-02, S1-03, S1-04, S1-05, S1-06 · S3-01, S3-02 (R-E blocking 4 waived, R-3), S3-03,
S3-05, S3-06, S3-07 · S2-01, S2-04, S2-05, S2-07 · S4-01, S4-04 (part; `_latest_evidence` kept, R-8),
S4-05, S4-06, S4-07 (kept, R-8), S4-10, S4-11 · S5.
Held: **S3-04** until Q-15 (applied in round 2 by S3 only if the user answers "yes" at U1).

## Revise

| Id | Objection (quoted) | Acceptable when | Owner | Budget |
|---|---|---|---|---|
| S1-07 `episode_start` | R-E: "52 lines, `grep` finds no caller in tier L, tier K or the tests" (blocking 3) | Stays in `_dpd_journey/anchor.py` (R-1, PLAN §2). A checked spec case calls it: S1's sanity run (card clean Jan–Mar 2025, delinquent from April, obs 31 May / 30 June → `episode_start` 2025-04-01; string vs long key) becomes an assertion in a `workplace_mirror/checks/` spec script, plus one left-censored row. One-line comment on `history_months - 1 - months_before_spell`; docstring says which rows are censored and what the consumer does (R-I N-12, N-13) | S1 | tier L +3; checks ≤ 60 |
| S1-08 `window_agg(start=)` | R-E: "parameter no caller sets … if kept, `start` must get a test case" (blocking 3) | Same check script: a row with `start` after `window_start(months)` and one before it; both bounds inclusive | S1 | in the above |
| S4-02 `__all__` | R-E: "Thirty-eight of them are `__all__`, and most entries are private names … that exist for the workplace tests" (blocking 4) | `__all__` removed; file-level `# ruff: noqa: F401`; imports in two commented groups ("public" / "re-exported for the parity tests"; one line that `H, N, P, R` are the reference's names). Keep `log_state_stats`. Delete `_month_label` and its two export lines (R-E N-1). Ruff for the file must not rise | S4 | ≤ −40 |
| `_dpd_journey/__init__.py` docstring | R-E N-2: "60-line docstring duplicates METHODOLOGY" | Contract, run commands, module list only; METHODOLOGY named, not repeated | S5 | ≤ −35 |
| S2-06 (reverted, E501) | Gate 2: 89-char comment. R-I: "the negation hides the tie-break … I do not yield on a bare negation with no explanation" | Re-submitted as private `_restructure_blind_spot(history)` in `cc_a4_deterioration/nodes.py` holding S2-06's single `min(struct(obs_date, -dlq_bucket))` aggregate; two comment lines ≤ 88 chars: earliest dated row, same-date tie → worst bucket; bucket negated so the smallest struct is that row (R-5). Replaces S4-09's CC half | S2 | ≤ +2 |
| S4-03 (reverted, E501) | R-E: "four new single-caller helpers … type hints on six small helpers; net lines up" (blocking 3, 4) | Only `_monthly_rows_per_account` and `_spine_rows_with_history`, re-based on `string_key` / `state_label`, each with a one-line column contract; no `_history_udf` / `_classify_udf`, no type hints, every line ≤ 88 (R-4) | S4 | ≤ +6 |
| S4-09 (reverted, E501) | R-E: "single caller each … no shorter result" (blocking 3) | RL half only: one helper `_original_loan_months` that also absorbs the nested `frame()` closure (R-I N-8); docstring first line ≤ 88 names the restructure-chain rule. CC half dropped (superseded by S2-06's helper) | S4 | ≤ +8 |
| S2-02 (applied) | R-I: "S11 'customer-initiated movement' and 'holds a CASA' are each split over a union column and an aggregate" (non-blocking) | Code and plan stay. `_casa_legs` (one-line contract per column) and `casa_active` / `casa_held` as named column expressions citing S11 (R-6, R-I N-4). Rename `INTERNAL` / `BUREAU` / `BUREAU_BOUNCE` to `SOURCE_INTERNAL` / `SOURCE_BUREAU` / `REASON_BUREAU_BOUNCE`, values unchanged (R-10) | S4 | ≤ +8 |
| S2-03 (applied) | R-I: "`gone_dark` stays an inline boolean … no output says which reachability rule fired"; R-E N-3: "the `rank` window now sorts every DCORE account-day" | One edit of `build_dcore_signals` (R-9): replace the window with the last-`streak` attempt days read in the same aggregate (`slice(sort_array(collect_list(when(attempt, struct(day, failed))), asc=False), 1, streak)` or equivalent), so non-attempt days are never sorted; `gone_dark` as a named expression / private function citing D-A2-7 / D-A2-20. Accept only if golden + A2 spec pass and local `explain()` shows no more Exchange nodes than HEAD. If not clearer or shorter, keep the window, do the naming, and the A2 bundle check carries the N-3 measurement | S2 | ≤ +6 |

## Revert

None. (The three gate reverts, S4-03, S4-09 and S2-06, are revise items above.)

## Dropped / rejected (logged, not proposed again)

- S4-08 (duplicate of S1-04, round 1 skip).
- S4-03 `_history_udf`, `_classify_udf` and the type hints (R-4).
- S4-09 CC half `_restructure_blind_spot` as a wrapper over the old self-join (superseded by S2-06).
- R-E N-8 `persona_tags()` helper (R-3 / S3-04 note).
- R-E N-10 lists where dataset and parameter names match (R-3).
- R-E: move S1-07 / S1-08 into the A3 bundle (R-1).
- R-I N-9 move `_RESTRUCTURE_DLQ_THRESHOLD` (R-12; revisit when `cc_spell` is deleted).
- R-I N-2 four-way split of `build_a1_ability` (R-13).
- R-E: inline `_latest_evidence`, `_shift_cycle_bills` (R-8).

## New issues for round 2 (deduplicated)

Priority 1 = needed for a revise or a PROD risk; 2 = rule visibility; 3 = small.

| # | Source | Issue | Owner | Pri | Budget |
|---|---|---|---|---|---|
| 1 | R-E N-3 + R-I N-3 | DCORE window sort and naming | S2 (in S2-03 row) | 1 | ≤ +6 |
| 2 | R-E N-4 | `scoped` broadcast in `pit_latest`: **no code change**; measurement and drop-the-hint rule go into the A1/A2 bundle plans (R-O.md "PROD cost items") | Master | 1 | 0 |
| 3 | R-E N-1, N-2 + R-I N-6 | `__init__` `__all__`, `_month_label`, docstring | S4 + S5 (rows above) | 1 | ≤ −75 |
| 4 | R-E N-5 + R-I N-12, N-13 | checked cases for `episode_start`, `window_agg(start=)`; anchor comment | S1 (rows above) | 1 | +3 |
| 5 | R-I N-11, R-O N-O3 | S1.md target A3 shape text: `SEG_*` keys instead of `"60_180"` literals; `_in_episode` bound aligned with `window_agg` (inclusive) pending Q-22 | S1 | 2 | text only |
| 6 | R-I N-2 (part) | `_LADDER` thresholds `4` / `2` as named constants with the spec ref; S11 Unknown gate as `_a1_unknown(...)` predicate. No split of `build_a1_ability` (R-13) | S4 | 2 | ≤ +8 |
| 7 | R-I N-7 | `_is_repeat_delinquent` (Q3), `_is_straight_roller` (Q4) as Q1/Q2 were; `STATE_RULES` keys carry the Q id; state names from `STATES` | S4 | 2 | ≤ +10 |
| 8 | R-I N-4, R-E N-6 / R-I N-5 | A1 legs naming and label constants | S4 (in S2-02 row) | 2 | ≤ +8 |
| 9 | R-I on S1-04 | `scoring_engine.py:89` `kv` → `pair` | S4 | 3 | 0 |
| 10 | R-I N-14 | `_log_sequence_stats` two-line contract | S5 | 3 | +2 |
| 11 | R-I N-17, R-E N-7 | `INCOME_POINTS` / `LIQUIDITY_POINTS`: cite the GRR points table | S5 | 3 | 0 |
| 12 | R-I on S1-06 | `latest_per_account`: "remove when cc_spine is month-end" | S5 | 3 | 0 |
| 13 | R-O N-O1, N-O2 | rebase on bundle 14's workplace head before the A1 bundle; N-3 / N-4 aggregates in the A1 / A2 bundle checks | Master (bundle plan) | 1 | 0 |

**Deferred to round 3 (S1 + S4 cross-axis pass):** R-I N-10 (one spelling for `TAGS`,
`DISPLAY_NAMES`/`LOCATION_LABELS`, ladder names), R-I N-11 / R-E N-11 (key every per-segment table by
segment; `for_model` only at the third table), R-I N-15 (`build_history` split, only if S4-03 lands
cleanly).

**Not refactor work (question):** R-I N-16 → Q-26 (rule-fired columns in A1 / A4). No output
column is added in this refactor.

**No action:** R-E N-12 (functions over 40 lines from `require_columns`; allowed by the scorecard).

Estimated net: −75 (#3) +3 (#4) +2 (S2-06) +6 (S4-03) +8 (S4-09) +8 (#8) +8 (#6) +10 (#7) +6 (#1)
+2 (#10) ≈ −22 to −30; the ≤ −25 target holds only if every item stays within budget.

## Round 2 roster

| Specialist | Items | Size |
|---|---|---|
| **S4** readability | S4-02 + `_month_label`, S4-03 (part), S4-09 (RL part), #6, #7, #8 (S2-02 naming + label renames), #9 | 7 items, the bulk |
| **S2** performance | S2-06 (as `_restructure_blind_spot`), S2-03 / N-3 (window-free DCORE + naming) | 2 items |
| **S1** architecture | checked cases for S1-07 / S1-08, anchor comment, A3 target-shape text (#5) | 3 small items (the Master may fold the check script into S2's run to save one agent) |
| **S5** docstrings | `__init__` docstring, #10, #11, #12; then its usual last pass on changed files only | 4 items |
| **S3** conventions | S3-04 only if Q-15 = yes at U1; otherwise not run | 0–1 |
| S6, S7 | not run | — |

Merge order as PLAN: S1 → S3 → S2 → S4 → S5. S2 owns `build_dcore_signals` and
`cc_a4_deterioration/nodes.py` this round; S4 does not touch them.

## Convergence after round 1

| Criterion | Status |
|---|---|
| Gates green | **met** |
| No open blocking objection | not met (R-E: S1-07/08, S4-02, S4-03, S4-09; S3-01/02 waived) |
| R-O ≥ 4 on every criterion | not met (O1 3.8, O2 3.8, O3 3.7, O7 3.2) |
| R-E and R-I average ≥ 3.5 | R-I 3.86 **met**; R-E ≈ 3.30 (file average) not met |
| No new revise items | not met |

Round 2 runs. An early stop after round 2 is possible if the items above land within budget.
