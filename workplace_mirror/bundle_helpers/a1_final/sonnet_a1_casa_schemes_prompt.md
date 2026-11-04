# A1 ability — CASA accounts by scheme code (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session (branch `feature/persona_redesign`).
It follows `tmp_validation/a1_casa_accounts/` (keep that folder until this one is done).

---

## Goal

A1's CASA signals (`casa_held`, `casa_active`, the "No CASA" reason) and the internal cheque / DDS
returns read every leg of `comp_financial_tran_repos_dly`, including the loan account itself.
The user decided (2026-11-04) that a **CASA account = an account whose scheme code is one of the 49
current + savings codes** (WM's `current_accounts` + `saving_accounts` lists; not the full
207-code `casa_scheme_codes`, which adds term deposits and "others"). The `101` prefix was only a
proxy and also drops 13-character accounts that look like CASA. Find the account → scheme source,
then measure the exact rule so the fix bundle can be built.

## Decided (do not change)

- Rule: CASA = `schm_code` in the 49 CA + SA codes. Everything else (loans, term deposits, others,
  unmatched) is not CASA.
- Where it applies (the bundle, not you): a new primary `prm_casa_accounts` (account, CIF, scheme
  code / type, open / close dates if the source has them), read by the CASA **feature** nodes
  (`feat_cif_casa_activity_monthly`, `feat_cif_returns_monthly`) as a filter on `foracid`. The
  primaries `prm_casa_transactions` / `prm_casa_return_events` stay all legs.
- The code lists are copied into our `parameters_casa.yml` (no imports from `wealth_management`).

## Hard rules

- Code search is read-only, across this repo and the `wealth_management` repo beside it.
- PROD snippet in a temporary **tracked** folder `tmp_validation/a1_casa_schemes/`; commit and
  push it. All data via `catalog.load(...)`; `model_id = catalog.load("params:model_id")`, in every
  output filename. No `spark.read`, no paths. If the scheme source is not in our catalog, say so and
  stop before the PROD part (the bundle then adds the catalog entry; give the exact entry WM uses).
- Aggregates only: no customer rows, no IDs, no full account numbers (prefixes, lengths and scheme
  codes are fine). Cells under 10 shown as `<10`.
- No pipeline, catalog or registry changes.

## Deliverables

1. **Source (code, once):** the dataset WM's balance node (`balance.py`, around the
   `casa_scheme_codes` filter) reads to get `schm_code` per account: its catalog entry (ours and
   WM's), columns, grain, keys (`foracid`? `acid`?), date / snapshot columns, open / close dates.
   Other candidates if better (e.g. `general_acct_mast_table`, `raw_general_acct_mast_table`). The
   49 codes verbatim, with CA / SA and their scheme descriptions if available.
2. **Coverage (PROD, `rl_60_180` and `cc_60_180`):** legs of the base CIFs in comp, last 12 months,
   by `foracid` length × scheme class (CA / SA / term deposit / other in the 207 / loan or other
   scheme outside the 207 / no scheme found): legs, CIFs. Top 10 non-CASA schemes by legs. Share of
   legs whose account finds a scheme. Does the 13-character non-`101` group fall in CA / SA?
3. **Effect (PROD, same two model_ids):** rescore A1 with the CASA feature inputs filtered to the
   49 codes (reuse the pipeline functions, as in `a1_casa_accounts`): `casa_held`, `casa_active`
   today × exact (2×2), the state crosstab today × exact, the No CASA count, distress changes; RL by
   product. Also the same against the `101` proxy (rows where exact and `101` disagree).

## Summary (back in UAT)

`tmp_validation/a1_casa_schemes/summary.md`: the source (dataset, key, catalog entry), the 49 codes,
then per model_id the coverage table, the 2×2s, the state crosstab and No CASA count, and one line
on exact vs `101`. The user pastes it back here.
