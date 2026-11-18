Set `model_id` in `conf/dev/globals_dev.yml` before each run; `cc` pipeline names for cc_60_180 / cc_180_plus, `rl` for rl_60_180 / rl_180_plus.

**Step 6 (before step 7).** Snapshot the persisted A1 / A3 states, **all four model_ids** (seconds each):

```bash
kedro run --env=dev --pipeline=crx_cc_b28_snapshot
```

```bash
kedro run --env=dev --pipeline=crx_rl_b28_snapshot
```

**Step 7.** Write the real tables, **per model_id, in this order** (all four):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

Not needed: `crx_cc_raw_extract`, A4, `crx_cc_a2_locatability`, and bureau for cc_180_plus / rl_60_180 / rl_180_plus (bundle 25's check showed them identical). Only if not run since bundle 25: `bureau_salary_bounces` for cc_60_180 and `crx_rl_a2_locatability` for rl_60_180 / rl_180_plus (before A1).

**Step 8 (after step 7).** Compare, **all four model_ids**:

```bash
kedro run --env=dev --pipeline=crx_cc_b28_compare
```

```bash
kedro run --env=dev --pipeline=crx_rl_b28_compare
```

Paste back, per model_id, the `=== B28 ROWS / B28 A1 / B28 A3 … START ===` … `END ===` blocks, the `a1_ability` and `a3` state distributions step 7 logged, and the run time of step 7's A1 and A3 runs (cc_180_plus above all). The old tables predate bundle 25's rules too, so the crosstabs show bundles 25 and 28 together. Then the cleanup prompt, then the A3 results prompt run 2 (`workplace_mirror/bundle_helpers/a3_final/sonnet_a3_results_prompt.md` in the mirror).
