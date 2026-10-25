**Step 4.** `_common` helpers now take months instead of days. Check that no file outside
this bundle still calls them — this must print nothing (otherwise stop and send the output
back):

```bash
grep -rnE "max_age_days|window_agg\(|lookback_floor\(|pit_latest\(" src --include='*.py' | grep -vE "crx_persona/_common.py|crx_persona/a1_ability/|crx_persona/cc_a1_ability_v2/"
```
