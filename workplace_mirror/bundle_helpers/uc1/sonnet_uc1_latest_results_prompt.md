# UAT Sonnet prompt: UC1 latest results and strategy impact (for the workshop)

Paste everything below the line into the UAT Sonnet session. Deadline: results the same day.

---

Goal
Recompute the UC1 workshop findings on UC1's August refresh (export snapshot 2026-08-31, 19,617 CIFs; the earlier
results used the 2026-10-31 cut with 5,040 CIFs) and size what each integration idea would touch in the collection
book. Output = tables the user can put in front of GRR tomorrow. Data understanding and sizing only: no pipeline
change, no new rules.

Decided (do not reopen)
- Axis numbers: A1 deterioration, A2 locatability, A3 credibility, A4 ability. Dataset names unchanged
  (`crx_<p>_a1_ability` holds the A4 ability states, `_dpd_journey` outputs are A1). Use the new numbers in text.
- State per signal = UC1's `estimated_value`, as is (transcripts and remarks). Apply the stated-block mapping by
  calling the functions in `crx_persona/uc1_stated/classify.py` (a tie takes the more cautious level), not by
  re-coding it. Stated ability = able / partly able / unable / not stated / no reading; stated intent = pays in full
  / partly or later / refuses / not stated / no reading; reason = lost / reduced / has employment, increased
  obligations, not stated.
- UC1 sits beside A1–A4 as a stated layer; it never changes an A1–A4 state. Ideas to size: (F) fill: stated
  ability orders cards inside A4 Unknown; (T) treat: delinquency reason as a hint; (C) context: last stance and
  call date for the collector; (R) recheck: stated intent inside A3 no_promise on loans; (P) 180+: customers with a
  recorded call.
- Unlogged promises and extraction precision are closed: do not measure them.
- No minimum n; show n beside every share; 95% intervals from 200 account resamples for the differences quoted.

Two readings, side by side
- R1 (continuity with the workshop doc): the export's `estimated_value` at the 2026-07-31 month end, outcome =
  August payments. Label it: the export uses evidence up to 08-31 (about 100 card remark days after 07-31).
- R2 (point in time, several month ends): `signal_level_posteriors`, top level per CIF × signal (ties: more
  cautious), at month ends 2026-04-30, 05-31, 06-30, 07-31, each with the next month's payments; pooled and per
  month end. Add evidence age (latest `proposer_level_observations` date on or before the month end, from the
  08-31 partition only) and a variant with evidence in the last 90 days only. Three-month outcome for 04-30 and
  05-31 as a check. Posteriors are not an agreed input: label R2 as an assessment.

What to produce (cc_60_180 and rl_60_180 in full; cc_180_plus and rl_180_plus only for P and coverage)
1. Coverage: accounts, A2 reachable, accounts with a UC1 reading (R1; R2 per month end, any age and ≤ 90 days),
   split transcript only / remark only / both.
2. Findings table, R1 and R2 pooled: paid_due (next-month payments ≥ max(due, 100 AED)) by
   - stated ability inside A4 Unknown, with AUC (able > partly > not stated > unable) and the no-reading group;
   - delinquency reason (all accounts with a reading, and inside A4 Unknown);
   - stated intent inside A3 no_promise and inside A3 promised;
   - having a reading vs not, inside A2 reachable (the selection check: earlier, readers paid 7 pp less).
   Transcript-based vs remark-only readings apart for ability and intent.
3. Money: accounts, outstanding, amount due, paid of due (sum of next-month payments / sum of due) for the whole
   book, accounts with a reading, A4 Unknown, A4 Unknown × stated ability, R1 at 07-31 and R2 pooled. CC
   outstanding: use the snapshot on the month end where it exists and say what share is exact (earlier only 71 of
   18,397 were); RL is exact.
4. Impact sizing per idea, per month end (R2) and at 07-31 (R1):
   - F: card A4 Unknown accounts and amount due with a stated ability; share of that tier's payers found in the
     "able / partly able" group vs its share of accounts (what ordering inside the tier would buy).
   - T: accounts and amount due with lost or reduced employment, by A2 reachable and A4 state; their paid_due vs
     has employment.
   - C: share of accounts with any UC1 record (any age, ≤ 90 days), by A2 reachable × A3 level: how often a
     collector would see a card.
   - R: loan accounts in A3 no_promise with a stated intent, and their paid_due by intent.
   - P: 180+ accounts whose CIF had a recorded call (read by UC1 or not) in the 90 days before the month end,
     their paid_due and amount due vs the rest.
5. Every integration idea, old vs new: one row each, both products, with the earlier figure (bundle 31, July end,
   old export), the R1 figure, the R2 pooled figure with its 95% interval, n, and a verdict stronger / same / weaker
   / still no signal. Include the dropped ideas: more coverage (mostly remarks) could revive them.

   | # | idea (where it would land) | earlier figure |
   |---|---|---|
   | 1 | stated ability inside A4 Unknown (fill) | cards able 27.3% (33) / partly 15.7% (108) / not stated 13.9% (101) / unable 6.9% (72), no reading 6.5%, AUC 0.613 (n 314); loans AUC 0.47 (n 98) |
   | 2 | delinquency reason (treat) | loans has employment 43.9% vs lost 23.3%; cards 17.3% vs 14.1%; cards in A4 Unknown 14.9% vs 10.8%, reduced 4.3% |
   | 3 | stated intent inside A3 no_promise (fill / recheck) | loans pays in full 22.2% vs partly 23.7%, AUC 0.52 at July; 34% vs 18%, AUC 0.61 pooled Apr-Jul (interim) |
   | 4 | stated intent inside A3 promised and partly kept (does a stated plan mean more where promises held?) | not measured |
   | 5 | payment period: weeks / salary cycle / months (treat) | specific statements went with payment on the sample; not measured on the export |
   | 6 | amount or date named with a paying intent (treat / context) | not measured on the export |
   | 7 | says able or pays in full while A4 Low (cross-check flag, dropped) | cc 20.0% vs 19.4%, rl 32.6% vs 33.1% |
   | 8 | says unable while A4 High / Moderate (cross-check flag) | not measured |
   | 9 | dispute stated; request stated (open-issue flags, dropped as risk signals) | no payment signal |
   | 10 | UC1 confidence HIGH vs LOW (filter, dropped) | almost all LOW |
   | 11 | transcript vs remark-only reading (which evidence carries the signal) | transcript orders payers better in 5 of 6, AUC 0.51-0.61 vs 0.44-0.55, all intervals include 0 |
   | 12 | having a reading inside A2 reachable (selection) | readers paid 7 pp less (cards, Apr-Jul) |
   | 13 | 180+: a recorded call in the last 90 days | cc 4.7% (read) / 7.2% (not read) vs 1.1%; rl 8.8% / 12.3% vs 1.3% (n 107-329) |

   "Inside" = within the A3 level / A4 state named; compare with the no-reading group of the same state too. AUC for
   ordered ideas, pp difference for flags and hints. Bar for a later decision (for the verdict only): ≥ 5 pp or
   ≥ +0.02 AUC inside the target state.

Known defects to fix first
- CC DPD band came out `unknown` for most UC1 rows in the last run (A4 `current_bucket` did not map to buckets 4-7);
  check the values and fix the mapping before any DPD split.
- CC outstanding was the latest July snapshot, not the month end (see item 3).

Rules
`catalog.load` only; UC1 tables via `catalog_crx.yml` and `conf/base/catalog/catalog_tmp_uc1_full.yml` (read
`proposer_level_observations` one `snapshot_date=` folder at a time; use 2026-08-31). Persisted persona outputs as
they are (obs base, A1–A4 axis outputs, payments as the A3 results run reads them); do not re-run any engine. model_id
= `catalog.load("params:model_id")`, in every output file name. Join persona rows to UC1 on `cif_id`. Aggregates
only: no account, CIF, agreement, conversation or agent ids, no transcript or remark text; cells under 10 as "<10".
Reuse loaders from `tmp_validation/uc1_refresh/` and `tmp_validation/uc1_full/`. A part that fails records its
error and the rest still runs. New tracked folder `tmp_validation/uc1_latest/`; commit only that folder. No
pipeline, catalog (beyond the temp file) or registry change.

Deliverables
1. Snippet + README (one command per model_id), pushed from UAT.
2. After the user commits the PROD results: `summary_uc1_latest.md` (under 200 lines): coverage, the findings
   table, the money table, the old-vs-new table of every idea and the impact sizing laid out as tables ready for
   slides, a short "what got stronger" list, and what could not be computed and why.
