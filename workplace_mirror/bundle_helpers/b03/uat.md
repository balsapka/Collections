**Step 6.** `_common` helpers now take months instead of days. Check that no file outside
this bundle still calls them the old way — this must print nothing (otherwise stop and send
the output back):

```bash
grep -rn "max_age_days\|days=\|window_agg(\|lookback_floor(" src --include=*.py | grep "window_agg\|lookback_floor\|pit_latest\|max_age_days" | grep -v "crx_persona/_common.py\|crx_persona/a1_ability/\|crx_persona/cc_a1_ability_v2/"
```
