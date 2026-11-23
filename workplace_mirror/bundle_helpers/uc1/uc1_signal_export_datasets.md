# UC1 signal export: dataset description (UC1 team, received 2026-11-23)

Populated in the shared store, `hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev/shared/05_feat/file_store/current/outputs/timelines/`:
`signal_level_conflicts`, `signal_level_posteriors`, `simple_signal_aggregation`, `time_weighted_signal_aggregation`,
`proposer_level_observations`, `customer_signal_export`. The last two are the official datasets; `customer_signal_export`
is the primary one. The text below is the UC1 team's description, as received.

## Dataset: Signal Decisioning

Table: `fs_current_customer_signal_export` (HDFS `current/outputs/timelines/customer_signal_export`), written by the `customer_signal_export` pipeline, overwritten in full on each run.
Signal levels: see the signal-detection guide.

## Grain

- One row per `cif_id` × `signal`, as of `snapshot_date`.
- Each customer with any observation has 10 rows: 7 categorical signals and 3 `repayment_specifics` slots. Rows appear even without evidence.
- Customers with no observations do not appear.

## Columns

*Definition* says what the value is. *How to read it* says how to use it and what it does not show.

| Column | Definition | Values | How to read it |
|---|---|---|---|
| `snapshot_date` | Date the run was built for. | A date, e.g. `2026-08-31`. | Compare tables only at the same date. |
| `cif_id` | Customer identifier. | String. | Join key. |
| `signal` | The signal the row describes. | 7 categorical names, plus `repayment_specifics:amount_mentioned`, `repayment_specifics:date_specific` and `repayment_specifics:plan_structure_mentioned`. | Repayment rows record what was mentioned about repayment, not a customer state. |
| `supporting_data` | Direction of bank corroboration for `estimated_value`: `Agree` or `Disagree`, from UC2 features, with recent evidence weighted higher (half-life 60 days). The `Agent` suffix means the only matching verdict came from a level named in an agent remark. | `Agree`, `Disagree`, `Agree Agent`, `Disagree Agent`, `N/A`. | `Agree` means account data supports the estimate, not that the customer confirmed it. Corroboration exists only for `delinquency_reason` = `lost_employment` and `payment_capacity` = `none` or `full`; other levels are always `N/A`. |
| `agent_remark_value` | Categorical: the level(s) named in the most recent agent remark up to the snapshot, joined by `\|`. Repayment: the latest value an agent remark recorded for the slot. | A schema level, an amount, a date, `detected`, or `not-detected`. | Records what the agent wrote, not what the customer said. |
| `latest_value` | Categorical: the level the most recent call transcript up to the snapshot detected. Repayment: the amount or date mentioned, or `detected` for plan structure. | A schema level; an amount with thousands separators (`2,400`); a date (`YYYY-MM-DD`); `detected`; or `not-detected`. | Amounts and dates are as transcribed and are not checked against the account. |
| `historic_consistency` | Whether `estimated_value` matches the most recent observation before the month of the snapshot. `N/A` when there are fewer than two earlier observations. | `Agree`, `Disagree`, `N/A`. | The estimate already uses that earlier evidence, so one earlier agreement is weak evidence of stability. |
| `average_value` | The most frequent level across all observations up to the snapshot. Ties go to the most recent. | A schema level or `not-detected`. | The long-run typical level, ignoring recency. Only the top level is shown. |
| `average_count` | Number of observations that named `average_value`. | Integer ≥ 0. | Small counts make `average_value` fragile. |
| `estimated_value` | The most likely current level, from transcript, remark and bank evidence, with older evidence weighted lower (half-life 60 days). Tied levels are sorted and joined by `\|`. | A schema level, tied levels joined by `\|`, or `not-detected`. | The headline answer for the signal. Read it with `confidence`. |
| `confidence` | `HIGH`: top score ≥ 0.60 and at least 0.15 ahead of the runner-up. `MEDIUM`: not HIGH, with top score ≥ 0.50 or margin ≥ 0.10. `LOW`: otherwise. | `HIGH`, `MEDIUM`, `LOW`, `N/A` (no estimate). | Measures how clearly one level wins, not how likely it is to be right. For `request` and `fraudulent_customer`, which have one level, it is the only thing that varies. |

## Placeholders

- `not-detected`: the signal was looked for and no level was found.
- `N/A`: the field does not apply to the row. On repayment rows this covers `supporting_data`, `historic_consistency`, `average_value`, `estimated_value` and `confidence`.
- null: `average_count` on repayment rows only.

## Caveats

- **Repayment text.** In the current run, some repayment `latest_value` and `agent_remark_value` entries are not amounts or dates, for example percentages, ranges, words or redaction tokens such as `[CARD_EXPIRY_DATE]`. Treat both columns as free text on repayment rows until the extraction is fixed, and filter them before use.
- **Bank data is the only account check.** Nothing except `supporting_data` is checked against account records.
- **Sparse coverage.** `not-detected` does not mean the customer denies the signal.

## Dataset: Source observation history

Table: `fs_current_proposer_level_observations`, one partition per `snapshot_date` (`current/outputs/timelines/proposer_level_observations/snapshot_date=YYYY-MM-DD/`), written by the `proposer_level_observations` pipeline.
Companion file: `fs_current_proposer_level_observations_parameters` (`parameters.json`) records the run settings: snapshot date, half-life, source bits, copy-share mode, confidence thresholds and UC2 verdict direction.

This is the evidence table behind the Phase 3.3 estimate. It covers the 7 categorical signals; `repayment_specifics` is not included.

## Grain

- One row per `snapshot_date` × `cif_id` × `observation_id` × `signal` × `source` × `level`.
- An observation is one customer on one calendar day.
- Only observations dated on or before `snapshot_date` are included.

## Columns

*Definition* says what the value is. *How to read it* says how to use it and what it does not show.

| Column | Definition | Values | How to read it |
|---|---|---|---|
| `snapshot_date` | Date the partition is valid for. | A date. | Filter to one partition before aggregating (see caveats). |
| `cif_id` | Customer identifier. | String. | Join key. |
| `observation_id` | The customer-day: `cif_id\|YYYY-MM-DD`. | String. | Customers with several calls on one day have a single observation. |
| `observed_at` | Midnight of the observation date. | Timestamp. | Use it for ordering. It does not record the call time. |
| `signal` | The categorical signal the level belongs to. | One of the 7 signal names. | Levels per signal are in the signal-detection guide. |
| `source` | Whether a call transcript or an agent remark named the level. | `transcript`, `remark`. | Transcript evidence weighs 3 times remark evidence in the estimate (default bits 3.0 and 1.0). |
| `level` | A level this source named for this signal on this observation. | A schema level. | One observation can name several levels; `statement` lists them all. |
| `statement` | Every level this source named for this signal on this observation, sorted. | Array of strings. | Use this for comparisons. `statement_signature` is the display form. |
| `statement_signature` | `statement` joined by `\|`. | String. | Display only. |
| `age_days` | Days from `observed_at` to `snapshot_date`. | Integer. | Measured from the snapshot, not from the month being estimated. |
| `half_life_days` | Half-life of the age weight. | `60.0`. | The same for every row; see `parameters.json`. |
| `age_weight` | `0.5 ^ (age_days / half_life_days)`. | Number from 0 to 1. | How much the observation counts, with 1 meaning the snapshot day itself. |
| `named_level_count` | Distinct levels this source named for this signal on this observation. | Integer ≥ 1. | Values above 1 mean each level carries less weight (see `proposer_level_share`). |
| `proposer_level_share` | `1 / named_level_count`. Summed over one source's levels in one observation, it gives 1. | Number in (0, 1]. | This level's share of the source's one unit of weight. |
| `is_pick` | Transcript rows only: `true` for the first level in `statement` in alphabetical order. | Boolean; null for remark rows. | Not a recency signal. See caveats for how this differs from the spec. |
| `remark_day_key` | Remark rows only: the remark's key, `cif_id\|YYYY-MM-DD`. | String; null for transcript rows. | Remark rows are kept once per key, so repeats are dropped. |

## Placeholders

- No `not-detected` or `N/A` rows exist. A missing row means the source named nothing for that level.
- `is_pick` and `remark_day_key` are null where they do not apply.

## Caveats

- **Partitions overlap.** Each partition holds the full history up to its own `snapshot_date`. Never add rows across partitions.
- **`is_pick` differs from the spec.** The tech spec (§2.1) describes it as the transcript's first named level. The code uses alphabetical order, as defined above. This is open; the choice between code and spec is pending.
