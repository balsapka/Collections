# A3: V1i, Thin vs Broken promises in the points (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
and pastes `summary_v1i.md` back here.

Why (user, 2026-11-13). The V1h back-test (`bundle_helpers/a3_final/v1h_review.md` §3) found that
at 61–180, accounts whose promises are Broken pay a due more often than Thin ones:
- cards 28.5 vs 11.6%, loans 40.5 vs 27.7%;
- ranked on Dimension A alone, Broken above Thin scores AUC 0.62–0.67, against 0.53–0.60 for the
  current order.

The points do the opposite: Kept 2 / Partly 1 / Thin 0 / Broken −1 (D-A3-23). Before changing them
we need to know two things:
- whether the gap is credibility, or engagement that reachability already counts (a Broken
  account has talked to us; most Thin accounts never promised);
- whether it holds at 180+ and within the same payment level and bucket.

Bundle 23 is applied in the workplace and step 8 has not run, so the engine code is bundle 23's.
The deadline is still open (GRR's month end vs 30 days), so V1i runs under both.

````text
Goal
Decide, with evidence for all four model_ids, whether Dimension A's points should change: where
Thin and Broken belong relative to each other, and whether Thin should be split. Exploration
only: aggregates, no pipeline change, no real output written.

Decided, to follow
- Engine: the applied code in src/enbd_collections/pipelines/crx_persona/a3_credibility/ and the
  product wrappers. Run the node functions in pipeline order on catalog loads, as in V1h
  (tmp_validation/a3_v1h/, reuse its code if the folder still exists). Do not re-implement any
  rule. For the point variants, build a Scorecard copy with a changed
  Dimension("commitments", ...) points dict (scoring_engine.Scorecard / Dimension, as
  constants.SCORECARD does). Thresholds stay High >= 4 / Moderate >= 2; refusal demotes; never
  Unknown for an episode row.
- Deadlines: GRR = as shipped (no override); LEN = CC "30_days", RL "30_days_month_end" (the
  deadline override on build_promise_events / build_a3_credibility). One engine run each; the
  point variants re-score the same run.
- Observation dates and outcomes: exactly as V1h. Month ends 2026-03-31, 04-30, 05-31, pooled;
  3 months of outcome. Outcomes: paid_due, paid_any, cured, rolled (61-180 only), exited (its own
  category). At 180+ lead with paid_due and paid_any; cure at cc_60_180 has no signal (0.2%), so
  read paid and not_rolled there.
- Thin split, from the commitment signals (commitments_concluded, commitments_kept,
  commitments_partial) and the promise events in the 12-month window:
  T0 = no promise event in the window;
  T1 = promise events, none concluded yet;
  T2 = concluded, nothing kept, not Broken: one concluded promise broken, or partial only.
  Note: a single broken promise is Thin today, two are Broken. Check that T0 + T1 + T2 = Thin.

Questions (each a short answer with the key numbers, per model_id; deadline GRR unless said)
Q1 Sizes. Share of rows in Kept / Partly / Broken / T0 / T1 / T2, under GRR and LEN.
Q2 Outcomes by level. paid_due, paid_any, rolled and cured for each of the six, with n and a 95%
   interval (bootstrap over accounts, 200 resamples). Is the order Kept > Partly > Broken > Thin
   at 180+ too? Where does each of T0 / T1 / T2 sit?
Q3 Is it engagement? Repeat Q2's paid_due for Broken vs T0 vs T2 within these strata:
   (a) A2 reachability on the same observation date (crx_<p>_a2_locatability: Reachable /
   Non-Reachable / Unknown);
   (b) a right-party contact in the 3 months before the observation date (A3 contact signals or
   DCORE, whichever the engine already reads);
   (c) the Dimension B level (regular / some / none);
   (d) the DPD bucket at the observation date.
   Say whether Broken > Thin survives inside each stratum, and by how much. A gap that vanishes
   within (a) or (b) is engagement, not credibility.
Q4 Point variants. Re-score the state under each variant, then report:
   - High / Moderate / Low shares;
   - rows changing state vs P0;
   - the AUC with a 95% interval for the state (High > Moderate > Low) and for a3_points_total,
     on paid_due, paid_any and not_rolled (61-180);
   - the paired difference vs P0, and whether its interval excludes 0.
   Variants (Kept 2 and Partly 1 throughout):
   P0 = Broken -1, Thin 0 (today);
   P1 = Broken 0;
   P2 = Broken +1;
   P3 = Broken 0, Thin -1;
   P4 = one data-led split of Thin chosen from Q2 / Q3 (for example T0 -1, T1 0, T2 0,
        Broken 0); state the points and why, or say none is warranted.
   Run P0-P4 under GRR and LEN (ten scorings per model_id).
Q5 Who moves. For P1 and P2 vs P0: the rows that change state (from -> to), their outcome rates
   next to the rows that stayed in each state, and their Q3 reachability mix.
Q6 Stability. Q4's state AUC on paid_due per observation month, for P0 and the best variant.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance: one engine run per deadline over all months at once; build
the point variants from the checkpointed levels, not by re-running the engine; localCheckpoint the
event tables and the scored output before counting; literal date filters right after
catalog.load; broadcast the small tables; no row-level collect; at 180+ (300k+ rows a month) check
the driver memory before the bootstrap and sample accounts if needed (say so). Work in a new
tracked folder tmp_validation/a3_v1i/ and commit only that.

Deliverables
1. Snippet + README_v1i.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_v1i_<model_id>.md.
3. Back in UAT: summary_v1i.md, under 90 lines.
   - One line per question per model_id, with the key numbers.
   - A verdict per segment (61-180, 180+), one paragraph each:
     (a) is Broken > Thin credibility or engagement (Q3);
     (b) which point variant ranks best, whether the gain is clear, and whether it holds under
         both deadlines and in every month;
     (c) whether Thin should be split, and how;
     (d) what the change does to the state mix.
````
