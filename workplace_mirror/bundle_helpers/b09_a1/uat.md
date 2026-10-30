**Step 4.** The A1 test modules are yours to update (the bundle does not touch tests):
`src/tests/pipelines/crx_persona/schema_registry.py` and `test_crx_persona.py`. Add
`a1_income_source` (string) and `a1_salary_stopped` (int) to the `crx_cc_a1_ability` /
`crx_rl_a1_ability` schema, replace any bundle 08 check reference, and point any bureau
salary test at `feat_cif_bureau_salary_monthly.build(alerts)`. Keep the rest passing. Then this
must print nothing (otherwise stop and send the output back):

```bash
grep -rnE "b08|prm_bureau_salary_history" src conf --include='*.py' --include='*.yml'
```

and `kedro registry list | grep -E "a1_ability|bureau_salary"` lists `bureau_salary_bounces`,
`crx_cc_a1_ability`, `crx_rl_a1_ability` and the two `*_a1_ability_b09_check` pipelines.
