**Step 4.** Ask Sonnet the following, in one go:

1. **Tests of deleted code.** Find every test under `src/tests/` that imports `cc_departure_signature`, `rl_departure_signature`, `cc_payment_trajectory`, `cc_utilisation`, `cc_a2_locatability.nodes`, `cc_a2_locatability.constants` or `rl_a2_locatability.nodes`. Delete tests of deleted code. A test of `build_rl_depart_spine` imports it from `crx_persona.rl_a4_spine.nodes` now. Run the remaining crx_persona tests; they must pass.
2. **Other readers.** `grep -rn` over `src` and `conf` for the deleted package names, the 20 removed datasets (`crx_cc_departure_*`, `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_rl_departure_signature`, `crx_rl_depart_travel_mcc`, `crx_rl_depart_foreign_signals`) and `parse_yyyymmdd`, `priority_reason`, `SEGMENTS`. Report any hit outside the tests; do not change it.

Then check: `kedro registry list` runs and lists `crx_rl_a4_spine_ra_check`, and none of the 4 removed pipelines.
