**Step 4.** Ask Sonnet the following, in one go:

1. **Leftovers of the DCORE judge.** `grep -rn "a3_kept_by\|instalment_amount_flags\|KEPT_BY\|GRACE" src conf` must find nothing in the A3 code or conf (`instalment_amount_flags` may stay in the DCORE feature code). Remove any workplace-only reader of `a3_kept_by` and report it.
2. **Catalog.** `crx_cc_a3_promise_events`, `crx_rl_a3_promise_events` and the four `crx_<p>_a3_check_*` entries exist exactly once; list every top-level key the apply removed from `catalog_crx.yml` compared with the last commit (`git diff` of the file, lines starting with `-` and no indent) and put back any that is not an A3 check entry.
3. **Tests.** Update the A3 tests for the new `build_commitment_signals(episode, events)` signature and `build_promise_events`; drop tests of the DCORE judge. The mirror's spec test (`workplace_mirror/checks/a3_engine_spec.py`) has the cases.

Then check: `kedro registry list | grep a3` lists `crx_cc_a3_check` and `crx_rl_a3_check`.
