# Bundle 16 (R-B) check results (2026-11-06)

User: every RF block matched (0 rows only in old / new, states on the diagonal) except RF A2 OUTPUT:
- rl_60_180: 3 rows unknown -> non_reachable (reported in chat, no block pasted);
- rl_180_plus: the block below (handoff 48).

Reading (Claude): the 22,328 `None -> ...` rows are rows missing from the OLD output (no old row), not Unknown rows reclassified; their state mix matches the rest (76% unknown__unknown vs 77%), so the persisted rl_180_plus A2 output predates the current obs base (stale), and step 11 refreshes it. "rows only in old: 4" are the 4 rows whose state changed (skip__unknown -> skip__non_reachable); with the 3 rows at 60_180 these move toward non_reachable, most likely DCORE events logged after the old A2 run (the golden harness shows the code identical on 79 datasets). Open: confirm with the HDFS dates of the old A2 output and the obs base.

## Terminal output (as shown)

````
...acaai402b retail.collections.risk_profiling]# kedro run --env=dev --pipeline=crx_rl_a2_rf_ch...
        WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:243: UserWa...
                 not have a '__name__' attribute: consider using 'functools.update_wrapper'...
                   warn(

        INFO     Running node: compare_crx_rl_a2_locatability_rf: <partial>() -> None
...3:56:42] INFO
                 === RF A2 OUTPUT START ===
                 model_id: rl_180_plus
                 rows old / new: 408675 / 431003
                 same schema: True
                 rows only in old: 4
                 rows only in new: 22332
                 rows whose a2_state differs: 22332
                   None -> deceased: 351
                   None -> in_country__non_reachable: 169
                   None -> in_country__reachable: 223
                   None -> in_country__unknown: 287
                   None -> skip__non_reachable: 397
                   None -> skip__reachable: 266
                   None -> skip__unknown: 2417
                   None -> unknown__non_reachable: 538
                   None -> unknown__reachable: 636
                   None -> unknown__unknown: 17044
                   deceased -> deceased: 5111
                   in_country__non_reachable -> in_country__non_reachable: 3102
                   in_country__reachable -> in_country__reachable: 5185
                   in_country__unknown -> in_country__unknown: 6001
                   skip__non_reachable -> skip__non_reachable: 6864
                   skip__reachable -> skip__reachable: 4687
                   skip__unknown -> skip__non_reachable: 4
                   skip__unknown -> skip__unknown: 42136
                   unknown__non_reachable -> unknown__non_reachable: 10056
                   unknown__reachable -> unknown__reachable: 10906
                   unknown__unknown -> unknown__unknown: 314623
                 === RF A2 OUTPUT END ===
        INFO     Completed node: compare_crx_rl_a2_locatability_rf
        INFO     Completed 8 out of 8 tasks
        INFO     Pipeline execution completed successfully in 157.6 sec.
...acaai402b retail.collections.risk_profiling]# 
````


## Notes on specific spots
- Row-count checks that pass: 408,675 - 4 (only in old) + 22,332 (only in new) = 431,003 (new rows). The 20 old-to-new lines below the counts (all lines except the ten `None -> ...` ones) add up to 408,671 = 408,675 - 4, i.e. every old row that is also in new is accounted for; of these, 408,667 keep their state and 4 change (`skip__unknown -> skip__non_reachable: 4`).
- Check that does not tie out: the ten `None -> ...` lines add up to 22,328 (351 + 169 + 223 + 287 + 397 + 266 + 2,417 + 538 + 636 + 17,044), not 22,332 as "rows only in new" says, which leaves 4 rows unaccounted for. "rows whose a2_state differs: 22332" does match 22,328 (the `None -> ...` rows) + 4 (`skip__unknown -> skip__non_reachable`). So either "rows only in new" is 4 too high or 4 `None -> ...` rows were not printed. Copied as shown; check against the real log.
- `None` is shown in the terminal's magenta colour (a Python `None` for rows missing on one side of the comparison). "rows only in old: 4" has no matching `X -> None` lines in the printout.
- The dominant states are `unknown__unknown` (314,623 unchanged, 17,044 new) and `skip__unknown` (42,136 unchanged, 2,417 new). State names use a double underscore (`in_country__non_reachable`, `skip__unknown`, `unknown__unknown`): the first part looks like a country / residency-type group (`deceased`, `in_country`, `skip`, `unknown`) and the second part the A2 reachability state. This reading is mine; the photo does not explain the names.
- The warning is Kedro's usual message that a `functools.partial` node function does not have a `__name__` attribute (the node is shown as `<partial>()`).
- Run time: "Completed 8 out of 8 tasks", "Pipeline execution completed successfully in 157.6 sec."
- OCR-risk digits: all counts in the block (they are printed in cyan without thousands separators), especially 408675, 431003, 22332, 17044, 42136, 314623, 10056, 10906 and 157.6.
