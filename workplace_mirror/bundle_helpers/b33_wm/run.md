**Step 7.** In PROD, after the pull, carry on with bundle 32's step 7 for each model_id (switch `model_id` in `globals_dev.yml` to the pipeline prefix): `casa_b32_snapshot` → `<model_id>.persona_e2e` → `casa_b32_compare`. If `casa_b32_snapshot` already ran for a model_id and `casa_features` did not finish since, don't rerun it.

```bash
kedro run --pipeline=casa_b32_snapshot
```

```bash
kedro run --env=dev --pipeline=<model_id>.persona_e2e
```

```bash
kedro run --pipeline=casa_b32_compare
```

Paste back the `=== B32 CASA OLD NEW START/END ===` block per model_id, and from the `persona_e2e` log each WM table's `weeks <first> to <last>` line, the `weeks start at ... later than the requested month` warnings and any `using adv_load_date=... instead of ...` warning.
