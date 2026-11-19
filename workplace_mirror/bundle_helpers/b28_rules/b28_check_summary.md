# B28 check: summary (old vs new A1 / A3 states)

Source: `crx_<p>_b28_compare` runs of 2026-11-19, one `<model_id>.md` per model_id in this folder. The crosstabs are for
the latest persona month (2026-08-31).
The old tables predate bundle 25's rules, so every change below is bundles 25 and 28 together; this check cannot split
them.

**Not captured:** the step 7 `a1_ability` / `a3` state distributions and the step 7 A1 and A3 run times were not saved
(runs done, output lost). Nothing here covers them; rerun step 7 only if they are needed.

## Rows

Old, new and in-both row counts are identical in every month for all four model_ids: no rows added or lost.

## Rows whose state changed (2026-08-31, of rows in both)

| model_id | rows | a1_state changed | a3_state changed |
|---|---|---|---|
| cc_60_180 | 19,292 | 687 (3.6%) | 7,355 (38.1%) |
| cc_180_plus | 318,663 | 1,703 (0.5%) | 268,351 (84.2%) |
| rl_60_180 | 3,985 | 21 (0.5%) | 789 (19.8%) |
| rl_180_plus | 55,371 | 55 (0.1%) | 36,206 (65.4%) |

A1 changes are stable across months (cc_60_180 rises from about 330 to 687 in the last two months). A3 changes track the
table size.

## A3

- **`unknown` is gone.** Every old `payment_credibility_unknown` row is now `low` (a handful of cc rows `moderate`):
  cc_180_plus 259,291 (81.4%), rl_180_plus 35,142 (63.5%), cc_60_180 2,228 (11.5%), rl_60_180 263 (6.6%). This is the
  bulk of the A3 change in the 180+ models.
- **Upgrades from `low`:** cc_60_180 3,829 rows (19.8%: 3,399 to moderate, 430 to high); cc_180_plus 6,744 (2.1%);
  rl_180_plus 725 (1.3%); rl_60_180 340 (8.5%). `moderate` to `high`: cc_60_180 1,295 (6.7%), cc_180_plus 1,489 (0.5%),
  rl_60_180 173, rl_180_plus 333. Consistent with same-day payments now counting.
- **Downgrades are rare:** `moderate` to `low` 565 rows in cc_180_plus, 3 / 4 / 1 in the other three. `high` to
  `moderate`: 50 (cc_180_plus), 9 (cc_60_180, rl_60_180), 5 (rl_180_plus).
- **`a3_commitments_level`:** `broken` no longer appears in the new tables (old `broken` rows: cc_180_plus 3,428,
  cc_60_180 2,621, rl_180_plus 302, rl_60_180 142). They move to `promised` / `partly_kept` (a few to `kept`). Most old
  `thin` rows become `no_promise` (cc_180_plus 94.9%, rl_180_plus 95.8%, rl_60_180 65.1%, cc_60_180 57.6%); the rest
  become `promised` / `partly_kept`.

## A1

- **Small and mostly stable:** about 85% of rows in the two 180+ models stay `unknown` (cc_180_plus 85.1%, rl_180_plus
  85.4%); cc_60_180 57.2%, rl_60_180 40.8%.
- **cc_180_plus:** the largest change is `low` to `unknown` (1,492 rows, 0.5%), plus `high` to `low` / `moderate` 145
  and `moderate` to `low` 59.
- **cc_60_180:** `moderate` to `low` 361 (1.9%), `unknown` to `low` / `moderate` 142, `high` to `low` / `moderate` 58,
  `low` to `moderate` 73.
- **rl models:** 55 (rl_180_plus) and 21 (rl_60_180) rows change, mostly `high` to `moderate`, `moderate` to `low`,
  `moderate` to `unknown`.
- **`a1_cross_product_level` (F4, card parent link and point-in-time CIF):** cc_180_plus 1,610 rows change, 99.3% of the
  `some` changes going to `none` (1,599) and 7 to `strong`; cc_60_180 37 rows (19 to `none`, 18 to `strong`);
  rl_180_plus 4; rl_60_180 1.

## Things to look at

- cc_180_plus `low` to `unknown` (1,492 A1 rows) and `some` to `none` (1,599 cross-product rows) are the largest A1
  moves and likely the same accounts losing a card-parent link; worth confirming against the F4 rule.
- A3 `unknown` to `low` is a relabel of rows with no A3 evidence, so the share of `low` in the new tables is not
  comparable with the old one.
- Both cc runs logged a YARN warning (executor removed, "User balzsv not found"); both completed. Compare-node times:
  cc_180_plus 96.1 s, cc_60_180 20.5 s, rl_180_plus 26.3 s, rl_60_180 10.5 s (not step 7 times).
