# A3: V1j, the final test of the promise points (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
and pastes `summary_v1j.md` back here.

Why (user, 2026-11-13). V1i (`bundle_helpers/a3_final/v1i_summary.md`) found:
- Broken customers pay well above customers who never promised, also inside reachable and contacted
  accounts;
- Broken +1 ranks best in every book.

But Broken +1 scores a broken record the same as Partly kept, which is not intuitive. The user needs
a strong case, for GRR, before not penalising Broken and even giving it points.

This round tests the case from three sides:
1. **Is it promising, or just talking to us?** Contact alone might carry the same lift.
2. **Is Broken one group?** Broken may mix customers who paid something (partial, or late) with
   customers who paid nothing.
3. **Which point scheme ranks best while keeping Kept > Partly > Broken?** And does it hold on money
   collected, not only on paid-or-not?

4. **Does it hold in the segments where the axis is used?** The axis is payment credibility, and
   a broken promise goes against credibility. Credibility matters most for reachable customers
   (who get worked in-house). Among them most have talked to us, so "promised at all" may only
   proxy reachability, and reliability (kept vs broken) may be what ranks. A moderate share of
   in-house accounts is Non-Reachable or Unknown reach (cards 19%, loans 40%) or abroad (Skip, about
   20%). For them an earlier promise may be the only sign of engagement.

Bundle 23 is applied; the deadline is still open (GRR's month end vs 30 days), so run under both.

5. **How often does the follow-up merge hide a promise?** (D-A3-29, user 2026-11-13: ships in bundle
   25.) The engine merges follow-ups less than 8 days after the previous one into one event judged
   by the first row's deadline, so a new promise made after that deadline is never judged. Q0 sizes
   the change before it ships.

````text
Goal
The final evidence on how Dimension A should score promises, for all four model_ids: is making a
promise (even a broken one) evidence beyond contact, which Broken customers deserve credit, and which
point scheme ranks customers best with the order Kept > Partly > Broken kept. Exploration only:
aggregates, no pipeline change, no real output written.

Decided, to follow
- Engine, months, outcomes, deadlines (GRR and LEN), Thin split (T0 never promised; T1 promised,
  none concluded; T2 concluded, nothing kept, not Broken) and the rules: exactly as V1i. Reuse
  tmp_validation/a3_v1i/ code; do not re-implement any rule. Variants re-score the checkpointed levels
  with a Scorecard copy (thresholds High >= 4 / Moderate >= 2, refusal demotes).
- Add one outcome: AED collected per account in the 3 months (the A3 payments), with the share of
  all money collected that each state holds.
- Broken split, from the promise events behind each Broken row (concluded events in the 12-month
  window):
  BA = Broken, attempted: at least one broken event was partial (100 AED or more, below the due) or
       paid in full within 30 days after its deadline (late);
  BN = Broken, nothing: no broken event had any payment of 100 AED or more up to 30 days after its
       deadline.
  Apply the same attempted / nothing split to T2. Report the share of partial, late and nothing among
  broken events.
- Contact: a right-party contact in the 12-month window (the A3 contact signals / DCORE the engine
  reads). C0 = T0 with no contact; C1 = T0 with contact but no promise.

Questions (each a short answer with the key numbers, per model_id; GRR unless said; LEN in brackets
where it differs)
Q0 Follow-up runs that cross their deadline (sizing only; Q1-Q7 keep the current rule). Today
   _followup_promises chains follow-up rows less than 8 days after the previous row into one run,
   dated at its first row and judged by that row's promise_cutoff. Proposed rule: a row also starts
   a new event when its day is after the current event's promise_cutoff (each new event's cutoff from
   its own first day). Under GRR and LEN, over the 12-month windows of the scored rows:
   - runs today, runs crossing their cutoff (share), the extra events the proposed rule creates, and
     the run length in days today (median, p90, max);
   - the outcome mix (Kept / Partly / Broken) of the extra events, and their AED paid;
   - rows whose promise level (Kept / Partly / Broken / T1 / T2) changes, from -> to, and rows whose
     P0 state changes, with paid_due for the movers next to the rows that stayed;
   - state AUC on paid_due under P0 with the proposed rule vs today, with 95% intervals (one extra
     engine run per deadline; build the variant as a local copy of _followup_promises, the pipeline
     stays untouched);
   - promise events dated on their own cutoff day (an empty payment window: payments must come after
     the event day), count and share by product and segment.
Q1 Promise or contact? paid_due, paid_any and AED per account for C0, C1, T1, T2, Broken, Partly,
   Kept. Does C1 (talked, never promised) pay like C0 or like Broken? Then a matched comparison:
   Broken vs C1, exact cells of Dimension B level x Dimension C level x DPD bucket x A2 reachability
   x A4 family x product (RL loan type). Report the cell-weighted difference in paid_due with a 95%
   interval (bootstrap over accounts), the share of Broken rows matched, and the same for T2 vs C1.
Q2 Is Broken one group? Sizes of BA and BN (and of their split by partial / late). paid_due, paid_any,
   AED per account and rolled for BA, BN, T2-attempted, T2-nothing, next to Partly, C1 and C0. Does
   BN pay like C0/C1 (no credit deserved) and BA like Partly? Also by the number of broken events
   (1, 2, 3+) and the months since the last broken event (0-2, 3-5, 6-12).
Q3 Point schemes. Re-score the state under each, then report:
   - High / Moderate / Low shares;
   - rows changing state vs P0;
   - state AUC and points-total AUC, with 95% intervals, on paid_due, paid_any, not_rolled (61-180)
     and AED collected (AUC on collected > 0 is paid_any; also the share of money in High + Moderate);
   - the paired difference vs P0, with whether its interval excludes 0.
   Schemes (A points; B and C unchanged):
   P0 today: Kept 2 / Partly 1 / Thin 0 / Broken -1
   P2 V1i best: Kept 2 / Partly 1 / Thin 0 / Broken +1
   P5 engagement + reliability: every account with a concluded promise earns 1 for engaging, keeping
      adds to it: Kept 3 / Partly 2 / Broken 1 / T2 1 / T1 1 / T0 0
   P6 P5 with Broken split: Kept 3 / Partly 2 / BA 1 / BN 0 / T2-attempted 1 / T2-nothing 0 / T1 1 /
      T0 0
   P7 P5 with the High cut-off moved to 5 (P5 adds 1 to every promiser, so check High does not
      inflate): P5 points, High >= 5, Moderate >= 2
   P8 contact instead of promise: Kept 2 / Partly 1 / Broken 0 / any right-party contact without a
      promise +1 (shows whether contact alone earns the same)
   Run P0, P2, P5, P6, P7, P8 under GRR and LEN.
Q4 Robustness of the best scheme vs P0 and P2:
   - state AUC on paid_due per outcome month;
   - within each DPD bucket;
   - by RL loan type;
   - at 180+ by charge-off age (< 24 / >= 24 months).
   Plus the order of the states on paid_due in each of those (does High > Moderate > Low hold
   everywhere?).
Q5 Who moves under the best scheme vs P0: from -> to, sizes, their paid_due / AED next to the rows
   that stayed in each state, their A2 reachability mix, and how many of them are BN (paid nothing
   on any promise).
Q6b (see Q7 for the segments) Kept vs Partly at 180+: V1i found Kept < Partly (227-417 rows). Same comparison with 95%
   intervals, under GRR and LEN, pooled and per month: real, or noise?

Q7 Segments. The A2 locatability state on the same observation date (crx_<p>_a2_locatability),
   grouped:
   S1 In Country + Reachable;
   S2 Reachable, location Skip or Unknown;
   S3 Non-Reachable (any location);
   S4 Unknown reachability (any location);
   S5 Skip (abroad), any reachability, as an extra cut that overlaps S2-S4.
   For each segment:
   - its share of rows;
   - the promise-level mix (Kept / Partly / BA / BN / T2 / T1 / C1 / C0);
   - paid_due and AED per account for Kept, Partly, BA, BN, T2, C1, C0;
   - the state AUC on paid_due, with 95% intervals, for P0, P2, P5, P6 (and P7 if it differs from
     P5), and the paired difference vs P0.
   The key question: inside S1, where nearly everyone has talked to us, does a penalty for breaking
   (P0) rank as well as or better than engagement credit (P5 / P6)? If so, the engagement gain is
   reachability showing through, and credibility should score reliability. Answer it explicitly.
   Also say whether S3-S5 behave differently, i.e. whether an earlier promise is the useful signal
   there.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance: one engine run per deadline over all months at once; the
schemes re-score the checkpointed levels; localCheckpoint the event tables and the scored output
before counting; literal date filters right after catalog.load; broadcast the small tables; no
row-level collect; at 180+ check the driver memory before the bootstrap and sample accounts if needed
(say so). Work in a new tracked folder tmp_validation/a3_v1j/ and commit only that.

Deliverables
1. Snippet + README_v1j.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_v1j_<model_id>.md.
3. Back in UAT: summary_v1j.md, under 130 lines.
   - One line per question per model_id, with the key numbers.
   - A verdict, one paragraph per model segment (61-180, 180+), that answers in plain words:
     (a) is a promise evidence beyond contact;
     (b) do Broken customers who paid nothing deserve credit, or only those who attempted;
     (c) which scheme to ship and why, with the gain over P0 and P2 and whether it holds under both
         deadlines, in every month and inside every DPD bucket;
     (d) whether the answer differs by A2 segment (Q7): one scheme for all, or reliability scoring
         for the reachable and engagement credit only where the customer cannot be reached now;
     (e) the two-sentence explanation a business reader would accept, true to "payment
         credibility" (how far we can believe the customer will pay): if Broken earns points, say
         what it is evidence of, and why that is credibility rather than reachability.
     (f) Q0: how many promises the follow-up merge hides today, and whether splitting at the
         deadline moves the state or its AUC.
````
