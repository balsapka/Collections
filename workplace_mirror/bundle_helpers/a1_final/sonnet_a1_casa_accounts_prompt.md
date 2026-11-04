# A1 ability — which accounts count as CASA (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session (branch `feature/persona_redesign`,
bundle 12 applied and cleaned up).

---

## Goal

A1 reports that every retail-loan customer at 61–180 has a CASA transaction, so "No CASA" never
fires on RL. The user doubts it: not every loan customer holds a CASA with us. Real CASA accounts
have an `account_id` / `foracid` starting with `101`; loan accounts are longer. Find out what A1
counts as a CASA transaction, and what changes if only real CASA accounts count.

## What the code does today (read it, do not change it)

- `nodes/primary/casa/prm_casa.py::build_transactions` → `prm_casa_transactions`: **every** leg
  of `comp_financial_tran_repos_dly` for all CIFs. `foracid` is kept but never filtered.
- `nodes/features/casa/feat_cif_casa.py::build_casa_activity` → `feat_cif_casa_activity_monthly`:
  legs per `(cif_id, month_end, lane)` (`transaction_lane`), any account of the CIF.
- `pipelines/crx_persona/a1_ability/signals.py::build_liquidity_signals` (or the function that
  builds them): `casa_active` = a leg in `CUSTOMER_LANES` (economic, card_spend, card_payment) in W;
  `casa_held` = any leg (any lane) or a positive WM CASA balance in the last 12 months. The S11
  Unknown gate and "No CASA" read these.
- `build_return_events` → `prm_casa_return_events` (cheque returns, DDS) has the same lack of an
  account filter.

Suspicion: loan-account legs (instalment recovery credits, disbursements, cash paid towards the
loan, PDC cheque returns) sit in the same table and make loan customers look like CASA holders.

## Hard rules

- Kedro notebook snippet in a temporary **tracked** folder `tmp_validation/a1_casa_accounts/`;
  commit and push it. All data via `catalog.load(...)`; `model_id = catalog.load("params:model_id")`,
  in every output filename; never hardcoded or overridden. No `spark.read`, no paths.
- Reuse the pipeline's own functions (`transaction_lane`, `build_casa_activity`, the A1 signal and
  classify functions) on filtered inputs; do not re-implement the rules.
- Latest observation month only for anything per account (`persona_end_date`'s month); the leg
  profile may use the last 12 months. Aggregates only: no customer rows, no IDs, no full account
  numbers (prefixes and lengths are fine). Cells under 10 shown as `<10`.
- No pipeline, catalog or registry changes.

## Hypotheses and results to save (`results_<model_id>.md`, one per model_id)

- **H1 — the table carries non-CASA accounts.** Legs of the model's base CIFs, last 12 months, by
  account class: `foracid` starts with `101` / other prefix (first 3 digits, top 10) / NULL, and
  `foracid` length. Look for any account-type or scheme column in `comp_financial_tran_repos_dly`
  (e.g. `schm_type`, `schm_code`, `acct_type`) and cross it with the prefix; say whether `101`
  matches it. Then account class × lane × `tran_dc` (legs, CIFs).
- **H2 — the CASA flags change.** For the latest month's accounts: `casa_held` and `casa_active` as
  today vs computed from `101` legs only (same rules, WM balance arm unchanged), 2×2 crosstab each.
  Also: CIFs with a positive WM CASA balance but no `101` leg in 12 months, and the reverse.
- **H3 — the states change.** Rescore A1 with `prm_casa_transactions` and
  `prm_casa_return_events` filtered to `101` accounts: state crosstab today × CASA-only (n), and
  which rule moved each row (Unknown gate, No CASA, distress). RL also by product
  (`rl_spine.loan_type`).
- **H4 — returns on loan accounts.** Cheque returns / DDS on non-`101` accounts: events and CIFs in
  12 months, by reason and account class (loan PDC bounces may be real distress; show them, do not
  decide).

Run for `rl_60_180`, `cc_60_180`, `rl_180_plus`, `cc_180_plus` (switch `model_id` in
`conf/dev/globals_dev.yml`, switch back after). The user runs it in PROD and commits the results.

## Summary (back in UAT, after the results are committed)

Write `tmp_validation/a1_casa_accounts/summary.md`, one section per model_id:
- H1: share of legs and of CIFs on non-`101` accounts, the lanes they fall in, and whether a scheme
  column confirms `101` = CASA.
- H2: `casa_held` / `casa_active` today vs CASA-only (n, %).
- H3: the state table today vs CASA-only and the 3 biggest moves, with the rule behind them.
- H4: returns on non-`101` accounts (n, by reason).
- One-line verdict per hypothesis.
The user pastes the summary back here.
