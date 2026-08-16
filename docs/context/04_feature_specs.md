# Label and Feature Specifications

Formula-level definitions for W1–W4. Conventions:
- `obs` = observation_date. All features use data `< obs` (R2). A4 additionally `≤ T0`.
- Field/table names are illustrative — resolve against the Asset Map (R9).
- `CONFIRM` marks a default the user/business must ratify. `[COND: X]` marks a feature
  only computable where domain X exists; emit NULL + let `relationship_breadth` carry
  the coverage signal.

## 1. Labels (W1)

Payment definition (shared): `payments(a, t1, t2]` = sum of customer-initiated credits
to the account in `(t1, t2]`, excluding fee/interest postings, reversals, and internal
adjustments. Exact posting-type codes: `<<FILL-IN>>`.

| Label | Definition | Params (defaults) |
|---|---|---|
| `futility_60_180` | 1 if `payments(obs, obs+N] <= ε` else 0 | N = 3 months CONFIRM (O4); ε = min(100 AED, 0.5% × outstanding_at_obs) CONFIRM (O5) |
| `recovery_aed_60_180` | `payments(obs, obs+N]` (continuous) | same N |
| `any_recovery_180p` | 1 if `payments(obs, obs+6m] > floor` | floor = 100 AED CONFIRM — a noise floor, not a business threshold |
| `recovery_amount_180p` | `payments(obs, obs+6m]`, modelled only where `any_recovery_180p = 1` (hurdle part 2) | |
| Legacy (reports only, R11) | roll label; 5%/1000 AED label | unchanged |

Re-aging (from D7/O6): if restructures reset DPD, add `reaged_in_horizon` flag; default
handling = exclude re-aged rows from futility training, keep in reporting. CONFIRM.

Leakage tests to implement: labels read only `(obs, obs+N]`; features only `< obs`;
assert in pipeline tests, not comments.

## 2. Spell / T0 table (W2)

Input: daily (or best-available) DPD history per contract. Output grain:
`(contract_id, spell_id)`.

Derivation:
1. Order DPD snapshots per contract by date.
2. A spell starts at the first snapshot with `DPD > 0` following a snapshot with
   `DPD = 0` (or account origin). `T0` = that snapshot's date.
3. A spell ends at the first later snapshot with `DPD = 0` (cure) or at
   write-off/closure (terminal) or remains open.
4. **Re-aging:** if D7 shows restructures reset DPD, a reset must NOT end a spell:
   join restructure events and bridge resets within `<<gap, default 35d>>` of a
   restructure into the same spell, setting `reaged_flag = 1`. CONFIRM rule with O6.
5. `current_spell(obs)` = the spell containing `obs`. Every A4 feature row is keyed by
   `(contract_id, spell_id)` and joined to observations via `current_spell`.

Columns: `contract_id, spell_id, t0, spell_end, spell_end_reason, reaged_flag,
max_dpd_so_far, days_to_dpd30, days_to_dpd60` (the last two: within-spell, NULL until
reached; safe at obs because obs is inside the spell and those events precede it for
the 60+/180+ populations).

Invariant tests: spells per contract non-overlapping; `t0 <= obs <= spell_end` for
every joined observation; DPD = 0 outside spells except bridged re-aged gaps.

## 3. A4 — manner-of-deterioration features (W3)

Windows (relative to T0, per D9 availability): `W12 = [T0−365d, T0)`,
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
| `tenure_at_t0_m`, `prior_spell_cnt_24m`, `months_since_prior_spell` | from W2 table |
| `roll_speed_30_d`, `roll_speed_60_d` | days T0 → first DPD ≥ 30 / ≥ 60 (from W2; past events at obs for this population) |
| `cross_prod_t0_gap_d` [COND: RL] | \|T0_card − T0_other\| where both products delinquent |
| `simultaneous_default_flag` [COND: RL] | above gap ≤ 35d |
| `aecb_leverage_slope` [COND: O7] | OLS slope of bureau total obligations over pulls in [T0−24m, T0]; NULL if < 2 pre-T0 pulls |
| `relationship_breadth` | count of product types held with us (ALWAYS computed — confound control, `01 §4`) |

### 3.5 Deterioration class v1 (rules)

Evaluate in order; first match wins; `det_class_confidence` = matched conditions /
listed conditions. Thresholds τ are placeholders — tune on D9-available data and log.

| Class | Conditions |
|---|---|
| `abrupt_shock` | `spend_cliff_flag` AND `pay_ratio_mean_h1 ≥ 0.8` AND payments ≈ 0 in last 2 pre-T0 months AND \|util_slope over H1\| < τ_u |
| `gradual_spiral` | `util_slope > τ_u` AND `pay_ratio_slope < −τ_p` AND `cash_adv_ramp > 1.5` |
| `chronic_marginal` | `min_pay_share_w12 ≥ 0.6` AND `fee_velocity_life` in top tercile AND `util_mean_h1 ≥ 0.8` |
| `mixed` | otherwise |

Validation (W3 DoD): within each segment, realised recovery/cure by class must
separate (extreme-class ratio ≥ 1.5×). Report class shares + separation in
`RESULTS.md`. If `mixed` > ~50%, iterate thresholds before shipping.

Output schema: `(contract_id, spell_id, t0, <features>, det_class_v1,
det_class_confidence, computed_at)`.

## 4. A2 — locatability states (W4)

States: `reachable | avoiding | skip | gone`. All gap features measured at `obs`.

### 4.1 Signals

| Tag | Feature | Definition |
|---|---|---|
| [CORE] | `last_card_txn_gap_d`, `last_payment_gap_d`, `last_digital_login_gap_d`, `last_casa_activity_gap_d` [COND] | `obs` − last activity date per channel |
| [CORE] | `channel_death_std_d` | std across the available gap set — small = all channels died together (departure signature); large = staggered (distress) |
| [CORE] | `post_t0_domestic_txn_flag` | any domestic-country activity after T0+60d ⇒ in-country |
| [CORE] | `travel_mcc_flag_90`, `last_txn_foreign_flag`, `foreign_login_flag` [COND: digital geo] | from A4 §3.3 / digital |
| [CORE] | `other_product_active_flag` [COND: RL/CASA] | any activity on other products in last 90d |
| [DCORE, gate D6] | `sms_delivered_rate`, `call_connect_rate`, `delivered_unanswered_ratio`, `wrong_number_flag`, `last_rpc_gap_d` | delivery/disposition-based; delivered-but-unanswered separates `avoiding` from `skip` |

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

- Join keys: contract-level features on `contract_id`; client-level (cross-product,
  CASA) via CIF then broadcast to contracts. Follow existing feature-layer patterns.
- Every new feature table: partition/layout consistent with existing feature layer;
  add a null-rate + coverage report per segment as part of the pipeline, not ad hoc.
- Every pipeline gets leakage tests (R2) and, where applicable, invariant tests
  (`04 §2`). Test data pattern: follow existing repo test conventions.
