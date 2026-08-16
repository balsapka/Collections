# Collections Scoring — Problem Statement and Proposed Direction

*Working document for discussion. v1, 2026-08-16. Status: positions stated to be
argued with, not finalised. Each problem carries an evidence status; "to verify" items
are checks scheduled for the first week.*

**Why this document.** The current scores are felt to "lack differentiation power".
We agree — but the causes are specific, and most of them are not model-quality issues.
This lays out the problems as we see them, the direction we propose, what we will
deliberately not do, and what we need from the business and the team. Push back where
you disagree; that is what the document is for.

---

## 1. What "no differentiation" actually means

Three different complaints hide under the phrase:

1. the score doesn't separate outcomes within the group an officer actually works
   *(a ranking problem)*;
2. the score doesn't tell the officer what to do differently *(a treatment problem)*;
3. the score repeats what is already on the screen *(an information problem)*.

Our evidence says **(3) is the dominant cause, with (2) close behind**. Pure ranking
(1) is largely fine — discrimination is decent and holds within DPD buckets — so
further tuning of the current model would not change how the score feels to use.

---

## 2. The problems

### P1 — The model mostly restates the account's delinquency state
**Evidence (verified):** the model's top features are days-since-last-payment, DPD
velocity, missed EMIs, last payment amount, block codes, DPD six months ago — all
measurements of *how delinquent the account already is*. Everything on that list is on
the officer's screen before the score loads.
**Consequence:** the score is accurate and unhelpful at the same time. It ranks, but
adds nothing the officer doesn't already see — which is precisely the complaint.
**Check (week 1):** a stripped model using only two state features, compared to the
full model. If it performs nearly as well, the point is proven quantitatively.
**Open to challenge:** if anyone believes specific non-state features carry real
weight today, name them and we will test exactly those.

### P2 — One score is serving three different decisions
Reachable customers need **negotiation** decisions (settle / restructure / pressure).
Unreachable customers need **locate** decisions (chase / field visit / agency / write
off). And 60–180 vs 180+ ask opposite questions: *who is not worth effort* (exclusion)
vs *which few are worth keeping in-house* (selection). No single Low/Medium/High label
can serve all of these; each needs a different quantity.

### P3 — The targets don't match the decisions
**60–180 (roll target).** An account paying half its installment every month still
"rolls forward" and gets the same label as one that vanished — yet for deciding where
to *stop spending effort*, those are opposite cases. The label also rewards treading
water (one installment = "stays in bucket") and looks one month ahead while the
decision commits months of effort. **To verify:** whether restructure-driven DPD
resets count as "moved back" — if so, part of today's target measures our own actions,
not customer behaviour.
**180+ (5% of outstanding or 1000 AED in 6m).** 1000 AED is 10% of a 10k balance and
0.2% of a 500k one — the target's meaning depends on balance. And a binary at a low
bar erases the differentiation being asked for: an account that recovers 5.1% and one
that recovers 55% get identical labels.

### P4 — "180+" is not one population
**Evidence (verified, cards):** under 2 years in the bucket → ~5% positive rate; over
2 years → 1–2%. The older cohort's internal history is stale by construction — their
pre-delinquency behaviour describes a person from 3–8 years ago. **Auto is different
again:** it is secured, recovery runs through the vehicle rather than the customer,
and it has not yet been measured separately *(to verify, week 1)*.

### P5 — The differentiating data is thinnest exactly where it is needed
- Bureau (AECB) goes quiet once a customer is delinquent — pulls fire at credit
  decisions, and for a delinquent customer there are none.
- Only ~10–20% of delinquent card customers hold another product with us; salary
  visibility (CASA) is partial.
- DCORE (contact attempts, promises-to-pay, field visits) has unresolved data-quality
  questions *(reconciliation check scheduled)*.

Net: for roughly **80% of the book, the card's own transaction and payment history
plus digital activity is all the live signal there is**. The proposal in §3 follows
from this: extract far more from that stream, rather than plan around data we do not
have.

### P6 — Extra information is not the same as knowing which treatment works
Knowing a customer is "willing but negotiating hard" vs "unable to pay" genuinely
helps choose actions — that we can build. But *proving* which action causes better
recovery requires variation in the actions taken, and offers were assigned
judgmentally (settlements went to accounts judged hopeless), so naive comparisons will
mislead. This cycle we will deliver segment descriptions plus an honest historical
crosstab (segment × action taken × outcome, clearly labelled correlational). We will
not claim causal treatment effects yet — and we ask that no one else does either.

### P7 — Selling below a cutoff destroys next year's training data
Once accounts below the keep/sell line are sold, their outcomes are never observed
again; future models can only learn from what past models chose to keep. This cannot
be repaired retroactively. **Ask:** agree a small permanent random holdout (~1%) kept
in-house below the cutoff, before the first sale wave.

### P8 — Personas must not be the score wearing a costume
If customer segments are built from the same information as the score, high-score
accounts pile into one segment and the segment × score grid adds nothing. Before any
strategy is designed on the grid, we will publish the segment mix *within* each score
band. If a band turns out to be 90% one segment, we will say the grid failed the test
there.

---

## 3. Proposed direction

- **Targets that match decisions, per segment.**
  - 60–180: **futility** — probability of essentially zero payment over the next N
    months (the exclusion call) — plus expected recovery amount. The current roll
    metric stays as a report.
  - 180+ under 2 years: **expected recovery in AED** via a two-part model
    (probability of any recovery × amount if any), delivered as an AED-ranked
    shortlist. The 5%/1000 view continues to be produced for continuity.
  - 180+ over 2 years: **no score from stale history.** Bulk treatment now; a costed
    proposal for bureau-based triggers if the economics justify it.
- **A priced keep/sell line, not a chosen one:** expected in-house recovery per decile
  against agency economics; the crossing point is the cutoff. Needs the numbers in §5.
- **Customer segments as estimated states, each validated against ground truth we
  hold** (this is what "synthesized features" means concretely — inferred states, not
  generated data):
  - *Manner of deterioration* — sudden shock vs gradual spiral vs chronically
    marginal, read from pre-delinquency card history anchored to when the trouble
    started. Full-book coverage; works even for dry late-stage accounts, because their
    histories differ even when their present looks identical.
  - *Locatability* — gone / stale details / avoiding / reachable, from channel-death
    patterns and travel/foreign signatures, validated against field-visit findings.
  - *Ability* and *willingness* — gated on two week-1 checks (value test on the
    salary-visible minority; DCORE trust test).
- **Deep learning in exactly one place:** learning representations of pre-delinquency
  behaviour sequences (an embedding feeding the LightGBM models), and only if simpler
  trajectory features leave measurable headroom. Everything else stays LightGBM.
- **Success criteria fixed in advance:** within-segment capture of recovered AED in
  the top 1/5/10%, precision of the bottom decile for futility, always against two
  deliberately dumb baselines (rank by balance; the two-feature state model). If we
  do not beat the dumb baselines, we will report that.

---

## 4. What we will NOT do, and why — argue here

| We won't | Because |
|---|---|
| Ship one "risk score" spanning 60–180 and 180+ | The decisions differ; a single label is what produced today's complaint |
| Build personas by unsupervised clustering | Cluster ids repackage the model's own inputs; they present well and change nothing |
| Generate synthetic data as a differentiator | Generation cannot add information absent from the source; useful only for imbalance/privacy |
| Regress recovery rate directly at 180+ | At 2–5% positives the distribution is a spike at zero; regression learns to predict zero for everyone |
| Make causal / uplift claims this cycle | No experiment and non-random assignment; we show correlational tables honestly instead |
| Score the >2y written-off book from internal history | That history describes who the customer was years ago |

---

## 5. What we need — decisions and inputs

| Ask | Why it matters | From |
|---|---|---|
| Field-visit unit cost; agency commission / sale terms by cohort | Sets the keep/sell line and the ROI of locate-work | Collections / Finance |
| Is 180+ disposal outright sale or commission placement? | Placement keeps outcomes visible → future models remain trainable | Collections |
| Feasible action menu per product (incl. Shariah position on settlements/ibra') | We model toward actions that are actually offerable | Collections / Shariah |
| Futility horizon N and the "negligible payment" threshold | Gives the exclusion label its operational meaning | Collections |
| Re-aging rules: does a restructure reset DPD? | Decides whether today's 60–180 target partly measures our own actions (P3) | Collections / IT |
| DCORE remediation timeline | Decides whether willingness/contact analytics are in or out this cycle | Data / IT |
| Permanent ~1% random holdout below the 180+ cutoff | The only way to validate the cutoff and keep future models honest (P7) | Collections / Finance |
| Bureau monitoring feed for the written-off book: permissible? cost? | The only live signal available for the >2y cohort | Compliance / Finance |

---

## 6. Sequencing

Week 1 is verification: the checks flagged in P1, P3, P4 and P5. Then, in order:
revised labels → deterioration features → locatability states → retrained per-segment
models → the P7/P8 gates before anything is operationalised. Progress and evidence
updates land in this document as checks close.

*Technical companion (implementation level): `docs/context/` in the modelling repo.*
