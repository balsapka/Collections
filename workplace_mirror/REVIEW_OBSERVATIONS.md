# Review observations — crx_persona CC pipeline (workplace mirror)

Living list of what the mirror review has found. Line numbers refer to the files under
`workplace_mirror/src/enbd_collections/` as transcribed (they match the workplace screen).
Nothing here has been changed in code yet; each item becomes a sub-task once agreed.

**Status:** `confirmed` = follows from the code alone · `data check` = depends on how the
source data looks, needs a quick PROD query before fixing · `design` = works as written,
but the choice is questionable.

**Severity:** **H** = feature values are wrong · **M** = wrong in edge cases / silent drift ·
**L** = docs, naming, hygiene.

Last updated: 2026-10-24 (O45–O52: A2 review for bundle 05); 2026-10-23 (batches 1–3: cc_spell, cc_full_history, cc_raw_extract,
cc_payment_trajectory, cc_utilisation, cc_departure_signature, pipeline_registry,
cc_a4_deterioration + `_dpd_journey` engine, cc_a2_locatability, cc_a1_ability_v2,
`_spine_utils`, `stg_rr_portf`, `nodes/utils/config`; batch 5: the RL chain — rl_full_history,
rl_spell_table, rl_departure_signature, rl_a4_spine, rl_a4_deterioration, rl_a2_locatability,
rl_a1_ability; batch 6: cc_a1_ability v1 + enrichers, scoring_engine, catalog_crx and globals).

---

## Summary

| # | Sev | Status | Module | One-liner |
|---|---|---|---|---|
| O1 | H | data check | departure Pass K vs T04b/T05 | Two opposite sign conventions for `txn_amount_aed` on the same table |
| O2 | H | confirmed | departure Pass I | Month-end `pay_month` shifts H2 by one month; M0-1 payroll is dropped |
| O3 | M | confirmed | cc_spell | One NULL-bucket month splits a spell in two |
| O4 | M | confirmed | cc_spell | Unparseable bucket `""` cast to int (ANSI error); dedupe not deterministic |
| O5 | M | confirmed | cc_utilisation, cc_payment_trajectory | `F.first` after groupBy picks an arbitrary row (comment says "max") |
| O6 | M | design | cc_payment_trajectory | "Retention floor" is the first *transaction*, not the data start |
| O7 | M | confirmed | cc_utilisation | Months with zero spend are absent, not 0 — H1/H2 means and slope are biased up |
| O8 | M | design | departure Pass A, Pass J | Features read past onset up to `spine_obs_date` (contradicts module header) |
| O9 | M | confirmed | departure Pass F | `cif_id` not cast to string (all other passes do); joins against the unscoped bridge |
| O10 | L | confirmed | T04b, T05, T06 outputs | `account_id` cast to `string` while upstream tables use `long` |
| O11 | L | confirmed | cc_utilisation | `spend_cliff_flag` never NULL → logged coverage always 100% |
| O12 | L | confirmed | various | Docstring/comment drift (see list) |
| O13 | H | data check | cc_a2_locatability Node 1 | `cif_id` re-attached from `cc_spine` without `distinct` — rows multiply per spine row |
| O14 | H | data check | cc_a2_locatability Node 3 | Spine schema guard requires `account_id`; docstrings say the column is `contract_id` → all contact signals NULL |
| O15 | M | data check | cc_a2_locatability Node 4 | Way4 deceased join on exact `observation_date` — likely why cc_180_plus matched zero rows |
| O16 | M | data check | cc_a2_locatability Node 4 | Demographics deceased join has no point-in-time filter and may multiply rows |
| O17 | M | confirmed | cc_a2_locatability Node 3/4 | Recent-avoidance compares an *event* count to a *date* count |
| O18 | L | confirmed | cc_a2_locatability Node 3 | `contact_confirmed_n` / `rpc_rate` double-count outbound SUC events that are also on the RPC list |
| O19 | M | design | cc_a4_deterioration | "Restructure" flag cannot tell a restructure from an account already delinquent at the data start |
| O20 | M | confirmed | crx_persona (all) | Repeated `.count()` logging without `persist` recomputes each node's full lineage |
| O21 | H | confirmed | departure Pass A + D | `fee_accel_h2` divides finance charges by late + overlimit fees — two different fee types |
| O22 | M | confirmed | `_spine_utils.join_spine_to_spell` | Drops spine rows whose account has spells but none covering the date (docstring says all rows kept) |
| O23 | M | data check | stg_rr_portf | Dedup keys on `ra_org_app_id`, not `acct_num` — can drop a second loan sharing an application |
| O24 | M | confirmed | cc_a1_ability_v2 Node 3 | `oldest_overdue_amount` uses the latest balance snapshot however old it is |
| O25 | M | data check | cc_raw_extract + config | `TXN_CATEGORIES` codes are zero-padded strings; an unpadded `txn_code` leaves every category NULL |
| O26 | H | confirmed | rl_departure_signature Node 0 (= crx_rl_a4_spine) | Only the *still-open* spell is joined: spine rows of later-cured spells lose their spell (feature nullness leaks the cure) or vanish |
| O27 | H | confirmed | rl_departure_signature Node 1 | CASA / payroll partition floors are `persona_start − 12m`, windows reach `t0 − 24m` / `t0 − 12m` — truncated or empty for older T0s |
| O28 | H | confirmed | rl_departure_signature Pass I | Same month-end `pay_month` off-by-one as O2 (copied from CC) |
| O29 | M | confirmed | rl_departure_signature Node 3 | Login PIT filter after a left join drops rows whose CIF has only later logins — their FX flag becomes 0 |
| O30 | M | confirmed | rl_a1_ability Node 4r | `[obs − 3m, obs]` on month-end dates keeps 4 months incl. the obs month; docstring says "3 months before" |
| O31 | M | design | rl_a1_ability Node 4r | `monthly_emi_recent` falls back to `overdue_total`, several EMIs at 60+ DPD — inflates the threshold |
| O32 | M | confirmed | rl_a1_ability Node 5 | The NULL-EMI sentinel (1e18) makes `casa_low` (`<`) **True**, not False as documented |
| O33 | M | confirmed | rl_a1_ability Node 2r | `wm_pri_labelled_transactions` floored at `persona_start`, but the H2 window reaches 3 months earlier |
| O34 | M | data check | rl_full_history → rl_spell_table | No per-(account, month) dedupe; duplicate months make spell boundaries non-deterministic |
| O35 | L | confirmed | RL modules | Docstring/naming drift (see list) |
| O36 | M | confirmed | cc_a1_ability enrichers (salary PIT) | `salary_amt_last` is the latest WM salary row before the anchor, however old — a years-old salary still scores A1 v2 income as "weak" |
| O37 | M | confirmed | cc_a1_ability_v2 Node 3 (+ v1, RL) | `wm_pri_labelled_transactions` floored at `persona_start`, H2 window reaches 3 months earlier (O33 in CC) |
| O38 | M | data check | cc_a1_ability enrichers (fea alerts) | `month_number` parsed as `yyyyMMdd`; docstring says the column is `YYYY-MM-DD` → `fea_salary_acct_flag` all NULL |
| O39 | M | confirmed | cc_a1_ability enrichers (bureau salary) | Ties on the latest salary month pick an arbitrary row; bridge dedup keeps an arbitrary `cif_id`; an extra `.count()` job |
| O40 | L | data check | enrichers (CASA avg balance, ext loans) | PIT filter is `<= anchor` (others use `<`) — a weekly row dated on/after the obs week can leak up to 6 days |
| O41 | L | confirmed | catalog_crx.yml, model_configs.yml | Config comments drift from code (see list) |
| O42 | H | data check | cc_a1_ability enrichers (ext card payments) | `date_format(..., "yyyyww")` is not a valid Spark 3 pattern — the node fails unless PROD runs the legacy time parser |
| O43 | M | confirmed | cc_a1_ability_v2 Node 1 | Spine rows without a resolved CIF are dropped, so those accounts get no A1 state at all |
| O45 | H | confirmed | cc_a2_locatability Node 3 | `gone_contact_flag` / `not_reachable_flag` fire on *any* dead or ringing event in the last 2 attempt dates, not *all* |
| O46 | M | design | cc_a2_locatability Node 4 | A confirmed contact any time since T0 keeps an account Reachable while every later call hits a dead line |
| O47 | M | confirmed | cc_departure_signature Pass A | Travel window is 3 months before the card block (`t0 + days_to_dpd60`), not before T0 as documented |
| O48 | M | design | cc_departure_signature Pass B | Departure salary stop uses its own raw-regex salary (A1 uses WM salary only) and reads job loss as departure |
| O49 | H | data check | cc_a2_locatability Node 3/4 | `dcore_observation_spine` and `prm_contract` join on the exact `observation_date`; month-end dates may match nothing |
| O50 | M | confirmed | cc_a2_locatability Node 2 | Login PIT compares `month_number` with `trunc(obs, 'month')`; if `month_number` is a month end, the observation month is never included |
| O51 | M | confirmed | departure Pass J + A2 Node 2 | Foreign login has no age bound, so an old foreign login marks a departure trail for good; `recent_login_but_foreign` can never fire |
| O52 | L | confirmed | cc_a2_locatability Node 3/4 | `rpc_rate`, `uns_rate` computed and never used by the state; `spell_id` emitted |
| O53 | H | confirmed | stg_digital_login | A login with no country (both `countrylocation` and `countrycode` NULL) is flagged foreign |
| O54 | H | data check | stg_digital_login | `dropDuplicates(["sessionid"])` collapses every login without a sessionid into one row |
| O55 | M | confirmed | prm_digital_login_monthly | The month's last login is picked by date only; same-day UAE and foreign logins tie at random |
| O56 | M | design | prm_digital_login_monthly | Keeps only the month's last login; the latest UAE login date is lost when the last one was foreign |
| O57 | H | fixed (bundle 04) | a1_ability/signals.py | `prm_casa_return_events` coverage guard compares a date with a string |
| O58 | M | closed (bureau v01) | prm_bureau_alert_enriched | `DT_OF_RETURN` is renamed, then dropped by the model projection |
| O59 | H | data check | cc_raw_extract / prm_cc | `is_international` (Way4 `DOMESTIC=N`) is 1 on 96% of card transactions in PROD |
| O60 | L | confirmed | feature_retail_loans | `aecb_direct_debit_returns_6m` is declared but missing from the PROD table |
| O61 | M | data check | prm_demographics | `build_customer_individual` projects through `CustomerGroupingXref`, which may drop `deceased_flag` |
| O62 | L | confirmed | data_engineering models / bureau | `BureauSalaryHistory.reference_month` documented as YYYYMM; staging says MMYYYY |

---

## Details

### O1 — Contradictory sign convention on `crx_cc_transactions.txn_amount_aed` (H, data check)

`cc_raw_extract/nodes.py:118` passes `settl_amount` through unchanged as `txn_amount_aed`;
`direction` (line 117) is kept alongside. Consumers then disagree:

- `cc_payment_trajectory/nodes.py:366, 565` — payments = `direction == 1`, and `p_m` sums the raw
  `txn_amount_aed` (no `abs`).
- `cc_utilisation/nodes.py:46, 352, 359` — "txn_amount_aed is negative for outflows", spend =
  `direction == -1` then `abs()`.
- `cc_departure_signature/nodes.py:2199, 2211` (Pass K) — payment = `txn_amount_aed < 0`,
  purchase = `txn_amount_aed > 0`; docstring 2147–2148 says the opposite of T05.

Whatever the real sign is, at least one is wrong:
- If purchases are negative and payments positive (T05's statement): Pass K is **inverted** —
  payments count as purchases (`max_7d_spend_ratio`, `limit_util_first_7d_flag`) and purchases
  count as payments (`ever_paid_flag` almost always 1).
- If `settl_amount` is unsigned (sign lives only in `direction`): Pass K's `< 0` never fires, so
  `ever_paid_flag` rests on `txn_category` alone and every payment is a "purchase".
- If payments are negative: T04b's `p_m` is negative → `pay_ratio_m ≤ 0` for everyone.

**Check:** `select direction, sign(settl_amount), count(*) from raw_transaction … group by 1, 2`.
Batch 4 note: `TXN_CATEGORIES["payment"]` exists (`nodes/utils/config.py:98`), so Pass K's
`txn_category == "payment"` fallback does work — but only if O25 is not hitting.
**Likely fix:** make Pass K use `direction` like T04b/T05 (`direction == 1` payment,
`direction == -1` purchase, `abs()` for amounts), and state the convention once in `cc_raw_extract`.

### O2 — Pass I month index is off by one (H, confirmed)

`cc_departure_signature/nodes.py:1924` builds `pay_month` from `month_number` (last day of month),
and 1944–1952 computes `floor(months_between(trunc(t0, 'month'), pay_month))` **without**
truncating `pay_month`. For t0 in June:

| pay_month | months_between | m_from_m0 |
|---|---|---|
| May-31 (M0-1) | 0.03 | **0** → in neither H2 nor H1 |
| Apr-30 (M0-2) | 1.06 | 1 |
| Mar-31 (M0-3) | 2.03 | 2 |
| Feb-28 (M0-4) | 3.13 | 3 |

So H2 is really M0-4..M0-2, the month right before onset is ignored, and H1 starts a month late.
`payroll_present_h2` and `payroll_stopped_flag` both shift. A customer whose salary stopped
exactly in M0-1 is not flagged.
**Fix:** `F.trunc(F.col("pay_month"), "month")` inside `months_between` (as Passes A, D, E do).
Passes G, H, H2 use `month_number` only in range filters, which are correct.

### O3 — A single NULL-bucket month splits a spell (M, confirmed)

`cc_spell/nodes.py:106–115`: a spell starts when `bucket ≥ 2` and the previous bucket is `< 2`
**or NULL**. A month whose `add_info` has no `BS_PMT_CYCLE_DUE` gives a NULL bucket; that row is
neither in-spell nor a cure, and the next delinquent row sees `_prev_dlq IS NULL` → new spell.
Result: one delinquency episode becomes two spells, the second with a later `t0`, a
`prior_spell_end` of NULL (no cure was found between them), and `prior_spell_cnt_24m` inflated.
**Fix:** drop NULL-bucket rows before the lag, or lag over non-null rows only; treat NULL as
"unknown", never as a boundary.

### O4 — cc_spell has the two parsing issues already fixed in cc_full_history (M, confirmed)

- `cc_spell/nodes.py:96–98`: `regexp_extract(...).cast("int")` on `""` — error under ANSI mode
  (Spark 4 default), NULL otherwise. `cc_full_history/nodes.py:48` already uses
  `F.when(raw != "", raw.cast("int"))`.
- `cc_spell/nodes.py:100`: `.distinct()` on `(account_id, observation_date, bucket)` keeps **two**
  rows when the same date has two buckets; the lag/cumsum then depends on row order.
  `cc_full_history` dedupes to the worst bucket per date.
**Fix:** reuse the cc_full_history logic, or build the spell table from `crx_cc_full_history`.

### O5 — `F.first` after groupBy is non-deterministic (M, confirmed)

- `cc_utilisation/nodes.py:226–228`: comment "take max util if duplicates", code `F.first`.
- `cc_payment_trajectory/nodes.py:637–639`: `F.first("d_m")` for duplicate billing rows in a month.
Two runs can give different `util_*` / `pay_ratio_*` values. **Fix:** `F.max` (or latest by
`observation_date` via a window) and make the comment match.

### O6 — Retention floor derived from activity, not data availability (M, design)

`cc_payment_trajectory/nodes.py:228–237`: `retention_floor_month` = month of the account's
**earliest transaction** in `crx_cc_transactions`. That table is already cut to
`[min(T0) − 12m, max(T0)]` (`cc_raw_extract` 66–78), so the floor is never the true data start.
It is the first month the customer happened to transact. A quiet customer gets
`w_pre_start` pushed forward, `w_pre_truncation_reason = 'retention'`, a smaller
`w_pre_clean_m`, and (via O7-style denominators) inflated `pay_dom_window_share`.
**Fix:** use a global data-start date (a parameter or the min date of the source table), not a
per-account activity date.

### O7 — Zero-spend months are missing, not zero (M, confirmed)

`cc_utilisation/nodes.py:442–452` aggregates only months that have ≥1 outflow. Then:
- `_spend_h1_avg` / `_spend_h2_avg` (457–458) average over active months only → biased up, and
  `spend_taper_ratio` compares two inflated means.
- `txn_cnt_slope` (accumulators 469–475) fits only active months; going silent before T0 (the signal) is invisible.
- `_spend_m1` uses `otherwise(0)` (460) so M0-1 *is* treated as 0 — inconsistent with H1.
**Fix:** build a month grid from `w_pre_start` to M0-1 per spell, left-join, coalesce to 0.

### O8 — Two departure features look past onset (M, design)

Module header (`cc_departure_signature/nodes.py:21`): "all joins enforce strict obs_date < M0".
But:
- Pass A, `last_txn_foreign_flag`: window ends at `_obs_ceil = coalesce(spine_obs_date, block_date)`
  (706–710).
- Pass J, `foreign_login_flag` / `last_login_country_h2`: ends at `spine_obs_date` (2095–2101).
The docstrings say this is deliberate ("T06 anchor-change"). Acceptable for scoring, but the header
should say so, and it is a leakage risk if the target is measured inside `[T0, spine_obs_date)`.
Also `last_login_country_h2` has no H2 window at all — the name is misleading.

### O9 — Pass F CIF join differs from every other CIF pass (M, confirmed)

`cc_departure_signature/nodes.py:380–386`: joins `feat_product_holding` to the **whole**
`contract_cif` bridge (not scoped to the spell population) and does **not** cast `cif_id` to
string. Passes B, E, G, H, H2, I, J all scope first and cast (`IntegerType` in retail.feature_space
vs string in `prm_client`). The implicit cast may silently drop matches or force a full shuffle.
**Fix:** same scoped, string-cast bridge as Pass G.

### O10 — `account_id` type drift (L, confirmed)

Spell table and raw extracts: `long`. Outputs: `cc_payment_trajectory/nodes.py:170`,
`cc_utilisation/nodes.py:127`, `cc_departure_signature/nodes.py:581` cast to `string`. Downstream
joins (e.g. departure spell base 196 joins spell `long` to trajectory `string`) rely on implicit
casts. **Fix:** keep `long` end to end.

### O11 — `spend_cliff_flag` coverage always 100% (L, confirmed)

`cc_utilisation/nodes.py:496–506` falls back to `0` when H1 is missing, so "no data" and "no cliff"
look the same, and the logged coverage (557) is meaningless. **Fix:** NULL when `_spend_h1_avg`
is NULL.

### O12 — Docstring / comment drift (L, confirmed)

- `cc_payment_trajectory/nodes.py:217`: "min obs_date per account" — code uses `open_date` (244).
- `cc_spell/nodes.py`: steps go 0 → 2 (no Step 1).
- `cc_departure_signature/nodes.py:2147–2148`: sign convention contradicts T05 (see O1).
- `cc_departure_signature/nodes.py:898` (Pass B): filters `tran_dc == 'C'` and `is_salary`
  (878) checks it again — harmless duplication.
- `cc_a2_locatability/nodes.py:136–138`: "CC's crx_cc_a2_base does not [carry cif_id]" — it does
  (Node 1 adds it at 311–317), so the `_build_cif_bridge` branch at 1229–1237 is dead code for CC.
- `stg_rr_portf.py:157`: comment "Restrict DPL tables from 2025-11" — the code uses
  `ECL_CUTOFF_DATE` = 2025-12-01.
- `computed_at` type differs per axis: `date` (A1 v2, `cc_a1_ability_v2/nodes.py:926`), `string`
  (A2), `timestamp` (T04b/T05/T06/A4).
- `cc_a1_ability_v2/nodes.py:933`: `_log_a1v2_stats` has no `try/except` (every other stats logger
  does) — a logging failure fails the node.
- `cc_a4_deterioration/nodes.py:20`: "Mirrors cc_spell/nodes.py's _RESTRUCTURE_DLQ_THRESHOLD" —
  `cc_spell` has no such constant; its censoring rule uses `>= 2` (`_CC_DELINQ_MIN`), A4 uses `>= 4`.

### O13 — A2 Node 1 multiplies rows when re-attaching `cif_id` (H, data check)

`cc_a2_locatability/nodes.py:311–317` selects `(contract_id, cif_id)` from `cc_spine` **without
`.distinct()`** and left-joins it on `account_id` alone. `cc_spine` has one row per
(contract, observation_date) — A4's `build_deterioration` says so explicitly ("classifies EVERY
spine row"), and departure Node 1 aggregates it with `max(observation_date)` for the same reason.
So an account with *k* spine rows comes out of `build_a2_base` with *k × k* rows, and every
later join on `(account_id, observation_date)` keeps the duplicates; counts and the state
distribution are inflated.
**Check:** the `build_a2_base: %d rows` log line vs `cc_spine.count()`.
**Fix:** `.select(...).distinct()` (or `dropDuplicates(["_cid"])`), as departure Node 2 does.

### O14 — A2 contact-signal spine guard looks for the wrong column name (H, data check)

`cc_a2_locatability/nodes.py:583` requires `{"account_id", "observation_date", "agreement_id",
"cif_id"}` on `dcore_observation_spine`, but the pipeline header (pipeline.py:21) and the node
docstring (485–487) both say the column is `contract_id`. If the table really carries
`contract_id`, the guard fires on every run and the node silently returns all-NULL contact
signals → every reachability state is `Unknown` (only a WARNING log line).
**Check:** `dcore_observation_spine` columns, or the `DCORE coverage` log (0% would confirm).
**Fix:** match the real name, or alias `contract_id → account_id` before the guard.

### O15 — Way4 deceased corroboration joins on an exact date (M, data check)

`cc_a2_locatability/nodes.py:1205–1213` joins `prm_contract` block codes on
`(account_id, observation_date)` — an exact-date match between Way4 contract snapshots and the
spine's per-account billing dates. If the two tables date their rows differently (month-end
snapshot vs billing day), almost nothing matches. That is a simpler explanation for the
"cc_180_plus prm_contract matched zero rows" anomaly the docstring (130–131) records.
**Fix:** match on month (`trunc(…, 'month')`) or take the latest snapshot `<= observation_date`.

### O16 — Demographics deceased join has no point-in-time filter (M, data check)

`cc_a2_locatability/nodes.py:1239–1242` joins `feat_demographics_cif` on `cif_id` only. If that
table has more than one row per CIF (monthly snapshots), rows multiply; and a deceased flag set
*after* `observation_date` is applied to earlier rows (look-ahead).
**Check:** grain of `feat_demographics_cif`. **Fix:** latest row with date `<= observation_date`.

### O17 — Recent-avoidance rule mixes event and date counts (M, confirmed)

Step 5c (`cc_a2_locatability/nodes.py:790–814`) ranks attempt *dates* (`dense_rank`) but sums
*events* per date. Node 4 (1114–1118) then requires `recent3_ringing_n == 3`. So:
- three ringing dates where one date had two ringing calls → `ringing_n = 4` → flag **not** set;
- three dates with one ringing event each plus a LINE BUSY (neither ringing nor confirmed) → flag
  set although not every attempt was ringing.
**Fix:** count distinct ringing dates, and require every ranked date to be ringing-only.

### O18 — Confirmed-contact count double-counts (L, confirmed)

`contact_confirmed_n = _rpc_n + _rpc_proxy_n` (888–890) and `rpc_rate` (822–827): an outbound
`SUC` event whose `result_name` is also on the RPC allowlist is counted in both. The flag that uses
it (`> 0`) is unaffected; `rpc_rate` can exceed 1 (numerator counts events, denominator counts
distinct dates). **Fix:** one `F.when(suc_outbound | rpc_name, 1)` per event.

### O19 — A4 restructure flag also catches data-start censoring (M, design)

`cc_a4_deterioration/nodes.py:41–58` flags `restructure_blind_spot_flag = 1` when the account's
earliest billing row is already `>= 4`. An account that was simply already delinquent when the
billing table starts looks identical. In `assign_state` both feed `history_blind`, so states are
unaffected, but the output column over-states restructures.
**Fix:** require the earliest row to be later than the table's global start month (the same
`_global_min` Stage 1 already computes), or rename the flag.

### O20 — Logging counts recompute whole lineages (M, confirmed)

Every A2 node logs with one to three `.count()` calls (326–328, 437–438, 574, 970–971, plus
`_log_a2_stats` at 1299) on un-persisted DataFrames, and T04b/T05/T06 do the same. Each count
re-runs the node's joins — on the CASA/DCORE-sized inputs this is several extra full scans per
run. **Fix:** compute stats from the saved output, gate them behind a `log_stats` param as
`_dpd_journey` does, or `persist()` before counting.

### O21 — `fee_accel_h2` compares two different kinds of fee (H, confirmed)

`fee_accel_h2 = (H2 fees / H2 months) / fee_rate_life` (departure `nodes.py:1209–1220`), but:
- **numerator** `_fee_amt_h2` (Pass A, 746–748, 774–776) sums transactions with
  `txn_category == "fee"`, and `TXN_CATEGORIES["fee"]` is `["500", "485"]` — *finance charges /
  billed interest* (`nodes/utils/config.py:127–129`), plus a narration fallback;
- **denominator** `fee_rate_life` (Pass D, 1195–1196) is lifetime **late + overlimit** fees from
  `prm_turnovers`, divided by tenure.

So the ratio is interest-this-quarter over penalty-fees-per-month. Accounts carrying a balance get
very large values regardless of any change in behaviour; the docstring's "fees accelerated in the
3 months before T0" reading does not hold. The `_FEE_CATEGORY = "fee"  # <<FILL-IN: verify>>`
(125) is exactly where this slipped through.
**Fix:** numerator from `late_fee` + `overlimit_fee` codes (`254, 255, 504, 519, 256, 257, 503`), or
denominator from the same finance-charge codes — same fee definition on both sides.

### O22 — `join_spine_to_spell` silently drops spine rows (M, confirmed)

`_spine_utils.py:19–21` promises "Left join preserves all spine rows; spell columns are NULL…".
The code (41–53) left-joins on account only, then filters `t0 IS NULL OR t0 <= obs` and
`spell_end IS NULL OR obs <= spell_end`. An account that **has** spells, but none covering this
`observation_date`, produces only joined rows that fail the filter — so the spine row disappears
instead of coming through with NULL spell columns. Typical trigger: CC billing dates (spell `t0`)
vs spine observation dates on different days of the same month, or a spine date after a cure.
Used by A1 (v1), A2 Node 1, A3 — those axes lose rows without a log line.
**Fix:** move both date conditions into the join (`on=[eq, t0 <= obs, (spell_end null | obs <=
spell_end)]`, still a left join) — the efficiency note in the docstring is about a cross-join plan,
which an equi-join plus extra conditions does not trigger.

### O23 — `stg_rr_portf` dedup key is the application, not the account (M, data check)

Module grain is `acct_num × ss_dt` (`stg_rr_portf.py:4`), but the dedup window (204–211)
partitions by `(ra_org_app_id, edp_load_date)` and keeps one row. If one application can carry
more than one `acct_num` (top-up / takeover — `ra_ln_nat_nm` has NEW/TOPUP/TAKEOVER), the second
account is dropped from every RL table built on this staging layer.
**Check:** `count(distinct acct_num) > 1 group by ra_org_app_id, edp_load_date`.
**Fix:** partition by `(acct_num, edp_load_date)` (or both keys).

### O24 — A1 v2 overdue anchor has no staleness bound (M, confirmed)

`_enrich_oldest_overdue_amount` (`cc_a1_ability_v2/nodes.py:304–327`) takes the latest
`prm_balance` row with `_bal_obs_date <= observation_date`, with **no lower bound**. If the
account's balance snapshots stopped (closed/blocked card), a snapshot from months or years earlier
sets `oldest_overdue_amount`, which then sets both liquidity floors (`_casa_floor`, `_pay_floor`).
Every other A1 v2 source is windowed (90 or 180 days).
**Fix:** require `_bal_obs_date >= observation_date - 31 days` (or the same month); NULL otherwise
→ falls back to the flat floor, as the docstring already allows.

### O25 — Transaction category codes may never match (M, data check)

`cc_raw_extract/nodes.py:97–102` maps `txn_code` to a category with
`F.col("txn_code").isin(codes)`, where `codes` are zero-padded strings such as `"036"`,
`"500"` (`nodes/utils/config.py:76–137`). If `raw_transaction.txn_code` is a string without
padding (`"36"`) or a double (`36.0` → `"36.0"` when compared as string), nothing matches and
`txn_category` is NULL for all rows: Pass A fees fall back to the narration regex only, Pass K
payments fall back to the sign test only (see O1).
**Check:** `select txn_code, count(*) from raw_transaction group by 1 order by 2 desc limit 20`.

### O26 — RL spine keeps only the still-open spell (H, confirmed)

`build_rl_depart_spine` (`rl_departure_signature/nodes.py:120–133`) keeps spells with
`spell_end IS NULL` only, left-joins them on `account_id`, then filters
`t0 IS NULL OR t0 <= observation_date`. `spell_end` is computed from the **full** history up to
today (`rl_spell_table/nodes.py:133–147`), not as of the observation date. So for a spine row in a
spell that cured later:
- the account has no open spell now → the row comes through with NULL `spell_id`/`t0`, so every
  spell-anchored signal (Node 1 CASA/payroll, Node 2 travel, Node 3 FX, A1 `eosb_like_flag`) is
  NULL or coalesced to 0;
- the account re-defaulted later → the open spell's `t0` is after the row's date → the row is
  **dropped**.
Either way, whether a row has spell features depends on what happened after the observation date,
which is the cure/roll outcome the model predicts — a leak, not just missing data.
`crx_rl_a4_spine` is the same function (`rl_a4_spine/pipeline.py:19`), so A1 and A2 inherit it,
while `rl_a4_deterioration` uses the full `rl_spine` — the axes end up with different row sets.
**Fix:** pick the spell that covers the date — join on `account_id` with
`t0 <= obs AND (spell_end IS NULL OR obs < spell_end)` inside the left join (as O22 proposes for
CC), and drop the `spell_end IS NULL` pre-filter. Keep `t0_censored_flag == 0` if wanted.

### O27 — Departure CASA / payroll floors are tied to the persona window, not to T0 (H, confirmed)

`build_rl_depart_casa_signals` (`rl_departure_signature/nodes.py:219–234`) filters
`comp_financial_tran_repos_dly` to `edp_load_date >= persona_start − 12m` and payroll to
`month_number >= persona_start − 12m`. The windows are anchored on `t0`: Pass B reads
`[t0 − 24m, t0)` (median from months 7–24), Pass I reads `[t0 − 12m, t0)`. `t0` is the start of
the delinquency spell, which is before the observation date and, for rl_180_plus, at least 6
months before it. For any `t0` before `persona_start`, months are missing:
- `t0` = `persona_start`: salary median uses months 7–12 only;
- `t0` < `persona_start − 12m`: Pass B sees no data → `casa_inflow_stop_gap_d` and
  `eosb_like_flag` NULL; Pass I sees no H1 → `payroll_stopped_flag` NULL.
The comment says the floor is "for efficiency — same as former build_rl_a4_casa_signals", so the
bug is older than this module.
**Fix:** floor at `min(t0) − 24m` (CASA) and `min(t0) − 12m` (payroll), computed from
`spell_base` (one small aggregate), or drop the floor and rely on the CIF leftsemi.

### O28 — RL Pass I repeats the CC month-end off-by-one (H, confirmed)

`_build_rl_pass_i` (`rl_departure_signature/nodes.py:449, 466–474`) is a port of CC Pass I and
carries O2 unchanged: `pay_month` is the month-end date, and `months_between(trunc(t0), pay_month)`
is not truncated, so M0-1 gets index 0 and falls out of H2. `payroll_present_h2` and
`payroll_stopped_flag` (A2 departure trail, A1 inputs) are shifted by a month.
**Fix:** same as O2 — `F.trunc(F.col("pay_month"), "month")` inside `months_between`.

### O29 — Node 3 login PIT filter drops rows (M, confirmed)

`build_rl_depart_foreign_signals` (`rl_departure_signature/nodes.py:802–810`) left-joins every
login month of the CIF, then filters `login_month IS NULL OR login_month <= trunc(obs)`. A CIF
whose logins all fall after the observation date has joined rows that all fail the filter, so the
row disappears from Node 3's output, together with its already-computed `last_txn_foreign_flag`.
Node 4 left-joins and coalesces to 0, so those rows report `last_txn_foreign_flag = 0` even
when FX leakage was positive.
**Fix:** put the date condition into the join condition (left join keeps the row with NULL
login), as for O22.

### O30 — Group C EMI window is 4 months and includes the obs month (M, confirmed)

`build_rl_a1_group_c_recent` (`rl_a1_ability/nodes.py:650–653`) keeps
`_loan_obs_date >= add_months(observation_date, −3)` and `<= observation_date`. Both are
month-ends, and `add_months` keeps the last day of the month (Mar-31 → Dec-31), so the window holds
Dec, Jan, Feb, Mar: four rows, including the observation month. The docstring (580–582) says
"the 3 months immediately before each observation_date". `emi_coverage_mean_recent` is a 4-month
mean.
**Fix:** `>` instead of `>=` for 3 months including obs, or `< observation_date` plus
`>= add_months(obs, −3)` for the 3 months before it — then decide which one the docstring means.

### O31 — `monthly_emi_recent` falls back to the overdue total (M, design)

`rl_a1_ability/nodes.py:674` uses `coalesce(installment_due_amount, overdue_total)`. At 60+ DPD
the overdue total is two or more instalments plus charges, so wherever `installment_due_amount` is
NULL the EMI threshold is a multiple of the real EMI. High Arms 1/4/6/6b (`>= _emi`) then fire less
often, and `casa_low` (`< _emi`) more often — a systematic push towards `ability_low` for exactly
the rows with missing instalment data.
**Fix:** leave EMI NULL (and handle it explicitly, see O32), or derive it from contract terms; at
least log how many rows use the fallback.

### O32 — NULL-EMI sentinel makes `casa_low` True (M, confirmed)

`_build_rl_ability_conditions` (`rl_a1_ability/nodes.py:1018`) sets
`_emi = coalesce(monthly_emi_recent, 1e18)`, and the docstring (1003–1005) says this makes "the
comparison False, not NULL". That holds for `>= _emi` (High Arms). But `casa_low` (1046–1048) is
`casa_avg < _emi`, which is **True** for every non-NULL balance when EMI is missing. So with no EMI,
`low_cond1` reduces to "salary stopped and no new salary account" and the row goes to
`ability_low` without any balance check.
**Fix:** `casa_low = casa NULL | (emi NOT NULL & casa < emi)` — or decide that "no EMI" is
`ability_unknown` and gate on it first.

### O33 — External CC payments truncated in the first months of the persona window (M, confirmed)

`build_rl_a1_group_b_income_recent` (`rl_a1_ability/nodes.py:345–348`) filters
`wm_pri_labelled_transactions` to `tran_date >= persona_start`, but `enrich_ext_cc_payments_h2`
reads `[obs − 3m, obs)`. For observation dates in the first three months of the window, part of the
H2 window is cut, so `ext_cc_payment_amt_h2_recent` is understated and High Arm 6 fires less. The
payroll floor right below it correctly uses `persona_start − 12m`.
**Fix:** floor at `persona_start − 3 months` (or −4 for safety with month-ends).

### O34 — RL history has no per-month dedupe (M, data check)

`build_rl_full_history` passes `int_loan_master` through without deduplicating
`(account_id, observation_date)`; `build_rl_spell_table` orders by `month_end_date` with `lag` and
`row_number` (`rl_spell_table/nodes.py:88–121`). If a month has two rows (snapshot reloads,
restructures), the order between them is arbitrary: a spell can start or end on the "wrong" twin,
and the censored check (`_rn == 1`) can flip between runs. The `_dpd_journey` engine dedupes its
own input, so A4 is unaffected.
**Check:** `count(*) > 1 group by account_id, observation_date` on `int_loan_master`.
**Fix:** dedupe in `build_rl_full_history` (worst bucket wins, like the amended CC node).

### O35 — RL docstring / naming drift (L, confirmed)

- `rl_full_history/nodes.py:55` selects `cif_id`, but neither the Args list nor the Returns
  schema (32–47) mention it.
- `rl_a1_ability/nodes.py:875` renames `prior_spell_cnt_12m` to `prior_spell_cnt_24m` — the window
  is 12 months; the column is also never used or output.
- `rl_a1_ability/nodes.py` computes `eosb_post_salary_flag` and `eosb_post_salary_flag_recent`
  with identical expressions (911–933).
- `high_arm2` (1058–1060): `salary_stopped_flag_recent == 0` is implied by
  `salary_months_h2_recent >= _TAU_SALARY_H2_MIN` — redundant clause.
- `ext_loan_payment_cnt_h2` is cast to `double` (307), its CC sibling `ext_cc_payment_cnt_h2` to
  `int`.
- `computed_at` is a `date` here (1253) and a `timestamp` in rl_full_history / rl_spell_table.
- `rl_a2_locatability/nodes.py:69` says `casa_inflow_stop_gap_d` is "forwarded from
  crx_rl_a4_class" (it comes from `crx_rl_departure_signature`); line 72 says all 4 departure
  columns are non-null on a join hit, but `casa_inflow_stop_gap_d` is not coalesced.
- `rl_a1_ability/pipeline.py:7` says Node 4b Group D was removed, the node module says it is kept
  but not wired.

### O36 — Stale WM salary counts as income evidence (M, confirmed)

`enrich_salary_pit` (`cc_a1_ability/enrichers.py:388–437`) takes the latest
`wm_fea_salary_days_since_increment` row with `week_date < anchor`, with no lower bound, and
returns `ft_last_salary_amount` as `salary_amt_last`. A customer whose salary stopped years ago
still carries their old salary. In A1 v2, `_income_level_col` (`cc_a1_ability_v2/nodes.py:766–785`)
treats `coalesce(salary_amt_last, bureau_salary_amt_last) >= _DEMIN` as **weak income** on its own,
so a stale salary is worth 1 income point. `bureau_salary_amt_last` is windowed to 6 months, the
WM one is not. Same pattern as O24.
**Fix:** require the PIT row within e.g. 90 days of the anchor (or use the source's own
`ft_days_since_salary_transaction` ≤ 90), NULL otherwise. Matters for the shared A1 engine
(CC + RL).

### O37 — External CC payments truncated in the first months (M, confirmed)

`build_a1v2_liquidity_signals` (`cc_a1_ability_v2/nodes.py:472–474`) and v1's
`build_a1_group_b_income` (`cc_a1_ability/nodes.py:374–376`) filter `wm_pri_labelled_transactions`
to `tran_date >= persona_start`, while `enrich_ext_cc_payments_h2` reads `[obs − 90d, obs)`. For
observation dates in the first three months of the persona window, part of the window is cut, so
`ext_cc_payment_amt_h2` is understated and the liquidity level drops. Same as O33 (RL).
**Fix:** floor at `persona_start − 3 months` in the shared engine.

### O38 — AECB feature-space alerts may never parse (M, data check)

`enrich_fea_bureau_alerts` (`cc_a1_ability/enrichers.py:1105–1176`) documents `month_number` as
"last day of month, YYYY-MM-DD" (1117) but parses it with `to_date(cast(string), "yyyyMMdd")`
(1152–1154). If the column really is `2026-05-31`, the parse returns NULL (or raises under ANSI),
every row fails the PIT filter, and `fea_salary_acct_flag` is NULL — so `a1_new_salary_acct_flag`
rests on `prm_bureau_alert_enriched` alone. The other `month_number` sources (payroll) are
`yyyyMMdd` ints, which is probably where the format was copied from.
**Check:** `select month_number from fea_monthly_aecb_alerts limit 5`.
**Fix:** parse with the format the column actually has (or `to_date` without a format if it is
already a date string).

### O39 — Bureau salary: non-deterministic picks and an extra job (M, confirmed)

`enrich_bureau_salary` (`cc_a1_ability/enrichers.py:910–1016`):
- the CIF bridge is deduplicated with `dropDuplicates(["bureau_file_id"])` (971–974), which keeps
  an arbitrary `cif_id` if a file id maps to more than one;
- the PIT window orders by `_sal_date` only (1003); salary history is reloaded per
  `edp_load_date` and parsed to the 1st of the month, so several rows tie on the latest month and
  `bureau_salary_amt_last` is whichever Spark returns first;
- `sal_with_cif.count()` (988) runs an extra full job over the bridged history on every call
  (called twice per run: T0 and obs-date variants).
**Fix:** order by `(_sal_date desc, _sal_amt desc)` or dedupe per (cif, month) first; replace the
count with a cheap `limit(1)` emptiness check or drop it.

### O40 — Inclusive PIT filter on weekly WM features (L, data check)

`enrich_casa_eod_avg_balance` (`enrichers.py:298–300`) and `enrich_ext_loan_payments_h2`
(`enrichers.py:713–715`) keep rows with `_snap_date <= anchor`; every other PIT enricher uses
`<`. If `week_number` is the week's start date, the row for the week containing the observation
date aggregates days after it — up to 6 days of look-ahead in the CASA balance gate (RL High
Arms 1/4).
**Check:** is `week_number` the first or the last day of the week?
**Fix:** `<` (or `<= anchor − 6 days` if it is the start date).

### O41 — Config comment drift (L, confirmed)

- `catalog_crx.yml` RL-B2 block says the spell table is "one row per account_id … spell_id=1 /
  spell_end=NULL adapter"; `rl_spell_table` builds several spells per account with real
  `spell_end` (this mismatch is the root of O26).
- `catalog_crx.yml` RL A1 block still declares `crx_rl_a1_group_a` and `crx_rl_a1_group_d`
  (nodes removed / not wired) and says Node 4r reads `feature_retail_loans` (it reads
  `int_loan_master`).
- `catalog_crx.yml` RL departure block numbers the travel / foreign nodes 1 / 2 (code: 2 / 3) and
  has no entries for `crx_rl_depart_spine` / `crx_rl_depart_casa_signals` (they run as memory
  datasets — fine, but undocumented).
- `model_configs.yml` `cc_180_plus` / `rl_180_plus`: comment "3-month look-ahead" next to
  `target_horizon_months: 12`.

### O42 — Week pattern `yyyyww` fails on Spark 3 (H, data check)

`enrich_ext_cc_payments_h2` (`cc_a1_ability/enrichers.py:645`) counts payment weeks with
`F.date_format(_tran_date, "yyyyww")`. Spark ≥ 3.0 rejects week-based patterns
(`INCONSISTENT_BEHAVIOR_CROSS_VERSION.DATETIME_PATTERN_RECOGNITION`) unless
`spark.sql.legacy.timeParserPolicy=LEGACY`. Reproduced on local Spark 3.5. Either PROD runs
with the legacy policy, or every A1 run (v1 and v2) fails at this node.
**Check:** `spark.conf.get("spark.sql.legacy.timeParserPolicy")` in a PROD notebook.
**Fix (bundle 01):** `F.date_trunc("week", tran_date)`.

### O43 — A1 v2 drops accounts without a CIF (M, confirmed)

`build_a1v2_cif_base` (`cc_a1_ability_v2/nodes.py:177–180`) keeps only spine rows whose
contract resolves to a CIF, and every later node starts from that table, so an account with
no client link has no row in `crx_cc_a1_ability_v2` (5% of rows in the synthetic check).
**Fix (bundle 01):** the observation base keeps every spine row; customer-level signals are
NULL and the state is `ability_unknown`.

### O44 — CC axes rebuild the CIF bridge the spine already carries (L, confirmed)

`cc_spine` has `cif_id` (`cc_full_history/nodes.py:56–59` reads it directly), yet CC A1 v1
(`cc_a1_ability/nodes.py:288`), CC A2 (`cc_a2_locatability/nodes.py:1234`) and the first
obs base joined `prm_contract` → `prm_client` (`_build_cif_bridge`) to get it again: two
extra table reads and a second CIF source that can disagree with the spine.
**Fix:** bundle 01 — `crx_cc_obs_base` takes `cif_id` from `cc_spine`; A2 moves onto the obs
base in bundle 5; v1 is removed in bundle 4.

---

## Not issues (checked, fine)

- Passes G, H, H2 window filters on month-end dates: `>= add_months(M0, -3)` and `< M0` keep exactly
  M0-3..M0-1.
- Pass E bureau slope (always NULL in PROD) is documented as a T21 drop; code is consistent.
- `cc_raw_extract` per-account T0 windows: same logic in all three builders.
- `_dpd_journey` engine: Stage 1 gap-fill, cycle-shift and dedupe rules, and Stage 2 point-in-time
  truncation are consistent with their docstrings; a smoke test of `classify` on a clean
  straight-roll sequence returns `early_payment_default` as the tree says it should.
- A2 Node 2 login window (`< trunc(obs, 'month')`) has no look-ahead.
- `stg_rr_portf` `_SELECT_COLS` has exactly 58 columns, as `build()`'s docstring says.
- A1 v2 CASA recent/prior windows (latest month-end row in `[obs-90d, obs)` vs `[obs-180d,
  obs-90d)`) do not overlap, since each row is already a trailing 3-month average.
- Departure Pass K's `_PAYMENT_CATEGORY = "payment"` matches the `TXN_CATEGORIES` key.
- RL wrappers match their callees: `build_a2_login_presence(obs_month_end=True)`,
  `build_a2_contact_signals(base, observation_spine, followup)`, the `build_a2_locatability`
  kwargs in `rl_a2_locatability/pipeline.py`, and `_dpd_journey`'s `build_dpd_sequences` /
  `build_deterioration` / `journey_params`.
- `rl_spell_table` `w_pre_clean_m` and `prior_spell_cnt_12m` window logic is consistent with the
  docstrings (NULL buckets count as clean, which is acceptable for RL).
- A1 Node 3r `_recent` renaming: every column the classifier reads (`aecb_*_recent`,
  `a1_new_salary_acct_flag_recent`, …) exists after the rename loop in `_assemble_rl_classify_inputs`.

- `enrich_salary_months_h2` / `_h4_h6`: `month_number` is a month-end date and the windows are
  `[trunc(anchor) − 3m, trunc(anchor))` / `[− 6m, − 3m)` on it — exactly 3 months each, no
  off-by-one (unlike O2, which uses `months_between`).
- `scoring_engine.StateLadder.state`: unknown first, then High, one-rung demotion to Moderate,
  Low floor — matches its docstring and A1 v2's use.
- Every enricher name imported by `cc_a1_ability_v2` and `rl_a1_ability` exists in
  `cc_a1_ability/enrichers.py` (`enrich_casa_self_transfer_wash_h2` is only mentioned in a
  docstring).

### O45 — Dead-line / gone flags test *any* event, not *all* (H, confirmed)

`cc_a2_locatability/nodes.py:855–874`: both flags need `_last_n_confirmed == 0` and
`_last_n_dead > 0` (or `_last_n_ringing > 0`) summed over every event of the last 2 attempt
dates. One ringing call plus one LINE BUSY or NO ANSWER (neither list) sets
`gone_contact_flag`; the docstring says "all N dead or ringing". **Fix (bundle 05):** classify
each attempt date as failed only if every outbound event that day is ringing or dead and none
is confirmed (spec Q5).

### O46 — An old confirmed contact outranks later dead lines (M, design)

`nodes.py:1184–1194`: `contact_confirmed_flag` counts any confirmed event since T0. The only
override above it is `recent_avoidance_flag`, which needs 3 *ringing* results; a number that
went dead after a confirmed contact stays Reachable. Spec Q5 proposes one "gone dark" rule
(ringing or dead) above a confirmed contact in the window.

### O47 — Travel window anchored on the card block, not T0 (M, confirmed)

`cc_departure_signature/nodes.py:722–743`: `travel_mcc_flag_h2` uses `m_from_block` 1–3,
block = `t0 + days_to_dpd60`. The old A2 spec said "3 months before T0". Moot once the window
is decided without T0 (spec Q2).

### O48 — Departure salary stop: second salary definition, ambiguous meaning (M, design)

`cc_departure_signature/nodes.py:877–917` detects salary with a narration regex on
`comp_financial_tran_repos_dly` (A1 decided WM-recovered salary is the only internal salary
source) and `casa_inflow_stop_gap_d > 180` before the T0 month marks a departure trail. A
salary stop is job loss as often as departure and is already A1 evidence (spec Q3).

### O49 — Exact-date joins break on month-end dates (H, data check)

`nodes.py:594–605` joins `dcore_observation_spine` on `(account_id, observation_date)`;
`nodes.py:1205–1213` does the same with `prm_contract`. If either table keeps the old billing
dates, every contact signal is NULL (reachability all Unknown) or no Way4 code matches.
Conversely, if `prm_contract` is a month-end snapshot, the move to month ends fixes O15.
**Check:** the date column and grain of both tables (Sonnet facts, spec Q9).

### O50 — Login month comparison depends on how `month_number` is dated (M, data check)

`nodes.py:405–410` keeps login months `<= trunc(observation_date, 'month')` (RL) or `<` (CC).
If `month_number` is the month end (`20261031`), RL never includes its observation month and
CC skips two months. **Fix:** compare `last_login_date <= observation_date` instead.

### O51 — Foreign login has no age bound (M, confirmed)

Pass J (`cc_departure_signature/nodes.py:2000+`) takes the latest login before the
observation date however old. The same login drives `in_country_flag`, so a foreign latest
login always yields a trail → Skip, and `location_unknown_reason = recent_login_but_foreign`
(`nodes.py:1153–1157`) can never fire (spec Q4).

### O52 — Unused contact outputs (L, confirmed)

`rpc_rate` / `uns_rate` (`nodes.py:821–834`) are not read by Node 4; `spell_id` is emitted by
Node 4. Dropped in bundle 05.

### O53 — Logins without a country count as foreign (H, confirmed)

`stg_digital_login.py:107–119`: `is_foreign_login = 0` only when `countrylocation` is
"United Arab Emirates" or `countrycode` is `AE`; every other row, including both NULL, gets 1.
The history table may lack `countrycode` (docstring, lines 42–43), so a history login with no
`countrylocation` is foreign. Under A2's "latest evidence wins" a missing country would mark
the customer Skip at any age. **Fix (location data layer):** NULL when neither column is
present; a login with unknown country is not location evidence.

### O54 — Session dedup collapses NULL sessionids (H, data check)

`stg_digital_login.py:101–102` runs `dropDuplicates(["sessionid"])` whenever the column
exists. `_normalise_source` (line 181) creates it as NULL for a source without `sessionid`, and
Spark treats NULLs as equal in `dropDuplicates`: all such logins collapse into one row. If
`loginlog` (history) has no `sessionid`, the whole login history is reduced to a single row.
**Check:** `sessionid` presence and NULL share per source (A2 v01, t4). **Fix:** dedup on
`sessionid` only where it is not NULL.

### O55 — Same-day tie in the monthly last login (M, confirmed)

`prm_digital_login_monthly.py:46–49` orders by `login_date`, a date (`createdon` is
truncated to a date in staging, line 163). Several logins on the month's last login day tie
and `row_number` picks one at random, so `last_login_foreign_flag` can flip between runs. A2's
rule (D-A2-14): on the same day, foreign evidence wins — the fix takes a foreign login first
on the last login day; no timestamp needed.

### O56 — The monthly table cannot give the latest UAE login (M, design)

`prm_digital_login_monthly` keeps the month's last login plus `any_foreign_login_flag`. When
the last login is foreign, the date of the latest UAE login that month is gone, and logins
cannot be ordered against card / CASA spending within a month. **Fix (bundle 05):** add the
month's latest UAE and latest foreign login (date and timestamp) to the primary table; A2
reads the primary table only (user, 2026-10-25: no staging outputs downstream). O50 is confirmed by `month_number` = the month's last day (line 42):
`<= trunc(obs, 'month')` never includes the observation month.

### O57 — Bundle 03 coverage guard compares a date with a string (H, fixed in bundle 04)

`a1_ability/signals.py:351` (`build_internal_returns`): `prm_casa_return_events` is written
partitioned by `event_month` (`yyyy-MM-dd` string, `prm_casa.py:65-67`); on read Spark infers
the folder values as `DateType`, while `lookback_floor` returns an ISO string. PROD
(2026-10-26, `crx_cc_a1_ability_b03_check`): `TypeError: '>' not supported between instances
of 'datetime.date' and 'str'`. Fix: `str(first) > since`. The `event_month >= since` column
filter was unaffected (Spark casts the literal).

### O58 — `prm_bureau_alert_enriched` drops the bureau return date (M, confirmed by Sonnet)

`prm_bureau.py:95-146` (`build_alert_enriched`) renames `DT_OF_RETURN` → `return_date` and
`CONTRACT_STATUS_DT` → `contract_status_date` (`_ALERT_RENAMES`, lines 105-106), but the
`BureauAlertEnriched` model (`data_engineering/primary/models/bureau.py:844`) has no such
fields, so the final projection silently drops both. A1 therefore can only date bureau
bounces by `extract_date`. Whether `DT_OF_RETURN` is worth exposing depends on bureau v01
(1,399 distinct values over ~801K bounced rows looks like a batch stamp, too). Separately,
`prm_bureau_payment_order` carries its own `return_date` and is already an optional A1 input
(`signals.py:311-320`), not yet in PROD.

### O59 — `is_international` flags 96% of card transactions (H, data check)

`cc_raw_extract/nodes.py:104–112` sets `is_international = 1` when `add_info` matches
`DOMESTIC=N` (the comment says it replicates `prm_cc.build_transaction`). PROD (A2 v01 t5,
cc_60_180, 2026-10-26): 96.35% of `crx_cc_transactions` rows are international, against 28.3%
with a travel MCC on the same table. Either the polarity is inverted, the regex also matches
another key ending in `DOMESTIC=`, or the flag means something else (e.g. the acquiring
network). It feeds `cc_departure_signature` (`foreign_txn_share_h2`, `last_txn_foreign_flag`,
`nodes.py:657–769`) and so the old A2's `departure_trail_flag` (`cc_a2_locatability/nodes.py:1083–1085`):
most CC accounts with card use likely carry a departure trail today. **Check:** A2 v02 Part A /
t7a (raw `DOMESTIC=` values by currency, MCC, cash advance). **Fix:** the new A2 reads the
card-abroad field v02 confirms; the old A2 retires with bundle 05.
**Update (handoff 9, 2026-10-27):** `prm_cc.build_transaction` (`prm_cc.py:375–386`) has the
same parse, so `prm_transaction` inherits it; its comment mentions `trans_country_code`, which
the code does not read.

**O58 closed (bureau v01, 2026-10-26):** `DT_OF_RETURN` moves with `EXTRACT_DT` on 99.65% of
repeated bounces (median 2 days before it), so it is "the latest registration as of this pull",
not the bounce date. Exposing it would not fix stale bounces; A1 dates bureau bounces by the
first report of each bounce instead (DESIGN_REVIEW, A1 finish plan).

### O60 — `aecb_direct_debit_returns_6m` missing in PROD (L, confirmed)

Declared in `feat_loan_application_risk.py` (bureau v01 inventory A.4) but NOT FOUND on the real
`feature_retail_loans` table for `rl_60_180` (bureau v01 w8). The RL waterfall had already
dropped it (RL-A1-14) and the new A1 does not read it; the declaration is dead.

### O61 — Deceased flag may be dropped by the wrong model (M, data check)

`prm_demographics.py:146–150`: `build_customer_individual` renames `cust_deceased_flg` to
`deceased_flag` (`_CUSTOMER_INDIVIDUAL_RENAMES`, `:83–94`) and then returns
`build_primary_dataframe(stg_customer_individual, CustomerGroupingXref, …)`. That model's name
says group cross-reference, not customer individual. If it does not declare `deceased_flag` /
`date_of_birth`, the projection drops them silently. A2's deceased rule reads
`feat_demographics_cif` (from `int_customer_demographics`), so the effect depends on which of
these feeds that table. **Check:** the A2 refactor reads the model's field list (one snippet), or
the RL t6 re-run shows `ft_deceased_flag` populated.

### O62 — Bureau salary month format documented two ways (L, confirmed)

`stg_aecb_salary_history.py:28–41` documents `subj_salcr_hist_ref_mnth` as MMYYYY (`"072023"`);
the `BureauSalaryHistory` model documents `reference_month` as YYYYMM. The A1 engine parses
MMyyyy, which matches staging. The bureau pipeline is unvalidated, so A1 v03b's v0 funnel
confirms this on the data. `prm_bureau_salary_history` (CC finish bundle) parses MMyyyy.
