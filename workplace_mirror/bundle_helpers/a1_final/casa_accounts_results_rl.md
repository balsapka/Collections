# A1 CASA accounts — RL results (handoff 34, 2026-11-04)

Source: `tmp_validation/a1_casa_accounts/summary.md` in the workplace (prompt
`sonnet_a1_casa_accounts_prompt.md`), transcribed from 4 photos. `rl_60_180` only (user: enough to
decide), latest month 2026-08, 3,985 rows, 3,608 CIFs, legs and returns 2025-09..2026-08. Rebuild
checks pass (today = persisted liquidity, distress, state). CASA proxy = `foracid` starting `101`.

## Findings

- **H0, WM:** `product_category = 'CASA'` on `wm_pri_labelled_transactions` is a literal on every FTR
  row, no account filter; only the population is narrowed (PRB / PSB / PB). WM's only real CASA test
  is the balance table's scheme list `casa_scheme_codes`: 207 codes = CA 36 + SA 13 + term deposits
  47 + others 111. The labelled table has `tran_type` and `in_out_flow` but not `reason_for_excluding`,
  `tran_particular_code`, `tran_narration_1`: it cannot feed `transaction_lane`. **Route B is out.**
- **H1, accounts in comp:** 959,135 legs; `101` 79.2%, other 20.8% (199,222). Non-`101` by length:
  - 16 characters: 41,513 legs on 3,607 CIFs, one per customer (prefixes 515 / 600 / 605 / 700 /
    735): **the loan itself**;
  - 13 characters: 156,560 legs on 830 CIFs (021, 095, 110, 012, 106, 014, 105): **look like other
    CASA schemes**;
  - 15 characters: 1,149 legs, 18 CIFs.
  No scheme or account-type column in comp; `module_id` does not separate them.
- **H2, flags:** `casa_held` = 1 on all 3,985 rows today (so No CASA never fires); `101` only: 887
  (22.3%) drop to 0, Auto 736 of 1,364 (54%), Personal 69, Personal Cash 82. `casa_active`: 1,332
  today, 288 (21.6%) drop. 243 of 2,909 CIFs with a positive WM balance have no `101` leg, all with
  non-`101` legs.
- **H3, states (`101` only):** 4.4% of rows move, Low → Unknown 173 (153 Unknown gate, 20 with
  distress too); No CASA 0 → 532 rows (13.3%), Auto 421 (30.9%). Distress: 31 of 725 lose the flag.
- **H4, returns:** non-`101` cheque returns 49 (22 CIFs) and DDS 3,041 (29) in 12 months, all on
  13-character accounts. Loan PDC bounces do not appear. Not material.

## Claude's review

- Sums reconcile (handoff notes). The loan-leg problem is confirmed: every RL customer has a
  16-character loan account in comp, which alone set `casa_held`.
- `101` over-corrects. The 13-character non-`101` accounts (830 CIFs) behave like CASA: the 243 CIFs
  with a positive WM balance (scheme-tested) and no `101` leg all have non-`101` legs, and all
  non-`101` returns (cheque, DDS) sit on them. Some of the 173 Low → Unknown moves and the 532 No
  CASA rows are therefore real CASA holders.
- Not measured: the effect of dropping only the 16-character accounts, which is the true size of
  "loan legs fake activity".
- Side point: A1's `casa_held` also reads the WM balance (> 0), and WM's balance uses all 207 codes,
  so a term deposit or an "other" scheme can count as holding a CASA. Small for the gate (balance
  is the second arm only), but the exact rule should use the 49 CA + SA codes there too.

## Decision needed (user)

Which accounts are CASA in `prm_casa_transactions` / `prm_casa_return_events`:
1. not a loan: drop the 16-character (and 15-character) accounts, keep every 13-character account;
2. `101` only (the user's rule; drops the 830 CIFs' 13-character accounts);
3. the exact scheme rule (49 CA + SA codes), which needs a `foracid` → `schm_code` bridge not in the
   catalog today.
