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

## Spotted while transcribing (left as-is; candidates for the review tasks)

- `cc_utilisation/nodes.py` 226–228: comment says "take max util if duplicates" but code uses
  `F.first` → non-deterministic. Same pattern in `cc_payment_trajectory/nodes.py` 638–639 (`F.first("d_m")`).
- `cc_spell/nodes.py` 97: `regexp_extract(...).cast("int")` on `""` — the ANSI-mode issue already fixed
  in `cc_full_history` (F1) is still present here; dedupe is `.distinct()`, not worst-bucket (F2).
- `account_id` leaves T04b/T05 as `string` (trajectory 170, utilisation 127) while spell/raw-extract use `long`.
- `spend_cliff_flag` falls back to `0`, never NULL, so its logged coverage is always 100%.
- `txn_cnt_slope` / H1–H2 spend means only see months with ≥1 outflow; zero-spend months are absent, not 0.
- `_compute_w_pre_truncation` docstring says account-open month is "min obs_date"; code uses `open_date`.
- `cc_spell` steps go 0 → 2 (no Step 1).

Batch 2:
- Departure Pass A sign convention vs Pass K: Pass K treats `txn_amount_aed > 0` as purchase, while
  `cc_utilisation` (T05) says outflows are negative and filters `direction == -1`. One of them is wrong
  for `crx_cc_transactions` (`settl_amount` cast straight through in `cc_raw_extract`).
- Pass A `last_txn_foreign_flag` and Pass J read up to `spine_obs_date` (post-T0) — intentional per the
  docstring "anchor-change", but it breaks the module header's "all joins enforce strict obs_date < M0".
- Pass B filters `tran_dc == 'C'` before computing `is_salary`, then `is_salary` re-checks it (harmless).
- Pass E (`aecb_leverage_slope`) and `cross_border_outflow_cnt_h2` are documented as always NULL (T21 drop).
- **Likely bug — Pass I (nodes 1945–1951):** `m_from_m0 = floor(months_between(trunc(t0), pay_month))`
  but `pay_month` is a month-END date (yyyyMMdd last day). For t0 in June: May-31 → 0.03 → 0,
  Apr-30 → 1, Mar-31 → 2. So the M0-1 month gets index 0 and drops out of H2 = [1, 3]; H2 really
  sees only 2 months and H1 starts one month late. `payroll_present_h2` / `payroll_stopped_flag`
  are affected. Fix: `trunc(pay_month, 'month')` inside months_between, as Passes A/D/E do.
- `build_departure_spell_base` takes `max(observation_date)` from `cc_spine` per contract — multiple
  spine rows (re-entry) collapse to the latest.
