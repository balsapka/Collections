# Deterioration states — methodology

How a credit-card account in buckets 4–7 fell into delinquency, and what it is doing now,
read from its DPD bucket history only. One state per account, assigned by a short
decision tree. MECE by construction, simple enough to explain to the risk team in one
slide, and designed to stay out of the way of the other persona axes.

> **Status.** Designed and validated on calibrated **synthetic** data, then independently
> reviewed (24 findings — see [REVIEW.md](REVIEW.md) for each finding and what was done).
> Not yet run on the bank's book. Every number marked *(synthetic)* is a *method check*,
> not a finding about the portfolio. The real-data run is `run.py validate` on a file
> (now) or `snippets/dpd_states_validate.py` on Spark (production); expectations in §8.

---

## 1. Where this sits among the persona axes

| Axis | Question it answers | Inputs |
|---|---|---|
| Locatability | Can we reach them? | Reachability flag, in-country flag |
| Ability | Can they pay? | Score: salary, inflow, CASA balance |
| Payment credibility | Do they pay and keep their word? | Score: promises kept (0–2), money coming in last 3 months (0–2), pre-delinquency history clean (0–1) |
| **Deterioration (this)** | **How did they fall in, and are they stabilized now?** | **DPD bucket history only** |

Design rules agreed with the business owner:

1. **MECE** — every account gets exactly one state; no "other" bucket for behaviour.
2. **Simplicity beats precision** — a rule a collector can repeat beats a better-fitting
   one nobody can explain. Thresholds are round numbers.
3. **Orthogonal where possible** — the states must not rebuild the credibility or ability
   score. Known overlaps are named (§7), not hidden.
4. **5–6 states, at most 8**, each with a different action for the risk team.

---

## 2. Population and data conventions

- **Spine:** credit-card accounts whose **current** bucket is 4, 5, 6 or 7. Bucket 8+ is
  a separate category. The input file for sign-off is the CC 60–180 DPD segment
  (Aug 2026); accounts at bucket 3 in it are outside the spine and filtered out.
- **The string:** one digit per month, **leftmost = current month**
  (`54320002000` → today 5, last month 4, …). The **oldest (rightmost) digit is the first
  billed month**, so it is almost always 0 or 1. Exceptions: rare missing history, 180+
  accounts without history (start at 9, outside the spine), and restructured cards/loans
  re-opened as a new account at their previous bucket.
- **Reliable window: January 2024 onwards.** Older DPD history is unreliable, so every
  string is cropped to the newest months from `RELIABLE_FROM` (2024-01) to
  `SNAPSHOT_MONTH` (2026-08) — **32 months** — or to the source's own fixed window if shorter
  (`SOURCE_WINDOW_MONTHS`; the sign-off file now carries full history, so 32 applies). A
  string that fills the whole window may have older history and is treated as cropped —
  never EPD, never "history starts delinquent", and a straight roller is seasoned.
  Effects, all handled:
  - EPD is unaffected: an EPD has at most 3 clean months plus a short straight roll, so its
    string is under 12 digits and never cropped. As a safety net, a cropped string can
    never be EPD (its oldest digit is no longer the first billed month).
  - A spell that started before 2024 makes a cropped string start delinquent. That is
    normal history, not a data issue, so Q0 skips cropped strings; these accounts (0.16%
    of the synthetic spine) are classified normally — in practice mostly stabilized.
  - Seasoned (≥ 12 months) and the 12-month repeat window fit inside 32 months; earlier
    spells that ended before 2024 are invisible, which can slightly under-count repeat
    delinquents whose spell began in early 2024.
  *(Synthetic: 74% of strings cropped; option-B shares essentially unchanged.)*
- **Read it as text.** A numeric column drops digits (Excel keeps 15 significant digits;
  leading zeros vanish). The file reader refuses number-like values.
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
- **Data artefacts are cleaned before anything else, and counted:**
  - *Impossible one-month glitches.* A single 0/1 month between two months at 3+
    (`4 0 4`: a cure cannot jump straight back to 4) is read as a hold; a single month at
    3+ between two clean months (`0 3 0`: an account cannot jump from 0 to 3) is read as
    clean. Neither creates an earlier spell.
  - *Billing-cycle +2 jumps.* A true `3 4 5` reported as `3 3 5` or `3 5 5` is repaired.
    The hold *before* the jump is preferred as the artefact (it is already observed); the
    hold after is used only if that does not move a month observed at 4 back below 4; a
    hold at 0/1 is never an artefact. The repair is therefore causal: a state assigned
    today does not change when next month's digit arrives. Any other +2 is read as a roll.

---

## 3. Features used by the states

| Feature | Definition | Fixed once past 4? |
|---|---|---|
| `left_censored` | the oldest month in the string is already at bucket 2+ | yes |
| `months_before_spell` | months of history before the current spell started (blip months included) | yes |
| `n_blips` | earlier 1–2 month excursions that never passed bucket 2 (EPD allows one) | yes |
| `n_prior_episodes` | earlier real (non-blip) spells (EPD requires none) | yes |
| `gap_prior_peak3` | clean months between the end of the most recent earlier spell that reached bucket 3 and the start of this one (repeat delinquent: ≤ 12) | yes |
| `spell_pay_events` | months in the current spell with any payment (hold or move back); EPD requires 0 | **no** — EPD ends when they pay, by design |
| `runup_len` | months from the last clean month to the first month at bucket 4 (3 = straight 2→3→4) | yes |
| `runup_pays` | months on the way to 4 in which 2+ months were paid (moved back) | yes |
| `last6_in_band` | of the last 6 months (incl. today), how many were within today's bucket ±1 | **no** — current behaviour, by design |
| `months_since_4`, `chg_6m` | months since first reaching 4 in this spell; today's bucket minus the bucket 6 months ago (long-run clause) | **no** — current behaviour, by design |

All other features (`runup_holds`, `post4_paid_rate`, `max_hold_run`, …) are diagnostics
only. The current-behaviour inputs are confined to the stabilized question and the EPD
"never paid" condition, so every other state is fixed once the account is past 4.

---

## 4. The states

Questions are asked **in order**; the first "yes" assigns the state.

```
Q0  History starts delinquent?  oldest month already at bucket 2+ (restructured re-open,
                                migrated or missing history)  -> history_starts_delinquent
Q1  Early payment default?  <= 3 months of history before this spell (at most one blip,
                            no earlier real spell) AND never paid since crossing bucket 2
                            (every month of the spell a roll — still falling)
                                                               -> early_payment_default
Q2  Stabilized?             >= 5 of the last 6 months within today's bucket ±1
                            OR (>= 6 months since first reaching 4 AND at most 1 bucket
                                higher than 6 months ago)      -> stabilized
Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and ended
                            <= 12 months before this spell started
                                                               -> repeat_delinquent
Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
      yes -> straight_roller  [B, C: >= 12 months of history before the spell
                               -> straight_roller_seasoned, else straight_roller_early_life]
      no  -> slow_roller      [C: paid 2+ months at once on the way down
                               -> slow_roller_erratic, else slow_roller_intermittent]
```

(Q3 "paying since bucket 4" was tested and rejected — §6.4.) Q0 is a data-quality guard,
not a behaviour state: it stops truncated or restructured histories from being forced
into EPD. It should be rare (E04); restructured accounts are a deferred decision.

### Three options

| Option | States | Use when |
|---|---|---|
| **A — minimal (4)** | EPD, stabilized, straight roller, slow roller | Strict orthogonality: prior-spell history is left entirely to credibility |
| **B — balanced (6), recommended** | EPD, stabilized, repeat delinquent, seasoned straight roller, early-life straight roller, slow roller | Default; the 5–6 target |
| **C — detailed (7)** | B with slow roller split into intermittent payer / erratic payer | The risk team has a different action for each and both are ≥ 4% |

Early-life straight roller stays a state in B and C, but if real data puts it under 5%
(E16) it is merged into straight roller and kept as an early-life flag (agreed).

### What each state means and the action it points to

| State (display name · `code`) | Reads as | Action flavour | Share *(synthetic)* |
|---|---|---|---|
| **Early payment default (EPD)** · `early_payment_default` | At most 3 months of history (one blip allowed), rolled straight in and has **never paid since crossing bucket 2** — still falling, so short-tenure by nature | Early-risk / first-party-fraud review, early legal; no restructuring | 4.3% (bank's broader rule: 6%) |
| **Stabilized** · `stabilized` | Paying about one month's due each month for 5 of 6 months — or, 6+ months after first reaching 4, still within one bucket of where it was 6 months ago (pays what is due on average, unevenly) | **Offer restructuring to break the hardship** | 7.8% (bank's rule alone: 6.9%; bank: 6%) |
| **Repeat delinquent (re-default)** · `repeat_delinquent` | Cured a spell that reached bucket 3 and fell back in within 12 months | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 10.8% |
| **Seasoned straight roller** · `straight_roller_seasoned` | At least a year on book, then rolled straight to bucket 4 with no payment on the way down (some have paid since) | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 57.4% |
| **Early-life straight roller** · `straight_roller_early_life` | 4–11 months on book, then rolled straight to bucket 4 | Same triage; also an underwriting signal for acquisition | 4.7% — under the 5% floor in synthetic data; the real share decides (E16) |
| **Slow roller (partial payer)** · `slow_roller` | Paid something on the way down to bucket 4 but kept rolling | Over-indebted: longer-tenor restructure or settlement | 15.1% |
| ↳ **Intermittent payer** *(C)* · `slow_roller_intermittent` | Paid one month here and there on the way down, never caught up | Chronic insufficiency: restructure to what they actually pay | 9.3% |
| ↳ **Erratic payer** *(C)* · `slow_roller_erratic` | Caught up 2+ months at once on the way down, then rolled again | Lumpy / irregular income: plan aligned to inflow timing | 5.7% |
| **Not classified — history starts delinquent** · `history_starts_delinquent` | Data quality: the string starts already delinquent | Fix the data / treat restructured accounts separately (deferred) | 0% *(synthetic has none)*; expect < 1% |

In option A the two straight-roller states are one: **Straight roller** · `straight_roller`.

**What moves month to month.** Stabilized is current behaviour (*synthetic:* 60% are still
stabilized next month). EPD ends the month the account pays (it then becomes stabilized
or a straight roller). Every other state describes how the account fell in and is fixed
once it is past bucket 4 — it can only move into stabilized (*synthetic:* 99.7%+ keep their
state or move into stabilized next month). Read "straight roller" as *rolled straight to
bucket 4*, not *never paid since*: 32–36% of straight rollers have paid at least one
month since reaching 4 *(review, synthetic)*.

### 4.1 Names

The names use established card-risk and collections terms, and follow two rules:

1. **Describe behaviour, not intent.** These labels reach collector screens, audit trails
   and possibly complaint files. They say what the DPD history shows ("never paid since
   crossing 2", "rolled straight to 4", "paid one month at a time"), never why ("fraud",
   "won't pay"), which the history cannot prove.
2. **Code names are stable; display names are free.** Code uses short identifiers
   (`early_payment_default`, `straight_roller_seasoned`, …). `DISPLAY_NAMES` and `REMARKS`
   in `dpd_states/states.py` carry the business labels, so renaming for the risk team never
   breaks the pipeline or old results. Every report starts with the names table.

| Term | Where it comes from | Note |
|---|---|---|
| **Early payment default (EPD)** | Early-risk monitoring (FPD / SPD / TPD = first / second / third payment default; EPD = default early in the life of the account) | **Formerly "bust-out"** — the bank's internal name, kept in remarks. Classic *bust-out* fraud is different: a customer builds a good record and limit, maxes out (often with cash advances) and disappears. Its DPD history is clean-then-straight-roll, so it lands in **seasoned straight roller**; spotting it needs spend / utilisation spikes before delinquency — a fraud overlay, not this axis |
| **Stabilized** | The bank's own term; roll-rate "stay" behaviour | Industry has no single standard label for "pays enough to stay in the bucket" |
| **Repeat delinquent / re-default** | Collections recidivism; re-default rates after cure or restructure, usually within 12–24 months | |
| **Straight roller** | Core card-collections term: rolls through the buckets without a payment | Here: on the way down to bucket 4 |
| **Seasoned / early-life** | Seasoning and months on book (MOB); the first 12 months is the standard early-life window | |
| **Slow roller (partial payer)** | Roll-rate language: the counterpart of the straight roller | **Also called partial payer** — the more common collections term. The rejected Q3 state was renamed `paying_since_4` so "partial payer" means only this state |
| **Intermittent / erratic payer** | Collections payment-pattern labels | |

---

## 5. Thresholds and the evidence behind them

Parameters marked **[business]** are agreed business definitions. They change only with
the business owner — never to make a share or an expectation check come out right (a
share-matching tune is circular: §6.14). Sweeps are reported in every run to show
sensitivity, not as a menu.

| Threshold (`parameter`) | Value | Why this value | What moving it does *(synthetic)* |
|---|---|---|---|
| EPD history (`epd_max_history`, `epd_max_blips`) [business] | **≤ 3 months, at most one blip** | A customer who never pays misses the first or second bill: 2–3 clean months at most (`0 0 2 3 4`, `0 0 0 2 3 4`, `0 2 0 2 3 4`) | At 6 or 12 months the state fills with early-life defaults (`0 0 0 0 0 0 2 3 4`), which now land in early-life straight roller |
| EPD "never paid" [business] | **no hold or move back in the current spell** | Owner: an EPD never pays after crossing bucket 2, it keeps falling and leaves the spine | `0 0 2 3 4 4 4 4 4 4` (paying monthly) is stabilized, not EPD; `0 0 2 3 4 4 5 6` (paid once) is an early-life straight roller |
| Straight-roller run-up (`straight_max_runup`) | **≤ 3 months** | Any single paid month on the way down makes it a slow roller | ≤ 4 moves ~70% of slow rollers into straight roller. 41% of slow rollers rest on one hold — E23 / E28 test whether that month is real |
| Stabilized band (`stabilized_min_in_band`) [business] | **5 of last 6 months within ±1** | The bank's existing stabilized rule, unchanged | 4 of 6: share ~14%, next-month roll ~46%. 6 of 6: ~5%, ~32% |
| Stabilized long-run clause (`stabilized_long_run_months`, `_max_rise`) [business] | **≥ 6 months since first reaching 4, at most +1 bucket over 6 months** | Fixes oscillating payers and accounts that just paid down (§6.15). Straight rollers cannot meet it (they leave the spine within ~4 months) | Adds ~1% of the spine to stabilized. +2 would take in slow drifters paying ~4 of 6 dues; `None` switches it off |
| Repeat-delinquent depth (`repeat_min_prior_peak`) [business] | **earlier spell reached 3** | Cures from 4+ are rare; spells reaching 3 give 83% one-spell vs the bank's ~85% | From 2: more; from 4: ~5% |
| Repeat-delinquent window (`repeat_window_months`) [business] | **ended ≤ 12 months before this spell** | Owner decision (changed from 24); the common re-default window. Measured to the start of this spell, so the state stays fixed | Lowers the overlap with credibility's lifetime clean point (eta² 0.81 with no window → 0.52 at 12 months) |
| Seasoned (`seasoned_min_months`) [business] | **≥ 12 months** | The first year on book is the standard early-life window; EPD already takes ≤ 3 months, so early life = 4–11 months | Early life 4.7% at 12 m; it depends on the book's tenure mix, so the real share decides (E16) |

**Rule order.** Q0 and EPD come before stabilized; since an EPD has never paid in its
spell, an account cannot be both, so the order no longer matters for them.

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
  ambiguous, so the soft-assignment advantage disappears. Not used. GMM fits continuous
  inputs (ability scores, balances) far better than DPD-derived counts.
- **Residual clustering (after EPD and stabilized) — a diagnostic only.** k-means at k = 6
  on the rest found six nameable groups (long-clean straight roll, short-clean straight
  roll, earlier spell to 3+, paying after 4 but still rolling, held on the way, paid 2+ on
  the way), and every B/C split maps to one of them with a one-line rule. Its agreement
  score (ARI) is **not** evidence for B over A: the independent review showed that any
  finer partition built on the clustered features gains ARI — a meaningless split at
  median tenure gained 0.16. E22 is therefore INFO only.

### 6.2 A "mixed" / residual state
Dropped. An ordered tree with a default branch is MECE without one, and a residual
bucket invites "everything we don't understand" to grow. (Q0 is a data-quality guard, not
a behaviour bucket.)

### 6.3 Staircase (holds for months at each level, then steps up)
Merged. While it is holding a bucket it *is* stabilized (that is the actionable fact);
just after a step it reads as a slow roller. Telling a genuine holder from a staircase
mid-hold needs more than 6 months of history and an extra rule, and the next-month risk
was the same (*synthetic:* 0.28 vs 0.29).

### 6.4 "Paying since bucket 4" — pays after reaching 4 but still rolling (Q3)
Tested at 0.34 / 0.5 / 0.67 months paid per month since 4. Rejected:
- barely separates risk (next-month roll ~80% vs ~86%);
- unstable — ~37% leave it every month — and it drags the stability of the fixed states
  down by ~7pp, because accounts flip in and out of it;
- 79% of it is "paid in the last 3 months" — the credibility axis's 2-point component.

It is one of the natural residual clusters, so it is real behaviour — but it belongs to
credibility. The switch is kept (`paying_since_4_min_rate`) so the test can be repeated (E24).

### 6.5 Separate states for slow slide, dip-and-roll, volatile
Merged into slow roller (A, B) or split once by "paid 2+ months on the way" (C). The three
confuse each other in every view, and the risk actions are close. Much of "volatile"
(cure then relapse) is a repeat delinquent by definition.

### 6.6 Repeat delinquent in option A
Left out of A on purpose. Repeat delinquent is built from earlier spells — the history
credibility's 1-point "pre-delinquency clean" flag scores. In the self-test the states
explain **52%** of that point's variance under the 12-month window (81% with no window). It is in B/C
because it is only 1 of credibility's 5 points and *cured from bucket 3 recently* is
evidence of catch-up capacity. E19b measures the real overlap and decides A vs B.

### 6.7 "Stabilized or improving" clause (today's bucket ≤ 6 months ago)
Dropped. It changed **0.0%** of assignments; the long-run clause (§6.15) covers the real cases.

### 6.8 Payment-based refinement of stabilized
Tested: "≤ 1 roll in 6 months AND paid 2+ months at least once" separated holders from
staircases at 99% precision — but only because the synthetic generator built it that way,
and it leans on payment behaviour (credibility). Replaced by the bank's own 5-of-6 rule.

### 6.9 Features that drift with time since bucket 4
Dropped from assignment: whole-spell roll rate, fixed-window counts, months paid since 4
as a count. Replaced by run-up features (fixed once past 4). The remaining
current-behaviour inputs (§3) are deliberate and confined to stabilized and EPD.

### 6.10 Shape table as the assignment
Kept for discovery and stakeholder examples only. ~5–6k distinct banded shapes; the top
30 cover ~35–40% of accounts — too fragmented to assign everyone.

### 6.11 n-gram ranking by planted-label purity
Fixed. Lift is measured against each account's own codes in shuffled order: lift > 1
means the order of moves matters. No planted labels are needed.

### 6.12 Treating +2 jumps as impossible — and the first repair
Replaced by repair. The first version of the repair looked ahead (it used next month's
digit) and also treated clean months as holds, so a "fixed" straight roller could become a
slow roller when the next month arrived (`…0224` → `…02244`), and `000034` borrowed a clean
month and became EPD. The repair is now causal and only uses holds at bucket 2+ (§2).

### 6.13 Payment-promise or inflow inputs in any state
Never used — credibility and ability own them. Their overlap is *measured* (§7).

### 6.14 EPD ("bust-out") with up to 6 months of history
The first version allowed ≤ 6 months, chosen to match "a few months". It made
`0 0 0 0 0 0 2 3 4` an EPD — but six clean months means about four bills were paid: an
**early-life default**. Its synthetic 6% match was circular: the generator's bust-out
volume had been tuned to hit 6% under that rule. Replaced by the agreed definition
(≤ 3 months, one blip) and, after review, the owner's "never paid since crossing 2".

### 6.15 Stabilized measured only around today's bucket (edge cases)
The bank's rule — 5 of the last 6 months within ±1 of **today's** bucket — misreads two
uncommon but real histories (oldest → newest, today is the last digit):

- **Oscillating payer** `0000 0000 2344 4334 5433 4565 54` — swings between 3 and 6 for over
  a year, paying roughly what is due on average. The rule flipped it between stabilized and
  "straight roller" **5 times in 16 months**.
- **Just paid down** `… 3 4 5 6 6 5 4` — paid two months twice (6 → 5 → 4). The band around
  today's 4 excludes the two 6s, so the rule called it a straight roller *because* it paid.

Fix adopted: the **long-run clause** (§5). Both cases are now stabilized from their sixth
month after first reaching 4; the only remaining dip is the single month at the top of a
3-month roll (3 → 4 → 5 → 6). Rejected alternatives: allowing +2 over 6 months (takes in
slow drifters), and a "sticky" rule that remembers last month's state (harder to audit).
Measured *(synthetic, with oscillating payers at 1.2% of the spine)*: of accounts ever
stabilized over 6 months, the share that **left and came back** is ~5% with the clause vs
~5.5–8% on the bank's rule alone. E26 tracks this on real data; both examples are
permanent regression cases.

### 6.16 Seasoned / early-life split in option A
Not in A: in synthetic data it adds no risk separation (by construction). It is in B/C for
its action difference (life event vs underwriting signal), with the merge rule in §4.

### 6.17 EPD that has started paying
Before the review, an account that entered like an EPD but then paid its monthly due for
6–10 months (`0 0 2 3 4 4 4 4 4 4`) stayed EPD, with the action "early legal; no
restructuring". The owner's rule — an EPD never pays after crossing bucket 2 — now sends it
to stabilized.

---

## 7. Overlap with the other axes (known and measured)

| Overlap | Size *(synthetic)* | Treatment |
|---|---|---|
| stabilized ↔ credibility "money coming in" (2 pts) | 98% of stabilized have money in; ~44% of the rest do too | One-directional: stabilized is stricter (enough to hold the bucket, 6 months). Accept and state it. E21 |
| slow roller ↔ credibility "money coming in" | near bucket 4 almost all slow rollers paid in the last 3 months (they paid on the way down); by bucket 7 far fewer | A clock effect of the run-up, not a separate signal. Reported by state × bucket in every run |
| stabilized ↔ credibility "promises kept" (2 pts) | likely (paying monthly) — not testable without the score | E19 measures the total |
| repeat delinquent ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.52 of the clean point explained by B states (12-month window) | Decides A vs B. E19b |
| straight / slow roller ↔ ability | none in synthetic (by construction) | Straight rolling may proxy income loss on real data — fine, but say so. E20 |
| any state ↔ locatability | none expected | E20b |

---

## 8. Real-data validation

### Two ways to run
- **File mode — for sign-off, no Spark.** `python docs/deterioration_states/run.py validate`
  reads `INPUT_FILE` (`data/input/dpd_synthetic_data.xlsx`, column `dpd_history_str`,
  CC 60–180 DPD, Aug 2026). A snapshot of today's segment has **no outcomes**: accounts that
  rolled to 8+ since are not in it, so roll rates and exits are SKIPPED. What it can show:
  shares, data quality, shapes, overlaps (if axis columns are in the file), and stability
  among the survivors (E13, E14, E26 run on accounts in the spine last month and today).
- **Spark mode — production.** `snippets/dpd_states_validate.py`, `main(catalog)`.

### How the backtest works from a single table (Spark mode)
Today's string holds the past: dropping its newest *k* digits gives the string as it was
*k* months ago, and the dropped digits are what happened next. Assumptions, each checked:
1. The table **keeps accounts that have since rolled to 8+ or closed** (a survivor-only
   table biases outcomes — the snippet warns when no backtest account is at 8+ today).
2. **Every string ends in the same (latest) month.** Strings frozen at charge-off or
   closure are not "today" — set `COL_STRING_AS_OF` to exclude them. Even 20% frozen exits
   bias bucket-4 roll by ~5pp while E03 still passes *(review)*.
3. **Exit codes are digits** — a write-off letter must be mapped in `CHAR_MAP`, or those
   accounts silently drop out (E02 now covers the backtest and the whole table).
4. The bank's roll rates (E03) are compared like for like (count- vs balance-weighted).

Outcome comparisons are **standardised to the bucket mix** (stabilized sits mostly at
bucket 4) and use exit within **3 months**, because 6-month exit saturates near 100% at
buckets 5–7.

### Expectations (checked automatically — `dpd_states/expectations.py`)

Anchor: **bank** = the bank's figures or rules · **design** = follows from the rules ·
**synthetic** = calibrated on the generator only (a WARN is a prompt to look) · **data**.

| | Check | Expected | Anchor |
|---|---|---|---|
| E01 | Exactly one known state per account | True (FAIL) | design |
| E02 | Unparseable strings (spine, backtest, whole table) | ≤ 2% (FAIL) | data |
| E03 | Backtest monthly roll rates vs 70/80/90/95% | ≤ 7pp (FAIL) | bank |
| E04 | Histories that start delinquent | ≤ 1% | bank |
| E05 | Unrepaired +2 jumps | ≤ 2% | synthetic |
| E06 | Bucket mix declines 4 → 7 | yes | bank |
| E07 | INFO: one-spell share, four definitions vs ~85% | report | bank |
| E08 / E09 | EPD / stabilized share | 3–8% / 4–10% | bank |
| E10 / E11 | Recall of the bank's existing flags | ≥ 80% / ≥ 90% | bank |
| E12 | Stabilized next-month roll below the rest (bucket-standardised) | ≥ 20pp | synthetic |
| E13 | Fixed states keep their state (or move into stabilized) | ≥ 95% | design |
| E14 | Stabilized persistence next month | 45–85% | synthetic |
| E15 | Option A straight-roller share | 55–80% | bank |
| E16 | Smallest optional option-B state (EPD and stabilized are required at any size; empty = 0) | ≥ 5% | design |
| E17 | Smaller slow-roller split (C) | ≥ 4% | design |
| E18 | Stabilized at bucket 4 vs 7 | ≥ 2× | bank |
| E19 / E19b / E20 / E20b | eta² of credibility / clean point / ability / locatability by state | ≤ 0.25 / 0.50 / 0.10 / 0.05 | design |
| E21 | Stabilized with money coming in | ≥ 90% | design |
| E22 | INFO: residual-cluster ARI gain (diagnostic only) | report | synthetic |
| E23 | INFO: straight vs one-hold slow roller, next-month roll | report | — |
| E24 | "Paying since 4" stays rejected | persistence ≤ 75% | synthetic |
| E25 | INFO: exit-within-3m spread across fixed states (bucket-std) | report | — |
| E26 | Stabilized accounts that leave and come back | ≤ 10% | synthetic |
| E27 | Uncropped string lengths vary (not padded / fixed-length) | p95 − p05 ≥ 6 | data |
| E28 | Run-up holds: largest calendar month vs its neighbours | ≤ 2.5× | data |

Every check carries an "if not met" action in the code and in the report; none of them
says "tune a business parameter until it passes". The self-test also runs **24 edge
cases** from the design discussion and the review, and fails if any changes state.

### Choosing the option on real data
1. Any **FAIL** → fix config/data first; read nothing else.
2. **E19b high** (repeat delinquent ≈ credibility clean point) **and** the risk team does
   not want the cured-recently nuance → **A**. Otherwise **B**.
3. **E17 passes and** the risk team has distinct actions for intermittent vs erratic payers → **C**.
4. **E16 fails on early-life straight roller** → merge it into straight roller (agreed).
5. **E25 ≥ 5pp** → how they fell in carries risk on its own; report it to the risk team.

---

## 9. Validation done so far *(synthetic)*

- **Calibrated generator** (`dpd_states/synth.py`): eight planted journey patterns
  (bust-out, clean abrupt shock, slow slide, staircase, stabilized, repeat episodes,
  dip-and-roll, volatile) plus a rare oscillating payer; full lifecycles to exit;
  length-biased snapshot like a real spine; payment holidays and billing-cycle +2 jumps;
  one continuous tenure distribution. Matches the bank's roll rates (71/78/89/94% vs
  70/80/90/95%), single spell 83% from bucket 3 (85%) and stabilized 6.9% under the
  bank's rule (6%).
- **Known calibration gap:** "never paid since reaching 4" is 59% in the generator vs the
  owner's first estimate of ~90% (which the owner later called overkill). The generator's
  holders are therefore probably over-represented; this affects synthetic shares of
  stabilized and slow roller, not the rules.
- **Method report:** `validation/dpd_states_validation_*.md` (`run.py synthetic`).
- **Real-data path self-test:** `validation/selftest_report_*.md` (`run.py selftest`) runs the
  exact analysis and expectations the workplace run uses, with fake axis columns, plus the
  24 edge cases. All checks pass except two expected WARNs: E16 (early-life straight roller
  4.7%) and E19b (repeat delinquent ≈ clean point).
- **Independent review:** 24 findings, none critical — see [REVIEW.md](REVIEW.md).

**What synthetic data cannot tell you:** whether the rolling states differ in outcome
(they share post-4 dynamics by construction), how big the real overlaps with credibility
and ability are, and how much payment holidays contaminate stabilized.

---

## 10. Open decisions

1. Option A, B or C — decide from E19b, E17 and the risk team's actions (§8).
2. The bank's exact spell definition — E07 reports four; it matters for the 85% check
   and for the repeat-delinquent depth.
3. EPD vs the bank's existing bust-out rule — ours is stricter ("never paid since
   crossing 2"); E10 shows the agreement.
4. Restructured accounts re-opened at their old bucket (Q0) — deferred by the owner.
5. Payment holidays / restructurings — account-level flags only show how often stabilized
   accounts carry them (E21, section 4 of the report); month-level exclusion needs
   month-level flags.
6. The long-run clause widens the bank's stabilized definition (~+1% of the spine) —
   confirm with the owners of the existing rule (E11).

## Glossary

Bucket — DPD band, one digit per month · Roll — +1 bucket, nothing paid · Hold — same
bucket, one month's due paid · Cure — back to 0/1 · Spell — continuous months at ≥ 2 ·
Blip — 1–2 month spell never past 2 · Run-up — last clean month to first month at 4 ·
Spine — accounts currently at 4–7 · eta² — share of an axis score's variance explained by
the states (0 = orthogonal) · ARI — agreement between two groupings (0 = chance, 1 = identical).
