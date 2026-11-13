# Transcription: Claude Code session, merge of the DE bureau salary chain (phone photo IMG_9066, 2026-11-13)

## Context
- Photo of a VS Code window (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99) with `pipeline_registry.py` open in the editor and a Claude Code session in the integrated terminal.
- Breadcrumb: `src > enbd_collections > pipeline_registry.py > register_pipelines`. Sticky scroll line 119: `def register_pipelines() -> dict[str, Pipeline]:`
- Claude Code status line: `Sonnet | mode: auto | 4%` - branch `feature/persona_refactor` (modified:1, untracked:1, ahead:30, stash:1) - `retail.collections.risk_profiling` - `tkn: 476.0K in: 434 op: 475.6K`
- Second line: `Today Overall Usage burn: 0.0% tkn: 477.0K in: 436 op: 476.6K`; `auto mode on (shift+tab to cycle)`
- VS Code status bar: Ln 171, Col 50, Spaces: 4, UTF-8, LF, Python; git blame "You, 20 hours ago" / "vajdab (19 hours ago)". "Update installed - Restart to apply".
- Transcribed from the photo, not copied from files. Verify names and numbers against the real session.

## Editor (lines 248-254 of `pipeline_registry.py`)

```python
248        # TEMPORARY (A1 bundle 24): the A1 bureau check; removed by the bundle's cleanup.
249        "crx_cc_a1_b24_check": crx_a1_b24_check.create_b24_check_pipeline("cc"),
250        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
251        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
252        "crx_cc_a3_payment_credibility": (
253            crx_cc_a3_payment_credibility.create_pipeline()
254        ),
```

## Terminal (Claude Code), top of the visible part, tail of the previous answer

- `tasks/todo.md`: I kept both sides' sections.

The DE catalog has no entries for `stg_aecb_crr_audit` and `stg_aecb_metric_cif`, so those two entries from my branch are gone. No pipeline in `src` uses them; only `test_stg_bureau.py` imports the node functions. If you want the catalog entries back, I can re-add them.

Your two uncommitted files, `inhouse_check_results.md` and `a3_v1h/summary_v1h.md`, are untouched.

Sautéed for 57s - done 10:33 AM

## Prompt

> what are the new / changed items?

## Claude Code response

Ran 1 shell command

The merge added 56 files (+1,352 / -69), all in bureau. The only file outside src and conf is `tasks/todo.md`.

**New nodes (the DE salary chain)**
- Staging: `stg_aecb_subj_charac`, `stg_aecb_sub_basic_dtl`, `stg_aecb_crr_audit` and `stg_aecb_metric_cif`, plus a shared `_scope.py`.
- Primary: `prm_bureau.py` gained `_add_cif_id` (shared bulk/mongo cif_id logic), `build_salary_history` (→ `prm_bureau_salary_history`) and `build_subj_charac`.
- Intermediate:
  - `int_bureau_alert_salary_monthly` takes salary from the four salary alert types, keeping the latest extract per CIF per month.
  - `int_bureau_salary_credit_monthly` takes salary from the credit history.
  - `int_bureau_salary_monthly` takes salary from bureau salary history.
- Feature: `feat_bureau_salary_unified` combines the three sources into one monthly salary per CIF. The priority is alert, then salary_credit, then bureau_salary. A 0 or null value is filled from the next source, and the result carries a `salary_source` column.

**Changed**
- `stg_aecb_salary_history` now keeps `source_identifier` and is reworked (+46 lines).
- `stg_aecb_alert` has a small change (+8 lines).
- `pipelines/bureau/` (staging, primary, intermediate, features, `__init__`) has the new node registrations, and `pipeline_registry.py` has 5 new lines.
- `parameters.yml` has 6 changed lines. One of them lists `sa_ops_aecb_crr_audit` as a staging source.
- The two catalog files are covered in my previous message. `feat_bureau_salary_unified` now lives only in `catalog_outputs.yml`.

**Tests**
- Schema registries and tests were extended for all four layers: staging, primary, intermediate and feature.
- About 30 new or updated JSON fixtures went in. They include `_mixed` and `_uni_in` variants for the null/zero fallback cases.
- I haven't run any of them.

Two other things came from this branch:
- The `dt_of_return` (cheque return date) field on `BureauAlertEnriched`, from the head commit. The Python for it lives under `src/data_engineering/`, which my diff above didn't cover.
- My own `feat_cif_bureau_salary_monthly` (A1's input) now reads the DE-owned `feat_bureau_salary_unified`.

Its `todo.md` entries still show "black / pylint / pytest - blocked", meaning the DE side hasn't run its tests either.

Sautéed for 12s - done 10:34 AM
