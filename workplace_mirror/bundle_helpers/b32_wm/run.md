**Step 7.** In PROD, after the pull, for each model_id you rerun (switch `model_id` in `globals_dev.yml`). Run them in this order, because the snapshot has to come before `casa_features` overwrites the table:

```bash
kedro run --pipeline=casa_b32_snapshot
```

```bash
kedro run --pipeline=casa_features
```

```bash
kedro run --pipeline=casa_b32_compare
```

Paste back the `=== B32 CASA OLD NEW START/END ===` block per model_id. Also paste the dataset's log lines from `casa_features`: `... weeks <first> to <last>` for each WM table, and any `using adv_load_date=... instead of ...` warning. Then carry on with the rest of the rerun (product features, persona pipelines) as planned. If a load fails with `no usable adv_load_date partition`, paste the message: it gives the reason for each partition tried.
