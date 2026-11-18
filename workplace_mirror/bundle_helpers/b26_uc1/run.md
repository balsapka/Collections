This is a new output, not a comparison: nothing to keep as a baseline and nothing temporary to remove in HDFS. The obs base must exist for the model_id (it does after bundle 25's step 8). Set `model_id` in `conf/dev/globals_dev.yml` for each run.

**Step 7.** Run the stated block for **all four model_ids** (`crx_cc_uc1_stated` for cc_60_180 and cc_180_plus, `crx_rl_uc1_stated` for rl_60_180 and rl_180_plus):

```bash
kedro run --env=dev --pipeline=crx_cc_uc1_stated
```

```bash
kedro run --env=dev --pipeline=crx_rl_uc1_stated
```

Paste back, per model_id, the three logged distributions (`uc1_stated [<model_id>] — uc1_evidence`, `— a5_state`, `— a6_state`, with their lines), or the error if the run stopped. Then the cleanup prompt.
