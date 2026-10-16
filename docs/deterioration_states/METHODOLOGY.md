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
| **Deterioration (this)** | **How did they fall in, and are they holding now?** | **DPD bucket history only** |

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
| `max_prior_bucket` | deepest bucket reached in any earlier (non-blip) spell; 0 if none | yes |
| `runup_len` | months from the last clean month to the first month at bucket 4 (3 = straight 2→3→4) | yes |
| `runup_pays` | months on the way to 4 in which 2+ months were paid (moved back) | yes |
| `last6_in_band` | of the last 6 months (incl. today), how many were within today's bucket ±1 | no — current behaviour, by design |

Other features (`n_blips`, `runup_holds`, `post4_paid_rate`, `max_hold_run`, …) are
computed for diagnostics and discovery only.

---

## 4. The states

Questions are asked **in order**; the first "yes" assigns the state.

```
Q1  Bust-out?   <= 6 months of history before this spell
                AND no earlier spell above bucket 2 (a payoff from 2 is allowed)
                AND run-up to 4 took <= 3 months                     -> bust_out
Q2  Holding?    >= 5 of the last 6 months within today's bucket ±1   -> holding
Q4  Relapse?    [B, C] an earlier spell reached bucket 3 and cured   -> relapse
Q5  Fell fast?  run-up (last clean month -> first month at 4) <= 3 months
      yes -> sudden    [B, C: >= 36 months of history before the spell
                        -> sudden_established, else sudden_early_life]
      no  -> gradual   [C: paid 2+ months at once on the way down
                        -> gradual_fought_back, else gradual_slide]
```

(Q3 "partial payer" was tested and rejected — §6.)

### Three options

| Option | States | Use when |
|---|---|---|
| **A — minimal (4)** | bust_out, holding, sudden_decline, gradual_decline | Strict orthogonality: prior-spell history is left entirely to credibility |
| **B — balanced (6), recommended** | bust_out, holding, relapse, sudden_established, sudden_early_life, gradual_decline | Default. Matches the natural groups in the data (§6.1) and the 5–6 target |
| **C — detailed (7)** | B with gradual split into gradual_slide / gradual_fought_back | The risk team has a different action for "slid" vs "fought back" and both are ≥ 4% |

### What each state means and the action it points to

| State | Reads as | Action flavour | Share *(synthetic)* |
|---|---|---|---|
| **bust_out** | Short history, rolled straight in, never really paid | Fraud / first-party review, early legal; no restructuring | 6% (bank: 6%) |
| **holding** | Paying about one month's due each month for 5 of 6 months | **Offer restructuring to break the hardship** | 7% (bank's stabilized: 6%) |
| **relapse** | Has been here before and cured from bucket 3 | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 17% |
| **sudden_established** | Years clean (≥ 36 months), then a straight roll | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 35% |
| **sudden_early_life** | Under 3 years of clean history, then a straight roll | Same triage; also an underwriting signal for acquisition | 20% |
| **gradual_decline** | Paid something on the way down but kept slipping | Over-indebted: longer-tenor restructure or settlement | 16% |
| ↳ gradual_slide *(C)* | Paid one month here and there, never caught up | Chronic insufficiency: restructure to what they actually pay | 10% |
| ↳ gradual_fought_back *(C)* | Paid 2+ months at once, then rolled anyway | Lumpy / irregular income: plan aligned to inflow timing | 6% |

**Holding is the only state that moves month to month** — it describes what the customer
is doing now (*synthetic:* 60% are still holding next month). Every other state is fixed
once the account is past bucket 4 (*synthetic:* 97–100% keep their state next month).

---

## 5. Thresholds and the evidence behind them *(synthetic sweeps)*

| Threshold | Value | Why this value | What moving it does |
|---|---|---|---|
| Bust-out history | **≤ 6 months** | Matches the bank's "max a few months". No natural knee in the data, so it is a definition | 6 m: catches ~80% of planted bust-outs at ~80% purity. 12 m: ~97% caught but purity falls to ~63% — short-history clean customers flood in |
| Bust-out earlier peak | **≤ 2** | A bust-out may pay off once, but only from bucket 2 (business rule) | `0 2 3 4 0 0 2 3 4 5 6` is therefore relapse, not bust-out |
| Run-up for "sudden" | **≤ 3 months** | The one sharp threshold: any single paid month on the way down makes it gradual | ≤ 4 moves ~70% of genuine slow slides into sudden (slides in gradual: 98% → ~30%) |
| Holding band | **5 of last 6 months within ±1** | The bank's existing stabilized rule, unchanged | 4 of 6: share ~14%, next-month roll ~46%, persistence ~63%. 6 of 6: ~5%, ~32%, ~80% |
| Relapse depth | **earlier spell reached 3** | The bank counts ~85% single-spell; spells from 3 give 83% *(synthetic)* | From 2: 19%. From 4: 5% (cures from 4+ are rare) |
| Established | **≥ 36 months** | Where the residual clusters split (§6.1); gives two usable groups | 24 m: 43% / 11%. 48 m: 27% / 28% |

**Rule order.** Bust-out is asked before holding (the bank's order). Only ~0.2% of the
spine is a bust-out that is also holding today, so the order barely matters.

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
- **Residual clustering (after bust-out and holding) — kept as a diagnostic.** k-means at
  k = 6 on the remaining ~88% found six clean, nameable groups: long-clean straight roll,
  short-clean straight roll, earlier spell to 3+, paying after 4 but still rolling, held on
  the way, paid 2+ on the way. Agreement with option A 0.16, **B 0.55, C 0.58** — the
  evidence that two residual states were too few. Every B/C split maps to one of these
  clusters with a one-line rule; the clusters themselves are not the states.

### 6.2 A "mixed" / residual state
Dropped. An ordered tree with a default branch is MECE without one, and a residual
bucket invites "everything we don't understand" to grow.

### 6.3 Staircase (holds for months at each level, then steps up)
Merged. While it is holding it *is* holding (that is the actionable fact); just after a
step it reads as gradual. Telling a genuine holder from a staircase mid-hold needs more
than 6 months of history and an extra rule, and the next-month risk was the same
(*synthetic:* 0.28 vs 0.29). It separates only over 6 months (exit 33% vs 50%).

### 6.4 Partial payer — "pays after reaching 4 but still rolling" (Q3)
Tested at 0.34 / 0.5 / 0.67 months paid per month since 4. Rejected:
- barely separates risk (next-month roll ~80% vs ~86%);
- unstable — ~37% leave it every month — and it **drags the stability of the fixed
  states from ~98% to ~91%**, because accounts flip in and out of it;
- 79% of it is "paid in the last 3 months" — the credibility axis's 2-point component.

It is one of the six natural residual clusters, so it is real behaviour — but it belongs
to credibility, not here. The switch is kept in code (`partial_min_paid_rate`) so the
test can be repeated (expectation E24).

### 6.5 Separate states for slow slide, dip-and-roll, volatile
Merged into gradual (A, B) or split once by "paid 2+ months on the way" (C). The three
confuse each other in every view (shapes, clusters, trees), and the risk actions are close.
Much of "volatile" (cure then relapse) is a relapse by definition.

### 6.6 Relapse in option A
Left out of A on purpose. Relapse is built from earlier spells — the same history
credibility's 1-point "pre-delinquency clean" flag scores. In the self-test (with a clean
point defined as "no earlier spell") the states explained **84%** of that point's
variance. It is included in B/C because it is only 1 of credibility's 5 points and it
carries more than a yes/no: *cured from bucket 3 before* is evidence of catch-up capacity.
Expectation E19b measures the real overlap and decides A vs B.

### 6.7 "Holding or improving" clause (today's bucket ≤ 6 months ago)
Dropped. It changed **0.0%** of assignments. Sudden/gradual describe how the account fell
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

### 6.14 Established / early-life split in option A
Not in A because, in synthetic data, it adds no risk separation (both ~94–95% exit within
6 months, by construction). It is in B/C for its action difference (life event vs
underwriting signal). Real outcomes decide whether it earns its place.

---

## 7. Overlap with the other axes (known and measured)

| Overlap | Size *(synthetic)* | Treatment |
|---|---|---|
| holding ↔ credibility "money coming in" (2 pts) | 100% of holders have money in; 44% of non-holders do too | One-directional: holding is stricter (enough to hold the bucket, 6 months). Accept and state it. E21 |
| relapse ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.84 of the clean point explained by B states | Decides A vs B. E19b |
| sudden/gradual ↔ ability | none in synthetic (by construction) | Sudden may proxy income loss on real data — fine, but say so. E20 |
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
| E08 / E09 | Bust-out / holding share | 4–8% / 4–9% | Bank 6% / 6% |
| E10 / E11 | Recall of the bank's existing flags | ≥ 80% / ≥ 90% | Same definitions |
| E12 | Holding next-month roll below the fixed states | ≥ 20pp gap | *Synthetic:* 44% vs ~85% |
| E13 | Fixed states keep their state next month | ≥ 95% | Run-up fixed once past 4 |
| E14 | Holding persistence next month | 45–85% | Current behaviour |
| E15 | Option A sudden share | 55–80% | Most roll straight |
| E16 | Smallest option-B state | ≥ 5% | Actionable size |
| E17 | Smaller gradual split (C) | ≥ 4% | Actionable size |
| E18 | Holding at bucket 4 vs 7 | ≥ 2× | 90–95% roll at 6–7 |
| E19 / E19b / E20 | eta² of credibility / clean point / ability by state | ≤ 0.25 / ≤ 0.50 / ≤ 0.10 | Orthogonality |
| E21 | Holders with money coming in | ≥ 90% | Holding = paying |
| E22 | Residual clusters favour B over A | ARI gain ≥ 0.15 | *Synthetic:* 0.39 |
| E23 | One paid month matters (gradual at run-up ≤ 4 / ≤ 3) | ≤ 0.70 | Most gradual held once |
| E24 | Partial payer stays rejected | persistence ≤ 75% | *Synthetic:* 63% |
| E25 | INFO: exit spread across fixed states | report | Unknowable from synthetic |

Every check carries an "if not met" action in the code and in the report.

### Choosing the option on real data
1. Any **FAIL** → fix config/data first; read nothing else.
2. **E19b high** (relapse ≈ credibility clean point) **and** the risk team does not want the
   cured-before nuance → **A**. Otherwise **B**.
3. **E17 passes and** the risk team has distinct actions for slide vs fought-back → **C**.
4. **E25 ≥ 5pp** → the mechanism carries risk on its own; report it to the risk team as a bonus.

---

## 9. Validation done so far *(synthetic)*

- **Calibrated generator** (`dpd_states/synth.py`): eight planted journey patterns
  (bust-out, clean abrupt shock, slow slide, staircase, stabilized, repeat episodes,
  dip-and-roll, volatile); full lifecycles to exit; length-biased snapshot like a real
  spine; payment holidays (frozen buckets) and billing-cycle +2 jumps; one continuous
  tenure distribution. Matches the bank's figures: roll rates 70/79/89/94% (target
  70/80/90/95%), bust-out 5.8% (6%), stabilized 6.6% (6%), single spell 83% from bucket 3 (85%).
- **Method report:** `validation/dpd_states_validation_*.md` (`python -m dpd_states.run_synthetic`).
- **Real-data path self-test:** `validation/selftest_report_*.md` (`python -m dpd_states.selftest`)
  runs the exact analysis and expectations the workplace run uses, on synthetic data with
  fake axis columns. All checks pass except E19b (expected WARN, §6.6).

**What synthetic data cannot tell you:** whether the rolling states differ in outcome (they
share post-4 dynamics by construction), how big the real overlaps with credibility and
ability are, and how much payment holidays contaminate holding. The real-data run answers
all three.

---

## 10. Open decisions

1. Option A, B or C — decide from E19b, E17 and the risk team's actions (§8).
2. Spell definition (from bucket 3 or 4) — E07 shows which matches the bank's 85%.
3. Bust-out history threshold — confirm 6 months against the bank's existing rule (E10).
4. Payment holidays / restructurings — if flags exist, exclude frozen months before Q2.

## Glossary

Bucket — DPD band, one digit per month · Roll — +1 bucket, nothing paid · Hold — same
bucket, one month's due paid · Cure — back to 0/1 · Spell — continuous months at ≥ 2 ·
Blip — 1–2 month spell never past 2 · Run-up — last clean month to first month at 4 ·
Spine — accounts currently at 4–7 · eta² — share of an axis score's variance explained by
the states (0 = orthogonal) · ARI — agreement between two groupings (0 = chance, 1 = identical).
