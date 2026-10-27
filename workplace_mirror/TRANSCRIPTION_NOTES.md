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

## Batch 6 — CC A1 v1, scoring_engine, conf (photos IMG_8234–8331)

| Module | Lines (screen) | Lines here | Status |
|---|---|---|---|
| `conf/dev/globals_dev.yml` | 57 | 57 | complete |
| `conf/base/model_configs.yml` | 36 | 36 | complete — comment column alignment approximate |
| `conf/base/parameters/parameters_crx_persona.yml` | 21 | 21 | complete |
| `conf/base/catalog/catalog_crx.yml` | 676 | 676 | complete — path of the file inside `conf/base` assumed |
| `crx_persona/cc_a1_ability/__init__.py` | 5 | 5 | complete |
| `crx_persona/cc_a1_ability/enrichers.py` | 1191 | 1191 | complete — lines 176–211 filled from the re-photo (IMG_8332) |
| `crx_persona/cc_a1_ability/nodes.py` | 1407 | 1407 | complete — all 17 `def`s on the same line as on screen |
| `crx_persona/cc_a1_ability/pipeline.py` | 198 | 198 | complete |
| `crx_persona/scoring_engine.py` | 100 | 100 | complete |

**`enrichers.py` gap:** IMG_8259 ends at line 175 (`LOG.warning(` inside `enrich_salary_stop_month`)
and IMG_8261 starts at 212 (`_CASA_EOD_BAL_SOURCE_COLS = {`). Lines 176–211 hold the rest of
`enrich_salary_stop_month` and probably a comment block for the CASA columns. They are filled with
`# <<MIRROR GAP …>>` marker lines so the line numbers stay aligned; the file does **not compile**
until they are replaced. Re-photograph `enrichers.py` lines 170–215. Never bundle this file before.

Checks: everything else compiles; ruff F/E9 clean apart from the known `__init__` re-exports and the
gap; YAML files parse; every enricher name `cc_a1_ability_v2` and `rl_a1_ability` import exists.

**The grep output was not in this batch** (IMG_8331 is the last `scoring_engine.py` page) — still
needed before removing v1 (catalog references are now visible in `catalog_crx.yml`, but other
consumers — reporting, notebooks, `conf/` outside the catalog — are not).

Uncertain characters: `enrichers.py:1117` the box between `cif_id` and `month_number` read as `×`;
`nodes.py:162` "N×M" (box glyph); `nodes.py:924` "D1–D5" (box glyph, read as en dash);
`pipeline.py:12–17` bracket glyphs beside "parallel".

### Batch 6 follow-up (IMG_8332–8334)

`enrichers.py` 176–211 transcribed; the file compiles and `cc_a1_ability`, `cc_a1_ability_v2`,
`rl_a1_ability` and `rl_a2_locatability` pipelines import (kedro stubbed). Every `catalog_crx.yml`
line number in the grep output (30 hits, 296–578) matches the transcription exactly.

**A1 reference grep** (outside the three ability folders; `.pyc` hits ignored):

| Where | What | Matters for v1 removal |
|---|---|---|
| `pipeline_registry.py:88, 91, 104, 232, 233, 239` | imports + registers `crx_cc_a1_ability`, `crx_cc_a1_ability_v2`, `crx_rl_a1_ability` | yes — rename / unregister |
| `conf/base/catalog/catalog_crx.yml:296–578` | v1, v2 and RL A1 dataset entries | yes — rename v2 to plain names, drop v1 / RL waterfall entries |
| `src/tests/pipelines/crx_persona/schema_registry.py:181, 187, 219` | `CRX_CC_A1_ABILITY` schema with `a1_state` | yes — **not in the mirror yet** |
| `src/tests/pipelines/crx_persona/test_crx_persona.py:31, 190` | imports `cc_a1_ability.nodes`, loads `cc_a1_ability_empty` | yes — **not in the mirror yet** |
| `src/tests/README_TEST_STRUCTURE.md:40` | tree listing `cc_a1_ability/` | doc only |
| `conf/base/catalog/catalog_casa_plus_ftr.yml:102` | comment mentioning `build_rl_a1_group_b_income_obs_anchored` | comment only |
| `_spine_utils.py:3`, `cc_spell/nodes.py:10`, `scoring_engine.py:3`, `rl_departure_signature/nodes.py:5, 8, 9` | docstrings naming the ability pipelines | text only |

No reporting, modelling or other pipeline reads `a1_state` / `crx_*_a1_*` — the A1 outputs have no
downstream consumer outside the persona code and its tests.

### `rl_departure_signature/pipeline.py` (IMG_8336–8338)

116 lines, matches the screen; all `crx_rl_*` packages now import (kedro stubbed).
Uncertain glyph: line 15 "steps 1–4" (box glyph, read as en dash).
The two test modules from the grep (`src/tests/pipelines/crx_persona/schema_registry.py`,
`test_crx_persona.py`) are **deliberately not mirrored**: the user will have the workplace Sonnet
update them as part of the A1 bundle prompt.

### `digital_login` pipeline (IMG_8372–8384, 2026-10-25)

- `pipelines/digital_login/pipeline.py` — 41 lines.
- `nodes/staging/digital_login/stg_digital_login.py` — 209 lines.
- `nodes/primary/digital_login/prm_digital_login_monthly.py` — 85 lines.
- Catalog entries (IMG_8390–8392, 2026-10-26): the three `raw_digital_*` Hive queries,
  `stg_digital_login` and `prm_digital_login_monthly` — recorded in
  `bundle_helpers/b04_a2/a2_v01_inventory_results.md` (not mirrored: the catalog YAMLs are
  only partly photographed).

All match the screen (line counts, `def` lines), compile, ruff F/E9 clean. Not seen: the
packages' `__init__.py` files and the catalog entries of the `raw_digital_*` / `stg_` datasets.
Uncertain glyphs: `×` in "(cif_id × month_number)" (box glyph on screen); separator lengths
approximate. Args-description column in the staging docstring read as column 40.

### PROD results handoff (2026-10-26, no photos)

The user could not move photos; a chat session transcribed 5 screen photos into
`pics/claude_code_handoff.md` (OCR quality). No code was on them. Filed as:

- A1: B03 OUTPUT + B03 INCOME → `bundle_helpers/b03/b03_check_results.md` (sums check out).
- A2: v01 `summary.md` (t1–t7, cc_60_180 + rl_60_180) →
  `bundle_helpers/b04_a2/a2_v01_results.md`, with the review; O59.
- Context only (Teams, DE on RL restructure predecessor matching, cf. T18 succession link):
  unmatched restructurings are Home → Personal cross-family ones, those before 2018-01 (no
  data), **Auto restructured since 2025-12** (the current history table has no Auto loans;
  a new table is recommended), and 531 loans whose predecessor is missing; 7 loans match through
  a two-step chain. Relevant to RL history-based features (A1 RL, A4) for Auto.
- Handoff 2 (`pics/claude_code_handoff_2.md`, 1 photo): A1 v02 DDS summary →
  `bundle_helpers/b03/sonnet_v02_summary.md` (G1 confirmed); the v02 prompt is removed.
- User, 2026-10-26: `cc_spine` and the DCORE inputs are still on mid-month billing dates in
  PROD (the month-end change is not rerun yet); A2 spec §2 and the v02 prompt say so.

### Handoff 6 (2026-10-27, photos 13–26, no full files)

Catalog format, `_ALERT_RENAMES`, `_join_cif_bridge`, `BureauSalaryHistory`, `BureauAlertEnriched`,
the A1 consumers grep (R7) and the repo layout (R8) → `bundle_helpers/a1_final/workplace_reference.md`
(partial files, so not under `src/`). The bureau salary model documents `reference_month` as
YYYYMM while the CC v1 code reads the staging column as MMYYYY: checked in A1 v03 (v2).

### Handoffs 7–9 (2026-10-27, photos 27–37, no full files)

- Handoff 7: A1 v03 `summary.md` (CC only, from the first prompt version) →
  `bundle_helpers/a1_final/a1_v03_results.md`; the missing parts go to `sonnet_a1_v03b_prompt.md`.
- Handoff 8: A2 v01 "Part 0 — follow-ups" → `bundle_helpers/b04_a2/a2_v01_results.md` and A2
  spec §10.
- Handoff 9: the gathered snippets (R4, R5, R8–R11) → `bundle_helpers/a1_final/workplace_reference.md`
  ("Handoff 9" and "What handoff 9 settles"); O59 updated, O61–O62 new; D1 answered (R4).

## Review findings

Moved to [REVIEW_OBSERVATIONS.md](REVIEW_OBSERVATIONS.md).

## Known limit: separator-line lengths

Comment rules (`# ── Node 1 ────`, `####…`) are transcribed with approximate lengths — the
exact count of `─`/`#`/`-` cannot be read from a photo (first seen: bundle 01 check,
2026-10-23). `apply_bundle.py` v3 compares runs of 4+ separator characters as equal and
keeps the workplace file's own separators on apply, so this never blocks a bundle.
The same goes for spacing and wrapping inside comments and docstrings (second PROD check,
2026-10-23): v4 accepts a file whose Python code (AST without docstrings) or YAML content
equals the photographed base. Only real code differences conflict.
