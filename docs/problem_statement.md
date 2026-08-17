# Collections Scoring — Problem Statement and Proposed Direction

*Working document for discussion. v2, 2026-08-16. Status: positions stated to be
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
decision commits months of effort.
**180+ (5% of outstanding or 1000 AED in 6m).** 1000 AED is 10% of a 10k balance and
0.2% of a 500k one — the target's meaning depends on balance. And a binary at a low
bar erases the differentiation being asked for: an account that recovers 5.1% and one
that recovers 55% get identical labels.

### P4 — "180+" is not one population, and neither is "the portfolio"
**Evidence (verified, cards):** under 2 years in the bucket → ~5% positive rate; over
2 years → 1–2%. The older cohort's internal history is stale by construction — their
pre-delinquency behaviour describes a person from 3–8 years ago.

**Cards and loans are also not one thing.** They sit in different source systems with
different structures, so they need separate pipelines and separate models — this is an
engineering fact before it is a modelling preference. Within loans, auto separates
cleanly (it is secured; recovery runs through the vehicle rather than the customer);
personal and personal cash do not. Auto has not yet been measured separately
*(to verify, week 1)*.

### P4b — Restructures break the account history, and may be inflating our numbers
A restructure closes the existing card or loan and opens a **new account**. Three
consequences, none currently handled:
- **Recovery may be overstated.** If the closing entry looks like a settlement credit,
  a restructure reads as a *recovery* in our outcome measures — but the debt moved, it
  was not repaid. *(To verify, week 1.)*
- **We lose the customer's history.** The new account starts empty, so any analysis
  built on pre-delinquency behaviour is blind for restructured customers.
- **We are throwing away a strong signal.** Agreeing a restructure is clear evidence of
  willingness to pay — arguably the cleanest we have, and it needs no collections-system
  data.

We cannot currently link the old account to the new one, and it is not uniform whether
the replacement starts at zero, at a lower bucket, or at the same one. **Ask:** does any
field, closure code, or system record connect them? (§5)

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
accounts pile into one segment and the segment × score grid adds nothing.

We are treating this as the **first** thing to prove, not the last. The segments are
being built and tested ahead of and independently of the scores, against four
questions, in order:

1. **Can we build it?** — coverage and class sizes across the book.
2. **Is it actually new?** — can the segment be predicted from the features we already
   have? If yes, it is a repackaging of what we know and we will say so and revise. This
   is the gate we expect to be hardest, and the one that most directly answers "does the
   persona angle work".
3. **Does it relate to outcomes?** — do cure and recovery rates genuinely differ across
   segments.
4. **Does it add anything?** — measured against a deliberately dumb two-feature model,
   not against our current model.

Then, with the business: **does each segment imply a different action?** If two segments
lead to the same action, we collapse them. A segment that fails question 2 will not be
carried forward, whatever it looks like on a slide.

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
| **How do we link a restructured account to its replacement?** Any reference field, closure code, or system record naming both | Without it: recovery may be overstated, restructured customers have no usable history, and we lose the best willingness signal we have (P4b) | Collections / IT |
| Where does the replacement account start — zero, lower bucket, or same bucket? Is it uniform? | Decides how restructures are treated in every outcome measure (P4b) | Collections / IT |
| DCORE remediation timeline | Decides whether willingness/contact analytics are in or out this cycle | Data / IT |
| Permanent ~1% random holdout below the 180+ cutoff | The only way to validate the cutoff and keep future models honest (P7) | Collections / Finance |
| Bureau monitoring feed for the written-off book: permissible? cost? | The only live signal available for the >2y cohort | Compliance / Finance |

---

## 6. Sequencing

**We are deliberately building the customer segments before touching the scores.** They
stand or fall on their own evidence (P8), and if the segment angle does not survive its
tests we would rather establish that in a few weeks than discover it after a model
rebuild.

- **Week 1 — verification:** the checks flagged in P1, P3, P4, P4b and P5. Two of these
  can change the plan materially: whether the current model is mostly restating account
  state, and whether restructures are inflating recorded recoveries.
- **Then — segments:** account-history table → manner-of-deterioration → locatability,
  each put through the four tests in P8, followed by an action-mapping session with
  collections (the real test).
- **In parallel — revised targets**, which do not depend on the segments.
- **Then — scores:** retrained per segment, measured against the dumb baselines, with
  the P7 holdout and P8 grid checks before anything is used operationally.

Cards lead; loans follow by porting the same patterns once the approach is proven.
Progress and evidence updates land in this document as checks close.

*Technical companion (implementation level): `docs/context/` in the modelling repo.*
