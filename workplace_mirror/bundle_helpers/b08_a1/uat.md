**Step 4.** The two A1 test modules are yours to update (the bundle does not touch tests):
`src/tests/pipelines/crx_persona/schema_registry.py` and `test_crx_persona.py`. They
import the deleted CC v1 (`cc_a1_ability.nodes`, the `cc_a1_ability_empty` fixture) and the
`CRX_CC_A1_ABILITY` v1 schema. Point them at the new `crx_cc_a1_ability` /
`crx_rl_a1_ability` output (columns: `account_id`, `observation_date`, `a1_state`,
`a1_state_label`, `a1_provenance`, `a1_unknown_reason`, `a1_income_level`,
`a1_liquidity_level`, `a1_points_total`, `a1_distress_flag`, `liquidity_anchor_amt`,
`a1_eosb_flag`, `computed_at`), drop the v1 tests, and keep the rest passing. Then this must
print nothing (otherwise stop and send the output back):

```bash
grep -rnE "a1_ability_v2|build_internal_returns|cc_a1_ability\.enrichers|create_b05_check_pipeline" src --include='*.py' | grep -v "crx_persona/a1_ability/pipeline.py"
```

and `kedro registry list | grep -E "a1|casa|bureau_salary"` lists `casa_primary`,
`casa_features`, `bureau_salary_bounces`, `crx_cc_a1_ability`, `crx_rl_a1_ability` and the
two `*_a1_ability_b08_check` pipelines.
