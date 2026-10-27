# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/persona_redesign_b01`; mirror branch `feature/persona_redesign`). Photograph the result and drop it in `pics/`.
Done requests are removed; their results are logged in `TRANSCRIPTION_NOTES.md`.

The A1 test modules (`src/tests/pipelines/crx_persona/schema_registry.py`,
`test_crx_persona.py`) are left to the workplace Sonnet, via the A1 bundle prompt.

## How to send these

Photos (breadcrumb visible) or a transcription `.md` in `pics/`, as before. For shell output,
run the command from the workplace repo root and photograph the terminal. Ordered by what each
request unblocks.

## A1 — CC finish bundle (relayer + rename + delete v1, S12 salary rule, bureau bounces)

### R5 — bureau, what is still missing

The bureau pipeline is unvalidated (written by an earlier model — user, 2026-10-27), so
`prm_bureau_salary_history` is written as our own explicit node (named columns, `require_columns`,
no silent model projection) and does not copy `build_primary_dataframe`. Only needed: the
salary-history node of `pipelines/bureau/staging.py` (the `stg_aecb_salary_history` column names).
The rest arrived 2026-10-27 (`bundle_helpers/a1_final/workplace_reference.md`).

### R8 — still missing (the layout arrived 2026-10-27)

The `node(...)` block that builds `feat_demographics_cif` (its pipeline file), and the
`raw_beneficiary_cards` catalog entry (for `prm_beneficiary_cards`).

## A2 — the refactor bundle (login fixes, location layer, engine, reachability, deceased)

### R9 — DCORE, one file + one entry (blocks `prm_dcore_account_agreements`)

`nodes/staging/dcore/stg_dcore_observation_spine.py` (~24–92: where `agreement_id` comes from and
how it joins the spine), and the raw catalog entry of the DCORE table it reads for that.

### R10 — deceased, two output selects

The final `select` of `prm_cc.build_contract` (~473–521: the block-code column names) and of
`prm_demographics.py` (~85–95: key and `deceased_flag`).

### R11 — card spend, after v02

The final `select` of `prm_cc.build_transaction` and the `DOMESTIC=` parse (~375–381).

### R12 — CASA spend source, after v02 (only the entry of the route v02 picks)

The catalog entries of `wm_pri_labelled_transactions_indicators_by_week`
(`catalog_casa_plus_ftr.yml`) and `comp_financial_tran_repos_dly`.

### R4 — who reads the departure / CC feature tables (decision D1 in DESIGN_REVIEW.md)

Run from the workplace repo root and photograph the output:

```bash
grep -rnE "crx_cc_departure_signature|crx_cc_payment_trajectory|crx_cc_utilisation_features|crx_rl_departure_signature|crx_cc_departure_pass" src conf notebooks 2>/dev/null | grep -v "\.pyc" | grep -vE "/crx_persona/|catalog_crx\.yml"
```

Empty output means nothing outside the persona code reads them.

(R13 dropped: the v01 inventory already gives `rl_spine.loan_type` and
`chargeoff_age_months` on both spines.)
