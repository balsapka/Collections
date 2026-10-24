Run everything for `cc_60_180` (the `model_id` in `conf/dev/globals_dev.yml`).

**Step 9.** First full build of `prm_casa_return_events` (scans the whole
`comp_financial_tran_repos_dly` once; later runs use the default `rebuild_days`):

```bash
kedro run --env=dev --pipeline=casa_primary --params=casa_primary.rebuild_days=4000
```

**Step 10.** Run the check pipeline (observation base + A1 into the temporary
`crx_cc_a1_ability_b03_check`, then the comparison):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the block from `=== B03 OUTPUT START ===` to `=== B03 OUTPUT END ===`
(aggregates only, no customer rows). Text is best; otherwise one photo.

**Step 11.** Only after the B03 block has been reviewed: refresh the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_v2
```
