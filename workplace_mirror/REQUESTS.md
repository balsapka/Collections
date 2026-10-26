# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/synthesized_features`). Photograph the result and drop it in `pics/`.
Done requests are removed; their results are logged in `TRANSCRIPTION_NOTES.md`.

The A1 test modules (`src/tests/pipelines/crx_persona/schema_registry.py`,
`test_crx_persona.py`) are left to the workplace Sonnet, via the A1 bundle prompt.

## R4 — who reads the departure / CC feature tables (decision D1 in DESIGN_REVIEW.md)

Run from the workplace repo root and photograph the output:

```bash
grep -rnE "crx_cc_departure_signature|crx_cc_payment_trajectory|crx_cc_utilisation_features|crx_rl_departure_signature|crx_cc_departure_pass" src conf notebooks 2>/dev/null | grep -v "\.pyc" | grep -vE "/crx_persona/|catalog_crx\.yml"
```

Empty output means nothing outside the persona code reads them.

## R5 — bureau primary pipeline (for `prm_bureau_salary_history`, user 2026-10-26)

Photograph in full, with the editor breadcrumb visible:

- `src/enbd_collections/nodes/primary/bureau/prm_bureau.py` (the whole file: `_join_cif_bridge`,
  `build_cif_bridge`, the payment-order / court-case builders and the models they project to)
- `src/enbd_collections/pipelines/bureau/primary.py`
- the `prm_bureau_*` entries of `conf/base/catalog/catalog_outputs.yml` (lines ~479–501) and
  the `stg_aecb_salary_history` entry (~140)
- the salary-history part of `src/enbd_collections/pipelines/bureau/staging.py` (lines ~40–60)
  and of the primary models file if a `BureauSalary…` model exists
  (`data_engineering/primary/models/bureau.py`)

## R6 — retail loan pipelines (for RL A1 on the engine, user 2026-10-26)

Photograph with the breadcrumb visible: the node building `int_loan_master` (its
`monthly_emi_due` / `total_paid` / `emi_*_flag` derivation and the tolerance parameters), its
pipeline file and catalog entry, and the `feat_loan_emi` node + catalog entry (reference only).
