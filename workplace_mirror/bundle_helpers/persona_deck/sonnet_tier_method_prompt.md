# Persona framework: one tiering method that works for every product

## 1. Goal

The out-of-sample test (`tmp_validation/persona_deck/oos_results.md`) showed that the allocation tiers keep their order on unseen months for both cards and loans. On cards the fixed AED cut-offs also hold. On loans the exact cut-offs drift: the loan book has about 5,400 accounts spread over about 210 personas, only about 20 of them with 30 or more accounts, so each persona's average collection is noisy.

We need **one tiering method that holds for every product**, including the loan types separately (Personal, Personal Cash, Auto), since Auto behaves differently from personal loans. Test a small set of methods out-of-sample and recommend one.

Use subagents where section 5 says so, and review your own work before handing anything back. There is no token limit.

## 2. Definitions (decided, do not re-open)

As in the out-of-sample test:
- **Persona:** the `combo`, i.e. deterioration family × locatability cell × credibility band × ability band, with D-A3-27 applied.
- **Outcomes:** `paid`, `collected` (AED in 3 months) and `rolled`; recovery = collected ÷ outstanding principal.
- **Cohorts:** January–May 2026.
- **Validation schemes:** strict, adjacent and grouped 5-fold by account.
- **Tiers:** in-house / agency / non-workable, ranked on expected collections per account.
- **Loan type:** from `rl_spine.loan_type` (Personal, Personal Cash, Auto). Report how many accounts each type has per cohort.

## 3. Methods to compare

**How each account's expected collections are estimated**
- **E1 Single-month persona rate** (today's method), with the fallback chain below 30 accounts.
- **E2 Pooled persona rate:** the persona's average over all training months together, with the same fallback.
- **E3 Shrunk persona rate:** each persona's rate pulled toward its family × locatability parent in proportion to its size (empirical Bayes or a simple credibility weight, n ÷ (n + k), with k chosen on the training data only).
- **E4 Model score:** a regularised regression on one-hot axis states (and loan type for loans) predicting `collected`. A two-part model (P(paid) × amount if paid) is fine if a direct regression is unstable.

**How the cut-offs are set**
- **C1 Fixed AED:** the current cut-offs (cards 1,250 / 175; loans 6,000 / 1,350).
- **C2 Share of money:** cut on the training data so that the non-workable group holds about 5% of money collected and in-house about 45%, then apply the AED values found to the test data.
- **C3 Share of accounts:** cut on the training data at fixed account shares (for example 15% in-house, 30% non-workable), then apply the values found to the test data.

**Granularity:** cards; loans pooled; and loans by type (Personal, Personal Cash, Auto), with separate cut-offs per type. If a type is too small for a reliable estimate (say under 500 accounts per cohort), say so and fall back to pooled loans for it.

## 4. What to measure (out-of-sample, every fold, mean and min–max)

Per method (E × C) and per product or loan type:
1. **Separation:** collected per account, recovery %, paid %, share of money and share of payers per tier. Report whether the order in-house > agency > non-workable holds in every fold.
2. **Threshold stability:** for C2 and C3, how much the AED cut-offs found on each training set move across folds. For C1, how often the test tiers miss their AED band.
3. **Tier stability:** the share of accounts changing tier from month *m* to *m*+1, split into persona changed vs persona's tier changed.
4. **Ranking:** AUC for `paid` and capture of money in the top 20% (E1–E4), so the gain or loss in ranking from smoothing is visible.

## 5. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Extend `persona_out_of_sample.py`, or write `tier_method_test.py` next to it, reusing its cohorts, outcomes, folds and fallback.
2. Implement E1–E4 and C1–C3 for cards, loans pooled and each loan type.
3. Save aggregates only to `tmp_validation/persona_deck/tier_method_<model_id>.json` and `.md`.
4. A review subagent checks:
   - no test data used when estimating rates, shrinkage weights or cut-offs;
   - loan type mapping;
   - `model_id` from globals, catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `cc_60_180` and `rl_60_180`, then commit and push.

**C. UAT, analyse (two subagents in parallel, then the main agent).**
- **C1** cards and loans pooled; **C2** loan types.
- **Main agent:** write `tmp_validation/persona_deck/tier_method_results.md` with:
  - a comparison table;
  - a recommendation of 6 lines at most: one method (E and C) for all products, the cut-offs it gives per product or loan type, how stable they are, and what it costs in ranking power versus E1;
  - caveats.

  Commit and push, then paste the whole file back.

## 6. Hard rules

Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed. No pipeline, catalog or registry changes. Never tune anything on test folds.
