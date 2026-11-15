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

## A1 — the CC finish bundle

R13 and R14 are no longer needed (2026-10-29): bundle 08 rounds the WM salary date to the nearest
first of a month (O64), and the activity gate classifies FTR legs by the FTR row-handling
reference (`bundle_helpers/ftr_transaction_handling.md`) instead of the v03b regexes.

## DE — bureau salary load date

R15. Keep a per-row load date on `feat_bureau_salary_unified`. The module builds `_load_date` per
source and drops it in the final select: alert = `alert_extract_date`, bulk pull = `EDP_LOAD_DATE`;
`salary_credit` has none and should carry the application date. With the date, A1 can cap each
bureau salary row at the date it became known, so an observation reads only rows already loaded by
then (Q-S6-13). Not part of bundle 25.
