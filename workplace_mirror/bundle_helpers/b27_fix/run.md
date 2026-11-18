Stop any `crx_<p>_b25_check` run still going (Ctrl+C); its in-memory outputs are lost anyway. Blocks it already printed stay valid: paste them if you have them.

**Step 7 (again).** Run the check for **all four model_ids** (set `model_id` in `conf/dev/globals_dev.yml` each time), cc_60_180 first. Each node now writes its `__b25` copy to HDFS and the comparisons read the copies, so it should run faster than the first attempt:

```bash
kedro run --env=dev --pipeline=crx_cc_b25_check
```

```bash
kedro run --env=dev --pipeline=crx_rl_b25_check
```

The log should now show `Saving data to crx_cc_..._b25 (SparkDataset)`; if it still says MemoryDataset, stop and paste the first such line. Paste back, per model_id, every `=== B25 … START ===` … `END ===` block and the run time. Then bundle 25's step 8, then this bundle's cleanup (not bundle 25's). The A3 results prompt (`a3_final/sonnet_a3_results_prompt.md`) runs on the `__b25` copies **before** step 8 and the cleanup.
