Run everything for `cc_60_180` (the `model_id` in `conf/dev/globals_dev.yml`).

Before Step 9, check that `crx_persona.persona_start_date` in `conf/dev/globals_dev.yml`
is not later than the first observation month in `cc_spine`. The A1 run stops otherwise
(`prm_casa_return_events` would not reach back far enough); move the date back if so.

**Step 9.** Build `prm_casa_return_events` (6 months before the persona start month
onwards):

```bash
kedro run --env=dev --pipeline=casa_primary
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
