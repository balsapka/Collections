**Step 4.** Ask Sonnet the following, in one go:

1. **Catalog.** The four `crx_<p>_a3_check_{new,old}` entries exist exactly once; list every top-level key the apply removed from `catalog_crx.yml` compared with the last commit (`git diff` of the file, lines starting with `-` and no indent) and put back any that is not an A3 check entry. Do the same for `pipeline_registry.py` (the `casa_windows*` entries must survive).
2. **Callers.** `grep -rn "build_promise_events\|build_a3_credibility\|PROMISE_DEADLINE" src` : every caller passes `model_id` and `product` (the nodes read `params:model_id`); fix any workplace-only caller and report it.
3. **Tests.** Update the A3 tests for the new signatures and the month-end deadline; the mirror's spec test (`workplace_mirror/checks/a3_engine_spec.py`) has the cases.

Then check: `kedro registry list | grep a3` lists `crx_cc_a3_check` and `crx_rl_a3_check`.
