# Which states drive the outcome, and how many does each case need?

## 1. Goal

A persona combines the states of all four axes. GRR may define a strategy for every persona, but for many cases one or two states probably decide the outcome (for example non-reachable with low credibility), while for others every state changes how the customer pays back. We want two answers, for cards and loans at 61–180 DPD.

1. **Book level, order-free:** how much each state contributes to ranking customers by payback.
   - The earlier comparison added states in one fixed order (reachability, then family, then credible-or-able, then the full persona). That credits shared information to whichever state enters first, so it can't say which states matter most.
   - Measure every state alone, every state dropped from the full set, and the fair share of each state averaged over all orders (Shapley).
2. **Branch level:** a transparent tree that splits the book on states only while the next state still changes payback materially and out of time. Its leaves are *decision groups*. Report how many accounts and how much money sit in groups that need 1, 2, 3, 4 or 5 states.

This is about personas and their outcomes only. No tier names (in-house / agency / non-workable) anywhere.

Use subagents where section 5 says so, and review your own work before handing anything back. There is no token limit; correctness matters more than speed.

## 2. Decided (do not re-open)

- **Persona, outcomes, schemes and fallback:** as in `persona_out_of_sample.py`, `inhouse_check.py` and `persona_value_map.py` (if present). Import or copy; don't redefine.
  - `paid`, `collected` (AED over *m*+1 … *m*+3), cure (below 61 DPD at month 3) and `rolled` as defined there.
  - Recovery = collected ÷ outstanding principal at the cohort month end, with the same field as the value map.
- **The five states (the "players"):**
  1. deterioration family (4; the 6 states as a sensitivity);
  2. location (In Country / Skip / Unknown);
  3. reachability (Reachable / Non-Reachable / Unknown);
  4. credibility band;
  5. ability band.

  Location and reachability are separate players on purpose, so we see which half of locatability does the work.
- **Cohorts:** January–May 2026 (the last complete 3-month outcome is May; payment data ends 2026-08-31).
- **Out-of-time evaluation:**
  - The main view builds on January–April pooled and tests on May.
  - Also report the adjacent scheme (build on months < *m*, test on *m*, for *m* = February–May) as the mean and min–max.
  - Never fit and score on the same month.
- **One estimator for every combination, so the comparison is fair.** A combination of states defines cells; each cell's estimate is its pooled training mean, shrunk toward the book mean with weight n ÷ (n + 20). The k = 20 is fixed, not tuned. Report the raw (unshrunk) version as a sensitivity. Test accounts in a cell unseen in training get the book mean.

## 3. Analyses and aggregates to save (cards and loans separately)

### A. Order-free contribution of each state

For all 31 non-empty subsets of the five players, plus the empty set (book mean), compute out of time:
- AUC for `paid`;
- the share of money collected captured by the top 10% and 20% of accounts;
- the Spearman correlation between the cell estimate and collected per account.

Then, per player:
1. **Alone:** the metric with that state only.
2. **Drop one:** all five minus that state, compared with all five.
3. **Shapley value:** the average gain from adding that state, over all orders. The five values add up to (all five − empty).

Report a table per metric. For AUC and money captured in the top 20%, add a bootstrap 90% interval for each Shapley value (resample accounts, 200 draws, recomputing on the test month only).

Also report:
- **pairwise overlap:** for each pair of states, the gain of the pair minus the sum of the two alone (a negative value means they carry the same information);
- the deterioration **6-state** sensitivity for the Shapley values.

### B. Decision tree: how many states does each case need?

Grow a transparent tree on 3-month **recovery**. Repeat with collected per account as a sensitivity.

- **Splits:** a split uses one state and divides its levels into two groups, with levels merged where they behave alike (binary splits, as in CART, but only on the five states). A state may be used again further down, on its remaining levels.
- **Split rule:** choose the split with the largest reduction in money-weighted squared error on the training months.
- **Stopping rules**, fixed in advance. Keep a split only if all of these hold:
  - each child has at least **300 accounts** on cards and **150** on loans, pooled training months;
  - the children's recovery differs by at least **25% relative** to the parent's;
  - **out of time:** on the May test cohort the children keep the same order, and the gap is at least half the training gap.
- Report the tree **as grown**, with no pruning on test results beyond the out-of-time rule above.

For every leaf (decision group), give:
- the path in plain words (for example "Non-Reachable · low credibility") and the **number of distinct states used**;
- accounts and share of accounts (May; and August composition);
- share of outstanding principal and of money collected;
- recovery %, paid % and AED per account, training and test;
- **within-leaf spread:** for the personas inside the leaf with at least 30 accounts, the account-weighted standard deviation and the min–max of their recovery. This shows whether the states not used really don't matter there.

Summary table: the share of accounts, outstanding and money in leaves that use 1, 2, 3, 4 and 5 states.

### C. Action-gated tree (GRR's lens)

Same rules as B, but the first split is forced on reachability (Reachable vs the rest), then grown freely. If a customer can't be reached, ability changes little about what can be done, so this shows whether credibility and ability matter mostly inside the reachable branch. Report the same leaf table and summary, and how far the forced first split loses fit against B (test-month error).

### D. Two contrasting examples

From the B leaves, pick by rule, not by story:
- the largest leaf (by accounts) that uses at most 2 states;
- the leaf with the most money that uses 4 or more states.

For each: the path, the personas inside it (≥ 30 accounts), and how their recovery varies.

## 4. Findings to write (8 lines at most per product)

1. The states ranked by Shapley value (AUC and money captured), with intervals; whether location or reachability does the work in locatability.
2. Which states overlap (carry the same information).
3. What the full persona adds over the best two- and three-state combinations, out of time.
4. The share of accounts and of money decided by 1, 2, 3 and 4+ states.
5. Whether the money concentrates in the groups that need the most states.
6. The two examples from 3D in plain words.
7. Whether the action-gated tree tells a different story.
8. How stable this is across the adjacent months.

## 5. Phases

**A. UAT, build (main agent, plus one review subagent).**
1. Write `tmp_validation/persona_deck/state_relevance.py`, reusing the persona, outcome and recovery code.
2. Implement section 3.
3. Save aggregates only to `tmp_validation/persona_deck/state_relevance_<model_id>.json` and `.md`.
4. A review subagent checks:
   - no fit and score on the same month;
   - the same estimator and k for every subset;
   - the Shapley values sum to the total gain;
   - the stopping rules applied as stated;
   - no tier names;
   - `model_id` from globals; catalog loads only.

   Then compile, commit and push.

**B. PROD (the user).** Run it for `cc_60_180` and `rl_60_180`, then commit and push the result files.

**C. UAT, analyse (main agent).** Write `tmp_validation/persona_deck/state_relevance_results.md` with:
- the findings of section 4;
- the Shapley, alone and drop-one tables;
- the leaf tables for B and C;
- the 1 / 2 / 3 / 4+ summary;
- caveats (thin loan cells, overlap of accounts across cohort months, month-grain loan payments, observed payments reflecting today's handling).

Commit and push, then paste the whole file back.

## 6. Hard rules

- Catalog loads only; `model_id` from globals; aggregates only, no customer rows; cells under 10 accounts suppressed in every output. Persona and leaf rows are aggregates and are fine.
- No pipeline, catalog, registry or axis changes.
- Nothing tuned on the test month: k, the leaf sizes, the 25% rule and the out-of-time rule are fixed as stated. Report what the data shows.
