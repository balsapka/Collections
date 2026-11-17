# Mirror bundle 25 — A1 + A3 council refactor with the promise-event, refusal, bucket-08, same-day and points steps (D-A3-29..33) and the A1 strong amount

apply_bundle version: 7 · built 2026-11-17 from `4536d52..f20ecaf` · source: 3 added, 30 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/council_a1_a3_refactor
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/25_council_a1_a3_refactor.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '25_council_a1_a3_refactor.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/25_council_a1_a3_refactor.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go, and fix what it finds before committing:

1. **Catalog and registry.** List every top-level key the apply removed from `conf/base/catalog/catalog_crx.yml` and `src/enbd_collections/pipeline_registry.py` compared with the last commit, and put back any that went missing (the 8 workplace A3 entries `crx_<p>_a3_payment_cycles` / `crx_rl_a3_dlq_cycles`, `*_dlq_payment_signals_single_payment_cycle_count`, `*_pre_dlq_payment_signals_single_payment_cycle_count`, `*_strong_negative_signals` must survive). `crx_cc_a3_dues`, `crx_cc_a3_payments`, `crx_rl_a3_dues`, `crx_rl_a3_payments` are each defined exactly once in `conf/`. The new `tmp_b25_check.yml` holds one dataset pattern, `"{name}__b25"`: confirm this Kedro version resolves it (for example, `crx_cc_a3_dues__b25` resolves to a SparkDataset under `.../b25_check/crx_cc_a3_dues`). `kedro registry list` shows `crx_cc_b25_check` and `crx_rl_b25_check`.
2. **Imports the mirror cannot check.** `b25_check.py` imports `cc_a4_deterioration.pipeline` and `cc_raw_extract`: confirm both import, and that `nodes/utils/config.py` has `EDP_LOAD_DATE_BUFFER_MONTHS` (`cc_raw_extract` needs it). Review the `cc_raw_extract/nodes.py` diff explicitly: apart from shorter docstrings, only the column checks and dict inputs change.
3. **Tests.** Update the workplace tests to the new code: `test_a1_ability.py` (`build_income_signals`, `build_distress_signals`, `build_eosb_signals` take keyword-only `crx_persona`; `cross_product_level(anchor, _w)`; the strong amount max(3,000, 2 x anchor) replaces the per-family floors), `test_a3_promise_events.py` (`build_promise_events` and `EVENTS` now in `a3_credibility/promises.py`; `_cutoff` is gone; `promise_deadline(product, model_id, override=None)`; the D-A3-29 event rule; levels `promised` / `no_promise`; points Kept 3 / Partly 2 / Broken 1 / Promised 1), `test_feat_cif_cross_product.py` (`PRODUCT_TYPES` removed). Run the crx_persona, products and bureau tests. Do not touch `tmp_validation/`.
4. Black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Bundle 25: A1 + A3 council refactor, D-A3-29..33, A1 strong amount, persisted A3 dues / payments, temporary check" && git push -u origin feature/council_a1_a3_refactor
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/25_council_a1_a3_refactor.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/council_a1_a3_refactor && git pull
```

The persisted tables are the baseline: do not re-run any persona, product or bureau pipeline before the check. Set `model_id` in `conf/dev/globals_dev.yml` for each run.

**Step 7.** Run the check for **all four model_ids** (`crx_cc_b25_check` for cc_60_180 and cc_180_plus, `crx_rl_b25_check` for rl_60_180 and rl_180_plus). It reruns every pipeline it compares, so it takes about as long as those pipelines together:

```bash
kedro run --env=dev --pipeline=crx_cc_b25_check
```

```bash
kedro run --env=dev --pipeline=crx_rl_b25_check
```

Paste back, per model_id, every `=== B25 … START ===` … `END ===` block (`B25 DIFF`, `B25 A3 EVENTS`, `B25 A3 LEVELS`, `B25 A3 MOVES`, `B25 A3 DUES`, `B25 A1`, and `B25 PARENT LINK` for the cc model_ids) and the total run time of each run (cc_180_plus above all).

**Step 8.** After the blocks are reviewed, write the real tables for **all four model_ids**, in this order (`rl` names for the rl model_ids; `crx_cc_raw_extract` is cc only):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=crx_cc_raw_extract
```

```bash
kedro run --env=dev --pipeline=crx_cc_a4_deterioration
```

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

A pipeline whose `B25 DIFF` lines all show 0 on both sides may be skipped (its persisted table already matches); A1 and A3 always run. Then the cleanup prompt, and after it the A3 results prompt (`workplace_mirror/bundle_helpers/a3_final/sonnet_a3_results_prompt.md` in the mirror).

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The second council review of A1 ability and A3 credibility: a refactor that changes no output, plus the behaviour steps the user decided (2026-11-14 to 2026-11-17). Apply after bundles 23 and 24 and their cleanups (base = the workplace state after them).

**Behaviour steps (outputs change):**
- **A3 promise events (D-A3-29):** plans and follow-up promises are one stream. An event starts with a promise and stays alive until its deadline passes or the payments since its day reach the promised amount; every promise meanwhile belongs to it (no 7-day chaining or plan matching). Promised amount = the latest known due on the event day, never below 100 AED. A card's next-statement deadline is at most 31 days after the promise. New module `a3_credibility/promises.py`.
- **A3 refusal (D-A3-30):** counted only when nothing may have followed it: a payment of 100 AED or more on or after the refusal day (loans: in the refusal month or later), or a plan starting on or after it, lifts it.
- **A3 card due at bucket 08 (D-A3-31):** on a statement with `overdue_bucket_08` non-zero, one month's due = the average ladder due of the latest 12 months before bucket 08 first held money (none = no due).
- **A3 same-day contacts (D-A3-32):** several dispositions on the latest contact day: promise > payment reported > refusal > dispute > contact > hung up.
- **A3 promise points (D-A3-33, GRR accepted):** Kept 3 / Partly kept 2 / Broken 1 / Promised 1 / No promise 0. New level `promised` (a promise in the 12-month window, none kept, not Broken); `thin` is renamed `no_promise`; new output column `commitments_n`. Thresholds unchanged (Moderate from 2, High from 4). The promise deadline stays GRR's.
- **A1 one strong amount:** max(3,000, 2 x anchor) for income, money in, money out, balance and assets; "some" for both flows = 1,000. `a1_sweepable_balance_flag` = the observation month's CASA balance at or above that amount (diagnostic).

**Refactor (no output change):** the CC read window moves into the CC A3 wrapper (`build_cc_acct_windows` now in `cc_a3_payment_credibility/nodes.py`); A1 source floors from `params:crx_persona`; one `promise_deadline(product, model_id, override)`; contact signals in one pass; A3 builders check their inputs; `cc_raw_extract` checks the columns it reads (docstrings shortened); `lookback_floor`, `PRODUCT_TYPES`, `pit_latest(anchor=)` and `build_contact_signals(max_months=)` removed; key helper `string_key` in `nodes/utils/frames.py`, used by the bureau features and the product primary. Renamed / moved symbols: see the UAT step (three workplace tests use old names).

**Persisted:** `crx_<p>_a3_dues` and `crx_<p>_a3_payments` get catalog entries (`catalog_crx.yml`, after each `*_a3_payment_credibility`); they were memory datasets.

**Check** (temporary, `pipelines/crx_persona/b25_check.py`, pipelines `crx_cc_b25_check` / `crx_rl_b25_check`): reruns the shipped pipelines (product primaries and features, bureau features, CC raw extract, A4, A2, A1, A3) with every output renamed `<name>__b25`, one catalog pattern in the new `conf/base/catalog/tmp_b25_check.yml`; the persisted tables are the baseline and no real output is touched. Blocks: `B25 DIFF` (every dataset old vs new: the refactor must give 0 rows only on one side; datasets a behaviour step changes are marked, and their other columns are compared on their own), `B25 A3 EVENTS`, `B25 A3 LEVELS`, `B25 A3 MOVES` (the state step by step: events and dues, refusal, points), `B25 A3 DUES` (cards at bucket 08 with no baseline; loans' EMI 0 / NULL / > 0 in the B window), `B25 A1` (old x new state and family levels, F1 / F2 / F3 strong with paid a due in the next 3 months), `B25 PARENT LINK` (cards: what `parent_contract_id` links). All four model_ids. Tested locally on the oracle's synthetic inputs (all diffs 0, recomputed state = output).

Gates in the mirror: A1 spec 93/93, A2 36/36, A3 spec, A4 chain spec, oracle 188 datasets; black, ruff and pylint clean on the touched files.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. A `MERGED` file differed from the copy
   this bundle was built from; show the user its `git diff` before committing.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `conf/base/catalog/catalog_crx.yml` |
| add | `conf/base/catalog/tmp_b25_check.yml` |
| replace | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` |
| replace | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py` |
| replace | `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` |
| replace | `src/enbd_collections/nodes/primary/products/prm_products.py` |
| replace | `src/enbd_collections/nodes/utils/frames.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/bureau/salary_bounces.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_common.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/promises.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py` |
| add | `src/enbd_collections/pipelines/crx_persona/b25_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/_window_utils.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/scoring_engine.py` |
| replace | `src/enbd_collections/pipelines/products/features.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `c442da7bbb7eb56c41fd593ed0b5335277bdcfd5aff8b03b8e124000343c9810` · base trailing newline: yes · new sha256 `a18ca273a8e4cbc66fc5bbc91300be0efcc6b34b94c2c59df690a77ea24758f4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the T03+ persona-axis pipeline live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- T04c: T0-scoped CC raw DDI intermediates ----------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions,
# crx_cc_balance and crx_cc_billing.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.
# Grain: (account_id). The per-account [acct_start, acct_end] window of the CC raw
# extracts, from the A3 episode anchor (build_cc_acct_windows).
crx_cc_acct_windows:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_cc_limits:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_limits"
  save_args:
    mode: overwrite

crx_cc_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_balance"
  save_args:
    mode: overwrite

# Grain: (contract_id, observation_date): one row per billing cycle, with due_date and
# next_billing_date (the next statement). A3 builds its cycles from it.
crx_cc_billing:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_billing"
  save_args:
    mode: overwrite

# -- CC full billing history ------------------------------------------------
# Grain: (account_id, billing_date) — one row per billing cycle.
# Full history, no date window — built straight from raw_stg_billing (dlq_bucket
# parsed from add_info), leftsemi-scoped to cc_spine.
crx_cc_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history"
  save_args:
    mode: overwrite

# -- T03: Delinquency-spell table (CC) ----------------------------------------
# Grain: (account_id, spell_id). One row per delinquency episode.
# T0 = spell anchor for all A4 features.
# Built from raw_stg_billing (no date/DLQ filter; leftsemi-scoped to cc_spine).
# model_id-namespaced so cc_60_180 and cc_180_plus runs do not overwrite each other.
crx_cc_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_spell_table"
  save_args:
    mode: overwrite

# -- CC A4 deterioration: DPD journey (one shuffle + per-account Python engine) --
# Built from crx_cc_full_history by the shared crx_persona/_dpd_journey/ package
# (CC scheme; RL uses the same package with its own scheme).
# restructure_blind_spot_flag is derived from crx_cc_full_history alone
# (see cc_a4_deterioration/nodes.py).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_cc_full_history gets a row (nothing silently dropped);
# build_cc_a4_deterioration keeps only build_status == 'ok'.
crx_cc_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: CC native 4-7; 180_plus:
# CC native 8-9).
crx_cc_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a4_deterioration"
  save_args:
    mode: overwrite

# ── CC A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_cc_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_cc_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_location_signals"
  save_args:
    mode: overwrite

crx_cc_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_cc_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── Observation base: (account_id, observation_date, cif_id), one per product ──
crx_cc_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_obs_base"
  save_args:
    mode: overwrite

crx_rl_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_obs_base"
  save_args:
    mode: overwrite

# ── CC A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_cc_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_cc_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_distress_signals"
  save_args:
    mode: overwrite

crx_cc_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
  save_args:
    mode: overwrite

# ── CC A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).
# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,
#             payment_credibility_low, payment_credibility_unknown}.
# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE plan
# instalments; crx_cc_a3_promise_events: the promise events judged by payment.
# Spec: workplace_mirror/specs/A3_credibility_spec.md.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_episode"
  save_args:
    mode: overwrite

crx_cc_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_instalments"
  save_args:
    mode: overwrite

crx_cc_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_promise_events"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B1) ───────────────────────────────────────────────────
# Grain: (account_id, month_end_date). Full pre-delinquency monthly history for
# all RL spine accounts. Source: int_loan_master (month-end snapshots).
# No date window — full history required for T0 identification (RL-B2) and
# pre-T0 A4 lookback (RL-A4-2). Date filter applied downstream in crx_rl_a4_spine.
crx_rl_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B2) ───────────────────────────────────────────────────
# Grain: one row per account_id. T0 anchor table with first delinquency onset
# date and pre-T0 behavioural metadata. spell_id=1 / spell_end=NULL adapter
# makes this compatible with join_spine_to_spell() (R18).
crx_rl_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_spell_table"
  save_args:
    mode: overwrite

# ── RL A4 Spine (structural — superseded CASA/EMI classifier removed) ───────

# Spine-grain structural projection (windowed to persona_start_date / persona_end_date).
# Grain: (account_id, observation_date). Carries cif_id, spell_id, t0 (sourced from
# crx_rl_spell_table) — no classification columns. Built by the rl_a4_spine pipeline.
# Filter point per TASKS_RL.md.
crx_rl_a4_spine:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine"
  save_args:
    mode: overwrite

# ── RL A4 deterioration: DPD journey (one shuffle + per-account Python engine) ──
# Built from crx_rl_full_history by the shared crx_persona/_dpd_journey/ package
# (RL scheme; CC uses the same package with its own scheme).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_rl_full_history gets a row (nothing silently dropped);
# build_rl_a4_deterioration keeps only build_status == 'ok'.
crx_rl_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: RL native 3-6; 180_plus:
# RL native 7).
crx_rl_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration"
  save_args:
    mode: overwrite

# Spine history with the original loans of matched restructured accounts in front.
crx_rl_full_history_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history_linked"
  save_args:
    mode: overwrite

# One row per restructure chain: when it is known, its size and match audit.
crx_rl_restructure_chains:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_restructure_chains"
  save_args:
    mode: overwrite

# crx_rl_dpd_sequences on the linked history.
crx_rl_dpd_sequences_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_linked"
  save_args:
    mode: overwrite

# ── RL A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_rl_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_rl_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_distress_signals"
  save_args:
    mode: overwrite

crx_rl_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability"
  save_args:
    mode: overwrite

# ── RL A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_rl_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_rl_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_location_signals"
  save_args:
    mode: overwrite

crx_rl_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_rl_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability"
  save_args:
    mode: overwrite

# ── RL A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain and states as CC (crx_rl_obs_base).
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_rl_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_episode"
  save_args:
    mode: overwrite

crx_rl_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_instalments"
  save_args:
    mode: overwrite

crx_rl_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_promise_events"
  save_args:
    mode: overwrite

crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite
`````

New:

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the T03+ persona-axis pipeline live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- T04c: T0-scoped CC raw DDI intermediates ----------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions,
# crx_cc_balance and crx_cc_billing.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.
# Grain: (account_id). The per-account [acct_start, acct_end] window of the CC raw
# extracts, from the A3 episode anchor (build_cc_acct_windows).
crx_cc_acct_windows:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_cc_limits:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_limits"
  save_args:
    mode: overwrite

crx_cc_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_balance"
  save_args:
    mode: overwrite

# Grain: (contract_id, observation_date): one row per billing cycle, with due_date and
# next_billing_date (the next statement). A3 builds its cycles from it.
crx_cc_billing:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_billing"
  save_args:
    mode: overwrite

# -- CC full billing history ------------------------------------------------
# Grain: (account_id, billing_date) — one row per billing cycle.
# Full history, no date window — built straight from raw_stg_billing (dlq_bucket
# parsed from add_info), leftsemi-scoped to cc_spine.
crx_cc_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history"
  save_args:
    mode: overwrite

# -- T03: Delinquency-spell table (CC) ----------------------------------------
# Grain: (account_id, spell_id). One row per delinquency episode.
# T0 = spell anchor for all A4 features.
# Built from raw_stg_billing (no date/DLQ filter; leftsemi-scoped to cc_spine).
# model_id-namespaced so cc_60_180 and cc_180_plus runs do not overwrite each other.
crx_cc_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_spell_table"
  save_args:
    mode: overwrite

# -- CC A4 deterioration: DPD journey (one shuffle + per-account Python engine) --
# Built from crx_cc_full_history by the shared crx_persona/_dpd_journey/ package
# (CC scheme; RL uses the same package with its own scheme).
# restructure_blind_spot_flag is derived from crx_cc_full_history alone
# (see cc_a4_deterioration/nodes.py).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_cc_full_history gets a row (nothing silently dropped);
# build_cc_a4_deterioration keeps only build_status == 'ok'.
crx_cc_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: CC native 4-7; 180_plus:
# CC native 8-9).
crx_cc_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a4_deterioration"
  save_args:
    mode: overwrite

# ── CC A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_cc_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_cc_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_location_signals"
  save_args:
    mode: overwrite

crx_cc_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_cc_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── Observation base: (account_id, observation_date, cif_id), one per product ──
crx_cc_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_obs_base"
  save_args:
    mode: overwrite

crx_rl_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_obs_base"
  save_args:
    mode: overwrite

# ── CC A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_cc_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_cc_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_distress_signals"
  save_args:
    mode: overwrite

crx_cc_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
  save_args:
    mode: overwrite

# ── CC A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).
# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,
#             payment_credibility_low, payment_credibility_unknown}.
# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE plan
# instalments; crx_cc_a3_promise_events: the promise events judged by payment.
# Spec: workplace_mirror/specs/A3_credibility_spec.md.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_episode"
  save_args:
    mode: overwrite

crx_cc_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_instalments"
  save_args:
    mode: overwrite

crx_cc_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_promise_events"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_cc_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_dues"
  save_args:
    mode: overwrite

crx_cc_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payments"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B1) ───────────────────────────────────────────────────
# Grain: (account_id, month_end_date). Full pre-delinquency monthly history for
# all RL spine accounts. Source: int_loan_master (month-end snapshots).
# No date window — full history required for T0 identification (RL-B2) and
# pre-T0 A4 lookback (RL-A4-2). Date filter applied downstream in crx_rl_a4_spine.
crx_rl_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B2) ───────────────────────────────────────────────────
# Grain: one row per account_id. T0 anchor table with first delinquency onset
# date and pre-T0 behavioural metadata. spell_id=1 / spell_end=NULL adapter
# makes this compatible with join_spine_to_spell() (R18).
crx_rl_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_spell_table"
  save_args:
    mode: overwrite

# ── RL A4 Spine (structural — superseded CASA/EMI classifier removed) ───────

# Spine-grain structural projection (windowed to persona_start_date / persona_end_date).
# Grain: (account_id, observation_date). Carries cif_id, spell_id, t0 (sourced from
# crx_rl_spell_table) — no classification columns. Built by the rl_a4_spine pipeline.
# Filter point per TASKS_RL.md.
crx_rl_a4_spine:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine"
  save_args:
    mode: overwrite

# ── RL A4 deterioration: DPD journey (one shuffle + per-account Python engine) ──
# Built from crx_rl_full_history by the shared crx_persona/_dpd_journey/ package
# (RL scheme; CC uses the same package with its own scheme).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_rl_full_history gets a row (nothing silently dropped);
# build_rl_a4_deterioration keeps only build_status == 'ok'.
crx_rl_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: RL native 3-6; 180_plus:
# RL native 7).
crx_rl_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration"
  save_args:
    mode: overwrite

# Spine history with the original loans of matched restructured accounts in front.
crx_rl_full_history_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history_linked"
  save_args:
    mode: overwrite

# One row per restructure chain: when it is known, its size and match audit.
crx_rl_restructure_chains:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_restructure_chains"
  save_args:
    mode: overwrite

# crx_rl_dpd_sequences on the linked history.
crx_rl_dpd_sequences_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_linked"
  save_args:
    mode: overwrite

# ── RL A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_rl_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_rl_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_distress_signals"
  save_args:
    mode: overwrite

crx_rl_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability"
  save_args:
    mode: overwrite

# ── RL A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_rl_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_rl_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_location_signals"
  save_args:
    mode: overwrite

crx_rl_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_rl_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability"
  save_args:
    mode: overwrite

# ── RL A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain and states as CC (crx_rl_obs_base).
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_rl_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_episode"
  save_args:
    mode: overwrite

crx_rl_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_instalments"
  save_args:
    mode: overwrite

crx_rl_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_promise_events"
  save_args:
    mode: overwrite

crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_rl_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_dues"
  save_args:
    mode: overwrite

crx_rl_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payments"
  save_args:
    mode: overwrite
`````

### FILE: `conf/base/catalog/tmp_b25_check.yml`
action: add · new sha256 `a1556ab0a3f23c849267fb8d09d6ddbfc6448b10f9fd3e30bda1c0a22a253728` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundle 25): every dataset crx_<p>_b25_check reruns, saved as <name>__b25;
# this file and the HDFS folder b25_check are removed by the cleanup.

"{name}__b25":
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/{name}"
  save_args:
    mode: overwrite
`````

### FILE: `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py`
action: replace · base sha256 `c5d9653ae0102575d6c38b21db8616cca961fdecba48c9bd7fdb91a9001542e7` · base trailing newline: yes · new sha256 `278a5a9c2ddc6e3f9f6a1d53f36ed9f4097e1b3a1c94cf5edc3169fabf433ee2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bounce, dated by the bureau's return date
(``dt_of_return``), not by the pull. A bounce is a ``(cif_id, dt_of_return)``: the same
return date repeated in later pulls is one bounce, and several cheques returned on one
day are one bounce with the largest amount.

* ``bounce_events`` — bounce days in the month;
* ``max_bounce_amount`` — the largest bounced amount of those days.

Rows with a bounced amount but no return date are not counted.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build(alerts: DataFrame) -> DataFrame:
    """Bounce days per month from ``prm_bureau_alert_enriched``."""
    missing = sorted(
        {"cif_id", "dt_of_return", "bounced_cheque_amount"} - set(alerts.columns)
    )
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    amount = F.col("bounced_cheque_amount").cast("double")
    bounces = (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & F.col("dt_of_return").isNotNull()
            & (amount > 0)
        )
        .groupBy(
            F.col("cif_id").cast("string").alias("cif_id"),
            F.to_date("dt_of_return").alias("bounce_date"),
        )
        .agg(F.max(amount).alias("amount"))
    )
    return bounces.groupBy("cif_id", F.last_day("bounce_date").alias("month_end")).agg(
        F.count(F.lit(1)).alias("bounce_events"),
        F.max("amount").alias("max_bounce_amount"),
    )
`````

New:

`````python
"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bounce, dated by the bureau's return date
(``dt_of_return``), not by the pull (S15). A bounce is a ``(cif_id, dt_of_return)``:
the same return date repeated in later pulls is one bounce, and several cheques
returned on one day are one bounce with the largest amount.

* ``bounce_events`` — bounce days in the month;
* ``max_bounce_amount`` — the largest bounced amount of those days.

Rows with a bounced amount but no return date are not counted.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import require_columns, string_key


def build(alerts: DataFrame) -> DataFrame:
    """Bounce days per month from ``prm_bureau_alert_enriched``."""
    require_columns(
        alerts,
        ["cif_id", "dt_of_return", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    amount = F.col("bounced_cheque_amount").cast("double")
    bounces = (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & F.col("dt_of_return").isNotNull()
            & (amount > 0)
        )
        .groupBy(
            string_key(alerts, "cif_id").alias("cif_id"),
            F.to_date("dt_of_return").alias("bounce_date"),
        )
        .agg(F.max(amount).alias("amount"))
    )
    return bounces.groupBy("cif_id", F.last_day("bounce_date").alias("month_end")).agg(
        F.count(F.lit(1)).alias("bounce_events"),
        F.max("amount").alias("max_bounce_amount"),
    )
`````

### FILE: `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py`
action: replace · base sha256 `0e2a8a5a0f02b3724772fe4d4c4860a33c600d3a7952235a2fcab3a28eaa471a` · base trailing newline: yes · new sha256 `a5582099b381154f73e2b6f888be9630850c759943226a6de0eeda9710e20b4f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: bureau salary per customer and month, the A1 income contract.

One row per ``(cif_id, month_end)`` from the DE's ``feat_bureau_salary_unified``, which
picks one monthly salary per customer across three AECB sources (``alert`` change events,
``salary_credit`` application-time history, ``bureau_salary`` bulk-pull aggregates spread
back over 12 months):

* ``bureau_salary`` - the unified ``monthly_salary`` (AED; 0 = no usable amount that
  month, e.g. a salary account closed);
* ``salary_source`` - the source that gave it (reporting only).

Months without a row have no bureau salary. How far a row carries is decided by the
consumer (A1 carries it one month, S14). To swap the bureau source, rebuild this table
from the new one; the A1 engine reads only this contract.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import require_columns


def build(unified: DataFrame) -> DataFrame:
    """``cif_id`` (string), ``month_end``, ``bureau_salary``, ``salary_source`` from
    ``feat_bureau_salary_unified`` (already one row per customer and month)."""
    require_columns(
        unified,
        ["cif_id", "salary_month_end", "monthly_salary", "salary_source"],
        "feat_bureau_salary_unified",
    )
    return unified.filter(
        F.col("cif_id").isNotNull() & F.col("monthly_salary").isNotNull()
    ).select(
        F.trim(F.col("cif_id").cast("string")).alias("cif_id"),
        F.last_day("salary_month_end").alias("month_end"),
        F.col("monthly_salary").cast("double").alias("bureau_salary"),
        "salary_source",
    )
`````

New:

`````python
"""Feature node: bureau salary per customer and month, the A1 income contract.

One row per ``(cif_id, month_end)`` from the DE's ``feat_bureau_salary_unified``, which
picks one monthly salary per customer across three AECB sources (``alert`` change
events, ``salary_credit`` application-time history, ``bureau_salary`` bulk-pull
aggregates spread back over 12 months):

* ``bureau_salary`` - the unified ``monthly_salary`` (AED; 0 = no usable amount that
  month, e.g. a salary account closed);
* ``salary_source`` - the source that gave it (reporting only).

Months without a row have no bureau salary. How far a row carries is decided by the
consumer (A1's ``BUREAU_CARRY_MONTHS``, S14). To swap the bureau source, rebuild this
table from the new one; the A1 engine reads only this contract.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import require_columns, string_key


def build(unified: DataFrame) -> DataFrame:
    """``cif_id`` (string), ``month_end``, ``bureau_salary``, ``salary_source`` from
    ``feat_bureau_salary_unified`` (already one row per customer and month)."""
    require_columns(
        unified,
        ["cif_id", "salary_month_end", "monthly_salary", "salary_source"],
        "feat_bureau_salary_unified",
    )
    return unified.filter(
        F.col("cif_id").isNotNull() & F.col("monthly_salary").isNotNull()
    ).select(
        string_key(unified, "cif_id").alias("cif_id"),
        F.last_day("salary_month_end").alias("month_end"),
        F.col("monthly_salary").cast("double").alias("bureau_salary"),
        "salary_source",
    )
`````

### FILE: `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py`
action: replace · base sha256 `979a803fb21087fd82602f4bd457878ed78318dfe470a6c1cdbd41cf21019e65` · base trailing newline: yes · new sha256 `2260aec4aeedf4fba767af62e0aa2eb8b4aaf049560e6de3cd534acec5e79887` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1 engine
can leave out the scored account itself. The WM asset sources are per customer, not per
account: their rows carry the fixed ids ``ASSET_IDS`` (they never equal a spine account).
Supplementary cards post to their contract and never appear as a product of their own; a
card that a newer card replaced is left out, so the scored card's predecessor is not
"another card". CASA balances are never a product here (they are A1's money held,
``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    months_back,
    require_columns,
    wm_month,
)

PRODUCT_TYPES = ("deposit", "investment", "wm", "card", "loan")
COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the month's
    last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series; a
    balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: a live contract (not replaced by a newer one) with a billing row in
    the month; current = billing level at most ``CARD_CURRENT_MAX_LEVEL``; the instalment
    is the month's minimum due."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    replaced = card_contracts.select(
        F.col("parent_contract_id").alias("contract_id")
    ).distinct()
    live = card_contracts.join(replaced, "contract_id", "left_anti")
    return card_month_end.join(
        live.select("cif_id", "contract_id"), "contract_id"
    ).select(
        "cif_id",
        "month_end",
        F.col("contract_id").cast("string").alias("product_account_id"),
        F.lit("card").alias("product_type"),
        _null("double").alias("balance_aed"),
        (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
        F.col("minimum_due").alias("instalment_aed"),
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days and
    not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the first of the last ``history_months`` months up to the persona
    start month on, for all customers (the persona scope is applied by the A1 engine's
    join on the observation base). The primaries are already bounded to that window by
    ``product_primary`` (same parameter).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = months_back(persona_start_date, history_months - 1)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

New:

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets
  under management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1
engine can leave out the scored account itself. The WM asset sources are per customer,
not per account: their rows carry the fixed ids ``ASSET_IDS`` (never a spine account).
Supplementary cards post to their contract and never appear as a product of their own; a
card that a newer card replaced is left out, so the scored card's predecessor is not
"another card". CASA balances are never a product here (they are A1's money held,
``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    history_floor,
    require_columns,
    wm_month,
)

COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
ASSET_TYPES = tuple(ASSET_IDS)
CREDIT_TYPES = ("card", "loan")
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the
    month's last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series;
    a balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: a live contract (not replaced by a newer one) with a billing row
    in the month; current = billing level at most ``CARD_CURRENT_MAX_LEVEL``; the
    instalment is the month's minimum due."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    replaced = card_contracts.select(
        F.col("parent_contract_id").alias("contract_id")
    ).distinct()
    live = card_contracts.join(replaced, "contract_id", "left_anti")
    return card_month_end.join(
        live.select("cif_id", "contract_id"), "contract_id"
    ).select(
        "cif_id",
        "month_end",
        F.col("contract_id").cast("string").alias("product_account_id"),
        F.lit("card").alias("product_type"),
        _null("double").alias("balance_aed"),
        (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
        F.col("minimum_due").alias("instalment_aed"),
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days
    and not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from ``history_floor(persona_start_date, history_months)`` on, for
    all customers (the A1 engine's join on the observation base applies the persona
    scope). The primaries are already bounded to that floor by ``product_primary`` (same
    parameters).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = history_floor(persona_start_date, history_months)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

### FILE: `src/enbd_collections/nodes/primary/products/prm_products.py`
action: replace · base sha256 `e5aca8dd53f80a371a6eb2f2607d5a433a93efa963a6ff4d58543e0baa07fd63` · base trailing newline: yes · new sha256 `420ce6096fa7ae422a8efbeded8f8857fb381d488249b480b940f4e720145cd8` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per ``(cif_id, contract_id)``: every Way4 card contract
  of a client, with ``parent_contract_id`` (the contract a newer one replaced; NULL for
  none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row in
  the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 = not
  overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off date.

All customers, from the first of the last ``history_months`` months up to the persona
start month on; values as in the source (which level or bucket is "current" is decided
by the consumers). The spine-scoped ``prm_contract`` / ``prm_balance`` hold only the
model's own accounts, so they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import months_back, require_columns

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _window(persona_start_date: str, history_months: int) -> tuple:
    """The first month kept and the ``edp_load_date`` bound that covers it."""
    floor = months_back(persona_start_date, history_months - 1)
    return floor, floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str) -> DataFrame:
    """``df`` with ``month_end`` = the month end of ``day``, keeping each ``key``'s latest
    ``day`` row per month."""
    month_end = F.last_day(day)
    latest = Window.partitionBy(key, month_end).orderBy(F.col(day).desc())
    return (
        df.withColumn("month_end", month_end)
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id`` of every card contract whose
    client is known (``ident_number`` is the CIF)."""
    require_columns(client, ["client_idt", "ident_number"], "raw_stg_client")
    require_columns(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", F.trim(F.col("ident_number").cast("string")).alias("cif_id")
    ).distinct()
    return (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_contract_id"),
        )
        .distinct()
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date").select(
        "contract_id", "month_end", "level"
    )


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot in
    the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the repo's
    own minimum-due derivation)."""
    require_columns(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return _latest_in_month(amounts, "contract_idt", "banking_date").select(
        F.col("contract_idt").alias("contract_id"),
        "month_end",
        F.col("minimum_due").cast("double").alias("minimum_due"),
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card contract
    with a billing row in the month."""
    floor, lo = _window(persona_start_date, history_months)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``, ``overdue_days``,
    ``instalment_due_aed`` and ``write_off_date`` of every monthly loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor, _ = _window(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        F.col("cust_num").cast("string").alias("cif_id"),
        F.trim(F.col("acct_num").cast("string")).alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
`````

New:

`````python
"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per ``(cif_id, contract_id)``: every Way4 card
  contract of a client, with ``parent_contract_id`` (the contract a newer one replaced;
  NULL for none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row
  in the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 =
  not overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off
  date.

All customers, from ``history_floor(persona_start_date, history_months)`` on; values as
in the source (which level or bucket is "current" is decided by the consumers). The
spine-scoped ``prm_contract`` / ``prm_balance`` hold only the model's own accounts, so
they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import (
    history_floor,
    require_columns,
    string_key,
)

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _load_bound(floor: datetime.date) -> datetime.date:
    """The ``edp_load_date`` bound that covers the month of ``floor`` (load lag)."""
    return floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str, value: str) -> DataFrame:
    """``key``, ``month_end`` (the month end of ``day``) and ``value`` of each ``key``'s
    latest ``day`` row per month; two rows on that day: the larger ``value``."""
    return (
        df.groupBy(key, F.last_day(day).alias("month_end"))
        .agg(F.max(F.struct(day, value)).alias("_latest"))
        .select(key, "month_end", F.col(f"_latest.{value}").alias(value))
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id`` of every card contract whose
    client is known (``ident_number`` is the CIF)."""
    require_columns(client, ["client_idt", "ident_number"], "raw_stg_client")
    require_columns(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", string_key(client, "ident_number").alias("cif_id")
    ).distinct()
    return (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_contract_id"),
        )
        .distinct()
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date", "level")


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot
    in the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the
    repo's own minimum-due derivation)."""
    require_columns(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return (
        _latest_in_month(amounts, "contract_idt", "banking_date", "minimum_due")
        .withColumnRenamed("contract_idt", "contract_id")
        .withColumn("minimum_due", F.col("minimum_due").cast("double"))
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card
    contract with a billing row in the month."""
    floor = history_floor(persona_start_date, history_months)
    lo = _load_bound(floor)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``,
    ``overdue_days``, ``instalment_due_aed`` and ``write_off_date`` of every monthly
    loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor = history_floor(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        string_key(loan_portfolio, "cust_num").alias("cif_id"),
        string_key(loan_portfolio, "acct_num").alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
`````

### FILE: `src/enbd_collections/nodes/utils/frames.py`
action: replace · base sha256 `e0391589906491e07ea5095b6d033ab084c232c98ec9ccde15ea02df81558195` · base trailing newline: yes · new sha256 `d67670696ea69f193df2c512a956e723e22c9fead60a70558200e86cc79d895f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Small helpers shared by the primary and feature nodes (CASA, products)."""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def require_columns(df: DataFrame, columns: list[str], source: str) -> None:
    """Raise ``ValueError`` naming ``source`` when ``df`` lacks any of ``columns``."""
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a WM ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def cif_column() -> Column:
    """``cif_id`` as a string (the persona join type)."""
    return F.col("cif_id").cast("string").alias("cif_id")
`````

New:

`````python
"""Small helpers shared by the primary and feature nodes and the persona axes."""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def history_floor(persona_start_date: str | date, months: int) -> date:
    """First day of the ``months``-month history that ends in the persona start month
    (that month included): the oldest month a source read keeps."""
    return months_back(persona_start_date, months - 1)


def require_columns(df: DataFrame, columns: list[str], source: str) -> None:
    """Raise ``ValueError`` naming ``source`` when ``df`` lacks any of ``columns``."""
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a WM ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def cif_column() -> Column:
    """``cif_id`` as a string (the persona join type)."""
    return F.col("cif_id").cast("string").alias("cif_id")


def string_key(df: DataFrame, col: str = "account_id") -> Column:
    """``col`` as a trimmed string join key. A double or decimal id is cast to ``long``
    first: cast straight to string it reads ``1.23456789E8`` and matches nothing."""
    key = F.col(col)
    if isinstance(df.schema[col].dataType, (T.DoubleType, T.FloatType, T.DecimalType)):
        key = key.cast("long")
    return F.trim(key.cast("string"))
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `1f41d063135c227607aff26b38bf1bf160e3b784bac8170a1647237866889d43` · base trailing newline: yes · new sha256 `dc52dc14e15627423000a537843797c09468a761576ac2fbebe3883f7410654e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import cc_spell as crx_cc_spell
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
    rl_spell_table as crx_rl_spell_table,
)
from enbd_collections.pipelines.crx_persona import rl_a4_spine as crx_rl_a4_spine
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_spell_table": crx_cc_spell.create_pipeline(),
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

New:

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import cc_spell as crx_cc_spell
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base
from enbd_collections.pipelines.crx_persona import b25_check  # TEMPORARY

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
    rl_spell_table as crx_rl_spell_table,
)
from enbd_collections.pipelines.crx_persona import rl_a4_spine as crx_rl_a4_spine
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_spell_table": crx_cc_spell.create_pipeline(),
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 25): removed by the cleanup
        "crx_cc_b25_check": b25_check.create_pipeline("cc"),
        "crx_rl_b25_check": b25_check.create_pipeline("rl"),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

### FILE: `src/enbd_collections/pipelines/bureau/salary_bounces.py`
action: replace · base sha256 `816fa665a06d0d1a8caa1fb88995cb3f1ad41ea53baf4655e743a2d0acc459b0` · base trailing newline: yes · new sha256 `65a5255da5aa755666e32dfa524aad1c7f2d5657c6a0654f2e33a185623e5778` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Bureau salary and bounce inputs of the persona axes (per model_id).

    feat_bureau_salary_unified ──► feat_cif_bureau_salary_monthly
    prm_bureau_alert_enriched ───► feat_cif_bureau_bounces_monthly

Needs the DE's ``feat_bureau_salary_unified`` (read-only here) and ``bureau_staging`` +
``bureau_primary`` (the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"unified": "feat_bureau_salary_unified"},
                outputs="feat_cif_bureau_salary_monthly",
                name="build_feat_cif_bureau_salary_monthly",
                tags=["bureau", "features"],
            ),
            node(
                func=feat_cif_bureau_bounces_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_bounces_monthly",
                name="build_feat_cif_bureau_bounces_monthly",
                tags=["bureau", "features"],
            ),
        ]
    )
`````

New:

`````python
"""Bureau salary and bounce inputs of the persona axes (per model_id).

    feat_bureau_salary_unified ──► feat_cif_bureau_salary_monthly
    prm_bureau_alert_enriched ───► feat_cif_bureau_bounces_monthly

Needs the DE's ``feat_bureau_salary_unified`` (read-only here) and ``bureau_staging`` +
``bureau_primary`` (the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The two monthly bureau features."""
    tags = ["bureau", "features"]
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"unified": "feat_bureau_salary_unified"},
                outputs="feat_cif_bureau_salary_monthly",
                name="build_feat_cif_bureau_salary_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_bureau_bounces_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_bounces_monthly",
                name="build_feat_cif_bureau_bounces_monthly",
                tags=tags,
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: replace · base sha256 `8f0711094e9ead483cbd7c8a9133fb94dde8ed7bbab55ea1600fb3669eb085fd` · base trailing newline: yes · new sha256 `00bf025511058d449342de7116390f04465bbf9838f425d841977c18f426532f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* windows are whole calendar months: the observation month (observation dates are month
  ends) and the months before it;
* point-in-time lookups read before the observation date and can be bounded in age
  (``pit_latest``), window aggregates read the last N months (``window_agg``);
* source partition floors follow from the earliest observation month
  (``lookback_floor``);
* each axis logs its state distribution for the latest observation month only
  (``log_latest_month``);
* DCORE events are read per scored account, through its agreements
  (``dcore_account_events``); each axis applies its own date window.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# The two segments; every per-segment setting in crx_persona is keyed by them.
SEG_60_180, SEG_180_PLUS = "60_180", "180_plus"

# The DPD segment each model_id scores; every segment-dependent rule keys on it.
MODEL_ID_SEGMENT = {
    "cc_60_180": SEG_60_180,
    "cc_180_plus": SEG_180_PLUS,
    "rl_60_180": SEG_60_180,
    "rl_180_plus": SEG_180_PLUS,
}

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 6}
# Failed call days in a row that make a customer gone dark: A2 Non-Reachable (D-A2-20),
# A3's no-pickup diagnostic (D-A3-19).
GONE_DARK_DAYS = {SEG_60_180: 3, SEG_180_PLUS: 6}


def segment(model_id: str) -> str:
    """``model_id``'s DPD segment: ``60_180`` or ``180_plus``."""
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    return MODEL_ID_SEGMENT[model_id]


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[segment(model_id)]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def string_key(df: DataFrame, col: str = "account_id") -> Column:
    """``col`` as a trimmed string join key. A double or decimal id is cast to ``long``
    first: cast straight to string it reads ``1.23456789E8`` and matches nothing."""
    key = F.col(col)
    if isinstance(df.schema[col].dataType, (T.DoubleType, T.FloatType, T.DecimalType)):
        key = key.cast("long")
    return F.trim(key.cast("string"))


def window_start(months: int, anchor: Column | None = None) -> Column:
    """First day of the last ``months`` calendar months, the month of ``anchor``
    (default ``observation_date``) included."""
    anchor = F.col("observation_date") if anchor is None else anchor
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def scoped(src: DataFrame, base: DataFrame, key: str) -> DataFrame:
    """``src`` rows whose ``key`` occurs in ``base``. Sources span the whole bank, the
    base one model's customers: the broadcast semi-join drops the rest before the
    shuffle of the join that follows."""
    return src.join(F.broadcast(base.select(key).distinct()), on=key, how="left_semi")


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_months: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_months`` keeps only rows in the anchor's last N calendar
    months (1 = its own month), so a stale record never stands in for a current one.
    Ties on the date are broken by the values (largest first, NULL last), so reruns
    agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    row_date, anchor_date = F.col("_d"), F.col("_anchor")
    cond = row_date <= anchor_date if inclusive else row_date < anchor_date
    if max_age_months is not None:
        cond = cond & (row_date >= window_start(max_age_months, anchor_date))
    latest = F.max(F.struct("_d", *value_cols))
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(
            scoped(
                src.select(key, F.col(date_col).alias("_d"), *value_cols), base, key
            ),
            on=key,
        )
        .filter(cond)
        .groupBy(*GRAIN)
        .agg(latest.alias("_latest"))
        .select(*GRAIN, *[F.col("_latest")[c].alias(c) for c in value_cols])
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    months: int,
    key: str = "cif_id",
    start: str | None = None,
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read. ``start`` names a
    base date column that bounds each row's window from below as well (A3, D-A3-2:
    the episode start); ``aggs`` may read it. Returns ``GRAIN + aggs`` for base rows
    with at least one row in the window.
    """
    obs = F.col("observation_date")
    lower = window_start(months)
    if start is not None:
        lower = F.greatest(lower, F.col(start))
    return (
        base.select(*GRAIN, key, *([start] if start is not None else []))
        .join(scoped(src, base, key), on=key)
        .filter((F.col(date_col) >= lower) & (F.col(date_col) <= obs))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, months: int) -> str:
    """ISO start of the earliest observation's ``months``-month window (the partition
    floor for a source read)."""
    first: date = base.agg(window_start(months, F.min("observation_date"))).first()[0]
    return first.isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(
    df: DataFrame,
    col: str,
    name: str,
    persona_end_date: str,
    *,
    latest_per_account: bool = False,
) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run. ``latest_per_account`` counts each
    account's latest row of that month once (cc_spine has billing dates, so a card can
    have two rows in a month; drop the option when cc_spine is month-end)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        latest = df.filter(F.trunc("observation_date", "month") == month)
        if latest_per_account:
            newest_first = Window.partitionBy("account_id").orderBy(
                F.col("observation_date").desc()
            )
            latest = latest.withColumn("_rn", F.row_number().over(newest_first)).filter(
                F.col("_rn") == 1
            )
        rows = latest.groupBy(col).count().orderBy(col).collect()
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%s: %s distribution not logged: %s", name, col, exc)
        return
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s, month of %s (n=%d)", name, col, persona_end_date, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str, crx_persona: dict) -> DataFrame:
    """The spine rows in the persona months — ``crx_persona.persona_start_date`` to
    ``persona_end_date``, whole months — with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    month = F.trunc("observation_date", "month")
    in_persona = month.between(
        F.trunc(F.lit(str(crx_persona["persona_start_date"])), "month"),
        F.trunc(F.lit(str(crx_persona["persona_end_date"])), "month"),
    )
    base = (
        spine.select(
            F.col(id_col).cast("string").alias("account_id"),
            F.col("observation_date").cast("date"),
            "cif_id",
        )
        .filter(in_persona)
        .dropDuplicates(list(GRAIN))
    )
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The CC observation base at month ends. Until ``cc_spine`` itself is month-end, each
    billing-date row moves to its month end; an account's rows in one month become one
    (the largest ``cif_id`` if they disagree). Remove the shift once the spine is month-end.
    """
    require_columns(cc_spine, ["contract_id", "observation_date", "cif_id"], "cc_spine")
    month_end = cc_spine.select(
        "contract_id",
        F.last_day(F.col("observation_date").cast("date")).alias("observation_date"),
        "cif_id",
    )
    collapsed = month_end.groupBy("contract_id", "observation_date").agg(
        F.max("cif_id").alias("cif_id")
    )
    return _obs_base(collapsed, "contract_id", crx_persona)


def build_rl_obs_base(rl_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The RL observation base (``rl_spine`` is already month-end)."""
    require_columns(rl_spine, ["account_id", "observation_date", "cif_id"], "rl_spine")
    return _obs_base(rl_spine, "account_id", crx_persona)


# ── DCORE ─────────────────────────────────────────────────────────────────────


def dcore_account_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """DCORE events on the agreements of the base's accounts: ``account_id``,
    ``day``, ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when
    missing). Shared by A2 (D-A2-8: all history, one agreement per account) and A3
    (D-A3-7: account level). Not dated by the observation: the caller joins its rows
    and window."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    return followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
`````

New:

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* windows are whole calendar months: the observation month (observation dates are month
  ends) and the months before it;
* point-in-time lookups read before the observation date and can be bounded in age
  (``pit_latest``), window aggregates read the last N months (``window_agg``);
* source partition floors follow from ``crx_persona.persona_start_date``, the first
  observation month (``nodes.utils.frames.history_floor``);
* each axis logs its state distribution for the latest observation month only
  (``log_latest_month``);
* DCORE events are read per scored account, through its agreements
  (``dcore_account_events``); each axis applies its own date window.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

# Re-exported: the axes import the key helper from here.
# pylint: disable-next=unused-import
from enbd_collections.nodes.utils.frames import string_key  # noqa: F401

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# The two segments; every per-segment setting in crx_persona is keyed by them.
SEG_60_180, SEG_180_PLUS = "60_180", "180_plus"

# The DPD segment each model_id scores; every segment-dependent rule keys on it.
MODEL_ID_SEGMENT = {
    "cc_60_180": SEG_60_180,
    "cc_180_plus": SEG_180_PLUS,
    "rl_60_180": SEG_60_180,
    "rl_180_plus": SEG_180_PLUS,
}

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 6}
# Failed call days in a row that make a customer gone dark: A2 Non-Reachable (D-A2-20),
# A3's no-pickup diagnostic (D-A3-19).
GONE_DARK_DAYS = {SEG_60_180: 3, SEG_180_PLUS: 6}


def segment(model_id: str) -> str:
    """``model_id``'s DPD segment: ``60_180`` or ``180_plus``."""
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    return MODEL_ID_SEGMENT[model_id]


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[segment(model_id)]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def window_start(months: int, anchor: Column | None = None) -> Column:
    """First day of the last ``months`` calendar months, the month of ``anchor``
    (default ``observation_date``) included."""
    anchor = F.col("observation_date") if anchor is None else anchor
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def scoped(src: DataFrame, base: DataFrame, key: str) -> DataFrame:
    """``src`` rows whose ``key`` occurs in ``base``. Sources span the whole bank, the
    base one model's customers: the broadcast semi-join drops the rest before the
    shuffle of the join that follows."""
    return src.join(F.broadcast(base.select(key).distinct()), on=key, how="left_semi")


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    max_age_months: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's observation date, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. ``inclusive``
    also accepts rows dated on it (same-day snapshots). ``max_age_months`` keeps only
    rows in the last N calendar months of the observation date (1 = its own month), so a
    stale record never stands in for a current one.
    Ties on the date are broken by the values (largest first, NULL last), so reruns
    agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    row_date, obs_date = F.col("_d"), F.col("observation_date")
    cond = row_date <= obs_date if inclusive else row_date < obs_date
    if max_age_months is not None:
        cond = cond & (row_date >= window_start(max_age_months))
    latest = F.max(F.struct("_d", *value_cols))
    return (
        base.select(*GRAIN, key)
        .join(
            scoped(
                src.select(key, F.col(date_col).alias("_d"), *value_cols), base, key
            ),
            on=key,
        )
        .filter(cond)
        .groupBy(*GRAIN)
        .agg(latest.alias("_latest"))
        .select(*GRAIN, *[F.col("_latest")[c].alias(c) for c in value_cols])
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    months: int,
    key: str = "cif_id",
    start: str | None = None,
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read. ``start`` names a
    base date column that bounds each row's window from below as well (A3, D-A3-2:
    the episode start); ``aggs`` may read it. Returns ``GRAIN + aggs`` for base rows
    with at least one row in the window.
    """
    obs = F.col("observation_date")
    lower = window_start(months)
    if start is not None:
        lower = F.greatest(lower, F.col(start))
    return (
        base.select(*GRAIN, key, *([start] if start is not None else []))
        .join(scoped(src, base, key), on=key)
        .filter((F.col(date_col) >= lower) & (F.col(date_col) <= obs))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(
    df: DataFrame,
    col: str,
    name: str,
    persona_end_date: str,
    *,
    latest_per_account: bool = False,
) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run. ``latest_per_account`` counts each
    account's latest row of that month once (cc_spine has billing dates, so a card can
    have two rows in a month; drop the option when cc_spine is month-end)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        latest = df.filter(F.trunc("observation_date", "month") == month)
        if latest_per_account:
            newest_first = Window.partitionBy("account_id").orderBy(
                F.col("observation_date").desc()
            )
            latest = latest.withColumn("_rn", F.row_number().over(newest_first)).filter(
                F.col("_rn") == 1
            )
        rows = latest.groupBy(col).count().orderBy(col).collect()
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%s: %s distribution not logged: %s", name, col, exc)
        return
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s, month of %s (n=%d)", name, col, persona_end_date, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str, crx_persona: dict) -> DataFrame:
    """The spine rows in the persona months — ``crx_persona.persona_start_date`` to
    ``persona_end_date``, whole months — with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    month = F.trunc("observation_date", "month")
    in_persona = month.between(
        F.trunc(F.lit(str(crx_persona["persona_start_date"])), "month"),
        F.trunc(F.lit(str(crx_persona["persona_end_date"])), "month"),
    )
    base = (
        spine.select(
            F.col(id_col).cast("string").alias("account_id"),
            F.col("observation_date").cast("date"),
            "cif_id",
        )
        .filter(in_persona)
        .dropDuplicates(list(GRAIN))
    )
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The CC observation base at month ends. While ``cc_spine`` is dated at billing
    dates, each row moves to its month end and an account's rows in one month become
    one (the largest ``cif_id`` if they disagree); on a month-end spine this changes
    nothing.
    """
    require_columns(cc_spine, ["contract_id", "observation_date", "cif_id"], "cc_spine")
    month_end = cc_spine.select(
        "contract_id",
        F.last_day(F.col("observation_date").cast("date")).alias("observation_date"),
        "cif_id",
    )
    collapsed = month_end.groupBy("contract_id", "observation_date").agg(
        F.max("cif_id").alias("cif_id")
    )
    return _obs_base(collapsed, "contract_id", crx_persona)


def build_rl_obs_base(rl_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The RL observation base (``rl_spine`` is already month-end)."""
    require_columns(rl_spine, ["account_id", "observation_date", "cif_id"], "rl_spine")
    return _obs_base(rl_spine, "account_id", crx_persona)


# ── DCORE ─────────────────────────────────────────────────────────────────────


def dcore_account_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """DCORE events on the agreements of the base's accounts: ``account_id``,
    ``day``, ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when
    missing). Shared by A2 (D-A2-8: all history, one agreement per account) and A3
    (D-A3-7: account level). Not dated by the observation: the caller joins its rows
    and window."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    scope = scoped(
        agreements.select("account_id", "agreement_id"), obs_base, "account_id"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    return followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `a9e284be1769f8bbaa3eee6b08bc8e87323df1a29ea53369160bd50db46e79ec` · base trailing newline: yes · new sha256 `0592e42bf6eec527d2b1c6b68988e70a1ae6a2f61a7d7ec975fd5a5a34573866` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks for independent evidence that the customer has
money — income, money coming in or held, money going out by choice, other products with us —
and failed payments, and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule is `specs/A1_ability_family_rule.md`
(income: `specs/A1_ability_spec.md` S1–S16); the code is
`signals.py` (evidence), `classify.py` (levels and state) and `pipeline.py` (nodes). CC wraps
it in `cc_a1_ability`, RL in `rl_a1_ability`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends**. Only the persona months are scored,
  `crx_persona.persona_start_date` to `persona_end_date`.
- **Layers:** the signal nodes read the observation base and monthly feature tables, one
  row per `(cif_id, month_end)` — never raw or staging tables:

  | Feature | Built from (pipeline) |
  |---|---|
  | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` (`casa_features`) |
  | `feat_cif_casa_balance_monthly` | WM CASA balance and flow tables (`casa_features`) |
  | `feat_cif_casa_flows_monthly` | `prm_casa_transactions` ← FTR + `wm_pri_labelled_transactions` (`casa_features`) |
  | `feat_cif_cross_product_monthly` | product holding, loan portfolio, card balances, WM assets (`product_features`) |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | the DE's `feat_bureau_salary_unified` (`bureau_salary_bounces`) |
  | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |

- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month. CC 180+: none.
  - RL: one EMI — `installment_due_amount` on the observation month's `int_loan_master`
    snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. F1 Income — Stable (2 points) / Weak (evidence) / None

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — one monthly AECB salary per CIF from the DE's unified table (alert
  change events first, then application-time salary history, then the bulk pull's
  aggregates spread back over 12 months). A row counts in its month and the next, never
  before it and no further (S14); a 0 row ends the carry.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`) and the prior window's internal salary (`internal_salary_prior`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`D_INC = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000 (no points, but evidence: Low rather
  than Unknown). **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Which transactions count (`feat_cif_casa_flows_monthly`)

Every CASA leg gets one class (`feat_cif_casa.flow_class`, on top of `transaction_lane`).
Only these count:

- **Money in:** transfers and remittances from others and clearing credits
  (`third_party_in`), cash deposits (`cash_in`), credits from the customer's own account at
  another bank (`own_in_external`, WM label).
- **Money out:** card spend, ATM, bills, transfers to others (`chosen_spend`), debits to the
  customer's own account at another bank (`own_out_external`, WM label).

Nothing else counts: salary-flagged credits (they are income), reversals, returned cheques /
DDS and the cheque presentments they undo (narrations `CHQ RTN` / `CHQ NO`), refunds,
transfers between the customer's accounts with us, fees and interest, paying their own card
or loan, and anything whose meaning is not established (the rest of `MISCELLANEOUS`). A
counted leg mirrored by a leg that does not count — the same amount (±1%) within 3 days —
is dropped (a bounce, a reversal, a sweep).

## 3. F2 Money in or held, F3 Money out — Strong (2) / Some (evidence) / None

- **F2 strong** = money in ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3 (3 of 6 at 180+),
  **or** the CASA balance ≥ max(AED 3,000, 1 × anchor) in 2 of m1–m3 and not more than 50%
  below the m4–m6 average (money held: the bank's sweep is manual, so a balance can survive
  it). **Some** = any month with ≥ AED 1,000 of money in. A balance below strong is not
  evidence.
- **F3 strong** = money out ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3. **Some** = any month
  ≥ AED 500.
- `a1_sweepable_balance_flag` = the balance is strong: money above the floor the bank could
  still sweep (a lead for collections; it changes nothing).

## 4. F4 Cross-product — Strong (2) / Some (evidence) / None

At the observation month end, the customer's other products with us (the scored account
left out): **strong** = deposits + investments + WM assets ≥ max(AED 10,000, 3 × anchor), or
another credit product (incl. other cards) that is current with an instalment / minimum due
≥ max(AED 1,000, 1 × anchor); **some** = any other current credit product or any asset.

## 5. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a bounced cheque reported by the bureau, one per CIF and return date
  (`DT_OF_RETURN`, S15).

## 6. The state

Only strong levels score (2 points each); weak / some are evidence.

| State | Rule |
|---|---|
| `high` | two or more strong families (4+ points) |
| `moderate` | one strong family |
| `low` | no strong family, but some evidence (income weak, money in / out some, cross-product some), or distress alone |
| `unknown` | no evidence in any family, no distress **and** no counted CASA leg in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA leg or positive balance in 12 months) or `dormant_casa` |

Distress moves a customer exactly one rung down (High → Moderate → Low). `a1_reason` names
the strongest family (or `distress`). `a1_eosb_flag` (a DCORE end-of-service result in the
window) is a diagnostic column and changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts as income.** Other regular credits count as money in;
  about a third of customers hold no CASA with us, so F2 / F3 cannot see them.
- **Money in / out rest on the class table.** A flow type counts only once its meaning is
  established; new transaction types land in `unplaced` until they are classified.
- **Bureau salary is mostly an event feed for now.** Most rows are alerts, which appear only
  when something changes, so no row means nothing is known, not that the salary stopped; the
  bulk pull covers about 1% of customers. GRR's feed of pulls every 2 months enters through
  the same table. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions`,
  the flows and the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

New:

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks for independent evidence that the customer has
money — income, money coming in or held, money going out by choice, other products with us —
and failed payments, and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule is `specs/A1_ability_family_rule.md`
(income: `specs/A1_ability_spec.md` S1–S16); the code is
`signals.py` (evidence), `classify.py` (levels and state) and `pipeline.py` (nodes). CC wraps
it in `cc_a1_ability`, RL in `rl_a1_ability`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends**. Only the persona months are scored,
  `crx_persona.persona_start_date` to `persona_end_date`.
- **Layers:** the signal nodes read the observation base and monthly feature tables, one
  row per `(cif_id, month_end)` — never raw or staging tables:

  | Feature | Built from (pipeline) |
  |---|---|
  | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` (`casa_features`) |
  | `feat_cif_casa_balance_monthly` | WM CASA balance and flow tables (`casa_features`) |
  | `feat_cif_casa_flows_monthly` | `prm_casa_transactions` ← FTR + `wm_pri_labelled_transactions` (`casa_features`) |
  | `feat_cif_cross_product_monthly` | product holding, loan portfolio, card balances, WM assets (`product_features`) |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | the DE's `feat_bureau_salary_unified` (`bureau_salary_bounces`) |
  | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |

- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month. CC 180+: none.
  - RL: one EMI — `installment_due_amount` on the observation month's `int_loan_master`
    snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. F1 Income — Stable (2 points) / Weak (evidence) / None

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — one monthly AECB salary per CIF from the DE's unified table (alert
  change events first, then application-time salary history, then the bulk pull's
  aggregates spread back over 12 months). A row counts in its month and the next, never
  before it and no further (S14); a 0 row ends the carry.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`) and the
prior window's internal salary (`internal_salary_prior`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = the strong amount, max(AED 3,000, 2 × anchor) (`STRONG_FLOOR`,
  `STRONG_ANCHOR_MULT`), the same for income, money in, money out, the balance and assets.
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`INCOME_MAX_FALL = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000 (no points, but evidence: Low rather
  than Unknown). **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Which transactions count (`feat_cif_casa_flows_monthly`)

Every CASA leg gets one class (`feat_cif_casa.flow_class`, on top of `transaction_lane`).
Only these count:

- **Money in:** transfers and remittances from others and clearing credits
  (`third_party_in`), cash deposits (`cash_in`), credits from the customer's own account at
  another bank (`own_in_external`, WM label).
- **Money out:** card spend, ATM, bills, transfers to others (`chosen_spend`), debits to the
  customer's own account at another bank (`own_out_external`, WM label).

Nothing else counts: salary-flagged credits (they are income), reversals, returned cheques /
DDS and the cheque presentments they undo (narrations `CHQ RTN` / `CHQ NO`), refunds,
transfers between the customer's accounts with us, fees and interest, paying their own card
or loan, and anything whose meaning is not established (the rest of `MISCELLANEOUS`). A
counted leg mirrored by a leg that does not count — the same amount (±1%) within 3 days —
is dropped (a bounce, a reversal, a sweep).

## 3. F2 Money in or held, F3 Money out — Strong (2) / Some (evidence) / None

- **F2 strong** = money in ≥ max(AED 3,000, 2 × anchor) in 2 of m1–m3 (3 of 6 at 180+),
  **or** the CASA balance ≥ max(AED 3,000, 2 × anchor) in 2 of m1–m3 and not more than 50%
  below the m4–m6 average (money held: the bank's sweep is manual, so a balance can survive
  it). **Some** = any month with ≥ AED 1,000 of money in (`FLOW_SOME`). A balance below
  strong is not evidence.
- **F3 strong** = money out ≥ max(AED 3,000, 2 × anchor) in 2 of m1–m3. **Some** = any month
  ≥ AED 1,000 (`FLOW_SOME`).
- `a1_sweepable_balance_flag` = the balance is strong: money above the floor the bank could
  still sweep (a lead for collections; it changes nothing).

## 4. F4 Cross-product — Strong (2) / Some (evidence) / None

At the observation month end, the customer's other products with us (the scored account
left out): **strong** = deposits + investments + WM assets ≥ max(AED 3,000, 2 × anchor), or
another credit product (incl. other cards) that is current with an instalment / minimum due
≥ max(AED 1,000, 1 × anchor); **some** = any other current credit product or any asset.

## 5. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a bounced cheque reported by the bureau, one per CIF and return date
  (`DT_OF_RETURN`, S15).

## 6. The state

Only strong levels score (2 points each); weak / some are evidence.

| State | Rule |
|---|---|
| `high` | two or more strong families (4+ points) |
| `moderate` | one strong family |
| `low` | no strong family, but some evidence (income weak, money in / out some, cross-product some), or distress alone |
| `unknown` | no evidence in any family, no distress **and** no counted CASA leg in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA leg or positive balance in 12 months) or `dormant_casa` |

Distress moves a customer exactly one rung down (High → Moderate → Low). `a1_reason` names
the strongest family (or `distress`). `a1_eosb_flag` (a DCORE end-of-service result in the
window) is a diagnostic column and changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts as income.** Other regular credits count as money in;
  about a third of customers hold no CASA with us, so F2 / F3 cannot see them.
- **Money in / out rest on the class table.** A flow type counts only once its meaning is
  established; new transaction types land in `unplaced` until they are classified.
- **Bureau salary is mostly an event feed for now.** Most rows are alerts, which appear only
  when something changes, so no row means nothing is known, not that the salary stopped; the
  bulk pull covers about 1% of customers. GRR's feed of pulls every 2 months enters
  through the same table. A stop shows only as a closure, a lower amount or the end of
  an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions`,
  the flows and the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: replace · base sha256 `e8b88e8d6b0f728b3e1f8741682b4a63b9853f2dceabaa95c4e5911457a1b05c` · base trailing newline: yes · new sha256 `011943f6c65ca6a1c667291766fe924fb9baa2b1ec960e380de8f73b471a0df0` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)

__all__ = [
    "build_a1_ability",
    "build_casa_signals",
    "build_cross_product_signals",
    "build_distress_signals",
    "build_eosb_signals",
    "build_income_signals",
]
`````

New:

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

# ruff: noqa: F401

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: replace · base sha256 `0518f4504399eddb1605d593b674029c3d925e5d03b1eabf5204721ec191d38e` · base trailing newline: yes · new sha256 `bc47badb12022536a01799f44a120883404e802b6158fed302761d1e6d90080f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability state — evidence families.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md``.

    F1 income        stable 2 / weak 0 (evidence) / none
    F2 money in/held strong 2 / some 0 (evidence) / none   (inflow, or a CASA balance)
    F3 money out     strong 2 / some 0 (evidence) / none
    F4 cross-product strong 2 / some 0 (evidence) / none
    = points         4+ high (two strong families), 2 moderate, else low
  distress (cheque / DDS return, new bureau bounce) lowers the state one rung;
  no evidence in any family and no counted CASA leg in the window → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (family rule §2; income: spec S2–S12): starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
MIN_MONTHS = {3: 2, 6: 3}  # months of the window a flow / balance must reach its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
INCOME_FLOOR = 3000.0  # S2: salary floor (internal and bureau), AED
INCOME_ANCHOR_MULT = 2.0  # S2: income must also cover this multiple of the anchor
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
FLOW_FLOOR = 1000.0  # F2 / F3 strong: a month's flow reaches max(floor, mult x anchor)
FLOW_ANCHOR_MULT = 1.0
MONEY_IN_SOME = 1000.0  # F2 some: any month with this much money in
MONEY_OUT_SOME = 500.0  # F3 some: any month with this much money out
BALANCE_FLOOR = 3000.0  # F2 balance strong (today's liquidity "adequate" on balances)
BALANCE_ANCHOR_MULT = 1.0
BALANCE_MAX_FALL = 0.50
ASSET_FLOOR = 10000.0  # F4 strong: assets reach max(floor, mult x anchor) …
ASSET_ANCHOR_MULT = 3.0
INSTALMENT_FLOOR = 1000.0  # … or a current credit product's instalment reaches
INSTALMENT_ANCHOR_MULT = 1.0  # max(floor, mult x anchor)
MIN_EVIDENCE_AMT = 1000.0  # smallest salary that counts as evidence (income weak)
INCOME_POINTS = {"stable": 2}  # weak is evidence (Low), not points
FAMILY_POINTS = {"strong": 2}  # some is evidence (Low), not points
HIGH_FROM, MODERATE_FROM = 4, 2  # two strong families / one

DISPLAY_NAMES = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "unknown": "Unknown",
}


def _window(w: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Month indices of the window (m1–mW) and of the prior window (m(W+1)–m(2W))."""
    return tuple(range(1, w + 1)), tuple(range(w + 1, 2 * w + 1))


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(INCOME_FLOOR), INCOME_ANCHOR_MULT * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _strong_months(prefix: str, floor: Column, w: int) -> Column:
    """At least ``MIN_MONTHS[w]`` months of the window reach ``floor``."""
    return _count_at_least(_months(prefix, _window(w)[0]), floor) >= MIN_MONTHS[w]


def balance_strong(anchor: Column, w: int) -> Column:
    """The CASA balance holds max(floor, anchor) in ``MIN_MONTHS`` months of the window
    and is not more than ``BALANCE_MAX_FALL`` below the prior window (money held)."""
    floor = F.greatest(F.lit(BALANCE_FLOOR), BALANCE_ANCHOR_MULT * anchor)
    return _strong_months("casa", floor, w) & _not_weakening(
        "casa", BALANCE_MAX_FALL, missing_is_zero=False, w=w
    )


def _flow_level(prefix: str, some_floor: float, anchor: Column, w: int) -> Column:
    """strong / some / none / NULL (no flow in the window) of a monthly flow."""
    last = _months(prefix, _window(w)[0])
    floor = F.greatest(F.lit(FLOW_FLOOR), FLOW_ANCHOR_MULT * anchor)
    has_data = F.greatest(*[c.isNotNull() for c in last])
    return (
        F.when(_strong_months(prefix, floor, w), "strong")
        .when(_count_at_least(last, F.lit(some_floor)) > 0, "some")
        .when(has_data, "none")
    )


def money_in_level(anchor: Column, w: int) -> Column:
    """F2: strong when money in or the balance held is strong; some on money in only (a
    balance below strong is not evidence)."""
    inflow = _flow_level("in", MONEY_IN_SOME, anchor, w)
    return F.when(balance_strong(anchor, w), "strong").otherwise(inflow)


def money_out_level(anchor: Column, w: int) -> Column:
    """F3: chosen spend and transfers to the customer's own accounts elsewhere."""
    return _flow_level("out", MONEY_OUT_SOME, anchor, w)


def cross_product_level(anchor: Column, w: int) -> Column:  # pylint: disable=W0613
    """F4 at the observation month end: strong on assets of max(floor, 3 x anchor) or a
    current credit product whose instalment reaches max(floor, anchor); some on any other
    current credit product or any asset."""
    assets = F.coalesce(F.col("xp_assets_aed"), F.lit(0.0))
    instalment = F.coalesce(F.col("xp_instalment_max"), F.lit(0.0))
    strong = (assets >= F.greatest(F.lit(ASSET_FLOOR), ASSET_ANCHOR_MULT * anchor)) | (
        (F.col("xp_current") == 1)
        & (
            instalment
            >= F.greatest(F.lit(INSTALMENT_FLOOR), INSTALMENT_ANCHOR_MULT * anchor)
        )
    )
    some = (F.col("xp_current") == 1) | (F.col("xp_holding") == 1)
    return F.when(strong, "strong").when(some, "some").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (money_in_level, Dimension("money_in", "a1_money_in_level", FAMILY_POINTS)),
    (money_out_level, Dimension("money_out", "a1_money_out_level", FAMILY_POINTS)),
    (
        cross_product_level,
        Dimension("cross_product", "a1_cross_product_level", FAMILY_POINTS),
    ),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={s: s for s in ("high", "moderate", "low", "unknown")},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def build_a1_ability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Families and points: family rule §2–§4; distress lowers the state one rung (S9).

    ``signals`` (income, CASA, cross-product, distress, EOSB: ``GRAIN`` + columns) and
    ``anchor``
    (``GRAIN + liquidity_anchor_amt``, product builder) are left-joined in that order.
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``; ``a1_reason`` is the
    strongest family (or ``distress``). Diagnostics, which change nothing:
    ``a1_sweepable_balance_flag`` (the CASA balance is strong: money above the floor the
    bank could still sweep), ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the
    prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    internal_w = _shows_evidence("internal_salary_w")
    bureau_w = _shows_evidence("bureau_salary_w")
    internal_prior = _shows_evidence("internal_salary_prior")
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_reason",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        balance_strong(amt, w).cast("int").alias("a1_sweepable_balance_flag"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        F.when(internal_w & bureau_w, "both")
        .when(internal_w, "internal")
        .when(bureau_w, "bureau")
        .otherwise("none")
        .alias("a1_income_source"),
        (internal_prior & ~internal_w).cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

New:

`````python
"""A1 ability state — evidence families.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md``.

    F1 income        stable 2 / weak 0 (evidence) / none
    F2 money in/held strong 2 / some 0 (evidence) / none   (inflow, or a CASA balance)
    F3 money out     strong 2 / some 0 (evidence) / none
    F4 cross-product strong 2 / some 0 (evidence) / none
    = points         4+ high (two strong families), 2 moderate, else low
  distress (cheque / DDS return, new bureau bounce) lowers the state one rung;
  no evidence in any family and no counted CASA leg in the window → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (family rule §2; income: spec S2–S12): starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
MIN_MONTHS = {3: 2, 6: 3}  # months of the window a flow / balance must be strong
# S12: stable income = the window's salary reaches this many strong amounts
STABLE_INCOME_FLOORS = {3: 2, 6: 3}
# Income, money in, money out, the balance and assets are strong from one amount:
# max(floor, mult x anchor) (family rule §2).
STRONG_FLOOR = 3000.0  # AED
STRONG_ANCHOR_MULT = 2.0
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
FLOW_SOME = 1000.0  # F2 / F3 some: any month with this much money in / out
BALANCE_MAX_FALL = 0.50  # F2 balance strong: at most this share below the prior window
INSTALMENT_FLOOR = 1000.0  # F4 strong: a current credit product's instalment reaches
INSTALMENT_ANCHOR_MULT = 1.0  # max(floor, mult x anchor) (family rule §2)
MIN_EVIDENCE_AMT = 1000.0  # smallest salary that counts as evidence (income weak)
INCOME_POINTS = {"stable": 2}  # weak is evidence (Low), not points
FAMILY_POINTS = {"strong": 2}  # some is evidence (Low), not points
HIGH_FROM, MODERATE_FROM = 4, 2  # two strong families / one

DISPLAY_NAMES = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "unknown": "Unknown",
}


def _window(w: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Month indices of the window (m1–mW) and of the prior window (m(W+1)–m(2W))."""
    return tuple(range(1, w + 1)), tuple(range(w + 1, 2 * w + 1))


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    """The ``{prefix}_m{i}`` columns of month indices ``months``."""
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    """The number of ``cols`` reaching ``floor`` (NULL counts as 0)."""
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def _strong_amount(anchor: Column) -> Column:
    """The amount a family is strong from: max(``STRONG_FLOOR``, ``STRONG_ANCHOR_MULT``
    x anchor); the floor alone without an anchor."""
    return F.greatest(F.lit(STRONG_FLOOR), STRONG_ANCHOR_MULT * anchor)


def _instalment_amount(anchor: Column) -> Column:
    """The instalment another current credit product makes F4 strong from:
    max(``INSTALMENT_FLOOR``, ``INSTALMENT_ANCHOR_MULT`` x anchor)."""
    return F.greatest(F.lit(INSTALMENT_FLOOR), INSTALMENT_ANCHOR_MULT * anchor)


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    strong = _strong_amount(anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * strong) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _strong_months(prefix: str, anchor: Column, w: int) -> Column:
    """At least ``MIN_MONTHS[w]`` months of the window reach the strong amount."""
    last = _months(prefix, _window(w)[0])
    return _count_at_least(last, _strong_amount(anchor)) >= MIN_MONTHS[w]


def balance_strong(anchor: Column, w: int) -> Column:
    """The CASA balance holds the strong amount in ``MIN_MONTHS`` months of the window
    and is not more than ``BALANCE_MAX_FALL`` below the prior window (money held)."""
    return _strong_months("casa", anchor, w) & _not_weakening(
        "casa", BALANCE_MAX_FALL, missing_is_zero=False, w=w
    )


def _balance_strong_now(anchor: Column) -> Column:
    """The observation month's CASA balance (``casa_m1``; NULL counts as 0) reaches the
    strong amount."""
    return F.coalesce(F.col("casa_m1"), F.lit(0.0)) >= _strong_amount(anchor)


def _flow_level(prefix: str, anchor: Column, w: int) -> Column:
    """strong / some / none / NULL (no flow in the window) of a monthly flow."""
    last = _months(prefix, _window(w)[0])
    has_data = F.greatest(*[c.isNotNull() for c in last])
    return (
        F.when(_strong_months(prefix, anchor, w), "strong")
        .when(_count_at_least(last, F.lit(FLOW_SOME)) > 0, "some")
        .when(has_data, "none")
    )


def money_in_level(anchor: Column, w: int) -> Column:
    """F2: strong when money in or the balance held is strong; some on money in only (a
    balance below strong is not evidence)."""
    inflow = _flow_level("in", anchor, w)
    return F.when(balance_strong(anchor, w), "strong").otherwise(inflow)


def money_out_level(anchor: Column, w: int) -> Column:
    """F3: chosen spend and transfers to the customer's own accounts elsewhere."""
    return _flow_level("out", anchor, w)


def cross_product_level(anchor: Column, _w: int) -> Column:
    """F4 at the observation month end: strong on assets of the strong amount or a
    current credit product whose instalment reaches ``_instalment_amount``; some on any
    other current credit product or any asset."""
    assets = F.coalesce(F.col("xp_assets_aed"), F.lit(0.0))
    instalment = F.coalesce(F.col("xp_instalment_max"), F.lit(0.0))
    strong = (assets >= _strong_amount(anchor)) | (
        (F.col("xp_current") == 1) & (instalment >= _instalment_amount(anchor))
    )
    some = (F.col("xp_current") == 1) | (F.col("xp_holding") == 1)
    return F.when(strong, "strong").when(some, "some").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (money_in_level, Dimension("money_in", "a1_money_in_level", FAMILY_POINTS)),
    (money_out_level, Dimension("money_out", "a1_money_out_level", FAMILY_POINTS)),
    (
        cross_product_level,
        Dimension("cross_product", "a1_cross_product_level", FAMILY_POINTS),
    ),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={state: state for state in DISPLAY_NAMES},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def _income_source() -> Column:
    """Who shows ``MIN_EVIDENCE_AMT`` or more in the window: both, internal, bureau or
    none."""
    internal = _shows_evidence("internal_salary_w")
    bureau = _shows_evidence("bureau_salary_w")
    return (
        F.when(internal & bureau, "both")
        .when(internal, "internal")
        .when(bureau, "bureau")
        .otherwise("none")
    )


def _salary_stopped() -> Column:
    """Internal salary in the prior window and none in the window."""
    return _shows_evidence("internal_salary_prior") & ~_shows_evidence(
        "internal_salary_w"
    )


def build_a1_ability(
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Families and points: family rule §2–§4; distress lowers the state one rung (S9).

    ``signals`` (income, CASA, cross-product, distress, EOSB: ``GRAIN`` + columns) and
    ``anchor`` (``GRAIN + liquidity_anchor_amt``, from the product wrapper) are
    left-joined in that order. ``a1_unknown_reason`` says why a row is unknown:
    ``no_casa`` (no CASA leg or positive balance with us in 12 months) or
    ``dormant_casa``; ``a1_reason`` is the strongest family (or ``distress``).
    Diagnostics, which change nothing: ``a1_sweepable_balance_flag`` (the observation
    month's CASA balance reaches the strong amount: money the bank could still sweep),
    ``a1_eosb_flag`` (a DCORE end-of-service result in the window), ``a1_income_source``
    (who shows AED 1,000 or more in the window: ``internal``, ``bureau``, ``both`` or
    ``none``),
    ``a1_salary_stopped`` (internal salary in the prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_reason",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        _balance_strong_now(amt).cast("int").alias("a1_sweepable_balance_flag"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        _income_source().alias("a1_income_source"),
        _salary_stopped().cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: replace · base sha256 `2b068c6ce426211319022b7a88fe4273964e1d8b8e9b0e142279d69ff05bdb1e` · base trailing newline: yes · new sha256 `3ee695c55f310ef0c82ad9cbf4e647a60b78e499549cbfbb33d6761b9b9dae0b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly
                      ├─ CASA signals ──────┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_casa_flows_monthly
                      ├─ cross-product ─────┤   feat_cif_cross_product_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``product_features``, ``bureau_salary_bounces`` and ``location_features``
(``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_casa_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "casa_flows": "feat_cif_casa_flows_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_casa_signals",
                name=f"build_{prefix}_casa_signals",
                tags=TAGS,
            ),
            node(
                func=build_cross_product_signals,
                inputs={
                    "obs_base": obs,
                    "products": "feat_cif_cross_product_monthly",
                },
                outputs=f"{prefix}_cross_product_signals",
                name=f"build_{prefix}_cross_product_signals",
                tags=TAGS,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": obs,
                    "returns": "feat_cif_returns_monthly",
                    "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_distress_signals",
                name=f"build_{prefix}_distress_signals",
                tags=TAGS,
            ),
            node(
                func=build_eosb_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_eosb_signals",
                name=f"build_{prefix}_eosb_signals",
                tags=TAGS,
            ),
            anchor,
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_signals",
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_ability",
                tags=TAGS,
            ),
        ],
    )
`````

New:

`````python
"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ──┐  feat_cif_internal_salary_monthly,
                      │                   │  feat_cif_bureau_salary_monthly
                      ├─ CASA signals ────┤  feat_cif_casa_balance_monthly,
                      │                   │  feat_cif_casa_flows_monthly
                      ├─ cross-product ───┤  feat_cif_cross_product_monthly
                      ├─ distress signals ┼─► crx_<p>_a1_ability
                      │                   │  feat_cif_returns_monthly,
                      │                   │  feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ────┤  dcore_prm_followup_outcomes,
                      │                   │  prm_dcore_account_agreements
                      └─ liquidity anchor ┘  (wrapper node: prm_balance or
                                              int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``product_features``, ``bureau_salary_bounces`` and ``location_features``
(``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_casa_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "casa_flows": "feat_cif_casa_flows_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_casa_signals",
                name=f"build_{prefix}_casa_signals",
                tags=TAGS,
            ),
            node(
                func=build_cross_product_signals,
                inputs={
                    "obs_base": obs,
                    "products": "feat_cif_cross_product_monthly",
                },
                outputs=f"{prefix}_cross_product_signals",
                name=f"build_{prefix}_cross_product_signals",
                tags=TAGS,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": obs,
                    "returns": "feat_cif_returns_monthly",
                    "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_distress_signals",
                name=f"build_{prefix}_distress_signals",
                tags=TAGS,
            ),
            node(
                func=build_eosb_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_eosb_signals",
                name=f"build_{prefix}_eosb_signals",
                tags=TAGS,
            ),
            anchor,
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_signals",
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_ability",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `990812ce5f0f7c5a2671b823bba73ea54de2e444eed3eac26ae3b0eb3f68e6d6` · base trailing newline: yes · new sha256 `8fdd80a7dd1fb5e52d1de5539661c421880bc189bf7c514138af629c8237e0e1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a bureau row counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month, whether
             any counted leg falls in the window (the Unknown gate) and whether the
             customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
    window_start,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each row's month, and the month
    after it unless that month has its own row (never before a row; pulls every 2 months
    make a continuous series). A row of 0 ends the carry.
    """
    none = F.lit(None).cast("double")
    own = bureau.select("cif_id", "month_end", "bureau_salary", none.alias("_carried"))
    carried = bureau.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        none.alias("bureau_salary"),
        F.col("bureau_salary").alias("_carried"),
    )
    return (
        own.unionByName(carried)
        .groupBy("cif_id", "month_end")
        .agg(
            F.coalesce(F.max("bureau_salary"), F.max("_carried")).alias("bureau_salary")
        )
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` / ``money_out``
    (AED of the counted classes; NULL on a balance row), ``balance`` (NULL on a flow row),
    ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money in),
    ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active`` (a
    counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code accounts
    of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    # The obs base starts in the persona start month: no window reaches older rows.
    first = F.lit(str(crx_persona["persona_start_date"])).cast("date")
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= window_start(CASA_HELD_MONTHS, first)
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account itself left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin("deposit", "investment", "wm")
    current_credit = F.col("product_type").isin("card", "loan") & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    rows = (
        obs.join(
            products.select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.col("month_end").alias("observation_date"),
                F.col("product_account_id").cast("string").alias("_acct"),
                "product_type",
                F.col("balance_aed").cast("double").alias("_bal"),
                "is_current",
                F.col("instalment_aed").cast("double").alias("_inst"),
            ),
            on=["cif_id", "observation_date"],
        )
        .filter(F.col("_acct") != F.col("account_id").cast("string"))
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a bureau row counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month,
             whether any counted leg falls in the window (the Unknown gate) and whether
             the customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    ASSET_TYPES,
    CREDIT_TYPES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)
from enbd_collections.nodes.utils.frames import cif_column, history_floor

from .._common import (
    GRAIN,
    left_join_all,
    require_columns,
    scoped,
    string_key,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"
# S14: a bureau salary also counts in the next N months that have no row of their own.
BUREAU_CARRY_MONTHS = 1


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", string_key(obs_base, "cif_id")
    )


def persona_floor(crx_persona: dict, months: int) -> str:
    """ISO first day of the earliest observation's ``months``-month window: the obs base
    starts in the persona start month, so no window reaches older source rows."""
    return history_floor(crx_persona["persona_start_date"], months).isoformat()


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months``
    months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _with_carry(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: the month's own row, else the
    newest row of the ``BUREAU_CARRY_MONTHS`` months before it (never before a row;
    pulls every 2 months make a continuous series). A row of 0 ends the carry.
    """
    ages = range(BUREAU_CARRY_MONTHS + 1)  # 0: the row's own month
    rows = reduce(
        DataFrame.unionByName,
        [
            bureau.select(
                "cif_id",
                F.last_day(F.add_months("month_end", age)).alias("month_end"),
                F.lit(age).alias("_age"),
                "bureau_salary",
            )
            for age in ages
        ],
    )
    newest = [F.max(F.when(F.col("_age") == a, F.col("bureau_salary"))) for a in ages]
    # the newest non-NULL amount wins: a 0 row is a value, so it hides the older rows
    return rows.groupBy("cif_id", "month_end").agg(
        F.coalesce(*newest).alias("bureau_salary")
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried ``BUREAU_CARRY_MONTHS`` months
    forward); NULL: no salary that month. Also the largest month per source:
    ``internal_salary_w`` / ``bureau_salary_w`` in the window, ``internal_salary_prior``
    in the prior window.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    sources = internal.unionByName(
        _with_carry(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` /
    ``money_out`` (AED of the counted classes; NULL on a balance row), ``balance`` (NULL
    on a flow row), ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a
    positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money
    in), ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active``
    (a counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code
    accounts of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= F.lit(persona_floor(crx_persona, CASA_HELD_MONTHS))
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account itself left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin(*ASSET_TYPES)
    current_credit = F.col("product_type").isin(*CREDIT_TYPES) & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    mine = scoped(
        products.select(
            cif_column(),
            F.col("month_end").alias("observation_date"),
            string_key(products, "product_account_id").alias("_acct"),
            "product_type",
            F.col("balance_aed").cast("double").alias("_bal"),
            "is_current",
            F.col("instalment_aed").cast("double").alias("_inst"),
        ),
        obs,
        "cif_id",
    )
    joined = obs.join(mine, on=["cif_id", "observation_date"])
    rows = (
        joined.filter(F.col("_acct") != string_key(joined))
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after "
            "changing crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                cif_column(),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, w)
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    mine = scoped(
        agreements.select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            cif_column(),
        ).distinct(),
        obs,
        "cif_id",
    )
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(F.broadcast(mine), on="agreement_id")
        .filter(F.col("day") >= F.lit(persona_floor(crx_persona, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py`
action: replace · base sha256 `5e5b483650ed26f7aa492d416909054d34430919283db04298db2b6da507a891` · base trailing newline: yes · new sha256 `56261ee631a60ea4cb948a70e63cfd9aae53ab4ff89b30def3d78170ffc437a9` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 payment credibility engine shared by the CC and RL credibility pipelines."""

from .classify import build_a3_credibility
from .pipeline import create_a3_pipeline
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import (
    build_a3_episode,
    build_cycle_ledger,
    build_instalments,
    build_promise_events,
)
`````

New:

`````python
"""A3 payment credibility engine shared by the CC and RL credibility pipelines."""

# ruff: noqa: F401

from .classify import build_a3_credibility
from .pipeline import create_a3_pipeline
from .promises import build_promise_events
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import build_a3_episode, build_cycle_ledger, build_instalments
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py`
action: replace · base sha256 `85a6cd96c1d6aa2bec1af0007dc690b6652bf32aa7be2f6cce08d581ac673f7d` · base trailing newline: yes · new sha256 `6d8861e832a286fba567eefc8776f0197bbd28b13653d4888504b36a17d54bfb` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD, promise_deadline

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    model_id: str,
    persona_end_date: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off. Unknown:
    no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode with no
    evidence scores 0 points and is Low.
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn(
        "a3_promise_deadline", F.lit(deadline or promise_deadline(product, model_id))
    )
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", "A3 credibility", persona_end_date)
    return out
`````

New:

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD, promise_deadline

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_n",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    model_id: str,
    persona_end_date: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27, -33).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off.
    Unknown: no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode
    with no evidence scores 0 points and is Low.
    """
    df = episode
    for part in (commitments, dlq_payments, pre_dlq, contacts):
        df = df.join(part, on=list(GRAIN), how="left")
    df = df.withColumn(
        "a3_promise_deadline", F.lit(promise_deadline(product, model_id, deadline))
    )
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", f"a3_credibility [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py`
action: replace · base sha256 `8ce15d77727b043fe0e90a9eb5417572a64f17033b3b65aedc24bab79b1e03fb` · base trailing newline: yes · new sha256 `c1516bc2c8039ccb628e2885be0ac97a4701779e86d735ce525376af4a9447d8` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS, segment
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
FOLLOWUP_RUN_DAYS = 7  # follow-up promises less than 8 days apart are one event
MATCH_DAYS = 7  # a follow-up promise within 7 days of a DCORE plan is that plan
# The deadline a promise is judged by (GRR, handoff 64), whatever date was promised: at
# 60-180 a card promise by the next statement after the promise day, however close; a
# loan promise, and every promise at 180+, by the end of the promise month. The
# alternatives are 30 days from the promise ("30_days"; RL "30_days_month_end") and
# bundle 20's RL rule, the end of the next month ("next_month_end").
DEADLINES = (
    "next_statement",
    "month_end",
    "next_month_end",
    "30_days",
    "30_days_month_end",
)
PROMISE_DEADLINE = {
    SEG_60_180: {"cc": "next_statement", "rl": "month_end"},
    SEG_180_PLUS: {"cc": "month_end", "rl": "month_end"},
}
STATEMENT_FALLBACK_D = 31  # no statement after the promise day yet: 31 days


def promise_deadline(product: str, model_id: str) -> str:
    """The ``PROMISE_DEADLINE`` of ``product`` in ``model_id``'s segment."""
    return PROMISE_DEADLINE[segment(model_id)][product]


# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20; Q-28, Q-29, Q-30) ─────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of positive minimum due averaged (D-A3-12)

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, ("thin",)),
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

New:

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS, segment
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
# The deadline a promise is judged by, whatever date was promised (D-A3-28): at 60-180 a
# card promise by the next statement after the promise day, however close; a loan
# promise, and every promise at 180+, by the end of the promise month. The options and
# their cutoffs: promises.CUTOFFS.
PROMISE_DEADLINE = {
    SEG_60_180: {"cc": "next_statement", "rl": "month_end"},
    SEG_180_PLUS: {"cc": "month_end", "rl": "month_end"},
}
# next-statement deadline: at most 31 days after the promise (no statement on record by
# then: statements are missing from the history) (D-A3-29)
NEXT_STATEMENT_MAX_DAYS = 31
PROMISE_DAYS = 30  # the "30_days" options: 30 days after the promise


def promise_deadline(product: str, model_id: str, override: str | None = None) -> str:
    """``override`` if given, else the ``PROMISE_DEADLINE`` of ``product`` in
    ``model_id``'s segment."""
    return override or PROMISE_DEADLINE[segment(model_id)][product]


# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
# Dimension A: the smallest promised amount and a partial payment (D-A3-29); the same
# 100 AED today, kept apart so the two can move separately.
PROMISE_MIN_AED = MIN_PAYMENT_AED
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20, -32; Q-29, Q-30) ──────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── Source history ────────────────────────────────────────────────────────────
# Months of payment history read before the earliest window a dimension opens (the
# episode start, or the first observation month): the longest window and one cycle.
HISTORY_MONTHS = (
    max(PRE_DLQ_MONTHS, COMMITMENT_MONTHS, *ANY_PAYMENT_MONTHS.values()) + 1
)

# ── State (D-A3-16, -19, -20, -22, -24, -33) ───────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
# a promise counts even when broken; never promising scores 0 (D-A3-33)
COMMITMENT_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension(
            "commitments", "a3_commitments_level", COMMITMENT_POINTS, ("no_promise",)
        ),
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py`
action: replace · base sha256 `59560b85bfb3cd66f89725e065c09fa6f8ece20bda3f7776331ce3287558950f` · base trailing newline: yes · new sha256 `a49f88cf5934b3afe99aebf05a3fd2e267eb067cdeee81dcb472d4799fd058bc` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A3 payment credibility pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base, crx_<p>_a4_deterioration ─► episode ─┬───────────────────┐
    product dues + payments (wrapper nodes) ─► cycle ledger ┼─ Dim B, Dim C ────┤
    DCORE plans ─► instalments ┬─ promise events ───────────┼─ Dim A ───────────┼─► state
    dcore_prm_followup_outcomes┴────────────────────────────┴─ contacts ────────┘

Needs, for the model_id: the obs base, A4, the product's payment sources and the DCORE
tables. Promises are judged by ``PROMISE_DEADLINE`` (at 60-180 CC the next statement, RL
the month end; at 180+ the month end).
"""

from functools import partial

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a3_credibility
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import (
    build_a3_episode,
    build_cycle_ledger,
    build_instalments,
    build_promise_events,
)

TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
# Ledger names as in the workplace catalog.
LEDGER = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}


def create_a3_pipeline(
    product: str, output: str, dues: Node, payments: Node, deadline: str | None = None
) -> Pipeline:
    """The A3 axis for ``product``, written to ``output``. ``dues`` / ``payments`` are
    the product nodes writing ``crx_<p>_a3_dues`` / ``crx_<p>_a3_payments``.
    ``deadline`` overrides ``PROMISE_DEADLINE`` (e.g. ``30_days``)."""
    p = f"crx_{product}_a3"
    episode, ledger, inst = f"{p}_episode", LEDGER[product], f"{p}_instalments"
    events = f"{p}_promise_events"

    def step(func, inputs: dict, out: str, name: str) -> Node:
        return node(
            func=func, inputs=inputs, outputs=out, name=f"build_{name}", tags=TAGS
        )

    return Pipeline(
        [
            step(
                build_a3_episode,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "deterioration": f"crx_{product}_a4_deterioration",
                },
                episode,
                episode,
            ),
            dues,
            payments,
            step(
                build_cycle_ledger,
                {"dues": f"{p}_dues", "payments": f"{p}_payments"},
                ledger,
                ledger,
            ),
            step(
                build_instalments,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "agreements": "prm_dcore_account_agreements",
                    "int_ptp": "dcore_int_ptp",
                    "ptp_instalments": "dcore_prm_promise_instalments",
                    "int_settlement": "dcore_int_settlement",
                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
                },
                inst,
                inst,
            ),
            step(
                partial(build_promise_events, product=product, deadline=deadline),
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "dues": f"{p}_dues",
                    "payments": f"{p}_payments",
                    "model_id": "params:model_id",
                },
                events,
                events,
            ),
            step(
                build_commitment_signals,
                {"episode": episode, "events": events},
                f"{p}_commitment_signals",
                f"{p}_commitment_signals",
            ),
            step(
                build_dlq_payment_signals,
                {"episode": episode, "ledger": ledger, "model_id": "params:model_id"},
                f"{p}_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_dlq_payment_signals",
            ),
            step(
                build_pre_dlq_payment_signals,
                {"episode": episode, "ledger": ledger},
                f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_pre_dlq_payment_signals",
            ),
            step(
                build_contact_signals,
                {
                    "episode": episode,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "payments": f"{p}_payments",
                    "dues": f"{p}_dues",
                    "model_id": "params:model_id",
                },
                f"{p}_strong_negative_signals",
                f"{p}_contact_signals",
            ),
            step(
                partial(build_a3_credibility, product=product, deadline=deadline),
                {
                    "episode": episode,
                    "commitments": f"{p}_commitment_signals",
                    "dlq_payments": f"{p}_dlq_payment_signals_single_payment_cycle_count",
                    "pre_dlq": f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                    "contacts": f"{p}_strong_negative_signals",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                output,
                f"{p}_payment_credibility",
            ),
        ]
    )
`````

New:

`````python
"""The A3 payment credibility pipeline for one product (``cc`` or ``rl``).

    obs base + A4 ─► episode (every signal starts from it)
    dues + payments (wrapper nodes) ─► cycle ledger ─► Dim B, Dim C signals
    DCORE plans ─► instalments ─► promise events ─► Dim A signals
    DCORE follow-up outcomes ─► contact signals
    episode + the four signal tables ─► state

Needs, for the model_id: the obs base, A4, the product's dues and payments and the DCORE
tables. Promises are judged by ``PROMISE_DEADLINE`` (at 60-180 CC the next statement, RL
the month end; at 180+ the month end).
"""

from functools import partial

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a3_credibility
from .promises import build_promise_events
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import build_a3_episode, build_cycle_ledger, build_instalments

TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
# Ledger names as in the workplace catalog.
LEDGER = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}


def create_a3_pipeline(
    product: str, output: str, dues: Node, payments: Node, deadline: str | None = None
) -> Pipeline:
    """The A3 axis for ``product``, written to ``output``. ``dues`` / ``payments`` are
    the product nodes writing ``crx_<p>_a3_dues`` / ``crx_<p>_a3_payments``.
    ``deadline`` overrides ``PROMISE_DEADLINE`` (e.g. ``30_days``)."""
    p = f"crx_{product}_a3"
    episode, ledger, inst = f"{p}_episode", LEDGER[product], f"{p}_instalments"
    events = f"{p}_promise_events"
    commitments = f"{p}_commitment_signals"
    dlq = f"{p}_dlq_payment_signals_single_payment_cycle_count"
    pre_dlq = f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
    contacts = f"{p}_strong_negative_signals"

    def step(func, inputs: dict, out: str, name: str) -> Node:
        return node(
            func=func, inputs=inputs, outputs=out, name=f"build_{name}", tags=TAGS
        )

    return Pipeline(
        [
            step(
                build_a3_episode,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "deterioration": f"crx_{product}_a4_deterioration",
                },
                episode,
                episode,
            ),
            dues,
            payments,
            step(
                build_cycle_ledger,
                {"dues": f"{p}_dues", "payments": f"{p}_payments"},
                ledger,
                ledger,
            ),
            step(
                build_instalments,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "agreements": "prm_dcore_account_agreements",
                    "int_ptp": "dcore_int_ptp",
                    "ptp_instalments": "dcore_prm_promise_instalments",
                    "int_settlement": "dcore_int_settlement",
                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
                },
                inst,
                inst,
            ),
            step(
                partial(build_promise_events, product=product, deadline=deadline),
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "dues": f"{p}_dues",
                    "payments": f"{p}_payments",
                    "model_id": "params:model_id",
                },
                events,
                events,
            ),
            step(
                build_commitment_signals,
                {"episode": episode, "events": events},
                commitments,
                commitments,
            ),
            step(
                build_dlq_payment_signals,
                {"episode": episode, "ledger": ledger, "model_id": "params:model_id"},
                dlq,
                f"{p}_dlq_payment_signals",
            ),
            step(
                build_pre_dlq_payment_signals,
                {"episode": episode, "ledger": ledger},
                pre_dlq,
                f"{p}_pre_dlq_payment_signals",
            ),
            step(
                build_contact_signals,
                {
                    "episode": episode,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "payments": f"{p}_payments",
                    "dues": f"{p}_dues",
                    "model_id": "params:model_id",
                },
                contacts,
                f"{p}_contact_signals",
            ),
            step(
                partial(build_a3_credibility, product=product, deadline=deadline),
                {
                    "episode": episode,
                    "commitments": commitments,
                    "dlq_payments": dlq,
                    "pre_dlq": pre_dlq,
                    "contacts": contacts,
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                output,
                f"{p}_payment_credibility",
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/promises.py`
action: add · new sha256 `99a56fdb6ec759625bff1d75abdfb53412de3391d488d524e1b4ecc6de3fb32e` · new trailing newline: yes

New:

`````python
"""A3 promise events (D-A3-25, -28, -29): DCORE plans and follow-up promises grouped
into events, each judged by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    NEXT_STATEMENT_MAX_DAYS,
    PROMISE_DAYS,
    PROMISE_MIN_AED,
    promise_deadline,
)
from .sources import DUES, INSTALMENTS, PAYMENTS

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]
# What a promise day decides for an event that starts on it (D-A3-29).
_TERMS = ("promise_cutoff", "promise_amount", "promise_paid_amount")
_DAY_TERMS = ("event_date", *_TERMS)


def _next_statement(day: Column, next_cycle_end: Column) -> Column:
    """The first cycle end after ``day``, at most ``NEXT_STATEMENT_MAX_DAYS`` days after
    it (no statement on record by then: that day)."""
    fallback = F.date_add(day, NEXT_STATEMENT_MAX_DAYS)
    return F.least(F.coalesce(next_cycle_end, fallback), fallback)


# ``promise_cutoff``, the last day a payment still counts, per deadline option
# (D-A3-28), from the promise day and the first cycle end after it.
CUTOFFS = {
    "next_statement": _next_statement,
    "month_end": lambda day, _: F.last_day(day),
    "next_month_end": lambda day, _: F.last_day(F.add_months(day, 1)),
    "30_days": lambda day, _: F.date_add(day, PROMISE_DAYS),
    "30_days_month_end": lambda day, _: F.last_day(F.date_add(day, PROMISE_DAYS)),
}
DEADLINES = tuple(CUTOFFS)


def _promise_rows(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
) -> DataFrame:
    """Every promise of the base's accounts, one row each: a DCORE plan dated at its
    start, a follow-up promise (``_dcore_codes.PROMISE_EVENT``) at its call day."""
    calls = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select(
            "account_id",
            F.col("day").alias("event_date"),
            F.col("name").alias("event_name"),
            F.lit(None).cast("string").alias("plan_id"),
            F.lit("followup").alias("event_source"),
        )
        .distinct()
    )
    plans = instalments.select(
        "account_id",
        F.col("plan_start").alias("event_date"),
        F.lit(None).cast("string").alias("event_name"),
        "plan_id",
        F.col("plan_type").alias("event_source"),
    ).distinct()
    return plans.unionByName(calls)


def _with_terms(days: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``days`` (``account_id``, ``event_date``) + ``promise_cutoff`` (``CUTOFFS``) and
    ``promise_amount``: the latest due on or before the day (cycles without a due amount
    skipped), at least ``PROMISE_MIN_AED`` (D-A3-29). One pass over the account's
    cycles."""
    day = F.col("event_date")
    known_due = F.col("due_amount").isNotNull() & (F.col("cycle_start") <= day)
    cycles = (
        days.join(
            dues.select("account_id", "cycle_start", "cycle_end", "due_amount"),
            on="account_id",
            how="left",
        )
        .groupBy("account_id", "event_date")
        .agg(
            F.min(F.when(F.col("cycle_end") > day, F.col("cycle_end"))).alias("_next"),
            F.max(F.when(known_due, F.struct("cycle_start", "due_amount")))[
                "due_amount"
            ].alias("_due"),
        )
    )
    return cycles.select(
        "account_id",
        "event_date",
        CUTOFFS[deadline](day, F.col("_next")).alias("promise_cutoff"),
        F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(PROMISE_MIN_AED))).alias(
            "promise_amount"
        ),
    )


def _after(day: Column) -> Column:
    """A payment counted as made after ``day``: dated later, or dated that day when its
    period started earlier (RL cash is dated at the month end)."""
    return (F.col("pay_date") > day) | (
        (F.col("pay_date") == day) & (F.col("pay_from") < F.col("pay_date"))
    )


def _with_payments(days: DataFrame, payments: DataFrame) -> DataFrame:
    """``days`` + three sums from one pass over the payments up to the day's
    ``promise_cutoff``: ``_paid_before`` (dated before the day), ``_paid_not_after``
    (not after it, ``_after``) and ``promise_paid_amount`` (after the day; NULL: none).
    Only a payment after the promise can keep it, so an event starting that day counts
    the last and never the money in ``_paid_not_after``."""
    day = F.col("event_date")
    pays = payments.select(
        F.col("account_id").alias("_p_account"),
        "pay_from",
        "pay_date",
        F.col("amount").alias("_amount"),
    )

    def total(counted: Column) -> Column:
        return F.coalesce(F.sum(F.when(counted, F.col("_amount"))), F.lit(0.0))

    return (
        days.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & (F.col("pay_date") <= F.col("promise_cutoff")),
            "left",
        )
        .groupBy(*days.columns)
        .agg(
            total(F.col("pay_date") < day).alias("_paid_before"),
            total(~_after(day)).alias("_paid_not_after"),
            F.sum(F.when(_after(day), F.col("_amount"))).alias("promise_paid_amount"),
        )
    )


def _event_step(live: Column, day: Column) -> Column:
    """Fold one promise day into ``live``, the event alive so far (D-A3-29). The day
    joins it while its deadline has not passed and the payments since the event day,
    before this day, have not reached its promised amount; otherwise the day starts a
    new event. ``starts``: the event start of every day so far."""
    # to the cent: a difference of two sums can fall a hair short of an exact payment
    paid_since_start = F.round(day["_paid_before"] - live["paid_at_start"], 2)
    joins = (
        live["start"].isNotNull()
        & (day["event_date"] <= live["cutoff"])
        & (paid_since_start < live["amount"])
    )

    def keep(old: str, new: str) -> Column:
        return F.when(joins, live[old]).otherwise(day[new]).alias(old)

    start = keep("start", "event_date")
    return F.struct(
        F.concat(live["starts"], F.array(start)).alias("starts"),
        start,
        keep("cutoff", "promise_cutoff"),
        keep("amount", "promise_amount"),
        keep("paid_at_start", "_paid_not_after"),
    )


def _no_event() -> Column:
    """The empty ``_event_step`` accumulator."""
    return F.struct(
        F.array().cast("array<date>").alias("starts"),
        F.lit(None).cast("date").alias("start"),
        F.lit(None).cast("date").alias("cutoff"),
        F.lit(None).cast("double").alias("amount"),
        F.lit(None).cast("double").alias("paid_at_start"),
    )


def _with_event_start(days: DataFrame) -> DataFrame:
    """``account_id``, ``_DAY_TERMS`` and ``event_start``, the event each promise day
    belongs to (``_event_step`` over the account's days in date order)."""
    ordered = F.array_sort(
        F.collect_list(F.struct(*_DAY_TERMS, "_paid_before", "_paid_not_after"))
    )
    return (
        days.groupBy("account_id")
        .agg(ordered.alias("_days"))
        .withColumn("_starts", F.aggregate("_days", _no_event(), _event_step)["starts"])
        .select("account_id", F.explode(F.arrays_zip("_days", "_starts")).alias("_d"))
        .select(
            "account_id",
            *[F.col(f"_d._days.{c}").alias(c) for c in _DAY_TERMS],
            F.col("_d._starts").alias("event_start"),
        )
    )


def _events(promises: DataFrame, days: DataFrame) -> DataFrame:
    """One event per ``event_start``: its first plan (``plan_id``, ``event_source``) and
    first follow-up promise (``event_name``); ``event_kind`` matched (both), table_only
    or followup_only; the start day's cutoff, promised amount and paid amount."""
    is_plan = F.col("plan_id").isNotNull()
    plan = F.min(F.when(is_plan, F.struct("event_date", "plan_id", "event_source")))
    call = F.min(F.when(~is_plan, F.struct("event_date", "event_name")))
    start_day = F.max(
        F.when(F.col("event_date") == F.col("event_start"), F.struct(*_TERMS))
    )
    return (
        promises.join(days, on=["account_id", "event_date"])
        .groupBy("account_id", "event_start")
        .agg(plan.alias("_plan"), call.alias("_call"), start_day.alias("_start"))
        .select(
            "account_id",
            F.col("event_start").alias("event_date"),
            F.when(F.col("_plan").isNull(), "followup_only")
            .when(F.col("_call").isNull(), "table_only")
            .otherwise("matched")
            .alias("event_kind"),
            F.coalesce("_plan.event_source", F.lit("followup")).alias("event_source"),
            F.col("_call.event_name").alias("event_name"),
            F.col("_plan.plan_id").alias("plan_id"),
            "_start.*",
        )
    )


def _judged(events: DataFrame) -> DataFrame:
    """``EVENTS``: ``promise_outcome`` paid when the payments reach the promised amount
    (to the cent, as in ``_event_step``), partial from ``PROMISE_MIN_AED``, else none.
    ``promise_paid_amount`` runs to the event's deadline, so after an event that ended
    early it overlaps the next event's: never sum it across events."""
    paid = F.round(F.coalesce("promise_paid_amount", F.lit(0.0)), 2)
    outcome = (
        F.when(paid >= F.col("promise_amount"), "paid")
        .when(paid >= PROMISE_MIN_AED, "partial")
        .otherwise("none")
    )
    return (
        events.withColumn("promise_paid_amount", paid)
        .withColumn("promise_outcome", outcome)
        .select(*EVENTS)
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    model_id: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment. ``EVENTS``.

    A promise is a non-cancelled PTP or settlement plan (dated at its start) or a
    follow-up promise. An event starts with the first promise and stays alive until its
    deadline passes or the payments since its day reach the promised amount; every
    promise meanwhile belongs to it, the first one after it starts a new event
    (D-A3-29). ``event_kind``: matched (plans and follow-up promises), table_only,
    followup_only.

    The event day sets the terms: ``promise_cutoff`` by ``deadline`` (default
    ``promise_deadline(product, model_id)``, D-A3-28) and ``promise_amount``, the latest
    due on or before that day (at least ``PROMISE_MIN_AED``). Judged once on the
    payments after the event day up to the cutoff: paid when they reach the amount,
    partial from ``PROMISE_MIN_AED``, else none. RL cash is dated at the month end, so
    the event month's cash counts in full and never ends an event mid-month.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    if deadline not in CUTOFFS:
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    promises = _promise_rows(obs_base, followup, agreements, instalments)
    days = promises.select("account_id", "event_date").distinct()
    days = _with_payments(_with_terms(days, dues, deadline), payments)
    return _judged(_events(promises, _with_event_start(days)))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py`
action: replace · base sha256 `ab3b282d9aecc152141ccda1826754749d2c8246aaef2667d132aedbcf90099a` · base trailing newline: yes · new sha256 `76aa555f6ef5d5593f98cdc0a78eb881dffdcd4e2490f7b8baf5c7a1f9de5804` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / thin / broken (D-A3-9, -25, -26).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only), concluded once their cutoff is on or before the
    observation date. Kept: paid; partial counts as not kept. Broken: the last 3
    concluded all not kept (a broken event ranks first on a shared day), or at least 2
    concluded and under 40% kept. Kept: at least 2 concluded and 80% kept.
    """
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct(
                        "event_date", (~F.col("_kept")).cast("int").alias("broken")
                    ),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    agg = rows.groupBy(*GRAIN).agg(
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when(
            (F.col("commitments_last_broken_n") >= BROKEN_STREAK)
            | ((done >= MIN_CONCLUDED) & (rate < BROKEN_RATE)),
            "broken",
        )
        .when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .otherwise("thin")
    )
    counts = [
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
        "commitments_last_broken_n",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
            rate.alias("commitments_kept_rate"),
            "commitments_last_broken_n",
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_REPORTED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


def _disposition(name: Column) -> Column:
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid after the
    refusal day, up to the observation date (Q-29)."""
    cycles = dues.select("account_id", "cycle_start", "cycle_end")
    pays = (
        payments.alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_from") > F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
    max_months: int | None = DCORE_MAX_MONTHS,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on the same day a non-refusal counts as later
    (a same-day promise followed the refusal); a remaining tie takes the largest
    disposition (Q-28). ``a3_refusal_flag``: it was a refusal and no plan started and no
    cycle / month with 100 AED or more paid followed. Diagnostics (not in the state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    base = _base(episode)
    lower = window_start(max_months) if max_months else None
    lower = F.col("_anchor") if lower is None else F.greatest(lower, F.col("_anchor"))
    events = (
        base.join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct(
                "day", (F.col("_disp") != "refusal").cast("int").alias("later"), "_disp"
            ),
        )
    )
    summary = events.groupBy(*GRAIN).agg(
        latest["day"].alias("last_rpc_date"),
        latest["_disp"].alias("last_rpc_disposition"),
        F.countDistinct(
            F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
        ).alias("contact_dates_n"),
    )
    after = events.join(summary.select(*GRAIN, "last_rpc_date"), on=list(GRAIN)).filter(
        F.col("day") > F.col("last_rpc_date")
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    quiet = after.groupBy(*GRAIN).agg(
        F.countDistinct(F.when(no_pickup, F.col("day"))).alias("no_pickup_days_n"),
        F.max(F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")).alias(
            "_dead"
        ),
    )
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") > F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        base.select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(quiet, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
`````

New:

`````python
"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    require_columns,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)
from .promises import EVENTS
from .sources import CYCLE_LEDGER, DUES, EPISODE, INSTALMENTS, PAYMENTS


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    """``GRAIN`` and ``_anchor`` of every base row."""
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _commitment_counts(base: DataFrame, events: DataFrame, lower: Column) -> DataFrame:
    """Per base row with an event in ``[lower, observation date]``: the event, concluded,
    kept and partly kept counts and ``commitments_last_broken_n``, the not-kept events among
    the last ``BROKEN_STREAK`` concluded."""
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct(
                        "event_date", (~F.col("_kept")).cast("int").alias("broken")
                    ),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    return rows.groupBy(*GRAIN).agg(
        F.count(F.lit(1)).alias("commitments_n"),
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / broken / promised / no promise (D-A3-9, -26, -33).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only); concluded once their cutoff is on or before the observation date.
    An event is kept when paid; partial counts as not kept. Broken: the last 3 concluded
    all not kept (a broken event ranks first on a shared day), or at least 2 concluded
    and under 40% kept. Kept: at least 2 concluded and 80% kept. Partly kept: any
    kept event. Promised: any other event in the window. Else no_promise.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(events, EVENTS, "A3 promise events")
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    agg = _commitment_counts(base, events, lower)
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when(
            (F.col("commitments_last_broken_n") >= BROKEN_STREAK)
            | ((done >= MIN_CONCLUDED) & (rate < BROKEN_RATE)),
            "broken",
        )
        .when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .when(F.col("commitments_n") >= 1, "promised")
        .otherwise("no_promise")
    )
    counts = [
        "commitments_n",
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
        "commitments_last_broken_n",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_n",
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
            rate.alias("commitments_kept_rate"),
            "commitments_last_broken_n",
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_REPORTED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


# Contacts on the same day: the one later in this order counts as the latest (D-A3-32:
# promise > payment reported > refusal > dispute > contact > hung up).
_SAME_DAY_ORDER = ("hung_up", "success", "dispute", "refusal", "paid", "ptp")


def _disposition(name: Column) -> Column:
    """The ``_DISPOSITIONS`` label of a DCORE result name (NULL: not a contact)."""
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid on or after
    the refusal day, up to the observation date (Q-29, D-A3-30). A payment that may
    have come after the refusal lifts it: one dated the refusal day, and on RL the
    refusal month's cash (known only to the month)."""
    accounts = F.broadcast(refusals.select("account_id").distinct())
    cycles = dues.select("account_id", "cycle_start", "cycle_end").join(
        accounts, on="account_id", how="left_semi"
    )
    pays = (
        payments.join(accounts, on="account_id", how="left_semi")
        .alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_date") >= F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def _contact_events(
    episode: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """The account's DCORE events in ``[max(episode start, last DCORE_MAX_MONTHS
    months), observation date]`` with their ``_disp`` disposition (NULL: not a
    contact)."""
    lower = F.greatest(window_start(DCORE_MAX_MONTHS), F.col("_anchor"))
    return (
        _base(episode)
        .join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )


def _contact_summary(events: DataFrame) -> DataFrame:
    """Per base row: the latest right-party contact (``last_rpc_date``,
    ``last_rpc_disposition``; on one day, the latest by ``_SAME_DAY_ORDER``), the call
    days (``contact_dates_n``), the days with no pickup after the contact
    (``no_pickup_days_n``) and ``_dead``, 1 when a dead-line result came after it."""
    same_day_rank = F.lit(None).cast("int")
    for rank, label in enumerate(_SAME_DAY_ORDER):
        same_day_rank = F.when(F.col("_disp") == label, rank).otherwise(same_day_rank)
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct("day", same_day_rank.alias("same_day_rank"), "_disp"),
        )
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    last_day = F.col("_last")["day"]
    after = F.col("day") > last_day
    return (
        events.withColumn("_last", latest.over(Window.partitionBy(*GRAIN)))
        .groupBy(*GRAIN)
        .agg(
            F.max("_last")["day"].alias("last_rpc_date"),
            F.max("_last")["_disp"].alias("last_rpc_disposition"),
            F.size(
                F.collect_set(
                    F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
                )
            )
            .cast("long")
            .alias("contact_dates_n"),
            F.size(F.collect_set(F.when(after & no_pickup, F.col("day"))))
            .cast("long")
            .alias("no_pickup_days_n"),
            F.max(
                F.when(
                    after, F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")
                )
            ).alias("_dead"),
        )
    )


def _plan_after_refusal(refusals: DataFrame, instalments: DataFrame) -> DataFrame:
    """Rows whose plan started on or after the refusal day, by the observation date
    (D-A3-30: a plan of the same day may have followed the refusal)."""
    return (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") >= F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on one day, the latest by ``_SAME_DAY_ORDER``
    (D-A3-32).
    ``a3_refusal_flag``: it was a refusal, no plan started after it and no cycle / month
    with 100 AED or more paid may have come after it (D-A3-30). Diagnostics (not in the
    state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(payments, PAYMENTS, "A3 payments")
    require_columns(dues, DUES, "A3 dues")
    events = _contact_events(episode, followup, agreements)
    summary = _contact_summary(events)
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = _plan_after_refusal(refusals, instalments)
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        _base(episode)
        .select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py`
action: replace · base sha256 `1394e42d6a185eeb0363af8950d2915d4dd0d77e23db8748483df3eae02db4ee` · base trailing newline: yes · new sha256 `e9a01a5e3a65681b4320184c39c17a7a0e9bfd850d2cf3d3a01c82c6ef8b4f9b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 source nodes shared by both products: the episode anchor, the cycle ledger, the
DCORE plans and the promise events."""

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import GRAIN, dcore_account_events, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start
from .constants import (
    DEADLINES,
    FOLLOWUP_RUN_DAYS,
    MATCH_DAYS,
    MIN_PAYMENT_AED,
    STATEMENT_FALLBACK_D,
    promise_deadline,
)

DUES = ["account_id", "cycle_start", "cycle_end", "due_amount", "billed_amount"]
PAYMENTS = ["account_id", "pay_from", "pay_date", "amount"]


def build_a3_episode(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for every base row (D-A3-2).

    ``episode_start`` is the first day of the month the current delinquency episode
    began, from A4 as of the observation date; NULL when A4 did not score the row (A3
    then reads Unknown, reason ``no_episode``, Q-12).
    """
    return obs_base.select(*GRAIN, "cif_id").join(
        episode_start(obs_base, deterioration), on=list(GRAIN), how="left"
    )


def build_cycle_ledger(dues: DataFrame, payments: DataFrame) -> DataFrame:
    """One row per account cycle: ``DUES`` + ``paid_amount``, the payments with
    ``cycle_start < pay_date <= cycle_end`` (paid before the next statement, D-A3-8).

    ``dues`` and ``payments`` follow the product contracts ``DUES`` / ``PAYMENTS``
    (CC: statement cycles and card payments; RL: months and the month's cash).
    """
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    paid = (
        dues.select("account_id", "cycle_start", "cycle_end")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(
            (F.col("pay_date") > F.col("cycle_start"))
            & (F.col("pay_date") <= F.col("cycle_end"))
        )
        .groupBy("account_id", "cycle_end")
        .agg(F.sum("amount").alias("paid_amount"))
    )
    return (
        dues.select(*DUES)
        .join(paid, on=["account_id", "cycle_end"], how="left")
        .withColumn("paid_amount", F.coalesce(F.col("paid_amount"), F.lit(0.0)))
    )


def build_instalments(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> DataFrame:
    """PTP and settlement instalments of the base's accounts (D-A3-7, D-A3-9).

    One row per instalment of a non-cancelled plan: ``account_id``, ``plan_id``,
    ``plan_type``, ``plan_start`` (PTP: promise start, else event date; settlement: event
    date, the only date DCORE keeps), ``due_date``, ``due_amount``, ``payment_amount``
    (DCORE's). Cancelled instalments are nulled by DCORE's own rule and dropped.
    """
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    require_columns(
        int_ptp,
        [
            "agreement_id",
            "promise_seqno",
            "promise_start",
            "event_date",
            "is_cancelled",
        ],
        "dcore_int_ptp",
    )
    require_columns(
        int_settlement,
        ["agreement_id", "rps_seqno", "event_date", "is_cancelled"],
        "dcore_int_settlement",
    )
    cols = ["due_date", "due_amount", "payment_amount", "instalment_status"]
    require_columns(
        ptp_instalments, ["promise_seqno", *cols], "dcore_prm_promise_instalments"
    )
    require_columns(
        settlement_instalments,
        ["rps_seqno", *cols],
        "dcore_prm_settlement_schedule_instalments",
    )
    links = scoped(
        agreements.select(
            string_key(agreements).alias("account_id"),
            F.col("agreement_id").cast("string").alias("agreement_id"),
        ),
        obs_base,
        "account_id",
    )

    def plans(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        plan: DataFrame, seq: str, start, kind: str, rows: DataFrame, cancelled
    ) -> DataFrame:
        live = plan.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            seq,
            F.concat_ws(":", F.lit(kind), F.col(seq).cast("string")).alias("plan_id"),
            F.lit(kind).alias("plan_type"),
            start.cast("date").alias("plan_start"),
        )
        return null_cancelled_instalment_fields(
            live.join(rows.select(seq, *cols), on=seq), cancelled
        ).drop(seq)

    ptp = plans(
        int_ptp,
        "promise_seqno",
        F.coalesce(F.col("promise_start"), F.col("event_date")),
        "ptp",
        ptp_instalments,
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = plans(
        int_settlement,
        "rps_seqno",
        F.col("event_date"),
        "settlement",
        settlement_instalments,
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    return (
        ptp.unionByName(settlement)
        .join(F.broadcast(links), on="agreement_id")
        .where(F.col("due_date").isNotNull())
        .select(
            "account_id",
            "plan_id",
            "plan_type",
            "plan_start",
            F.col("due_date").cast("date").alias("due_date"),
            F.col("due_amount").cast("double").alias("due_amount"),
            F.col("payment_amount").cast("double").alias("payment_amount"),
        )
    )


# ── Promise events (D-A3-25) ──────────────────────────────────────────────────

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]


def _followup_promises(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Follow-up promise runs per account: rows less than 8 days after the previous one
    belong to the same run, dated (and named) at its first row."""
    rows = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select("account_id", "day", "name")
        .distinct()
    )
    order = Window.partitionBy("account_id").orderBy("day", "name")
    gap = F.datediff("day", F.lag("day").over(order))
    new_run = F.when(gap.isNull() | (gap > FOLLOWUP_RUN_DAYS), 1).otherwise(0)
    first = F.min(F.struct("day", "name"))
    return (
        rows.withColumn(
            "_run", F.sum(new_run).over(order.rowsBetween(Window.unboundedPreceding, 0))
        )
        .groupBy("account_id", "_run")
        .agg(first["day"].alias("fu_date"), first["name"].alias("event_name"))
        .drop("_run")
    )


def _consolidate(plans: DataFrame, promises: DataFrame) -> DataFrame:
    """One event per DCORE plan and per follow-up promise no plan claims. A plan takes
    its nearest follow-up promise within 7 days (each promise at most once): the event
    keeps the plan's date and the promise's name (``matched``)."""
    pairs = (
        plans.select("account_id", "plan_id", "event_date")
        .join(promises, on="account_id")
        .withColumn("_dist", F.abs(F.datediff("fu_date", "event_date")))
        .where(F.col("_dist") <= MATCH_DAYS)
    )
    for key, tie in ((["plan_id"], "fu_date"), (["fu_date"], "plan_id")):
        nearest = Window.partitionBy("account_id", *key).orderBy("_dist", tie)
        pairs = pairs.withColumn("_r", F.row_number().over(nearest)).where("_r = 1")
    table = plans.join(
        pairs.select("account_id", "plan_id", "event_name"),
        on=["account_id", "plan_id"],
        how="left",
    ).select(
        "account_id",
        "event_date",
        F.when(F.col("event_name").isNotNull(), "matched")
        .otherwise("table_only")
        .alias("event_kind"),
        F.col("plan_type").alias("event_source"),
        "event_name",
        "plan_id",
    )
    alone = promises.join(
        pairs.select("account_id", "fu_date"), on=["account_id", "fu_date"], how="anti"
    ).select(
        "account_id",
        F.col("fu_date").alias("event_date"),
        F.lit("followup_only").alias("event_kind"),
        F.lit("followup").alias("event_source"),
        "event_name",
        F.lit(None).cast("string").alias("plan_id"),
    )
    return table.unionByName(alone)


def _cutoff(events: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``events`` + ``promise_cutoff``: the last day a payment still counts."""
    day = F.col("event_date")
    fixed = {
        "month_end": F.last_day(day),
        "next_month_end": F.last_day(F.add_months(day, 1)),
        "30_days": F.date_add(day, 30),
        "30_days_month_end": F.last_day(F.date_add(day, 30)),
    }
    if deadline in fixed:
        return events.withColumn("promise_cutoff", fixed[deadline])
    if deadline != "next_statement":
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    nxt = (
        events.select("account_id", "event_date")
        .distinct()
        .join(dues.select("account_id", "cycle_end"), on="account_id")
        .where(F.col("cycle_end") > day)
        .groupBy("account_id", "event_date")
        .agg(F.min("cycle_end").alias("promise_cutoff"))
    )
    return events.join(nxt, on=["account_id", "event_date"], how="left").withColumn(
        "promise_cutoff",
        F.coalesce("promise_cutoff", F.date_add(day, STATEMENT_FALLBACK_D)),
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    model_id: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment (D-A3-25). ``EVENTS``.

    Events: every non-cancelled PTP and settlement plan (dated at its start) and every
    follow-up promise run (``_dcore_codes.PROMISE_EVENT``) no plan claims
    (``event_kind`` matched / table_only / followup_only). Judged once: the payments
    after the event day up to ``promise_cutoff`` (``deadline``, by default
    ``promise_deadline(product, model_id)``) against ``promise_amount``, the due of the
    cycle open on the event day (the last known one, at least 100 AED). Paid: they reach
    it; partial: 100 AED or more; else none. RL cash is dated at the month end, so the
    event month's cash counts in full.
    """
    plans = instalments.select(
        "account_id", "plan_id", "plan_type", F.col("plan_start").alias("event_date")
    ).distinct()
    events = _cutoff(
        _consolidate(plans, _followup_promises(obs_base, followup, agreements)),
        dues,
        deadline or promise_deadline(product, model_id),
    )
    keys = ["account_id", "event_date"]
    due = (
        events.select(*keys)
        .distinct()
        .join(dues.select("account_id", "cycle_start", "due_amount"), on="account_id")
        .where(F.col("cycle_start") <= F.col("event_date"))
        .groupBy(*keys)
        .agg(F.max(F.struct("cycle_start", "due_amount"))["due_amount"].alias("_due"))
    )
    after = (F.col("pay_date") > F.col("event_date")) | (
        (F.col("pay_date") == F.col("event_date"))
        & (F.col("pay_from") < F.col("pay_date"))
    )
    paid = (
        events.select(*keys, "promise_cutoff")
        .distinct()
        .join(
            payments.select("account_id", "pay_from", "pay_date", "amount"),
            "account_id",
        )
        .where(after & (F.col("pay_date") <= F.col("promise_cutoff")))
        .groupBy(*keys, "promise_cutoff")
        .agg(F.sum("amount").alias("promise_paid_amount"))
    )
    amount = F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(MIN_PAYMENT_AED)))
    got = F.coalesce("promise_paid_amount", F.lit(0.0))
    return (
        events.join(due, on=keys, how="left")
        .join(paid, on=[*keys, "promise_cutoff"], how="left")
        .withColumn("promise_amount", amount)
        .withColumn("promise_paid_amount", got)
        .withColumn(
            "promise_outcome",
            F.when(got >= F.col("promise_amount"), "paid")
            .when(got >= MIN_PAYMENT_AED, "partial")
            .otherwise("none"),
        )
        .select(*EVENTS)
    )
`````

New:

`````python
"""A3 source builders shared by both products: the episode anchor, the cycle ledger and
the DCORE plan instalments."""

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start

DUES = ["account_id", "cycle_start", "cycle_end", "due_amount", "billed_amount"]
PAYMENTS = ["account_id", "pay_from", "pay_date", "amount"]
# Columns of the tables the A3 builders pass on: each consumer requires them.
EPISODE = [*GRAIN, "cif_id", "episode_start", "episode_left_censored"]
CYCLE_LEDGER = [*DUES, "paid_amount"]
INSTALMENTS = [
    "account_id",
    "plan_id",
    "plan_type",
    "plan_start",
    "due_date",
    "due_amount",
    "payment_amount",
]


def build_a3_episode(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for every base row (D-A3-2).

    ``episode_start`` is the first day of the month the current delinquency episode
    began, from A4 as of the observation date; NULL when A4 did not score the row (A3
    then reads Unknown, reason ``no_episode``, Q-12).
    """
    return obs_base.select(*GRAIN, "cif_id").join(
        episode_start(obs_base, deterioration), on=list(GRAIN), how="left"
    )


def build_cycle_ledger(dues: DataFrame, payments: DataFrame) -> DataFrame:
    """One row per account cycle: ``DUES`` + ``paid_amount``, the payments with
    ``cycle_start < pay_date <= cycle_end`` (paid before the next statement, D-A3-8).

    ``dues`` and ``payments`` follow the product contracts ``DUES`` / ``PAYMENTS``
    (CC: statement cycles and card payments; RL: months and the month's cash).
    """
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    paid = (
        dues.select("account_id", "cycle_start", "cycle_end")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(
            (F.col("pay_date") > F.col("cycle_start"))
            & (F.col("pay_date") <= F.col("cycle_end"))
        )
        .groupBy("account_id", "cycle_end")
        .agg(F.sum("amount").alias("paid_amount"))
    )
    return (
        dues.select(*DUES)
        .join(paid, on=["account_id", "cycle_end"], how="left")
        .withColumn("paid_amount", F.coalesce(F.col("paid_amount"), F.lit(0.0)))
    )


_INSTALMENT_FIELDS = ["due_date", "due_amount", "payment_amount", "instalment_status"]


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _require_plan_sources(
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> None:
    """Raise when a DCORE source of ``build_instalments`` lacks a column it reads."""
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    require_columns(
        int_ptp,
        [
            "agreement_id",
            "promise_seqno",
            "promise_start",
            "event_date",
            "is_cancelled",
        ],
        "dcore_int_ptp",
    )
    require_columns(
        int_settlement,
        ["agreement_id", "rps_seqno", "event_date", "is_cancelled"],
        "dcore_int_settlement",
    )
    require_columns(
        ptp_instalments,
        ["promise_seqno", *_INSTALMENT_FIELDS],
        "dcore_prm_promise_instalments",
    )
    require_columns(
        settlement_instalments,
        ["rps_seqno", *_INSTALMENT_FIELDS],
        "dcore_prm_settlement_schedule_instalments",
    )


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _plan_instalments(
    plan: DataFrame,
    seq: str,
    start: Column,
    kind: str,
    rows: DataFrame,
    cancelled: object,
    agreement_ids: DataFrame,
) -> DataFrame:
    """The instalments of the non-cancelled plans of one ``kind`` (``plan_id`` =
    ``kind:seq``, ``plan_start`` = ``start``) on the agreements in ``agreement_ids``;
    ``cancelled`` is DCORE's cancelled instalment status."""
    live = plan.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        seq,
        F.concat_ws(":", F.lit(kind), F.col(seq).cast("string")).alias("plan_id"),
        F.lit(kind).alias("plan_type"),
        start.cast("date").alias("plan_start"),
    )
    live = live.join(agreement_ids, on="agreement_id", how="left_semi")
    return null_cancelled_instalment_fields(
        live.join(rows.select(seq, *_INSTALMENT_FIELDS), on=seq), cancelled
    ).drop(seq)


def build_instalments(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> DataFrame:
    """PTP and settlement instalments of the base's accounts (D-A3-7, D-A3-9).

    One row per instalment of a non-cancelled plan: ``account_id``, ``plan_id``,
    ``plan_type``, ``plan_start`` (PTP: promise start, else event date; settlement:
    event date, the only date DCORE keeps), ``due_date``, ``due_amount``,
    ``payment_amount`` (DCORE's). Cancelled instalments are nulled by DCORE's own rule
    and dropped.
    """
    _require_plan_sources(
        agreements, int_ptp, ptp_instalments, int_settlement, settlement_instalments
    )
    links = scoped(
        agreements.select(
            string_key(agreements).alias("account_id"),
            F.col("agreement_id").cast("string").alias("agreement_id"),
        ),
        obs_base,
        "account_id",
    )
    mine = F.broadcast(links.select("agreement_id").distinct())
    ptp = _plan_instalments(
        int_ptp,
        "promise_seqno",
        F.coalesce(F.col("promise_start"), F.col("event_date")),
        "ptp",
        ptp_instalments,
        PTP_INSTALMENT_STATUS_CANCELLED,
        mine,
    )
    settlement = _plan_instalments(
        int_settlement,
        "rps_seqno",
        F.col("event_date"),
        "settlement",
        settlement_instalments,
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
        mine,
    )
    return (
        ptp.unionByName(settlement)
        .join(F.broadcast(links), on="agreement_id")
        .where(F.col("due_date").isNotNull())
        .select(
            "account_id",
            "plan_id",
            "plan_type",
            "plan_start",
            F.col("due_date").cast("date").alias("due_date"),
            F.col("due_amount").cast("double").alias("due_amount"),
            F.col("payment_amount").cast("double").alias("payment_amount"),
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/b25_check.py`
action: add · new sha256 `b7c3797f73f93125177c0b654890e35bd5203764c8db69fa45ee0d37aebea7b6` · new trailing newline: yes

New:

`````python
"""TEMPORARY (bundle 25): the shipped code rerun next to the persisted outputs.

``crx_<p>_b25_check`` runs the product's pipelines as they ship (CC raw extract, A4, A2,
A1, A3, plus product primaries / features and the bureau features) with every output
renamed ``<name>__b25`` (one catalog pattern, ``tmp_b25_check.yml``), so no real output
is touched; inputs they do not build are the persisted ones. Then it logs, for
``model_id``:

- ``B25 DIFF``: per dataset, rows old / new and rows only on one side (``exceptAll``,
  doubles rounded to 2 decimals). The refactor must give 0; datasets a behaviour step
  changes are marked, with the columns outside that step compared on their own;
- ``B25 A3 EVENTS``: promise events old / new (kind, outcome, 31-day cap, 100 AED floor);
- ``B25 A3 LEVELS``: latest month, Dimension A / B levels, refusal and latest contact
  old x new, refusals lifted by a later payment or plan;
- ``B25 A3 MOVES``: the state step by step: old -> new events and dues (old points, old
  refusal) -> new refusal -> new points (D-A3-33);
- ``B25 A3 DUES``: cards: statements with bucket 08 open and no baseline (no due);
  loans: B-window months with EMI 0 / NULL / > 0;
- ``B25 A1``: latest month, state and family levels old x new, the sweepable balance
  flag, and F1 / F2 / F3 strong (8 cells) with paid a due in the next 3 months;
- ``B25 PARENT LINK`` (cards): what ``parent_contract_id`` links on the card contracts.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b25_check
"""

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.bureau import salary_bounces
from enbd_collections.pipelines.products import features as product_features
from enbd_collections.pipelines.products import primary as product_primary

from . import (
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_raw_extract,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
)
from ._common import GRAIN, window_months
from .a3_credibility.constants import DISPLAY_NAMES, HIGH_FROM, MODERATE_FROM
from .cc_a4_deterioration import pipeline as cc_a4_deterioration

logger = logging.getLogger(__name__)
NEW = "__b25"
TAGS = ["crx_persona", "crx", "b25_check"]
OLD_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}  # before D-A3-33
NEW_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
B_POINTS, C_POINTS = {"regular": 2, "some": 1}, {"clean": 1}
CONTACT_STEP = [  # contact columns D-A3-30 / D-A3-32 may change
    "last_rpc_disposition",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
]


def _parts(product: str) -> list[Pipeline]:
    """The pipelines step 8 reruns for ``product``, in run order."""
    shared = [
        product_primary.create_pipeline(),
        product_features.create_pipeline(),
        salary_bounces.create_pipeline(),
    ]
    if product == "cc":
        axes = [cc_raw_extract, cc_a4_deterioration, cc_a2_locatability]
        axes += [cc_a1_ability, cc_a3_payment_credibility]
    else:
        axes = [rl_a4_deterioration, rl_a2_locatability, rl_a1_ability]
        axes += [rl_a3_payment_credibility]
    return shared + [m.create_pipeline() for m in axes]


def _expected(product: str) -> dict[str, list[str] | None]:
    """Datasets a behaviour step changes: name -> the columns it may change (None =
    every column). Datasets with no old version (new outputs) map to ``[]``."""
    p = f"crx_{product}"
    out: dict[str, list[str] | None] = {
        f"{p}_a3_promise_events": None,
        f"{p}_a3_commitment_signals": None,
        f"{p}_a3_payment_credibility": None,
        f"{p}_a1_ability": None,
        f"{p}_a3_strong_negative_signals": CONTACT_STEP,
        f"{p}_a3_dues": [],
        f"{p}_a3_payments": [],
    }
    if product == "cc":  # D-A3-31 changes card dues at bucket 08
        out["crx_cc_a3_payment_cycles"] = ["due_amount"]
        out["crx_cc_a3_dlq_payment_signals_single_payment_cycle_count"] = None
    return out


# ── Logging helpers ───────────────────────────────────────────────────────────


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], changed_only: bool = False) -> list[str]:
    """``cols`` value counts (``old_x`` / ``new_x`` pairs may be filtered to changes)."""
    if changed_only:
        df = df.filter(~F.col(cols[0]).eqNullSafe(F.col(cols[1])))
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "    " + " | ".join(str(r[c]) for c in cols) + f": {r['count']}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ] or ["    none"]


# ── B25 DIFF ──────────────────────────────────────────────────────────────────


def _comparable(df: DataFrame, cols: list[str]) -> DataFrame:
    """``cols`` with doubles rounded to 2 decimals; map columns cannot be compared."""
    kinds = {f.name: f.dataType for f in df.schema.fields}
    return df.select(
        *[
            (
                F.round(c, 2).alias(c)
                if isinstance(kinds[c], (T.DoubleType, T.FloatType))
                else F.col(c)
            )
            for c in cols
            if not isinstance(kinds[c], T.MapType)
        ]
    )


def _one_sided(old: DataFrame, new: DataFrame, cols: list[str]) -> tuple[int, int]:
    a, b = _comparable(old, cols), _comparable(new, cols)
    return a.exceptAll(b).count(), b.exceptAll(a).count()


def _diff_line(name: str, old: DataFrame, new: DataFrame, step) -> list[str]:
    common = [c for c in new.columns if c in old.columns]
    gone = sorted(set(old.columns) - set(new.columns))
    added = sorted(set(new.columns) - set(old.columns))
    only_old, only_new = _one_sided(old, new, common)
    tag = {False: "refactor, expect 0", None: "behaviour step"}.get(
        step if step is None or step is False else "cols", "behaviour step on columns"
    )
    line = (
        f"  {name} [{tag}]: rows old {old.count()} new {new.count()}; only old "
        f"{only_old}, only new {only_new}"
    )
    lines = [line]
    if gone or added:
        lines.append(f"      columns dropped {gone or '-'}, added {added or '-'}")
    if step:  # the columns outside the behaviour step must match
        rest = [c for c in common if c not in step]
        o, n = _one_sided(old, new, rest)
        lines.append(f"      without {step}: only old {o}, only new {n} (expect 0)")
    return lines


def compare_datasets(model_id: str, names: list[str], expected: dict, **frames) -> None:
    """``B25 DIFF``: every rerun dataset against its persisted version."""
    lines = []
    for i, name in enumerate(names):
        try:
            step = expected.get(name, False)
            lines += _diff_line(name, frames[f"o{i}"], frames[f"n{i}"], step)
        except Exception as err:  # noqa: BLE001  # pylint: disable=broad-except
            lines.append(f"  {name}: FAILED {type(err).__name__}: {err}")
    _block("B25 DIFF", model_id, lines)


# ── A3 ────────────────────────────────────────────────────────────────────────


def _events_lines(events: DataFrame, side: str) -> list[str]:
    days = F.datediff("promise_cutoff", "event_date")
    s = events.agg(
        F.count(F.lit(1)).alias("n"),
        F.sum((days == 31).cast("int")).alias("cap"),
        F.sum((F.col("promise_amount") <= 100).cast("int")).alias("floor"),
    ).collect()[0]
    return [
        (
            f"  {side}: events {s['n']}, deadline 31 days after {s['cap']}, amount at "
            f"the 100 AED floor {s['floor']}"
        ),
        "   kind | outcome:",
    ] + _counts(events, ["event_kind", "promise_outcome"])


def _points(levels: dict[str, int], col: str) -> Column:
    expr = F.lit(0)
    for level, pts in levels.items():
        expr = F.when(F.col(col) == level, F.lit(pts)).otherwise(expr)
    return expr


def _state(a_points: dict[str, int], refusal: str) -> Column:
    """The A3 state from the level columns, ``a_points`` for Dimension A and the
    ``refusal`` flag column (a refusal takes one rung off)."""
    pts = (
        _points(a_points, "a3_commitments_level")
        + _points(B_POINTS, "a3_dlq_payment_level")
        + _points(C_POINTS, "a3_pre_dlq_payment_level")
    )
    rung = F.when(pts >= HIGH_FROM, 2).when(pts >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(
        rung - F.coalesce(F.col(refusal), F.lit(False)).cast("int"), F.lit(0)
    )
    label = (
        F.when(rung == 2, DISPLAY_NAMES["high"])
        .when(rung == 1, DISPLAY_NAMES["moderate"])
        .otherwise(DISPLAY_NAMES["low"])
    )
    return F.when(F.col("episode_start").isNull(), DISPLAY_NAMES["unknown"]).otherwise(
        label
    )


def _dues_lines(ledger: DataFrame, base: DataFrame, model_id: str) -> list[str]:
    if "rl" not in model_id:
        no_due = ledger.filter(F.col("due_amount").isNull())
        return [
            (
                f"  card statements with no due (bucket 08 open, no baseline): "
                f"{no_due.count()} on {no_due.select('account_id').distinct().count()} "
                "accounts"
            ),
        ]
    since = F.add_months(F.col("observation_date"), -window_months(model_id))
    window = base.select("account_id", "observation_date").join(ledger, "account_id")
    window = window.filter(
        (F.col("cycle_end") > since) & (F.col("cycle_end") <= F.col("observation_date"))
    )
    emi = (
        F.when(F.col("due_amount").isNull(), "NULL")
        .when(F.col("due_amount") == 0, "0")
        .otherwise("> 0")
    )
    return ["  loan B-window months by EMI:"] + _counts(
        window.withColumn("emi", emi), ["emi"]
    )


def compare_a3(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old_events: DataFrame,
    new_events: DataFrame,
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A3 EVENTS / LEVELS / MOVES / DUES``."""
    _block(
        "B25 A3 EVENTS",
        model_id,
        _events_lines(old_events, "old") + _events_lines(new_events, "new"),
    )
    cols = [
        "a3_commitments_level",
        "a3_dlq_payment_level",
        "a3_pre_dlq_payment_level",
        "a3_refusal_flag",
        "last_rpc_disposition",
        "a3_state",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols]
    )
    rows = (
        _latest(new, persona_end_date)
        .join(o, list(GRAIN), "left")
        .withColumn("s_events", _state(OLD_POINTS, "old_a3_refusal_flag"))
        .withColumn("s_refusal", _state(OLD_POINTS, "a3_refusal_flag"))
        .withColumn("s_points", _state(NEW_POINTS, "a3_refusal_flag"))
        .localCheckpoint()
    )
    lines = []
    for c in cols[:5]:
        lines += [f"  {c}, old | new (changed rows):"]
        lines += _counts(rows, [f"old_{c}", c], changed_only=True)
    lines += ["  latest contact a refusal: followed by a payment | by a plan:"]
    lines += _counts(
        rows.filter(F.col("last_rpc_disposition") == "refusal"),
        ["refusal_followed_by_payment", "refusal_followed_by_plan"],
    )
    _block("B25 A3 LEVELS", model_id, lines)
    moves = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a3_state"])
    for step, a, b in (
        ("events and dues", "old_a3_state", "s_events"),
        ("refusal", "s_events", "s_refusal"),
        ("points", "s_refusal", "s_points"),
    ):
        moves += [f"  step {step}, from | to (changed rows):"]
        moves += _counts(rows, [a, b], changed_only=True)
    check = rows.filter(~F.col("s_points").eqNullSafe(F.col("a3_state"))).count()
    moves += [
        f"  rows whose recomputed state differs from a3_state: {check} (expect 0)"
    ]
    _block("B25 A3 MOVES", model_id, moves)
    _block(
        "B25 A3 DUES",
        model_id,
        _dues_lines(ledger, _latest(new, persona_end_date), model_id),
    )


# ── A1 ────────────────────────────────────────────────────────────────────────


def _paid_due(base: DataFrame, ledger: DataFrame) -> DataFrame:
    """Per base row: paid a due = payments of the cycles ending in the 3 months after
    the observation date reach max(the latest due on or before it, 100 AED)."""
    obs = F.col("observation_date")
    joined = base.select(*GRAIN).join(ledger, "account_id")
    due = F.max(F.when(F.col("cycle_end") <= obs, F.struct("cycle_end", "due_amount")))[
        "due_amount"
    ]
    paid = F.sum(
        F.when(
            (F.col("cycle_end") > obs) & (F.col("cycle_end") <= F.add_months(obs, 3)),
            F.col("paid_amount"),
        )
    )
    agg = joined.groupBy(*GRAIN).agg(due.alias("_due"), paid.alias("_paid"))
    hit = F.coalesce("_paid", F.lit(0.0)) >= F.greatest(
        F.coalesce("_due", F.lit(0.0)), F.lit(100.0)
    )
    return agg.select(*GRAIN, hit.cast("int").alias("paid_due"))


def compare_a1(  # pylint: disable=too-many-arguments
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A1``: old x new, and F1 / F2 / F3 strong with paid a due."""
    cols = [
        "a1_state",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        "a1_sweepable_balance_flag",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols if c in old.columns]
    )
    rows = _latest(new, persona_end_date).join(o, list(GRAIN), "left").localCheckpoint()
    lines = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a1_state"])
    for c in cols:
        if f"old_{c}" in rows.columns:
            lines += [f"  {c}, old | new (changed rows):"]
            lines += _counts(rows, [f"old_{c}", c], changed_only=True)
        else:
            lines += [f"  {c} (new column):"] + _counts(rows, [c])
    strong = [
        F.coalesce(F.col("a1_income_level") == "stable", F.lit(False))
        .cast("int")
        .alias("f1"),
        F.coalesce(F.col("a1_money_in_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f2"),
        F.coalesce(F.col("a1_money_out_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f3"),
    ]
    lines += ["  F1 | F2 | F3 strong, latest month:"]
    lines += _counts(rows.select(*strong), ["f1", "f2", "f3"])
    end = F.add_months(F.lit(str(persona_end_date)), -3)
    pooled = new.filter(F.col("observation_date") <= end).select(*GRAIN, *strong)
    outcome = pooled.join(_paid_due(pooled, ledger), list(GRAIN), "left")
    rates = (
        outcome.groupBy("f1", "f2", "f3")
        .agg(F.count(F.lit(1)).alias("n"), F.avg("paid_due").alias("rate"))
        .orderBy("f1", "f2", "f3")
        .collect()
    )
    lines += ["  F1 | F2 | F3 strong, pooled months with 3 months after: n, paid a due"]
    lines += [
        f"    {r['f1']} | {r['f2']} | {r['f3']}: {r['n']}, "
        f"{100 * (r['rate'] or 0):.1f}%"
        for r in rates
    ] or ["    none"]
    _block("B25 A1", model_id, lines)


# ── Card parent link (Q-S6-14) ────────────────────────────────────────────────


def _share(part: int, whole: int) -> str:
    return f"{part} ({100 * part / max(whole, 1):.1f}%)"


def compare_parent_link(  # pylint: disable=too-many-locals
    contracts: DataFrame,
    month_end: DataFrame,
    obs_base: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 PARENT LINK``: what ``parent_contract_id`` links on the card contracts."""
    c = contracts.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("contract_id").cast("string").alias("contract_id"),
        F.col("parent_contract_id").cast("string").alias("parent_id"),
    ).localCheckpoint()
    n = c.count()
    parents = c.filter(F.col("parent_id").isNotNull()).select(
        F.col("parent_id").alias("contract_id")
    )
    kids = parents.groupBy("contract_id").count()
    bands = F.when(F.col("count") >= 4, "4+").otherwise(F.col("count").cast("string"))
    pairs = c.filter(F.col("parent_id").isNotNull()).join(
        c.select(
            F.col("contract_id").alias("parent_id"), F.col("cif_id").alias("parent_cif")
        ),
        "parent_id",
        "left",
    )
    n_pairs = pairs.count()
    month = F.last_day(F.lit(str(persona_end_date)))
    live = (
        month_end.filter(F.col("month_end") == month)
        .select(F.col("contract_id").cast("string").alias("contract_id"))
        .distinct()
    )
    both_live = pairs.join(live, "contract_id").join(
        live.withColumnRenamed("contract_id", "parent_id"), "parent_id"
    )
    scored = (
        _latest(obs_base, persona_end_date)
        .select(F.col("account_id").cast("string").alias("contract_id"))
        .distinct()
    )
    n_scored = scored.count()
    named = scored.join(parents.distinct(), "contract_id").count()
    with_parent = scored.join(
        c.filter(F.col("parent_id").isNotNull()).select("contract_id"), "contract_id"
    ).count()
    no_parent_row = pairs.filter(F.col("parent_cif").isNull()).count()
    same_cif = pairs.filter(F.col("cif_id") == F.col("parent_cif")).count()
    lines = [
        (
            f"  card contracts {n}; with a parent {_share(n_pairs, n)}; named as a parent "
            f"{_share(kids.count(), n)}"
        ),
        "  children per parent:",
        *_counts(kids.withColumn("children", bands), ["children"]),
        (
            f"  pairs: parent not a card contract {_share(no_parent_row, n_pairs)}; same CIF "
            f"{_share(same_cif, n_pairs)}; both with a month-end row in the latest month "
            f"{_share(both_live.count(), n_pairs)}"
        ),
        (
            f"  scored accounts {n_scored}: named as a parent {_share(named, n_scored)}; "
            f"with a parent {_share(with_parent, n_scored)}"
        ),
    ]
    _block("B25 PARENT LINK", model_id, lines)


# ── Pipeline ──────────────────────────────────────────────────────────────────


def create_pipeline(product: str, parts: list[Pipeline] | None = None) -> Pipeline:
    """The shipped pipelines into ``<name>__b25``, then the comparisons. ``parts``
    replaces the pipelines rerun (a local test runs one axis at a time)."""
    real = sum(parts if parts is not None else _parts(product), Pipeline([]))
    outputs = sorted(real.all_outputs())
    rerun = pipeline(real, outputs={o: f"{o}{NEW}" for o in outputs})
    expected = _expected(product)
    names = [o for o in outputs if expected.get(o) != []]
    common = {"model_id": "params:model_id"}
    end = {**common, "persona_end_date": "params:crx_persona.persona_end_date"}
    nodes = [
        node(
            func=partial(compare_datasets, names=names, expected=expected),
            inputs={
                **common,
                **{f"o{i}": o for i, o in enumerate(names)},
                **{f"n{i}": f"{o}{NEW}" for i, o in enumerate(names)},
            },
            outputs=None,
            name=f"crx_{product}_b25_diff",
            tags=TAGS,
        )
    ]
    p = f"crx_{product}_a3"
    ledger = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}[product]
    if f"{p}_payment_credibility" in outputs:
        nodes.append(
            node(
                func=compare_a3,
                inputs={
                    "old_events": f"{p}_promise_events",
                    "new_events": f"{p}_promise_events{NEW}",
                    "old": f"{p}_payment_credibility",
                    "new": f"{p}_payment_credibility{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a3",
                tags=TAGS,
            )
        )
    if (
        f"crx_{product}_a1_ability" in outputs
        and f"{ledger}{NEW}" in rerun.all_outputs()
    ):
        nodes.append(
            node(
                func=compare_a1,
                inputs={
                    "old": f"crx_{product}_a1_ability",
                    "new": f"crx_{product}_a1_ability{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a1",
                tags=TAGS,
            )
        )
    if product == "cc" and "prm_card_contracts" in outputs:
        nodes.append(
            node(
                func=compare_parent_link,
                inputs={
                    "contracts": f"prm_card_contracts{NEW}",
                    "month_end": f"prm_card_month_end{NEW}",
                    "obs_base": "crx_cc_obs_base",
                    **end,
                },
                outputs=None,
                name="crx_cc_b25_parent_link",
                tags=TAGS,
            )
        )
    return rerun + Pipeline(nodes)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py`
action: replace · base sha256 `00e560b625582b4b405e802b92f87d3ef7bc854d3000111c429611002f7c57a4` · base trailing newline: yes · new sha256 `720b02e7f37cb9a1e9d6394f742532c3d533a015d7066f0cc48898dd0f0d5987` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, SEG_60_180, pit_latest, require_columns, segment

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# No balance snapshot in the observation month means the card stopped reporting; no anchor.
_BALANCE_MAX_AGE_M = 1


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll (S1).

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if segment(model_id) != SEG_60_180:
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_months=_BALANCE_MAX_AGE_M,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
`````

New:

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    SEG_60_180,
    pit_latest,
    require_columns,
    segment,
    string_key,
)

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# No balance snapshot in the observation month: the card stopped reporting, no anchor.
_BALANCE_MAX_AGE_M = 1


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll (S1).

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if segment(model_id) != SEG_60_180:
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        string_key(prm_balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_months=_BALANCE_MAX_AGE_M,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py`
action: replace · base sha256 `eb424eba496165e83e60be411712720dfbb5b3c58c7294b1fb38d16deff439ad` · base trailing newline: yes · new sha256 `d55b035ec45d3680ce65370313918a814ccd3d4c58aaca0add04e338d8b221a9` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A3 sources: statement cycles with one month's due, and card payments."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, string_key
from ..a3_credibility.constants import (
    BUCKET08_BASELINE_MONTHS,
    CYCLE_MAX_DAYS,
    FLOOR_LOOKBACK_DAYS,
)

_LADDER = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]


def _nonzero(col: str):
    """Way4 writes an empty bucket as 0, not NULL."""
    return F.col(col).isNotNull() & (F.col(col) != 0.0)


def _balance_dues(balance: DataFrame) -> DataFrame:
    """``(account_id, cycle_start, billed_amount, due_amount)`` per statement.

    One month's due: the oldest open bucket 07..01, else the minimum due (bucket 08 is
    Way4's accumulator, not one month). Once only bucket 08 holds money, ``due_amount``
    is the average positive minimum due of the 12 months before that point (D-A3-12);
    ``billed_amount`` (Dimension C) has no such fallback.
    """
    rows = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("cycle_start"),
        "minimum_due",
        F.coalesce(*[F.when(_nonzero(c), F.col(c)) for c in _LADDER]).alias(
            "billed_amount"
        ),
        (
            ~F.coalesce(
                *[F.when(_nonzero(c), F.lit(True)) for c in _LADDER], F.lit(False)
            )
            & _nonzero("overdue_bucket_08")
        ).alias("_stagnated"),
    )
    since = (
        rows.where("_stagnated")
        .groupBy("account_id")
        .agg(F.min("cycle_start").alias("_since"))
    )
    recent = Window.partitionBy("account_id").orderBy(F.col("_month").desc())
    baseline = (
        rows.join(since, "account_id")
        .where(_nonzero("minimum_due") & (F.col("cycle_start") < F.col("_since")))
        .groupBy("account_id", F.trunc("cycle_start", "month").alias("_month"))
        .agg(F.avg("minimum_due").alias("_m"))
        .withColumn("_r", F.row_number().over(recent))
        .where(F.col("_r") <= BUCKET08_BASELINE_MONTHS)
        .groupBy("account_id")
        .agg(F.avg("_m").alias("_baseline"))
    )
    return rows.join(baseline, "account_id", "left").select(
        "account_id",
        "cycle_start",
        "billed_amount",
        F.coalesce(
            "billed_amount", F.when(F.col("_stagnated"), F.col("_baseline"))
        ).alias("due_amount"),
    )


def build_cc_a3_dues(
    billing: DataFrame, balance: DataFrame, history_floor_date: str
) -> DataFrame:
    """A3 dues contract per statement cycle (D-A3-15): ``cycle_start`` = the statement,
    ``cycle_end`` = the next one. A cycle longer than 62 days spans missing statements
    and is dropped, as is one starting more than 35 days before the history floor; the
    latest cycle (no next statement yet) has no result and is left out."""
    require_columns(
        billing,
        ["contract_id", "observation_date", "next_billing_date"],
        "crx_cc_billing",
    )
    require_columns(
        balance,
        ["contract_id", "observation_date", "overdue_bucket_08", *_LADDER],
        "crx_cc_balance",
    )
    start, end = F.col("observation_date").cast("date"), F.col(
        "next_billing_date"
    ).cast("date")
    floor = F.date_sub(F.lit(str(history_floor_date)).cast("date"), FLOOR_LOOKBACK_DAYS)
    cycles = (
        billing.where(
            end.isNotNull()
            & (F.datediff(end, start) <= CYCLE_MAX_DAYS)
            & (start >= floor)
        )
        .select(
            string_key(billing, "contract_id").alias("account_id"),
            start.alias("cycle_start"),
            end.alias("cycle_end"),
        )
        .distinct()
    )
    return cycles.join(
        _balance_dues(balance), on=["account_id", "cycle_start"], how="left"
    )


def build_cc_a3_payments(transactions: DataFrame) -> DataFrame:
    """A3 payments contract: card payments (category ``payment``, no post-block fee
    artefacts), dated by banking date."""
    require_columns(
        transactions,
        [
            "contract_id",
            "observation_date",
            "txn_amount_aed",
            "txn_category",
            "is_post_block_x_fee",
        ],
        "crx_cc_transactions",
    )
    day = F.col("observation_date").cast("date")
    return transactions.where(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        string_key(transactions, "contract_id").alias("account_id"),
        day.alias("pay_from"),
        day.alias("pay_date"),
        F.col("txn_amount_aed").cast("double").alias("amount"),
    )
`````

New:

`````python
"""CC A3 sources: the history window of the raw extract, statement cycles with one
month's due, and card payments."""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, string_key
from .._dpd_journey.anchor import episode_start
from ..a3_credibility.constants import HISTORY_MONTHS

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of ladder due averaged (D-A3-12, -31)
_LADDER = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]


def _history_floor(history_floor_date: str) -> Column:
    """The first statement day kept: ``history_floor_date`` less ``FLOOR_LOOKBACK_DAYS``
    (the statement just before the floor)."""
    return F.date_sub(F.lit(str(history_floor_date)).cast("date"), FLOOR_LOOKBACK_DAYS)


def build_cc_acct_windows(
    obs_base: DataFrame, deterioration: DataFrame, history_floor_date: str
) -> DataFrame:
    """``account_id``, ``acct_start``, ``acct_end``: the raw history the CC A3 extracts
    read per account (``crx_cc_raw_extract``).

    ``acct_start``: ``HISTORY_MONTHS`` before the earlier of the account's earliest
    episode start (A4) and its first observation month, never before the history floor;
    ``acct_end``: its last observation date.
    """
    episodes = episode_start(obs_base, deterioration)
    first = (
        obs_base.join(episodes, on=["account_id", "observation_date"], how="left")
        .groupBy("account_id")
        .agg(
            F.least(
                F.min("episode_start"), F.trunc(F.min("observation_date"), "month")
            ).alias("_first"),
            F.max("observation_date").alias("acct_end"),
        )
    )
    return first.select(
        "account_id",
        F.greatest(
            F.add_months(F.col("_first"), -HISTORY_MONTHS),
            _history_floor(history_floor_date),
        ).alias("acct_start"),
        "acct_end",
    )


def _nonzero(col: str) -> Column:
    """Way4 writes an empty bucket as 0, not NULL."""
    return F.col(col).isNotNull() & (F.col(col) != 0.0)


def _balance_dues(balance: DataFrame) -> DataFrame:
    """``(account_id, cycle_start, billed_amount, due_amount)`` per statement.

    ``billed_amount`` (the ladder value): the oldest open bucket 07..01, else the
    minimum due. ``due_amount`` (one month's due) is the ladder value while bucket 08
    (Way4's accumulator, not one month) is empty. On a statement with bucket 08 open it
    is the baseline: the average ladder value of the 12 months before bucket 08 first
    held money, or NULL when there is none (D-A3-12, -31). ``billed_amount``
    (Dimension C) keeps the ladder value.
    """
    billed = F.coalesce(*[F.when(_nonzero(c), F.col(c)) for c in _LADDER])
    rows = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("cycle_start"),
        billed.alias("billed_amount"),
        _nonzero("overdue_bucket_08").alias("_accumulating"),
    )
    rows = rows.withColumn(
        "_since",
        F.min(F.when(F.col("_accumulating"), F.col("cycle_start"))).over(
            Window.partitionBy("account_id")
        ),
    )
    recent = Window.partitionBy("account_id").orderBy(F.col("_month").desc())
    baseline = (
        rows.where(
            F.col("billed_amount").isNotNull()
            & (F.col("cycle_start") < F.col("_since"))
        )
        .groupBy("account_id", F.trunc("cycle_start", "month").alias("_month"))
        .agg(F.avg("billed_amount").alias("_m"))
        .withColumn("_r", F.row_number().over(recent))
        .where(F.col("_r") <= BUCKET08_BASELINE_MONTHS)
        .groupBy("account_id")
        .agg(F.avg("_m").alias("_baseline"))
    )
    return rows.join(baseline, "account_id", "left").select(
        "account_id",
        "cycle_start",
        "billed_amount",
        F.when(F.col("_accumulating"), F.col("_baseline"))
        .otherwise(F.col("billed_amount"))
        .alias("due_amount"),
    )


def build_cc_a3_dues(
    billing: DataFrame, balance: DataFrame, history_floor_date: str
) -> DataFrame:
    """A3 dues contract per statement cycle (D-A3-15): ``cycle_start`` = the statement,
    ``cycle_end`` = the next one. A cycle longer than 62 days spans missing statements
    and is dropped, as is one starting more than 35 days before the history floor; the
    latest cycle (no next statement yet) has no result and is left out."""
    require_columns(
        billing,
        ["contract_id", "observation_date", "next_billing_date"],
        "crx_cc_billing",
    )
    require_columns(
        balance,
        ["contract_id", "observation_date", "overdue_bucket_08", *_LADDER],
        "crx_cc_balance",
    )
    start = F.col("observation_date").cast("date")
    end = F.col("next_billing_date").cast("date")
    floor = _history_floor(history_floor_date)
    cycles = (
        billing.where(
            end.isNotNull()
            & (F.datediff(end, start) <= CYCLE_MAX_DAYS)
            & (start >= floor)
        )
        .select(
            string_key(billing, "contract_id").alias("account_id"),
            start.alias("cycle_start"),
            end.alias("cycle_end"),
        )
        .distinct()
    )
    return cycles.join(
        _balance_dues(balance), on=["account_id", "cycle_start"], how="left"
    )


def build_cc_a3_payments(transactions: DataFrame) -> DataFrame:
    """A3 payments contract: card payments (category ``payment``, no post-block fee
    artefacts), dated by banking date."""
    require_columns(
        transactions,
        [
            "contract_id",
            "observation_date",
            "txn_amount_aed",
            "txn_category",
            "is_post_block_x_fee",
        ],
        "crx_cc_transactions",
    )
    day = F.col("observation_date").cast("date")
    return transactions.where(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        string_key(transactions, "contract_id").alias("account_id"),
        day.alias("pay_from"),
        day.alias("pay_date"),
        F.col("txn_amount_aed").cast("double").alias("amount"),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/__init__.py`
action: replace · base sha256 `501be0968405dd675c5db9d357a1f88854f359f13057f4fe47cfc43ac292d044` · base trailing newline: yes · new sha256 `d1dfdda76350fd5f81fa6a679dda796e506c389728130998087d48ef084bcfba` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T04c — CRX CC Raw Extract pipeline.

Promotes the T0-scoped raw DDI extracts (previously private helpers inside
T04b) to persisted intermediate catalog datasets consumed by T04b, T05, and T06.

Assets produced:
    crx_cc_transactions : CC transaction history, T0-scoped, enriched schema
    crx_cc_limits       : CC credit-limit snapshots, T0-scoped
    crx_cc_balance      : CC total_due billing history, T0-scoped
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC raw extracts for A3: window-scoped Way4 transactions, balance and billing, and the
credit-limit snapshots (``nodes.py``)."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/_window_utils.py`
action: replace · base sha256 `d4be8f3a56b79c62b9cf2dfe16c64003aa956208d46da233ca62264bef0b36bd` · base trailing newline: yes · new sha256 `4eee9eb5160239be1b4cccb7ae88af095ef347798d1831fd5691cdbe4a822754` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared per-account windowing helpers for cc_raw_extract's nodes.

Factors out two blocks that were duplicated near-verbatim across
build_cc_transactions / build_cc_balance / build_cc_billing (and, for the
join+filter mechanics only, build_cc_limits) — pure extraction, no behavior
change (2026-10-21).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.utils.config import EDP_LOAD_DATE_BUFFER_MONTHS


def prune_by_edp_load_date(raw_df: DataFrame, acct_windows: DataFrame) -> DataFrame:
    """Partition-prune raw_df on edp_load_date to the global acct window ± buffer.

    acct_windows: any DataFrame with acct_start/acct_end columns (e.g.
    crx_cc_acct_windows). The global [min(acct_start), max(acct_end)] bound is
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS before filtering raw_df's
    edp_load_date column — see build_cc_transactions' docstring for why the
    buffer is needed (absorbs load-date lag; cc_spine has no backward lookback
    of its own). This is a superset filter only — callers still apply their
    own per-account date-range filter afterwards (see scope_to_acct_window).
    """
    window_lo, window_hi = acct_windows.agg(
        F.min("acct_start"), F.max("acct_end")
    ).first()
    load_date_lo = F.add_months(F.lit(window_lo), -EDP_LOAD_DATE_BUFFER_MONTHS)
    load_date_hi = F.add_months(F.lit(window_hi), EDP_LOAD_DATE_BUFFER_MONTHS)
    return raw_df.where(
        F.col("edp_load_date").cast(DateType()).between(load_date_lo, load_date_hi)
    )


def scope_to_acct_window(
    raw_df: DataFrame, acct_windows: DataFrame, date_col: str
) -> DataFrame:
    """Cast contract_idt to long, inner-join to acct_windows, filter date_col
    to [acct_start, acct_end].

    acct_windows: a DataFrame keyed by contract_idt with acct_start/acct_end
    columns — either crx_cc_acct_windows (re-keyed via _as_contract_windows)
    or build_cc_limits' own locally-built, T0-only window. date_col is the
    only thing that varies across call sites ("banking_date" or
    "billing_date").
    """
    return (
        raw_df.withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col(date_col).cast(DateType()) >= F.col("acct_start"))
            & (F.col(date_col).cast(DateType()) <= F.col("acct_end"))
        )
    )
`````

New:

`````python
"""Per-account windowing shared by the ``cc_raw_extract`` nodes: partition pruning on
``edp_load_date`` and the per-account date scope."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.utils.config import EDP_LOAD_DATE_BUFFER_MONTHS


def prune_by_edp_load_date(raw_df: DataFrame, acct_windows: DataFrame) -> DataFrame:
    """``raw_df`` pruned on ``edp_load_date`` (the Hive partition column) to the global
    [min(acct_start), max(acct_end)] of ``acct_windows`` widened by
    ``EDP_LOAD_DATE_BUFFER_MONTHS``. The buffer absorbs the lag between an event date
    and its load-date partition; ``cc_spine`` has no backward lookback of its own. A
    superset filter: callers still scope each account to its own window with
    ``scope_to_acct_window``."""
    window_lo, window_hi = acct_windows.agg(
        F.min("acct_start"), F.max("acct_end")
    ).first()
    load_date_lo = F.add_months(F.lit(window_lo), -EDP_LOAD_DATE_BUFFER_MONTHS)
    load_date_hi = F.add_months(F.lit(window_hi), EDP_LOAD_DATE_BUFFER_MONTHS)
    return raw_df.where(
        F.col("edp_load_date").cast(DateType()).between(load_date_lo, load_date_hi)
    )


def scope_to_acct_window(
    raw_df: DataFrame, acct_windows: DataFrame, date_col: str
) -> DataFrame:
    """``raw_df`` with ``contract_idt`` cast to long (the raw key is a double), joined
    to ``acct_windows`` (keyed by ``contract_idt``, with ``acct_start`` / ``acct_end``)
    and cut to ``date_col`` within [acct_start, acct_end]."""
    return (
        raw_df.withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col(date_col).cast(DateType()) >= F.col("acct_start"))
            & (F.col(date_col).cast(DateType()) <= F.col("acct_end"))
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py`
action: replace · base sha256 `cfc2c63b81b0d5084c12b45e1ea0516185dffa2f74ecacb123597845ad80f10c` · base trailing newline: yes · new sha256 `985def5b2e78c79474f7d5b53eadd17d176e76a1652707cd9cf7d360b9352de6` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CRX CC raw extract nodes: window-scoped Way4 extracts for A3.

# pylint: disable=too-many-locals

    build_cc_acct_windows : per-account [acct_start, acct_end] window from the A3
                            episode anchor (A4) and the observation rows; persisted
                            once, read by the three extracts below.
    build_cc_transactions : window-scoped transaction history with the prm_cc
                            derivations (A3 payments).
    build_cc_limits       : credit-limit snapshots pivoted by type_code, on its own
                            spell-table window (no persona reader at present).
    build_cc_balance      : window-scoped minimum_due / overdue buckets / total_due
                            (A3 dues).
    build_cc_billing      : window-scoped billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).

Quality filter (transactions + limits): primary_entry_idt != 0, org == 100.
Type cast: contract_idt (double -> long) at the DDI raw boundary.
"""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import (
    derive_billing_amounts,
    derive_overdue_buckets,
)
from enbd_collections.nodes.utils.config import (
    POST_BLOCK_X_SENTINEL_DATE,
    TXN_CATEGORIES,
)
from enbd_collections.pipelines.crx_persona._dpd_journey.anchor import episode_start
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def build_cc_acct_windows(
    crx_cc_obs_base: DataFrame,
    crx_cc_a4_deterioration: DataFrame,
    history_floor_date: str,
) -> DataFrame:
    """Shared per-account [acct_start, acct_end] window for the A3 extracts.

    acct_start covers 12 months plus one cycle before the earliest episode start the
    account's observation rows have (A3 Dimension C, D-A3-2), and at least 13 months
    before its first observation (A3 Dimensions A and B); never before
    history_floor_date minus 35 days (the statement just before the floor).
    acct_end = the account's last observation date.

    Persisted once and consumed by build_cc_transactions, build_cc_balance and
    build_cc_billing.

    Args:
        crx_cc_obs_base: account_id, observation_date, cif_id.
        crx_cc_a4_deterioration: the A4 rows the episode anchor is read from.
        history_floor_date: ISO date (params:cc_a3_history_floor_date).

    Returns:
        DataFrame with columns (account_id, acct_start, acct_end).
    """
    episodes = episode_start(crx_cc_obs_base, crx_cc_a4_deterioration)
    first = (
        crx_cc_obs_base.join(
            episodes, on=["account_id", "observation_date"], how="left"
        )
        .groupBy("account_id")
        .agg(
            F.least(
                F.min("episode_start"), F.trunc(F.min("observation_date"), "month")
            ).alias("_first"),
            F.max("observation_date").alias("acct_end"),
        )
    )
    floor = F.date_sub(F.lit(str(history_floor_date)).cast(DateType()), 35)
    return first.select(
        "account_id",
        F.greatest(F.add_months(F.col("_first"), -13), floor).alias("acct_start"),
        "acct_end",
    )


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped CC transaction history with enriched schema.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows).
    Partition pruning: raw_transaction is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a transaction happens (banking_date) and when it
    lands in its edp_load_date partition. Unlike stg_transaction.build() (whose
    spine, data_spine_contracts_way4, already bakes the lookback into
    observation_date, so it needs no extra buffer), cc_spine has no backward
    lookback at all — crx_cc_acct_windows builds that bound itself, so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.
    Quality filters: primary_entry_idt != 0, org == 100 (same as stg_transaction.build()).
    Replicates prm_cc.build_transaction() derivation logic for txn_category and
    is_international, and stg_transaction.build()'s is_post_block_x_fee sentinel-fee
    derivation (Block-W fee-accrual artifacts that must not be mistaken for real
    post-delinquency payment activity).

    Args:
        raw_transaction:     Raw Way4 transaction table (DDI-backed). Long history.
                             Required cols: primary_entry_idt, org, contract_idt,
                             banking_date, edp_load_date, settl_amount, direction,
                             txn_code, txn_description, add_info, trans_mcc,
                             trans_date, card_idt, service_class.
        crx_cc_acct_windows: T04c — build_cc_acct_windows output.
                             Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), direction (int),
            txn_amount_aed (double), txn_description (string),
            merchant_category_code (int), is_international (int),
            txn_category (string), is_post_block_x_fee (int)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        # Base quality filters (same as stg_transaction.build())
        .filter(F.col("primary_entry_idt") != 0).filter(F.col("org") == 100)
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # Derive txn_category from txn_code (replicates prm_cc.build_transaction logic).
    # Default NULL — unrecognized codes excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # Derive is_international from DOMESTIC flag in add_info JSON
    # (replicates prm_cc.build_transaction logic).
    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # Derive is_post_block_x_fee (replicates stg_transaction.build()'s sentinel-fee
    # derivation) — system-generated fee-accrual events posted after collector
    # Block W, flagged so A3 Dimension B/C never count them as a real payment.
    sentinel = F.lit(POST_BLOCK_X_SENTINEL_DATE).cast(DateType())
    df = df.withColumn(
        "is_post_block_x_fee",
        F.when(
            (F.col("trans_date").cast(DateType()) == sentinel)
            & (F.col("card_idt") == 0)
            & (F.col("settl_amount") == 0)
            & (F.col("service_class") == "I"),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
        F.col("is_post_block_x_fee").cast("int"),
    ).distinct()


def build_cc_limits(
    raw_stg_limit: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """Extract T0-anchored CC credit-limit snapshots, pivoted by type_code.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Pivot logic replicates stg_limit.build() but uses type_code FIN_LIMIT and
    AVAILABLE only (ADD_LIMIT excluded; not needed for util_ratio computation).

    Deliberately does NOT consume crx_cc_acct_windows — that window's forward
    edge is cc_spine-anchored (extends past T0), which this function does not
    need (see module docstring).

    Args:
        raw_stg_limit:       Raw Way4 limit table (DDI-backed).
                             Required cols: contract_idt, banking_date,
                             type_code, amount.
        crx_cc_spell_table:  T03 output. Used for per-account T0 window.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date),
            credit_limit (double), available_limit (double)
    """
    # Excludes both censored subtypes — see build_cc_transactions Step 0 comment.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)

    acct_windows = (
        spell.groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("acct_start"),
            F.trunc(F.max("t0"), "month").alias("acct_end"),
        )
        .select(
            F.col("account_id").alias("contract_idt"),
            "acct_start",
            "acct_end",
        )
    )

    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join). This T0-only
    # acct_windows is the one built just above, NOT crx_cc_acct_windows —
    # see module/function docstring for why this window is deliberately kept
    # separate.
    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped
        # Only limit types needed for util_ratio: FIN_LIMIT (credit_limit) + AVAILABLE
        .filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # Pivot — max() is deterministic when multiple rows exist for same key
        # (highest approved limit wins; highest available = least alarming)
        .groupBy("contract_idt", "banking_date")
        .pivot("type_code", ["FIN_LIMIT", "AVAILABLE"])
        .agg(F.max("amount"))
        .withColumnRenamed("FIN_LIMIT", "credit_limit")
        .withColumnRenamed("AVAILABLE", "available_limit")
    )

    return pivoted.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("credit_limit").cast("double"),
        F.col("available_limit").cast("double"),
    )


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped minimum_due/stmt_balance/total_due/overdue-bucket history.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge.

    Reuses prm_cc.derive_billing_amounts() and prm_cc.derive_overdue_buckets() —
    the authoritative, production-verified derivations — rather than hand-rolling
    the pivots here, per the standing team decision to never reverse-engineer
    billing amounts from raw stg_balance. raw_stg_balance already carries its own
    native banking_date column (the daily snapshot grain both derive_* functions
    group by) distinct from billing_date — scoping/output use banking_date
    directly rather than aliasing billing_date onto it.

    Way4 stores credit balances as negative; derive_billing_amounts/
    derive_overdue_buckets flip the sign.

    Partition pruning: raw_stg_balance is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a balance snapshot is taken (banking_date) and
    when it lands in its edp_load_date partition. cc_spine has no backward
    lookback at all (unlike data_spine_contracts_way4, which already bakes it
    into observation_date for the credit_card_way4 staging layer), so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.

    Args:
        raw_stg_balance:       Raw Way4 balance table (DDI-backed).
                               Required cols: contract_idt, banking_date,
                               edp_load_date, account_group_id, balance.
        raw_stg_account_group: Dimension table mapping account_group_id →
                               type_code / class_code.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), minimum_due (double),
            stmt_balance (double), total_due (double),
            overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_stg_balance, crx_cc_acct_windows).withColumn(
            "banking_date", F.col("banking_date").cast(DateType())
        )
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    scoped_balance = scope_to_acct_window(scoped_balance, acct_windows, "banking_date")

    billing_amounts = derive_billing_amounts(scoped_balance, raw_stg_account_group)
    overdue_buckets = derive_overdue_buckets(scoped_balance, raw_stg_account_group)

    combined = billing_amounts.join(
        overdue_buckets, on=["contract_idt", "banking_date"], how="left"
    )

    select_cols = [
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("minimum_due").cast("double"),
        F.col("stmt_balance").cast("double"),
        F.col("total_due").cast("double"),
    ] + [
        F.col(f"overdue_ovd_{i:02d}").cast("double").alias(f"overdue_bucket_{i:02d}")
        for i in range(1, 9)
    ]

    return combined.select(*select_cols)


def build_cc_billing(
    raw_stg_billing: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped billing-cycle header: billing_date, due_date,
    next_billing_date, dlq_level_m.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge. This is the
    primitive A3 Dimension B/C's payment-attribution helper
    (cc_a3_payment_credibility._signals_common.attribute_payments_to_billing_cycles)
    is built on.

    next_billing_date = F.lead(billing_date) per contract. A payment belongs to
    the cycle (billing_date, due_date) iff billing_date < banking_date <=
    next_billing_date — NOT billing_date < banking_date <= due_date. due_date is
    ~billing_date+25d while the next statement cuts ~billing_date+30d, leaving a
    ~5-6 day dead zone where late payments (common in practice) would otherwise
    be dropped or misattributed to the wrong cycle — found and fixed in the
    exploratory notebook (notebooks/data_engineering/crx_persona/
    cc_account_payment_profiling.ipynb). next_billing_date is NULL for the most
    recent cycle per contract — treated as open-ended by the attribution helper.

    dlq_level_m is Way4's own per-cycle DLQ bucket (0-9), extracted from the
    add_info KV field's BS_PMT_CYCLE_DUE= key — the identical extraction
    nodes/spine/cc_way4/spine_builders.py uses to build cc_spine's
    dlq_bucket_from_hist, so this is the same ground truth the rest of the
    business already treats as authoritative, not a reconstruction from
    crx_cc_balance's overdue buckets. [CONFIRM]: BS_PMT_CYCLE_DUE is
    sometimes blank/missing in add_info (seen in sample data) — regexp_extract
    then casts to NULL, same as spine_builders.py's own behavior; no fallback
    is applied. Consumed by build_a3_payment_cycles for the DPD-bucket-based
    alternative to Dimension B/C's payment-cycle method (see
    cc_a3_payment_credibility.constants._DLQ_LEVEL_SATURATED).

    Partition pruning: raw_stg_billing is filtered on edp_load_date to the
    global [min(acct_start), max(acct_end)] bound (from crx_cc_acct_windows)
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS (12 months), before the
    per-account join — same rationale as build_cc_transactions/build_cc_balance
    (cc_spine has no backward lookback of its own).

    Args:
        raw_stg_billing:       Raw Way4 billing table (DDI-backed).
                               Required cols: contract_idt, billing_date,
                               edp_load_date, due_date, add_info.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date, = billing_date),
            due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    # Partition prune on edp_load_date before the join (see docstring), then
    # scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    pruned = prune_by_edp_load_date(raw_stg_billing, crx_cc_acct_windows)
    scoped = (
        scope_to_acct_window(pruned, acct_windows, "billing_date")
        .withColumn("billing_date", F.col("billing_date").cast(DateType()))
        .withColumn("due_date", F.col("due_date").cast(DateType()))
        .withColumn(
            "dlq_level_m",
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1).cast(
                "int"
            ),
        )
        .select("contract_idt", "billing_date", "due_date", "dlq_level_m")
        .distinct()
    )

    next_billing_window = Window.partitionBy("contract_idt").orderBy("billing_date")
    with_next = scoped.withColumn(
        "next_billing_date", F.lead("billing_date").over(next_billing_window)
    )

    return with_next.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("billing_date").alias("observation_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
        F.col("dlq_level_m"),
    )
`````

New:

`````python
"""CC raw extract nodes: Way4 extracts scoped to each account's window.

    build_cc_transactions : transaction history with the ``prm_cc`` derivations (A3
                            payments).
    build_cc_balance      : minimum_due / overdue buckets / total_due (A3 dues).
    build_cc_billing      : billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).
    build_cc_limits       : credit-limit snapshots pivoted by type_code, on its own
                            spell-table window (no persona reader at present).

The first three read ``crx_cc_acct_windows`` (``build_cc_acct_windows`` in
``cc_a3_payment_credibility.nodes``) and prune raw partitions with
``_window_utils.prune_by_edp_load_date``. ``contract_idt`` is cast double -> long at the
raw boundary; transactions keep primary_entry_idt != 0 and org == 100.
"""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import (
    derive_billing_amounts,
    derive_overdue_buckets,
)
from enbd_collections.nodes.utils.config import (
    POST_BLOCK_X_SENTINEL_DATE,
    TXN_CATEGORIES,
)
from enbd_collections.pipelines.crx_persona._common import require_columns
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    require_columns(
        acct_windows, ["account_id", "acct_start", "acct_end"], "crx_cc_acct_windows"
    )
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC transactions in each account's window, with ``txn_category`` (``prm_cc``'s
    ``TXN_CATEGORIES`` by ``txn_code``; NULL for an unrecognised code),
    ``is_international`` (``DOMESTIC=N`` in ``add_info``) and ``is_post_block_x_fee``
    (the Block-W fee-accrual artefacts, as in ``stg_transaction.build()``, which A3 must
    not read as payments).

    Returns::

        contract_id (long), observation_date (date, banking date), direction (int),
        txn_amount_aed (double), txn_description (string),
        merchant_category_code (int), is_international (int),
        txn_category (string), is_post_block_x_fee (int)
    """
    require_columns(
        raw_transaction,
        [
            "primary_entry_idt",
            "org",
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "settl_amount",
            "direction",
            "txn_code",
            "txn_description",
            "add_info",
            "trans_mcc",
            "trans_date",
            "card_idt",
            "service_class",
        ],
        "raw_transaction",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        .filter(F.col("primary_entry_idt") != 0)
        .filter(F.col("org") == 100)
    )
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # NULL for unrecognised codes: excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # System-generated fee accruals posted after collector Block W carry a sentinel
    # trans_date; flagged so A3 Dimension B/C never count them as a payment.
    sentinel = F.lit(POST_BLOCK_X_SENTINEL_DATE).cast(DateType())
    df = df.withColumn(
        "is_post_block_x_fee",
        F.when(
            (F.col("trans_date").cast(DateType()) == sentinel)
            & (F.col("card_idt") == 0)
            & (F.col("settl_amount") == 0)
            & (F.col("service_class") == "I"),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
        F.col("is_post_block_x_fee").cast("int"),
    ).distinct()


def build_cc_limits(
    raw_stg_limit: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """CC credit-limit snapshots (``FIN_LIMIT`` and ``AVAILABLE`` pivoted by type_code)
    in the window [min(t0) − 12 months, max(t0)] of each account's non-censored spells;
    it does not read ``crx_cc_acct_windows``, whose forward edge is the observation
    base.

    Returns::

        contract_id (long), observation_date (date),
        credit_limit (double), available_limit (double)
    """
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)

    acct_windows = (
        spell.groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("acct_start"),
            F.trunc(F.max("t0"), "month").alias("acct_end"),
        )
        .select(
            F.col("account_id").alias("contract_idt"),
            "acct_start",
            "acct_end",
        )
    )

    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped.filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # max(): the highest limit and the highest available amount win on a tie
        .groupBy("contract_idt", "banking_date")
        .pivot("type_code", ["FIN_LIMIT", "AVAILABLE"])
        .agg(F.max("amount"))
        .withColumnRenamed("FIN_LIMIT", "credit_limit")
        .withColumnRenamed("AVAILABLE", "available_limit")
    )

    return pivoted.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("credit_limit").cast("double"),
        F.col("available_limit").cast("double"),
    )


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC balance history in each account's window: the billing amounts and overdue
    buckets of ``prm_cc.derive_billing_amounts`` / ``derive_overdue_buckets`` per
    banking date (Way4 stores credit balances as negative; both flip the sign).

    Returns::

        contract_id (long), observation_date (date), minimum_due (double),
        stmt_balance (double), total_due (double),
        overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    require_columns(
        raw_stg_balance,
        ["contract_idt", "banking_date", "edp_load_date"],
        "raw_stg_balance",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = prune_by_edp_load_date(
        raw_stg_balance, crx_cc_acct_windows
    ).withColumn("banking_date", F.col("banking_date").cast(DateType()))
    scoped_balance = scope_to_acct_window(scoped_balance, acct_windows, "banking_date")

    billing_amounts = derive_billing_amounts(scoped_balance, raw_stg_account_group)
    overdue_buckets = derive_overdue_buckets(scoped_balance, raw_stg_account_group)

    combined = billing_amounts.join(
        overdue_buckets, on=["contract_idt", "banking_date"], how="left"
    )

    select_cols = [
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("minimum_due").cast("double"),
        F.col("stmt_balance").cast("double"),
        F.col("total_due").cast("double"),
    ] + [
        F.col(f"overdue_ovd_{i:02d}").cast("double").alias(f"overdue_bucket_{i:02d}")
        for i in range(1, 9)
    ]

    return combined.select(*select_cols)


def build_cc_billing(
    raw_stg_billing: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC billing-cycle headers in each account's window. ``next_billing_date`` is the
    next statement of the contract (NULL for its latest cycle). A payment belongs to the
    cycle ``(billing_date, next_billing_date]``, not ``(billing_date, due_date]``: the
    due date falls about 5 days before the next statement, and late payments would
    otherwise be dropped. ``dlq_level_m`` is Way4's per-cycle bucket
    (``BS_PMT_CYCLE_DUE`` in ``add_info``; NULL when blank).

    Returns::

        contract_id (long), observation_date (date, = billing_date),
        due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    require_columns(
        raw_stg_billing,
        ["contract_idt", "billing_date", "edp_load_date", "due_date", "add_info"],
        "raw_stg_billing",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    pruned = prune_by_edp_load_date(raw_stg_billing, crx_cc_acct_windows)
    scoped = (
        scope_to_acct_window(pruned, acct_windows, "billing_date")
        .withColumn("billing_date", F.col("billing_date").cast(DateType()))
        .withColumn("due_date", F.col("due_date").cast(DateType()))
        .withColumn(
            "dlq_level_m",
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1).cast(
                "int"
            ),
        )
        .select("contract_idt", "billing_date", "due_date", "dlq_level_m")
        .distinct()
    )

    next_billing_window = Window.partitionBy("contract_idt").orderBy("billing_date")
    with_next = scoped.withColumn(
        "next_billing_date", F.lead("billing_date").over(next_billing_window)
    )

    return with_next.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("billing_date").alias("observation_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
        F.col("dlq_level_m"),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py`
action: replace · base sha256 `26866762bbd0f8125a23ea96b0c9d1f91a080d5e38004237d4ed11d41b6122b1` · base trailing newline: yes · new sha256 `292e6baa67bcadd7652a16056abf0cbbe3bf5593d20a2c95f75960bad477bb2f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CRX CC raw DDI extract (5 intermediate datasets) for A3.

build_cc_acct_windows reads the obs base and A4 (the episode anchor), so this runs
after crx_cc_a4_deterioration and before crx_cc_a3_payment_credibility. The three A3
extracts (transactions, balance, billing) read its window; build_cc_limits keeps its own
spell-table window.

Run with:
    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_cc_acct_windows,
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Five-node pipeline: build window-scoped CC raw extract intermediates."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs=[
                    "crx_cc_obs_base",
                    "crx_cc_a4_deterioration",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs=["raw_transaction", "crx_cc_acct_windows"],
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs=["raw_stg_limit", "crx_cc_spell_table"],
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs=[
                    "raw_stg_balance",
                    "raw_stg_account_group",
                    "crx_cc_acct_windows",
                ],
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs=["raw_stg_billing", "crx_cc_acct_windows"],
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: the CC raw extract for A3.

``build_cc_acct_windows`` reads the obs base and A4 (the episode anchor), so this runs
after ``crx_cc_a4_deterioration`` and before ``crx_cc_a3_payment_credibility``. The
transactions, balance and billing extracts read its windows; ``build_cc_limits`` keeps
its own spell-table window.

    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from ..cc_a3_payment_credibility.nodes import build_cc_acct_windows
from .nodes import (
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The account windows and the four extracts."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs={
                    "obs_base": "crx_cc_obs_base",
                    "deterioration": "crx_cc_a4_deterioration",
                    "history_floor_date": "params:cc_a3_history_floor_date",
                },
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs={
                    "raw_transaction": "raw_transaction",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs={
                    "raw_stg_limit": "raw_stg_limit",
                    "crx_cc_spell_table": "crx_cc_spell_table",
                },
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs={
                    "raw_stg_balance": "raw_stg_balance",
                    "raw_stg_account_group": "raw_stg_account_group",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs={
                    "raw_stg_billing": "raw_stg_billing",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py`
action: replace · base sha256 `23f671214c3dcdf1de701638f0f8c80ed854dde309e093e49df1184dbd1a2f78` · base trailing newline: yes · new sha256 `58fe7c566d4c21bdc9faf434c667db73ed4a23f3a5d69081b841dce54e4ededa` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, lookback_floor, pit_latest, require_columns

# int_loan_master is a month-end snapshot; none in the observation month means no anchor.
_LOAN_MAX_AGE_M = 1


def build_rl_liquidity_anchor(
    obs_base: DataFrame, int_loan_master: DataFrame
) -> DataFrame:
    """One EMI (S1): ``installment_due_amount`` on the loan's snapshot in the
    observation month. NULL (flat floors) when the snapshot is missing or the EMI is not
    positive.
    """
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "installment_due_amount"],
        "int_loan_master",
    )
    since = lookback_floor(obs_base, _LOAN_MAX_AGE_M)
    src = int_loan_master.filter(F.col("observation_date") >= F.lit(since)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("installment_due_amount").cast("double").alias("emi"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["emi"],
        inclusive=True,
        max_age_months=_LOAN_MAX_AGE_M,
    )
    return latest.select(
        *GRAIN, F.when(F.col("emi") > 0, F.col("emi")).alias("liquidity_anchor_amt")
    )
`````

New:

`````python
"""RL-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns, string_key
from ..a1_ability.signals import persona_floor

# int_loan_master is a month-end snapshot; none in the observation month: no anchor.
_LOAN_MAX_AGE_M = 1


def build_rl_liquidity_anchor(
    obs_base: DataFrame, int_loan_master: DataFrame, crx_persona: dict
) -> DataFrame:
    """One EMI (S1): ``installment_due_amount`` on the loan's snapshot in the
    observation month. NULL (flat floors) when the snapshot is missing or the EMI is not
    positive.
    """
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "installment_due_amount"],
        "int_loan_master",
    )
    since = persona_floor(crx_persona, _LOAN_MAX_AGE_M)
    src = int_loan_master.filter(F.col("observation_date") >= F.lit(since)).select(
        string_key(int_loan_master).alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("installment_due_amount").cast("double").alias("emi"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["emi"],
        inclusive=True,
        max_age_months=_LOAN_MAX_AGE_M,
    )
    return latest.select(
        *GRAIN, F.when(F.col("emi") > 0, F.col("emi")).alias("liquidity_anchor_amt")
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `0971a2ae70291a54efd81cc964cbb8c1eadb599b9c5c726a17f9165895090881` · base trailing newline: yes · new sha256 `5f769105f6cc65580733b445eb54fd09a675485f359537ae8e41512c2f1da47f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_rl_liquidity_anchor

_ANCHOR = node(
    func=build_rl_liquidity_anchor,
    inputs={"obs_base": "crx_rl_obs_base", "int_loan_master": "int_loan_master"},
    outputs="crx_rl_a1_liquidity_anchor",
    name="build_crx_rl_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability", **kwargs
) -> Pipeline:
    """The RL A1 axis written to ``output``."""
    return create_a1_pipeline("rl", output, _ANCHOR)
`````

New:

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_rl_liquidity_anchor

_ANCHOR = node(
    func=build_rl_liquidity_anchor,
    inputs={
        "obs_base": "crx_rl_obs_base",
        "int_loan_master": "int_loan_master",
        "crx_persona": "params:crx_persona",
    },
    outputs="crx_rl_a1_liquidity_anchor",
    name="build_crx_rl_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability", **kwargs
) -> Pipeline:
    """The RL A1 axis written to ``output``."""
    return create_a1_pipeline("rl", output, _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/scoring_engine.py`
action: replace · base sha256 `f175e335a6844f25825a8c30139c0c2ff4dc8b1745f8afd22e0e440985dd901e` · base trailing newline: yes · new sha256 `633d252666b19f28819b2c3eaf9bf69e63d96f795d65a216a4b008bbb3769969` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Points -> state scoring shared by the axes (A1; A3 next). An axis declares a
``Scorecard`` (dimensions with points per level, thresholds, overrides, state labels)
and builds its own level columns; ``Scorecard.score`` adds points, state, the override
that fired and the reason. Imported by the axes; not run on its own."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

DEMOTE, CAP, FORCE = "demote", "cap", "force"  # Override modes
RUNGS = ("low", "moderate", "high")
LOW, MOD, HIGH = range(len(RUNGS))  # rung indices


@dataclass(frozen=True)
class Dimension:
    """A scored dimension: its ``level`` column, the points per level (others 0; may be
    negative) and the ``silent`` levels that mean "no evidence" (the Unknown gate)."""

    name: str
    level: str
    points: Mapping[str, int]
    silent: tuple[str, ...] = ("none",)


@dataclass(frozen=True)
class Override:
    """A boolean ``flag`` column that, when true, moves the state: ``DEMOTE`` one rung
    (never below Low), ``CAP`` at rung ``to``, or ``FORCE`` to rung ``to``."""

    name: str
    flag: str
    mode: str = DEMOTE
    to: str = "low"


@dataclass(frozen=True)
class Scorecard:  # pylint: disable=too-many-instance-attributes,too-many-locals
    """Points over ``dimensions`` -> High / Moderate / Low, overrides, an Unknown gate.

    Rungs from the points total (``high_from`` / ``moderate_from``, inclusive); High
    also needs ``high_min_dimensions`` dimensions with points, one in ``high_current``
    if given, else Moderate. The first override whose flag is true, in declared order,
    moves the rung (no stacking; a NULL flag does not fire). Unknown: every level silent
    or NULL, no override, and ``unknown_also``. ``labels``: rung or "unknown" -> value.
    """

    prefix: str
    dimensions: tuple[Dimension, ...]
    labels: Mapping[str, str]
    high_from: int
    moderate_from: int
    overrides: tuple[Override, ...] = ()
    high_min_dimensions: int = 0
    high_current: tuple[str, ...] = ()

    def score(self, df: DataFrame, unknown_also: Column | None = None) -> DataFrame:
        """``df`` + ``<prefix>_<dimension>_points``, ``_points_total``, ``_state``,
        ``_override`` (the one that fired), ``_reason`` (it, else the top dimension)."""
        p = self.prefix
        pts = {
            d.name: F.coalesce(state_label(d.level, d.points), F.lit(0))
            for d in self.dimensions
        }
        total = sum(pts.values())
        scored = sum((c > 0).cast("int") for c in pts.values())
        high = (total >= self.high_from) & (scored >= self.high_min_dimensions)
        if self.high_current:
            high &= F.array_max(F.array(*[pts[n] for n in self.high_current])) > 0
        rung = F.when(high, HIGH).when(total >= self.moderate_from, MOD).otherwise(LOW)
        fired = F.coalesce(
            *[F.when(F.col(o.flag), F.lit(o.name)) for o in self.overrides],
            F.lit(None).cast("string"),
        )
        for o in self.overrides:
            to = F.lit(RUNGS.index(o.to))
            moved = {DEMOTE: F.greatest(rung - 1, F.lit(LOW)), CAP: F.least(rung, to)}
            rung = F.when(fired == o.name, {**moved, FORCE: to}[o.mode]).otherwise(rung)
        unknown = F.lit(True) if unknown_also is None else unknown_also
        unknown &= fired.isNull()
        for d in self.dimensions:
            unknown &= F.coalesce(F.col(d.level).isin(*d.silent), F.lit(True))
        state = F.when(unknown, self.labels["unknown"])
        for i in (HIGH, MOD):
            state = state.when(rung == i, self.labels[RUNGS[i]])
        ranked = [
            F.struct(c.alias("pts"), F.lit(-i).alias("i"), F.lit(n).alias("n"))
            for i, (n, c) in enumerate(pts.items())
        ]
        top = F.sort_array(F.array(*ranked), asc=False)[0]  # ties: declared order
        return df.select(
            "*",
            *[c.alias(f"{p}_{n}_points") for n, c in pts.items()],
            total.alias(f"{p}_points_total"),
            state.otherwise(self.labels["low"]).alias(f"{p}_state"),
            fired.alias(f"{p}_override"),
            F.coalesce(fired, F.when(top["pts"] > 0, top["n"])).alias(f"{p}_reason"),
        )


def state_label(col: str, labels: Mapping[str, object]) -> Column:
    """The ``labels`` value of each ``col`` value; NULL for a value ``labels`` lacks."""
    pairs = [F.lit(x) for pair in labels.items() for x in pair]
    return F.create_map(*pairs)[F.col(col)]
`````

New:

`````python
"""Points -> state scoring shared by the axes (A1, A3; A2 uses ``state_label``). An axis
declares a ``Scorecard`` (dimensions with points per level, thresholds, overrides, state
labels) and builds its own level columns; ``Scorecard.score`` adds points, state, the
override that fired and the reason. Imported by the axes; not run on its own."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

DEMOTE, CAP, FORCE = "demote", "cap", "force"  # Override modes
RUNGS = ("low", "moderate", "high")
LOW, MOD, HIGH = range(len(RUNGS))  # rung indices


@dataclass(frozen=True)
class Dimension:
    """A scored dimension: its ``level`` column, the points per level (others 0; may be
    negative) and the ``silent`` levels that mean "no evidence" (the Unknown gate)."""

    name: str
    level: str
    points: Mapping[str, int]
    silent: tuple[str, ...] = ("none",)


@dataclass(frozen=True)
class Override:
    """A boolean ``flag`` column that, when true, moves the state: ``DEMOTE`` one rung
    (never below Low), ``CAP`` at rung ``to``, or ``FORCE`` to rung ``to``."""

    name: str
    flag: str
    mode: str = DEMOTE
    to: str = "low"


@dataclass(frozen=True)
class Scorecard:  # pylint: disable=too-many-instance-attributes,too-many-locals
    """Points over ``dimensions`` -> High / Moderate / Low, overrides, an Unknown gate.

    Rungs from the points total (``high_from`` / ``moderate_from``, inclusive); High
    also needs ``high_min_dimensions`` dimensions with points, one in ``high_current``
    if given, else Moderate. The first override whose flag is true, in declared order,
    moves the rung (no stacking; a NULL flag does not fire). Unknown: every level silent
    or NULL, no override, and ``unknown_also``. ``labels``: rung or "unknown" -> value.
    """

    prefix: str
    dimensions: tuple[Dimension, ...]
    labels: Mapping[str, str]
    high_from: int
    moderate_from: int
    overrides: tuple[Override, ...] = ()
    high_min_dimensions: int = 0
    high_current: tuple[str, ...] = ()

    def score(self, df: DataFrame, unknown_also: Column | None = None) -> DataFrame:
        """``df`` + ``<prefix>_<dimension>_points``, ``_points_total``, ``_state``,
        ``_override`` (the one that fired), ``_reason`` (it, else the top dimension)."""
        p = self.prefix
        pts = {
            d.name: F.coalesce(state_label(d.level, d.points), F.lit(0))
            for d in self.dimensions
        }
        total = sum(pts.values())
        scored = sum((c > 0).cast("int") for c in pts.values())
        high = (total >= self.high_from) & (scored >= self.high_min_dimensions)
        if self.high_current:
            high &= F.array_max(F.array(*[pts[n] for n in self.high_current])) > 0
        rung = F.when(high, HIGH).when(total >= self.moderate_from, MOD).otherwise(LOW)
        fired = F.coalesce(
            *[F.when(F.col(o.flag), F.lit(o.name)) for o in self.overrides],
            F.lit(None).cast("string"),
        )
        for o in self.overrides:
            to = F.lit(RUNGS.index(o.to))
            moved = {DEMOTE: F.greatest(rung - 1, F.lit(LOW)), CAP: F.least(rung, to)}
            rung = F.when(fired == o.name, {**moved, FORCE: to}[o.mode]).otherwise(rung)
        unknown = F.lit(True) if unknown_also is None else unknown_also
        unknown &= fired.isNull()
        for d in self.dimensions:
            unknown &= F.coalesce(F.col(d.level).isin(*d.silent), F.lit(True))
        state = F.when(unknown, self.labels["unknown"])
        for i in (HIGH, MOD):
            state = state.when(rung == i, self.labels[RUNGS[i]])
        ranked = [
            F.struct(c.alias("pts"), F.lit(-i).alias("i"), F.lit(n).alias("n"))
            for i, (n, c) in enumerate(pts.items())
        ]
        top = F.sort_array(F.array(*ranked), asc=False)[0]  # ties: declared order
        return df.select(
            "*",
            *[c.alias(f"{p}_{n}_points") for n, c in pts.items()],
            total.alias(f"{p}_points_total"),
            state.otherwise(self.labels["low"]).alias(f"{p}_state"),
            fired.alias(f"{p}_override"),
            F.coalesce(fired, F.when(top["pts"] > 0, top["n"])).alias(f"{p}_reason"),
        )


def state_label(col: str, labels: Mapping[str, object]) -> Column:
    """The ``labels`` value of each ``col`` value; NULL for a value ``labels`` lacks."""
    pairs = [F.lit(x) for pair in labels.items() for x in pair]
    return F.create_map(*pairs)[F.col(col)]
`````

### FILE: `src/enbd_collections/pipelines/products/features.py`
action: replace · base sha256 `7275b9e4515bec8a30c773158dd6abab6504eec6b6c6d82cb6ac07d7dfea2765` · base trailing newline: yes · new sha256 `d6e6060a3f575720ac975cc8a1ff30ba5fa8b11fd692a3f21c26af3e31e0423b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Product feature pipeline: the customer's other products with us per month.

    prm_card_contracts, prm_card_month_end, prm_loan_month_end,
    wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif ► feat_cif_cross_product_monthly

Needs ``product_primary`` for the model_id first.

    kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline([_cross_product_node("feat_cif_cross_product_monthly")])


def _cross_product_node(output: str):
    return node(
        func=feat_cif_cross_product.build,
        inputs={
            "card_contracts": "prm_card_contracts",
            "card_month_end": "prm_card_month_end",
            "loan_month_end": "prm_loan_month_end",
            "wm_balances": "wm_fea_casa_eod_avg_balance",
            "wm_holdings": "wm_fea_wealth_holdings_by_cif",
            "persona_start_date": "params:crx_persona.persona_start_date",
            "history_months": "params:products.history_months",
        },
        outputs=output,
        name=f"build_{output}",
        tags=["products", "features"],
    )
`````

New:

`````python
"""Product feature pipeline: the customer's other products with us per month.

    prm_card_contracts, prm_card_month_end, prm_loan_month_end,
    wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif
        ► feat_cif_cross_product_monthly

Needs ``product_primary`` for the model_id first.

    kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline(
        [
            node(
                func=feat_cif_cross_product.build,
                inputs={
                    "card_contracts": "prm_card_contracts",
                    "card_month_end": "prm_card_month_end",
                    "loan_month_end": "prm_loan_month_end",
                    "wm_balances": "wm_fea_casa_eod_avg_balance",
                    "wm_holdings": "wm_fea_wealth_holdings_by_cif",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:products.history_months",
                },
                outputs="feat_cif_cross_product_monthly",
                name="build_feat_cif_cross_product_monthly",
                tags=["products", "features"],
            )
        ]
    )
`````

## Apply script

Written to `data/input/mirror_bundles/apply_bundle.py` by step 3.

`````python
"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

When a repo file differs from the copy the bundle was built from (an edit made at work, a
lint fix, a photo slip), the bundle still applies — it never stops on a difference:
  * replace: three-way merge (git merge-file) of this repo's file, the bundle's base copy and
    the bundle's new version. Edits made here survive wherever the bundle did not change the
    same lines; where both changed the same lines, the bundle's version wins.
  * delete: the file is deleted (git history keeps it).
  * add over an existing file: the bundle's version is written.
Each such file is listed as MERGED; review it with `git diff <path>` before committing.

Safety rules:
  * refuses to write on main/master, or when a touched file has uncommitted changes, so
    `git diff` shows exactly what the bundle did and --revert restores HEAD.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

APPLY_VERSION = 7
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


# Separator lines in comments (``# ── Node 1 ─────``, ``#######``) are transcribed from
# photos, where their exact length cannot be read. Runs of 4+ identical separator
# characters therefore compare equal whatever their length; so do trailing spaces.
_RULE_RUN = re.compile(r"([─━═=\-#*~_])\1{3,}")


def _loose(text: str) -> str:
    return "\n".join(
        _RULE_RUN.sub(r"\1\1\1\1", line.rstrip()) for line in _norm(text).split("\n")
    )


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _same_code(path: str, a: str, b: str) -> bool:
    """Same Python code (comments and docstrings aside) or the same YAML content."""
    try:
        if path.endswith(".py"):
            return ast.dump(_strip_docstrings(ast.parse(a))) == ast.dump(
                _strip_docstrings(ast.parse(b))
            )
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(
        e["path"], current, e["new"]
    )


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_dump(yaml.safe_load(text), sort_keys=True)
    except Exception:  # pylint: disable=broad-except
        pass
    return _loose(text)


def _matches_base(current: str | None, e: dict) -> bool:
    """The repo file is the version the bundle was built from: identical up to
    separator lengths and trailing spaces, or — since comments and docstrings are
    transcribed from photos — the same code / YAML content."""
    if current is None:
        return False
    if _loose(current) == _loose(e["base"]):
        return True
    return _same_code(e["path"], current, e["base"])


def _rebase(new: str, base: str, current: str) -> str:
    """``new`` with every line the bundle did not change taken from ``current``.

    ``current`` matches ``base`` line by line up to separator lengths (``_matches_base``),
    so the repo's own separators survive and ``git diff`` shows only real changes.
    """
    base_l, new_l, cur_l = (_norm(t).split("\n") for t in (base, new, current))
    if len(cur_l) != len(base_l):  # comments wrapped differently: no line alignment
        return new
    out: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, base_l, new_l, autojunk=False
    ).get_opcodes():
        out += cur_l[i1:i2] if tag == "equal" else new_l[j1:j2]
    return "\n".join(out)


def _merge3(current: str, base: str, new: str) -> str:
    """Three-way merge: this repo's edits on top of the bundle's change (git merge-file;
    on overlapping lines the bundle's version wins). Without git: the bundle's version.
    """
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, text in (("current", current), ("base", base), ("new", new)):
            f = pathlib.Path(tmp) / name
            f.write_text(_norm(text), encoding="utf-8")
            paths.append(str(f))
        try:
            out = subprocess.run(
                ["git", "merge-file", "-p", "--theirs", *paths],
                capture_output=True,
                check=False,
            )
        except OSError:
            return new
    return out.stdout.decode("utf-8") if out.returncode >= 0 else new


def _sha(text: str) -> str:
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_bytes().decode("utf-8")


# ── Parsing ──────────────────────────────────────────────────────────────────


def parse_bundle(md: str) -> list[dict]:
    """Return one dict per file: path, action, base/new sha and text."""
    lines = _norm(md).split("\n")
    entries, i = [], 0
    while i < len(lines):
        m = re.match(r"^### FILE: `([^`]+)`\s*$", lines[i])
        if not m:
            i += 1
            continue
        meta = lines[i + 1]
        entry = {
            "path": m.group(1),
            "action": re.search(r"action: (add|replace|delete)", meta).group(1),
            "base_sha": None,
            "new_sha": None,
            "base": None,
            "new": None,
        }
        for kind in ("base", "new"):
            sm = re.search(kind + r" sha256 `([0-9a-f]{64})`", meta)
            if sm:
                entry[kind + "_sha"] = sm.group(1)
        j = i + 2
        for kind in ("base", "new"):
            if entry[kind + "_sha"] is None:
                continue
            while not FENCE.match(lines[j]):
                j += 1
            fence = FENCE.match(lines[j]).group(1)
            k = j + 1
            while lines[k] != fence:
                k += 1
            body = "\n".join(lines[j + 1 : k])
            if re.search(kind + r" trailing newline: yes", meta) and body:
                body += "\n"
            entry[kind] = body
            j = k + 1
        entries.append(entry)
        i = j
    return entries


def verify_bundle(entries: list[dict]) -> list[str]:
    """Blocks whose content no longer matches the checksum (a damaged copy)."""
    errors = []
    for e in entries:
        for kind in ("base", "new"):
            if e[kind + "_sha"] and _sha(e[kind]) != e[kind + "_sha"]:
                errors.append(f"{e['path']}: {kind} block does not match its checksum")
    return errors


# ── Git guards ───────────────────────────────────────────────────────────────


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _head_version(path: str) -> str | None:
    """The committed (HEAD) content of a file, byte-exact, or None."""
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("utf-8")


def git_problems(entries: list[dict]) -> list[str]:
    """Reasons to refuse: a protected branch, or uncommitted edits in a touched file."""
    problems = []
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch is not None:
        branch = branch.strip()
    if branch is None:
        print("note: not a git repository (or git missing) — branch checks skipped")
        return problems
    if branch in PROTECTED_BRANCHES:
        problems.append(
            f"you are on '{branch}' — create a branch first: git checkout -b <name>"
        )
    # Files already in their final state may be uncommitted (applied, not yet committed).
    pending = [e["path"] for e in entries if file_status(e) != "done"]
    dirty = _git("status", "--porcelain", "--", *pending) if pending else ""
    for line in (dirty or "").splitlines():
        if line[:2] != "??":  # untracked files are compared by content below
            problems.append(f"uncommitted change in a touched file: {line[3:]}")
    return problems


# ── Status ───────────────────────────────────────────────────────────────────


def file_status(e: dict) -> str:  # pylint: disable=too-many-return-statements
    """One of: todo, done, merge (the repo file differs from the bundle's base copy)."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "merge"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "merge"
    # delete
    if current is None:
        return "done"
    return "todo" if _matches_base(current, e) else "merge"


def explain_merge(e: dict) -> None:
    """One line on what happened to a file that differed from the bundle's copy."""
    what = {
        "replace": "merged with this repo's own edits",
        "delete": "deleted, although it had edits the bundle's copy lacks (git keeps them)",
        "add": "already existed with other content; replaced by the bundle's version",
    }[e["action"]]
    print(f"MERGED {e['path']}: {what} — review: git diff -- {e['path']}")


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    """One line per bundle file: its action and status."""
    word = {
        "todo": "will apply",
        "done": "already applied",
        "merge": "will apply — MERGED (differs from the bundle's copy)",
    }
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        note = ""
        if s == "todo" and _comment_only(e):
            note = "  (comments differ from the bundle's copy — fine)"
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}{note}")


# ── Post-apply checks ────────────────────────────────────────────────────────


def _module_name(path: str) -> str | None:
    p = pathlib.PurePosixPath(path)
    if p.suffix != ".py" or p.parts[0] != "src":
        return None
    parts = list(p.with_suffix("").parts[1:])
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def compile_and_import(entries: list[dict], do_import: bool) -> list[str]:
    """Compile every touched .py file and import its module (plus the registry)."""
    failures = []
    existing = [
        e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")
    ]
    for e in existing:
        try:
            compile(_read(pathlib.Path(e["path"])), e["path"], "exec")
        except SyntaxError as exc:
            failures.append(f"compile: {e['path']}: {exc}")
    if not do_import or failures:
        return failures
    modules = [m for m in (_module_name(e["path"]) for e in existing) if m]
    if pathlib.Path("src/enbd_collections/pipeline_registry.py").is_file():
        modules.append("enbd_collections.pipeline_registry")
    env = dict(os.environ)
    env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")
    for mod in dict.fromkeys(modules):
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    """Dry run: what --apply would do; False only when git refuses."""
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for p in problems:
        print("REFUSED: " + p)
    print(
        f"\n{statuses.count('todo') + statuses.count('merge')} to apply "
        f"({statuses.count('merge')} merged), {statuses.count('done')} already applied"
    )
    print("CHECK FAILED — nothing was written" if problems else "CHECK PASSED")
    return not problems


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    """Write every file (merging where this repo differs), then verify and import."""
    if not cmd_check(entries):
        return False
    merged = []
    for e in entries:
        status = file_status(e)
        if status == "done":
            continue
        path = pathlib.Path(e["path"])
        if status == "merge":
            merged.append(e)
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
            continue
        new = e["new"]
        if e["action"] == "replace":
            current = _read(path)
            if status == "todo":
                new = _rebase(new, e["base"], current)
            elif current is not None:  # a file missing here gets the bundle's version
                new = _merge3(current, e["base"], new)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(new.encode("utf-8"))
    print()
    for e in merged:
        explain_merge(e)
    # a merged file keeps this repo's own edits, so it need not equal the bundle's version
    merged_paths = {e["path"] for e in merged if e["action"] == "replace"}
    bad = [
        e["path"]
        for e in entries
        if e["path"] not in merged_paths and file_status(e) != "done"
    ]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(
        f"{len(entries)} files in their new state, compile OK"
        + (", imports OK" if do_import else " (imports skipped)")
    )
    print(
        "APPLY PASSED — review with `git status` / `git diff`"
        + (f" (look closely at the {len(merged)} MERGED files)" if merged else "")
    )
    return True


def cmd_revert(entries: list[dict]) -> bool:
    """Put every touched file back to HEAD (apply refuses to run over uncommitted changes,
    so HEAD is the state before --apply); files the bundle added are removed."""
    for e in entries:
        path = pathlib.Path(e["path"])
        committed = _head_version(e["path"])
        if committed is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(committed.encode("utf-8"))
        elif path.exists():
            path.unlink()
            _prune_empty_dirs(path.parent)
    print("REVERT DONE — `git status` should show none of the bundle's files")
    return True


def main() -> int:
    """Parse the arguments, verify the bundle's checksums and run the chosen mode."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--revert", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    args = ap.parse_args()

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(
            f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
            f"{APPLY_VERSION}. Redo step 3 of the bundle."
        )
        return 1
    entries = parse_bundle(md)
    if not entries:
        print("No files found — was the raw markdown copied (not the rendered page)?")
        return 1
    errors = verify_bundle(entries)
    if errors:
        for err in errors:
            print("DAMAGED: " + err)
        print("The bundle copy is damaged — recopy the RAW file. Nothing was written.")
        return 1
    if not pathlib.Path("src").is_dir():
        print("Run this from the workplace repo root (no src/ folder here).")
        return 1
    print(f"{len(entries)} files in bundle, all checksums OK\n")
    if args.check:
        ok = cmd_check(entries)
    elif args.apply:
        ok = cmd_apply(entries, do_import=not args.no_import)
    else:
        ok = cmd_revert(entries)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
`````

## Cleanup prompt

Copy this to the workplace assistant in UAT once the bundle's PROD checks are done:

````text
Clean up after mirror bundle 25_council_a1_a3_refactor.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the path from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for each of the four model_ids (skip folders that do not exist): `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/b25_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundle 25):
  - delete `conf/base/catalog/tmp_b25_check.yml`;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_b25_check` / `crx_rl_b25_check` entries, their comment line and the `b25_check` import;
  - delete `src/enbd_collections/pipelines/crx_persona/b25_check.py`.
- **Retired snippets that no longer import** (from finished validation prompts): delete `tmp_validation/a1_high_whatif/`, `a1_aecb_whatif/`, `a1_bureau_fill/`, `a1_bureau_unified/`, `a1_payment_cure/`, `a1_bulk_pull/`, `a1_casa_accounts/`, `a3_detail/`, `a3_v1h/`, `a3_v1i/`, `a3_v1_v4/`, `a3_check_new/` (whichever exist); list any other `tmp_validation/` folder without deleting it.

  Then check that `kedro registry list` still works and that `grep -rn "b25" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
