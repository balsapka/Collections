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

**Loans — no equivalent *24-month history feature* exists**, so the bucket series comes
from the snapshot table. Resolution is monthly by construction.

> ⚠ **UNVERIFIED — check before building any reconstruction (raised 2026-08-20).** The
> loan snapshot rows may carry a **days-overdue column**. If they do, the bucket series is
> *assembled* (order snapshots per account, read the column, map days → bucket), not
> *derived* — and the `arrears / emi` arithmetic below is unnecessary. This is a schema
> question: check the workplace repo's loan snapshot docs **in UAT first** (R9/R14), no
> PROD round trip needed to answer existence. Do not build the reconstruction until this
> is settled. Four things to establish, not just existence:
> 1. **Which DPD convention.** Days since the *oldest unpaid instalment's* due date
>    (climbs 30/60/90, maps to buckets — what we want) or days since the most recent
>    missed payment (resets each cycle — useless for bucketing, and would show a flat
>    series for a chronic non-payer).
> 2. **How partial payments are applied** — oldest-instalment-first (a partial payment
>    can cure the oldest instalment and drop DPD), pro-rata, or held in suspense. This
>    decides whether a chronic partial payer's DPD climbs, sawtooths or plateaus, and
>    that population is exactly `chronic_marginal`.
> 3. **DPD at snapshot date, or max DPD during the month?**
> 4. **Days → bucket boundary convention** — is 30 DPD bucket 1 or 2, `>` or `>=`? A raw
>    days column avoids the CC code-offset trap (§2 above) but needs its own mapping
>    stated explicitly.
>
> Also worth measuring: **snapshot history depth**. CC's 24-month string is a hard
> censoring limit (`t0_censored_flag`, and an independent reason not to score the 180+
> >2y cohort). A snapshot *table* may retain further back — in which case loans have no
> such limit and are *better* than CC on this one dimension.

If no such column exists, buckets must be reconstructed from the full data model, which
is real work and part of the separate loan pipeline. Approximate months-in-arrears as
`arrears / emi` — and validate it specifically on partial payers, where it drifts from
calendar DPD (see the amendment log).

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
                  retention_floor_month[source])  # PER SOURCE TABLE — see below
w_pre_clean_m = months_between(M0, w_pre_start)   # integer by construction
```

⚠ **`retention_floor` is per source table, not one window-wide cut** (user-ratified
2026-08-20). CC balance, utilisation and payment data live in **dedicated tables**, not only
in transaction history — so a single transaction-derived floor would truncate feature
families that never depended on the transaction stream. Only §3.3 (departure — MCC, country
codes) genuinely needs transactions. Resolve the floor per family, and record which floor
applied in `w_pre_truncation_reason`.

| Cut | Why it matters |
|---|---|
| `prior_spell_end` | **The one that bites.** For a repeat delinquent, `[T0−12m, T0)` overlaps their *previous* spell — so "pre-delinquency behaviour" is really post-cure behaviour from an earlier episode, possibly while blocked. Two identical feature vectors would then mean different things. |
| `account_open_date` | Short-tenure accounts have no 12-month run-up. Early-default is a distinct population, not a missing-data case — read with `tenure_at_t0_m`. |
| `retention_floor` | The **source table for that feature family** does not reach back far enough (T02). Payment/balance/utilisation tables and transaction history retain independently — ask T02 the question of each, and apply the answer per family, not once globally. Note `W_pre` starts at `T0−12m` and T0 is *itself* months before `obs`, so a 180+ account needs data from roughly `obs−18m` to `obs−30m` — much deeper than 12 months from today. |

**Emit on every A4 row, always:** `w_pre_start`, `w_pre_clean_m` (months actually
available), `w_pre_contaminated_flag` (1 where any cut bit), and
`w_pre_truncation_reason` ∈ `none | prior_spell | tenure | retention`. Truncation that
is not visible downstream gets read as data-quality noise.

**Slopes count clean months only.** The ≥ 4-non-null-month rule below applies to months
inside `w_pre_start`, not to the nominal 12 — a slope fitted across a prior spell
boundary measures the boundary, not the deterioration.

### 3.0c Windows and monthly series — applies to §3.1–§3.4

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
| `abrupt_shock` | `spend_cliff_flag` AND `pay_ratio_mean_h1 ≥ 0.8` AND payments ≈ 0 in last 2 pre-T0 months AND \|util_slope over H1\| < τ_u **AND NOT dormant** (see ⚠ below) |
| `gradual_spiral` | `util_slope > τ_u` AND `pay_ratio_slope < −τ_p` AND `cash_adv_ramp > 1.5` |
| `chronic_marginal` | `min_pay_share_w12 ≥ 0.6` AND `fee_velocity_life` in top tercile AND `util_mean_h1 ≥ 0.8` **AND a duration condition** (see ⚠ below) AND `w_pre_clean_m ≥ τ_m` |
| `mixed` | otherwise |

### ⚠ Two conditions that do not yet establish what their class names claim

**`chronic_marginal` asserts duration it cannot see.** `min_pay_share_w12` spans the
~12-month window and `util_mean_h1` is narrower still; only `fee_velocity_life` is
lifetime. Under §3.0b truncation the window can be a handful of months, so "chronic" can
rest on very thin evidence.

The consequence is a **systematic confusion with `gradual_spiral`**: a spiral that plateaued
at the limit *before* `W_pre` opened shows flat high utilisation with minimum payments,
fails `gradual_spiral`'s rising-`util_slope` condition, falls through the ordered rules and
lands in `chronic_marginal`. Which class an account receives then depends on **when the
spiral started relative to our window** — an artefact of the anchor, not a property of the
customer. That is precisely the boundary carrying the action difference (long-run revolver =
structured arrangement; plateaued spiral = insolvent, settlement).

Fix: recruit the duration features **already computed in §3.4 and currently unused here** —
`prior_spell_cnt_24m`, `months_since_prior_spell`, `tenure_at_t0_m` — as an explicit
condition, and require a minimum clean window `w_pre_clean_m ≥ τ_m` (τ_m placeholder,
CONFIRM). **Honest ceiling:** CC prior-spell history is capped at 24 months by the DPD
string, so the class can only ever mean *sustained across up to two years, plus lifetime
tenure and fee rate* — never "years of minimum payments". If the rule cannot carry that
meaning, rename the class rather than keep the claim.

**`abrupt_shock`'s zero-payment condition may be firing on dormancy.** With
`DELINQ_MIN = 2` (§2), T0 is the *first* overdue month — so if payments genuinely stopped
two months earlier, T0 should have been earlier too. The condition is therefore either
redundant, or it fires on accounts where **nothing was due** (paid-ahead or dormant), which
is a different customer from one whose income stopped. §2 already exposes the signal to
separate them (`months_at_code0_w12`, from the code-`0`/code-`1` distinction) and this rule
does not use it. **Cross-tab `abrupt_shock` against `months_at_code0_w12` at T07**; if the
class is enriched for code-`0` months, the not-dormant guard is required, not optional.

### Validation

- **Outcome separation (T07/T08):** within each segment, realised recovery/cure by class must
  separate (extreme-class ratio ≥ 1.5×). Report class shares + separation in `RESULTS.md`.
  If `mixed` > ~50%, iterate thresholds before shipping.
- **Face validity (T07) — distinct from the above.** Do the classes mean what their *names*
  claim? `abrupt_shock` should show low prior spells and longer clean `tenure_at_t0_m`;
  `gradual_spiral` rising `fee_velocity_ratio_h2`; `chronic_marginal` high
  `prior_spell_cnt_24m`. A class can separate outcomes perfectly while being misnamed —
  and the gates will not catch it (`personas.md §5`).

### Output schema and provenance

`(contract_id, spell_id, t0, <features>, det_class_v1, det_class_confidence,
w_pre_clean_m, w_pre_contaminated_flag, computed_at)`.

**The label does not travel alone.** If `det_class_v1` reaches the DCORE screen or any
agent-facing surface, `det_class_confidence` and the `observed|inferred` flag (R6/S8) travel
with it. The class names are *legible* — `abrupt_shock` describes a trajectory shape, not a
diagnosed cause — and an agent reading one as "this customer lost their job" carries an
unearned assumption into a live negotiation (`personas.md §5`).

## 4. A2 — locatability states

States: `reachable | avoiding | skip | gone | unknown`. All gap features measured at `obs`.
Plain-language definitions and the action mapping are in `personas.md §4` — read that first
if you are not sure what `skip` means.

### 4.0 Derivation principle — two streams, crossed

**A2 is derived, not learned** (revised 2026-08-20; supersedes the field-visit-supervised
design). Two independent evidence streams resolve the states between them:

- **Channel status** — what contact attempts came back with (§4.1b)
- **Presence evidence** — whether the customer is still visibly active anywhere (§4.1a)

| Attempt came back as | Presence evidence | No presence evidence |
|---|---|---|
| Right party answered | `reachable` | `reachable` — wherever they are, we have them |
| Rang, no answer | `avoiding` | **ambiguous** — departure signature decides, else `unknown` |
| Someone else answered | `skip` | `gone` on a departure trail, else `skip` |
| Number dead / no delivery | `skip` | `gone` on a departure trail, else `unknown` |

**Why not train on field-visit dispositions.** A visit is dispatched *because* calling
already failed, so a model trained on visited accounts learns
P(state | features, **already failed contact**) and cannot be pointed at the rest of the
book. `reachable` is near-absent from that sample — the state most needing a label source,
worst supplied by it. Field visits keep two jobs: **adjudicating the ambiguous cell**, and
**validating `gone` precision**, which is what protects the visit budget. Their coverage is
unverified and may be low; this design does not depend on it.

### 4.1 Signals

#### 4.1a Presence evidence [CORE — banking data, no DCORE dependency]

| Tag | Feature | Definition |
|---|---|---|
| [CORE] | `last_card_txn_gap_d`, `last_payment_gap_d`, `last_digital_login_gap_d`, `last_casa_activity_gap_d` [COND] | `obs` − last activity date per channel |
| [CORE] | `channel_death_std_d` | std across the available gap set — small = all channels died together (departure signature); large = staggered (distress) |
| [CORE] | `post_t0_domestic_txn_flag` | any domestic-country activity after T0+60d ⇒ in-country |
| [CORE] | `travel_mcc_flag_90`, `last_txn_foreign_flag`, `foreign_login_flag` [COND: digital geo] | from A4 §3.3 / digital |
| [CORE] | `other_product_active_flag` [COND: RL/CASA] | any activity on other products in last 90d |
| [CORE] | `observable_channel_cnt` | how many channels we can see at all. **Always computed** — the guard for §4.4a |

#### 4.1b Channel status [DCORE, gate T11]

The recorded contact-attempt vocabulary (user-confirmed 2026-08-20). Resolve the actual code
list before building — never guess (R9), and see the open question below.

| Outcome | Reads as | Contributes to |
|---|---|---|
| Right-party contact | Channel live **and** correct — a *positive observation* | `reachable` |
| Rang, no answer | Channel live, no pickup | `avoiding` / ambiguous |
| Answered, no meaningful conversation | **Ambiguous — see below** | `avoiding` or `skip` |
| Call did not go through | Channel dead (invalid / disconnected / unobtainable) | `skip` / `gone` |
| No reply to email; SMS undelivered | Channel-specific, weak alone | supporting |

⚠ **Open question (O15), and it decides how cleanly two states separate.** Does "answered
but no meaningful conversation" distinguish *the customer deflecting* from *a stranger on a
reassigned number*? If it is one undifferentiated code, that row collapses and `avoiding` /
`skip` both inherit the ambiguity. Establish this before T12, not after.

**All contact signals are attempt-normalised (§4.4b)** — rates over attempts made, never raw
flags:

| Feature | Definition |
|---|---|
| `contact_attempts_n` | attempts in the window. **Always emitted** — the exposure denominator |
| `connect_rate` | went-through / attempted |
| `pickup_rate` | answered / went-through |
| `rpc_rate` | right-party / answered |
| `last_rpc_gap_d` | `obs` − last right-party contact |
| `attempt_time_diversity` | spread of attempts across hour-of-day and day-of-week |
| `wrong_party_flag` | answered by someone who is not the customer (subject to O15) |

### 4.2 Derivation rules

Evaluate in order; first match wins; emit `a2_confidence` = matched conditions / listed.

- **`reachable`** — right-party contact within the labelling window (§4.4c), or recent
  inbound contact from the customer. **Directly observed, not inferred.** Needs no presence
  evidence: if the right party picks up, they are reachable wherever they are.
- **`gone`** — dead or wrong-party channels AND no presence evidence AND a **positive
  departure trail**: `travel_mcc_flag_90` OR `last_txn_foreign_flag` OR `foreign_login_flag`
  OR `casa_inflow_stop_gap_d` large. **Never assigned on absence alone** (§4.4a).
- **`skip`** — in-country evidence (`post_t0_domestic_txn_flag` OR
  `other_product_active_flag`) AND dead-or-wrong contact channels (`connect_rate` ≈ 0, or
  `wrong_party_flag`).
- **`avoiding`** — live channel with no pickup (`connect_rate` high, `pickup_rate` ≈ 0 or
  `rpc_rate` ≈ 0 across sufficient attempts) AND presence evidence.
- **`unknown`** — everything else, and mandatory where the §4.4 guards bite.

**Without trustworthy DCORE (T11 fails):** channel status is unavailable, so the axis
degrades to `gone` (departure trail + no presence) / `active-but-not-paying` / `unknown` —
three states. Say so in the output schema and documentation. Do not fabricate a fourth state
to make the grid look complete.

### 4.3 Supervised refinement (optional — scoped by coverage, not a prerequisite)

Where field-visit history is deep enough, a classifier can sharpen the **ambiguous cell
only** — the rang-no-answer / no-presence case where §4.2 falls to `unknown`.

- Ground truth = field-visit dispositions (O10). Mapping to fill from the actual code list:
  premises vacant / relocated abroad / person unknown → `gone`; relocated locally / address
  stale with in-country evidence → `skip`; confirmed residing + persistent no-answer →
  `avoiding`; met customer → `reachable`.
- **Train and apply on the same population.** Field visits are dispatched to the unreached,
  so a model trained on them may be applied *only* to the unreached — never to the book.
  State the population in the output.
- Report the held-out confusion matrix per state. `gone` precision is the number that
  matters: it protects the visit budget.
- Compare against §4.2's rules — where do they agree, where do they diverge? — so the rules
  improve even if the refinement does not ship.

Also worth reporting: how visited accounts differ from unvisited ones on observables. Even
within the unreached, dispatch is unlikely to be random (O16).

### 4.4 Guards — three ways this axis goes wrong

#### 4.4a Silence is not proof of departure

`gone` requires a **positive** departure trail, never mere absence. Roughly 80% of the
delinquent CC book is card-only (`domain_and_decisions §4`), and once the card is blocked
there may be no channel left to observe presence on at all. Silence then measures how little
we can see, not where the customer is — and it correlates with exactly the population the
axis exists to sort.

**Rule:** where `observable_channel_cnt` is below τ_c (CONFIRM) and there is no departure
trail, the state is `unknown`, not `gone`. Emit `observable_channel_cnt` on every row.

#### 4.4b Uncontacted is not unreachable

An account nobody called has no contact record, and a naive rule or model reads absence as
`gone` — the same conditional error as training on visited accounts only.

**Rule:** every contact signal is a rate over `contact_attempts_n`, never a raw flag; the
state is `unknown` below τ_a attempts (CONFIRM); and `attempt_time_diversity` is carried,
because someone only ever called at 10am on weekdays who never answers may simply be at work.

#### 4.4c The labelling window

Both a visit and a contact evidence the state **at the time they happened**, not at `obs`.
Set an explicit maximum gap between `obs` and the labelling event; rows outside it are
unusable, not stale-but-accepted. Default `<<FILL-IN — CONFIRM>>`. Undefined "recent"
silently mixes a state observed last week with one observed six months ago.

### 4.5 Where A2 stops

**Locatability ends the moment the right party picks up.** A customer who answers and then
says nothing useful is *reached* — the failure is willingness, not location, and it belongs
to A3. Assign `reachable` and route the deflection onward.

This boundary is load-bearing: it is exactly where UC1's transcript-derived features will
operate (`personas.md §6`), and blurring it now guarantees grid collinearity later (S7/T15).

### 4.6 Output schema

`(account_id, obs, a2_state_v1, a2_confidence, observed|inferred, contact_attempts_n,
observable_channel_cnt, label_event_gap_d, computed_at)`.

Provenance travels with the state, same discipline as A4 §3.5.

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
