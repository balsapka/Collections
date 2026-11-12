The persisted tables are the baseline: do not re-run `product_features`, `bureau_salary_bounces` or the A1 pipelines before the checks. Set `model_id` in `conf/dev/globals_dev.yml` for each run.

**Step 7.** Run the checks.

**cc_60_180:** build the product primaries, then both checks:

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features_b24_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_b24_check
```

**rl_60_180, cc_180_plus, rl_180_plus:** the A1 check only (`crx_rl_a1_b24_check` for rl, `crx_cc_a1_b24_check` for cc):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_b24_check
```

Paste back, per model_id, every `=== B24 … START ===` … `END ===` block: `B24 PRODUCTS` and `B24 A1 INPUTS` (cc_60_180 only), `B24 BUREAU`, `B24 INCOME`, `B24 A1 OUTPUT`, `B24 A1 MOVES`. Also note the run time of each pipeline.

**Step 8.** After the blocks are reviewed, write the real tables for **all four model_ids**, in this order:

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
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

(`crx_rl_a1_ability` for the rl model_ids.) Then the cleanup prompt.
