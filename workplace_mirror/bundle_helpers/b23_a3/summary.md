**What this bundle does.** Judges A3 promises by GRR's thresholds (Teams answer, handoff 64): loans, and every promise at 180+, must be paid by the end of the promise month; cards at 61–180 keep the next statement. Apply on top of bundle 22 (bundle 21 is independent).

**What changes in the logic** (spec `specs/A3_credibility_spec.md`, D-A3-28):
- **Deadline, whatever date was promised:**
  - 61–180 cards: the next statement after the promise day, however close (unchanged);
  - 61–180 loans: the end of the promise month (was the end of the next month);
  - 180+ cards and loans: the end of the promise month (cards were on the next statement).
- Loan cash is dated at the month end, so the promise month's cash still counts in full. Paying on the deadline day counts.
- Nothing else changes: events, amounts, the 12-month window, the ladder and the thresholds.

**Code:** `PROMISE_DEADLINE` is keyed by segment and product, read from `params:model_id` (`promise_deadline(product, model_id)`); `build_promise_events` and `build_a3_credibility` take `model_id` and `product`. `a3_promise_deadline` in the output shows the deadline used. The 30-day and next-month-end options stay available.

**Check** (temporary, `a3_credibility/check.py`, pipelines `crx_<p>_a3_check`): the latest month through the engine twice: `new` (as shipped, `crx_<p>_a3_check_new`) and `old` (bundle 20's deadline, `crx_<p>_a3_check_old`). Blocks: `A3 OUTPUT` (states, old × new with the share changed), `A3 PROMISES` (concluded events and outcomes per deadline, outcome old × new, changed events by kind and by promise day of month, accounts with a concluded / kept promise), `A3 LEVELS` (Dimension A levels old × new). At 61–180 the CC block must show 0 changed.
