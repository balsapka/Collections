Run everything twice: first for **`cc_60_180`** (the default in `conf/dev/globals_dev.yml`),
then for **`rl_60_180`** (set `model_id: rl_60_180`, persona dates unchanged). Switch it
back to `cc_60_180` when you are done. Steps 6–8 per model_id.

**Step 6.** Build the new inputs. Only the two new CASA primaries (the existing ones are
unchanged; `prm_casa_transactions` scans 12+ months of the raw table, so expect a long run),
then the bureau and CASA features:

```bash
kedro run --env=dev --pipeline=casa_primary --nodes=build_prm_casa_transactions,build_prm_beneficiary_cards
```

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=casa_features
```

If `bureau_salary_bounces` stops on `stg_aecb_salary_history`, `prm_bureau_cif_bridge` or
`prm_bureau_alert_enriched` (PATH_NOT_FOUND / table not found), send the error back.

**Step 7.** Run the check pipeline (observation base, the new A1 into the temporary
`crx_<p>_a1_ability_b08_check`, then the report blocks). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b08_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b08_check
```

It reads the current output `crx_<p>_a1_ability_v2` and `prm_dcore_account_agreements`
(built by `location_features`). If it stops with PATH_NOT_FOUND on the agreements, run
`kedro run --env=dev --pipeline=location_features --nodes=build_prm_dcore_account_agreements`
and repeat step 7; on anything else, send the error back.

Paste back every block from `=== B08 … START ===` to `=== B08 … END ===`: `OUTPUT`,
`REPORT`, `SOURCES`, `CHANGES`. Aggregates only. Text is best; otherwise one photo per
block.

**Step 8.** Only after the B08 blocks have been reviewed: write the real output (it
replaces the old CC v1 / RL waterfall output at the same path).

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```
