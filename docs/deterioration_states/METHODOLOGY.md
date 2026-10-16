# Deterioration states — methodology

How a credit-card account in buckets 4–7 fell into delinquency, and what it is doing now,
read from its DPD bucket history only. One state per account, assigned by a short
decision tree. MECE by construction, simple enough to explain to the risk team in one
slide, and designed to stay out of the way of the other persona axes.

> **Status.** Designed and validated on calibrated **synthetic** data. Not yet run on the
> bank's book. Every number below marked *(synthetic)* is from simulation and is a
> *method check*, not a finding about the portfolio. The real-data run is
> `snippets/dpd_states_validate.py`; its expectations are in §8.

---

## 1. Where this sits among the persona axes

| Axis | Question it answers | Inputs |
|---|---|---|
| Locatability | Can we reach them? | Reachability flag, in-country flag |
| Ability | Can they pay? | Score: salary, inflow, CASA balance |
| Payment credibility | Do they pay and keep their word? | Score: promises kept (0–2), money coming in last 3 months (0–2), pre-delinquency history clean (0–1) |
| **Deterioration (this)** | **How did they fall in, and are they stabilized now?** | **DPD bucket history only** |

Design rules agreed with the business owner:

1. **MECE** — every account gets exactly one state; no "other" bucket.
2. **Simplicity beats precision** — a rule a collector can repeat beats a better-fitting
   one nobody can explain. Thresholds are round numbers.
3. **Orthogonal where possible** — the states must not rebuild the credibility or ability
   score. Known overlaps are named (§7), not hidden.
4. **5–6 states, at most 8**, each with a different action for the risk team.

---

## 2. Population and data conventions

- **Spine:** credit-card accounts whose **current** bucket is 4, 5, 6 or 7. Bucket 8+ is
  a separate category. Full history is available for every account.
- **The string:** one digit per month, **leftmost = current month**
  (`54320002000` → today 5, last month 4, …). Configurable if a source is reversed.
- **0 ≡ 1.** Bucket 1 (a few days late) is treated as normal.
- **Monthly movement `d` = bucket this month − bucket last month**, which reads as a payment:

  | d | Meaning | Months paid that month (= 1 − d) |
  |---|---|---|
  | +1 | roll — paid nothing (or less than one month's due) | 0 |
  | 0 at bucket ≥ 2 | **hold** — paid one month's due, stays in the same bucket | 1 |
  | −k | paid k + 1 months, moved back k buckets | k + 1 |
  | back to 0/1 | **cure** — common from 2–3, very rare from 4+ | — |

- **Spell:** a continuous run of months at bucket ≥ 2. The *current spell* is the one the
  account is in today.
- **Blip:** an earlier spell of 1–2 months that never passed bucket 2 (`0 0 2 0 0`).
  Blips do not count as earlier spells and do not end the clean history.
- **Billing-cycle jumps:** a +2 move next to a hold (`3 3 5` or `3 5 5`) is the reporting
  artefact of a straight roll and is repaired to `3 4 5`. Any other +2 is read as a roll.

---

## 3. Features used by the states

Only features that **do not drift with time since reaching 4** are used to assign states.
For most of the spine the current bucket is a clock (one bucket per month), so any
count over a fixed window, or any rate over the whole spell, changes with the bucket
rather than with behaviour.

| Feature | Definition | Fixed once past 4? |
|---|---|---|
| `months_before_spell` | months of history before the current spell started | yes |
| `n_blips` | earlier excursions of 1–2 months that never passed bucket 2 (EPD allows one) | yes |
| `n_prior_episodes` | earlier real (non-blip) spells (EPD requires none) | yes |
| `max_prior_bucket` | deepest bucket reached in any earlier (non-blip) spell; 0 if none (repeat delinquent) | yes |
| `runup_len` | months from the last clean month to the first month at bucket 4 (3 = straight 2→3→4) | yes |
| `runup_pays` | months on the way to 4 in which 2+ months were paid (moved back) | yes |
| `last6_in_band` | of the last 6 months (incl. today), how many were within today's bucket ±1 | no — current behaviour, by design |

Other features (`runup_holds`, `post4_paid_rate`, `max_hold_run`, …) are
computed for diagnostics and discovery only.

---

## 4. The states

Questions are asked **in order**; the first "yes" assigns the state.

```
Q1  Early payment default?  <= 3 months of history before this spell
                            (at most one blip inside it — a payoff from 2 — and no
                            earlier real spell) AND run-up to 4 took <= 3 months
                                                           -> early_payment_default
Q2  Stabilized?             >= 5 of the last 6 months within today's bucket ±1
                            OR (>= 6 months in buckets 4+ AND at most 1 bucket
                                higher than 6 months ago)  -> stabilized
Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3 and cured
                                                           -> repeat_delinquent
Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
      yes -> straight_roller  [B, C: >= 12 months of history before the spell
                               -> straight_roller_seasoned, else straight_roller_early_life]
      no  -> slow_roller      [C: paid 2+ months at once on the way down
                               -> slow_roller_erratic, else slow_roller_intermittent]
```

(Q3 "paying since bucket 4" was tested and rejected — §6.4.)

### Three options

| Option | States | Use when |
|---|---|---|
| **A — minimal (4)** | EPD, stabilized, straight roller, slow roller | Strict orthogonality: prior-spell history is left entirely to credibility |
| **B — balanced (6), recommended** | EPD, stabilized, repeat delinquent, seasoned straight roller, early-life straight roller, slow roller | Default. Matches the natural groups in the data (§6.1) and the 5–6 target |
| **C — detailed (7)** | B with slow roller split into intermittent payer / erratic payer | The risk team has a different action for each and both are ≥ 4% |

### What each state means and the action it points to

| State (display name · `code`) | Reads as | Action flavour | Share *(synthetic)* |
|---|---|---|---|
| **Early payment default (EPD)** · `early_payment_default` | At most 3 months of history (one blip allowed), rolled straight in, never really paid | Early-risk / first-party-fraud review, early legal; no restructuring | 6% (bank: 6%) |
| **Stabilized** · `stabilized` | Paying about one month's due each month for 5 of 6 months — or, after 6+ months in buckets 4+, still within one bucket of where it was 6 months ago (pays what is due on average, unevenly) | **Offer restructuring to break the hardship** | 8% (bank's rule alone: 7%; bank: 6%) |
| **Repeat delinquent (re-default)** · `repeat_delinquent` | Has been here before and cured from bucket 3 | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 16% |
| **Seasoned straight roller** · `straight_roller_seasoned` | At least a year on book (≥ 12 months clean), then rolled every month without paying | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 52% |
| **Early-life straight roller** · `straight_roller_early_life` | 4–11 months on book, then rolled every month without paying | Same triage; also an underwriting signal for acquisition | 3% — below the 5% floor in synthetic data; the real share decides (E16) |
| **Slow roller (partial payer)** · `slow_roller` | Paid something on the way down but kept rolling | Over-indebted: longer-tenor restructure or settlement | 16% |
| ↳ **Intermittent payer** *(C)* · `slow_roller_intermittent` | Paid one month here and there, never caught up | Chronic insufficiency: restructure to what they actually pay | 10% |
| ↳ **Erratic payer** *(C)* · `slow_roller_erratic` | Caught up 2+ months at once, then rolled again | Lumpy / irregular income: plan aligned to inflow timing | 6% |

In option A the two straight-roller states are one: **Straight roller** · `straight_roller`.

**Stabilized is the only state that moves month to month** — it describes what the
customer is doing now (*synthetic:* 62% are still stabilized next month). Every other
state is fixed once the account is past bucket 4 (*synthetic:* 97–100% keep their state
next month).

### 4.1 Names

The names use established card-risk and collections terms, and follow two rules:

1. **Describe behaviour, not intent.** These labels reach collector screens, audit trails
   and possibly complaint files. They say what the DPD history shows ("never really
   paid", "rolled every month", "paid one month at a time"), never why ("fraud",
   "won't pay"), which the history cannot prove.
2. **Code names are stable; display names are free.** Code uses short identifiers
   (`early_payment_default`, `straight_roller_seasoned`, …). `DISPLAY_NAMES` and `REMARKS`
   in `dpd_states/states.py` carry the business labels, so renaming for the risk team never
   breaks the pipeline or old results. Every report starts with the names table.

| Term | Where it comes from | Note |
|---|---|---|
| **Early payment default (EPD)** | Early-risk monitoring (FPD / SPD / TPD = first / second / third payment default; EPD = default early in the life of the account) | **Formerly "bust-out"** — the bank's internal name, kept in remarks. Classic *bust-out* fraud is different: a customer builds a good record and limit, maxes out (often with cash advances) and disappears. Its DPD history is clean-then-straight-roll, so it lands in **seasoned straight roller**; spotting it needs spend / utilisation spikes before delinquency — a fraud overlay, not this axis |
| **Stabilized** | The bank's own term; roll-rate "stay" behaviour | Industry has no single standard label for "pays enough to stay in the bucket" |
| **Repeat delinquent / re-default** | Collections recidivism; re-default rates after cure or restructure | |
| **Straight roller** | Core card-collections term: rolls through every bucket without a payment | |
| **Seasoned / early-life** | Seasoning and months on book (MOB); the first 12 months is the standard early-life window | |
| **Slow roller (partial payer)** | Roll-rate language: the counterpart of the straight roller | **Also called partial payer** — the more common collections term. The rejected Q3 state was renamed `paying_since_4` so "partial payer" means only this state |
| **Intermittent / erratic payer** | Collections payment-pattern labels | |

---

## 5. Thresholds and the evidence behind them *(synthetic sweeps)*

| Threshold (`parameter`) | Value | Why this value | What moving it does |
|---|---|---|---|
| EPD history (`epd_max_history`, `epd_max_blips`) | **≤ 3 months, at most one blip** | Business definition (agreed): a customer who never pays misses the first or second bill, so 2–3 clean months at most (`0 0 2 3 4`, `0 0 0 2 3 4`, `0 2 0 2 3 4`). No natural knee in the data | *Synthetic:* at 3 months 93% of the state is a planted early defaulter; at 6 months 79%, at 12 months 55% — longer histories are early-life defaults and land in early-life straight roller. Sweep reported in every run (2–12 months) |
| EPD earlier spells | **none; one blip allowed** | An early defaulter may pay off once, but only from bucket 2 (a blip) | `0 2 3 4 0 0 2 3 4 5 6` is therefore repeat delinquent, not EPD; two blips (`0 2 0 2 0 2 3 4`) is not EPD |
| Straight-roller run-up (`straight_max_runup`) | **≤ 3 months** | The one sharp threshold: any single paid month on the way down makes it a slow roller | ≤ 4 moves ~70% of genuine slow rollers into straight roller |
| Stabilized band (`stabilized_min_in_band`) | **5 of last 6 months within ±1** | The bank's existing stabilized rule, unchanged | 4 of 6: share ~14%, next-month roll ~46%, persistence ~63%. 6 of 6: ~5%, ~32%, ~80% |
| Stabilized long-run clause (`stabilized_long_run_months`, `stabilized_long_run_max_rise`) | **≥ 6 months in 4+, at most +1 bucket over 6 months** | Fixes the two edge cases in §6.15: oscillating payers and accounts that just paid down. Straight rollers cannot meet it (they leave the spine within ~4 months) | Adds ~1% of the spine to stabilized, which still rolls far less than the rest (~44% vs ~85% next month). +2 would take in slow drifters paying ~4 of 6 dues; `None` switches the clause off |
| Repeat-delinquent depth (`repeat_min_prior_peak`) | **earlier spell reached 3** | The bank counts ~85% single-spell; spells from 3 give 83% *(synthetic)* | From 2: 19%. From 4: 5% (cures from 4+ are rare) |
| Seasoned (`seasoned_min_months`) | **≥ 12 months** | Business definition (agreed): the first year on book is the standard early-life window. EPD already takes ≤ 3 months, so early life = 4–11 months | *Synthetic:* 12 m gives early life only 3.4% (below the 5% floor), 18 m 7%, 24 m 11%, 36 m 20% — but these shares come from the generator's assumed tenure distribution, so the real share decides (E16) |

**Rule order.** EPD is asked before stabilized (the bank's order). Only ~0.2% of the spine
is an early defaulter that is also stabilized today, so the order barely matters.

---

## 6. What was tried and dropped — and why

### 6.1 Unsupervised clustering as the source of states (k-means, GMM)

- **Whole spine, k-means:** very stable (bootstrap ARI 0.99) but only ARI 0.3–0.4 against
  the planted patterns and 0.1–0.3 against the rule states. It always merged holders with
  staircases and never isolated slow slides. **Stability does not mean validity** — on real
  data stability is the only check available, and it cannot detect merged behaviours.
- **GMM:** BIC never reached a minimum (kept improving to 12 components) because the
  features are spiky — 56–93% of accounts sit on a single value (run-up = 3, no earlier
  spell, …), and GMM fits narrow components to the spikes. Under 1% of accounts were
  ambiguous, so the soft-assignment advantage disappears. Best ARI vs planted 0.48 but
  stability fell to 0.67–0.93. Not used. GMM fits continuous inputs (ability scores,
  balances) far better than DPD-derived counts.
- **Residual clustering (after EPD and stabilized) — kept as a diagnostic.** k-means at
  k = 6 on the remaining ~88% found six clean, nameable groups: long-clean straight roll,
  short-clean straight roll, earlier spell to 3+, paying after 4 but still rolling, held on
  the way, paid 2+ on the way. With the final thresholds, agreement at k = 6 is A 0.11,
  **B 0.32, C 0.34** (best at k = 3: B 0.65 vs A 0.31) — the evidence that two residual
  states were too few. Every B/C split maps to one of these clusters with a one-line
  rule; the clusters themselves are not the states. The clusters split clean history
  near 36 months, but that reflects the generator's assumed tenure distribution; the
  seasoned cut is a business definition (12 months, §5).

### 6.2 A "mixed" / residual state
Dropped. An ordered tree with a default branch is MECE without one, and a residual
bucket invites "everything we don't understand" to grow.

### 6.3 Staircase (holds for months at each level, then steps up)
Merged. While it is holding a bucket it *is* stabilized (that is the actionable fact);
just after a step it reads as a slow roller. Telling a genuine holder from a staircase mid-hold needs more
than 6 months of history and an extra rule, and the next-month risk was the same
(*synthetic:* 0.28 vs 0.29). It separates only over 6 months (exit 33% vs 50%).

### 6.4 "Paying since bucket 4" — pays after reaching 4 but still rolling (Q3)
Tested at 0.34 / 0.5 / 0.67 months paid per month since 4. Rejected:
- barely separates risk (next-month roll ~80% vs ~86%);
- unstable — ~37% leave it every month — and it **drags the stability of the fixed
  states from ~98% to ~91%**, because accounts flip in and out of it;
- 79% of it is "paid in the last 3 months" — the credibility axis's 2-point component.

It is one of the six natural residual clusters, so it is real behaviour — but it belongs
to credibility, not here. The switch is kept in code (`paying_since_4_min_rate`, state `paying_since_4` — renamed
from "partial payer" so that term means only the slow roller) so the
test can be repeated (expectation E24).

### 6.5 Separate states for slow slide, dip-and-roll, volatile
Merged into slow roller (A, B) or split once by "paid 2+ months on the way" (C). The three
confuse each other in every view (shapes, clusters, trees), and the risk actions are close.
Much of "volatile" (cure then relapse) is a repeat delinquent by definition.

### 6.6 Repeat delinquent in option A
Left out of A on purpose. Repeat delinquent is built from earlier spells — the same history
credibility's 1-point "pre-delinquency clean" flag scores. In the self-test (with a clean
point defined as "no earlier spell") the states explained **84%** of that point's
variance. It is included in B/C because it is only 1 of credibility's 5 points and it
carries more than a yes/no: *cured from bucket 3 before* is evidence of catch-up capacity.
Expectation E19b measures the real overlap and decides A vs B.

### 6.7 "Stabilized or improving" clause (today's bucket ≤ 6 months ago)
Dropped. It changed **0.0%** of assignments. Straight / slow roller describe how the account fell
in, so an improving account carries no misleading label without it.

### 6.8 Payment-based refinement of stabilized
Tested: "≤ 1 roll in 6 months AND paid 2+ months at least once" separated holders from
staircases at 99% precision — but only because the synthetic generator built it that way,
and it leans on payment behaviour (credibility). Replaced by the bank's own 5-of-6 rule.

### 6.9 Features that drift with time since bucket 4
Dropped from assignment: whole-spell roll rate, fixed-window counts (rolls in the last 6
or 12 months), months paid since 4 as a count. Straight rollers at bucket 4 and 7 looked
different only because of the clock. Replaced by run-up features (fixed once past 4) and
rates within the current spell.

### 6.10 Shape table as the assignment
Kept for discovery and stakeholder examples only. ~5–6k distinct banded shapes; the top
30 cover ~35–40% of accounts — too fragmented to assign everyone.

### 6.11 n-gram ranking by planted-label purity
Fixed. The first version had a meaningless "lift" (per-account presence divided by
per-month code frequencies, rescaled by an arbitrary constant) and ranked by planted
labels that real data does not have. Lift is now measured against each account's own
codes in shuffled order: lift > 1 means the order of moves matters.

### 6.12 Treating +2 jumps as impossible
Replaced by repair (+2 next to a hold → straight roll) and "otherwise a roll". Real data
has billing-cycle effects (example: `…3 4 3 5 4…`).

### 6.13 Payment-promise or inflow inputs in any state
Never used — credibility and ability own them. Their overlap is *measured* (§7).

### 6.14 EPD ("bust-out") with up to 6 months of history
The first version allowed ≤ 6 months before the spell, chosen to match "a few months".
It made `0 0 0 0 0 0 2 3 4` a bust-out (now EPD) — but six clean months means about four bills were
paid (or nothing was due): an **early-life default**, not a customer who never paid. The
synthetic 6% match did not support 6 months either: the generator's bust-out volume had
been tuned to hit 6% *under that rule*, so the match was circular. Replaced by the agreed
business definition: **≤ 3 months, at most one blip**. Under it the generator still gives
5.8% EPD; every planted early defaulter is caught, and 93% of the state is a planted
early defaulter (79% under the old 6-month rule).

### 6.15 Stabilized measured only around today's bucket (edge cases)
The bank's rule — 5 of the last 6 months within ±1 of **today's** bucket — misreads two
uncommon but real histories (oldest → newest, today is the last digit):

- **Oscillating payer** `0000 0000 2344 4334 5433 4565 54` — swings between 3 and 6 for over
  a year, paying roughly what is due on average. The rule flipped it between stabilized and
  "straight roller" **5 times in 16 months**; every time it left the band it was called a
  straight roller, which it is not.
- **Just paid down** `… 3 4 5 6 6 5 4` — paid two months twice (6 → 5 → 4). The band around
  today's 4 excludes the two 6s, so the rule called it a straight roller *because* it paid.

Fix adopted: the **long-run clause** (§5). Both cases are now stabilized from their sixth
month at 4+ onwards; the only remaining dip is the single month at the top of a
3-month roll (3 → 4 → 5 → 6), which is a fair description of that month. Rejected
alternatives: allowing +2 over 6 months (takes in slow drifters), and a "sticky" rule
that remembers last month's state (harder to explain and audit).

Measured on synthetic data with oscillating payers added (1.2% of the spine): of the
accounts ever stabilized during the 6 backtest months, the share that **left and came
back** fell from ~8% (bank's rule) to ~5–7%, and oscillating payers bounced 41% less.
The rest are staircases (hold, step up, hold) and swingers in their first 6 months at 4.
Expectation E26 tracks this on real data. Both examples are permanent regression cases
in the self-test.

**Known limitation.** After an oscillating or stabilized account breaks out and rolls,
its fixed state comes from the original run-up (often "straight roller"). That is by
design — post-4 payment history belongs to credibility — but read "straight roller" as
*how they fell in*, not *never paid since*.

### 6.16 Seasoned / early-life split in option A
Not in A because, in synthetic data, it adds no risk separation (both ~94–95% exit within
6 months, by construction). It is in B/C for its action difference (life event vs
underwriting signal). Real outcomes decide whether it earns its place.

---

## 7. Overlap with the other axes (known and measured)

| Overlap | Size *(synthetic)* | Treatment |
|---|---|---|
| stabilized ↔ credibility "money coming in" (2 pts) | 100% of stabilized have money in; 44% of the rest do too | One-directional: stabilized is stricter (enough to hold the bucket, 6 months). Accept and state it. E21 |
| repeat delinquent ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.84 of the clean point explained by B states | Decides A vs B. E19b |
| straight / slow roller ↔ ability | none in synthetic (by construction) | Straight rolling may proxy income loss on real data — fine, but say so. E20 |
| any state ↔ locatability | none expected | E19/E20 report it |

---

## 8. Real-data validation

### How the backtest works from a single table
Today's string holds the past: dropping its newest *k* digits gives the string as it was
*k* months ago, and the dropped digits are what happened next. So one table of
latest-month strings gives the spine as of *k* months ago **and** its outcomes (next-month
roll, exit to 8+ within *k*, cure, next-month state). This needs the table to **keep
accounts that have since rolled to 8+ or closed** — a survivor-only table biases the
outcomes (the snippet detects and warns).

### Expectations (checked automatically — `dpd_states/expectations.py`)

| | Check | Expected | Basis |
|---|---|---|---|
| E01 | Exactly one state per account | True (FAIL otherwise) | Tree with default branch |
| E02 | Unparseable strings | ≤ 2% (FAIL) | CHAR_MAP / STRIP_CHARS set right |
| E03 | Backtest monthly roll rates vs 70/80/90/95% | ≤ 7pp off (FAIL) | Confirms orientation and reconstruction |
| E04 | Histories starting inside the spell | ≤ 10% | Full history exists |
| E05 | Unrepaired +2 jumps | ≤ 2% | Most jumps sit next to a hold |
| E06 | Bucket mix declines 4 → 7 | yes | Rising roll rates |
| E07 | One spell only (from bucket 3) | 78–92% | Bank ~85% |
| E08 / E09 | EPD / stabilized share | 4–8% / 4–9% | Bank 6% / 6% |
| E10 / E11 | Recall of the bank's existing flags | ≥ 80% / ≥ 90% | Same definitions |
| E12 | Stabilized next-month roll below the fixed states | ≥ 20pp gap | *Synthetic:* 40% vs ~85% |
| E13 | Fixed states keep their state next month | ≥ 95% | Run-up fixed once past 4 |
| E14 | Stabilized persistence next month | 45–85% | Current behaviour |
| E15 | Option A straight-roller share | 55–80% | Most roll straight |
| E16 | Smallest option-B state | ≥ 5% | Actionable size |
| E17 | Smaller slow-roller split (C) | ≥ 4% | Actionable size |
| E18 | Stabilized at bucket 4 vs 7 | ≥ 2× | 90–95% roll at 6–7 |
| E19 / E19b / E20 | eta² of credibility / clean point / ability by state | ≤ 0.25 / ≤ 0.50 / ≤ 0.10 | Orthogonality |
| E21 | Stabilized with money coming in | ≥ 90% | Stabilized = paying |
| E22 | Residual clusters favour B over A | ARI gain ≥ 0.15 | *Synthetic:* 0.20 |
| E23 | One paid month matters (slow roller at run-up ≤ 4 / ≤ 3) | ≤ 0.70 | Most slow rollers held once |
| E24 | "Paying since 4" stays rejected | persistence ≤ 75% | *Synthetic:* 63% |
| E25 | INFO: exit spread across fixed states | report | Unknowable from synthetic |
| E26 | Stabilized accounts that leave and come back within k months | ≤ 10% | *Synthetic:* ~5–7% (§6.15) |

Every check carries an "if not met" action in the code and in the report. The self-test
also runs 14 **edge cases** from the design discussion (EPD with a blip, six clean months,
two blips, payoff from 4, staircase, both oscillating payers, …) and fails if any changes
state.

### Choosing the option on real data
1. Any **FAIL** → fix config/data first; read nothing else.
2. **E19b high** (repeat delinquent ≈ credibility clean point) **and** the risk team does not want the
   cured-before nuance → **A**. Otherwise **B**.
3. **E17 passes and** the risk team has distinct actions for intermittent vs erratic payers → **C**.
4. **E25 ≥ 5pp** → the mechanism carries risk on its own; report it to the risk team as a bonus.

---

## 9. Validation done so far *(synthetic)*

- **Calibrated generator** (`dpd_states/synth.py`): eight planted journey patterns
  (bust-out, clean abrupt shock, slow slide, staircase, stabilized, repeat episodes,
  dip-and-roll, volatile) plus a rare oscillating payer (1.2% of the spine); full lifecycles to exit; length-biased snapshot like a real
  spine; payment holidays (frozen buckets) and billing-cycle +2 jumps; one continuous
  tenure distribution. Matches the bank's figures: roll rates 70/80/89/95% (target
  70/80/90/95%), EPD 5.8% (6%), stabilized 6.5% (6%), single spell 83% from bucket 3 (85%).
- **Method report:** `validation/dpd_states_validation_*.md` (`python docs/deterioration_states/run.py synthetic`).
- **Real-data path self-test:** `validation/selftest_report_*.md` (`python docs/deterioration_states/run.py selftest`)
  runs the exact analysis and expectations the workplace run uses, on synthetic data with
  fake axis columns. All checks pass except two expected WARNs: E19b (repeat delinquent ≈
  credibility clean point, §6.6) and E16 (early-life straight roller 3.4% under the 12-month
  seasoned cut — a property of the synthetic tenure distribution, §5).

**What synthetic data cannot tell you:** whether the rolling states differ in outcome (they
share post-4 dynamics by construction), how big the real overlaps with credibility and
ability are, and how much payment holidays contaminate stabilized. The real-data run answers
all three.

---

## 10. Open decisions

1. Option A, B or C — decide from E19b, E17 and the risk team's actions (§8).
2. Spell definition (from bucket 3 or 4) — E07 shows which matches the bank's 85%.
3. EPD history threshold — confirm 3 months (one blip) against the bank's existing bust-out rule (E10).
4. Payment holidays / restructurings — if flags exist, exclude frozen months before Q2.
5. The long-run clause widens the bank's stabilized definition (+~1% of the spine) —
   confirm it with the owners of the existing rule (E11 will show the agreement drop).

## Glossary

Bucket — DPD band, one digit per month · Roll — +1 bucket, nothing paid · Hold — same
bucket, one month's due paid · Cure — back to 0/1 · Spell — continuous months at ≥ 2 ·
Blip — 1–2 month spell never past 2 · Run-up — last clean month to first month at 4 ·
Spine — accounts currently at 4–7 · eta² — share of an axis score's variance explained by
the states (0 = orthogonal) · ARI — agreement between two groupings (0 = chance, 1 = identical).
