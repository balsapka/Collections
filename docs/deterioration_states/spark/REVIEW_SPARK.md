# PySpark deterioration pipeline — review and rewrite (CC + RL)

Reviewed from 15 screenshots (Oct 2026) of `src/enbd_collections/pipelines/crx_persona/`:
`cc_full_history/nodes.py`, `rl_full_history/nodes.py`, `cc_a4_deterioration/{nodes,pipeline}.py`,
`rl_a4_deterioration/pipeline.py`, `_dpd_journey.py` (`resolve_gaps`, `encode_transitions`).
**Not seen:** `classify_from_grid`, `BucketScheme`, `_log_*` bodies, the start of
`build_cc_full_history`. Findings about those are marked *(inferred)*.

**Verdict:** the code is careful and well documented, but it has three correctness problems
that change states — dropped accounts (F7), no cropped flag behind the CC floor (F8), and
glitch/repair results that differ from the signed-off reference (F9). Fixing them inside the
window-function design is hard, so the logic is **rewritten**: Spark scopes the data and
makes **one shuffle**, then a plain-Python port of the reference runs per account. Parity
with the reference is tested (0 mismatches), and so is the Spark pipeline end to end.

---

## 1. Findings

| # | Where | Severity | Finding | Fix (in this folder) |
|---|---|---|---|---|
| F7 | `resolve_gaps` | **High** | An account with any gap whose two neighbours differ is **dropped**. Real CC run: 17,675 of 192,587 (9.2%) gone — the output no longer covers the spine. Causes, roughly in order of likely size: (a) **billing-cycle shift**: a cycle date near month-end puts two bills in one month and none in the next; the month dedupe throws one bill away and leaves a hole; (b) **CC 0 vs 1** compared natively — both mean clean, yet `0 _ 1` counts as a disagreement; (c) **straight-roll gaps** `3 _ 5` (only one path is possible); (d) short ambiguous gaps `3 _ 4`. | Cycle-shift repair, canonical comparison, straight-roll fill, inference for gaps ≤ 2 months (all counted per account), and **truncate instead of drop**: keep the months after an unresolvable gap, flag `history_cropped`, still classify. No account with rows is dropped. |
| F8 | `build_cc_dpd_sequences` (+ `classify_from_grid`, *inferred*) | **High** | The 2024-01 floor removes older months, but Node 1's output has **no "cropped" flag**. In the reference, a cropped history can never be EPD, and a cropped straight roller is seasoned. Without the flag, a card opened in 2019 whose spell started in Mar 2024 has `months_before_spell = 2` → labelled **EPD**; a 2019 card that rolled in Jun 2024 → **early-life**. (Synthetic: 74% of spine histories are cropped by a 32-month window.) | `history_cropped` uses dates, which is better than the reference's length heuristic: the first raw bill is before the floor, or the history was truncated at a gap, or the first month is the very first month of the source. |
| F9 | `encode_transitions` | **High** | Glitch fix and +2 repair use `lag`/`lead` on the unfixed column. The reference loops and **cascades**: a fixed month feeds the next comparison. The docstring calls this a "known, flagged divergence". It changes states for chains of artefacts, and nobody has measured by how much. | Exact loop port. `tests/test_parity.py`: 20,000 spine accounts × options A/B/C, the same accounts in RL numbering, 8,000 accounts at 180+, and 56 business cases — **0 mismatches** on every feature and state. |
| F3 | `resolve_gaps` dedupe | Medium | The month dedupe keeps the latest `obs_date` **even when its bucket is NULL** (an unparseable `add_info`). A valid bill earlier that month is lost, the month becomes a gap, and the account may be dropped. | NULL / out-of-range buckets are removed before the dedupe and counted (`n_invalid_rows`). |
| F2 | `build_cc_full_history` | Medium | `dropDuplicates(["account_id","billing_date"])` keeps an **arbitrary** row: two runs can give different buckets, and a NULL row can win. | `groupBy(...).agg(max(dlq_bucket))`: deterministic, the worst non-NULL bucket wins. |
| F1 | `build_cc_full_history` | Medium | `regexp_extract(...).cast("int")`: no match gives `""`. That casts to NULL with ANSI off, but **fails the job** with ANSI on (the default from Spark 4 / some CDP profiles). | `when(x != "", x.cast("int"))`. |
| F4 | `build_rl_full_history` | Medium | `rl_spine.account_id.cast("string")`: if the spine key is a double, the cast gives `"1.23456789E8"` and the leftsemi join **silently matches nothing**. This is the trap the CC node's own comment warns about. | A double or decimal key is cast to long first, then trimmed to string. Tested: 100/100 matched. |
| F5 | `build_rl_full_history` | Low–Med | "No broadcast — rl_spine is model-sized" — that is exactly when to broadcast. ~31k keys is under 1 MB. Without the hint, Spark cannot estimate the size of a `distinct()` and may **shuffle all of `int_loan_master`**. | `F.broadcast(spine_keys)`. |
| F6 | `_log_stats`, `_log_sequence_stats`, `_log_state_stats` | Low–Med | Logging inside a node runs extra jobs. Without `persist()`, Kedro then recomputes the whole node to save the output — each node can run 2–4 times. | Opt-in (`dpd_journey.log_stats`): one `agg` job each, after `persist()`. |
| F10 | `build_cc_a4_deterioration` | Low–Med | An account is in the spine if its **latest grid row** is 4–7, even when that row is months old (frozen or closed accounts). Accounts excluded for this reason are not counted. | `history_stale_months` column (snapshot month − last observed month); Node 1 keeps every account with a `build_status`. |
| F11 | constants | Low | `_CC_HISTORY_FLOOR_DATE` and `_DET_OPTION` are code constants. The floor is temporary, so lifting it should be a config change, not a code change. | Moved to params (`conf/parameters_crx_persona_dpd_journey.yml`). |
| F12 | structure | Low | CC and RL are two near-copies of the same logic, with thresholds hand-ported ("CC ≥3, RL ≥2"). | One engine. RL is mapped onto the CC scale with **+1** (RL 0 → 1 = clean, RL 7 → 8 = 180+), so every threshold is written once. |

### Rule changes agreed after the review (Oct 2026) — in the engine AND the reference

| Rule | Why | Effect (synthetic) |
|---|---|---|
| **Stabilized never at the ceiling bucket** (CC 9, RL 7; canonical cap 9 / 8) | At the cap the bucket cannot rise, so `9 9 9` looks like a hold although nothing was paid — every long-default account would be "stabilized". CC 8 (181–210) can still be stabilized in the 180+ tree. | 180+ stabilized 0% at the cap; 60–180 unchanged (never at the cap) |
| **Unknown** replaces `history_starts_delinquent` and `history_not_available` | If the oldest OBSERVED month is clean (0 DPD), the whole current journey is seen and the fall-in states are confident. If it is already delinquent (spell older than the window / CC floor, restructured, migrated, missing), they would be guesses. Observed-evidence states still win: stabilized (60–180 and CC 8), paying_in_default and broken_payer (180+). | 60–180: 3.3% unknown with the 32-month window; 180+: 17–32% unknown depending on time at 9 |

New output column `starts_delinquent` (oldest observed month at canonical 2+).

### Efficiency

Old Node 1 + Node 2 (from the screenshots): a groupBy for bounds, sequence/explode, a join
back, two windows, a filter, an anti-join, a groupBy, a join, several lag/lead windows, more
windows and groupBys in `classify_from_grid` *(inferred)*, a `row_number` window, a leftsemi
join and a restructure join. That is many shuffle stages over an (account × month) grid —
and each `_log_*` reruns all of it.

New: **Node 1 = one shuffle** (`groupBy(account_id)` that collects the month rows) plus a
1-row broadcast aggregate and the restructure join. **Node 2 = no shuffle** (filter + map).
Python work per account is about 30–60 list steps. At about 200k accounts that is seconds
of executor CPU. Local run (4 cores, 5k CC accounts + 2.5k RL, raw rows to states, ANSI on):
about 30 s, mostly Spark start-up.

---

## 2. Design

```
raw_stg_billing ──► build_cc_full_history ──► crx_cc_full_history ─┐
cc_spine ─────────┘   (F1, F2; NO floor here)                       ├► build_cc_dpd_sequences ─► crx_cc_dpd_sequences ─► build_cc_a4_deterioration ─► crx_cc_a4_deterioration
crx_cc_spell_table ─────────────────────────────────────────────────┘   (one row / account)          (one row / account in segment)

int_loan_master ──► build_rl_full_history ──► crx_rl_full_history ──► build_rl_dpd_sequences ─► crx_rl_dpd_sequences ─► build_rl_a4_deterioration ─► crx_rl_a4_deterioration
rl_spine ─────────┘   (F4, F5, F6)
```

**Bucket scale.** Every rule is written once, on the CC ("canonical") scale:
canonical = max(native + offset, 1), with CC offset 0 and RL offset 1.

| DPD | 0 | 1–30 | 31–60 | 61–90 | 91–120 | 121–150 | 151–180 | 181–210 | 210+ |
|---|---|---|---|---|---|---|---|---|---|
| CC native | 0 / 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 (cap) |
| RL native | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (cap = 180+) | — |
| canonical | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Segments: `60_180` = canonical 4–7 (CC native 4–7, RL native 3–6). `180_plus` = canonical
8+ (CC 8–9, RL 7). For RL 180+ the cap is RL 7, so "paying in default" means dropping
below RL 7. Outputs carry native buckets (`dlq_buckets`, `current_bucket`). Feature names
keep the reference's names: `months_since_4` means months since first reaching canonical 4
(CC 4, RL 3, i.e. 61–90 DPD).

**Node 1 — `build_dpd_sequences`**: one row per account, every account in the history.

| column | meaning |
|---|---|
| `build_status` | `ok` / `no_rows_in_window` (all rows before the floor) / `no_valid_rows` / `dropped_unresolvable_gap` (only with `on_unresolvable_gap: drop`) |
| `first_month`, `last_month`, `history_months` | the kept window (month-end dates) |
| `dlq_buckets` | array<int>, native, oldest → newest, gap-filled |
| `dpd_string` | the same, as the bank's string (leftmost = latest month), for the file-mode validator |
| `history_cropped` | older history exists but is not used (floor, gap truncation, or starts at the source's first month) |
| `n_gap_months_filled` / `_rolled` / `_inferred` | gap months filled by: neighbours agree / straight roll / short-gap inference |
| `n_cycle_shift_moves`, `n_months_truncated`, `n_dup_month_rows`, `n_invalid_rows` | audit counts |
| `legacy_drop` | **the old rule would have dropped this account** — reconciles with the 17,675 |
| `restructure_blind_spot_flag` | CC: any spell `restructured_entry` (R13). RL: `is_restructured` in any month |

Gap rules, in order (all in `build_history`, all counted):

1. **Cycle shift.** A month with two bills next to an empty interior month gives one bill
   to that month. The earlier bill moves back if the previous month is empty, otherwise
   the later bill moves forward.
2. Dedupe: the latest bill in the month (ties → worst bucket).
3. **Neighbours agree** on the canonical scale → fill (hold, or clean through; CC 0 = 1).
4. **Straight roll** when `R − L = gap + 1` on the canonical scale → `L+1, L+2, …` (the only path without a +2 jump).
5. **Inferred** when the gap is ≤ `max_inferred_gap_months` (default 2): carry the left
   value, roll as late as possible (`3 _ 4 → 3 3 4`, `6 _ _ 3 → 6 6 6 3`). Note that an
   inferred month in a spell reads as a hold, i.e. a payment, so it can move an account
   out of EPD. That is why it is counted, and why the default is short.
6. Anything else → **truncate**: keep the months after the gap and flag `history_cropped`.

**Node 2 — `build_deterioration`**: filters `build_status = 'ok'` and today's segment.
Features and the state come from the reference port. Output columns: `account_id,
det_state, det_state_label, det_state_option, det_segment, current_bucket,
n_gap_months_filled, left_censored, months_before_spell, n_blips, n_prior_episodes,
gap_prior_peak3, spell_pay_events, runup_len, runup_pays, last6_in_band, months_since_4,
chg_6m, n_glitches, n_jumps_repaired, n_jumps_left, [180+ extras], history_months,
history_cropped, n_months_truncated, history_stale_months, restructure_blind_spot_flag,
computed_at`. This is the old schema plus `det_segment`, `current_bucket`, `n_jumps_left`,
`history_months`, `history_cropped`, `n_months_truncated` and `history_stale_months`.

**Schema change:** `crx_*_dpd_sequences` changes from grain (account, month) to grain
(account) with an array. Its only consumer is Node 2. If anything else needs the long grid:

```python
seq.select("account_id", "first_month", F.posexplode("dlq_buckets").alias("t", "dlq_bucket")) \
   .withColumn("calendar_month", F.last_day(F.add_months("first_month", F.col("t"))))
```

**Python UDFs on the executors.** The per-account code is pickled **by value**
(`cloudpickle.register_pickle_by_value`, PySpark ≥ 3.3), so the executors do not need the
Kedro package installed. The local test proves this: the workers there cannot import
`crx_persona`. On PySpark < 3.3 the package must be importable on the executors (a wheel
or `--py-files`). If the cluster forbids Python UDFs entirely, keep the old window-function
code and apply F1–F8 and F10–F12 to it. F9 (exact parity) cannot be reached with
`lag`/`lead`; it would need Spark SQL `aggregate()` folds over the array.

---

## 3. Coverage — reaching 99.9%

Coverage = accounts classified ÷ accounts whose latest bucket is in the segment. With
`truncate`, every account with at least one valid row in the window is classified. So only
these lose coverage: `no_rows_in_window` (no bill since the floor), `no_valid_rows` (every
bucket NULL), and spine accounts missing from the history altogether (a key mismatch —
see `spine accounts found` in the RL log).

`prod_check.py` (run by you in PROD, §5 step P2) prints coverage per segment against the
99.9% target. It also reconciles with the old code: `old rule would have dropped` should
be close to 17,675 (same rule as the old `resolve_gaps`), followed by which new rule
rescued those accounts. If many are `truncated`, the gaps are long and real (missing
billing months) — ask the data owner before raising `max_inferred_gap_months`. The
truncated and cropped accounts should show state shares similar to the rest, apart from
fewer EPD / early-life (expected: they are cropped).

## 4. Tests

```bash
python docs/deterioration_states/spark/tests/test_parity.py     # no Spark: core vs numpy reference -> PARITY PASSED (~30 s)
python docs/deterioration_states/spark/tests/test_spark_e2e.py  # local Spark (Java 17, pyspark) -> SPARK E2E PASSED
```

The e2e test builds raw billing and loan-master tables from the synthetic generators, with
noise: same-day duplicates, unparseable `add_info`, cycle shifts, months missing between
equal neighbours, unresolvable 3-month gaps, history before the floor, and a double spine
key. It runs the actual node functions under ANSI mode and checks every account against
the expected state and cropped flag (CC 60–180, CC 180+, RL 60–180).

## 5. Shipping to the workplace repo

Two roles. **Sonnet** (workplace assistant): edits code and runs offline tests only — it
has no PROD data and must not load catalog datasets. **You**: run the pipelines in PROD
and paste the aggregate report back.

### Sonnet — code changes and offline tests (no catalog, no PROD data)

**S1 — unpack.** "Save BUNDLE.md raw at `docs/deterioration_states/BUNDLE.md`, create
`docs/deterioration_states/extract_bundle.py` from its Extractor section, run
`python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md`
— it must end with `0 mismatched`. Then run
`python docs/deterioration_states/spark/tests/test_parity.py` → must print `PARITY PASSED`.
If `pyspark` is missing, report it; do not change any code to work around it."

**S2 — impact scan, no edits yet.** "Read `docs/deterioration_states/spark/REVIEW_SPARK.md`.
In `src/enbd_collections/pipelines/crx_persona/`, list (a) every importer of
`_dpd_journey` and every name it imports (`grep -rn "_dpd_journey"`), (b) every dataset in
`conf/**/catalog*.yml` named `crx_cc_dpd_sequences`, `crx_rl_dpd_sequences`,
`crx_cc_a4_deterioration`, `crx_rl_a4_deterioration`, with format / partitioning / schema
settings, (c) every consumer of those four datasets in other pipelines, (d) the current
value of `_DPD_BUCKET_REGEX`. Report only — change nothing."

**S3 — apply.** "Replace, keeping the repo's own imports and conventions:
`crx_persona/_dpd_journey.py` ← `spark/crx_persona/_dpd_journey.py`;
`cc_full_history/nodes.py::build_cc_full_history`,
`rl_full_history/nodes.py::build_rl_full_history`, and `cc_a4_deterioration/nodes.py`,
`rl_a4_deterioration/nodes.py` ← the files under `spark/crx_persona/`. Keep the repo's
`_DPD_BUCKET_REGEX` value. If S2(a) found importers of names the new module no longer has
(`resolve_gaps`, `encode_transitions`, `classify_from_grid`, `BucketScheme` fields), stop
and show them to me. Merge `spark/conf/parameters_crx_persona_dpd_journey.yml` under the
existing `crx_persona:` block. If `rl_full_history`'s pipeline should pass
`params:crx_persona` (only needed for `log_stats`), add it. Update the catalog entries for
the two `*_dpd_sequences` datasets: the grain is now one row per account with an array
column `dlq_buckets` — drop any partitioning by month. Show me the full diff."

**S4 — offline verification.** "Run `python -m pytest` (or the repo's lint/test command)
on the changed files; run
`python -c "from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import create_pipeline as c; from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import create_pipeline as r; print(c().describe()); print(r().describe())"`;
and, if Java + local Spark work in the dev container,
`python docs/deterioration_states/spark/tests/test_spark_e2e.py 2000` → `SPARK E2E PASSED`
(synthetic data only). Report each result verbatim."

### You — in PROD, after Sonnet's changes are merged

**P1 — run.** First run on dev settings: `log_stats: true` in the params.

```bash
kedro run --pipeline=crx_cc_full_history       # whatever the repo calls the CC full-history pipeline
kedro run --pipeline=crx_cc_a4_deterioration
kedro run --pipeline=crx_rl_a4_deterioration    # after crx_rl_full_history
```

For the 180+ run, set `dpd_journey.segment: "180_plus"` (CC 8–9, RL 7) and re-run Node 2.
Node 1 does not depend on the segment.

**P2 — check.** In `kedro ipython` / a Kedro notebook:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "spark"))
from prod_check import report
report(catalog)                    # or report(catalog, products=("cc",))
```

It is read-only and prints aggregates only (counts and shares, no account ids or DPD
strings). Paste the block between `=== DPD_JOURNEY PROD CHECK START / END ===` back for
review.

**P3 — decide** (business owner): are truncated / inferred-gap accounts acceptable as
classified, and is the `unknown` share at 180+ acceptable as reported?

## 6. Open points

- `BucketScheme` and `classify_from_grid` were not visible. If other pipelines import them,
  W1 lists those importers before anything is overwritten.
- CC bucket meaning is assumed as in the table above (CC 2 = 1–30 DPD = RL 1). The node
  thresholds in the screenshots ("CC ≥3 / RL ≥2", "CC ≥2 / RL ≥1") imply exactly this
  offset of 1.
- RL 180+ uses the 180+ prototype tree with cap RL 7. It has not been validated on RL
  data — the 180+ tree is a prototype for CC too.
- The cycle-shift rule assumes two bills in one month next to an empty month are one
  shifted cycle. If cycles legitimately double up (a product change, re-issue),
  `n_cycle_shift_moves` will be high on those accounts — check a few dozen.
