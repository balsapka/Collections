Run everything twice: first for **`cc_60_180`** (the default in `conf/dev/globals_dev.yml`),
then for **`rl_60_180`** (set `model_id: rl_60_180`, persona dates unchanged). Switch it
back to `cc_60_180` when you are done. Steps 6–8 per model_id.

**Step 6.** Rebuild the bureau features:

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

For `rl_60_180`, if bundle 08's step 6 never ran for it, first build its CASA inputs:

```bash
kedro run --env=dev --pipeline=casa_primary --nodes=build_prm_casa_transactions,build_prm_beneficiary_cards
```

```bash
kedro run --env=dev --pipeline=casa_features
```

If `bureau_salary_bounces` stops on `prm_bureau_alert_enriched` (PATH_NOT_FOUND / table not
found), send the error back. The persisted alerts end 2026-08-27; a later observation month
needs them rebuilt first.

**Step 7.** Run the check pipeline (observation base, the new A1 into the temporary
`crx_<p>_a1_ability_b09_check`, then the report blocks). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b09_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b09_check
```

Paste back every block from `=== B09 … START ===` to `=== B09 … END ===`: `OUTPUT`,
`REPORT`, `SOURCES`, `AECB`. Aggregates only. Text is best; otherwise one photo per block.

**Step 8.** Only after the B09 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```
