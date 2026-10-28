Run everything twice: first for **`cc_60_180`** (the default in
`conf/dev/globals_dev.yml`), then for **`rl_60_180`** (set `model_id: rl_60_180`, persona
dates unchanged). Switch it back to `cc_60_180` when you are done. Steps 6–8 per model_id.

**Step 6.** Rebuild the logins with the fixes, then the CASA primaries (return events +
the new debit-card table; the card table scans 36 months of the raw table, so expect a
long run):

```bash
kedro run --env=dev --pipeline=digital_login
```

```bash
kedro run --env=dev --pipeline=casa_primary
```

**Step 7.** Run the check pipeline (observation base, `location_features`, the new A2
into the temporary `crx_<p>_a2_locatability_b06_check`, then the comparison). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check
```

It reads the old A2's existing output `crx_<p>_a2_locatability`. If it stops with
`PATH_NOT_FOUND` on that dataset (or on `prm_transaction` / `prm_contract` / `prm_client`
for RL), send the error back.

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: `OUTPUT`,
`RULES`, `DEBIT` (and `PRODUCT` for RL). Aggregates only. Text is best; otherwise one
photo per block.

**Step 8.** Only after the B06 blocks have been reviewed: write the real output (it
replaces the old A2's output at the same path).

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability
```
