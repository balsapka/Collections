# Review observations — crx_persona CC pipeline (workplace mirror)

Living list of what the mirror review has found. Line numbers refer to the files under
`workplace_mirror/src/enbd_collections/` as transcribed (they match the workplace screen).
Nothing here has been changed in code yet; each item becomes a sub-task once agreed.

**Status:** `confirmed` = follows from the code alone · `data check` = depends on how the
source data looks, needs a quick PROD query before fixing · `design` = works as written,
but the choice is questionable.

**Severity:** **H** = feature values are wrong · **M** = wrong in edge cases / silent drift ·
**L** = docs, naming, hygiene.

Last updated: 2026-10-23 (batches 1–2: cc_spell, cc_full_history, cc_raw_extract,
cc_payment_trajectory, cc_utilisation, cc_departure_signature, pipeline_registry).

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

---

## Not issues (checked, fine)

- Passes G, H, H2 window filters on month-end dates: `>= add_months(M0, -3)` and `< M0` keep exactly
  M0-3..M0-1.
- Pass E bureau slope (always NULL in PROD) is documented as a T21 drop; code is consistent.
- `cc_raw_extract` per-account T0 windows: same logic in all three builders.
