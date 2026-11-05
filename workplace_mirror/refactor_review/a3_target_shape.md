# A3 target shape (S1, between rounds 1 and 2)

Supersedes "Target A3 shape" in `round_1/proposals/S1.md`. Input: worktree HEAD `2942237`, spec
`specs/A3_credibility_spec.md` (D-A3-1..21, Validations, Open), `bundle_helpers/a3_final/` (handover,
DE sheet, V1–V4 review, V1c summary, V1d prompt), O66–O89, Q-11..13, Q-20, Q-22, Q-25, Q-27, Q-28.
Nothing in `src` changes here; A3 files stay tier A.

The aim: every decided rule has one code home, and every pending one is a single named constant,
parameter or predicate. No pending option needs a change to the shared layer that is not listed in
§6 (round 2 items).

## 1. Shape

One engine, thin product wrappers (the A1 / A2 / A4 shape). A product supplies only what really
differs: **dues** (what one month asks for) and **payments** (dated money into the account).
Everything else is written once.

```
crx_persona/
  _common.py           GRAIN · SEG_* · segment · window_months · window_start
                       window_agg(start=) · pit_latest · string_key · require_columns
                       left_join_all · log_latest_month · dcore_account_events · GONE_DARK_DAYS
  scoring_engine.py    Scorecard · Dimension · Override · state_label        (§5, round 2 item 1)
  _dpd_journey/anchor.py  episode_start   (A3's anchor, D-A3-2; A1 does not use it)
  a3_credibility/
    __init__.py
    constants.py       every D-A3-16 threshold, the band dicts, KEPT_BY, the Scorecard
    sources.py         build_cycle_ledger · build_instalments
    signals.py         build_commitment_signals (A) · build_dlq_payment_signals (B)
                       build_pre_dlq_payment_signals (C) · build_contact_signals (refusal + diagnostics)
    classify.py        build_a3_credibility (Scorecard, output select, log)
    pipeline.py        create_a3_pipeline(product, output, dues, payments)
  cc_a3_payment_credibility/
    nodes.py           build_cc_a3_dues · build_cc_a3_payments
    pipeline.py        create_pipeline() -> create_a3_pipeline("cc", ...)
  rl_a3_payment_credibility/
    nodes.py           build_rl_a3_dues · build_rl_a3_payments
    pipeline.py        create_pipeline() -> create_a3_pipeline("rl", ...)
```

### Contracts between wrappers and engine

| Dataset | Grain | Columns | Built by |
|---|---|---|---|
| `crx_<p>_a3_dues` (memory) | (account_id, cycle_end) | `cycle_start`, `cycle_end` (the statement / month end that shows the cycle's result), `due_amount` (one month's due, Dim B), `billed_amount` (what "paid as billed" compares with, Dim C) | CC: statements, D-A3-15 filter, oldest open bucket 07..01 → `minimum_due`, D-A3-12 bucket-08 fallback (into `due_amount` only); RL: month ends, `due_amount = billed_amount = monthly_emi_asof` (D-A3-13) |
| `crx_<p>_a3_payments` (memory) | one row per payment | `account_id`, `pay_from`, `pay_date`, `amount` — the money arrived in `[pay_from, pay_date]` | CC: card payments (`txn_category = payment`, no post-block fee), `pay_from = pay_date` = banking date; RL: `int_loan_master.total_paid > 0`, `pay_from` = first day of the month, `pay_date` = month end |

`pay_from` / `pay_date` carry the date precision, so "after the refusal" (`pay_from > refusal_day`),
"by the due date" (`pay_from <= due_date + grace`) and the ledger attribution
(`cycle_start < pay_date <= cycle_end`) are written once and read correctly for both products: an RL
month counts after a refusal only from the next month (D-A3-14), and an RL instalment is matched by
month (D-A3-11). A dated RL source later (`prm_loan_payments`) only sets `pay_from = pay_date`.

### Nodes (`<p>` = cc | rl; names `build_crx_<p>_a3_<step>`, dict inputs, one `TAGS`)

| # | Node | Inputs | Output (catalog) |
|---|---|---|---|
| 1 | episode (engine node on `_dpd_journey.episode_start`) | `crx_<p>_obs_base`, `crx_<p>_a4_deterioration` | `crx_<p>_a3_episode` (new) |
| 2 | dues (wrapper) | CC `crx_cc_billing`, `crx_cc_balance`, `params:cc_a3_history_floor_date`; RL `int_loan_master`, `crx_rl_obs_base` | `crx_<p>_a3_dues` (memory) |
| 3 | payments (wrapper) | CC `crx_cc_transactions`; RL `int_loan_master`, `crx_rl_obs_base` | `crx_<p>_a3_payments` (memory) |
| 4 | ledger | dues, payments | `crx_cc_a3_payment_cycles` / `crx_rl_a3_dlq_cycles` (kept names) |
| 5 | instalments | `dcore_int_ptp`, `dcore_prm_promise_instalments`, `dcore_int_settlement`, `dcore_prm_settlement_schedule_instalments`, `prm_dcore_account_agreements`, obs base | `crx_<p>_a3_instalments` (new; layer: Q-32) |
| 6 | Dim A | obs base, episode, instalments, payments | `crx_<p>_a3_commitment_signals` (kept) |
| 7 | Dim B | obs base, episode, ledger, `params:model_id` | `crx_<p>_a3_dlq_payment_signals_single_payment_cycle_count` (kept name) |
| 8 | Dim C | obs base, episode, ledger | `crx_<p>_a3_pre_dlq_payment_signals_single_payment_cycle_count` (kept name) |
| 9 | contact | obs base, episode, `dcore_prm_followup_outcomes`, `prm_dcore_account_agreements`, instalments, payments, `params:model_id` | `crx_<p>_a3_strong_negative_signals` (kept) |
| 10 | state | obs base, episode, nodes 6–9, `params:model_id`, `params:crx_persona.persona_end_date` | `crx_<p>_a3_payment_credibility` (kept) |

Dropping the `_single_payment_cycle_count` suffix is a rename (PLAN rule 5): ask at bundle time, not
needed for the design. Gone from the catalog: the 3 waterfall / bucket-movement datasets per product.
No longer read by A3: `cc_spine`, `crx_cc_spell_table`, `crx_rl_a4_spine`, `dcore_observation_spine`,
`dcore_feat_ptp`, `dcore_feat_settlement`, `crx_cc_full_history`, `crx_rl_full_history`.

Run order per model_id: A4 → A3 (node 1 reads A4). D-A3-18: `cc_raw_extract.build_cc_acct_windows`
(tier K, edited in the A3 bundle) takes its window from `crx_cc_a3_episode`
(`min(episode_start) − 13 months` per account, floored at `cc_a3_history_floor_date`) instead of the
spell table, so the CC order is A4 → episode → raw extract → A3. No cycle: A4 reads
`crx_cc_full_history`, not the extracts.

## 2. Onset bounds (one private helper)

`episode_start` is a month (first day; Q-11). A3 derives its three bounds in one place,
`signals._onset_bounds()`, so a Q-11 / Q-31 answer edits one function:

| Column | Today's rule it reproduces | Value |
|---|---|---|
| `dlq_from` (Dim B lower bound, `window_agg(start=)`) | `evidence > t0`: the onset statement is not a payment in delinquency | `add_months(episode_start, 1)` |
| Dim C window (A3-private filter on the evidence date) | `[t0 − 12 m, t0)`: the onset statement is not pre-delinquency either | the 12 calendar months before `episode_start`'s month |
| `_in_episode(day)` (DCORE, plans, refusal) | `[t0, obs)` | `episode_start <= day <= observation_date` (inclusive, Q-22 / Q-27) |

On CC (~99% one statement a month, D-A3-15) and RL (month ends) the month bounds select the same
statements as today's `t0` bounds. Where they differ is Q-11 (the first episode month's DCORE events).

## 3. Decision map (21 / 21)

| Decision | Code home | Shared helper |
|---|---|---|
| D-A3-1 grain = obs base | every node's base is `crx_<p>_obs_base`; node 10 builds on `left_join_all(obs_base, …)` (not the bridge, O70) | `GRAIN`, `left_join_all`, `require_columns` |
| D-A3-2 anchor + three windows | node 1; `signals._onset_bounds` (§2) | `episode_start`, `window_agg(start=)`, `window_start` |
| D-A3-3 one method per dimension | one builder per dimension; no method params, no per-method nodes, columns or pair validation | — |
| D-A3-4 output | `classify.OUTPUT_COLUMNS`; `a3_state`; no confidence / provenance / `computed_at` | `state_label` |
| D-A3-5 100 AED in Dim B | `constants.MIN_PAYMENT_AED`; `signals._qualifies(paid, due) = paid >= greatest(QUALIFYING_SHARE * due, MIN_PAYMENT_AED)`, `signals._any_payment(paid) = paid >= MIN_PAYMENT_AED`; Dim C's `_paid_as_billed` does not use it | — |
| D-A3-6 band by model_id | `constants.REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}`, `ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}`; Regular window = `window_months(model_id)` | `segment`, `window_months`, `SEG_*` |
| D-A3-7 account-level DCORE | node 5 links plans through `prm_dcore_account_agreements`; node 9 reads `dcore_account_events` | `dcore_account_events` |
| D-A3-8 paid before the next statement | node 4 `build_cycle_ledger`: `paid_amount` = payments with `cycle_start < pay_date <= cycle_end`; `on_time_*` gone | — |
| D-A3-9 commitments from instalments | node 6: one `window_agg(months=COMMITMENT_MONTHS, start="episode_start", date_col="due_date", key="account_id")` with three aggregates (concluded, kept, last-N concluded as `slice(sort_array(collect_list(struct(due_date, broken)), False), 1, BROKEN_STREAK)`); predicates `_concluded`, `_kept` | `window_agg(start=)` |
| D-A3-10 history floor kept and measured | `params:cc_a3_history_floor_date` in `build_cc_a3_dues` (+ the extract window); output carries `pre_dlq_window_start` and `episode_left_censored` so the bundle check counts floor-cut rows | — |
| D-A3-11 kept by payments unless DCORE proves reliable | `constants.KEPT_BY`, `KEPT_GRACE_DAYS`; `signals._kept()` (§4 P1) | — |
| D-A3-12 bucket-08 due | `cc_a3_payment_credibility/nodes._bucket08_due` (today's `resolve_bucket08_fallback_due`), coalesced into `due_amount` | (`pit_latest` not needed) |
| D-A3-13 RL record uses last known EMI | `build_rl_a3_dues`: `billed_amount = monthly_emi_asof` | `string_key` |
| D-A3-14 RL refusal payment test | `signals._paid_after(day)`: `pay_from > day` and amount ≥ `MIN_PAYMENT_AED` on the payments contract | — |
| D-A3-15 one-month CC cycles | `cc_…/nodes`: `CYCLE_MAX_DAYS = 62`, `FLOOR_LOOKBACK_DAYS = 35` in `build_cc_a3_dues` | — |
| D-A3-16 DE thresholds | `a3_credibility/constants.py` (one named constant each, sheet row in the comment); the O75 hard-coded `>= 2` becomes `MIN_CONCLUDED` (same value) | — |
| D-A3-17 output carries every input | `classify.OUTPUT_COLUMNS` (episode, windows, levels, points per dimension, counts, flags, reason, evidence) | `Scorecard` points / reason columns |
| D-A3-18 A3 builds its own sources | wrapper nodes 2–3 on the tier-K extracts; `build_cc_acct_windows` re-anchored on `crx_cc_a3_episode` | `episode_start` |
| D-A3-19 no contact negative; two diagnostics | node 9: `a3_no_pickup_after_contact` (≥ `GONE_DARK_DAYS[segment]` ringing / no-answer / left-message days after a right-party contact, no dead-line outcome between), `a3_hung_up_last`; not in the Scorecard | `GONE_DARK_DAYS` (round 2 item 4), `dcore_account_events` |
| D-A3-20 refusal negative, dispute a column | node 9 `_latest_rpc` (one `max(struct(day, not_refusal, disposition))` aggregate, S2-H-01), `a3_refusal_flag`, `a3_dispute_flag`; Scorecard `Override("refusal", DEMOTE)`; `_dcore_codes` split (handoff N-1) | `Scorecard` |
| D-A3-21 flow overlap with A4 reported | no code: the bundle check / axis report crosstab Dim B / C with A4 | — |

## 4. Pending and potential decisions

Each row: where the choice lives, what each option changes, and whether the shared layer moves.
"Shared: none" means every option is expressible with today's helpers plus the §6 items.

| # | Item | Options | Choice lives in | What changes per option | Shared |
|---|---|---|---|---|---|
| P1 | D-A3-11 kept vs broken (V1d) | (a) DCORE status; (b) ledger at the due date; (c) ledger + grace days; (d) hybrid: DCORE `overdue` = broken (V1c: always confirmed), DCORE `paid` kept only if the ledger confirms | `constants.KEPT_BY` ∈ {`dcore`, `ledger`, `hybrid`}, `KEPT_GRACE_DAYS` (0 / 5), predicate `signals._kept()` | (a) node 6 does not read payments (input dropped); (b)–(d) node 6 reads payments and allocates them to a plan's instalments in due-date order (cumulative paid since plan start ≥ cumulative due, the V1c rule; one window over the plan's instalments, engine-private) | none |
| P2 | Broken commitments (V1d): negative, cap or drop | (a) demote one level (DE sheet); (b) cap: no High; (c) drop: Broken is a level with 0 points only | `constants.BROKEN_OVERRIDE` = `Override("broken_commitments", "a3_broken_flag", DEMOTE \| CAP_AT "moderate")` or omitted | one line of the Scorecard declaration; reason column follows | none (Scorecard modes) |
| P3 | Due-date grace (user, V1d) | 0 / 5 days / until the next statement | `KEPT_GRACE_DAYS` | `_kept` cut-off | none |
| P4 | V1d H1 / H4: money outside card payments | (a) card payments only (D-A3-7); (b) more credit categories / adjustments; (c) the CIF's other accounts (FTR) | CC `build_cc_a3_payments` (`PAYMENT_CATEGORIES` constant; (c) adds an input) | the payments contract is unchanged; (c) breaks D-A3-7's "payments are the account's own" and is a user decision | none |
| P5 | GRR calibration: Moderate from 2, High from 3 (V4) | values | `constants.MODERATE_FROM`, `HIGH_FROM` (Scorecard) | constants only | none |
| P6 | High needs more than points (e.g. not commitments-only) | Scorecard `high_min_dimensions`, `high_current` | constants | declaration only | none (Scorecard gate) |
| P7 | RL exact payments (`prm_loan_payments`) | later option | `build_rl_a3_payments` source | `pay_from = pay_date` (day grain); D-A3-11 / -14 sharpen with no engine change | none |
| P8 | CC sources into the CC primaries / ledger as a CC feature | later option (spec Open) | wrapper nodes 2–3 read the primaries; node 4 may move to the CC feature pipeline | the engine reads the ledger by name, unchanged | none |
| P9 | Right-party definition (O80) | V1c: the two extra names never fire; keep or add | `signals.RIGHT_PARTY` (one set built from `_dcore_codes`) | one set | none |
| Q-11 | Anchor day | (a) first of month; (b) last day of the month; (c) exact first delinquent statement | `signals._onset_bounds` | (a)/(b) one expression; (c) a CC-wrapper refinement node joining `crx_cc_full_history` (product data, not shared) | none |
| Q-12 | Rows A4 does not score | (a) Unknown, reason `no_episode`; (b) fall back to `window_start(ANY_PAYMENT_MONTHS)`, no Dim C; (c) the A4 history's first month | (a) Scorecard `unknown_also` + `a3_unknown_reason`; (b) `coalesce` in `_onset_bounds` | (a)/(b) A3 only; **(c) needs the shared layer**: rows A4 drops have no A4 row, so the first month must come from `crx_<p>_dpd_sequences` (a `history_first_month(obs_base, sequences)` helper in `_dpd_journey/anchor.py`). Recommend (a) | (c) only |
| Q-13 | Calendar vs day windows | (a) `window_start` everywhere; (b) day arithmetic for commitments | `window_agg` call in node 6 | (b) would be a private filter (`due_date >= add_months(obs, -12)`) instead of `window_agg` | none |
| Q-20 | Quiet-null guards | settled by the spec ("Open": all A3 sources are required, D2) | `require_columns` in every node | — | none |
| Q-22 / Q-27 | DCORE bound at the observation date | (a) inclusive; (b) exclusive | `signals._in_episode` | (b) changes one comparison there; `window_agg` stays inclusive (no mode switch) | none |
| Q-25 | Censored anchor | (a) censored rows: Dim C `no_record` with reason `censored`, windows from the observation lookback; (b) use as is | `_onset_bounds` + `a3_unknown_reason` / `pre_dlq_reason` | A3 only, once `episode_left_censored` means "history cropped and the episode starts in the first kept month" (round 2 item 3) | item 3 |
| Q-28 | Tie on the latest right-party contact | (a) largest disposition; (b) a named priority | `signals.DISPOSITION_RANK` (b) inside the `max(struct)` | struct field only | none |
| Q-29 | Unit of "a payment ≥ 100 AED after the refusal" (new) | (a) payments after the refusal day, summed per cycle / month; (b) summed since the refusal (CC code at 180+ today); (c) one payment | `signals._paid_after` | aggregate expression only | none |
| Q-30 | DCORE look-back at 180+ (new) | (a) unbounded `[episode_start, obs]` (spec); (b) a cap, e.g. 24 months, both products (RL has it today as a pruning floor, O69) | `constants.DCORE_MAX_MONTHS` (None or N) in `_in_episode`; the partition floor = `persona_start_date − N` from params (no Spark action) | (a) CC reads all follow-up history, as today | none |
| Q-31 | Onset cycle (new) | (a) in neither B nor C (today); (b) in C; (c) in B | `_onset_bounds` | one bound each | none |
| Q-32 | Layer of the instalment node (new; V1 left it open) | (a) A3 source node mixing `dcore_int_*` + `dcore_prm_*` (as today); (b) a DCORE primary `dcore_prm_commitment_instalments` (DE pipeline) | node 5's inputs | (b) node 5 becomes a read of one primary; nodes 6 / 9 unchanged | none |

Validations still open, and where their answer lands: V1 section 4 (Dim A level DCORE vs ledger) and
the floor count (D-A3-10) come from the bundle check on the new output columns; V1d sets P1–P4;
the 180+ runs check `ANY_PAYMENT_MONTHS` / `REGULAR_FROM` at 180+ (constants); RL V2 N1 / N2 / N4
failed but D-A3-19 already keeps them out of the state (diagnostic columns only).

## 5. Scoring: one `Scorecard` for A1 and A3

The central shared item (round 2 item 1, full text and A1 diff in `round_1/triage.md`). A3's state:

```python
# D-A3-16 points (DE sheet rows). Dim A = commitments, Dim B = payments while delinquent,
# Dim C = record before delinquency.
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1}  # Dim A, D-A3-9 / D-A3-11
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}  # Dim B, D-A3-3 / D-A3-5
PRE_DLQ_POINTS = {"clean": 1}  # Dim C, D-A3-2 / D-A3-13
HIGH_FROM, MODERATE_FROM = 4, 1  # D-A3-16 cut-offs (GRR calibration: V4)

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, silent=("thin",)),
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, silent=("none",)),
        Dimension("pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, silent=("no_record",)),
    ),
    overrides=(BROKEN_OVERRIDE, Override("refusal", "a3_refusal_flag", DEMOTE)),  # order = priority
    labels=DISPLAY_NAMES,  # house label-map name, as A1; payment_credibility_{high,moderate,low,unknown}
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
scored = SCORECARD.score(df)  # a3_<dim>_points, a3_points_total, a3_state, a3_override, a3_reason
```

`a3_override` is today's `a3_strong_negative_reason`; `a3_reason` (override, else the top dimension)
answers Q-26 for A3. Unknown = every dimension silent and no override, the DE sheet's rule. Broken has
0 points but is not silent, so it is never Unknown, whichever P2 option is taken.

## 6. Shared-layer gaps (round 2 items, in `round_1/triage.md`)

1. `scoring_engine.Scorecard` (+ `Dimension`, `Override`), replacing `StateLadder`; A1 moves onto it.
2. (withdrawn) `window_agg(before=)`: A1 reads no pre-delinquency window (GRR), so Dim C is its only
   caller; the pre-onset window is an A3-private filter.
3. `episode_start`: `episode_left_censored = left_censored AND history_cropped` (Q-25; a fix to the
   existing A3 helper).
4. `GONE_DARK_DAYS` moves to `_common` (A2 reachability, A3 D-A3-19 diagnostic).
5. The episode node stays in the A3 engine (`crx_<p>_a3_episode`); text only in round 2.

Checked, not gaps:
- `window_agg` / `pit_latest` with `key="account_id"` (the key is also in `GRAIN`): run locally,
  correct.
- The DCORE bound and look-back: `_in_episode`, A3-private.
- The cycle ledger: one engine function serving both products; no other axis needs it.
- Rule / reason columns: the Scorecard.
- The "oldest open bucket" (S6-H04): inline in A3 and A1 (deferred by R-O).
- A `since` floor on `dcore_account_events`: only A3 would use it, so A3 filters itself.

## 7. What goes, and the size after

| Goes | Lines today |
|---|---|
| `cc_a3_payment_credibility/_signals_common.py` (spell windows, waterfall walk, bucket movement, `payment_meets_floor`, the per-method window aggregators, the pooled streak window, plan and refusal follow-up joins) | 1,153 |
| CC `nodes.py`: bridge + 2 `.count()`, `_guarded_feat`, `_null_disposition`, 5 per-method builders, pair validation, `_select_shipped_methods`, the duplicate reason loop (O66), `_a3_state_col`, confidence / provenance, `_log_a3_stats` | most of 1,570 |
| RL adapters (`_signals_common.py`, CC shims, wrapped combiner, method switches) | 105 + most of 797 |
| `constants.py` ×2 (method names, `_CONF_*`, bucket-scale translations, duplicated RL copies) | 151 |
| `pipeline.py` ×2 (18 nodes → 10 per product, in one factory) | 406 |
| params `a3_*_method`, `rl_a3_*_method` (4 keys) | — |

Estimate after the rebuild: engine ~650 (constants 60, sources 150, signals 300, classify 90,
pipeline 110), CC wrapper ~170 (dues with the bucket logic, payments, 15-line pipeline), RL wrapper
~70. **~890 lines against 4,192 today (−79%).** P1 (b)–(d) adds ~40 to `signals` for the cumulative
allocation.

## 8. Build order for the A3 session

1. Round 2 lands items 1–4 (shared layer, A1 on the Scorecard, golden green).
2. `a3_credibility/constants.py` + Scorecard declaration (§5), with `checks/a3_engine_spec.py` cases
   for the ladder (the DE sheet's 72-cell map is the test table).
3. Episode node and the two wrapper source nodes per product; ledger (node 4) checked against
   today's `crx_cc_a3_payment_cycles` / `crx_rl_a3_dlq_cycles` on cycles both have.
4. Dim B and Dim C (nodes 7–8): reproduce today's shipped-method levels where the anchor month equals
   `t0`'s month (V1: 19,290 / 19,292 CC).
5. Instalments + Dim A (nodes 5–6) with `KEPT_BY = "dcore"` first (matches V1b counts), then the
   ledger options once V1d is back.
6. Contact node 9 (refusal, dispute, diagnostics) after the `_dcore_codes` split.
7. Node 10, output columns, `log_latest_month`; delete the old nodes, params and catalog entries;
   rescope `build_cc_acct_windows`.
8. Bundle check: old-vs-new crosstab, floor-cut and censored counts, V1 section 4 (Dim A by DCORE
   vs ledger) from the new columns.
