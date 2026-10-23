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
| `crx_persona/cc_raw_extract/pipeline.py` | ≥47 | 48 | **line 48+ not photographed** — closing `    )` inferred |
| `crx_persona/cc_raw_extract/nodes.py` | 267 | 267 | complete |
| `crx_persona/cc_payment_trajectory/pipeline.py` | 38 | 38 | complete |
| `crx_persona/cc_payment_trajectory/nodes.py` | 781 | 781 | complete |
| `crx_persona/cc_utilisation/pipeline.py` | 41 | 41 | complete |
| `crx_persona/cc_utilisation/nodes.py` | 569 | 569 | complete |
| `pipeline_registry.py` | 255 | — | only lines 220–255 seen → `_partial/` |

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
4. `cc_utilisation/nodes.py` 37 and 350: right end of the RLIKE pattern was cut off; assumed
   `'CASH ADVANCE|CASH DISBURSEMENT'` (matches the code at 375).
5. `cc_utilisation/nodes.py` 469: comment end cut off; assumed `… increasing toward T0)`.
6. `cc_payment_trajectory/nodes.py` 387: `trunc(t0,'month')` — the closing quote looked curly.

No uncertainty in executable code.

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
