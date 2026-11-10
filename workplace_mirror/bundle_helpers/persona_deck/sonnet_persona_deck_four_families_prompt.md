# Persona deck numbers: four deterioration families, outstanding principal, credibility Unknown rule (follow-up)

## Goal
The deck's deterioration families change from three to four. Stabilized customers are curing now. Slow rollers and repeat delinquents have paid or cured before but are falling now. GRR will see these as different groups. Separately, the book is always measured as **outstanding principal**, not statement balance or total outstanding. Third, credibility Unknown narrows: an account with an observed delinquency episode but no evidence is Low. Rerun the deck numbers for all four segments, and refresh the lines of `tmp_validation/persona_deck/fill_in.md` that depend on the families, on exposure or on credibility.

## Decided (user, 2026-11-10)
- Families (deterioration `det_state` → `family`):
  - `stabilized` → `curing_now`
  - `slow_roller`, `repeat_delinquent` → `cure_history`
  - `straight_roller_seasoned`, `straight_roller_early_life` → `stopped_suddenly`
  - `early_payment_default` → `never_paid`
  - anything else → `unknown`, as now.
- Exposure (`exposure_amt`, every AED figure) = **outstanding principal** in the observation month, for cards and loans alike. It replaces `crx_cc_balance.stmt_balance` (cards) and `crx_rl_full_history.outstanding_balance` (loans). Find the principal column in the catalog datasets the persona code already reads (prm_ / int_ / crx_, never stg_ or raw_). Report the dataset and column you use per product. If no outstanding-principal column exists for a product, stop and say so; don't substitute another balance.
- **D-A3-27, credibility Unknown:** no payment while delinquent is evidence (0 points). So an A3 row with `a3_unknown_reason = 'no_evidence'` counts as **Low** in the deck; Unknown is left only for `no_episode`. The A3 pipeline gets the same change in a later bundle; until then the snippet applies it.
- The action segment `cure_reach_cred` keeps its meaning: family `curing_now` **or** `cure_history`, reachable, credibility High or Moderate.
- Regression check: `never_paid`, `not_reachable`, `cure_reach_cred` and `stopped_reach_means` keep their shares and paid % to the decimal. Only `reach_notcred_means` and `other` may move, because some reachable Unknown-credibility accounts with means become Low. AED figures change with the exposure.
- All four model_ids are rerun: the credibility change touches the 180+ mix too.

## Hard rules
- Edit **your** version of `tmp_validation/persona_deck/persona_deck_numbers.py` (commit 5fc0e8f3 and later). Keep every fix you made to it: payments rebuilt from `crx_cc_transactions` / `int_loan_master`, `crx_rl_dpd_sequences_linked`, NULL buckets, the A2 default, `element_at` guards, the `bt_accounts` suppression and the output folder.
- Catalog loads only. `model_id` comes from globals. Aggregates only: no customer rows in any output.

## Changes to the script
1. `FAMILY` mapping as above, plus a constant `CAN_CURE = ("curing_now", "cure_history")`.
2. Credibility band: load `a3_unknown_reason` with the A3 output; band = `'low'` where it is `'no_evidence'`, else the band of `a3_state` as now.
3. The `action` column: `F.col("family") == "can_cure"` becomes `F.col("family").isin(*CAN_CURE)`. No other change to the segments.
4. Two new tables next to `a1_family_x_band`:
   - `a1_state_outcome` = `_rates(bt, ["det_state"])`;
   - `a1_state_x_band` = `_rates(bt, ["dpd_band", "det_state"])`.
5. `_exposure`: outstanding principal as above, same point-in-time join to the observation month.
6. Combinations:
   - `possible` = number of distinct families in `FAMILY` (4) × 3 × 3 × 4 × 4 = 576;
   - add `non_empty_known_family`: non-empty combinations whose family is not `unknown`.

## Deliverables
1. **UAT:** apply the changes, check that the script still compiles, then commit and push.
2. **PROD (user):** run the script for `cc_60_180`, `rl_60_180`, `cc_180_plus` and `rl_180_plus`. Commit and push the four refreshed `deck_<model_id>.md/.json` files.
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
   - **A3 Payment credibility, 61–180:** High / Moderate / Low / Unknown, cards and loans (`mix_a3_band`); roll % at 91–120, High vs Low, cards (`a3_band_x_band`); untested share, cards and loans (`a3_untested`).
   - **Regression check:** as in Decided: list every change in `action`, `score_action` and `volume` against the previous run for the 61–180 model_ids, and confirm that only `reach_notcred_means` and `other` moved (AED aside).
   - **Exposure source:** dataset and column used for each product.
   - **A3 Payment credibility at 180+:** High / Moderate / Low / Unknown shares for cards 180+ and loans 180+, from `mix_a3_band` in the refreshed 180+ files; also the 180+ positive-signal share, cards and loans (`positive_signal`), to confirm it did not move.
