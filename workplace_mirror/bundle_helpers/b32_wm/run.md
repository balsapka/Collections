**Step 7.** In PROD, after the pull, for each model_id you rerun (switch `model_id` in `globals_dev.yml` to the same model_id as the pipeline prefix). Run them in this order, because the snapshot has to come before `casa_features` (part of `persona_e2e`) overwrites the table:

```bash
kedro run --pipeline=casa_b32_snapshot
```

```bash
kedro run --env=dev --pipeline=<model_id>.persona_e2e
```

```bash
kedro run --pipeline=casa_b32_compare
```

Paste back the `=== B32 CASA OLD NEW START/END ===` block per model_id. From the `persona_e2e` log, also paste each WM table's `... weeks <first> to <last>` line and any `using adv_load_date=... instead of ...` warning. If a load fails with `no usable adv_load_date partition`, paste the message: it gives the reason for each partition tried.
