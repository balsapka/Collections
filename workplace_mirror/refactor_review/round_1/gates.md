# Round 1 gates

Run 2026-11-05 on the merged tree (S7 → S1 → S3 → S2 → S4, after the three reverts), macOS,
Python 3.13, PySpark 3.5.3, Kedro 1.7.0, `JAVA_HOME=/opt/homebrew/opt/openjdk@17`. Spark jobs ran
one at a time. Baseline: `00_baseline/gates_baseline.md`, `00_baseline/metrics.json`.

| # | Gate | Command | Result | Key numbers |
|---|---|---|---|---|
| 1 | py_compile | `python -m py_compile` on the 28 changed / added `.py` files | **pass** | 28 files |
| 2a | black | `black --check -l 88` on the same files | **pass (baseline)** | 27 unchanged; `pipeline_registry.py` would reformat (known non-crx baseline issue) |
| 2b | ruff | `ruff check --select F,E,W,I,B,SIM,UP` (per file, via `refactor_metrics.py`) | **pass** | 0 files gain findings; tier L 178 → 134 (−44: `_dpd_journey/__init__.py` 58 → 17 with `__all__`) |
| 2c | pylint | `PYTHONPATH=workplace_mirror/src pylint --disable=relative-beyond-top-level` (per file, via `refactor_metrics.py`; also run once on the 27 crx files: 9.97/10 overall) | **pass** | 0 files below baseline; tier L 9.98 line-weighted; `states.py` 9.62 → 9.70, `history.py` 9.86 → 9.87, every other changed file 10.00 |
| 3a | A1 spec | `JAVA_HOME=… python workplace_mirror/checks/a1_engine_spec.py` | **pass** | 69/69 cases + dating, lanes, anchor, returns, loan-salary checks (26 s) |
| 3b | A2 spec | `… a2_engine_spec.py` | **pass** | 36/36 (19 s) |
| 3c | A4 chain spec | `… a4_chain_spec.py` | **pass** | all checks pass (14 s) |
| 4 | Golden compare | `JAVA_HOME=… python workplace_mirror/checks/refactor_golden.py` (compare mode) | **pass** | `golden: pass`; 14 runs, 79 datasets identical; 3 guards fired (mid-month RL spine, prm_balance without OVD_06, unknown dpd_journey key) (211 s) |
| 5 | Import smoke | `python workplace_mirror/checks/refactor_smoke.py` | **pass (baseline failure only)** | 19 crx pipelines build (23 at baseline − 4 tier-D pipelines); only failure `crx_cc_a3_payment_credibility: input crx_cc_billing not in catalog_crx.yml` (baseline); memory-only outputs 18 → 16, packages without `__init__` 7 → 4 (tier D gone) |
| 6a | No new Spark actions in tier L | `git grep '\.(count|collect|first|take|show|toPandas)\('` on tier L, `d1ad38a` vs HEAD | **pass** | 10 call sites → 8; removed: RL A4 `collect` of spine accounts (S2-07), A4 state log `count`+`collect` folded into `log_latest_month`'s one job (S1-06). None added. (The moved `build_rl_depart_spine` is tier K and has no action; `rl_a4_spine/nodes.py` counts 2 by the metrics regex, the same lines it had in tier D.) |
| 6b | No `spark.read` | `grep -rn spark.read` on tier L | **pass** | 0 |
| 6c | No hard-coded model_id | grep `model_id = '…'` and `"cc_60_180"`-style literals | **pass** | only the four `MODEL_ID_SEGMENT` keys in `_common.py` (moved from `_dpd_journey/constants.py`, the map itself) |
| 6d | `node()` keywords | AST scan of tier-L `node(` calls | **pass** | 26 calls, all with `func=`, `inputs=`, `outputs=`, `name=`, `tags=`, no positional arguments |

## Gate failures during the merge, and what was done

First gate 2 run on the merged tree (all 5 stages, before reverts): golden, spec tests and smoke
passed, but three files gained a ruff finding. Bisected by stage commit with the metrics script and
`git blame`; each was one new over-long docstring or comment line (E501), traced to one proposal:

| File | Baseline → merged | Offending line | Proposal | Action |
|---|---|---|---|---|
| `_dpd_journey/_dates.py` | 3 → 4 | `:32` `"""Month as an integer (year * 12 + month - 1) — the Spark twin of ``_month_idx``."""` (89 chars) | S4-03 | reverted |
| `rl_a4_deterioration/nodes.py` | 5 → 6 | `:80` first line of the `_original_loan_months` docstring (90 chars) | S4-09 | reverted |
| `cc_a4_deterioration/nodes.py` | 9 → 10 (seen after the S4-09 revert, in the S2 stage commit) | `# The worst bucket on the account's earliest dated row: the smallest (date, -bucket).` (89 chars) | S2-06 | reverted |

Failing output (ruff, `--select F,E,W,I,B,SIM,UP --output-format concise`, the new lines only):

```
…/_dpd_journey/_dates.py:32:89: E501 Line too long (89 > 88)
…/rl_a4_deterioration/nodes.py:80:89: E501 Line too long (90 > 88)
…/cc_a4_deterioration/nodes.py:47:89: E501 Line too long (89 > 88)
```

After the reverts every gate above was run again on the final tree (results in the table). The
three proposals are behaviour-neutral (golden passed with them in); a one-line rewrap would make
each of them gate-clean, so they are candidates for round 2 (S4 / S2 re-submit).
