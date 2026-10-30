GRR accepted the A2 logic with one change: at 180+ the failed-call-day streak for Non-Reachable is 6,
not 3 (D-A2-20). `GONE_DARK_DAYS` is now per segment (3 at 60–180, 6 at 180+), read through
`gone_dark_days(model_id)`; `build_dcore_signals` uses it. Nothing
changes at 60–180: `cc_60_180` and `rl_60_180` outputs stay as they are, so bundle 06 step 8 and
the RL product and v04 snippets are unaffected. `b06_check.py` is not in this bundle: the bundle 06 cleanup
already removed it. `apply_bundle.py` v7 no longer crashes on a file missing here.
