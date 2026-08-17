# Label and Feature Specifications

Formula-level definitions for the label, spell and feature tasks. Conventions:
- `obs` = observation_date. All features use data `< obs` (R2). A4 additionally `≤ T0`.
- Field/table names are illustrative — resolve against the workplace repo's own docs
  and code, never guessed (R9).
- `CONFIRM` marks a default the user/business must ratify. `[COND: X]` marks a feature
  only computable where domain X exists; emit NULL + let `relationship_breadth` carry
  the coverage signal.

## 1. Labels

Payment definition (shared): `payments(a, t1, t2]` = sum of customer-initiated credits
to the account in `(t1, t2]`, excluding fee/interest postings, reversals, internal
adjustments, **and restructure/succession postings** (R13). Exact posting-type codes:
`<<FILL-IN>>`.

**⚠ Succession exclusion is not optional.** A restructure closes the account and opens a
replacement; if the closing credit is not excluded, a restructure reads as full recovery
and the label is inverted (debt moved, not repaid). Until T03/T04 identifies successions
reliably, exclude via closure-posting type and flag affected accounts. Emit
`succession_excluded_flag` on every label row so contamination is measurable.

| Label | Definition | Params (defaults) |
|---|---|---|
| `futility_60_180` | 1 if `payments(obs, obs+N] <= ε` else 0 | N = 3 months CONFIRM (O4); ε = min(100 AED, 0.5% × outstanding_at_obs) CONFIRM (O5) |
| `recovery_aed_60_180` | `payments(obs, obs+N]` (continuous) | same N |
| `any_recovery_180p` | 1 if `payments(obs, obs+6m] > floor` | floor = 100 AED CONFIRM — a noise floor, not a business threshold |
| `recovery_amount_180p` | `payments(obs, obs+6m]`, modelled only where `any_recovery_180p = 1` (hurdle part 2) | |
| Legacy (reports only, R11) | roll label; 5%/1000 AED label | unchanged |

Restructure handling (R13, from T02/T03): add `restructured_in_horizon` flag. Default =
exclude restructured rows from futility *training*, keep them in reporting, and never
score a restructure as recovery. CONFIRM once O14 clarifies where the successor account
starts.

Leakage tests to implement: labels read only `(obs, obs+N]`; features only `< obs`;
assert in pipeline tests, not comments.

## 2. Spell / T0 table

Output grain: `(account_id, spell_id)`. **Inputs differ by unit (R15) — two derivation
paths:**

**CC — use the existing 24-month DPD bucket history feature.** It stores a per-month
bucket string (e.g. `33321000000000…`). T0 is the transition from `0` to non-zero;
spell end is the return to `0`. This makes CC spell derivation nearly free — reuse it
rather than reconstructing from raw DPD (R14). Confirm before use: string orientation
(most-recent-first or last?), the as-of reference month, and the bucket encoding.

Two limitations to handle explicitly:
- **24-month horizon.** A spell starting more than 24 months ago is unlocatable — the
  string is entirely non-zero and T0 falls outside it. This affects the 180+ >2y cohort
  exactly, and is an independent reason not to score that book from internal history.
  Emit `t0_censored_flag = 1` rather than guessing a T0.
- **Monthly resolution.** T0 resolves to a month, not a day. For CC this can optionally
  be refined to a day using the payment/balance tables — locate the month cheaply from
  the string, then refine. Record which resolution was used.

**Loans — no equivalent feature exists.** Buckets must be reconstructed from the full
data model (month-end snapshots), which is real work and part of the separate loan
pipeline. Resolution is monthly by construction.

Derivation (both paths, once buckets are available):
1. Order the monthly bucket series per account.
2. A spell starts at the first period with `DPD > 0` following `DPD = 0` (or account
   origin). `T0` = that period's date.
3. A spell ends at the first later snapshot with `DPD = 0` (cure) or at
   write-off/closure (terminal) or remains open.
4. **Restructures (R13) — succession, not reset.** The old account closes and a new one
   opens, so the old account's spell simply *ends at closure* (`spell_end_reason =
   'restructure_closure'` where identifiable). The successor account starts its own
   spell history, beginning at DPD 0, lower, or the same bucket — not uniform (O14).
   Do **not** bridge DPD resets within an account; that mechanic does not exist here.
5. **Inherited history.** Where T03/T04 supplies a link, the successor row carries
   `predecessor_account_id` and `inherited_history_flag = 1`, and A4 windows may be
   extended back through the predecessor's timeline (its own T0 becomes the effective
   anchor). Without a link the successor is a known A4 blind spot — set
   `inherited_history_flag = 0` and let coverage reporting show it.
6. `current_spell(obs)` = the spell containing `obs`. Every A4 feature row is keyed by
   `(account_id, spell_id)` and joined to observations via `current_spell`.

Columns: `account_id, account_type, spell_id, t0, spell_end, spell_end_reason,
predecessor_account_id, inherited_history_flag, max_dpd_so_far, days_to_dpd30,
days_to_dpd60` (the last two: within-spell, NULL until reached; safe at obs because obs
is inside the spell and those events precede it for the 60+/180+ populations).

Built separately per source system (R3/S15): CC and loan accounts have different
structures, so this is two pipelines sharing one output schema.

Invariant tests: spells per account non-overlapping; `t0 <= obs <= spell_end` for every
joined observation; DPD = 0 outside spells; no spell bridges an account closure; where
`inherited_history_flag = 1`, the predecessor link resolves to exactly one account.

## 3. A4 — manner-of-deterioration features

### 3.0 Anchoring — three regimes, not one

Existing CC outflow/transaction features are anchored on the **card block date**
(~60 DPD). That anchor is downstream of the deterioration and is an *operational*
event: a 12-month lookback from block mixes pre-delinquency behaviour with the
delinquency period, and if block policy ever changed the anchor moved with it, breaking
comparability across time. T0 is a customer event and policy-independent.

The fix is not to discard the block-anchored features — they measure a different and
useful regime. Separate three windows explicitly:

| Window | Span | What it measures | Feature family |
|---|---|---|---|
| `W_pre` | `[T0−12m, T0)` | How they deteriorated *into* delinquency — shock vs spiral | **A4 core** (§3.1–§3.4) |
| `W_early` | `[T0, block_date)` | How they behaved *once* delinquent but still able to transact | **Early-delinquency response** — a willingness-flavoured signal (see below) |
| post-block | `[block_date, …)` | Card outflow is structurally near-zero (the instrument is disabled) | Only payments, digital, other products remain — this is the "dry data" problem stated precisely |

**`W_early` is worth keeping as its own family.** Continuing to spend after missing
payments means the customer is prioritising other outgoings — a willingness signal.
Going quiet immediately points to shock or departure. That distinction is invisible in
the pre-T0 window and is exactly what the existing block-anchored features can be
reused for, relabelled.

**Also derive:** `t0_to_block_days` and `blocked_flag`. If blocking is purely
DPD-triggered these are mechanical (and belong with the state features, not here); if
the timing varies, check whether the variation is informative or just policy noise
(T06).

**Consequence for T11/T14/T15:** existing block-anchored outflow features are the
principal **ADAPT** case — re-anchor to T0 for A4, and retain the block-anchored
originals as `W_early` features rather than rebuilding either.

### 3.1 onwards — feature definitions (all on `W_pre` unless stated)

Windows (relative to T0, per T05 availability): `W12 = W_pre = [T0−365d, T0)`,
`H1 = [T0−365d, T0−90d)`, `H2 = [T0−90d, T0)`. Monthly series over W12: payments
`P_m`, amount due `D_m`, utilisation `U_m`, spend `S_m`, cash advances `CA_m`,
fees `F_m`. Slopes = OLS over month index; require ≥ 4 non-null months else NULL.

### 3.1 Payment periodicity and trajectory (income proxy)

| Feature | Definition |
|---|---|
| `pay_dom_std` | std of payment day-of-month over W12; NULL if < 3 payments |
| `pay_dom_window_share` | share of active months with ≥ 1 payment within ±2 days of the modal payment day |
| `pay_dom_drift` | OLS slope of payment day-of-month vs month index (positive = paying later and later — distress signature) |
| `pay_gap_max_d`, `pay_gap_last_d` | max gap between consecutive payments in W12; days from last payment to T0 |
| `pay_ratio_mean_h1`, `pay_ratio_mean_h2` | mean of `P_m / D_m` (cap at 2, `D_m > 0` months only) |
| `pay_ratio_slope` | OLS slope of `P_m / D_m` |
| `min_pay_share_w12` | share of months where payment ∈ [0.9, 1.1] × minimum due |
| `months_since_full_pay_t0` | months since last full statement payment (full-pay flag: `<<FILL-IN source>>`) |

### 3.2 Utilisation, spend, liquidity stress

| Feature | Definition |
|---|---|
| `util_mean_h1`, `util_mean_h2`, `util_t0`, `util_slope`, `util_accel` | means; OLS slope over W12; mean second difference |
| `cash_adv_ramp` | `(CA count in H2 + 1) / (monthly-avg CA count in H1 + 1)`; plus `cash_adv_amt_share_h2` = CA amount / total spend in H2 |
| `spend_taper_ratio` | monthly-avg spend H2 / monthly-avg spend H1 (low = cliff, ~1 = no taper) |
| `spend_cliff_flag` | last full pre-T0 month spend < 0.2 × H1 avg AND the month before ≥ 0.8 × H1 avg |
| `spend_active_days_share_h2` | active spend days / calendar days in H2 |
| `txn_cnt_slope` | OLS slope of monthly transaction counts |

### 3.3 Departure / travel signature

| Feature | Definition |
|---|---|
| `travel_mcc_flag_90` | any airline/travel-agency MCC (4511, 4722, 3000–3299) in [T0−90d, T0] |
| `foreign_txn_share_h2` | share of H2 transactions with non-domestic country code |
| `last_txn_foreign_flag` | last pre-T0 transaction carries a foreign country code |
| `casa_inflow_stop_gap_d` [COND: CASA] | days between last salary-like inflow and T0 |
| `eosb_like_flag` [COND: CASA] | single inflow > 3× median monthly salary inflow within [T0−180d, T0], followed by inflow stop |

### 3.4 History shape and cross-product

| Feature | Definition |
|---|---|
| `fee_velocity_life`, `fee_velocity_ratio_h2` | lifetime fees / tenure months; H2 monthly fee rate / lifetime rate |
| `tenure_at_t0_m`, `prior_spell_cnt_24m`, `months_since_prior_spell` | from the spell table (§2) |
| `roll_speed_30_d`, `roll_speed_60_d` | days T0 → first DPD ≥ 30 / ≥ 60 (from the spell table §2; past events at obs for this population) |
| `cross_prod_t0_gap_d` [COND: RL] | \|T0_card − T0_other\| where both products delinquent |
| `simultaneous_default_flag` [COND: RL] | above gap ≤ 35d |
| `aecb_leverage_slope` [COND: O7] | OLS slope of bureau total obligations over pulls in [T0−24m, T0]; NULL if < 2 pre-T0 pulls |
| `relationship_breadth` | count of product types held with us (ALWAYS computed — confound control, `01 §4`) |

### 3.5 Deterioration class v1 (rules)

Evaluate in order; first match wins; `det_class_confidence` = matched conditions /
listed conditions. Thresholds τ are placeholders — tune on T05-available data and log.

| Class | Conditions |
|---|---|
| `abrupt_shock` | `spend_cliff_flag` AND `pay_ratio_mean_h1 ≥ 0.8` AND payments ≈ 0 in last 2 pre-T0 months AND \|util_slope over H1\| < τ_u |
| `gradual_spiral` | `util_slope > τ_u` AND `pay_ratio_slope < −τ_p` AND `cash_adv_ramp > 1.5` |
| `chronic_marginal` | `min_pay_share_w12 ≥ 0.6` AND `fee_velocity_life` in top tercile AND `util_mean_h1 ≥ 0.8` |
| `mixed` | otherwise |

Validation (T17/T18): within each segment, realised recovery/cure by class must
separate (extreme-class ratio ≥ 1.5×). Report class shares + separation in
`RESULTS.md`. If `mixed` > ~50%, iterate thresholds before shipping.

Output schema: `(contract_id, spell_id, t0, <features>, det_class_v1,
det_class_confidence, computed_at)`.

## 4. A2 — locatability states

States: `reachable | avoiding | skip | gone`. All gap features measured at `obs`.

### 4.1 Signals

| Tag | Feature | Definition |
|---|---|---|
| [CORE] | `last_card_txn_gap_d`, `last_payment_gap_d`, `last_digital_login_gap_d`, `last_casa_activity_gap_d` [COND] | `obs` − last activity date per channel |
| [CORE] | `channel_death_std_d` | std across the available gap set — small = all channels died together (departure signature); large = staggered (distress) |
| [CORE] | `post_t0_domestic_txn_flag` | any domestic-country activity after T0+60d ⇒ in-country |
| [CORE] | `travel_mcc_flag_90`, `last_txn_foreign_flag`, `foreign_login_flag` [COND: digital geo] | from A4 §3.3 / digital |
| [CORE] | `other_product_active_flag` [COND: RL/CASA] | any activity on other products in last 90d |
| [DCORE, gate T10] | `sms_delivered_rate`, `call_connect_rate`, `delivered_unanswered_ratio`, `wrong_number_flag`, `last_rpc_gap_d` | delivery/disposition-based; delivered-but-unanswered separates `avoiding` from `skip` |

### 4.2 Labels (v2 supervised)

Ground truth = field-visit dispositions (DCORE; O10). Mapping table to fill:

| Disposition code (`<<FILL-IN>>`) | Label |
|---|---|
| premises vacant / relocated abroad / person unknown | `gone` |
| relocated locally / address stale, in-country evidence | `skip` |
| confirmed residing + persistent no-answer | `avoiding` |
| met customer / right-party contact | `reachable` |

Train multiclass LightGBM on visited accounts; apply to all; report held-out
confusion matrix per state. `observed|inferred`: `observed` only for accounts with a
recent field-visit or right-party-contact fact; else `inferred`.

### 4.3 v1 rules (ships even if DCORE fails)

- `gone`: all [CORE] gaps > 90d AND `channel_death_std_d` small AND
  (`travel_mcc_flag_90` OR `last_txn_foreign_flag` OR `foreign_login_flag`) AND NOT
  `post_t0_domestic_txn_flag`
- `avoiding`: (digital activity OR domestic txn activity recent) AND no payment —
  with DCORE: delivered/ringing evidence AND no right-party contact
- `skip`: in-country evidence (`post_t0_domestic_txn_flag` OR `other_product_active_flag`)
  AND dead contact channels — with DCORE: disconnected/wrong-number codes
- `reachable`: recent right-party contact or inbound contact [DCORE]; without DCORE,
  assign only via v2 labels or leave `unknown`

Without DCORE this degrades to 3 reliable states (`gone / active-but-not-paying /
unknown`) — say so in outputs rather than faking 4.

## 5. Cross-cutting implementation notes

- **Separate pipelines per source system** (R3/S15): CC and loan accounts have
  different structures. Build CC first; port to loans once the CC axes clear Phase P.
  Shared output schemas so downstream code is source-agnostic.
- Join keys: account-level features on `account_id`; client-level (cross-product,
  CASA) via CIF then broadcast to accounts. Follow existing feature-layer patterns.
- Every new feature table: partition/layout consistent with existing feature layer;
  add a null-rate + coverage report per segment as part of the pipeline, not ad hoc.
- Every pipeline inherits the repo's existing leakage discipline (R2 — already in place
  across the current modelling spectrum) and adds T0-boundary assertions for A4, plus
  the invariant tests in §2. Test data pattern: follow existing repo conventions.

## 6. Account succession linkage (T03/T04)

**Problem.** A restructure closes the account and opens a replacement; no link between
them is currently known (O13). Needed for correct labels (§1), A4 coverage of
restructured customers (§2.5), and as a willingness signal (`01 §4`).

**Step 1 — size it before solving it.** Count closures whose pattern suggests a
restructure (closure with outstanding balance, followed by a new same-CIF account within
a short window). If the share of the book is trivial, cap effort here, record the blind
spot with its size in `RESULTS.md`, and move on.

**Step 2 — look for an explicit link first.** Any of: a reference/parent-account field
on the new account; a closure reason code naming restructure; a DCORE restructure event
recording both account numbers. If one exists, T04 is unnecessary — it is a lookup, not a modelling task.

**Step 3 — heuristic record linkage, only if no explicit link exists.** Candidate pairs
= same CIF, `open_date(new) - close_date(old)` within `<<window, default 0–45d>>`, same
account_type family. Score each pair on:
- balance correspondence: `|initial_principal(new) - closing_balance(old)|` relative to
  the closing balance (tightest single signal)
- date proximity
- product-transition plausibility
- presence of a restructure-flavoured posting or DCORE event near the closure

Resolve to at most one successor per predecessor (and vice versa) — greedy on score,
with a minimum threshold; leave ambiguous cases unlinked rather than guessing.

**Step 4 — validate.** If any subset carries an explicit link, use it as ground truth
and report precision/recall of the heuristic on held-out pairs. With no ground truth
available, hand-validate a sample and report agreement, clearly labelled as such.

**Output:** `(old_account_id, new_account_id, link_method, link_confidence,
close_date, open_date, balance_delta)`. Consumers must respect `link_confidence` —
label exclusion should be conservative (exclude on weak links too); A4 history
inheritance should be strict (inherit only on strong links).
