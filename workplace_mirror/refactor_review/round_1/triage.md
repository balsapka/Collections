# Round 1 triage (= round 2 brief)

Reviews: R-E 3.5 (shared layer and engines 3.75), R-I 4.05, R-O about 4.15 (O1 3.9, O2 3.8 below 4).
No blocking objection from R-E or R-I on anything applied. R-O: one blocking revise (S3-04).
Gates on `a6a0b95`: all pass (oracle 188 datasets; smoke = the six baseline lines).

## Keep (R-O accepts, no reviewer blocks)

S7 B-01/02/03/05 · S1-01..09 · S3-02, S3-09, S3-10 · S2-01, -02, -04, -05, -07, -08, -09 · S4-01, -02,
-03, -05, -07, -08, -10, -11, -13, -14, -15 · S5.

## Round 2 items (specialists run one after another on the branch; gates before each commit)

| # | Owner | Item | Source |
|---|---|---|---|
| 1 | S2 | S2-11: no `F.broadcast(obs)` in the cross-product feature (2.4M rows on the driver at cc_180_plus): drop the hint or scope the products to the obs CIFs | R-O revise, must be done before the bundle |
| 2 | S3 | S3-04: drop `account_group_id` and `balance` from the `raw_stg_balance` check (only the unmirrored `prm_cc` reads them; no gate verifies the names) | R-O revise, **blocking** |
| 3 | S3 | S3-01: one `require_columns` (`_common` re-exports `frames`), keeping `_common`'s error wording | held -> apply (R-O, R-E, R-I) |
| 4 | S3 | The episode contract is checked once where the episode is built, not five times in `a3_credibility/signals.py` | R-E N-3 |
| 5 | S3 | A3 state log label carries the model_id like the other axes (a log line change, listed for the bundle) | R-O N-1 |
| 6 | S1 | S1-06: drop the redundant `age == 0` branch in `_with_carry`; one comment on why a 0 row stops older rows | R-E + R-I revise |
| 7 | S1 | The persona-start floor is computed in A1 `_floor` and again in the RL anchor: one helper | R-E N-1 |
| 8 | S4 | S4-04 narrowed: locals only for the three signal-output dataset names typed twice in `create_a3_pipeline` (stays under 15 locals) | R-O, R-I |
| 9 | S4 | S2-01 follow-up: name the `later` field in `_contact_summary` and declare the disposition order as a constant instead of relying on label spelling (same order as today: oracle must pass) | R-I revise |
| 10 | S4 | Promise floor gets its own constant (`PROMISE_MIN_AED = MIN_PAYMENT_AED`), so Dimension B's floor and the promise floor can move apart | R-I N-2 |
| 11 | S4 | `_cutoff`: the deadline options live in one place beside `DEADLINES`; the literal 30 is named | R-I N-4 |
| 12 | S5 | `_latest_in_month` docstring states the tie rule; docstrings of anything items 1-11 touch | R-O (D-1-3) |

## Dropped (logged, not proposed again)

S3-11 (R-E reject, R-O drop) · S2-12 (to the `cc_raw_extract` primary bundle, Q-R-06 b) · S4-06 (R-E blocking,
R-O: to the carry bundle; R-I wanted it now, R-O decides) · S4-16 (run 1 D-3-1: renaming a shared symbol
for wording is churn; R-E wanted it, R-I wanted another name) · S3-03, S3-07 (skips upheld; R-E's re-raise of
S3-03 overruled) · S3-05, S3-06, S3-08, S2-06, S4-09 (duplicates) · R-E's revise of S4-03 (R-O accepts S4-03 as
applied) · R-I N-3 (deadline plumbing through `build_a3_credibility`: output column, later) · R-I N-5, N-7,
N-8 (dataset names are fixed, hard rule 5).

## R-O rulings

- D-1-2 upheld narrowly: "no new message" only for files whose messages are all E0401 / E0611 on unmirrored
  imports plus their baseline C0411; `gates.md` records each such file's baseline message set.
- D-1-3: S2-10 stays. Conditions: tie rule in the docstring; the bundle check counts `prm_card_month_end` keys
  with two or more rows on the latest day per model_id; an A1 difference is allowed only on CIFs holding such
  a card.
- R-E vs R-I: single-use helpers that name a spec concept stay; `HISTORY_MONTHS` stays derived; the contract
  lists stay; `promises.py` stays its own module; `require_columns` line growth is allowed.
- `cc_raw_extract/nodes.py` (tier K): O2 = 2 recorded as an exception (a 345-line diff on a module the mirror
  cannot import); UAT reviews its `MERGED` result explicitly.

## Waiting on the user (U1): `questions.md`

Before the bundle is built: Q-S6-01 (D-A3-29 on matched runs). Held code: Q-R-01 (dead packages, needs the
workplace grep; R-O: its own bundle after 25), Q-R-02, Q-R-03, Q-R-04.

## Bundle 25 plan items for the Master (R-O)

Renamed / moved / removed list (in `gates.md`); two-step check with the tie-key split; run times for A1 EOSB
and the cross-product join on cc_180_plus; UAT `MERGED` review of `cc_raw_extract`; top-level catalog keys
before and after the apply; workplace grep extended to `lookback_floor`, `pit_latest(anchor=`, the old
`build_cc_acct_windows` import path, `PRODUCT_TYPES`, and the two CASA features.
