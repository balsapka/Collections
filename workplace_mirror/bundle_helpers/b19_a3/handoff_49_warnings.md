# Handoff 49: two terminal outputs: Kedro dot-name warnings (`crx_cc_a3_check`) and Spark cross-join warning + RF A4 compare (`crx_cc_a4_rf_check`) (2 photos), 2026-11-09

## Context for Claude Code
- Source: 2 phone photos of VS Code on a second monitor (workspace `retail.collections.risk_profiling`, dev container). Both show the TERMINAL panel (tabs PROBLEMS, OUTPUT, DEBUG CONSOLE, TERMINAL, PORTS 4, GITLENS). They are console output, not source files. Photo 1 also shows the bottom of `conf/dev/globals_dev.yml`'s model_id block above the panel is cut off; photo 2 shows lines 10-28 of that file above the terminal. Follows handoffs 1-48.
- Photo 1: end of `kedro run --env=dev --pipeline=crx_cc_a3_check`, a list of Kedro `UserWarning`s (node.py:645) about dataset names with a `.` in them (all `a3_check.<name>`). The photo is taken at an angle and cropped at the top and right edge; the first warning is cut off and some lines end at the edge.
- Photo 2: `kedro run --env=dev --pipeline=crx_cc_a4_rf_check` (CC A4 deterioration, old vs new "RF" comparison on `cc_60_180`). It contains the tail of a state distribution, a Spark `WARN ExtractPythonUDFFromJoinCondition` (join condition built only from a Python UDF, turned into a cross join), the "RF A4 OUTPUT" comparison block, and the run summary. Taskbar clock 6:02 PM 11/6/2026 (Spark log time 14:01-14:02 is the same run in UTC).
- The user asked what these two kinds of warning mean (answer in chat, summarised under "Notes" below). Same RF comparison for A2 on `rl_180_plus` is in handoff 48.
- Transcribed by Claude (chat) from the images, not copied from the terminal. Verify against the real run log.
- Photos are in the order sent: photo 1 = Kedro warnings; photo 2 = `globals_dev.yml` lines 10-28 + `crx_cc_a4_rf_check` output.
- Saved through the Mac link if available (see the reply in chat); otherwise copy it to `~/Python/Collections/pics/claude_code_handoff_49.md`.

---

## Photo 1: `kedro run --env=dev --pipeline=crx_cc_a3_check` (Kedro dot-name warnings)

Editor strip above the panel (cut at the left; the file is `globals_dev.yml`, see photo 2 for the full lines):
````
"cc_60_180"
ld: "rl_60_180"
ld: "rl_180_plus"
```` 
and, further up, the tail of line 15: `pipeline (kedro run --pipeline=rl_60_180).` with blame text "You, 41 minutes ago • Uncommitted changes". Status bar: "You, 41 minutes ago", "Not Committed Yet", Ln 17, Col 22, Spaces: 2, UTF-8, LF.

Terminal (as shown; lines are wrapped by the terminal and cut at the right edge, `...` marks cut text):
````
...1402b retail.collections.risk_profiling]# kedro run --env=dev --pipeline=crx_cc_a3_check
        as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.commitments_dcore' contains '.' characters, which is not
         recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_cc_a3_dlq_payment_signals_single_payment_cycle_count'
         contains '.' characters, which is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention...
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_coun...
         contains '.' characters, which is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_cc_a3_strong_negative_signals' contains '.' characters, ...
         is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.contacts_uncapped' contains '.' characters, which is not
         recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_episode' contains '.' characters, which is not
         recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_instalments' contains '.' characters, which is not
         recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_payments' contains '.' characters, which is not
         recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_dues' contains '.' characters, which is not recommended
         as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_dlq_payment_signals_single_payment_cycle_count'
         contains '.' characters, which is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count'
         contains '.' characters, which is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
          warnings.warn(
WARNING  /usr/local/lib/python3.11/site-packages/kedro/pipeline/node.py:645: UserWarning: Dataset name 'a3_check.crx_rl_a3_strong_negative_signals' contains '.' characters, which ...
         is not recommended as the dot notation is reserved for automatic namespacing in Kedro. Consider using a different naming convention.
````
Datasets named in the visible warnings (in order): `a3_check.commitments_dcore`, `a3_check.crx_cc_a3_dlq_payment_signals_single_payment_cycle_count`, `a3_check.crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count`, `a3_check.crx_cc_a3_strong_negative_signals`, `a3_check.contacts_uncapped`, `a3_check.crx_rl_a3_episode`, `a3_check.crx_rl_a3_instalments`, `a3_check.crx_rl_a3_payments`, `a3_check.crx_rl_a3_dues`, `a3_check.crx_rl_a3_dlq_payment_signals_single_payment_cycle_count`, `a3_check.crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count`, `a3_check.crx_rl_a3_strong_negative_signals`. The output continues below the visible part (the photo ends at the last warning), so the run result is not visible.

---

## Photo 2: `conf/dev/globals_dev.yml` (lines 10-28) and `kedro run --env=dev --pipeline=crx_cc_a4_rf_check`

Editor (breadcrumb `conf > dev > ! globals_dev.yml > ...`; the line-17 gutter bar shows it is modified; Ln 19, Col 20, Spaces: 2, UTF-8, LF, YAML; blame "You, 1 hour ago" and "balzsv (3 weeks ago)"):
````yaml
10  # Namespace for model-agnostic datasets (e.g. genesys) — replaces model_id in their paths
11  shared_id: "shared"
12
13  # Active model variant — change this to switch the namespace for all domain pipeline runs.
14  # ModelConfigHook reads this when running non-model-variant pipelines (bureau, demographics, etc.).
15  # Overridden automatically when running a model variant pipeline (kedro run --pipeline=rl_60_180).
16  # model_id: "cc_180_plus"
17  model_id: "cc_60_180"
18  # model_id: "rl_60_180"
19  # model_id: "rl_180_plus"
20  dlq_min: 4
21  dlq_max: 7
22  collateral_codes: ["WO", "SK"]   # default matches cc_60_180; overridden by ModelConfigHook at runtime
23
24  folders:
25    dct: "00_dictionary"
26    raw: "01_raw"
27    stg: "02_stg"
28    int: "03_int"
````

Terminal (as shown; the right-hand file:line labels are Kedro's log source and are listed in brackets after the line they belong to):
````
[root@lvenaacaai402b retail.collections.risk_profiling]# kedro run --env=dev --pipeline=crx_cc_a4_rf_check
        INFO     repeat_delinquent               1599  (  8.3%)      [_common.py:213]
        INFO     slow_roller                     3259  ( 16.9%)      [_common.py:213]
        INFO     stabilized                      1273  (  6.6%)      [_common.py:213]
        INFO     straight_roller_early_life      2937  ( 15.2%)      [_common.py:213]
        INFO     straight_roller_seasoned        8724  ( 45.2%)      [_common.py:213]
        INFO     unknown                           60  (  0.3%)      [_common.py:213]
        INFO     Saving data to crx_cc_a4_deterioration_rf_check (SparkDataset)...      [data_catalog.py:1006]
26/11/06 14:01:55 WARN ExtractPythonUDFFromJoinCondition: The join condition:((isnotnull((((year(last_day(make_date(cast((cast(_udf(_rows#221, _first_raw#223, _global_min#234)#249.first_month_idx as bigint) div 12)
 as int), ((_udf(_rows#221, _first_raw#223, _global_min#234)#249.first_month_idx % 12) + 1), 1, false))) * 12) + month(last_day(make_date(cast((cast(_udf(_rows#221, _first_raw#223, _global_min#234)#249.first_month_
idx as bigint) div 12) as int), ((_udf(_rows#221, _first_raw#223, _global_min#234)#249.first_month_idx % 12) + 1), 1, false)))) - 1))) AND isnotnull((((year(last_day(make_date(cast((cast(_udf(_rows#221, _first_raw#223, _global_min#234)#249.last_month_idx as bigint) div 12) as int), ((_udf(_rows#221, _first_raw#223, _global_min#234)#249.last_month_idx % 12) + 1), 1, false))) * 12) + month(last_day(make_date(cast((cast(_udf(_rows#221, _first_raw#223, _global_min#234)#249.last_month_idx as bigint) div 12) as int), ((_udf(_rows#221, _first_raw#223, _global_min#234)#249.last_month_idx % 12) + 1), 1, false)))) - 1))) AND (_udf(_rows#221, _first_raw#223, _global_min#234)#249.build_status = ok)) of the join plan contains PythonUDF only, it will be moved out and the join plan will be turned to cross join.
[11/06/26 14:02:05] INFO     Completed node: rf_cc.build_crx_cc_a4_deterioration      [runner.py:245]
                    INFO     Completed 4 out of 5 tasks      [runner.py:246]
                    INFO     Loading data from crx_cc_a4_deterioration (SparkDataset)...      [data_catalog.py:1046]
                    INFO     Loading data from crx_cc_a4_deterioration_rf_check (SparkDataset)...      [data_catalog.py:1046]
                    INFO     Loading data from params:model_id (MemoryDataset)...      [data_catalog.py:1046]
                    INFO     Running node: compare_crx_cc_a4_deterioration_rf: <partial>() -> None      [node.py:420]
[11/06/26 14:02:23] INFO                                                                   [rf_check.py:59]
                    === RF A4 OUTPUT START ===
                    model_id: cc_60_180
                    rows old / new: 311277 / 311277
                    same schema: True
                    rows only in old: 0
                    rows only in new: 0
                    rows whose det_state differs: 0
                      early_payment_default -> early_payment_default: 20805
                      repeat_delinquent -> repeat_delinquent: 25535
                      slow_roller -> slow_roller: 57349
                      stabilized -> stabilized: 35342
                      straight_roller_early_life -> straight_roller_early_life: 61696
                      straight_roller_seasoned -> straight_roller_seasoned: 107503
                      unknown -> unknown: 3047
                    === RF A4 OUTPUT END ===
        INFO     Completed node: compare_crx_cc_a4_deterioration_rf      [runner.py:245]
        INFO     Completed 5 out of 5 tasks      [runner.py:246]
        INFO     Pipeline execution completed successfully in 183.8 sec.      [runner.py:119]
[root@lvenaacaai402b retail.collections.risk_profiling]# 
````
The other terminal tabs on the right side are `python`, `bash`, `bash` (the last is selected).

## Notes on specific spots
- Checks that pass: the seven "RF A4" lines add up to 311,277 (20,805 + 25,535 + 57,349 + 35,342 + 61,696 + 107,503 + 3,047), equal to "rows old / new" and to 0 rows differing; the state distribution above it (1,599 + 3,259 + 1,273 + 2,937 + 8,724 + 60 = 17,852 of the latest month's 19,292 rows) leaves 1,440 (7.5%) for the `early_payment_default` row that is cut off above the visible part, which fits the 92.5% already shown.
- Photo 2 log times: Spark WARN at 14:01:55 (`26/11/06` is Spark's yy/MM/dd format), node `rf_cc.build_crx_cc_a4_deterioration` completed 14:02:05 (10 s later), comparison printed at 14:02:23; pipeline total 183.8 sec; Completed 5 out of 5 tasks. The taskbar clock of the photo is 6:02 PM Dubai time = 14:02 UTC.
- The Spark warning text is long and cut off by the right edge of the photo at several places; the part after `... - 1))) AND ...` is read from the wrapped lines and may have small errors in the `#221 / #223 / #234 / #249` expression ids. The structure is: `isnotnull(year(last_day(make_date(...first_month_idx...))) * 12 + month(...) - 1)` AND the same for `last_month_idx` AND `build_status = ok`, all on the output of `_udf(_rows, _first_raw, _global_min)`.
- Meaning (my reading, given in chat): the Kedro warning is cosmetic (dot in dataset names; either use `__` or a real Kedro namespace); the Spark warning means the join in the `rf_cc` A4 node has a condition built only from the Python UDF result (no key columns on both sides), so Spark moves the UDF out and runs it as a cross join plus filter. It ran fast here but can be expensive on bigger models. Fix: compute the UDF fields once into plain columns before the join.
- Photo 1 other content: a laptop screen in the background shows a "Meet Nova! AI HR assistant" banner (not relevant).
- Note on `globals_dev.yml` line 17: the active `model_id` is `"cc_60_180"` (the modified line, gutter bar), with `cc_180_plus`, `rl_60_180` and `rl_180_plus` commented out.
- OCR-risk digits: all counts in the RF A4 block (311277, 20805, 25535, 57349, 35342, 61696, 107503, 3047), the state distribution (1599, 3259, 1273, 2937, 8724, 60), and 183.8 sec.
