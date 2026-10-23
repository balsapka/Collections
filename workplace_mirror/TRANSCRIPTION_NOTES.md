# Workplace mirror — transcription notes

Mirror of `retail.collections.risk_profiling` (branch `feature/synthesized_features`), transcribed
from screen photos. Paths under `workplace_mirror/` match the workplace repo root.

## Workplace repo root (from the explorer photo)

```
.claude/ .devcontainer/ .github/ .pytest_cache/ .ruff_cache/ conf/ data/ docs/
model_registry/ notebooks/ scripts/ src/ tasks/
.coverage .dockerignore .gitignore .pre-commit-config.yaml build_project.sh coverage.xml
Dockerfile jupyter_server_config.py Makefile package.json pyproject.toml README.md
release_body.md setup.py sonar-project.properties uc.properties
```

## Batch 1 — 5 modules (photos IMG_7854–7909)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `crx_persona/cc_spell/pipeline.py` | 30 | 30 | complete |
| `crx_persona/cc_spell/nodes.py` | 237 | 237 | complete |
| `crx_persona/cc_full_history/pipeline.py` | 30 | 30 | complete |
| `crx_persona/cc_full_history/nodes.py` | 60 | 60 | complete |
| `crx_persona/cc_raw_extract/pipeline.py` | 48 | 48 | complete (end confirmed in batch 2) |
| `crx_persona/cc_raw_extract/nodes.py` | 267 | 267 | complete |
| `crx_persona/cc_payment_trajectory/pipeline.py` | 38 | 38 | complete |
| `crx_persona/cc_payment_trajectory/nodes.py` | 781 | 781 | complete |
| `crx_persona/cc_utilisation/pipeline.py` | 41 | 41 | complete |
| `crx_persona/cc_utilisation/nodes.py` | 569 | 569 | complete |
| `pipeline_registry.py` | 254 | 254 | completed in batch 2 |

All files compile, `ruff --select F,E9` is clean, and the four nodes modules that don't need
`enbd_collections.nodes.utils.config` import under pyspark 3.5.3. Every `def` sits on the same
line number as on screen.

Not seen, so not created: `__init__.py` files, `conf/` catalog entries, `enbd_collections/nodes/utils/config.py`
(`TXN_CATEGORIES`), `utils/ols.py`.

## Uncertain characters — check against the screen

1. **Glyph shown as a box** in `M0□12m`, `M0□3m`, `M0□1`, `[min(T0) □ 12m, …]`. The editor font
   lacks it; I used `−` (U+2212). Affects docstrings only:
   `cc_raw_extract/nodes.py` 40, 132; `cc_payment_trajectory/nodes.py` 40–42, 55, 212, 225, 344, 539.
2. **Section separators** like `# ── Step 0: … ──────`: I used `─` (U+2500); the exact character and
   the number of dashes per line are approximate. Comments only.
3. **Docstring column alignment** (Args/feature tables) is approximate. Docstrings only.
4. ~~`cc_utilisation/nodes.py` 37 and 350 RLIKE pattern~~ — confirmed `'CASH ADVANCE|CASH DISBURSEMENT'` in batch 2.
5. `cc_utilisation/nodes.py` 469: comment end cut off; assumed `… increasing toward T0)`.
6. `cc_payment_trajectory/nodes.py` 387: `trunc(t0,'month')` — the closing quote looked curly.

No uncertainty in executable code.

## Batch 2 — departure signature + full registry (photos IMG_7910–7983)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `crx_persona/cc_departure_signature/pipeline.py` | 267 | 267 | complete |
| `crx_persona/cc_departure_signature/nodes.py` | 2375 | 2375 | complete — all 28 `def`s on the same line as on screen |
| `pipeline_registry.py` | 254 | 254 | complete |

Box glyphs in this batch (docstrings/comments only), rendered as: `318–327`, `3000–3299`,
`2022–2023`, `1–2 days` (en dash) and `cif_id × month_number`, `3× the monthly median` (times sign).
The registry's `# -- Section ------` comment dash counts are approximate.

## Batch 3 — A4 deterioration, `_dpd_journey` engine, A2 locatability (photos IMG_7984–8075)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `crx_persona/cc_a4_deterioration/pipeline.py` | 47 | 47 | complete |
| `crx_persona/cc_a4_deterioration/nodes.py` | 81 | 81 | complete |
| `crx_persona/_dpd_journey/__init__.py` | 85 | 85 | complete |
| `crx_persona/_dpd_journey/_dates.py` | 31 | 31 | complete |
| `crx_persona/_dpd_journey/constants.py` | 40 | 40 | complete |
| `crx_persona/_dpd_journey/core.py` | 172 | 172 | complete |
| `crx_persona/_dpd_journey/history.py` | 165 | 165 | complete |
| `crx_persona/_dpd_journey/logging.py` | 100 | 100 | complete |
| `crx_persona/_dpd_journey/params.py` | 92 | 92 | complete |
| `crx_persona/_dpd_journey/spark.py` | 399 | 399 | complete |
| `crx_persona/_dpd_journey/states.py` | 144 | 144 | complete |
| `crx_persona/cc_a2_locatability/__init__.py` | 5 | 5 | complete |
| `crx_persona/cc_a2_locatability/pipeline.py` | 104 | 104 | complete |
| `crx_persona/cc_a2_locatability/constants.py` | 299 | 299 | complete |
| `crx_persona/cc_a2_locatability/nodes.py` | 1320 | 1320 | complete — all 6 `def`s on the same line as on screen |

Checks: all files compile; `ruff --select F,E9` is clean apart from the intentional re-exports in
`_dpd_journey/__init__.py` (the original carries `# pylint: disable=unused-import`); the engine
imports and classifies a sample sequence with a stub for `stg_rr_portf`.

Not seen, so not created: `crx_persona/_spine_utils.py` (`join_spine_to_spell`, `_build_cif_bridge`),
`enbd_collections/nodes/staging/retail_loans/stg_rr_portf.py` (`ECL_CUTOFF_DATE`,
`ECL_WINNOWED_PRODUCT_CODES`), `_dpd_journey/history.py` is complete but its RL callers are not.

Uncertain characters (comments/strings only):
- `_dpd_journey/history.py:47, 92`: the glyph between `0` and `1` in "CC 0 · 1" (and `3 · 5`) is a
  box on screen; I used `·`. Same in `params.py:33`.
- `cc_a2_locatability/constants.py:65, 235`: `"DIGITAL COLLECT  PTP SUBSCRIBED"` has **two** spaces
  on screen — kept as seen (it must match the DCORE value exactly).
- `cc_a2_locatability/constants.py:271`: `"MOBILE SWICTHED OFF"` (typo) sits next to
  `"MOBILE SWITCHED OFF"` on screen — kept both; the typo is probably the real DCORE value.

## Review findings

Moved to [REVIEW_OBSERVATIONS.md](REVIEW_OBSERVATIONS.md).
