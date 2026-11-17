# Bundle 25 preflight: symbol grep and A3 catalog listing (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. It is read-only and needs no data. Paste its answer back here.

````text
Goal
We are about to ship a refactor of the A1 ability and A3 credibility code (plus small changes in the
shared layer, bureau and product features). The mirror we work from lacks workplace-only code (tests,
extra modules, extra catalog entries). Before we build the bundle we need two facts from the real
workplace repo. Answer both in one batch.

Hard rules
- Read-only. No edits, no commits, no pipeline runs, no data access.
- Search src, tests, conf, notebooks and any other tracked folder (use git grep).
- Report exact path:line for every hit. Say "0 references" for a symbol with none. Do not shorten or
  merge the lists below.
- "Inside" = a file the bundle rewrites (list at the end). "Outside" = every other file. We only care
  about outside hits; mention inside hits only as a count.
- Match whole words. Names that are common words (`_window`, `__all__`, `_floor`) must be checked in the
  named file's module context: report only imports or uses that resolve to the symbol below.

Task 1: symbol grep
For each symbol, find every remaining reference outside the rewritten files. Paths are under
`src/enbd_collections/`. Symbols were removed, renamed or moved, so a hit outside means a workplace-only caller
(tests, notebooks, other modules) that will break.

Removed or renamed
- `pipelines/crx_persona/_common.py`: `lookback_floor`
- `nodes/features/products/feat_cif_cross_product.py`: `PRODUCT_TYPES`
- `nodes/primary/products/prm_products.py`: `_window` (now `_load_bound`)
- `pipelines/crx_persona/a1_ability/signals.py`: `_with_next_month` (now `_with_carry`)
- `pipelines/products/features.py`: `_cross_product_node`
- `pipelines/crx_persona/a1_ability/__init__.py`: `__all__` (names stay importable)
- `pipelines/crx_persona/a1_ability/classify.py`: `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`, `FLOW_FLOOR`,
  `FLOW_ANCHOR_MULT`, `BALANCE_FLOOR`, `BALANCE_ANCHOR_MULT`, `ASSET_FLOOR`, `ASSET_ANCHOR_MULT`,
  `MONEY_IN_SOME`, `MONEY_OUT_SOME` (now `STRONG_FLOOR`, `STRONG_ANCHOR_MULT`, `FLOW_SOME`)
- `pipelines/crx_persona/a1_ability/classify.py`: `_strong_months(prefix, floor, w)` (the second parameter
  is now `anchor`); `_flow_level(prefix, some_floor, anchor, w)` (now `_flow_level(prefix, anchor, w)`)
- `pipelines/crx_persona/a3_credibility/constants.py`: `FOLLOWUP_RUN_DAYS`, `MATCH_DAYS`,
  `STATEMENT_FALLBACK_D`
- `pipelines/crx_persona/a3_credibility/promises.py` and `sources.py` (old promise rule): `_followup_promises`,
  `_consolidate`, `_cutoff`, `_with_due`, `_with_paid`, `_with_paid_by`, `_event_starts`, `_run_step`,
  `_no_runs`
- `pipelines/crx_persona/a3_credibility/constants.py`: `DEADLINES` (now in `promises.py`)
- `pipelines/crx_persona/_common.py`: `pit_latest` lost its `anchor=` keyword

Moved
- `pipelines/crx_persona/a3_credibility/sources.py` to `promises.py`: `build_promise_events`, `EVENTS`
  (a test importing them from `.sources` breaks; `from ...a3_credibility import build_promise_events`
  still works)
- `pipelines/crx_persona/cc_raw_extract/nodes.py` to `cc_a3_payment_credibility/nodes.py`:
  `build_cc_acct_windows` (parameters renamed `crx_cc_obs_base` to `obs_base`,
  `crx_cc_a4_deterioration` to `deterioration`; node, dataset and pipeline names unchanged)
- `pipelines/crx_persona/a3_credibility/constants.py` to `cc_a3_payment_credibility/nodes.py`:
  `CYCLE_MAX_DAYS`, `FLOOR_LOOKBACK_DAYS`, `BUCKET08_BASELINE_MONTHS`

Changed signatures (find callers outside the rewritten files, including tests that call them with the
old arguments)
- `a1_ability/signals.py`: `build_income_signals`, `build_distress_signals`, `build_eosb_signals` (new
  keyword-only `crx_persona: dict`)
- `pipelines/crx_persona/rl_a1_ability/nodes.py`: `build_rl_liquidity_anchor(obs_base, int_loan_master,
  crx_persona)`
- `a3_credibility/signals.py`: `build_contact_signals` (`max_months=` removed)
- `a3_credibility/constants.py`: `promise_deadline(product, model_id, override=None)`
- `a1_ability/classify.py`: `cross_product_level(anchor, _w)` (second parameter renamed)
- `nodes/primary/products/prm_products.py`: `_latest_in_month(df, key, day, value)` (new `value`)
- `a3_credibility/promises.py`: `_events(promises, days)` (was `_events(rows, starts)`)
- `a1_ability/signals.py`: `_floor(crx_persona, months)` is now `persona_floor`
- `nodes/utils/frames.py`: `history_floor` is new (only report if a workplace module defines its own
  function with that name that could clash)

Also report any test or notebook that asserts on the A3 log label `A3 credibility` (it is now
`a3_credibility [<model_id>]`).

Dead packages (planned deletion in a later bundle). Under `src/enbd_collections/pipelines/crx_persona/`:
`_spine_utils.py`, `rl_a4_spine/`, `rl_spell_table/`, `cc_spell/`, and the function `build_cc_limits` in
`cc_raw_extract/nodes.py` (with its node in `cc_raw_extract/pipeline.py` and the dataset `crx_cc_limits`).
Related dataset names: `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine`, `crx_cc_limits`,
`raw_stg_limit`. For each, list who imports or references it: python imports, pipeline registry
(imports and entries), catalog entries (every file in `conf/`, every model_id variant), parameters, tests,
notebooks, checks. Also list who reads `raw_stg_limit`. We do not delete anything in this task.

Unread CASA features. In the mirror nothing reads the datasets `feat_cif_casa_activity_monthly` and
`feat_cif_ext_card_payment_monthly`. List every reader in the workplace (node inputs in any pipeline,
catalog entries, notebooks, tests), or say "0 readers" for each. Add them to table (b).

Task 2: A3 catalog listing
We want to persist two new datasets per product, `crx_<p>_a3_dues` and `crx_<p>_a3_payments` (`<p>` = `cc`,
`rl`). Our apply tool can silently drop a workplace-only block that sits next to an edited line, so we
need the exact workplace state. We will diff your answer against our reference
(`bundle_helpers/a3_final/workplace_reference.md`: `catalog_crx.yml` lines 14 to 78, which already show
`crx_cc_acct_windows` and `crx_cc_billing`). Give us:
1. Every top-level key of the workplace `conf/base/catalog/catalog_crx.yml`, in file order, with its line
   number (keys only, no bodies).
2. The full body, comments included, of every entry in `conf/` whose name contains `a3` (any file, any
   model_id variant).
3. Whether a key named like `crx_cc_a3_dues`, `crx_rl_a3_dues`, `crx_cc_a3_payments`,
   `crx_rl_a3_payments` (or any key containing `a3_dues` / `a3_payments`) already exists anywhere in
   `conf/`, with path:line.
4. Every line of `pipeline_registry.py` that mentions `a3`, with line numbers, and the registry entries
   around them that are not in the mirror if you can see any.

Deliverable
Return one markdown block, nothing else, with:
(a) a table: symbol | status in workplace (absent / only in files the bundle rewrites / referenced
    elsewhere) | path:line hits outside;
(b) a table for the dead packages and functions: item | referenced by (path:line, kind: import, registry,
    catalog, test, notebook, other);
(c) the catalog key list with line numbers, the `a3` entries in full, the answer on the two new dataset
    names, and the registry lines;
(d) anything surprising, for example workplace-only modules that import from A1, A3, `_common` or
    `cc_raw_extract` modules, tests that exercise the removed symbols, or other catalog keys next to
    `a3` entries that you would expect us to lose.

Files the bundle rewrites ("inside", paths from the repo root without the mirror prefix)
- `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` (rewritten)
- `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py` (rewritten)
- `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` (rewritten)
- `src/enbd_collections/nodes/primary/products/prm_products.py` (rewritten)
- `src/enbd_collections/nodes/utils/frames.py` (rewritten)
- `src/enbd_collections/pipelines/bureau/salary_bounces.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/_common.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/promises.py` (new)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/__init__.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/_window_utils.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` (rewritten)
- `src/enbd_collections/pipelines/crx_persona/scoring_engine.py` (rewritten)
- `src/enbd_collections/pipelines/products/features.py` (rewritten)
````
