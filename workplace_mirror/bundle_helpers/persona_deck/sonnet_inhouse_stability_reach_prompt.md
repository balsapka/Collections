# Persona framework: is the in-house list stable, and is it more than reachability?

## 1. Goal

The in-house tier is a list of personas whose expected collections per account clear a cut-off. Two concerns need honest answers, for cards and loans at 61–180 DPD.

1. **Stability.** So far the in-house list was built from one month: the May 2026 persona table, applied to August accounts. The earlier out-of-sample test (`oos_results.md`) showed that tiers keep their order and their money on unseen months. It did **not** test whether the **same personas** are in-house when the table is rebuilt on a different month. If the list moves from month to month, a strategy attached to a list of personas will not match what scoring assigns next month.
2. **Reachability.** On cards, the ten largest in-house personas are all Reachable. On loans, some Non-Reachable personas are in-house. We need to know whether the framework does more than keep the reachable customers, and how much the in-house list depends on the exact reachability definition. In particular: are there valuable Non-Reachable customers, with Moderate or High credibility or ability, that a slightly different definition or cut would bring in-house?

Use subagents where section 5 says so, and review your own work before handing anything back. There is no token limit; correctness matters more than speed.

## 2. Definitions (decided, do not re-open)

Reuse everything from `persona_out_of_sample.py` and `persona_deck_numbers.py`. Import them or copy the functions; don't redefine anything.
- **Persona** = deterioration family × locatability cell (location × reachability, 9 cells) × credibility band × ability band: the `combo` column. Credibility applies D-A3-27. Ability is the current A1 output (bundle 21 rule).
- **Outcomes** `paid`, `collected` and `rolled` over *m*+1 … *m*+3, as defined there.
- **Cohort months:** January to May 2026 (3-month outcome complete by August). The persona month for current composition is **August 2026**.
- **Tier cut-offs:** cards in-house from AED 1,250, non-workable below AED 175; loans 6,000 and 1,350. A persona needs at least 10 training accounts to get a tier.
- **Validation schemes:** *strict*, *adjacent* and *grouped K-fold by account*, exactly as in the out-of-sample test. Every out-of-sample number must come from a table trained only on data its scheme allows.

## 3. Questions and the aggregates to save

### A. Composition of the in-house tier: is it more than reachability?

1. **The in-house list today:** every in-house persona (family level, 10+ accounts), on the August accounts with the May table, the way the list was built so far. Give one row per persona, with:
   - deterioration family, location, reachability, credibility, ability;
   - August accounts and the share of in-house accounts;
   - May training accounts, paid %, AED collected per account;
   - the distance to the cut in AED.
2. **In-house accounts split by the 9 locatability cells,** cards and loans. Also: the share of in-house accounts that are Skip (abroad), and the share that are Non-Reachable or Unknown reach.
3. **Non-Reachable and Unknown-reach accounts with credibility or ability at Moderate or above:**
   - their share of all accounts;
   - out-of-sample, their paid %, AED per account and recovery %, by deterioration family;
   - which tier they land in, and how far their personas sit below the in-house cut;
   - side by side, the same figures for Reachable accounts with the same credibility or ability.
4. **How much of the ranking is reachability alone.** Out-of-sample AUC for `paid`, and the share of money captured by the top 10 / 20 / 30% of accounts, for these views:
   - R: reachability only (3 levels);
   - LR: locatability cell (9 cells);
   - FR: deterioration family × reachability;
   - FRN: family × reachability × "credible or able" (yes / no);
   - B: full persona (with the out-of-sample fallback chain).

   Also report the tier mix and in-house money share if tiers were cut from view FR instead of B. This shows what credibility and ability add on top of reachability.
5. **Effort:** call days per account in the 3 months before the cohort month, for each tier and each reachability level. This shows how hard we already tried to reach the Non-Reachable groups.

### B. Sensitivity to the reachability definition and the cut

Rebuild reachability with these variants. Use the A2 engine's own inputs and logic, changing only the stated parameter, in the validation snippet (no pipeline change):

| Variant | Change |
|---|---|
| R0 | current rule (Non-Reachable = the last 3 call days all failed, the oldest within the window, no contact since; window 3 months) |
| R1 | Non-Reachable needs the last 6 call days failed (the 180+ setting) |
| R2 | contact window 6 months instead of 3 |
| R3 | Unknown reach counted with Reachable (no recompute) |

For each variant, and for the in-house cut at −20 / −10 / 0 / +10 / +20%:
- the in-house share of accounts and of money;
- out-of-sample paid % and AED per account of the in-house tier;
- the number of in-house personas;
- which personas enter or leave the list compared with R0 at the current cut (top 10 by accounts, each with its credibility and ability).

### C. Stability of the in-house list

1. **One table per month.** For each cohort month January–May, build the persona table from that month alone and cut it. Report:
   - the number of in-house personas per month;
   - the pairwise Jaccard overlap of the in-house persona sets (a 5 × 5 matrix);
   - the account-weighted overlap: the share of August in-house accounts (under the May table) whose persona is also in-house under each other month's table.
2. **Core and flippers:**
   - the personas in-house in all 5 months and the share of in-house accounts they cover;
   - in 4 of 5 months, and the same share;
   - every persona in-house in 1–3 months, with its monthly AED per account, monthly training accounts and distance to the cut.
3. **Pooled table with a band.** Build the table from pooled months instead of one, using only the cohorts the scheme allows. Evaluate two list rules:
   - P: pooled table, the plain cut;
   - PB: pooled table with a band. A persona enters in-house at ≥ 1.1 × the cut, and once in, it stays while it is ≥ 0.9 × the cut, judged month by month in time order.

   For each rule, out-of-sample, compare with the single-month table:
   - the in-house paid %, AED per account and share of money;
   - the month-to-month list overlap;
   - the share of accounts whose tier changes while their persona stays the same.
4. **Frozen list.** Build the in-house list once, from the earliest cohorts the strict scheme allows (and from January–March under the adjacent scheme), then apply it unchanged to every later month. Compare its out-of-sample in-house paid %, AED per account and share of money with a list rebuilt every month.

## 4. Verdict to write (8 lines at most)

1. Is in-house reachable-only? Give the share of in-house accounts that are not Reachable, for cards and loans.
2. Do abroad (Skip) customers reach in-house, and how many?
3. Non-Reachable customers who are credible or able: how many, what do they pay, and where do they land?
4. How close does reachability alone (R, FR) come to the full persona (B)?
5. How sensitive is the in-house list to the reachability variants and to the cut?
6. Is the single-month in-house list stable? Give the core personas' coverage and the overlap.
7. Do pooled and band rules stabilise it, and at what cost in money captured?
8. Does a frozen list hold up on later months?

## 5. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Write `tmp_validation/persona_deck/inhouse_check.py`, reusing the persona, outcome, fallback and fold logic of `persona_out_of_sample.py`.
2. Implement sections 3A–3C.
3. Save aggregates only to `tmp_validation/persona_deck/inhouse_<model_id>.json` and `.md`.
4. A review subagent checks:
   - no leakage (time order, account grouping, the pooled and frozen tables built only from the allowed cohorts);
   - the reachability variants change only the stated parameter, and R0 reproduces the current A2 output (0 differences);
   - `model_id` from globals; catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `cc_60_180` and `rl_60_180`, then commit and push the result files.

**C. UAT, analyse (two subagents in parallel, then the main agent).**
- **C1 Reachability:** sections 3A and 3B.
- **C2 Stability:** section 3C.
- **Main agent:** write `tmp_validation/persona_deck/inhouse_check_results.md` with:
  - the key tables;
  - the verdict of section 4;
  - caveats (cohort overlap, thin loan personas, loan amounts from `int_loan_master.total_paid`, the fact that observed payments reflect today's handling, so Non-Reachable groups were worked differently).

  Commit and push, then paste the whole file back.

## 6. Hard rules

- Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed in every output. Persona rows are aggregates and are fine.
- No pipeline, catalog, registry or A2 parameter changes: the reachability variants live only inside the validation snippet.
- Don't tune anything on test data: the cut-offs and band factors are fixed as stated; the sensitivity grid is reported, not optimised.
