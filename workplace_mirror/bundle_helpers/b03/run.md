Run everything for `cc_60_180` (the `model_id` in `conf/dev/globals_dev.yml`).

**Step 9.** First build of `prm_casa_return_events`, from July 2024 (6 months before the CC
modelling start, enough for cc_60_180 and cc_180_plus). Later monthly runs leave
`rebuild_from` unset and rebuild only the previous and the current month:

```bash
kedro run --env=dev --pipeline=casa_primary --params=casa_primary.rebuild_from=2024-07-01
```

**Step 10.** Run the check pipeline (observation base + A1 into the temporary
`crx_cc_a1_ability_b03_check`, then the comparison):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the two blocks, each from `=== B03 … START ===` to `=== B03 … END ===`:
`B03 OUTPUT` (old vs new states) and `B03 INCOME` (the 2 × anchor income bar and the
income-weakening check: how often each fires and the levels / states without them).
Aggregates only, no customer rows. Text is best; otherwise one photo per block.

**Step 11.** Only after the B03 block has been reviewed: refresh the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_v2
```
