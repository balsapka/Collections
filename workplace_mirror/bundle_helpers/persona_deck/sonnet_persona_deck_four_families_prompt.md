# Persona deck numbers: four deterioration families, exposure = outstanding principal (follow-up)

## Goal
The deck's deterioration families change from three to four. Stabilized customers are curing now. Slow rollers and repeat delinquents have paid or cured before but are falling now. GRR will see these as different groups. Separately, the book is always measured as **outstanding principal**, not statement balance or total outstanding. Rerun the deck numbers for the 61–180 segments, and refresh the lines of `tmp_validation/persona_deck/fill_in.md` that depend on the families or on exposure.

## Decided (user, 2026-11-10)
- Families (deterioration `det_state` → `family`):
  - `stabilized` → `curing_now`
  - `slow_roller`, `repeat_delinquent` → `cure_history`
  - `straight_roller_seasoned`, `straight_roller_early_life` → `stopped_suddenly`
  - `early_payment_default` → `never_paid`
  - anything else → `unknown`, as now.
- Exposure (`exposure_amt`, every AED figure) = **outstanding principal** in the observation month, for cards and loans alike. It replaces `crx_cc_balance.stmt_balance` (cards) and `crx_rl_full_history.outstanding_balance` (loans). Find the principal column in the catalog datasets the persona code already reads (prm_ / int_ / crx_, never stg_ or raw_). Report the dataset and column you use per product. If no outstanding-principal column exists for a product, stop and say so; don't substitute another balance.
- The action segment `cure_reach_cred` keeps its meaning: family `curing_now` **or** `cure_history`, reachable, credibility High or Moderate. So every action segment's share and paid %, the risk-score table and the pilot volumes must come out identical to the last run. That is the regression check. Only the AED figures change.
- Only `cc_60_180` and `rl_60_180` are rerun. The 180+ numbers in the deck don't depend on the families.

## Hard rules
- Edit **your** version of `tmp_validation/persona_deck/persona_deck_numbers.py` (commit 5fc0e8f3 and later). Keep every fix you made to it: payments rebuilt from `crx_cc_transactions` / `int_loan_master`, `crx_rl_dpd_sequences_linked`, NULL buckets, the A2 default, `element_at` guards, the `bt_accounts` suppression and the output folder.
- Catalog loads only. `model_id` comes from globals. Aggregates only: no customer rows in any output.

## Changes to the script
1. `FAMILY` mapping as above, plus a constant `CAN_CURE = ("curing_now", "cure_history")`.
2. The `action` column: `F.col("family") == "can_cure"` becomes `F.col("family").isin(*CAN_CURE)`. No other change to the segments.
3. Two new tables next to `a1_family_x_band`:
   - `a1_state_outcome` = `_rates(bt, ["det_state"])`;
   - `a1_state_x_band` = `_rates(bt, ["dpd_band", "det_state"])`.
4. `_exposure`: outstanding principal as above, same point-in-time join to the observation month.
5. Combinations:
   - `possible` = number of distinct families in `FAMILY` (4) × 3 × 3 × 4 × 4 = 576;
   - add `non_empty_known_family`: non-empty combinations whose family is not `unknown`.

## Deliverables
1. **UAT:** apply the changes, check that the script still compiles, then commit and push.
2. **PROD (user):** run the script for `cc_60_180` and `rl_60_180`. Commit and push the two refreshed `deck_<model_id>.md/.json` files.
3. **UAT:** update `fill_in.md`. Replace only the sections below, then commit and push. Paste back these sections plus the regression check, nothing else:
   - **A1 Deterioration:**
     - family shares, cards and loans 61–180 (four families, plus unknown if above 0.5%);
     - paid within 3 months by family, overall and within each DPD band, cards and loans;
     - paid within 3 months by deterioration state (all six), overall and within each DPD band, cards and loans (`a1_state_outcome`, `a1_state_x_band`; mark cells under 10 accounts);
     - one line verdict: within most DPD bands, does `curing_now` pay at least 5 pts more than `cure_history`? Answer for cards and loans separately.
   - **Part 2, combinations:** possible / non-empty / non-empty with a known family / empty (= possible − non-empty with a known family) / number covering 80% / number under 0.5%, cards and loans; and the top 8 for cards 61–180 (share % · paid %).
   - **Summary:** % of reachable 61–180 who are credible or able, with AED m on outstanding principal, cards and loans.
   - **Part 2, action:** share, AED m (outstanding principal) and paid % for the six segments, cards and loans; total AED m of the 61–180 book per product.
   - **Part 2, tree:** share and paid % for each family × nuance leaf, cards 61–180 (four families × three leaves; mark leaves under 10 accounts).
   - **Regression check:** confirm that the shares and paid % in `action`, plus `score_action` and `volume`, match the previous run for both model_ids, to the decimal. List any difference. AED is expected to change.
   - **Exposure source:** dataset and column used for each product.
