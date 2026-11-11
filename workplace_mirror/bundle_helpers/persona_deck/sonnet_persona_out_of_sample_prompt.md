# Persona framework: out-of-sample test of the personas, tiers and DPD bucket

## 1. Goal

So far every ranking result for the persona framework was measured **in-sample**: the payment rate of each group was learned and scored on the same back-test month (May 2026). We now need honest, out-of-sample answers to three questions, for cards and loans at 61–180 DPD:
1. Do the **personas** rank who pays better than the **DPD bucket** alone, and by how much?
2. Does the bucket still add something **within** the personas? If so, a risk score has room to rank customers within the personas.
3. Are the **allocation tiers** stable out-of-sample: do in-house, agency and the non-workable pool deliver similar money and recovery on unseen months, and do accounts keep their tier?

Use subagents where section 5 says so, and review your own work before handing anything back. There is no token limit; correctness matters more than speed.

## 2. Definitions (decided, do not re-open)

- **Persona** = the combination of an account's four axis states in a month: deterioration family (`curing_now`, `cure_history`, `stopped_suddenly`, `never_paid`, `unknown`), locatability cell (location × reachability, 9 cells), credibility band, ability band. This is the `combo` column of `persona_deck_numbers.py`. The credibility band applies D-A3-27: `a3_unknown_reason = 'no_evidence'` counts as Low.
- **Outcome**, for an account in cohort month *m*:
  - `paid`: a meaningful payment in months *m*+1 … *m*+3, meaning in at least one month a payment of at least the amount that stabilises the bucket (cards: the oldest overdue bucket amount; loans: one EMI). Use the same definition the script already uses.
  - `collected`: the total amount paid in *m*+1 … *m*+3 (AED).
  - `rolled`: the bucket at *m*+3 is worse than at *m*.
- **Cohort months:** every month from January 2026 whose 3-month outcome is complete by August 2026, that is January to May 2026. Report the cohort sizes.
- **Tiers:** expected collections per account (AED collected in 3 months) per persona, with the cut-offs used so far: cards in-house from AED 1,250 and non-workable below AED 175; loans 6,000 and 1,350.
- **Fallback for small groups:** a persona with fewer than 30 training accounts takes the rate of its family × locatability cell. If that has fewer than 30, it takes its family's rate; otherwise the overall rate. Report how many test accounts used each fallback level.

## 3. Views to compare (each scored out-of-sample)

| View | Score for a test account = training rate of … |
|---|---|
| A. DPD bucket only | its DPD band (61–90 / 91–120 / 121–150 / 151–180) |
| B. Persona | its persona (with the fallback) |
| C. 3 tiers | its tier, from the training month(s) persona collections and the fixed cut-offs |
| D. Persona × bucket | its persona within its DPD band (fallback: persona, then the persona fallback chain) |
| E. Tiers × bucket | its tier within its DPD band |
| F. Simple model (risk-score preview) | a regularised logistic regression on one-hot axis states (4 axes) + DPD band, fitted on the training data |

For F, also fit a version with interactions limited to deterioration × locatability, if it converges. Keep it simple: this is a preview of whether a risk score adds anything, not the risk score.

## 4. Two validation schemes

1. **Rolling time split** (production-like). Train on earlier cohorts and test on a later one. Use both:
   - *strict:* train only on cohorts whose outcomes are fully known when the test month is scored (cohorts ≤ *m* − 3; possible tests: April with January, May with January–February);
   - *adjacent:* train on all cohorts before *m* (tests: February … May, expanding window).
2. **Grouped K-fold by account** (5 folds across all cohort months pooled). All months of an account sit in the same fold, so an account is never in training and test at once.

Report every fold, plus the mean and the spread (min–max) across folds.

## 5. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Write `tmp_validation/persona_deck/persona_out_of_sample.py`, reusing the persona, outcome and payment logic of `persona_deck_numbers.py` (import it or copy the functions). Compute the persona, DPD band, `paid`, `collected` and `rolled` for every cohort month January–May 2026.
2. Implement views A–F and both validation schemes.
3. Save aggregates only (no customer rows) to `tmp_validation/persona_deck/oos_<model_id>.json` and `.md`.
4. A review subagent checks:
   - no training data leaks into a test fold (time order; account grouping);
   - the fallback chain;
   - the definitions in section 2;
   - `model_id` from globals, catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `cc_60_180` and `rl_60_180`, then commit and push the result files.

**C. UAT, analyse (two subagents in parallel, then the main agent).**
- **C1 Ranking:** for each view and scheme, cards and loans:
  - AUC for `paid` and for `rolled` (every fold, mean, min–max);
  - the share of money collected and of payers captured by the top 10 / 20 / 30% of test accounts ranked by each view's expected collections (views B–E) or predicted probability (F);
  - the in-sample AUC beside it (training month scored on itself), so the gap is visible.
- **C2 Tiers:**
  - per tier, out-of-sample: share of test accounts, paid %, collected per account, recovery % (collected ÷ outstanding principal), share of payers and of money (every fold, mean, min–max);
  - tier stability: the share of accounts whose tier changes from month *m* to *m*+1 (their persona changed vs their persona's tier changed);
  - whether the fixed cut-offs still separate the tiers on unseen months.
- **Main agent:** write `tmp_validation/persona_deck/oos_results.md` with:
  - the two tables above;
  - a verdict of 6 lines at most:
    1. Do personas beat the bucket out-of-sample, by how much?
    2. Does the bucket add within personas (D vs B, E vs C)?
    3. Does the simple model F beat the persona rate table?
    4. Are the tiers stable?
  - caveats (cohort overlap, small personas, loan amounts from `int_loan_master.total_paid`).

  Commit and push, then paste the whole file back.

## 6. Hard rules

- Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed in every output.
- No pipeline, catalog or registry changes: this is a validation snippet in `tmp_validation/`.
- Don't tune the tier cut-offs on test data: they stay fixed as in section 2.
