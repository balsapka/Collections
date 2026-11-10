Today's real `crx_<p>_a1_ability` (bundle 14 rule) is the baseline: do not re-run A1 before the check. Run for **all four model_ids** (`cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus`; set `model_id` in `conf/dev/globals_dev.yml`).

**Step 6.** Build the new features (per model_id):

```bash
kedro run --env=dev --pipeline=casa_features
```

```bash
kedro run --env=dev --pipeline=product_features
```

**Step 7.** Run the check (CC model_ids: the CC check; RL model_ids: the RL check):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_check
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_check
```

Paste back every block from `=== A1 … START ===` to `=== A1 … END ===` (4 per model_id). A summary file is fine.

**Step 8.** After the blocks are reviewed, write the real output for every model_id, then re-run the persona master if the deck needs it:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

Then the cleanup prompt.
