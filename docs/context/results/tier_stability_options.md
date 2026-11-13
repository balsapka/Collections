# Tier stability: options, what they mean, and results

Status (2026-11-13): **parked.** The tier mapping keeps the full persona. GRR wants the strategy to depend mainly on them, so no more work on tier rules for now. When this resumes, the first step is a longer pooling window (below).

Source: tier stability check, cc / rl 60_180, cohorts January–May 2026 (`workplace_mirror/bundle_helpers/persona_deck/tier_stability_results_handoff75.md`; the earlier in-house check is `inhouse_stability_results_handoff74.md`).

This is the drift-monitoring side of putting the tiers into use. The tier list should stay put from one run to the next, change only when the book really changes, and say when it needs re-running.

## Terms

- **Tier mapping:** the rule that puts each persona in in-house, agency or non-workable. A persona's average collection per account over 3 months is compared with the cut-offs (cards AED 1,250 / 175, loans 6,000 / 1,350).
- **Churn:** the share of accounts whose tier changes from one month's mapping to the next while their persona stays the same.
  - Accounts moving between personas is a different thing. That is expected, since customers change state.
  - Churn is the mapping itself flipping.
- **Sampling noise:** a persona's average moving only because of which accounts happened to land in it that month, not because customers behave differently.
  - A loan persona often has 10–30 accounts a month, and loan payments are lumpy, so one 40k settlement can push the average across the cut.
  - It was measured by drawing two random resamples of the same month and rebuilding the tiers from each (a bootstrap). Any flip between them is pure noise.
- **Money captured at equal share:** the money collected by the top x% of accounts, with x the same for every rule. It compares the value of rules at the same capacity, since rules list different numbers of accounts in-house.

## Options tested

| Option | What it means | Why it might help |
|---|---|---|
| **Today (E1)** | One month's data per persona, full persona, fixed AED cut | The baseline |
| **Pooling (E2)** | A persona's average over several months together (up to 6; only 1–4 were available) | More accounts per persona, so less noise |
| **Cap (V2)** | Amounts capped at the 99th percentile of the training months before averaging | One huge payment can't swing a persona |
| **Relative cut (C2)** | The cut moves with the book-wide average collection | If the whole book collects more one month, the list doesn't grow just from that |
| **Rank cut (C3)** | In-house takes the personas covering a fixed share of accounts | Keeps the list size constant |
| **Band (H1, hysteresis)** | Two lines instead of one: enter in-house at 1.1 × the cut, stay while above 0.9 ×, keep last tier in between (same at the bottom cut) | Small wobbles around the line no longer flip the tier |
| **Two runs agree (H2)** | A persona changes tier only if two consecutive runs agree | Ignores a one-off swing |
| **Shrinkage (E3)** | A small persona's average is pulled toward its parent group (family × reach × credible-or-able), the more so the smaller it is | Keeps persona detail where data supports it and borrows strength where it doesn't |
| **Coarser key (G3 = pooled + capped + relative cut on family × reach × credible-or-able)** | Tier decided on about 20–27 broader groups instead of about 200 personas; the full persona then drives the strategy within the tier | Far more accounts per group |
| **Cadence (frozen mapping)** | Build the mapping once and use it unchanged for *h* months, compared with rebuilding monthly | Shows how often it must be re-run |
| **Early re-run triggers** | A monitoring band that triggers a re-run before the scheduled one, for example in-house realised paid % or the book-wide collection per account leaving its usual range | Drift monitoring between runs |

## Results

**Why loans churn:**
- About 80% of loan churn is sampling noise. Two resamples of one month flip 27% of loan tiers, against 34% between real months; on cards it is nearly all noise.
- Loan personas are thin: 18 of 226 have 30 or more accounts a month.
- The book level does move (loans +19% from January to April), but adjusting the cut for it barely helps.

Accounts whose tier changes while the persona stays the same, month to month (adjacent scheme):

| Rule | Loans | Cards | Money captured at equal share vs today |
|---|---|---|---|
| Today (one month, full persona) | 35.0% | 12.9% | baseline |
| Pooled | 15.4% | 5.9% | about the same |
| Pooled + capped | 11.0% | 6.6% | +1.0 / +0.4 pt |
| Pooled + band | 13.9% | 5.4% | +0.6 / −0.1 pt (loans list fewer accounts) |
| Two runs agree | 8.1% | 4.9% | −0.4 / 0 pt |
| Shrinkage + capped + relative cut | 10.0% | 4.0% | +0.6 / +0.5 pt |
| **G3** (coarser key) | **4.5%** | **1.2%** | +0.3 / 0 pt |
| Relative cut, rank cut or cap alone | 25–34% | 12–13% | no stability gain |

**Cadence:**
- G3 frozen for 3 months loses nothing visible on either product.
- Full-persona pooled + band loses about 2 points of money on cards after 2 months, so it would need monthly re-runs.
- Twice a year could not be tested.

**Early re-run triggers** (the observed range over the five months, provisional):
- loans in-house paid % outside 65–80%, book collection per account outside ±20%, or in-house share outside 6–15%;
- cards 52–60%, ±10% and 14–22%.

**Loan types:** one pooled rule is equally stable for Personal, Personal Cash and Auto. On Auto, though, the tiers find no more money than the account share (lift 1.0).

**Limits:**
- Only five cohort months (payment data ends 2026-08-31), so there is no hold-out.
- The deployable test (mapping built only on outcomes known at the time) is a single month pair.
- Cadence evidence is 1–2 pairs.

## Next step when resumed

1. **A longer pooling window on the full persona.**
   - Extend the persona window back before 2026 (the user can do this), so the pool can reach 12 months.
   - Pooling was the biggest gain with only 1–4 months available. A 12-month pool may bring loans under 10% churn without the coarser key.
   - Re-test pooled, pooled + capped, pooled + band and shrinkage at W = 6 and 12.
2. **Refresh payment data past 2026-08-31,** then confirm on June onwards as a true hold-out and test cadences of 6 months and more.
3. **Refine G3 so it is acceptable** (user, 2026-11-13: G3 looks promising, but keep location in).
   - Today G3 tiers on family × reachability × credible-or-able. Credible-or-able means credibility or ability at Moderate or above, which already combines the two.
   - Candidate coarser keys to test, all with pooling and the p99 cap:
     - **K1** family × locatability cell (9 cells: location × reachability) × credible-or-able: about 72 groups;
     - **K2** family × a 5-way location-reach segment (in-country reachable, other reachable, non-reachable, unknown reach, abroad; the segments A3 V1j uses) × credible-or-able: about 40 groups;
     - **K3** family × locatability cell × a 3-level "means and will" (neither, one at Moderate or above, both or either High): about 108 groups;
     - **K4** the full persona shrunk toward K1 or K2, which keeps persona detail where the data supports it.
   - Judge each on the same churn and money measures as above, and on how many groups have 30 or more accounts a month. More groups means thinner groups again, so these go with the longer pooling window of step 1.
4. **Take Auto loans to GRR separately.**
