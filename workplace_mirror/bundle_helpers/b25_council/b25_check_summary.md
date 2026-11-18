# B25 preflight summary (4 model_ids, 2026-11-18)

Raw blocks per model_id: `rl_60_180.md`, `cc_60_180.md`, `cc_180_plus.md`, `rl_180_plus.md`
(same folder). Old = persisted output, new = `_b25` rerun after the A1/A3 / raw-extract refactor.
All four runs completed (36 tasks for rl, 40 for cc). Every "expect 0" check is 0.

## 1. Run time

| model_id    | total s | total min | tasks | slowest nodes (min)                             |
|-------------|--------:|----------:|------:|-------------------------------------------------|
| rl_60_180   |  1902.4 |      31.7 |    36 | diff 7.2, cross-product 9.4, month_end 3.7      |
| cc_60_180   |  3132.5 |      52.2 |    40 | diff 9.2, balance 7.7, limits 5.7, txns 5.8     |
| **cc_180_plus** | **4019.4** | **67.0** | 40 | diff 15.6, balance 12.1, cross-product 7.4 |
| rl_180_plus |  1910.5 |      31.8 |    36 | diff 10.3, cross-product 5.1, month_end 3.3     |
| all four    | 10964.8 |     182.7 |       | about 3.0 h if run back to back                 |

The `crx_*_b25_diff` node (full `exceptAll` of every dataset) is the single largest node on
cc_180_plus and rl_180_plus. Spark start-up adds about 1 min per run.

## 2. B25 DIFF: rows only on one side (old / new; one number when both are equal)

"all" = every row differs. `-` = dataset does not exist for that product. 0 = identical.

| dataset                    | rl_60_180 | cc_60_180 | cc_180_plus | rl_180_plus |
|----------------------------|----------:|----------:|------------:|------------:|
| a1_ability                 |       all |       all |         all |         all |
| a3_payment_credibility *   |       all |       all |         all |         all |
| a4_deterioration           |       all |       all |         all |         all |
| a3_commitment_signals *    |     21282 |    106452 |     2469172 |      426129 |
| a3_promise_events          | 12850/10560 | 53843/38373 | 279172/244596 | 22808/19322 |
| a3_strong_neg_signals **   |       207 |       826 |        3405 |         535 |
| a3_dlq_payment_signals     |         0 |         0 |       25951 |           0 |
| a3_pre_dlq_payment_signals |         0 |       222 |         561 |           0 |
| a3_payment_cycles ***      |         - |         2 |     3255960 |           - |
| a1_income_signals          |         0 |      8673 |           0 |           0 |
| a2_dcore_signals / a2_locatability |         3 |         0 |           0 |     4/22332 |
| a2_location_signals        |         0 |         0 |           0 |     0/22328 |
| a2_demographics_deceased   |         0 |         0 |           0 |     0/22304 |
| a2_way4_deceased           |         0 |         0 |           0 |     0/12004 |
| bureau_bounces_monthly     |         0 |     3/320 |           0 |           0 |
| bureau_salary_monthly **** |         0 | 23068/193041 |           0 |           0 |
| cross_product_monthly      |     0/119 |     1/120 |       1/120 |       0/119 |
| prm_card_contracts         |       0/7 |       0/7 |         0/7 |         0/7 |
| prm_card_month_end         |         0 |       1/1 |         1/1 |           0 |

\* Column `commitments_n` added (nothing dropped) in both commitment tables.
\*\* 0 differences once the six refusal / disposition columns are excluded (expected).
\*\*\* 0 differences once `due_amount` is excluded (expected).
\*\*\*\* Column `salary_source` added in cc_60_180 only.

Row counts equal old vs new everywhere except: promise_events (table 3), cross_product_monthly
(+119), prm_card_contracts (+7), cc_60_180 bureau_bounces (+317) and bureau_salary (+169973),
and the rl_180_plus A2 tables (about +22.3k rows each, way4_deceased +12,004).
Unchanged (0/0) in all four: casa, cross_product, distress, eosb, liquidity_anchor signals;
a3_episode, a3_instalments, dlq_cycles, dpd_sequences(+linked), full_history_linked,
restructure_chains, acct_windows, balance, billing, limits, transactions, prm_loan_month_end.

## 3. B25 A3 EVENTS and levels

| metric (old -> new)       | rl_60_180    | cc_60_180      | cc_180_plus      | rl_180_plus  |
|---------------------------|--------------|----------------|------------------|--------------|
| promise events (k)        | 12.9 -> 10.6 | 99.2 -> 83.7   | 279.7 -> 245.1   | 22.8 -> 19.3 |
| change                    | -17.8%       | -15.6%         | -12.4%           | -15.3%       |
| deadline 31 days after    | 553 -> 0     | 12235 -> 26974 | 12824 -> 0       | 1811 -> 0    |
| at 100 AED floor          | 58 -> 54     | 23959 -> 18693 | 155084 -> 140854 | 84 -> 76     |
| outcome paid, % events    | 69.2 -> 49.2 | 47.9 -> 30.9   | 30.9 -> 13.6     | 56.8 -> 38.6 |
| outcome none, % events    | 20.2 -> 33.5 | 48.2 -> 64.8   | 66.8 -> 83.5     | 30.5 -> 43.5 |
| refusal flag F->T / T->F  | 5 / 20       | 26 / 5         | 41 / 7           | 7 / 14       |
| thin -> no_promise rows   | 2596         | 11105          | 302529           | 53071        |
| ... as % changed rows     | 75.6%        | 75.8%          | 96.3%            | 97.4%        |
| dlq_payment_level changed | 0            | 0              | 1337             | 0            |
| pre_dlq_payment_level chg | 0            | 7              | 25               | 0            |

Event kinds
(followup_only / matched / table_only) are in each model file.

## 4. B25 A3 MOVES, DUES, state mix (latest month 2026-08-31)

| metric                    | rl_60_180 | cc_60_180 | cc_180_plus | rl_180_plus |
|---------------------------|----------:|----------:|------------:|------------:|
| scored rows               |      3985 |     19292 |      318663 |       55371 |
| A3 high % (latest month)  |       8.4 |       8.8 |         0.4 |         0.9 |
| A3 moderate %             |      32.3 |      31.4 |         4.3 |         5.0 |
| A3 low %                  |      59.3 |      59.8 |        95.3 |        94.1 |
| steps events+dues changed |       560 |      2857 |      262011 |       35465 |
| ... unknown -> low        |       263 |      2228 |      259503 |       35142 |
| ... as % of that step     |     47.0% |     78.0% |       99.0% |       99.1% |
| step refusal moves        |         8 |         5 |           6 |           6 |
| step points moves         |       713 |      4474 |        8296 |        1213 |
| recomputed state differs  |         0 |         0 |           0 |           0 |
| DUES: cards no-due stmts  |         - |     51272 |     6761920 |           - |
| DUES: ... on accounts     |         - |     13613 |      233998 |           - |
| DUES: loan windows NULL/0 |     1 / 0 |         - |           - |       2 / 2 |

A2 `unknown__unknown` / A4 `unknown` share of scored rows: cc_180_plus 77.7% / 78.2%,
rl_180_plus 75.4% / 58.7%, cc_60_180 3.2% / 0.3%, rl_60_180 6.6% / 0%.

## 5. B25 A1

| metric                             | rl_60_180 | cc_60_180 | cc_180_plus | rl_180_plus |
|------------------------------------|----------:|----------:|------------:|------------:|
| new a1 high %                      |       1.0 |       1.4 |         0.2 |         0.1 |
| new a1 moderate %                  |       8.6 |      13.5 |         5.9 |         3.3 |
| new a1 low %                       |      49.6 |      27.8 |         8.8 |        11.1 |
| new a1 unknown %                   |      40.8 |      57.4 |        85.1 |        85.4 |
| a1_state changed rows              |        21 |       674 |         207 |          53 |
| a1_income_level changed rows       |         0 |       642 |           0 |           0 |
| money_in / money_out changed       |   25 / 36 | 116 / 174 |   236 / 297 |     56 / 33 |
| cross_product / sweepable changed  |     1 / 8 |   18 / 58 |     7 / 111 |      2 / 70 |
| paid a due, F1F2F3 = 000           |     28.9% |     15.8% |        1.3% |        1.6% |
| paid a due, F1F2F3 = 100           |     50.0% |     30.4% |        9.7% |       18.9% |
| paid a due, F1F2F3 = 111           |     72.7% |     40.5% |       21.9% |       33.3% |

Largest a1_state moves: rl_60_180 moderate -> low 12; cc_60_180 moderate -> low 361, unknown ->
low 102; cc_180_plus high -> low 75 and high -> moderate 70; rl_180_plus moderate -> low 19 and
moderate -> unknown 19, high -> moderate 13.

## 6. B25 PARENT LINK (cards only)

Card contracts 4,592,922; with a parent 60,332 (1.3%); named as a parent 22,993 (0.5%).
Children per parent: 1 = 66.1%, 2 = 17.3%, 3 = 6.2%, 4+ = 10.4%. Parent not a card contract 0;
same CIF 38.8%; both with a month-end row in the latest month 66.6%.
Scored accounts: cc_60_180 19,292 (19 named as parent, 7 with a parent);
cc_180_plus 318,663 (1,687 named as parent = 0.5%, 139 with a parent).
These counts come from the shared contract build, so the contract-level numbers are identical
in both cc runs.

## 7. Points to look at

1. cc_60_180 `deadline 31 days after` goes UP (12235 -> 26974); the other three go to 0.
2. rl_180_plus A2 tables grow by about 22k rows (408,675 -> 431,003 = full obs base); the other
   three models keep their A2 row counts.
3. cc_60_180 only: bureau salary +169,973 rows with new `salary_source`, which likely
   explains the 8,673 changed `a1_income_signals` rows and 642 `a1_income_level` changes.
4. Shared builds differ by run: cross_product +119 (rl) vs +120 (cc), month_end 1/1 (cc) vs 0
   (rl); likely the old persisted copy, not the model.
5. Event mix moves toward "none" and away from "paid" in all four models, as promise events fall
   12-18%; the unknown -> low step is where most state changes arise (47-99% of those steps).
6. rl_180_plus `a1_money_in_level` has both `None` (32) and `none` (5) as new values.
