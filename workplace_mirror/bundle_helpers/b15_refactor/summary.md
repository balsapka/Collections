**What this bundle does.** Removes the persona code nothing runs any more, after the A1, A2 and A4 rebuilds. No live output changes. It is the first of three bundles applied in order: this one (dead code), then the refactor of the shared layer, A1, A2 and A4 (zero-difference checks), then the new A3.

- **Deleted packages and files:** `cc_departure_signature/`, `rl_departure_signature/` (except one function, below), `cc_payment_trajectory/`, `cc_utilisation/`, and the old A2 `cc_a2_locatability/nodes.py` + `constants.py` and `rl_a2_locatability/nodes.py` (orphaned since the A2 refactor; the wrappers call the `a2_locatability` engine).
- **Moved, unchanged:** `build_rl_depart_spine` moves from `rl_departure_signature/nodes.py` into `rl_a4_spine/nodes.py`, because `crx_rl_a4_spine` (read by A3) is built by it. Same code, same name, same output.
- **Removed from the registry:** the 4 pipelines of the deleted packages (`crx_cc_departure_signature`, `crx_rl_departure_signature`, `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`).
- **Removed from the catalog:** their 20 datasets (17 CC, 3 RL); the HDFS folders go in the cleanup.
- **Removed unused symbols:** `parse_yyyymmdd` (`_common`), `priority_reason` (`scoring_engine`), `SEGMENTS` (`_dpd_journey.constants`).
- **Not touched:** A3, `_dcore_codes.py`, `cc_raw_extract/`, the spell tables, every A1 / A2 / A4 node.
- **Check** (temporary): `crx_rl_a4_spine_ra_check` rebuilds the spine with the moved function and compares it with the current `crx_rl_a4_spine`. Expected: same row count, same schema, 0 rows only in either.
