# UC1 timelines — handoff for the builder session

> **STATUS: `cc_60_180` measured in PROD on 2026-11-17** (`uc1_timelines_results_cc_60_180.md`, committed `d6ce67e7`).
> Sections 1-6 and 8-10 are filled from it. **Not yet run:** B4-B6 for `cc_180_plus`, `r1_60_180`, `r1_180_plus` (marked
> `NOT RUN`); the table profile (B1-B3) does not depend on `model_id`.

**Labels.** **[V]** measured in PROD by the snippet. **[code]** read in code: `path:line` on the UC1 branch
`origin/eda/explore-dcore @ 37c9cac0` (a branch of the same GitHub repo as ours, `AdvancedAnalyticsCenterofExcellence/
retail.collections.risk_profiling`; the knowledge base was written from `dc75eb7e`, 47 files older), or on our branch
`feature/persona_refactor @ 3625b14d`. **[doc]** from a document (path given). Anything not found is `NOT FOUND` with
where it was looked for.

**Sample warning.** UC1 extraction ran on a sample only (11,920 of 147,004 pooled conversations, 8.1%, a purposive
UC2-scoped draw) [doc `docs/context/reference/uc1_data_kb.md`]. Every count in section 1 and 3-6 is a sample statistic.
Formats, value sets, rules, keys and grain are structural.

Source paths in the UC1 branch below are relative to its repo root. Write locations in the UC1 code are
`${_project.hdfs_path}/UC1/file_store/...` (their own root, `conf/base/catalog/catalog.yml:525-552`); we read only the
shared copy `hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev/shared/05_feat/file_store`.

---

## 1. What arrived

```text
table (under `current/outputs/timelines/`)   | in shared store | part files | bytes     | latest part mtime    | rows
---------------------------------------------+-----------------+------------+-----------+----------------------+--------
`latest_flags`                               | yes             | 1          | 433,105   | 2026-11-16 13:28 UTC | 11,920
`simple_signal_aggregation`                  | yes             | 10         | 389,563   | 2026-11-16 13:28 UTC | 5,751
`signal_level_conflicts`                     | yes             | 10         | 1,884,125 | 2026-11-16 13:28 UTC | 262,240
`time_weighted_aggregation_scores` (not      | NO              |            |           |                      |
requested; the only dated table)             |                 |            |           |                      |

`time_weighted_signal_aggregation` (not      | NO              |            |           |                      |
requested)                                   |                 |            |           |                      |
```

Source [V]: B1, B2 (`cc_60_180` run, 2026-11-17). All three arrived together (same minute) after the 2026-11-16 profile;
sample warning: 11,920 conversations, 5,751 customers. The shared-store listing in `data/input/UC1/filestore.md` names
only `metadata`, `extracted_signals`, `agent_remarks_extracted_signals` and `uc2/signal_corroboration` [doc]; the
timelines were absent when profiled on 2026-11-16 [doc KB §2].

---

## 2. Table reference

All three read `fs_metadata` (= `metadata`) and `fs_current_extracted_signals` (= `current/outputs/extracted_signals`)
only [code `src/enbd_collections/pipeline_registry.py:368-410`]. **None reads the agent-remark ledger.** All three are
full recomputes with `mode: overwrite` [code `catalog.yml:525-541`], rerun by hand (no trigger) [doc
`docs/roadmap/P2.1-03-kedro-wiring-PLAN.md:95`]. Kedro pipeline names = registry keys `latest_flags`,
`simple_signal_aggregation`, `signal_level_conflicts` [code `pipeline_registry.py:536-538`].

### 2.1 `simple_signal_aggregation` — the only customer-level table

- **Writer** [code]: `src/data_engineering/nodes/post_extraction_transformations.py:50`
  `build_simple_signal_aggregation_node` → `_build_signal_aggregation_rows` `:59`; catalog
  `fs_current_simple_signal_aggregation` (`catalog.yml:531`); path
  `current/outputs/timelines/simple_signal_aggregation`. It `collect()`'s the joined rows to the driver and builds rows
  in Python.
- **Grain** [code `:59-85`]: one row per `cif_id` that has at least one extracted conversation with a metadata row
  (inner join). `cif_id` is `str(record["cif_id"])`, so a null `cif_id` becomes the literal string `"None"` [doc
  `docs/roadmap/P2.3-02-confidence-workspace/work/h1-f-consumers-decision-rules.md` C30]. Uniqueness [V]: 5,751 rows =
  5,751 distinct `cif_id` (unique); no literal `None`, no empty.
- **Columns** [code `post_extraction_transformations.py:19-25`, `schema_verifier.py:302-320`]: `cif_id` string NOT NULL,
  `conversationid` string NOT NULL, `signals_json` string NOT NULL. Measured schema [V]: all three `string`, **nullable
  = true** (the verifier expects NOT NULL), 0.0% null.
- `conversationid` = the customer's latest extracted conversation (max of `(str(conversationstart), conversationid)`)
  [code `:95-118`]. It is the only link to a date: no date column exists.
- `signals_json` = `{"<signal>": "NA" | {"level": "<one level>"}}` for all 8 signals, validated by
  `SignalAggregationSchema` (`extra="forbid"`; `src/data_engineering/nodes/signal_aggregation_schema.py`). No `notes`
  key. No confidence, count, date or `request_type`.
- **Value sets** [code `src/signal_utils/signal_extraction/schema.py`; doc KB §4.1]: levels per signal as in the KB;
  `repayment_specifics` level is the full encoded string (`amount_mentioned:<n>`, `date_specific:<YYYY-MM-DD>`,
  `plan_structure_mentioned`). Measured [V] (customers per aggregated level; `NA` = not detected): all 5,751 rows carry
  exactly the 8 signal keys, 0 unparseable.

  ```text
  signal              | levels (customers)
  --------------------+-------------------------------------------------------------------------------------------------
  payment_capacity    | NA 2,049; partial 1,797; full 1,649; none 256
  payment_intent      | NA 1,363; payback_full 2,284; with_delay 1,143; partial 902; no_payment 59
  delinquency_reason  | NA 3,037; has_employment 1,307; lost_employment 649; increased_obligations 454;
                      | reduced_employment 304

  dispute             | NA 4,450; system_problem 1,173; other 92; customer_scammed 36
  request             | NA 3,366; detected 2,385
  payment_period      | NA 3,346; weeks 1,176; salary_cycle_dependent 1,146; months_or_longer 83
  repayment_specifics | NA 2,513; `amount_mentioned:<n>` 2,407; `date_specific:<date>` 740; `plan_structure_mentioned`
                      | 91

  fraudulent_customer | NA 5,751
  ```

- **Inputs** [code `:121-142`]: transcript signals only. `_parse_levels` keeps a detection only if the signal value is a
  list (or one dict) of dicts with a `level`. **Legacy-format rows (flat string values) contribute no level at all**;
  their customer still gets a row (the latest-conversation index is built from every joined row) with every signal
  `"NA"`. Remark-only customers have no row. Measured [V]: 452 customers have only legacy conversations; all 452 have a
  row, **0** with any non-NA level. Of 1,131 remark CIFs, 413 are remark-only: **0** have a row here (or in the grid).
  All 11,920 conversations' customers are covered (see Build status).
- **How time enters** [code]: **it does not.** No date column, no as-of parameter, no window, no recency weight; the
  aggregate is over the customer's entire extracted history (`docs/milestone-planning/specs/P3.2-03.md:111`: "do not
  filter by `is_latest`"). A value for a past date cannot be read from the table; it can only be recomputed from
  `extracted_signals` + `metadata` by filtering `conversationstart` first (the function `_select_aggregated_level` takes
  any observation list). Window parameters: NONE for these three tables.
- **Pick across conversations** [code `:145-157`]: count **detections** (one per `{level,...}` object, not one per
  conversation; the same level with different confidence is two detections [doc KB §4.2]); modal level wins; **tie → the
  level whose latest occurrence is later** (compare `(str(conversationstart), conversationid)`). Confidence is ignored;
  the ordered-signal conservative rank is not used here. For `repayment_specifics` the unit is the full encoded string,
  so two different amounts are two levels.
- **`request_type`**: dropped; `request` is `{"level":"detected"}` or `"NA"`. **`repayment_specifics`**: one modal
  encoded string out of all three slots (amount, date, plan), not one per slot.
- **Confidence**: not carried. (UC1's plan for Latest / Historic Consistency / Estimated value / High-Medium-Low is
  design only [doc KB §6].)
- **Build status**: built and run; last evidenced output 2,033 customers on 2026-10-12, when the ledger held 5,140
  conversations; the ledger has since grown to 11,920, so an unrefreshed copy is stale [doc `../h1-j-execution-state.md`
  C9, C32]. Measured [V]: **not stale**: 0 extracted CIFs (via `index`) are missing from it and 0 of its CIFs are
  outside the extracted set (5,751 = 5,751); written 2026-11-16 13:28 UTC against the full 11,920-conversation ledger.
  (The 6,169 'extracted conversations not in table' in B3 is expected: it stores one `conversationid` per customer.)

### 2.2 `latest_flags` — per conversation, not per customer

- **Writer** [code]: `post_extraction_transformations.py:28` `build_latest_flags_node`; catalog
  `fs_current_latest_flags` (`catalog.yml:525`).
- **Grain** [code `:28-41`]: one row per **extracted conversation** that has a metadata row. Columns exactly
  `conversationid` string, `is_latest` boolean NOT NULL [code `schema_verifier.py:280-299`]. `is_latest` = `row_number()
  == 1` over `partitionBy(cif_id) orderBy(conversationstart desc)` among the customer's **extracted** conversations
  (ties on `conversationstart` are arbitrary; all null-`cif_id` conversations share one partition). Values: `true` /
  `false`.
- **Inputs**: transcript ledger ids + metadata; legacy-format conversations are included (only ids are used). No signal
  content.
- **Time**: none (no date column; `is_latest` is "latest extracted call", not "latest call"; as of the last refresh).
- **Pick / confidence / request_type / repayment_specifics**: not applicable (a flag only).
- **Build status**: built and run; 5,140 conversations on 2026-10-12 [doc C8]. Measured [V]: 11,920 rows = the 11,920
  extracted conversations, unique; `is_latest` true 5,751 (= one per customer), false 6,169; 1,437 legacy conversations
  included; 0 missing, 0 extra; columns nullable = true.

### 2.3 `signal_level_conflicts` — per conversation × 22 slots

- **Writer** [code]: `post_extraction_transformations.py:43` `build_signal_level_conflicts_node` →
  `src/data_engineering/extraction/utils.py:71` `build_signal_level_conflict_grid_spark`; catalog
  `fs_current_signal_level_conflicts` (`catalog.yml:537`).
- **Grain** [code `utils.py:43-50,71-125`]: one row per **extracted conversation × slot** (22 slots = every
  `signal:level` of the base schema: reason 4, dispute 3, request 1, intent 4, capacity 3, period 3, fraud 1,
  repayment_specifics 3). Expected 22 rows per conversation. Key `(conversationid, signal, value)`; `cif_id` is a
  nullable left join to metadata. Measured [V]: 262,240 rows = 11,920 conversations × 22 (every conversation has exactly
  22 rows); key unique; `detected` 33,428 / `not-detected` 228,812; `conflicting_signals` non-null in 1,802 rows (350
  reason, 37 dispute, 18 capacity, 232 intent, 471 period, 694 repayment_specifics); no (conversation, signal, slot) has
  more than one `detected` row; `fraudulent_customer` 0 detected; request `detected` 3,894.
- **Columns** [code `utils.py:43-50`]: `cif_id` string, `conversationid` string, `signal` string NOT NULL, `value`
  string, `observation` string NOT NULL (`detected` | `not-detected`), `conflicting_signals` string (null, or `conflict:
  <level>, conflict: <level>`). No confidence, no `request_type`, no date. (Docs disagree on 4 / 6 columns:
  `h1-a-observation-records.md` K5; the code has 6.) Measured [V]: types as coded, all nullable = true, `cif_id` 5,751
  distinct, never null.
- **Meaning of `value`**: for a `detected` row, the level the conversation-level resolver chose; for a `not-detected`
  row, the slot's own level name. For `repayment_specifics` a detected row's `value` is the encoded string
  (`amount_mentioned:<n>` ...); the slot is the part before `:`. Only the **primary** level of a signal in a
  conversation is `detected`; the other levels seen in that conversation appear only as text in `conflicting_signals` of
  the detected row, and their own slot rows stay `not-detected`.
- **Within-conversation pick** [code `utils.py:323-329`]: per `(conversationid, signal)` (per slot for
  repayment_specifics) order by confidence (`high` > `low`; `CONFIDENCE_ORDER` `schema.py:29`), then **lowest ordered
  rank first** (capacity none 0 < partial 1 < full 2; intent no_payment 0 < with_delay = partial 1 < payback_full 2;
  every other signal rank 0, `utils.py:375-384`), then latest span end, latest span start, then level name; row 1 wins.
  `request_type` creates no conflicts.
- **Inputs**: transcript signals; **only list-format values**: the span flattener keeps a signal only if its JSON text
  starts with `[` (`utils.py:223`). A legacy conversation is in the grid (the universe is every `extracted_signals` row)
  with **all 22 slots `not-detected`**.
- **Time**: none. But the table is per conversation, so a past date is reproducible by joining
  `metadata.conversationstart` and filtering.
- **Build status**: built (wired; unit tests in `src/tests/data_engineering/extraction/test_utils.py`) but **no run
  record on any data**: no output, count or date found in any notebook or doc [doc `../h1-j-execution-state.md` C10].
  Measured [V]: **it was run**, on the full ledger (262,240 rows, 2026-11-16 13:28 UTC); the UC1 docs' 'no run record'
  is out of date. 1,437 legacy conversations are in it with 0 `detected` rows; 0 remark-only customers.

### 2.4 Not requested but relevant: the dated tables

- `time_weighted_aggregation_scores`: [code `src/data_engineering/nodes/time_weighted_aggregation_scores.py:328`,
  catalog `catalog.yml:543`, registry `:417`]. Grain `as_of_date × cif_id × signal × level`; columns `as_of_date` date,
  `cif_id` string, `signal`, `level`, `support` double, `contest` double, `source_normalised_support` double (SPEC
  `docs/roadmap/P3.3-02-timeline-aggregation-scores-dataset-SPEC.md`). Inputs: transcripts, **agent remarks**, UC2
  corroboration (`pipeline_registry.py:417-434`). Time: month-end `as_of_date` from
  `time_weighted_aggregation.observation_start_month` (`2026-01`) to the last day of the month of the latest evidence;
  evidence with `observed_at <= as_of_date` is used (**inclusive**: a call on the month-end day itself counts,
  `:212,359`); exponential weight `0.5 ** (days / half_life_days)`, `half_life_days` `60.0`
  (`conf/base/parameters.yml:59-61`). Source weights: transcript 3.0, remark 1.0 (`:15-16`). No confidence class
  (High/Medium/Low is assigned "downstream"). Built status: wired, with unit tests
  (`src/tests/data_engineering/test_p3_3_02_...`); **no run record found** in docs or notebooks.
- `time_weighted_signal_aggregation`: [code `src/data_engineering/nodes/time_weighted_signal_aggregation.py:19`,
  `catalog.yml:549`] one estimated level per `as_of_date × cif_id × signal` (`estimated_value`, `runner_up`, `support`,
  `contest`, `source_normalised_support`); excludes `repayment_specifics`; `estimated_value` null when support <= 0. No
  run record found.
- Presence in the shared store [V]: **neither exists** (B1), so there is no dated table to read; B4 extras not
  applicable.

### 2.5 Differences between code and data

[V] Code vs data, everything else matches (column names, types, value sets, 22 rows per conversation, `None` literal
absent):
1. All columns are `nullable = true` in the files; the verifier (`schema_verifier.py`) and the node docstrings say NOT
   NULL for `is_latest` and the three `simple_signal_aggregation` columns.
2. `signal_level_conflicts` exists with data although the UC1 docs record no run.
3. `time_weighted_*` are wired in code but not in the shared store.
4. `simple_signal_aggregation` has 5,751 customers (docs: 2,033 on 2026-10-12): it was rebuilt on the full ledger.
5. Detected counts in the grid reproduce the KB's per-signal conversation counts (capacity 2,278 + 548 + 3,003 = 5,829;
   intent 3,308 + 2,255 + 1,684 + 151 = 7,398; request 3,894).

---

## 3. Time

**Code verdict [code];** none of the three tables has an as-of date, window or recency parameter.
`simple_signal_aggregation` is the customer's full history as of the last refresh; `latest_flags` and
`signal_level_conflicts` are per conversation and can be filtered by joining `metadata.conversationstart`. The only
dated tables are the `time_weighted_*` pair (monthly, 60-day half-life, `<=` inclusive). Past dates are reproducible
only by recomputing from `extracted_signals` + `metadata` (UC1 logic is in `_select_aggregated_level`) or from the
time-weighted pair.

**B4 numbers [V]** (`cc_60_180` run; the snippet rebuilds dates from `metadata.conversationstart`; the stored
`conversationid` of every `simple_signal_aggregation` row matches the rebuilt latest conversation: 0 differences). Calls
span 2026-03-06..2026-07-16.

```text
month end  | rows | latest conversation on/after   | ALL conversations on/after (past | has a conversation strictly
           |      | (published value rests on a    | value would be empty)            | before (past value recomputable)
           |      | later call)                    |                                  |
-----------+------+--------------------------------+----------------------------------+---------------------------------
2026-01-31 | 5751 | 5751                           | 5751                             | 0
2026-02-28 | 5751 | 5751                           | 5751                             | 0
2026-03-31 | 5751 | 5426                           | 5018                             | 733
2026-04-30 | 5751 | 4972                           | 4339                             | 1412
2026-05-31 | 5751 | 4479                           | 3886                             | 1865
2026-06-30 | 5751 | 3185                           | 2403                             | 3348
2026-07-31 | 5751 | 0                              | 0                                | 5751
2026-08-31 | 5751 | 0                              | 0                                | 5751
```

`latest_flags`: 5,751 rows flagged `is_latest`; flagged rows dated on/after the month end: 5,751 / 5,751 / 5,426 / 4,972
/ 4,479 / 3,185 / 0 / 0 (Jan..Aug). `signal_level_conflicts` conversations dated strictly before the month end: 0 / 0 /
1,376 / 3,119 / 4,655 / 7,577 / 11,920 / 11,920 (of 11,920). Extracted conversations dated exactly ON a month end:
2026-03-31 100; 04-30 64; 06-30 408; none on the others. `time_weighted_*`: absent.

**Verdict [V]: usable for the latest months only (2026-07-31 and 2026-08-31, where no row rests on a later call); not
usable as is for 2026-01..2026-06** (3,185 to 5,751 of 5,751 rows rest on a call dated on/after the month end, and for
Jan/Feb no call precedes the date at all); a past month's value can be had only by recomputing from `extracted_signals`
+ `metadata` filtered by date, or by filtering the per-conversation `signal_level_conflicts` / `latest_flags` through
`metadata`, not from `simple_signal_aggregation`.

---

## 4. No evidence

[code] The three cases, for a signal:

```text
case                           | `simple_signal_aggregation`  | `signal_level_conflicts`                 | `latest_flags`
-------------------------------+------------------------------+------------------------------------------+---------------
customer has extracted         | row, signal `"NA"`           | rows for the conversations, the signal's | row(s)
conversations, signal not      |                              | slots `not-detected`                     |
detected in any                |                              |                                          |

customer has conversations but | no row                       | no rows                                  | no row
none extracted                 |                              |                                          |

customer has no conversation   | no row                       | no rows                                  | no row
customer has only              | row, all signals `"NA"`      | rows, all 22 slots `not-detected`        | row(s)
legacy-format conversations    |                              |                                          |

customer has only remark       | no row                       | no rows                                  | no row
evidence                       |                              |                                          |
```

The second and third cases are indistinguishable in all three tables; only `index` / `metadata` tell them apart.
Confirmed on data [V] (`cc_60_180`, latest month 2026-08-31, spine rows, capacity; intent is similar): no CIF 0; **no
conversation 13,387**; conversation but none extracted **4,848**; extracted but no row **0** (state absent in every
month); row with signal `NA` 367; row with a level 690. All 452 legacy-only customers have a row with every signal `NA`,
indistinguishable in the table from "extracted, signal not detected". Remark-only customers (413) have no row. States
'no conversation' and 'none extracted' both mean no row; only `index`/`metadata` separate them. Tables: section 6.

---

## 5. Key and join

- UC1 side [doc KB §2; code]: `cif_id` string (8-digit in `index`); `"None"` string possible in
  `simple_signal_aggregation`.
- Our side [code `src/enbd_collections/pipelines/crx_persona/_common.py:224-271`]: `crx_{cc,rl}_obs_base.cif_id` is
  passed through from the spine unchanged (CC: `max(cif_id)` per account-month). The spine's type is not set in the
  persona code (`bureau_cif_bridge.py:57` casts the bureau side to `long`). RL rows without `cif_id` are kept [code
  `_common.py:228`].
- **[V]:** `crx_cc_obs_base.cif_id` is Spark **string**. `index`, `metadata`, `simple_signal_aggregation`,
  `signal_level_conflicts`: string, 100% length 8, 0.0% leading zero, 0 non-digit, 0 null (147,004 / 147,004 / 5,751 /
  262,240 rows). The obs base's own length / leading-zero distribution was not measured.
- **Join [V]:** exact string join = left-padded to 8 = leading zeros stripped: 999 of 18,731 spine customers (**5.3%**)
  in the latest month (1,057 of 19,292 rows, 5.5%), identical for the three tables. **No conversion is needed** (cast to
  string and trim is what the snippet did). `cif_id` is never null in the obs base (0 rows without a CIF in all 8
  months) for `cc_60_180`.

---

## 6. Reach and first sizes

**[V] `cc_60_180` only** (`cc_180_plus`, `r1_60_180`, `r1_180_plus`: **NOT RUN**). Rows = account × observation month;
'row' = customer has a row (the three tables cover the same 5,751 customers). 'all convs before obs' = the published
value rests only on calls strictly before the date (the as-of-valid share).

### B5

```text
obs month  | rows  | customers | rows w/o  | rows w/ row in               | rows w/ row in  | rows w/ row in
           |       |           | cif_id    | simple_signal_aggregation    | latest_flags    | signal_level_conflicts
-----------+-------+-----------+-----------+------------------------------+-----------------+---------------------------
2026-01-31 | 14664 | 14225     | 0         | 391 (2.7%)                   | 391 (2.7%)      | 391 (2.7%)
2026-02-28 | 14576 | 14143     | 0         | 369 (2.5%)                   | 369 (2.5%)      | 369 (2.5%)
2026-03-31 | 14455 | 14024     | 0         | 354 (2.4%)                   | 354 (2.4%)      | 354 (2.4%)
2026-04-30 | 14671 | 14240     | 0         | 467 (3.2%)                   | 467 (3.2%)      | 467 (3.2%)
2026-05-31 | 15890 | 15412     | 0         | 645 (4.1%)                   | 645 (4.1%)      | 645 (4.1%)
2026-06-30 | 16982 | 16492     | 0         | 837 (4.9%)                   | 837 (4.9%)      | 837 (4.9%)
2026-07-31 | 18397 | 17854     | 0         | 969 (5.3%)                   | 969 (5.3%)      | 969 (5.3%)
2026-08-31 | 19292 | 18731     | 0         | 1057 (5.5%)                  | 1057 (5.5%)     | 1057 (5.5%)

obs month  | customers w/ row in       | customers w/ | customers w/ row in    | non-empty  | non-empty  | capacity
           | simple_signal_aggregation | row in       | signal_level_conflicts | capacity   | intent     | AND all
           |                           | latest_flags |                        |            |            | convs
           |                           |              |                        |            |            | before obs
-----------+---------------------------+--------------+------------------------+------------+------------+-----------
2026-01-31 | 375 (2.6%)                | 375 (2.6%)   | 375 (2.6%)             | 177 (1.2%) | 210 (1.4%) | 0 (0.0%)
2026-02-28 | 351 (2.5%)                | 351 (2.5%)   | 351 (2.5%)             | 162 (1.1%) | 190 (1.3%) | 0 (0.0%)
2026-03-31 | 336 (2.4%)                | 336 (2.4%)   | 336 (2.4%)             | 153 (1.1%) | 190 (1.3%) | <10 (<10)
2026-04-30 | 441 (3.1%)                | 441 (3.1%)   | 441 (3.1%)             | 192 (1.3%) | 225 (1.5%) | 65 (0.4%)
2026-05-31 | 609 (4.0%)                | 609 (4.0%)   | 609 (4.0%)             | 338 (2.1%) | 394 (2.5%) | 239 (1.5%)
2026-06-30 | 789 (4.8%)                | 789 (4.8%)   | 789 (4.8%)             | 486 (2.9%) | 553 (3.3%) | 446 (2.6%)
2026-07-31 | 914 (5.1%)                | 914 (5.1%)   | 914 (5.1%)             | 569 (3.1%) | 644 (3.5%) | 569 (3.1%)
2026-08-31 | 999 (5.3%)                | 999 (5.3%)   | 999 (5.3%)             | 690 (3.6%) | 772 (4.0%) | 690 (3.6%)

obs month  | intent AND all convs before obs | has an extracted conv before obs
-----------+---------------------------------+---------------------------------
2026-01-31 | 0 (0.0%)                        | 0 (0.0%)
2026-02-28 | 0 (0.0%)                        | 0 (0.0%)
2026-03-31 | <10 (<10)                       | 51 (0.4%)
2026-04-30 | 82 (0.6%)                       | 301 (2.1%)
2026-05-31 | 279 (1.8%)                      | 551 (3.5%)
2026-06-30 | 505 (3.0%)                      | 799 (4.7%)
2026-07-31 | 644 (3.5%)                      | 969 (5.3%)
2026-08-31 | 772 (4.0%)                      | 1057 (5.5%)
```

Evidence state of spine rows (timeless; capacity):

```text
obs month  | 2_no_conversation | 3_conversation_none_extracted | 5_row_signal_NA | 6_row_signal_level
-----------+-------------------+-------------------------------+-----------------+-------------------
2026-01-31 | 13861             | 412                           | 214             | 177
2026-02-28 | 13839             | 368                           | 207             | 162
2026-03-31 | 13760             | 341                           | 201             | 153
2026-04-30 | 13600             | 604                           | 275             | 192
2026-05-31 | 13528             | 1717                          | 307             | 338
2026-06-30 | 13384             | 2761                          | 351             | 486
2026-07-31 | 13493             | 3935                          | 400             | 569
2026-08-31 | 13387             | 4848                          | 367             | 690
```

Intent:

```text
obs month  | 2_no_conversation | 3_conversation_none_extracted | 5_row_signal_NA | 6_row_signal_level
-----------+-------------------+-------------------------------+-----------------+-------------------
2026-01-31 | 13861             | 412                           | 181             | 210
2026-02-28 | 13839             | 368                           | 179             | 190
2026-03-31 | 13760             | 341                           | 164             | 190
2026-04-30 | 13600             | 604                           | 242             | 225
2026-05-31 | 13528             | 1717                          | 251             | 394
2026-06-30 | 13384             | 2761                          | 284             | 553
2026-07-31 | 13493             | 3935                          | 325             | 644
2026-08-31 | 13387             | 4848                          | 285             | 772
```

### B6 (latest month 2026-08-31, 19,292 rows; cells under 10 masked)

**capacity value x a1_state**

```text
cap_v   | a1_state | rows  | rows (all convs before obs)
--------+----------+-------+----------------------------
NA      | high     | 14    | 14
NA      | low      | 118   | 118
NA      | moderate | 90    | 90
NA      | unknown  | 145   | 145
full    | high     | <10   | <10
full    | low      | 36    | 36
full    | moderate | 35    | 35
full    | unknown  | 51    | 51
no_row  | high     | 276   | 0
no_row  | low      | 4598  | 0
no_row  | moderate | 2593  | 0
no_row  | unknown  | 10768 | 0
none    | high     | <10   | <10
none    | low      | 49    | 49
none    | moderate | 26    | 26
none    | unknown  | 68    | 68
partial | high     | 15    | 15
partial | low      | 147   | 147
partial | moderate | 106   | 106
partial | unknown  | 151   | 151
```

**intent value x a3_state**

```text
int_v        | a3_state                     | rows  | rows (all convs before obs)
-------------+------------------------------+-------+----------------------------
NA           | payment_credibility_high     | 12    | 12
NA           | payment_credibility_low      | 194   | 194
NA           | payment_credibility_moderate | 69    | 69
NA           | payment_credibility_unknown  | 10    | 10
no_payment   | payment_credibility_low      | 28    | 28
no_payment   | payment_credibility_moderate | <10   | <10
no_payment   | payment_credibility_unknown  | <10   | <10
no_row       | payment_credibility_high     | 458   | 0
no_row       | payment_credibility_low      | 12063 | 0
no_row       | payment_credibility_moderate | 3510  | 0
no_row       | payment_credibility_unknown  | 2204  | 0
partial      | payment_credibility_high     | <10   | <10
partial      | payment_credibility_low      | 141   | 141
partial      | payment_credibility_moderate | 46    | 46
partial      | payment_credibility_unknown  | <10   | <10
payback_full | payment_credibility_high     | <10   | <10
payback_full | payment_credibility_low      | 143   | 143
payback_full | payment_credibility_moderate | 38    | 38
payback_full | payment_credibility_unknown  | <10   | <10
with_delay   | payment_credibility_high     | <10   | <10
with_delay   | payment_credibility_low      | 256   | 256
with_delay   | payment_credibility_moderate | 79    | 79
with_delay   | payment_credibility_unknown  | <10   | <10
```

**dispute** (value NA / no_row = not present)

```text
disp_v           | rows  | rows (all convs before obs)
-----------------+-------+----------------------------
NA               | 787   | 787
customer_scammed | 16    | 16
no_row           | 18235 | 0
other            | 25    | 25
system_problem   | 229   | 229
```

**request** (value NA / no_row = not present; request_type not carried by simple_signal_aggregation)

```text
req_v    | rows  | rows (all convs before obs)
---------+-------+----------------------------
NA       | 416   | 416
detected | 641   | 641
no_row   | 18235 | 0
```

**intent x kind of the single aggregated `repayment_specifics` level** (simple_signal_aggregation holds ONE modal level
of the three slots)

```text
int_v        | rs_kind                  | rows  | rows (all convs before obs)
-------------+--------------------------+-------+----------------------------
NA           | NA                       | 284   | 284
NA           | amount_mentioned         | <10   | <10
no_payment   | NA                       | 28    | 28
no_payment   | amount_mentioned         | <10   | <10
no_payment   | plan_structure_mentioned | <10   | <10
no_row       | no_row                   | 18235 | 0
partial      | NA                       | 22    | 22
partial      | amount_mentioned         | 128   | 128
partial      | date_specific            | 10    | 10
partial      | plan_structure_mentioned | 34    | 34
payback_full | NA                       | 33    | 33
payback_full | amount_mentioned         | 121   | 121
payback_full | date_specific            | 33    | 33
payback_full | plan_structure_mentioned | <10   | <10
with_delay   | NA                       | 95    | 95
with_delay   | amount_mentioned         | 153   | 153
with_delay   | date_specific            | 89    | 89
with_delay   | plan_structure_mentioned | 12    | 12
```

**intent x repayment_specifics slots detected in ANY of the customer's conversations** (from signal_level_conflicts;
amounts / dates themselves are not reported):

```text
int_v        | any amount_mentioned | any date_specific | any plan_structure_mentioned | rows
-------------+----------------------+-------------------+------------------------------+------
NA           | False                | False             | False                        | 284
NA           | True                 | False             | False                        | <10
no_payment   | False                | False             | False                        | 28
no_payment   | True                 | False             | False                        | <10
no_payment   | True                 | False             | True                         | <10
no_payment   | True                 | True              | False                        | <10
no_row       | False                | False             | False                        | 18235
partial      | False                | False             | False                        | 22
partial      | False                | False             | True                         | <10
partial      | False                | True              | False                        | <10
partial      | False                | True              | True                         | <10
partial      | True                 | False             | False                        | 52
partial      | True                 | False             | True                         | 31
partial      | True                 | True              | False                        | 37
partial      | True                 | True              | True                         | 37
payback_full | False                | False             | False                        | 33
payback_full | False                | False             | True                         | <10
payback_full | False                | True              | False                        | 22
payback_full | True                 | False             | False                        | 59
payback_full | True                 | False             | True                         | <10
payback_full | True                 | True              | False                        | 50
payback_full | True                 | True              | True                         | 20
with_delay   | False                | False             | False                        | 95
with_delay   | False                | False             | True                         | <10
with_delay   | False                | True              | False                        | 65
with_delay   | False                | True              | True                         | <10
with_delay   | True                 | False             | False                        | 67
with_delay   | True                 | False             | True                         | 16
with_delay   | True                 | True              | False                        | 70
with_delay   | True                 | True              | True                         | 30
```

Confidence split: none of the three tables carries a confidence column [code], so no split exists; the snippet's column
check confirms it (`'NONE'` for all three). `request_type` is not carried by any of the three [code]. Sample warning
applies.

---

## 7. Final output table

`data/input/UC1/output_schema.md` (a local, git-ignored file; every cell copied verbatim from the file's tab-separated
rows, laid out here as wrapped text tables of at most 120 columns: ids 1-55 and 56-86 are the file's two header blocks).
It is the UC1/UC2 delivery schema: one row per `(cif_id, account_id, observation date)`.

```text
field id | field                                                   | type       | Example value | Desc
---------+---------------------------------------------------------+------------+---------------+-----------------------
1        | cif_id                                                  | numeric    | 123           |
2        | account_id                                              | numeric    | 345           |
3        | observation date                                        | YYYY-MM-DD | 2026-11-30    | inference date
4        | persona                                                 | string     | persona value | This is the result of
         |                                                         |            |               | UC1/2 combination;
         |                                                         |            |               | value set unknown,
         |                                                         |            |               | will be provided by
         |                                                         |            |               | dec 11

5        | collection_action                                       | string     | TBD           | This is the result of
         |                                                         |            |               | UC1/2 combination;
         |                                                         |            |               | value set to be
         |                                                         |            |               | aligned on and created
         |                                                         |            |               | by dec 11 and will be
         |                                                         |            |               | provided

6        | SF_1_Deterioration                                      | string     | Default       | Synthetic feature 1
         |                                                         |            |               | value; format "value";
         |                                                         |            |               | reference table will
         |                                                         |            |               | be provided for values
         |                                                         |            |               | here

7        | SF_2_Locatability                                       | string     | In country    | Synthetic feature 2
         |                                                         |            |               | value; format "value";
         |                                                         |            |               | reference table will
         |                                                         |            |               | be provided for values
         |                                                         |            |               | here

8        | SF_3_Payment_credibility                                | string     | Promises kept | Synthetic feature 3
         |                                                         |            |               | value; format "value";
         |                                                         |            |               | reference table will
         |                                                         |            |               | be provided for values
         |                                                         |            |               | here

9        | SF_4_Ability                                            | string     | Moderate      | Synthetic feature 4
         |                                                         |            |               | value; format "value";
         |                                                         |            |               | reference table will
         |                                                         |            |               | be provided for values
         |                                                         |            |               | here

10       | last_transcript_date                                    | YYYY-MM-DD | 2026-10-02    |
11       | transcript_count                                        | numeric    | 5             |
12       | delinquency_reason_has_employment                       | string     | detected      | detected or
         |                                                         |            |               | not-detected

13       | delinquency_reason_has_employment_confidence            | string     | high          | high or medium or low
14       | delinquency_reason_increased_obligations                | string     | detected      | detected or
         |                                                         |            |               | not-detected

15       | delinquency_reason_increased_obligations_confidence     | string     | high          | high or medium or low
16       | delinquency_reason_lost_employment                      | string     | detected      | detected or
         |                                                         |            |               | not-detected

17       | delinquency_reason_lost_employment_confidence           | string     | high          | high or medium or low
18       | delinquency_reason_reduced_employment                   | string     | detected      | detected or
         |                                                         |            |               | not-detected

19       | delinquency_reason_reduced_employment_confidence        | string     | high          | high or medium or low
20       | dispute_customer_scammed                                | string     | detected      | detected or
         |                                                         |            |               | not-detected

21       | dispute_customer_scammed_confidence                     | string     | high          | high or medium or low
22       | dispute_other                                           | string     | detected      | detected or
         |                                                         |            |               | not-detected

23       | dispute_other_confidence                                | string     | high          | high or medium or low
24       | dispute_system_problem                                  | string     | detected      | detected or
         |                                                         |            |               | not-detected

25       | dispute_system_problem_confidence                       | string     | high          | high or medium or low
26       | fraudulent_customer_detected                            | string     | detected      | detected or
         |                                                         |            |               | not-detected

27       | fraudulent_customer_detected_confidence                 | string     | high          | high or medium or low
28       | payment_capacity_full                                   | string     | detected      | detected or
         |                                                         |            |               | not-detected

29       | payment_capacity_full_confidence                        | string     | high          | high or medium or low
30       | payment_capacity_none                                   | string     | detected      | detected or
         |                                                         |            |               | not-detected

31       | payment_capacity_none_confidence                        | string     | high          | high or medium or low
32       | payment_capacity_partial                                | string     | detected      | detected or
         |                                                         |            |               | not-detected

33       | payment_capacity_partial_confidence                     | string     | high          | high or medium or low
34       | payment_intent_no_payment                               | string     | detected      | detected or
         |                                                         |            |               | not-detected

35       | payment_intent_no_payment_confidence                    | string     | high          | high or medium or low
36       | payment_intent_partial                                  | string     | detected      | detected or
         |                                                         |            |               | not-detected

37       | payment_intent_partial_confidence                       | string     | high          | high or medium or low
38       | payment_intent_payback_full                             | string     | detected      | detected or
         |                                                         |            |               | not-detected

39       | payment_intent_payback_full_confidence                  | string     | high          | high or medium or low
40       | payment_intent_with_delay                               | string     | detected      | detected or
         |                                                         |            |               | not-detected

41       | payment_intent_with_delay_confidence                    | string     | high          | high or medium or low
42       | payment_period_months_or_longer                         | string     | detected      | detected or
         |                                                         |            |               | not-detected

43       | payment_period_months_or_longer_confidence              | string     | high          | high or medium or low
44       | payment_period_salary_cycle_dependent                   | string     | detected      | detected or
         |                                                         |            |               | not-detected

45       | payment_period_salary_cycle_dependent_confidence        | string     | high          | high or medium or low
46       | payment_period_weeks                                    | string     | detected      | detected or
         |                                                         |            |               | not-detected

47       | payment_period_weeks_confidence                         | string     | high          | high or medium or low
48       | repayment_specifics_amount_mentioned                    | string     | detected      | detected or
         |                                                         |            |               | not-detected

49       | repayment_specifics_amount_mentioned_confidence         | string     | high          | high or medium or low
50       | repayment_specifics_date_specific                       | string     | detected      | detected or
         |                                                         |            |               | not-detected

51       | repayment_specifics_date_specific_confidence            | string     | high          | high or medium or low
52       | repayment_specifics_plan_structure_mentioned            | string     | detected      | detected or
         |                                                         |            |               | not-detected

53       | repayment_specifics_plan_structure_mentioned_confidence | string     | high          | high or medium or low
54       | request_detected                                        | string     | detected      | detected or
         |                                                         |            |               | not-detected

55       | request_detected_confidence                             | string     | high          | high or medium or low

field id | field                                | type       | Example value           | Desc
---------+--------------------------------------+------------+-------------------------+--------------------------------
56       | SF_1_months_before_delinquency       | numeric    | 18                      | Months of our history before
         |                                      |            |                         | this delinquency began. 0 = it
         |                                      |            |                         | began before our history
         |                                      |            |                         | (cards: from Jan 2024)

57       | SF_1_prior_delinquency_count         | numeric    | 1                       | Earlier delinquencies that
         |                                      |            |                         | ended with the account up to
         |                                      |            |                         | date. Counted if 31+ DPD or 3+
         |                                      |            |                         | months overdue; depth not shown

58       | SF_1_months_since_61_dpd             | numeric    | 5                       | Months since the account first
         |                                      |            |                         | reached 61+ DPD in this
         |                                      |            |                         | delinquency

59       | SF_2_location_reason                 | string     | uae_recent              | abroad_latest (latest evidence
         |                                      |            |                         | is abroad) /
         |                                      |            |                         | travelled_then_quiet (travel
         |                                      |            |                         | purchase, no UAE evidence later
         |                                      |            |                         | than 3 months after it, none in
         |                                      |            |                         | the last month) / uae_recent
         |                                      |            |                         | (UAE evidence in the period) /
         |                                      |            |                         | uae_too_old / no_evidence

60       | SF_2_reachability_reason             | string     | call_connected          | call_connected (a call got
         |                                      |            |                         | through in the period) /
         |                                      |            |                         | calls_failing (last 3 call
         |                                      |            |                         | days, 6 at 180+, all failed in
         |                                      |            |                         | the period, none connected
         |                                      |            |                         | since) / no_recent_connection
         |                                      |            |                         | (no connected call in the
         |                                      |            |                         | period) / no_calls (no
         |                                      |            |                         | collection-system activity)

61       | SF_2_last_uae_date                   | YYYY-MM-DD | 2026-11-12              | Latest evidence of being in the
         |                                      |            |                         | UAE: a UAE login or a card used
         |                                      |            |                         | in person there. Blank = none

62       | SF_2_last_uae_source                 | string     | login                   | login / debit_card /
         |                                      |            |                         | credit_card

63       | SF_2_last_foreign_date               | YYYY-MM-DD | 2026-03-04              | Latest evidence of being
         |                                      |            |                         | abroad. Blank = none

64       | SF_2_last_foreign_source             | string     | credit_card             | login / debit_card /
         |                                      |            |                         | credit_card / collector_note
         |                                      |            |                         | (departure noted by a
         |                                      |            |                         | collector)

65       | SF_2_last_travel_date                | YYYY-MM-DD | 2026-10-20              | Latest travel purchase
         |                                      |            |                         | (airline, travel agency,
         |                                      |            |                         | cruise). Blank = none

66       | SF_2_recent_travel_purchase_flag     | numeric    | 1                       | 1 = travel purchase in the
         |                                      |            |                         | period (early warning of a
         |                                      |            |                         | departure)

67       | SF_3_main_reason                     | string     | promises                | What set the state most:
         |                                      |            |                         | promises /
         |                                      |            |                         | payments_while_overdue /
         |                                      |            |                         | record_before_delinquency /
         |                                      |            |                         | refusal. Blank = no positive
         |                                      |            |                         | evidence

68       | SF_3_promise_level                   | string     | kept                    | kept / partly_kept / broken /
         |                                      |            |                         | thin (0-1 judged, none kept),
         |                                      |            |                         | from the promise counts below

69       | SF_3_promises_judged_count           | numeric    | 4                       | Promises and plans of the last
         |                                      |            |                         | 12 months whose deadline has
         |                                      |            |                         | passed; repeats before the
         |                                      |            |                         | deadline count once (deadline:
         |                                      |            |                         | cards 61-180 next statement,
         |                                      |            |                         | else month end)

70       | SF_3_promises_kept_count             | numeric    | 3                       | Of those, the monthly due (min
         |                                      |            |                         | AED 100) paid by the deadline

71       | SF_3_promises_partly_paid_count      | numeric    | 1                       | Of those, AED 100+ paid but
         |                                      |            |                         | less than the monthly due

72       | SF_3_promises_broken_count           | numeric    | 0                       | Of those, not paid
73       | SF_3_last_3_promises_not_kept_flag   | numeric    | 0                       | 1 = none of the last 3 judged
         |                                      |            |                         | promises was kept

74       | SF_3_full_due_paid_months            | numeric    | 1                       | Months in the period, since
         |                                      |            |                         | falling behind, with the full
         |                                      |            |                         | monthly due (min AED 100) paid

75       | SF_3_payment_while_overdue_level     | string     | some                    | regular (full due paid in 2
         |                                      |            |                         | months of the period, 3 at
         |                                      |            |                         | 180+) / some (AED 100+ paid in
         |                                      |            |                         | a month of the period; at 180+,
         |                                      |            |                         | of the last 12 months) / none

76       | SF_3_record_before_delinquency_level | string     | clean                   | clean (monthly due, for cards
         |                                      |            |                         | the minimum, paid in 80%+ of
         |                                      |            |                         | billed months in the 12 months
         |                                      |            |                         | before this delinquency) /
         |                                      |            |                         | not_clean / no_record (under 3
         |                                      |            |                         | bills, or start not visible)

77       | SF_3_refusal_flag                    | numeric    | 0                       | 1 = latest contact was a
         |                                      |            |                         | refusal, with no plan or AED
         |                                      |            |                         | 100+ payment since

78       | SF_4_main_reason                     | string     | income                  | What set the state most: income
         |                                      |            |                         | / money_in / spending /
         |                                      |            |                         | other_products / distress.
         |                                      |            |                         | Blank = nothing strong

79       | SF_4_income_level                    | string     | stable                  | stable (period salary ≥ 2 × the
         |                                      |            |                         | strong amount, 3 × at 180+, and
         |                                      |            |                         | not more than 25% below the
         |                                      |            |                         | period before) / weak (a month
         |                                      |            |                         | with AED 1,000+) / none

80       | SF_4_money_in_level                  | string     | strong                  | Non-salary money into or held
         |                                      |            |                         | in accounts with us: strong
         |                                      |            |                         | (the strong amount in 2 of 3
         |                                      |            |                         | months, 3 of 6 at 180+, as
         |                                      |            |                         | inflow or balance held) / some
         |                                      |            |                         | (a month with AED 1,000+) /
         |                                      |            |                         | none. Blank = no data

81       | SF_4_spending_level                  | string     | some                    | Money spent or moved out by
         |                                      |            |                         | choice, same scale as money in.
         |                                      |            |                         | Blank = no data

82       | SF_4_other_products_level            | string     | none                    | strong (deposits / investments
         |                                      |            |                         | ≥ the strong amount, or an
         |                                      |            |                         | up-to-date loan / card with
         |                                      |            |                         | instalment ≥ max(AED 1,000,
         |                                      |            |                         | amount due)) / some (any
         |                                      |            |                         | deposit / investment, or any
         |                                      |            |                         | up-to-date loan / card) / none

83       | SF_4_distress_flag                   | numeric    | 0                       | 1 = returned cheque, rejected
         |                                      |            |                         | direct debit or a bounced
         |                                      |            |                         | payment reported by the credit
         |                                      |            |                         | bureau in the period

84       | SF_4_income_source                   | string     | internal                | Where salary of AED 1,000+ was
         |                                      |            |                         | seen in the period: internal /
         |                                      |            |                         | bureau / both / none

85       | SF_4_salary_stopped_flag             | numeric    | 0                       | 1 = salary with us in the
         |                                      |            |                         | period before, none in the
         |                                      |            |                         | period

86       | SF_4_unknown_reason                  | string     | no_account_activity_12m | no_account_activity_12m /
         |                                      |            |                         | inactive_account (account with
         |                                      |            |                         | us, no transaction in the
         |                                      |            |                         | period). Blank unless Ability
         |                                      |            |                         | is Unknown
```

- It has **86 fields** (the knowledge base says 55): fields 1-55 as above, fields 56-86 the `SF_*` detail columns (a
  second header row sits at field 56).
- **No code builds this table** [code]: searched the UC1 branch for `SF_1`, `collection_action`, `last_transcript_date`,
  `transcript_count`: only a doc mention of `transcript_count` in `src/enbd_collections/sampling/utils.py:118,241` (a
  docstring: "use distinct `conversationid`"); and our repo (`src/`, `conf/`) has no `SF_*` column.
  `data/input/UC1/final_output_schema.md` is an empty file. A `signals draft`
  (`data/input/UC1/output_schema_uc2_signals_draft.md`) proposes rows from field 56 on.
- **Where `SF_1..4` come from (our datasets)** [doc `output_schema_uc2_signals_draft.md:7,43,82,158`]:
  `SF_1_Deterioration` = A4 (`crx_{cc,rl}_a4_deterioration`), `SF_2_Locatability` = A2 (`crx_{cc,rl}_a2_locatability`),
  `SF_3_Payment_credibility` = A3 (`crx_{cc,rl}_a3_payment_credibility`), `SF_4_Ability` = A1
  (`crx_{cc,rl}_a1_ability`). **The SF numbering is not the A numbering.**
- `persona` and `collection_action`: value sets "will be provided by Dec 11" [doc schema]; no dataset of ours holds
  them.
- Of the 55 base fields, the UC1 part is `last_transcript_date`, `transcript_count` and the detected / confidence pairs;
  the schema's confidence values are `high / medium / low`, whereas extraction carries `high / low` [doc KB §4.2]. None
  of the three timelines tables carries confidence, a count, or a last date (the last date is derivable from
  `simple_signal_aggregation.conversationid` + `metadata`).

---

## 8. Our side

- **Persona output (the table with the `SF_` columns)**: **NOT FOUND.** No node, pipeline or catalog entry.
  `docs/context/TASKS.md` §0: "No combined persona table, tiering or consumer exists yet"; planned as P1
  `crx_cc_persona` / `crx_rl_persona` (names proposed in TASKS, not in code). What exists is one dataset per axis, per
  `model_id` (namespace `${globals:model_id}`), grain `(account_id, observation_date)` (`GRAIN`, `_common.py:31`):

  ```text
  axis            | catalog dataset (cc / rl)         | registry name                    | state column
  ----------------+-----------------------------------+----------------------------------+----------------------------
  obs base        | `crx_cc_obs_base` /               | `crx_cc_obs_base`,               | -
                  | `crx_rl_obs_base`                 | `crx_rl_obs_base`                |
                  | (`catalog_crx.yml:159,166`)       |                                  |

  A1 ability      | `crx_cc_a1_ability` /             | `crx_cc_a1_ability`,             | `a1_state` ∈ high /
                  | `crx_rl_a1_ability` (`:220,431`)  | `crx_rl_a1_ability`              | moderate / low / unknown
                  |                                   | (`pipeline_registry.py:243,253`) | (ids), `a1_state_label`
                  |                                   |                                  | (display)

  A2 locatability | `crx_cc_a2_locatability` /        | `crx_cc_a2_locatability`,        | `a2_state`,
                  | `crx_rl_a2_locatability`          | `crx_rl_a2_locatability`         | `a2_state_label`,
                  | (`:151,474`)                      |                                  | `location_state`,
                  |                                   |                                  | `reachability_state`

  A3 credibility  | `crx_cc_a3_payment_credibility` / | `crx_cc_a3_payment_credibility`, | `a3_state` ∈
                  | `crx_rl_a3_payment_credibility`   | `crx_rl_a3_payment_credibility`  | `payment_credibility_high /
                  | (`:291,539`)                      |                                  | _moderate / _low /
                  |                                   |                                  | _unknown`

  A4              | `crx_cc_a4_deterioration` /       | `crx_cc_a4_deterioration`,       | NOT FOUND (column list not
  deterioration   | `crx_rl_a4_deterioration`         | `crx_rl_a4_deterioration`        | read)
                  | (`:108,353`)                      |                                  |

  axis             | other columns used here
  -----------------+----------------------------------------------------------------------------------------------------
  obs base         | `account_id` (string), `observation_date` (date), `cif_id` (spine type)
  A1 ability       | `a1_provenance`, `a1_unknown_reason`, `a1_reason`, `a1_income_level`, `a1_money_in_level`,
                   | `a1_money_out_level`, `a1_cross_product_level`, `a1_points_total`, `a1_distress_flag`,
                   | `liquidity_anchor_amt`, `a1_sweepable_balance_flag`, `a1_eosb_flag`, `a1_income_source`,
                   | `a1_salary_stopped`, `computed_at`. No `cif_id`.

  A2 locatability  | `deceased_flag`, `location_rule`, `last_contact_date`, ...
  A3 credibility   | `cif_id`, `episode_start`, commitments / DLQ / pre-DLQ levels and counts, `a3_points_total`,
                   | `a3_reason`, `a3_unknown_reason` (`a3_credibility/classify.py:10-60`)

  A4 deterioration |
  ```

All are per `model_id` (`cc_60_180`, `cc_180_plus`, `r1_60_180`, `r1_180_plus`); persona months 2026-01-31 ..
2026-08-31 (`globals_dev.yml:52-54`, `crx_persona`). A1 and A3 values quoted from code; measured value counts: section
6 [V] (`a1_state` values high / low / moderate / unknown; `a3_state` `payment_credibility_high / _moderate / _low /
_unknown`; both populated for all 19,292 rows).
- **`cif_id` type in `crx_cc_obs_base` / `crx_rl_obs_base`**: pass-through from the spine [code `_common.py:224-248`];
  the dtype is **string** for `crx_cc_obs_base` [V] (`cc_60_180`); `crx_rl_obs_base` NOT RUN; unpadded join works
  (section 5).
- **Pointing a catalog entry at the shared store**:
  - Globals key for the `shared` root: **`shared_id: "shared"`** (`conf/dev/globals_dev.yml:11`, same in
    `globals_local.yml`); `${_project.hdfs_path}` (`catalog_outputs.yml:17-18`) =
    `hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev`; `${globals:folders.feat}` = `05_feat`. So
    `${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/...` **is exactly** the shared
    `file_store` path.
  - Key for another project's root: NOT FOUND (UC1's own `.../risk_collections/risk_collections/dev/UC1/file_store` has
    no key; we do not read it).
  - Existing entries outside the model_id folders: `catalog_casa.yml:169,223`
    (`.../${globals:shared_id}/${globals:folders.feat}/casa/...`), `catalog_outputs.yml:329,333,691` (`shared_id` +
    `stg` / `prm` genesys). Sibling-repo (WM / feature space) entries: see
    `docs/context/reference/sibling_repo_partitions.md` (not read here).
  - Catalog file: new persona-programme assets belong in `conf/base/catalog/catalog_crx.yml` (its header: all `crx_`
    assets, one file to delete on abandon; R18).
  - **PROPOSED entry text** (names are proposals, R9; read-only, so no `save_args`):

    ```yaml
    crx_uc1_latest_flags:
      type: spark.SparkDataset
      file_format: parquet
      filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/\
        timelines/latest_flags"

    crx_uc1_simple_signal_aggregation:
      type: spark.SparkDataset
      file_format: parquet
      filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/\
        timelines/simple_signal_aggregation"

    crx_uc1_signal_level_conflicts:
      type: spark.SparkDataset
      file_format: parquet
      filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/\
        timelines/signal_level_conflicts"
    ```

  The same pattern would serve `metadata` and `index` (`.../file_store/metadata`) if the builder needs conversation
  dates.
- **Branch and head** (writing time): `feature/persona_refactor`, `git log -1 --oneline` = `3625b14d Add the UC1
  timelines PROD snippet ...` (before it `39f8d5a1 uc1 followup check`). Working tree also holds uncommitted edits to
  `docs/context/TASKS.md`, `docs/context/reference/uc1_data_kb.md`, `tmp_validation/uc1_profile/summary.md` and an
  untracked `docs/context/reference/uc1_ideation_prompt.md` (earlier UC1 work).
- **Bundle 25**: **NOT FOUND.** No reference to "bundle 25" in the repo (all files, all commit messages); the highest
  bundle mentioned is 24, whose temporary checks were removed in `96a6e316`. So it is not applied here, or it is not
  recorded in this repo.

---

## 9. Anything that would surprise the builder

Facts only, against `docs/context/reference/uc1_data_kb.md` and the task description.

1. **Only one of the three tables is customer-level.** `latest_flags` and `signal_level_conflicts` are per conversation
   (the latter ×22 slots).
2. **None of the three has a date, a confidence, a count or `request_type`.** The "Latest / Historic Consistency /
   Average value (count) / Estimated value / Confidence" columns of the UC1 plan (KB §6) are not in them; the dated,
   scored tables are the two `time_weighted_*` tables (section 2.4), whose run status is unknown.
3. **`simple_signal_aggregation` ignores legacy rows and remarks completely**, ignores confidence, and counts detections
   not conversations; a customer with only legacy conversations has a row with all signals `"NA"`.
4. **In the grid only the primary level is `detected`**; alternates live in the `conflicting_signals` text. A legacy
   conversation shows 22 `not-detected` slots.
5. **The UC1 "repo" is a branch of our own GitHub repo**, and it moved from `dc75eb7e` (KB) to `37c9cac0` (47 files,
   +12k lines); the KB's "tables absent in our shared copy" is a statement about 2026-11-16.
6. **The final schema has 86 fields, not 55, and its SF numbering is not the A numbering** (SF_1 = A4, SF_2 = A2, SF_3 =
   A3, SF_4 = A1); `cif_id` and `account_id` are typed `numeric` there, ours are strings / spine type. The file is
   git-ignored and local.
7. **Nothing builds the final table or a persona table on our side**; A1's output has no `cif_id` (join to the obs base
   on `account_id, observation_date`).
8. **Staleness**: the timelines were last evidenced at 5,140 conversations / 2,033 customers (2026-10-12) against a
   11,920-row ledger; `signal_level_conflicts` has never been recorded as run.
9. **`time_weighted_*` includes evidence dated on the `as_of_date` itself** (`<=`); our rule R2 requires strictly before
   the observation date.
10. [V] Against `uc1_data_kb.md`: the timelines now **exist** in the shared store (KB §2 says absent); all three were
    written together on 2026-11-16 13:28 UTC on the full 11,920-conversation ledger (5,751 customers, 1,437 legacy
    conversations, as in the KB). `cif_id` is an 8-digit string with **no leading zeros** in every table and the obs
    base joins exactly (KB: "leading-zero preservation unconfirmed"). Grid detections reproduce the KB's per-signal
    counts. Spine reach in the latest month is 5.5% of rows with any row, 3.6% with a capacity level, 4.0% with an
    intent level (timeless; the as-of-valid share equals it only for 2026-07/08).
11. [V] A customer's `simple_signal_aggregation` row exists for 5,751 customers but only 1,057 of 19,292 spine rows
    (`cc_60_180`, 2026-08) have one: 13,387 spine rows have no conversation at all and 4,848 have conversations that
    were not extracted.

---

## 10. Not found / not measured

- Bundle 25: NOT FOUND (searched all files and all commit messages of this repo).
- Persona output node / pipeline / catalog entry; the code that builds the 86-field table: NOT FOUND.
- A4's state column list: NOT FOUND (not read).
- A run record for `signal_level_conflicts`, `time_weighted_aggregation_scores`, `time_weighted_signal_aggregation`: NOT
  FOUND in the UC1 docs and notebooks (searched `docs/`, `notebooks/`, `src/`).
- Globals key for another project's root: NOT FOUND (`conf/dev/globals_dev.yml`, `conf/local/globals_local.yml`,
  `conf/base/**`).
- NOT RUN: B4-B6 for `cc_180_plus`, `r1_60_180`, `r1_180_plus` (spine reach and sizes depend on `model_id`); obs base
  `cif_id` length / leading-zero distribution (not in the snippet). Confidence and `request_type` per row: not carried
  by the tables. Not measurable from any of these tables: signal-vs-outcome relationship; reach of model_ids other than
  the ones run; whether UC1's full extraction changes any of it.
