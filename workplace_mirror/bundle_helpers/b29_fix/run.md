**Step 6.** Carry on with bundle 28's step 7 from where it stopped (`model_id` set in `conf/dev/globals_dev.yml` each run): for each model_id, `product_primary`, `product_features`, A1, A3. Bundle 28's step 6 snapshots stay valid (they hold the tables before step 7, and step 7 failed before writing anything); rerun a snapshot only for a model_id where it never ran. Then bundle 28's step 8, its cleanup (it also covers this bundle), and the A3 results prompt run 2.

```bash
kedro run --env=dev --pipeline=product_primary
```
