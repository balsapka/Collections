**What this bundle does.** Changes A3 payment credibility's Dimension A to GRR's promise events judged by a sufficient payment, moves the Moderate cut-off to 2 points, and removes the DCORE judge option. Apply on top of bundles 17–19 and bundle 17's cleanup.

**What changes in the logic** (spec `specs/A3_credibility_spec.md`, D-A3-24, D-A3-25):
- **Promises (Dimension A) are promise events, judged by payment.**
  - **Events:** every non-cancelled PTP and settlement plan (dated at its start), plus every follow-up promise (`_dcore_codes.PROMISE_EVENT`: promise to pay, scheduled, digital collect, pay at salary) that no plan claims. Follow-up promises less than 8 days apart are one event; a plan takes its nearest follow-up promise within 7 days.
  - **Judged once:** paid when the payments after the event day reach the due of the cycle open on that day (at least 100 AED) by the deadline. Partial: 100 AED or more but below it (counts as not kept). Otherwise none.
  - **Deadline (GRR):** CC the next statement after the promise, however close; RL the end of the next month. One constant (`PROMISE_DEADLINE`); the 30-day alternative is built in and runs in the check.
  - The ladder is unchanged (Kept / Partly kept / Thin / Broken on the last 12 months of the episode); points Kept 2, Partly 1, Thin 0, Broken −1.
- **Moderate from 2 points** (was 1), High from 4; a refusal still takes one rung off.
- **Contact disposition:** payment reports (partially paid, claims made payment, KSA paid / partial payment, customer kept promise made) now read `paid`, not `ptp` (diagnostic only; the refusal rule is unchanged).

**Code:** `a3_credibility/sources.py` gains `build_promise_events` (new dataset `crx_<p>_a3_promise_events`); `build_commitment_signals` reads the events; the DCORE judge, `KEPT_BY`, `GRACE` and `params:a3_kept_by` go. Output: `a3_kept_by` becomes `a3_promise_deadline`, `commitments_partial` is added. `_dcore_codes` gains `PROMISE_EVENT` and `PAYMENT_REPORTED`.

**Check** (temporary, `a3_credibility/check.py`, pipelines `crx_<p>_a3_check`): the latest month through the new engine with GRR's deadline (`crx_<p>_a3_check_grr`) and with 30 days (`crx_<p>_a3_check_30d`), against bundle 17's real output. Blocks: `A3 OUTPUT` (state old / old at Moderate from 2 / GRR / 30 days, crosstabs), `A3 PROMISES` (events by kind and source, outcomes, follow-up names, accounts with a concluded promise), `A3 LEVELS` (Dimension A levels and crosstabs), `A3 CONTACTS` (refusal and disposition old × new).
