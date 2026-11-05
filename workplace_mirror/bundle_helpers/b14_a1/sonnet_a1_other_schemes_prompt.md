# A1 ability — what the busy non-CASA schemes are (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session (branch `feature/persona_redesign_b14`,
bundle 14 applied, its check run).

---

## Goal

Bundle 14 counts a leg as CASA only when the account's scheme code is one of the 49 current +
savings codes (`casa_primary.current_account_codes` / `saving_account_codes`, WM's
`current_accounts` + `saving_accounts`). The B14 check (`tmp_validation/a1_b14_check/summary.md`)
shows 13-character accounts on other schemes with many legs: 012 (cc_60_180 65k legs), 095 (61k;
rl_60_180 13.7k on 65 CIFs), 014 (18k), 099 (16k). That is about 45 legs per customer, not
term-deposit behaviour. Find out what these schemes are, so the user can decide whether any belongs
in the CASA lists.

## Hard rules

- Code search is read-only, across this repo and `wealth_management`.
- PROD snippet in a temporary **tracked** folder `tmp_validation/a1_other_schemes/`; commit and push
  it. Data via `catalog.load(...)` only (`raw_casa_acid_to_cif`, `gen_schm_parm_table`,
  `prm_casa_transactions`, the obs base); `model_id = catalog.load("params:model_id")` in every
  output filename. No `spark.read`, no paths.
- Aggregates only: no customer rows, IDs or account numbers; scheme codes are fine. Cells under 10
  shown as `<10`. No pipeline, catalog or registry changes.

## Deliverables

1. **Code (once):** for 012, 095, 014, 099 and the other 13-character schemes in the check's top
   list, which WM list each is in (term deposits / others / investment / none of the 207), with
   file:line, and any comment WM has on them.
2. **Scheme table (PROD, once):** from `gen_schm_parm_table`, the columns that describe a scheme
   (`schm_type`, `product_type`, and a description if one exists without PII), for every scheme found
   on the base CIFs' 13-character accounts, together with the 49 CASA codes for comparison: code, in
   the 49 (y/n), `schm_type`, `product_type`.
3. **Behaviour (PROD, `cc_60_180` and `rl_60_180`):** for each 13-character other scheme with 1,000+
   legs in 12 months, and for current and savings as a reference: legs, CIFs, legs per CIF, debit
   share, and the share of legs in each `transaction_lane` lane
   (`feat_cif_casa.py::transaction_lane`). Then: how many of the CIFs that became `no_casa` in B14
   (old `dormant_casa` or not Unknown → new `no_casa`) have a leg on each of these schemes.

## Summary (back in UAT)

`tmp_validation/a1_other_schemes/summary.md`: one table per scheme with WM list, `schm_type`,
`product_type`, legs per CIF, lane mix and new-`no_casa` CIFs, then one line per scheme:
"looks like a current / savings account", "term deposit / investment", or "unclear". The user pastes
it back here.
