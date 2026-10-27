# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/persona_redesign_b01`; mirror branch `feature/persona_redesign`). Photograph the result and drop it in `pics/`.
Done requests are removed; their results are logged in `TRANSCRIPTION_NOTES.md`.
R4, R5 and R7–R11 arrived (handoffs 6 and 9, `bundle_helpers/a1_final/workplace_reference.md`).

The A1 test modules (`src/tests/pipelines/crx_persona/schema_registry.py`,
`test_crx_persona.py`) are left to the workplace Sonnet, via the A1 bundle prompt.

## How to send these

Ask the UAT Sonnet to copy the items verbatim into `tmp_validation/mirror_requests/snippets.md`
(as before), then photograph or transcribe that file. Ordered by what each request unblocks.

## A2 — the refactor bundle

### R9b — the RL DCORE spine (for `prm_dcore_account_agreements` on RL)

The DCORE spine in R9 is CC only (it joins `spine_contracts_way4` and `cc_spine`), but A2 v01
Part 0 found an RL DCORE spine on month ends. Wanted: the node that builds it (its `build`
function and its `node(...)` block), i.e. how an RL `account_id` maps to a DCORE
`agreement_id`.

### R12 — CASA spend source, after v02 (only the entry of the route v02 picks)

The catalog entries of `wm_pri_labelled_transactions_indicators_by_week`
(`catalog_casa_plus_ftr.yml`) and `comp_financial_tran_repos_dly`.
