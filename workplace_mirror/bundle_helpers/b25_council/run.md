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
