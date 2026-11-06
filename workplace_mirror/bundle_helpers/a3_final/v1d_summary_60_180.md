# A3 V1d summary (60_180), verbatim from handoff 44 (2026-11-06)

Source: workplace `tmp_validation/a3_v1_v4/summary_v1d.md`, transcribed from 3 photos by the chat assistant. OCR-risk digits: see the handoff notes (all percentages, the outcome table). Review: `v1_v4_review.md`, V1d.

# A3 V1d summary - where is the money behind DCORE 'paid'? (cc_60_180, rl_60_180)

Evidence: `results_v1d_cc_60_180.md`, `results_v1d_rl_60_180.md` (month 2026-08-31, full runs). H2
ran separately (`results_v1d_cc_60_180_H2.md`, from `prm_last_operation`). CC = card payments to due
+ 5 d; RL = loan master to month end.

## Group sizes (G1 paid/ledger not kept, G2 paid/kept, G3 overdue)
| model | plan | G1 | G2 | G3 |
|---|---|---|---|---|
| cc | PTP | 207 | 460 | 4,034 |
| cc | settlement | 3,813 | 2,027 | 6,311 |
| rl | PTP | <10 | 132 | 737 |
| rl | settlement | 71 | 80 | 182 |

## Hypotheses (cc PTP / cc settlement / rl settlement; rl PTP G1 is <10)
- **H1 card, other form - not supported.** Other credit-side rows cover 0 of 207 / 0 of 3,813 G1.
 Raw vs crx: identical same-day payments merged by `.distinct()` would cover 0.9% of settlement G1
 (35); quality-filter losses 0; PTP <10. Partly only for that 0.9%.
- **H2 Way4 last payment (`prm_last_operation`, as-of) - not supported.** Settlement G1: 11,372
 logged payments in the window, 99.9% match a ledger payment of the same amount on the same day (12
 unmatched; G2/G3 100%), so the table adds no money the ledger lacks and the two date clocks agree;
 ledger-short-but-logged-covers 0. PTP too sparse to read (only 24-29% of PTP instalments have an
 observation row in the window; G1 PTP: none of 49 logs a payment). `summary_balance` not read.
- **H3 balance - not supported.** Outstanding drops by >= the due amount in 11.7% / 6.5% of G1 (G2
 10.4% / 11.9%, G3 2.6% / 2.5%); drops with no payment row in the cycle: 0, so no waiver/write-off
 signature; where it drops, payments are below the drop in 50% / 65%.
- **H4 another account - not supported.** CASA card-payment legs (T1+T2): PTP <10; settlement 11.5%
 of G1 vs 13.5% G2 and 12.8% G3 - no uplift; T3 narration hits <10. Other cards of the CIF: 0.7% of
 settlement G1 (25) have payments >= the cum due. RL settlement G1: 0.
- **H5 late - supported (main explanation).** Cumulative payments reach the cum due later: PTP 61.8%
 (<=15 d <10, 16-30 d 25.6%, 31-60 d 18.8%, >60 d 14.5%), settlement 73.7% (6-15 d 10.1%, 16-30 d
 16.7%, 31-60 d 27.7%, >60 d 19.2%); never by obs 38.2% / 26.3%. RL settlement: 76.1% (1 month
 32.4%, 2-3 months 42.3%), never 23.9%.
- **H6 partial - supported.** At the cut-off: PTP 97.6% nothing paid; settlement 18.2% nothing,
 70.5% 50-99%, 11.3% <50%. RL settlement: 16.9% nothing, 71.8% 50-99%. By obs date some money
 exists for 73.9% (PTP) / 96.1% (settlement) of G1.
- **H7 DCORE's own reading - supported for PTP, and shows what 'paid' means.** PTP G1: paid amount =
 due amount in 100%, payment date, status date and update date all before the due date in 98-99%
 (G2: on/after due in 98%): the flag is set ahead of the money. Settlement G1: amount = due in 100%
 (G3 never), payment date > 5 d after due in 76.5% (RL 91.5%) - DCORE marks paid when it eventually
 arrives. Whole plan marked at once: 2.1% of plans with a G1; later cancelled 2.0%; payment
 source/mode do not separate G1 from G2.

## Delinquency outcome (share of instalments; cured = 0 everywhere in 2 cycles; base levels differ
by group)
| model/plan | grp | 1 cycle improved / held / rolled | 2 cycles improved / held / rolled |
|---|---|---|---|
| cc PTP | G1 | 12.1 / 86.0 / <10 | 7.2 / 45.4 / 40.6 |
| cc PTP | G2 | 11.5 / 84.3 / 4.1 | 8.7 / 40.2 / 45.2 |
| cc PTP | G3 | 2.8 / 29.1 / 68.1 | 1.9 / 15.2 / 78.9 |
| cc settl. | G1 | 14.3 / 67.1 / 18.2 | 16.8 / 49.6 / 17.7 |
| cc settl. | G2 | 31.7 / 64.6 / 3.5 | 27.2 / 49.8 / 9.4 |
| cc settl. | G3 | 5.6 / 34.7 / 59.7 | 4.8 / 18.8 / 53.0 |
| rl settl. | G1 | 16.9 / 49.3 / 33.8 | 19.7 / 39.4 / 22.5 |
| rl settl. | G2 | 30.0 / 63.8 / <10 | 17.5 / 46.2 / <10 |
| rl settl. | G3 | 6.0 / 34.6 / 59.3 | <10 / 18.7 / 47.8 |
G1 behaves like G2, not G3, for PTP; for settlement it sits between them (more roll than G2, far
less than G3).

## RL loan account
FTR credit legs on the loan account (all `MISCELLANEOUS`) do not reproduce `total_paid`: settlement
G1 - 0 paid by the due date, 0 later in the month, 76.1% some credit but not enough, 23.9% none. The
181 PTP 'overdue but ledger kept' (G3): 0 by due date, 8.8% later in the month, 75.7% not enough. So
the 24.6% cannot be split into late-but-paid vs DCORE error from FTR.
`int_loan_master.last_payment_date` is the only extra day-level field (other paid fields are
`total_paid` aliases): for settlement G1 it falls plan start..due 45.1%, after due in the due month
26.8%, null 25.4%.

## Verdict
H1-H6 together explain most of G1 as money that is late or partial, not hidden: some money exists by
the observation date for 73.9% of PTP G1 (full 61.8%) and 96.1% of settlement G1 (full 73.7%); other
forms (H1, H2, H4) add at most ~1% each. Unexplained: 54 PTP (26.1%) and 150 settlement (3.9%) G1
instalments with no payment at all (RL: <10 / 23.9% never fully covered). Payments are the better
judge of a *kept* instalment: DCORE PTP 'paid' is stamped before the due date with the exact due
amount, and DCORE settlement 'paid' means eventually paid, often > 5 d late. DCORE 'paid' still
carries signal (G1 outcome is far better than G3), so for A3 judge kept/broken by payments with a
longer grace window and a partial class, using DCORE status only as a secondary flag; the grace
length is a decision for GRR.

## Open items
1. H2 `summary_balance` not read; `last_operation` logs only the latest payment per row (lower
  bound). Unlikely to change the verdict.
2. 180+ models not run. RL PTP G1 is too small to read.

