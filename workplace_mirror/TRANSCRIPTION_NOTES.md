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

## Batch 4 — A1 ability v2, `_spine_utils`, `stg_rr_portf`, `utils/config` (photos IMG_8076–8130)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `crx_persona/cc_a1_ability_v2/__init__.py` | 5 | 5 | complete |
| `crx_persona/cc_a1_ability_v2/nodes.py` | 945 | 945 | complete |
| `crx_persona/cc_a1_ability_v2/pipeline.py` | 98 | 98 | complete |
| `crx_persona/_spine_utils.py` | 120 | 120 | complete |
| `nodes/staging/retail_loans/stg_rr_portf.py` | 266 | 266 | complete |
| `nodes/utils/config.py` | 619 | 619 | complete |

IMG_8084 was not in the batch; IMG_8083 → IMG_8085 overlap (lines 254–300), so nothing is missing.
Checks: everything compiles, ruff F/E9 clean, and `cc_raw_extract`, `cc_a2_locatability` and
`_dpd_journey` now import for real (no stubs needed any more).

Still not seen (imported by `cc_a1_ability_v2`): `crx_persona/cc_a1_ability/enrichers.py`
(`enrich_salary_months_h2`, `enrich_salary_pit`, `enrich_bureau_salary`,
`enrich_ext_cc_payments_h2`, `enrich_casa_inflow_h2`, `_CASA_BAL_COL`) and
`crx_persona/scoring_engine.py` (`StateLadder`, `points_from_level`).

Uncertain characters: `stg_rr_portf.py:4` "acct_num × ss_dt" (box glyph, read as ×);
`cc_a1_ability_v2/pipeline.py:10–12` the bracket glyphs drawn beside "parallel" (┐ ┤ ┘).

## Batch 5 — the RL chain (photos IMG_8131–8233)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `crx_persona/rl_full_history/__init__.py` | 5 | 5 | complete |
| `crx_persona/rl_full_history/pipeline.py` | 33 | 33 | complete |
| `crx_persona/rl_full_history/nodes.py` | 96 | 96 | complete |
| `crx_persona/rl_spell_table/__init__.py` | 5 | 5 | complete |
| `crx_persona/rl_spell_table/pipeline.py` | 32 | 32 | complete |
| `crx_persona/rl_spell_table/nodes.py` | 366 | 366 | complete |
| `crx_persona/rl_departure_signature/__init__.py` | 10 | 10 | complete |
| `crx_persona/rl_departure_signature/nodes.py` | 998 | 998 | complete |
| `crx_persona/rl_a4_spine/__init__.py` | 9 | 9 | complete (no `nodes.py` — reuses `build_rl_depart_spine`) |
| `crx_persona/rl_a4_spine/pipeline.py` | 39 | 39 | complete |
| `crx_persona/rl_a4_deterioration/__init__.py` | 5 | 5 | complete |
| `crx_persona/rl_a4_deterioration/nodes.py` | 50 | 50 | complete |
| `crx_persona/rl_a4_deterioration/pipeline.py` | 47 | 47 | complete |
| `crx_persona/rl_a2_locatability/__init__.py` | 5 | 5 | complete |
| `crx_persona/rl_a2_locatability/nodes.py` | 214 | 214 | complete |
| `crx_persona/rl_a2_locatability/pipeline.py` | 113 | 113 | complete |
| `crx_persona/rl_a1_ability/__init__.py` | 5 | 5 | complete |
| `crx_persona/rl_a1_ability/nodes.py` | 1360 | 1360 | complete — all 11 `def`s on the same line as on screen |
| `crx_persona/rl_a1_ability/pipeline.py` | 113 | 113 | complete |

IMG_8133 was not in the batch; every file still reaches its on-screen line count, so nothing is missing. IMG_8233 is
the Explorer tree (no code).
Checks: everything compiles, ruff F/E9 clean; the RL wrappers' calls match the signatures of the
mirrored CC / `_dpd_journey` functions they delegate to.

Not seen yet: `rl_departure_signature/pipeline.py` (registered in `pipeline_registry.py:240`),
`rl_a3_payment_credibility/`, `cc_a3_payment_credibility/`, `cc_a4_class/`, `cc_a1_ability/`
(`nodes.py` — `_TAU_SALARY_H2_MIN` — and `enrichers.py`, now also `enrich_salary_stop_month`,
`enrich_casa_eod_avg_balance`, `enrich_ext_loan_payments_h2`, `join_required_signals`,
`RequiredJoin`, `log_a1_stats`), `scoring_engine.py`.

Uncertain characters: `rl_a1_ability/pipeline.py:13–15` bracket glyphs beside "parallel"
(┐ ┤ ┘, as in batch 4); `rl_a1_ability/nodes.py:613–614` the "~" in "(NULL ~where feature
absent)" is on screen as written.

## Review findings

Moved to [REVIEW_OBSERVATIONS.md](REVIEW_OBSERVATIONS.md).
