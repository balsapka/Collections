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

### R13 — how WM decodes `week_number` (O64)

`week_number` is `yyyyMM0W` (week 01–04 of the month). Wanted: the function in `wealth_management`
that turns it into a date (the one `ft_days_since_salary_transaction` is counted to), with file:line,
and the snippet A1 v03b used for "WM's decode" (`tmp_validation/a1_v03/`).

### R14 — the v03b CASA transaction classification (S11 gate)

The code in `tmp_validation/a1_v03/` that sorted `comp_financial_tran_repos_dly` rows into
administrative / unclassified / customer-initiated / self-transfer / EMI repayment (the regexes and
columns, part D of v03b), verbatim.
