# Persona tiers: a mapping that stays stable for months, cards and loans

## 1. Goal

The tier mapping (persona → in-house / agency / non-workable) should hold for months, so that GRR re-runs it rarely (target: twice a year, at most quarterly) and a strategy attached to a persona keeps the same tier from one run to the next.

The in-house check (`tmp_validation/persona_deck/inhouse_check_results.md`, from `inhouse_check.py`) showed:
- **Cards:** a pooled table with a band is fairly stable. Mean list Jaccard is .80, and 5.4% of accounts change tier while their persona stays the same, at little cost. But six of the ten largest in-house personas sit within AED 100 of the cut.
- **Loans:** not stable. Only 1 persona is in-house in all five single-month tables. Jaccard is .09–.36, and 35% of accounts change tier with the same persona (13.9% even with pooling and the band). Pooling also costs 4–6 points of money share.
- **Likely causes on loans** (to confirm, not assume):
  - thin personas: 81 with a table, many monthly cells under 10 accounts;
  - heavy-tailed AED per account, where single large payments swing a persona (one went 2,906 → 6,816 → 2,669 → 7,517 → 12,848);
  - month-grain noise in `int_loan_master.total_paid`;
  - a monthly level shift that an absolute AED cut turns into list churn (loans had 8–10 in-house personas in Jan–Mar and 16–19 in Apr–May);
  - too fine a persona: location may add noise on loans.

Find **one tiering rule per product** that is stable and keeps most of the money captured. Say **how often it needs re-running**, and **what monitoring signal should trigger an early re-run**. Fix loans first; then check that the chosen design also works for cards.

If `tmp_validation/persona_deck/tier_method_<model_id>.json` exists (the earlier tier-method prompt), reuse its findings and code instead of repeating them.

Use subagents where section 6 says so, and review your own work before handing anything back. There is no token limit; correctness matters more than speed.

## 2. Decided (do not re-open)

- **Persona, outcomes, schemes, fallback chain and the 10-account minimum:** as in `persona_out_of_sample.py` and `inhouse_check.py`. Import or copy, don't redefine.
- **Value:** tiers rank personas on expected collections per account over 3 months; the non-workable group sits at the bottom. GRR sets the business cut-offs from cost. The current values (cards 1,250 / 175, loans 6,000 / 1,350) are the reference point, not a target to fit.
- **Cohorts:**
  - Use every month for which all four axes can be built and the 3-month outcome is complete as of today. Find the earliest month the inputs allow (A3 needs 12 months of history, A1 its windows, persona_start in the obs base) and report it. July 2026 is the latest month with complete outcomes.
  - **June and July 2026 are a hold-out:** never used to choose a rule, a parameter or a window. They are only used to confirm the final choice.
- Account states change month to month; that is expected. Stability here means the **persona → tier mapping**, and the account-level tier churn that comes from the mapping, not from persona moves.

## 3. Questions and the aggregates to save

### A. Why loans churn (diagnose first)

1. **Noise floor.** Bootstrap accounts within one cohort month (200 resamples). Rebuild the table and the list each time, and report the expected tier-flip rate and Jaccard from sampling noise alone. Compare with the observed month-to-month churn: what share of it is noise, and what share is real drift? Do this for loans and cards.
2. **Level shift.** Per cohort month and product: overall paid %, AED per account (mean, median, p90, p99), and the number of in-house personas. Is the churn mostly the whole book moving against a fixed AED cut?
3. **Tails.** For loans: what share of each persona's money comes from its top 1 and top 3 accounts? How much does persona AED per account move when amounts are capped at p95 / p99 of the training months?
4. **Amount source.** `int_loan_master.total_paid` is a month-end figure. If a dated customer-payment source for loans exists in the catalog (for example from `comp_financial_tran_repos_dly`, customer payments only), compare its 3-month totals with `total_paid` on one cohort. Report the share of accounts that differ by more than AED 100 and whether personas re-rank. If none exists, say so; don't build one.
5. **Granularity.** How many loan personas have 30+, 50+ and 100+ accounts per month, and what share of accounts they cover?

### B. Candidate rules (fixed list; parameters chosen on training data only)

**Estimate**
- **E1** single-month persona rate (today);
- **E2** pooled over a rolling window W ∈ {3, 6, 12} months;
- **E3** shrunk toward the parent: n ÷ (n + k) along B → family × reach × credible-or-able (FRN) → family × reach (FR) → family, with k chosen by cross-validation inside the training months;
- **E4** a coarser loan persona: drop location, or tier on FRN (FRN had AUC .749 vs .757 for the full persona on loans).

**Value metric**
- **V1** mean AED per account;
- **V2** mean with amounts capped at the training p99;
- **V3** P(paid) × capped mean amount when paid.

**Cut**
- **C1** fixed AED (current values);
- **C2** relative: the cut as a multiple of the training window's book-wide AED per account, so it moves with the level;
- **C3** rank: the in-house tier takes the personas covering the top q% of accounts, with q fixed at today's in-house share per product (non-workable the same way at the bottom).

**Hysteresis**
- **H0** none;
- **H1** the band from the in-house check (enter at 1.1 × the cut, stay while ≥ 0.9 ×);
- **H2** a minimum stay: a persona changes tier only if two consecutive runs agree.

**Do not run the full grid.** Run the diagnostics first. Then test the combinations the diagnostics point to, plus E1-V1-C1-H0 (today) and E2(6)-V1-C1-H1 (the in-house check's PB) as baselines, 10–20 combinations per product at most. Say why each one was included.

### C. Refresh cadence

For the 3–4 best rules per product: build the mapping once at month *t* and apply it unchanged for *h* = 1, 3, 6, 9 and 12 months (as far as the cohorts allow). Compare with a mapping rebuilt every month.

Report, by horizon:
- the in-house paid %, AED per account and money share;
- the money captured at equal in-house share;
- the account-weighted list overlap.

Where does the frozen mapping start losing more than 1 point of money share, or 2 points of in-house paid %?

### D. Metrics for every rule (adjacent and strict, mean and min–max)

- **Stability:**
  - the share of accounts whose tier changes while their persona stays the same, month to month and at the cadence horizons;
  - the mean list Jaccard;
  - the account-weighted overlap;
  - the number of personas within ±10% of each cut.
- **Value:**
  - in-house paid %, AED per account and money share;
  - **money captured at equal in-house share** (compare at the same capacity, since rules list different numbers of accounts);
  - the AUC for `paid`;
  - the order in-house > agency > non-workable in every fold.
- **Loans by type** (Personal, Personal Cash, Auto, from `rl_spine.loan_type`): for the final rule only, report whether it holds per type. Report the counts per type, and fall back to pooled loans where a type is too thin.

## 4. Choosing (state the rule before looking at the hold-out)

Pick per product the simplest rule that:
- keeps tier changes with an unchanged persona under 10% at the chosen cadence;
- loses at most 2 points of money captured at equal in-house share against E1-V1-C1-H0.

If none meets both, show the trade-off curve and recommend one. Then confirm the pick on June–July 2026 and report the hold-out numbers next to the validation ones.

## 5. Verdict (8 lines at most)

1. How much of loan churn is sampling noise, level shift, tails, the amount source and granularity?
2. The recommended rule per product: estimate, value metric, cut, hysteresis.
3. The stability it reaches and the value it costs, against today's rule.
4. The recommended re-run cadence per product.
5. The monitoring signal that should trigger an early re-run (for example the in-house realised paid % or the book-wide AED per account leaving a band), with the band.
6. Whether the hold-out confirms it.
7. Loan types: does one rule hold for all three?
8. What it needs from data or the pipeline (a loan payment primary, longer history), if anything.

## 6. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Write `tmp_validation/persona_deck/tier_stability.py`, reusing `inhouse_check.py` and `persona_out_of_sample.py`.
2. Implement sections 3A–3D.
3. Save aggregates only to `tmp_validation/persona_deck/tier_stability_<model_id>.json` and `.md`.
4. A review subagent checks:
   - no leakage: time order, account grouping, parameters (k, W, caps, q, band) set on training months only, June–July untouched until the confirm step;
   - the bootstrap resamples accounts, not rows;
   - `model_id` from globals; catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `rl_60_180` first, then `cc_60_180`. Commit and push the result files.

**C. UAT, analyse (two subagents in parallel, then the main agent).**
- **C1 Loans:** diagnostics, rules, cadence and loan types.
- **C2 Cards:** the same, with the chosen loan design checked on cards.
- **Main agent:** write `tmp_validation/persona_deck/tier_stability_results.md` with:
  - the key tables;
  - the verdict of section 5;
  - caveats (cohort overlap across months, thin loan personas, the fact that observed payments reflect today's handling).

  Commit and push, then paste the whole file back.

## 7. Hard rules

- Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed in every output. Persona rows are aggregates and are fine.
- No pipeline, catalog, registry or axis changes.
- Nothing is tuned on test months or the hold-out. The candidate list in 3B is fixed; anything added must be justified by the diagnostics and listed as such.
