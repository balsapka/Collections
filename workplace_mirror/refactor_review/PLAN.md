# crx_persona A3 credibility + A1 ability: council review and refactor plan (run 2)

Status: **U0 approved 2026-11-14; round 1 running.**

Run 1 (all axes, signed off 2026-11-06, shipped as bundles 15 and 16) is on branch
`refactor/persona_review`; its plan is kept here as `run1/PLAN.md` (with its decisions, questions and final report). Since then A3 was built as an
engine (bundles 17–20, 23) and A1 moved to the evidence-family rule and product primaries (bundles
21, 24). Neither has been through the council in its current shape.

## 1. Goal

A3 and A1 at the standard A2 and A4 reached in run 1: readable, well designed, as short as clarity
allows, docstrings only where they help, validated against their specs. **Behaviour is preserved.**
Logic issues become questions for the user.

## 2. Scope (import graph and node inputs at `4536d52`, 2026-11-13)

Paths are under `workplace_mirror/src/enbd_collections/`.

| Tier | What | Lines | Treatment |
|---|---|---|---|
| **L** live | **A3:** `pipelines/crx_persona/a3_credibility/` (constants, sources, signals, classify, pipeline), `cc_a3_payment_credibility/`, `rl_a3_payment_credibility/` · **A1:** `a1_ability/` (signals, classify, pipeline), `cc_a1_ability/`, `rl_a1_ability/` · **scoring:** `scoring_engine.py` (only A1 and A3 use it) · **A1 features we wrote:** `nodes/features/products/feat_cif_cross_product.py`, `nodes/primary/products/prm_products.py`, `pipelines/products/`, `nodes/features/bureau/feat_cif_bureau_salary_monthly.py`, `feat_cif_bureau_bounces_monthly.py`, `pipelines/bureau/salary_bounces.py`, `nodes/utils/frames.py` · their entries in `catalog_crx.yml`, `catalog_products.yml`, `catalog_bureau.yml`, `parameters_*.yml` | 3,131 | full workflow |
| **S** shared, signed off in run 1 | `crx_persona/_common.py` (307), `_dcore_codes.py` (312), `_dpd_journey/anchor.py` (58) | 677 | editable where an A1 / A3 proposal needs it (user, §10 Q2); A2 and A4 pipelines are in the oracle |
| **A** designed in, edited in the workplace | `nodes/features/casa/feat_cif_casa.py` (618; lines 438–487 not photographed; the workplace Sonnet rewrote the netting and added the legs node), `feat_cif_casa_flow.py` (159), `pipelines/casa/features.py` (100) | 877 | reviewed; changes go to `casa_handoff.md` as a Sonnet prompt (user, §10 Q3) |
| **D?** dead candidates | `cc_spell/` (267), `rl_spell_table/` (403), `rl_a4_spine/` (133), `_spine_utils.py` (120): no A1 / A3 module reads their outputs since A3 moved to the obs base (bundle 17) | 923 | S7 confirms (imports, catalog consumers, registry); user approves the list (§10 Q4) |
| **K** live input of CC A3 | `cc_raw_extract/` (578): CC A3 reads `crx_cc_billing`, `crx_cc_balance`, `crx_cc_transactions` | 578 | editable when an A3 proposal needs it (user, §10 Q2); not polished for its own sake |
| **X** out of scope | A2 (`a2_locatability/`, wrappers, `location/`, `digital_login/`, `prm_casa.py`), A4 (`_dpd_journey/` except `anchor.py`, `*_a4_deterioration/`, `*_full_history/`), `obs_base/`, DE bureau chain (`feat_bureau_salary_unified.py`, `pipelines/bureau/features.py`), `feat_cif_windows.py` and `pipelines/casa/windows*.py` (workplace modules), staging, `config.py`, `pipeline_registry.py` (mirror incomplete: lines 54–130 and 180+), test modules (workplace Sonnet) | — | not reviewed; editable only when an accepted A1 / A3 proposal needs it (user, §10 Q2), except the files hard rules 6 and 9 protect |

**Bundle 25 = D-A3-29 + this refactor (user, 2026-11-13).** No bundle 25 was built or run. The
Master codes D-A3-29 (a follow-up promise after the event's deadline starts a new event) on the
branch **before** the baseline, with the spec test updated. The oracle is recorded after it, so the
council's zero-difference rule is measured against the post-D-A3-29 tree. The rest of the old
bundle 25 list (promise points, deadline, 180+ cut-offs, RL dispute codes) is still undecided and
stays out; the council leaves extension points for it. A1's carry / closure change waits on the DE.

**Corrections from Phase 0** (`00_baseline/inventory.md` §7): tier L is 3,162 lines after D-A3-29;
`scoring_engine.state_label` is also imported by `a2_locatability/classify.py`; `cc_spell/` is dead
only together with `build_cc_limits` / `crx_cc_limits` in `cc_raw_extract`; `a1_ability/signals.py`
imports `MONEY_IN_CLASSES` / `MONEY_OUT_CLASSES` from tier A `feat_cif_casa`; `cc_raw_extract` does
not import in the mirror (`config.EDP_LOAD_DATE_BUFFER_MONTHS` missing: the smoke baseline's six
failures); 12 workplace A3 catalog names are not in the mirror's `catalog_crx.yml`.

## 3. Hard rules (every agent prompt includes them)

1. **No behaviour change.** Same rows, columns, types and values. A suspected bug or spec mismatch
   is a finding, never a fix.
2. **Decisions are final:** `specs/A1_ability_spec.md` (S1–S16), `specs/A1_ability_family_rule.md`,
   `specs/A3_credibility_spec.md` (D-A3-1..29), DESIGN_REVIEW §6 / §7, the "Working rules" and
   "Decided" lists in `CLAUDE.local.md`, run 1's `decisions.md` and dropped proposals (FINAL_REPORT
   §4). X1–X10 are not proposed again.
3. **Kedro.** I/O only through node inputs and outputs; `model_id` from `params:model_id`; every
   `node()` has `func=, inputs=, outputs=, name=, tags=`; one layer per node; no `raw_` / `stg_`
   inputs in persona or feature nodes.
4. **Contracts.** Required columns through `require_columns`; customer signals at CIF level;
   observation dates are month ends; income month = larger of internal and bureau; distress =
   bureau ∪ internal.
5. **Names that must not change** without the user: catalog dataset names and paths, registry
   pipeline names, parameter keys, output columns. Internal renames are listed for the test owner.
6. **Catalog and registry.** The workplace has entries the mirror lacks. No edit next to a
   workplace-only block; compare with `bundle_helpers/a3_final/workplace_reference.md` first.
   `pipeline_registry.py` is not edited.
7. **No new Spark actions** (`count`, `collect`, `show`, `toPandas`). `log_latest_month` stays.
8. **Docstrings** say what the code does now: no bundle, ticket or O-number history.
9. **Tiers.** The focus is A3 and A1; any other file may be edited only when an accepted A1 / A3
   proposal needs it. Tier A files and the DE bureau chain are never edited here (handoff only).
   Imports must keep working, including the workplace-only `casa_windows` imports of `_cif` / `_require` /
   `_wm_month` from `feat_cif_casa`.

## 4. Roles

As in SKILL.md: Master (this session), Cartographer, S1–S7, R-E, R-I, R-O. S1, S6, R-O and the
Cartographer on Opus, the rest on Sonnet.

## 5. Phases

`workflow.md`, with these specifics:

- **Worktree** `.worktrees/council_a1_a3`, branch `refactor/council_a1_a3`, base `4536d52`
  (`refactor/a1_products`: bundles 21 + 24 + 23 with cleanups, the closest copy of the workplace).
- **Oracle.** Run 1's `checks/refactor_golden.py`, `refactor_smoke.py` and `refactor_metrics.py`
  are ported from `refactor/persona_review` and re-scoped: A1 (both products, both segments, every
  family and override), A3 (every dimension, promise event outcomes, Unknown rule, both deadlines),
  `product_primary`, `product_features`, `bureau_salary_bounces`, plus the A2 and A4 pipelines and
  the obs base as a regression guard (tier S is editable). Kedro `SequentialRunner`, in-memory datasets, Spark
  local, `JAVA_HOME=/opt/homebrew/opt/openjdk@17`, 2 GB driver memory, cache cleared between
  products. **One Spark job at a time**; agents never run Spark in parallel.
- **Rubrics.** Run 1's three frozen rubrics and scorecard are reused as they are. "Fits A3 easily"
  is read as "fits the pending A3 / A1 rule changes (bundle 25, carry) easily". No rubric agent
  runs unless the user wants them rewritten at U0.
- **Rounds.** R1 broad (S1–S4, S6, S7, then S5). From R2 specialists run one after another on the
  branch, each passing the gates before committing. Early stop after R2 if converged.

## 6. Gates (Master runs them after every merge)

Run from `workplace_mirror/`.

1. `python -m py_compile` on every changed file.
2. `black --check -l 88`; `ruff check --select F,E,W,I,B,SIM,UP`;
   `PYTHONPATH=src pylint --disable=relative-beyond-top-level` (no file below its baseline score).
3. Spec tests: `python checks/a1_engine_spec.py`, `python checks/a3_engine_spec.py`; also
   `a2_engine_spec.py` and `a4_chain_spec.py` when a file outside A1 / A3 is touched.
4. `python checks/refactor_golden.py`: identical outputs.
5. `python checks/refactor_smoke.py`: modules import, pipelines build, node inputs and outputs are
   in the catalog; nothing fails beyond the baseline.
6. Grep rules: no `spark.read`, no hard-coded `model_id`, no new `.count()` / `.collect()`, five
   keywords on every `node(`, no `stg_` / `raw_` inputs added.

## 7. Formats

The skill's `formats.md`. New findings also get an O-number in `REVIEW_OBSERVATIONS.md` (from O93).

## 8. Delivery

Mirror bundles built with `make_bundle.py` from the stage branch, applied in the workplace with
`apply_bundle.py`. One bundle, number 25: D-A3-29 + the refactor. PROD check = temporary Kedro
nodes in two steps: persisted output → D-A3-29 (the expected moves, D4 crosstab) → refactored
(**0 differing rows**), and A1 old vs new 0 differing rows; all four model_ids; cleanup prompt at the end. Tier A changes ship as a Sonnet prompt, not a bundle. Each bundle lists renamed and removed functions for the
workplace tests. Rebase on the latest workplace-equivalent head and re-run the gates before
building.

## 9. Folder layout

```
workplace_mirror/refactor_review/
  PLAN.md  run1/ (run 1 plan, decisions, questions, final report)
  00_baseline/  rubrics/  round_1..3/
  decisions.md  questions.md  casa_handoff.md  FINAL_REPORT.md
workplace_mirror/checks/refactor_golden.py  refactor_smoke.py  refactor_metrics.py
```

## 10. Decisions (user, 2026-11-13)

1. **Bundle 25** is rebuilt as D-A3-29 + the refactor on top; the old bundle 25 was never run.
2. **Any code may be edited**; the focus stays on A3 and A1.
3. **CASA features:** reviewed, changes handed to the workplace Sonnet as one prompt.
4. **Dead candidates:** deleted if S7 confirms them; the user approves the list at U0.
5. Defaults taken: run 1's rubrics reused (frozen), about 20 agent runs, R3 skipped if R2 converges.
