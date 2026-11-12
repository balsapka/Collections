Bundle 21's persisted `feat_cif_cross_product_monthly` is the baseline: do not re-run `product_features` before the check. The tables cover all customers, so the check needs one model_id: **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`).

**Step 7.** Build the primaries, then run the check (cc_60_180):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features_b24_check
```

Paste back both blocks, `=== B24 PRODUCTS START ===` … `END ===` and `=== B24 A1 INPUTS START ===` … `END ===`. Also note the run time of each pipeline.

**Step 8.** After the blocks are reviewed, write the real tables for **all four model_ids** (A1 does not need a re-run: its inputs do not change):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

Then the cleanup prompt.
