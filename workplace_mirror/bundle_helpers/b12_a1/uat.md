**Step 4.** Ask Sonnet two things:

1. Run the A1 test modules. `income_level` now reads `internal_salary_w` and
   `internal_salary_prior`, so fix any test that builds income rows without them.
2. Find the nodes that build the alert staging dataset and `prm_bureau_alert_enriched`, and write out
   the exact command that rebuilds **only those** (`kedro run --env=dev --pipeline=... --nodes=...`),
   because other raw AECB tables are missing and a full `bureau_staging` run may stop on them.
   Say whether `prm_bureau_alert_enriched` needs another dataset rebuilt first. You will use it in
   step 6.

Then `grep -rnE "a1_ability_v2|b09" src conf --include='*.py' --include='*.yml' | grep -v scoring_engine.py`
must print nothing, and `kedro registry list | grep a1_ability` lists the two `*_b12_check` pipelines.
