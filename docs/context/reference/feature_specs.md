# Label and Feature Specifications

Formula-level definitions for the label, spell and feature tasks. Conventions:
- `obs` = observation_date. All features use data `< obs` (R2). A4 additionally `≤ T0`.
- Field/table names are illustrative — resolve against the workplace repo's own docs
  and code, never guessed (R9).
- `CONFIRM` marks a default the user/business must ratify. `[COND: X]` marks a feature
  only computable where domain X exists; emit NULL + let `relationship_breadth` carry
  the coverage signal.
- **Window arithmetic is in months, not days** — see below. Day arithmetic appears only
  *inside* a window, for features that genuinely measure days.

## 0. Window arithmetic — months, matching the existing pipelines

**Window boundaries are month-based.** `M0 = month(T0)`; `W_pre = [M0−12, M0)` means the
**12 complete calendar months strictly before the onset month.** Three reasons, in order
of weight:

1. **T0 is month-resolved** (§2 derives it from the bucket string). `T0 − 365d` is false
   precision on a value that is only accurate to a month.
2. **The features are monthly series.** A boundary landing mid-month leaves the first and
   last buckets partial, which biases every mean and every OLS slope — the quantities A4
   is built on.
3. **It matches the existing pipelines**, which use `F.add_months` / `F.months_between`.

```python
w_pre_start = F.add_months(F.trunc(F.col("t0"), "month"), -12)   # boundaries
month_idx   = F.floor(F.months_between(F.trunc(c, "month"), w_pre_start))
```

⚠ **`F.months_between` returns a fractional double** (and special-cases end-of-month
pairs). For a month *index*, truncate both sides to month start and floor — or diff a
`yyyyMM` key. Comparing raw `months_between` output against an integer is a silent bug.

**The onset month `M0` is excluded from `W_pre`.** The miss happens inside it, so it is
not a pre-delinquency month; keeping it would also make the last bucket partial in a
different way for every account. Where onset-month behaviour is wanted, take it as its
own named feature, not as the tail of `W_pre`.

**Days still belong inside a window.** Anything measuring an actual elapsed interval or
a calendar position stays in days, computed from event timestamps: `pay_dom_*`,
`pay_gap_max_d`, `pay_gap_last_d`, `casa_inflow_stop_gap_d`, `t0_to_block_days`,
`days_to_dpd30/60`. The rule is: **month arithmetic decides which rows are in the
window; day arithmetic measures what happened within it.**

## 1. Labels

Payment definition (shared): `payments(a, t1, t2]` = sum of customer-initiated credits
to the account in `(t1, t2]`, excluding fee/interest postings, reversals, internal
adjustments, **and restructure/succession postings** (R13). Exact posting-type codes:
`<<FILL-IN>>`.

**⚠ Succession exclusion is not optional.** A restructure closes the account and opens a
replacement; if the closing credit is not excluded, a restructure reads as full recovery
and the label is inverted (debt moved, not repaid). Until T18/T19 identifies successions
reliably, exclude via closure-posting type and flag affected accounts. Emit
`succession_excluded_flag` on every label row so contamination is measurable.

| Label | Definition | Params (defaults) |
|---|---|---|
| `futility_60_180` | 1 if `payments(obs, obs+N] <= ε` else 0 | N = 3 months CONFIRM (O4); ε = min(100 AED, 0.5% × outstanding_at_obs) CONFIRM (O5) |
| `recovery_aed_60_180` | `payments(obs, obs+N]` (continuous) | same N |
| `any_recovery_180p` | 1 if `payments(obs, obs+6m] > floor` | floor = 100 AED CONFIRM — a noise floor, not a business threshold |
| `recovery_amount_180p` | `payments(obs, obs+6m]`, modelled only where `any_recovery_180p = 1` (hurdle part 2) | |
| Legacy (reports only, R11) | roll label; 5%/1000 AED label | unchanged |

Restructure handling (R13, from T17/T18): add `restructured_in_horizon` flag. Default =
exclude restructured rows from futility *training*, keep them in reporting, and never
score a restructure as recovery. CONFIRM once O14 clarifies where the successor account
starts.

Leakage tests to implement: labels read only `(obs, obs+N]`; features only `< obs`;
assert in pipeline tests, not comments.

## 2. Spell / T0 table

Output grain: `(account_id, spell_id)`. **Inputs differ by unit (R15) — two derivation
paths:**

**CC — use the existing 24-month DPD bucket history feature.** It stores a per-month
bucket string (e.g. `33321000000000…`). This makes CC spell derivation nearly free —
reuse it rather than reconstructing from raw DPD (R14). Confirm before use: string
orientation (most-recent-first or last?) and the as-of reference month.

### ⚠ The bucket code is offset on CC — "non-zero" is NOT delinquent

Confirmed with the user 2026-08-19. **The same code means different things per unit:**

| Code | CC | Retail loan |
|---|---|---|
| `0` | nothing due | nothing due (**not differentiated from `1`, or `1` unused**) |
| `1` | **due but not overdue** — ordinary revolver behaviour, recurs every cycle | **already 0–30 DPD** |
| `2` | **0–30 DPD — delinquency starts here** | 31–60 DPD |
| `n` | `(n−2)×30` to `(n−1)×30` DPD | `(n−1)×30` to `n×30` DPD |

So define the threshold per unit and reference it everywhere — never `> 0`:

- **CC: `DELINQ_MIN = 2`.** Spell starts at the first month with code **≥ 2**; cure is a
  return to code **≤ 1** — *not* to `0`, because an account sitting at `1` is current
  with a statement due.
- **Retail loan: `DELINQ_MIN = 1`.** Spell starts at code ≥ 1; cure is a return to `0`.

**Using `> 0` on CC is a defect with a specific fingerprint:** a revolver who always
carries a statement balance never returns to `0`, so the string reads as permanently
non-zero — producing one enormous spell with T0 at the customer's first-ever statement,
and a spuriously high `t0_censored_flag` spread across *all* cohorts instead of
concentrating in 180+ >2y. If a run shows that pattern, this is why (see T03b).

**Segment filters inherit the offset too.** "60+ DPD" is code ≥ 4 on CC but code ≥ 3 on
loans. Any snippet that scopes by bucket code must use the per-unit mapping, never a
shared constant (R20 — the wrong constant silently selects the wrong population).

**Free signal from the `0`/`1` distinction (CC only).** Because `1` means "statement
due", the pre-T0 mix of `0` and `1` months separates transactor/inactive from revolver
at no cost: `months_at_code0_w12` (nothing due — dormant or paid before statement) and
`revolver_share_w12` (share of clean months at code `1`). CONFIRM the exact semantics of
"nothing due" before shipping these.

Two limitations to handle explicitly:
- **24-month horizon.** A spell starting more than 24 months ago is unlocatable — the
  string never drops below `DELINQ_MIN` and T0 falls outside it. This affects the 180+ >2y cohort
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
2. A spell starts at the first period with `code >= DELINQ_MIN` following a period
   below it (or account origin). `T0` = that period's date. **`DELINQ_MIN` is 2 for CC,
   1 for loans** — never `> 0`.
3. A spell ends at the first later snapshot with `code < DELINQ_MIN` (cure) or at
   write-off/closure (terminal) or remains open.
4. **Restructures (R13) — succession, not reset.** The old account closes and a new one
   opens, so the old account's spell simply *ends at closure* (`spell_end_reason =
   'restructure_closure'` where identifiable). The successor account starts its own
   spell history, beginning at DPD 0, lower, or the same bucket — not uniform (O14).
   Do **not** bridge DPD resets within an account; that mechanic does not exist here.
5. **Inherited history.** Where T18/T19 supplies a link, the successor row carries
   `predecessor_account_id` and `inherited_history_flag = 1`, and A4 windows may be
   extended back through the predecessor's timeline (its own T0 becomes the effective
   anchor). Without a link the successor is a known A4 blind spot — set
   `inherited_history_flag = 0` and let coverage reporting show it.
6. `current_spell(obs)` = the spell containing `obs`. Every A4 feature row is keyed by
   `(account_id, spell_id)` and joined to observations via `current_spell`.

Columns: `account_id, account_type, spell_id, t0, spell_end, spell_end_reason,
prior_spell_end, predecessor_account_id, inherited_history_flag, max_dpd_so_far,
days_to_dpd30, days_to_dpd60` (the last two: within-spell, NULL until reached; safe at
obs because obs is inside the spell and those events precede it for the 60+/180+
populations). `prior_spell_end` carries the previous spell's cure date — NULL for a
first spell — because the A4 window is truncated at it (§3.0).

Built separately per source system (R3/S15): CC and loan accounts have different
structures, so this is two pipelines sharing one output schema.

Invariant tests: spells per account non-overlapping; `t0 <= obs <= spell_end` for every
joined observation; `code < DELINQ_MIN` outside spells (**≤ 1 on CC, 0 on loans** — not
`= 0`); no spell bridges an account closure; where
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
(T21).

**Consequence for T01/T04/T05:** existing block-anchored outflow features are the
principal **ADAPT** case — re-anchor to T0 for A4, and retain the block-anchored
originals as `W_early` features rather than rebuilding either.

### 3.0b `W_pre` is truncated, not assumed — three cut points

A nominal 12 months before T0 is often not 12 months of *pre-delinquency*. Truncate at
the latest of three boundaries (user-ratified 2026-08-19):

```
M0          = month(T0)                       # onset month, excluded from W_pre
w_pre_start = max(M0 − 12,
                  month_after(prior_spell_end),   # cure month is partly delinquent
                  month(account_open_date),
                  retention_floor_month)       # all month-aligned (§0)
w_pre_clean_m = months_between(M0, w_pre_start)   # integer by construction
```

| Cut | Why it matters |
|---|---|
| `prior_spell_end` | **The one that bites.** For a repeat delinquent, `[T0−12m, T0)` overlaps their *previous* spell — so "pre-delinquency behaviour" is really post-cure behaviour from an earlier episode, possibly while blocked. Two identical feature vectors would then mean different things. |
| `account_open_date` | Short-tenure accounts have no 12-month run-up. Early-default is a distinct population, not a missing-data case — read with `tenure_at_t0_m`. |
| `retention_floor` | Transaction history does not reach back far enough (T02). Note `W_pre` starts at `T0−12m` and T0 is *itself* months before `obs`, so a 180+ account needs data from roughly `obs−18m` to `obs−30m` — much deeper than 12 months from today. |

**Emit on every A4 row, always:** `w_pre_start`, `w_pre_clean_m` (months actually
available), `w_pre_contaminated_flag` (1 where any cut bit), and
`w_pre_truncation_reason` ∈ `none | prior_spell | tenure | retention`. Truncation that
is not visible downstream gets read as data-quality noise.

**Slopes count clean months only.** The ≥ 4-non-null-month rule below applies to months
inside `w_pre_start`, not to the nominal 12 — a slope fitted across a prior spell
boundary measures the boundary, not the deterioration.

### 3.1 onwards — feature definitions (all on `W_pre` unless stated)

Windows — **month-aligned (§0)**, per T02 availability and §3.0b truncation.
`M0 = month(T0)`, excluded:

| Window | Months | Was (do not use) |
|---|---|---|
| `W12 = W_pre` | `[w_pre_start, M0)` — nominally 12 | `[T0−365d, T0)` |
| `H1` | `[w_pre_start, M0−3)` — nominally 9 | `[T0−365d, T0−90d)` |
| `H2` | `[M0−3, M0)` — 3 | `[T0−90d, T0)` |

Monthly series over W12: payments `P_m`, amount due `D_m`, utilisation `U_m`, spend
`S_m`, cash advances `CA_m`, fees `F_m`. Slopes = OLS over month index (from
`months_between` on month-truncated dates — see the §0 warning); require ≥ 4 non-null
**clean** months else NULL. Where truncation leaves fewer than 3 months, `H1` is empty
and every `_h1`/ratio feature is NULL — emit rather than defaulting to zero.

**On the residual anchor lag.** With `DELINQ_MIN = 2` (§2), CC T0 is the month the
payment went *overdue* — so the first missed due date sits inside that same month and
the old "T0 is a cycle or two late" concern largely dissolves. What remains is that the
unpaid statement covers the *prior* cycle's spend, so the final ~30 days of `W_pre`
carry the run-up to the miss. That is wanted here (A4 is descriptive, and the label
looks forward from `obs`, so there is no R2 exposure) — but do not describe these as
strictly pre-hardship features. Day-level refinement via the due date is optional (§2).

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

> **Reuse before you derive any of these (R14, T06).** Departure/travel features already
> exist in the working repo's feature layer and in the sibling repos
> `wealth_management` and `retail.feature_space`. The definitions below are the
> **gap fill** — what to build when the search turns up nothing usable, or when a
> borrowed feature fails the coverage / T0-anchoring / protected-input screen. Deriving
> them from transaction history while a maintained version exists creates a second
> version of the same number.

| Feature | Definition |
|---|---|
| `travel_mcc_flag_h2` | any airline/travel-agency MCC (4511, 4722, 3000–3299) in `H2` = `[M0−3, M0)` (renamed from `travel_mcc_flag_90` — the window is 3 months, not 90 days) |
| `foreign_txn_share_h2` | share of H2 transactions with non-domestic country code |
| `last_txn_foreign_flag` | last pre-T0 transaction carries a foreign country code |
| `casa_inflow_stop_gap_d` [COND: CASA] | days between last salary-like inflow and T0 |
| `eosb_like_flag` [COND: CASA] | single inflow > 3× median monthly salary inflow within `[M0−6, M0)`, followed by inflow stop |

### 3.4 History shape and cross-product

| Feature | Definition |
|---|---|
| `fee_velocity_life`, `fee_velocity_ratio_h2` | lifetime fees / tenure months; H2 monthly fee rate / lifetime rate |
| `tenure_at_t0_m`, `prior_spell_cnt_24m`, `months_since_prior_spell` | from the spell table (§2) |
| `roll_speed_30_d`, `roll_speed_60_d` | days T0 → first DPD ≥ 30 / ≥ 60 (from the spell table §2; past events at obs for this population) |
| `cross_prod_t0_gap_d` [COND: RL] | \|T0_card − T0_other\| where both products delinquent |
| `simultaneous_default_flag` [COND: RL] | above gap ≤ 35d |
| `aecb_leverage_slope` [COND: O7] | OLS slope of bureau total obligations over pulls in `[M0−24, M0)`; NULL if < 2 pre-T0 pulls |
| `relationship_breadth` | count of product types held with us (ALWAYS computed — confound control, `01 §4`) |

### 3.5 Deterioration class v1 (rules)

Evaluate in order; first match wins; `det_class_confidence` = matched conditions /
listed conditions. Thresholds τ are placeholders — tune on T02-available data and log.

| Class | Conditions |
|---|---|
| `abrupt_shock` | `spend_cliff_flag` AND `pay_ratio_mean_h1 ≥ 0.8` AND payments ≈ 0 in last 2 pre-T0 months AND \|util_slope over H1\| < τ_u |
| `gradual_spiral` | `util_slope > τ_u` AND `pay_ratio_slope < −τ_p` AND `cash_adv_ramp > 1.5` |
| `chronic_marginal` | `min_pay_share_w12 ≥ 0.6` AND `fee_velocity_life` in top tercile AND `util_mean_h1 ≥ 0.8` |
| `mixed` | otherwise |

Validation (T07/T08): within each segment, realised recovery/cure by class must
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
| [DCORE, gate T11] | `sms_delivered_rate`, `call_connect_rate`, `delivered_unanswered_ratio`, `wrong_number_flag`, `last_rpc_gap_d` | delivery/disposition-based; delivered-but-unanswered separates `avoiding` from `skip` |

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

## 6. Account succession linkage (T18/T19)

**Problem.** A restructure closes the account and opens a replacement; no link between
them is currently known (O13). Needed for correct labels (§1), A4 coverage of
restructured customers (§2.5), and as a willingness signal (`01 §4`).

**Step 1 — size it before solving it.** Count closures whose pattern suggests a
restructure (closure with outstanding balance, followed by a new same-CIF account within
a short window). If the share of the book is trivial, cap effort here, record the blind
spot with its size in `RESULTS.md`, and move on.

**Step 2 — look for an explicit link first.** Any of: a reference/parent-account field
on the new account; a closure reason code naming restructure; a DCORE restructure event
recording both account numbers. If one exists, T19 is unnecessary — it is a lookup, not a modelling task.

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
