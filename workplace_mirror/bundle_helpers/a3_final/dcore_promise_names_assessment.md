# DCORE result names as promise events: assessment and consolidation rules (2026-11-09)

For GRR's Dimension A (V1f): which `dcore_prm_followup_outcomes` result names mark a commitment to pay,
and how to merge them with the PTP / settlement tables. Built from the names in
`crx_persona/_dcore_codes.py` (curated from the A2 inventory) and V1c's counts. **Counts exist only
for the PTP-type names**; every other count comes from V1f (Q1). Names are upper-cased and trimmed.

## 1. Known frequencies (V1c: latest 12 months, the model's agreements; rows / agreements / rows in delinquency)

| Result name | CC | RL |
|---|---|---|
| PROMISE TO PAY | 9,180 / 4,445 / 4,418 | 1,087 / 632 / 694 |
| PROMISE TO PAY SCHEDULED | 9,867 / 3,613 / 7,023 | 1,758 / 780 / 1,189 |
| DIGITAL COLLECT  PTP SUBSCRIBED | 750 / 583 / 422 | 187 / 116 / 172 |
| RETAIN PTP | 68 / 26 / 58 | 90 / 26 / 70 |
| SOFTPTP | 35 / 32 / 34 | <10 |
| PROMISE TO PAY PARTIALLY | <10 | <10 |
| HISTORICAL PROMISE TO PAY | 0 | 0 |
| EOSB_PTP_DOCUMENTS (in no set) | <10 / <10 / 0 | — |

For scale: V1c's concluded **table** PTP instalments in the episode window were 4,701 (CC) and 877
(RL). The follow-up has PTP-type rows on roughly 4,400–8,000 CC agreements. The windows differ (12
months without the anchor vs the episode), so these aren't comparable one to one, but follow-up
promises look much more frequent than table PTPs. That is the discrepancy to resolve.

## 2. Classification (proposal)

| Class | Use in Dimension A | Names |
|---|---|---|
| **P1 Explicit promise** | a promise event | PROMISE TO PAY · PROMISE TO PAY SCHEDULED · KSA/PROMISE TO PAY · PROMISE TO PAY PARTIALLY · DIGITAL COLLECT  PTP SUBSCRIBED (self-service) · HISTORICAL PROMISE TO PAY (0 rows) · EOSB_PTP_DOCUMENTS (immaterial) |
| **P2 Promise to pay at salary** | a promise event (the date is implied: the next salary, inside the grace) | WILL PAY AT SALARY · CODE25 WILL PAY AT SALARY · KSA/CUSTOMER WILL PAY AT SALARY |
| **P3 Soft promise** | an event, reported separately until its outcome rate is known | SOFTPTP |
| **A1 Arrangement agreed** | matched to a settlement / plan record; an event on its own only when no record exists | SETTLEMENT · KSA/EARLY/FINAL SETTLEMENT · BALCON WP 12 / 24 / 48 MONTHS · BALCON WOP 12 / 24 MONTHS · REWRITE AGREED |
| **A2 Dated payment instrument** | a promise event (a post-dated cheque is a dated promise) | POST DATED CHEQUE AVAILABLE · POST DATED COLLECTED |
| **R Re-affirmation** | not a new event; merged into the open promise | RETAIN PTP |
| **K DCORE's own outcome** | not an event; a cross-check of the payment outcome | CUSTOMER KEPT PROMISE MADE · ACCOUNT PAID · CUSTOMER MADE PAYMENT · CLAIMS MADE PAYMENT · PARTIALLY PAID · KSA/PAID AMOUNT · KSA/PARTIAL PAYMENT · RECEIVED EOSB |
| **I Request or intent** | not an event (no commitment yet) | CUSTOMER WANTS SETTLEMENT · NEED BALCON · NEED DEFERMENT · KSA/NEED DEFERMENT · NEED RESTRUCTURE · RESTRUCTURE REQUIRED · KSA/RESCHEDULING REQUEST · EPP REQUEST · EXPECTING EOSB · KSA/EOSB · REQUESTED FOR FD LIQUIDATION · REQUEST FOR DUE DATE CHANGE · REQUEST FOR PAYMENT MODE CHANGE · REQUEST TO PRESENT SECURITY CHEQUE · CUSTOMER WILL VISIT US · KSA/CUSTOMER WILL VISIT US |
| **D Payment postponed** | not an event (the bank deferred the due) | DEFERMENT FOR IMPACTED CUSTOMERS |
| **N Against a promise** | already used elsewhere (refusal, D-A3-20) | REFUSE TO PAY · REFUSED TO PAY · KSA/REFUSE TO PAY · REWRITE NOT AGREED · RESTRUCTURE NOT REQUIRED · NO NEED DEFERMENT |
| — Not about paying | ignored | the remaining right-party names (customer behaviour colours, job / medical / salary situation, NEW SECURITY CHEQUE COLLECTED, administrative requests), failed-call and deceased names |

Notes:
- **`_dcore_codes.PROMISE_TO_PAY` mixes three classes.** It holds P1–P3, A1 and five K names (ACCOUNT
  PAID, CUSTOMER MADE PAYMENT, CLAIMS MADE PAYMENT, PARTIALLY PAID, KSA/PAID AMOUNT, KSA/PARTIAL
  PAYMENT). That is fine for "the customer engaged" but wrong for a promise event, so V1f needs its own
  set. Side effect today: in the A3 contact disposition, PARTIALLY PAID, CLAIMS MADE PAYMENT, KSA/PAID
  AMOUNT and KSA/PARTIAL PAYMENT count as `ptp`, not `paid`. Minor; fix with this redesign.
- **K names validate outcomes.** DCORE logging CUSTOMER KEPT PROMISE MADE or a payment confirmation
  after an event can be checked against the payment outcome: a second, independent reading of "paid".
- **The salary promises (P2) and post-dated cheques (A2) are commitments with a date**, even without a
  PTP table record. Counts unknown.
- **The master table may hold names outside `_dcore_codes`.** V1f lists every name that occurs, so
  nothing is missed.

## 3. Consolidating the follow-up with the tables

1. **Table events.** Every non-cancelled PTP (reference date = promise start, else event date; it also
   has instalment due dates) and every settlement plan (reference = event date, plus its instalment
   schedule).
2. **Follow-up events.** P1, P2, P3 and A2 names, any action code (RETAIN PTP and payment confirmations
   are often logged administratively as IA), on the account's agreements.
3. **Collapse repeats.** On one agreement, follow-up promise rows within 7 days of each other are one
   event, dated at the first. Promise follow-ups and reminders, e.g. PROMISE TO PAY then PROMISE TO PAY
   SCHEDULED, often come in runs.
4. **Match follow-up to table.** A follow-up event and a table event on the same agreement within ±7
   days are one event: the table's dates and schedule, the follow-up's name as the source tag. Each is
   matched at most once, to the nearest. A1 names are matched to settlement records the same way.
5. **Three kinds of event come out:**
   - **matched:** a call logged the promise and DCORE recorded the plan;
   - **table-only:** a plan with no logged promise call (digital channel, branch, or the name logged
     outside the window);
   - **follow-up only:** a promise with no plan record. GRR's rule judges it on the payment alone, so
     it needs no amount.
6. **Re-affirmations (R)** fall into the open event's run and add nothing. **K names** are joined to
   each event's grace window as DCORE's own outcome, for comparison only.
7. **Judging (GRR):**
   - PTP and follow-up events from the reference date to the grace cutoff (the first statement on or
     after it / the next month end). Paid: payments ≥ the minimum payable due. Partial: ≥ 100 AED,
     below it. Broken: less.
   - Settlement plans per instalment due date, the same way.

What V1f must show for this to be trusted:
- the match-distance distribution (0, 1–3, 4–7, 8–30, > 30 days), so the ±7-day choice is not
  arbitrary;
- the matched / table-only / follow-up-only split by class and name;
- whether follow-up-only events are paid at a similar rate to matched ones. If they are, they are
  real promises the tables miss.
