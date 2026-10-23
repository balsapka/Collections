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
