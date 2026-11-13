# Persona value map: which personas matter, which pay, and how the most positive ones pay

## 1. Goal

One slide for senior GRR stakeholders has to answer three questions about the personas, for cards and loans at 61–180 DPD:

1. **Which personas matter most?** Their share of the book's **outstanding principal**.
2. **Which personas pay back best?** Their **recovery**, i.e. collected ÷ outstanding principal over 3 months, and their share of all money collected.
3. **How do the most positive personas pay?** Customers with High credibility or High ability, against the rest.

The planned visual is a **value map**:
- each persona is a bubble;
- x = share of the book's outstanding principal;
- y = 3-month recovery %;
- bubble size = accounts;
- a reference line at the book's average recovery.

That gives four quadrants:
- large and paying back;
- large and not paying back (the money at risk);
- small but paying back well;
- small and not paying.

A short side panel covers the High-credibility / High-ability customers.

Produce the facts behind it. They must be **robust** (not one month's noise on a thin persona) and **named in plain words**.

Use subagents where section 5 says so, and review your own work before handing anything back. There is no token limit; correctness matters more than speed.

## 2. Decided (do not re-open)

- **Persona, outcomes and the out-of-sample machinery:** as in `persona_out_of_sample.py` and `inhouse_check.py`. Import or copy; don't redefine.
  - Persona = deterioration family (and state, where asked) × locatability cell × credibility band × ability band.
  - `paid`, `collected` (AED over *m*+1 … *m*+3) and `rolled` as defined there.
- **Recovery** = collected ÷ outstanding principal at the cohort month end, as in the earlier tier work.
  - Find the outstanding principal field for cards and for loans. Report which field you used, and its coverage (share of accounts with a non-null, positive value).
  - Keep the same definition for every figure.
- **Cohorts:**
  - **May 2026** (payments June–August) is the headline, matching the deck.
  - **Pooled January–May 2026** is the robustness check. The last complete outcome is May; payment data ends 2026-08-31.
- **Composition:** August 2026 accounts for the "today" shares, as in the deck.
- **Granularity:**
  - Family-level persona, with **at least 30 accounts** in the cohort to be shown individually.
  - Personas between 10 and 29 accounts are grouped as "other small personas".
  - Under 10 accounts are suppressed.
  - On loans, report state-level personas only if they pass the same rule.
- No tier names (in-house / agency / non-workable) anywhere in the outputs. This slide is about personas, not allocation.

## 3. Aggregates to save (cards and loans separately)

### A. Book totals (May cohort and pooled)

- accounts, total outstanding principal, total collected, recovery %, paid %;
- AED collected per account;
- mean and median outstanding per account.

### B. Persona table (family level, ≥ 30 accounts)

One row per persona, May cohort, with:
- the persona in plain words, for example "Curing now · in country · reachable · moderate credibility · low ability";
- accounts and share of accounts (May; and August composition);
- outstanding principal: total, share of book, mean per account;
- collected: total, share of all collected, AED per account;
- recovery % and paid %; cure % (below 61 DPD at month 3) and roll %;
- **the pooled January–May recovery and paid %, with the monthly min–max**;
- a bootstrap 90% interval for recovery (resample accounts, 500 draws);
- a flag where the May value sits outside the pooled monthly range.

### C. Concentration

Rank the personas three ways:
- by share of outstanding;
- by share of collected;
- by recovery %.

For each ranking, report the cumulative share of outstanding and of collected held by the top 5, 10, 20 and 50 personas. Report how many personas hold 50% and 80% of outstanding. Name the top 10 by outstanding and the top 10 by collected, and say how many appear in both lists.

### D. The most positive customers

1. **Credibility band × ability band grid** (4 × 4 with Unknown, summed over the other axes). Per cell:
   - accounts and share;
   - share of outstanding and of collected;
   - recovery %, paid %, AED per account.
2. **Groups:**
   - High credibility (any ability);
   - High ability (any credibility);
   - both High;
   - either High;
   - neither High but at least one Moderate;
   - neither High nor Moderate.

   Same metrics as the grid, May and pooled, with bootstrap intervals.
3. **Within each deterioration family:** either-High vs the rest, recovery and paid %. This shows whether "High" adds value beyond being curing now.
4. **The High-band personas** (any persona containing a High band) with **at least 20 accounts pooled**. Give the persona name, accounts, recovery, paid % and AED per account, so the slide can name one or two examples.

### E. Value-map data

For every persona with at least 30 accounts (pooled, so the map is stable), give x (share of outstanding), y (recovery %), size (accounts) and the plain name. Use the book average recovery as the reference line, and say which quadrant each persona falls in (split at the book average recovery, and at the median share of outstanding). Add:
- the share of outstanding and of collected in each quadrant;
- the three largest personas by outstanding in each quadrant.

### F. Robustness

- The Spearman rank correlation of persona recovery between January–April pooled and May, over personas with at least 30 accounts in both.
- The share of personas whose quadrant is the same in the January–April and May maps.

## 4. Findings to write (6 lines at most per product)

1. How concentrated outstanding is: the number of personas for 50% and 80%.
2. Whether the personas holding the most outstanding are the ones paying back. Give the overlap of the top 10 lists and the money in the "large, not paying" quadrant.
3. The best-recovering large personas, named, with recovery against the book average.
4. How the High-credibility and High-ability customers pay against the rest, with intervals, and whether it holds within each family.
5. One or two High-band personas worth naming on a slide, or a statement that none is large enough.
6. How stable the picture is month to month: rank correlation and quadrant agreement.

## 5. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Write `tmp_validation/persona_deck/persona_value_map.py`, reusing the persona and outcome code.
2. Implement section 3.
3. Save aggregates only to `tmp_validation/persona_deck/persona_value_<model_id>.json` and `.md`.
4. A review subagent checks:
   - the outstanding principal field and recovery definition;
   - that the bootstrap resamples accounts;
   - the size rules and suppression;
   - no tier names;
   - `model_id` from globals; catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `cc_60_180` and `rl_60_180`, then commit and push the result files.

**C. UAT, analyse (main agent).** Write `tmp_validation/persona_deck/persona_value_results.md` with:
- the findings of section 4;
- the value-map table (section 3E) as a plain table ready to plot;
- the grid (3D-1);
- the High-band persona list (3D-4);
- caveats (thin loan personas, month-grain loan payments, observed payments reflecting today's handling).

Commit and push, then paste the whole file back.

## 6. Hard rules

- Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed in every output. Persona rows are aggregates and are fine.
- No pipeline, catalog, registry or axis changes.
- Report what the data shows; don't pick personas to fit a story. The slide examples come from the rules in 3B, 3D-4 and 3E.
