# Handover: A3 payment credibility, review and refactor (written 2026-11-03)

For the Opus 5.5 session. The DE finished A3. The code is transcribed from photos and sits in the
mirror; nothing has been reviewed or changed. Read `CLAUDE.local.md` first (workplace-mirror
rules, working decisions D1–D6, bundle flow, lint rule), then `DESIGN_REVIEW.md` and the A1 / A2
specs for the precedent: one engine, thin per-product wrappers, fail-loud columns, readable docstrings.

## What is in the mirror (all verbatim, commits `1f50516`, `6fd7677`)

Under `workplace_mirror/src/enbd_collections/pipelines/crx_persona/`:

| File | Lines | Role |
|---|---|---|
| `cc_a3_payment_credibility/__init__.py` | 5 | exports `create_pipeline` |
| `.../constants.py` | 93 | CC thresholds, method names, `[CONFIRM]` tags |
| `.../_signals_common.py` | 1153 | window resolvers, cycle attribution, waterfall walk, due amount, Dim A streak, plans on record, refusal follow-ups |
| `.../nodes.py` | 1570 | 9 nodes; combiner `build_a3_payment_credibility` |
| `.../pipeline.py` | 238 | Kedro wiring |
| `rl_a3_payment_credibility/` (same 5 files) | 5/58/105/797/168 | RL adapters: shim over CC nodes, `build_rl_a3_dlq_cycles`, RL Dim B/C approaches, wrapped combiner |
| `_dcore_codes.py` | 281 | now complete: A2 sets plus A3 `REFUSING`, `RINGING`, `PROMISE_TO_PAY`, `NOT_REACHABLE`, `RETAIN_PTP`, `PAYMENT_CONFIRMED` |
| `conf/base/parameters/parameters_crx_persona.yml` | 80 | `a3_*`, `rl_a3_*` method switches, `cc_a3_history_floor_date` |

The `--exclude` on `_dcore_codes.py` in `make_bundle.py` is no longer needed for completeness,
but the file is shared with A2: ship it only if it changes.

## NOT in the mirror (ask the user to photograph before the part that needs it)
- `pipeline_registry.py` A3 entries and `catalog_crx.yml` A3 datasets (wiring review, catalog layers).
- `_spine_utils.py` (`join_spine_to_spell`, `rl_spine_as_cc_shim`): CC and RL both lean on it.
- `cc_raw_extract` `build_cc_acct_windows` (takes `cc_a3_history_floor_date`), `crx_cc_billing` /
  `crx_cc_balance` / `crx_cc_transactions` builders, `crx_rl_full_history`, `int_loan_master`.
- The A3 test modules (`test_cc_a3_*`, `test_a3_v2_scoring.py`), left to the workplace Sonnet.
- The DE's spec: `logs/A3_credibility_shared.xlsx`, sheet "A3 framework". The docstrings quote it
  as the source for the rules, so without it review is code-only. Ask for a copy or a spec dump.
- Memory notes say the A3 points were defined by the user earlier ("persona axes" memory):
  check them against the code instead of trusting docstrings.

## Photo caveats
Separator-rule lengths and comment wrapping are approximate. The `pipeline.py` docstring tables
(CC and RL) and `parameters_crx_persona.yml` comment blocks were re-aligned by eye.
Logged in `TRANSCRIPTION_NOTES.md` (handoffs 31, 32). Code lines are exact: `def`s sit on the photo line numbers.

## How A3 works today (read from the code, not verified against a spec)
State `a3_state_v1` in `payment_credibility_{high, moderate, low, unknown}` from points A+B+C
(0–5) minus a strong-negative demotion:
- **A commitments** (DCORE PTP and settlement instalments): level broken / kept / partly_kept / thin;
  points 0 / 2 / 1 / 0. Counts from `dcore_feat_ptp` / `dcore_feat_settlement`; broken streak from raw instalments.
- **B payments while delinquent**: regular 2 / some 1 / none 0. Window 3 m at 61-180, 6 m regular
  and 12 m any-payment at 180+, floor 100 AED at 180+. Three methods always computed
  (`single_payment_cycle_count` shipped, `payment_sum_waterfall`, `dpd_bucket_movement`).
- **C record before delinquency**: 12 m before t0, clean / not_clean / no_record, points 1 / 0 / 0;
  clean share 0.8, ≥ 3 billed months, strict 100% of due.
- **Strong negatives** (one reason, priority `broken_commitments` > `refusal` > `no_response`),
  evidence from `dcore_prm_followup_outcomes`.
- **State**: Unknown when A thin, B none, C no_record and no negative; High ≥ 4 points, Moderate ≥ 1,
  a negative demotes by one level; fixed confidences 0.90 / 0.75 / 0.60 / 0.
- **RL**: no billing ladder; cash = `int_loan_master.total_paid`, EMI = `monthly_emi_due`
  (forward-filled `monthly_emi_asof`); bucket scale 0-7; deep band = bucket 7; CC combiner reused through the shim.

## Observations already logged (REVIEW_OBSERVATIONS.md)
- O66 duplicate loop in `_strong_negative_reason` (`nodes.py:1313-1322`).
- O67 ticket history in docstrings and comments (D3 breach), worst in
  `resolve_dlq_waterfall_qualifying_months_cleared`.
- O68 repeated `crx_cc_transactions` line and duplicate pylint pragma.
- O69 hardcoded 24-month floor in the RL strong-negative node.

## Things worth checking first (my reading, unreviewed; do not treat as findings)
1. Rules the persona work already settled: customer signals at CIF level (A3 is account / agreement
   based; payment evidence is the account's own, so likely fine, but DCORE contact is per agreement);
   `model_id` from globals (CC combiner takes `params:model_id`; check no hardcoding); no spells / T0 (D5):
   **A3 still keys Dimension C and the Dim B window on spells and `t0`** (`crx_cc_spell_table`,
   `crx_rl_a4_spine.spell_id`). Your notes say spells stay only until the DE moves A3 off them; decide
   with the user whether this refactor does that.
2. Shared layers: A3 nodes read `crx_cc_billing`, `crx_cc_balance`, `crx_cc_transactions`,
   `crx_cc_full_history` and `dcore_*` prm / feat / int tables: check against "one layer per node" and "no
   stg_/raw_ in persona nodes" once the catalog is photographed.
3. `build_a3_payment_credibility` shadow columns for all methods are computed from the shipped
   method's strong negatives only (the docstring says so): decide whether the shadows are worth keeping.
4. `cc_a3_history_floor_date` (2024-01-01, marked TEMPORARY) silently turns any spell with t0 before
   it into "no record"; its effect on the latest-month distribution should be measured.
5. Month-end observation dates: A3 joins `cc_spine` (mid-month billing dates still in PROD, per the A2
   notes) to cycle / statement dates; check each join for the same date trap A1 / A2 fixed.
6. RL `monthly_emi_due` and `total_paid` come from `int_loan_master`; A1's RL anchor uses
   `installment_due_amount` on the observation month's snapshot (= `monthly_emi_due`); A1 notes that EMI
   payment behaviour belongs to A3, so A3 is the owner of the cash-vs-EMI logic.
7. Strong-negative rule thresholds (3 contact dates, refusal follow-ups, no-response) and window
   lengths are `[CONFIRM]` in `constants.py`: they are business decisions, so surface as questions.
8. Dead or duplicated code: unused methods once the user picks the shipped approach per product.

## Working rules that matter most here (from `CLAUDE.local.md`, do not re-litigate)
- The user decides every spec-vs-code discrepancy: ask explicitly, hold the bundle.
- Fixes are folded into the refactor bundle; PROD checks are distribution + old-vs-new crosstab.
- Kedro I/O only through node inputs and outputs; checks are temporary nodes and temporary catalog entries.
- Lint every shipped file: black (88) + ruff + pylint (`PYTHONPATH=src pylint --disable=relative-beyond-top-level`).
- Next bundle number: check `ls workplace_mirror/bundles` (13 shipped; next is 14, but `make_bundle.py` numbers by file count).
- Another session may commit on `feature/persona_redesign`: `git pull`, commit only A3 files (prefix `A3:`),
  push, and `--exclude` other axes' files when building the bundle.
- A3's DE-owned modules (`cc_a3_payment_credibility`, `rl_a3_payment_credibility`) were never to be
  transcribed; the user lifted that for this review. They are the baseline of the next bundle (`--base`
  a commit that has them).

## Suggested order
1. Ask the user for the missing photos / spec above (registry, catalog, `_spine_utils`, the spec).
2. Read `nodes.py` (CC) end to end, then the RL adapter; write a short A3 review (findings with H/M/L and file:line)
   into `REVIEW_OBSERVATIONS.md` (continue from O70) and the open questions for the user.
3. Write `specs/A3_credibility_spec.md` in the A1 / A2 style (decisions D-A3-n) and a conformance test
   (`checks/a3_engine_spec.py`) once the user answers.
4. Plan the bundle in `DESIGN_REVIEW.md` (engine + wrappers, fail-loud columns, no spells if decided),
   then build, lint, add the check pipeline and the cleanup prompt.
