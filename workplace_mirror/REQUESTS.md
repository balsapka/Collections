# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/synthesized_features`). Photograph the result and drop it in `pics/`.
Done requests are removed; their results are logged in `TRANSCRIPTION_NOTES.md`.

## R3 — files the A1 rework will touch that are not mirrored yet

Whole files, line numbers visible:

1. `src/tests/pipelines/crx_persona/schema_registry.py` — at least the `CRX_CC_A1_ABILITY`
   block around lines 170–230 (whole file if it is short).
2. `src/tests/pipelines/crx_persona/test_crx_persona.py` — the imports at the top and the A1
   test around line 190 (whole file if it is short).
3. `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/pipeline.py` — whole file
   (the package's `__init__.py` imports it; the mirror cannot import the package without it).
