# A1 v02 — DDS retries: PROD summary (cc_60_180, 2026-10-26)

Part B of the v02 prompt (removed once absorbed), written by the workplace Sonnet from
`tmp_validation/a1_v02/results_cc_60_180.json`. Transcribed from a photo by a chat session
(`pics/claude_code_handoff_2.md`), so single digits may be misread.

## Summary (Sonnet, verbatim)

# A1 v02 — DDS return-leg validation (cc_60_180)

## G1 — DDS rows are one failed debit retried (real distress): CONFIRMED

- `most_common_amount_share` median = 0.98; 828/1,446 CIFs (57%) sit in the 80-100%
  band. A CIF's DDS debit legs are overwhelmingly the same amount, not varied.
- Median gap between consecutive debit legs = 1 day for 897/1,412 CIFs (64%) — a
  steady, short (daily) retry cadence, not sporadic/random timing.
- `balance_to_debit_ratio < 0.5` for 93,472/101,591 legs (92%) — the CASA balance
 is under half the debit amount at the moment of almost every DDS debit leg.

## G2 — DDS rows are bank-side corrections, unrelated to delinquency: REJECTED

- The same three numbers above are the opposite of G2's prediction: amounts
 repeat rather than vary, and the debit is short of balance in 92% of legs, not
 "never."
- `share_with_dds`: 54.1% of obs-base (60-180 DPD) CIFs with any return event
 carry a DDS row, vs 7.0% of all CIFs with any return event — a ~7.7x
 concentration in the delinquent population. A pattern that fired independent
 of delinquency would not show this gap.

## What this means for counting DDS as distress

The evidence matches G1: DDS rows look like one failed debit retried against an
insufficient CASA balance, and the pattern is heavily concentrated in the
delinquent population rather than spread evenly across all CASA customers.
Counting a DDS row (`reason_for_excluding = "DDS Rejects/Reversal"`) as
`distress_flag` in `build_distress_signals` is supported by this data.


## Review

- **Decision stands: DDS Rejects/Reversal counts as distress** (bundle 03 code, no change).
  G1 holds on all three tests: one repeated amount (median share 0.98), a daily retry cadence
  (64% of CIFs), and a CASA balance under half the debit on 92% of legs. DDS is 7.7× more
  common among the 60–180 CIFs than among all CIFs with a return.
- **Retries do not inflate the signal:** `distress_flag` is "at least one" in the window, so a
  debit retried every day still counts once. A count-based feature would need the retries
  collapsed to one failed debit first.
- **Size:** ~1,446 obs-base CIFs with a DDS debit in 3 months, about 7.5% of the latest
  month's 19,292 accounts (CIFs vs accounts, so roughly) — close to the 9.6% distress rate in
  the B03 check, so DDS is the main distress source.
- The balance test uses the weekly 4-week average balance, not the balance at the debit, so
  the 92% is indicative; the amount and cadence tests decide on their own.
