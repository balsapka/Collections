# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/synthesized_features`). Photograph the result and drop it in `pics/`.

## R1 — A1 reference grep (needed before removing A1 v1)

Run from the workplace repo root and photograph the full output:

```bash
grep -rnE "cc_a1_ability|a1v2|a1_state|crx_rl_a1|rl_a1_ability|_TAU_SALARY_H2_MIN|a1_ability\.enrichers|cc_a1_ability import" src conf | grep -vE "/(cc_a1_ability|cc_a1_ability_v2|rl_a1_ability)/"
```

If the output is long, write it to a file and photograph it in the editor:

```bash
grep -rnE "cc_a1_ability|a1v2|a1_state|crx_rl_a1|rl_a1_ability|_TAU_SALARY_H2_MIN|a1_ability\.enrichers|cc_a1_ability import" src conf | grep -vE "/(cc_a1_ability|cc_a1_ability_v2|rl_a1_ability)/" > /tmp/a1_refs.txt
```

It lists every place outside the three ability folders that uses A1 v1, v2 or the RL waterfall
(imports, `pipeline_registry.py`, catalog/parameter entries, downstream readers of `a1_state`).

## R2 — enrichers.py gap

Photograph `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/enrichers.py`,
**lines 170–215** (line numbers visible). Lines 176–211 were missing from batch 6.
