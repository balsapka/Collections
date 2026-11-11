# Persona framework: how many personas occur, and how concentrated the in-house tier is

## 1. Goal

We need three counts, for cards and loans at 61–180 DPD:

1. how many personas occur when deterioration is read at **state** level, not family level;
2. how many of those have enough accounts to judge;
3. how many personas make up the in-house tier, and how few of them cover most in-house accounts.

This is a small job: aggregate counts on top of `tmp_validation/persona_deck/persona_deck_numbers.py`. Review your own work before handing anything back.

## 2. Definitions (decided, do not re-open)

**State-level persona** = `det_state` × locatability cell (location × reachability, 9 cells) × credibility band × ability band.
- `det_state` has six values: early payment default, stabilized, repeat delinquent, seasoned straight roller, early-life straight roller, slow roller. Count `unknown` separately if it occurs.
- Credibility band applies D-A3-27: `a3_unknown_reason = 'no_evidence'` counts as Low.
- Ability band: High / Moderate / Low / Unknown, as in the script today.
- Possible personas = 6 × 9 × 3 × 4 = 648. Confirm the level counts actually present.

**Family-level persona** = the script's `combo` (family × cell × credibility band × ability band).

**Month:** the latest persona month, August 2026, the same month as the script's mix tables.

**Tiers:** as in the script (`_with_tier`). Persona rates come from the May 2026 back-test, collections in June–August.
- Cut-offs, AED collected per account: cards in-house ≥ 1,250, non-workable < 175; loans in-house ≥ 6,000, non-workable < 1,350.
- Set `TIER_CUTS` to these values if they are still unset in your copy.
- Tiers are assigned per family-level persona.

## 3. What to compute (cards `cc_60_180`, loans `rl_60_180`)

**A. State-level personas, August 2026**
- possible, occurring (at least 1 account), with 10+ accounts;
- accounts in personas under 10 accounts: count and share;
- median accounts per occurring persona;
- the same three counts at family level, for comparison with the script's `combos` block.

**B. In-house tier concentration, August 2026 accounts**
1. Number of family-level personas in the in-house tier, and the in-house share of accounts.
2. Sort the in-house personas by accounts, descending. Report how many it takes to cover 50 / 80 / 90% of in-house accounts.
3. The top 10 in-house personas, each with:
   - its four states in plain words;
   - share of in-house accounts;
   - back-test paid % and collected per account.
4. Within in-house accounts, the number of distinct **state-level** personas, and how many cover 80% of in-house accounts.

## 4. Phases

**A. UAT.** Write `tmp_validation/persona_deck/persona_counts.py`. Reuse the script's base frames and helpers (import or copy), rather than rebuilding the axes.

It saves aggregates only to:
- `tmp_validation/persona_deck/persona_counts_<model_id>.json`
- `tmp_validation/persona_deck/persona_counts_<model_id>.md`

Compile, commit, push.

**B. PROD (the user).** Run for `cc_60_180` and `rl_60_180`, then commit and push the result files.

**C. UAT.** Write `tmp_validation/persona_deck/persona_counts_results.md`:
- one table for section A;
- one table for section B with the top 10 lists;
- three lines of caveats (for example, small personas on loans).

Commit, push, and paste the whole file back.

## 5. Hard rules

- Catalog loads only.
- `model_id` from globals.
- Aggregates only, no customer rows; cells under 10 accounts suppressed in every list. Counts of personas are fine.
- No pipeline, catalog or registry changes.
