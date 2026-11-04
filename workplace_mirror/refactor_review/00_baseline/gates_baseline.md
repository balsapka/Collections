# Baseline gate run (Phase 0)

Run 2026-11-04 on `refactor/persona_review` at `088580b` (code = bundle 14 head), macOS,
Python 3.13, PySpark 3.5.3, Kedro 1.7.0, `JAVA_HOME=/opt/homebrew/opt/openjdk@17`, Spark
`local[2]`. Every later round must reach at least this result.

| # | Gate | Command | Result | Key numbers | Time |
|---|---|---|---|---|---|
| 1 | py_compile | `find …/crx_persona -name '*.py' \| xargs python -m py_compile` | **pass** | 79 files | <1 s |
| 2 | Lint (per file) | `python workplace_mirror/checks/refactor_metrics.py` | recorded | see `metrics.md`; tier L: pylint 9.98 (line-weighted, lowest file 9.62 `_dpd_journey/states.py`), ruff 178 findings (58 in `_dpd_journey/__init__.py`, the re-export block) | 24 s |
| 3a | A1 spec | `JAVA_HOME=… python workplace_mirror/checks/a1_engine_spec.py` | **pass** | 69/69 cases + dating, lanes, anchor, returns, loan-salary checks | 31.7 s |
| 3b | A2 spec | `… a2_engine_spec.py` | **pass** | 36/36 cases (32 at 60–180 + 4 reachability at 180+) | 23.3 s |
| 3c | A4 chain spec | `… a4_chain_spec.py` | **pass** | all checks | 14.7 s |
| 4a | Golden record | `… checks/refactor_golden.py --record` | **pass** | 14 runs, 79 datasets, 3 guards fired | 3 min 34 s |
| 4b | Golden compare (parquet, `exceptAll` both ways) | `… checks/refactor_golden.py` | **pass** | 79/79 identical, 0 DIFF | 3 min 39 s |
| 4c | Golden compare (manifest hash only, parquet moved away) | same, without `golden/*/` | **pass** | 79/79 hashes equal | 2 min 57 s |
| 5a | Import smoke + catalog | `python workplace_mirror/checks/refactor_smoke.py` | **FAIL (baseline)** | 23 crx pipelines build (A3 incl.); 1 failure, below | <1 s |
| 5b | `kedro registry list` | — | not runnable | the mirror has no `pyproject.toml` / settings; 5a replaces it | — |

## Golden runs (4a, per run)

| Run | Datasets | Time |
|---|---|---|
| `crx_cc_a1_ability.cc_60_180` (obs base + A1) | 7 | 14.3 s |
| `crx_cc_a2_locatability.cc_60_180` (obs base + A2) | 6 | 19.3 s |
| `crx_cc_a4_deterioration.cc_60_180` (full history + A4) | 3 | 5.0 s |
| `crx_cc_a1_ability.cc_180_plus` | 7 | 11.3 s |
| `crx_cc_a2_locatability.cc_180_plus` | 6 | 19.0 s |
| `crx_cc_a4_deterioration.cc_180_plus` | 3 | 4.5 s |
| `crx_cc_a4_deterioration.cc_60_180_alt` (every `dpd_journey` switch flipped) | 3 | 3.3 s |
| `crx_rl_a1_ability.rl_60_180` | 7 | 11.6 s |
| `crx_rl_a2_locatability.rl_60_180` | 6 | 19.5 s |
| `crx_rl_a4_deterioration.rl_60_180` | 6 | 9.1 s |
| `crx_rl_a1_ability.rl_180_plus` | 7 | 13.1 s |
| `crx_rl_a2_locatability.rl_180_plus` | 6 | 28.6 s |
| `crx_rl_a4_deterioration.rl_180_plus` | 6 | 8.9 s |
| `crx_rl_a4_deterioration.rl_60_180_alt` | 6 | 7.7 s |

Input building (A1 spec executed, A2 spec `main` run) takes about 40 s of the total. Every
state value and history-rule counter listed in `harness_coverage.md` is reached; no gaps.

## Gate 5a failure on the baseline (recorded, not fixed)

```
FAIL crx_cc_a3_payment_credibility: input crx_cc_billing not in catalog_crx.yml
```

`crx_cc_billing` is written by `crx_cc_raw_extract` (K) and read by the CC A3 pipeline (A), but
has no catalog entry in the mirror. Neither file is tier L. Likely a mirror gap (the workplace
catalog may have it); to confirm with the user / workplace. Later rounds compare against this:
the gate passes when no **new** failure appears.

Also reported by 5a, not failures:
- 24 workplace modules are stubbed (other domains' pipelines; for crx code only
  `nodes.primary.cc_way4.prm_cc`, `nodes.utils.config.EDP_LOAD_DATE_BUFFER_MONTHS`,
  `nodes.features.dcore._feat_dcore_utils`, `nodes.utils.config_dcore`);
- 7 crx packages have no `__init__.py` in the mirror (`crx_persona`, `cc_spell`,
  `cc_full_history`, `cc_payment_trajectory`, `cc_utilisation`, `cc_departure_signature`,
  `cc_a4_deterioration`); the smoke test reads their `pipeline.py`;
- 18 crx node outputs are memory-only inside their own pipeline (A3 intermediates,
  `crx_cc_acct_windows`, `crx_rl_depart_*`);
- 33 non-crx datasets live in catalogs not mirrored (spines, primaries, features);
- every `params:` key resolves (`parameters_*.yml` + `globals_dev.yml`).

## How to rerun

```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a1_engine_spec.py
JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a2_engine_spec.py
JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a4_chain_spec.py
JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/refactor_golden.py
python workplace_mirror/checks/refactor_smoke.py
python workplace_mirror/checks/refactor_metrics.py <out dir>   # never over 00_baseline
```
