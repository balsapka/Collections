No check pipeline for this bundle. Only the 180+ output changes: rerun the final A2 pipeline, nothing
upstream, per model_id (`model_id` in `globals_dev.yml`). 60–180 needs nothing.

`model_id: cc_180_plus`:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability
```

`model_id: rl_180_plus`:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability
```
