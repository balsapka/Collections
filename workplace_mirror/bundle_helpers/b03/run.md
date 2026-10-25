Run everything for `cc_60_180` (the `model_id` in `conf/dev/globals_dev.yml`).

The axis covers the persona months, `crx_persona.persona_start_date` to
`persona_end_date` in `conf/dev/globals_dev.yml` (dev today: 2026-01 to 2026-08). The B03
OUTPUT compares those months only. If you change either date, rerun Step 7 too.

**Step 7.** Build `prm_casa_return_events` (6 months before the persona start month
onwards):

```bash
kedro run --env=dev --pipeline=casa_primary
```

**Step 8.** Run the check pipeline (observation base + A1 into the temporary
`crx_cc_a1_ability_b03_check`, then the comparison):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the two blocks, each from `=== B03 … START ===` to `=== B03 … END ===`:
`B03 OUTPUT` (old vs new states) and `B03 INCOME` (the 2 × anchor income bar and the
income-weakening check: how often each fires and the levels / states without them).
Aggregates only, no customer rows. Text is best; otherwise one photo per block.

**Step 9.** Only after the B03 block has been reviewed: refresh the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_v2
```
