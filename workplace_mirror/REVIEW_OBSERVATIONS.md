# Review observations — crx_persona CC pipeline (workplace mirror)

Living list of what the mirror review has found. Line numbers refer to the files under
`workplace_mirror/src/enbd_collections/` as transcribed (they match the workplace screen).
Nothing here has been changed in code yet; each item becomes a sub-task once agreed.

**Status:** `confirmed` = follows from the code alone · `data check` = depends on how the
source data looks, needs a quick PROD query before fixing · `design` = works as written,
but the choice is questionable.

**Severity:** **H** = feature values are wrong · **M** = wrong in edge cases / silent drift ·
**L** = docs, naming, hygiene.

Last updated: 2026-10-23 (batches 1–3: cc_spell, cc_full_history, cc_raw_extract,
cc_payment_trajectory, cc_utilisation, cc_departure_signature, pipeline_registry,
cc_a4_deterioration + `_dpd_journey` engine, cc_a2_locatability, cc_a1_ability_v2,
`_spine_utils`, `stg_rr_portf`, `nodes/utils/config`).

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
