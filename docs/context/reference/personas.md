# Personas — what the axes are, what the states mean, and how to talk about them

Orientation and definition. Read this when you need to know **what an axis is claiming**,
what its states mean, or how to describe them to someone outside the modelling work.
Formula-level definitions live in `feature_specs.md`; execution order in `../TASKS.md`;
why each task exists in `roadmap.md`.

This file is the answer to "what is a persona axis, and what does `skip` mean" — questions
that kept being asked because the specs define the states operationally without ever
saying plainly what they are.

---

## 1. What an axis is, and what it is not

**A persona axis is an estimated latent state describing the _mechanism_ of a collections
failure** — a small set of named, mutually exclusive values, each implying a different
action.

The existing risk score answers **how bad is this account**. It answers it well and
redundantly: a model built only from the 24-month DPD history performs close enough to the
full model that the gap does not change behaviour in use, and everything driving it is on
the officer's screen before the score loads (`current_state §2`, T01). That dimension is
saturated — more features of the same kind add nothing (X2).

The axes answer **why is collection failing here**. Two accounts at 90 DPD with identical
balances can be a salary shock, a slow over-leverage spiral, or someone who has left the
country. Same present state, different correct actions. The difference lives in behaviour
*before* the delinquency, which is why it is invisible on the screen today — and why it
survives into the dry late-stage buckets, where the present looks identical for everyone
but the histories still differ.

| An axis IS | An axis is NOT |
|---|---|
| A supervised or rule-derived state with named values (S6) | An unsupervised cluster id (X1 — a lossy function of features the GBM already sees) |
| An **inferred state**, validated against ground truth we hold (S13) | Generated or synthetic data (X5 — generation cannot add information absent from the source) |
| A description of a **pattern** | A diagnosis of a **cause** — see §5 |
| Mechanism information | Magnitude information — expected recovery is the score, not an axis (X7) |
| Shipped with `observed\|inferred` + a validation number (S8/R6) | Shipped on face validity |

**Division of labour.** We ship axes, scores and evidence. The business owns the mapping
from a grid cell to an action (`domain_and_decisions §1`). The grid stays small: ~3 persona
states × ~3 score bands, collapsing to ≤6 strategies (S7).

---

## 2. The four axes

| Axis | Question | Coverage | Derivation | Status |
|---|---|---|---|---|
| **A4** manner of deterioration | How did they fall in? | Full book — card data only | Ordered rules over T0-anchored trajectory features | Build first (S9 — no DCORE dependency) |
| **A2** locatability | Can we reach them, and if not why? | Full book for core signals | Derived from contact outcomes × presence evidence; supervised refinement optional | Second |
| **A1** ability | Is there money, whatever the intent? | ~10–20% direct (CASA/RL), proxy elsewhere | Gated on T24 value test | Gated |
| **A3** willingness | Do they intend to pay? | Contact-dependent | Gated on T11; UC1 is the eventual source | Deferred, not blocked (§6) |

Build order follows **dependency, not importance** (S9). A4 leads because it needs nothing
outside our own card data — which matters because ~80% of the delinquent CC book is
card-only (`domain_and_decisions §4`).

---

## 3. A4 — manner of deterioration

Rules in `feature_specs.md §3.5`. Anchored to **T0**, the month the customer first went
overdue — not the calendar, and not the card block date, which is an operational event
downstream of the deterioration that moves whenever blocking policy changes (§3.0).

### `abrupt_shock`

**Was paying normally, then stopped dead.** Spend falls off a cliff (one month near-normal,
the next below a fifth of it), payment ratio was healthy through the earlier window, and
utilisation was *flat* beforehand rather than creeping up.

**What it implies:** this customer **was solvent**. Capacity may still exist, or may return.
Job loss, death, medical event, departure, business failure — all produce this shape.

**Action flavour:** locate first — this is the class where A2 matters most, because the
recovery case depends entirely on finding them. The expensive error is settling one cheaply.

### `gradual_spiral`

**Slowly drowning.** Utilisation climbing, payment ratio declining, cash advances ramping.
Taking expensive cash off a card is the signature of having run out of liquidity everywhere
else — borrowing to service borrowing.

**What it implies:** **structurally insolvent.** The capacity is not coming back, because in
the final stretch it was not income, it was credit. Almost certainly spiralling with other
lenders too, so we are competing for a shrinking pot.

**Action flavour:** settlement or restructure at realistic terms. Pressure is wasted.

### `chronic_marginal`

**At the limit, paying minimums — drift rather than a fall.** Minimum payments in most
observed months, high lifetime fee rate, persistently high utilisation.

**What it implies:** not a deterioration event at all, but a long-running pattern. Note this
customer was *profitable* on exactly this behaviour for a long time. Expect repeat
delinquency — the right frame is an annuity, not a cure.

**Action flavour:** structured arrangement, sized to what they have always actually paid.

> ⚠ **This class currently asserts more duration than it evidences.** Two of its three
> conditions (`min_pay_share_w12`, `util_mean_h1`) see only the ~12-month pre-delinquency
> window; only `fee_velocity_life` is lifetime. Under §3.0b truncation the window can be a
> few months, so "chronic" can rest on very thin evidence.
>
> **The consequence is a real confusion with `gradual_spiral`.** A spiral that plateaued at
> the limit *before* `W_pre` opened shows flat high utilisation with minimum payments, fails
> `gradual_spiral`'s rising-`util_slope` condition, falls through the ordered rules and lands
> here. Which class an account receives then depends on **when the spiral started relative to
> our window** — an artefact of the anchor, not a property of the customer. And that is
> exactly the boundary carrying the action difference.
>
> Fix: recruit `prior_spell_cnt_24m` / `months_since_prior_spell` / `tenure_at_t0_m` (already
> computed in §3.4, unused by §3.5) into the rule, and require a minimum `w_pre_clean_m`.
> Honest ceiling: CC prior-spell history is capped at 24 months by the DPD string, so the
> class can only ever mean *sustained across up to two years, plus lifetime tenure and fee
> rate*.

### `mixed`

**Not a class — a residual.** No rule fired cleanly. If it exceeds ~50% of volume the rules
are not discriminating and thresholds need iterating before the gates (T07 decision rule).

### Known blind spots

- **Restructured customers** (R13): the replacement account has no pre-delinquency history,
  so there is nothing to anchor on. `inherited_history_flag = 0` until T18/T19 supplies a link.
- **Truncated windows** (§3.0b): `w_pre_contaminated_flag` marks accounts where a prior spell,
  short tenure or the retention floor cut the window. The class is weaker evidence there.
- **The 180+ >2y cohort**: T0 often falls outside the 24-month DPD string entirely
  (`t0_censored_flag`) — an independent reason not to score that book from internal history (S5).

---

## 4. A2 — locatability

States and signals in `feature_specs.md §4`. **Derived, not learned** — see §4.2 there for
why the supervised version is a refinement rather than the main path.

### The states

| State | What is true | What you do |
|---|---|---|
| `reachable` | The right party picks up | Negotiate — hand to A1/A3 territory |
| `avoiding` | Channel live, right party there, will not engage | Escalate. This is a willingness problem wearing a contact costume |
| `skip` | Still here, but our contact details are wrong | Trace: address refresh, alternative number, employer, bureau address pull |
| `gone` | Left the jurisdiction | Domestic tracing and field visits are wasted — agency, cross-border, or write off |

**`skip` is skip-tracing jargon** — a "skip" is a debtor who moved on without leaving
forwarding details. Collections teams use the term natively; it is opaque to everyone else.
It earns its own state because it is **the cheapest state to fix**: trace them and they
often convert straight to `reachable`. Calling one `gone` writes off a recoverable account;
calling one `avoiding` means dialling a number that will never work.

### How the states are derived

Two independent evidence streams, crossed. Neither is a field visit.

- **Channel status** — what contact attempts came back with: number dead / rang unanswered /
  someone else answered / right-party contact. Plus email bounce vs delivered-no-reply.
- **Presence evidence** — is the customer still visibly active anywhere: post-T0 domestic
  transaction, CASA activity, domestic-IP login, other-product movement. Read against the
  departure signature already built for A4 §3.3.

| Attempt came back as | Presence evidence | No presence evidence |
|---|---|---|
| Right party answered | `reachable` | `reachable` — wherever they are, we have them |
| Rang, no answer | `avoiding` | **the one ambiguous cell** — departure signature decides |
| Someone else answered | `skip` | `gone` on a departure trail, else `skip` |
| Number dead / no delivery | `skip` | `gone` — **only** on a departure trail |

Three consequences:

1. **`reachable` needs no inference.** Speaking to the customer *is* the observation. This
   was the state field-visit labels supplied worst, and it turns out not to need them.
2. **Only one cell is genuinely uncertain**, and A4's departure features resolve most of it.
3. **Field visits are the adjudicator, not the label source.** A visit is sent *because*
   calling already failed, so visits can only ever teach us about accounts where calling
   already failed. Their remaining jobs: adjudicate the ambiguous cell, and validate `gone`
   precision — which is what protects the visit budget.

### Two traps

**Silence is not proof of departure.** `gone` is assigned only on a *positive* trail — travel
spend, foreign transaction, foreign login, salary stop — never on absence alone. For the ~80%
card-only population, once the card is blocked there may be no channel left to observe
presence on at all; silence then measures how little we can see, not where they are. Where
there is neither a departure trail nor anything left to watch, the answer is `unknown`.

**Uncontacted is not unreachable.** An account nobody called has no contact record, and a
naive model reads absence as `gone` — the same conditional error as training only on visited
accounts. Every signal is attempt-normalised (connect rate, pickup rate, RPC rate over
attempts made), `contact_attempts_n` travels on every row, and the state is `unknown` below a
minimum. Attempt time-diversity matters too: someone only ever called at 10am on weekdays who
never answers may simply be at work.

### Where A2 stops

**Locatability ends the moment the right person picks up.** A customer who answers and then
says nothing useful is *reached* — the failure is willingness, not location, and it belongs
to A3. Keeping this boundary sharp matters because it is exactly where UC1 will operate (§6),
and blurring it now guarantees grid collinearity later (S7/T15).

---

## 5. Naming discipline — two opposite failure modes

Both have already occurred in this pack, and they fail in opposite directions.

| Failure | Example | Why it is dangerous | Fix |
|---|---|---|---|
| **Too opaque** | `skip` | A reader who does not know the term cannot act on it — but they *ask*, so it surfaces | Gloss it, or rename if the audience is not collections |
| **Too legible** | `abrupt_shock` | Reads as a finding about a person's life. Nobody asks, so unearned confidence propagates silently into a live customer conversation | Provenance must travel with the label |

The opaque label announces its own uncertainty. The legible one hides it.

**Standing check for any new class (T07):** state what the name claims, then name the feature
that evidences the claim. If there is no such feature, either recruit one or rename the class.
Two of the four A4 classes failed this on inspection — `abrupt_shock` implies a diagnosed
cause the trajectory shape cannot supply, and `chronic_marginal` implies a duration the window
cannot see.

**Note this is not caught by the gates.** A class can separate outcomes perfectly (PV3) and
lift the model (PV4) while being misnamed — and a misnamed class misleads every downstream
reader, including the PV5 workshop where the business decides what action it implies.

**Consequence for shipping:** if any class label reaches the DCORE screen or an agent-facing
surface, the `observed|inferred` flag and `det_class_confidence` travel with it. The bare
label is not shippable to a live conversation.

---

## 6. A1 / A3 and the UC1 seam

**UC1 will deliver ability and willingness features from call-transcript analysis.** Keeping
A1 and A3 defined now — even while gated — means that work lands into a schema that already
exists rather than forcing a re-cut.

Four consequences:

1. **A3's gate is deferral, not permanent block.** It is currently framed as gated on DCORE
   PTP trust (T11), but its eventual source may be transcripts rather than structured fields.
2. **A2 sizes UC1's addressable book.** Transcripts exist only where the right party answered
   — that is precisely A2's `reachable` population.
3. **UC1 can never cover the unreached.** So A4 is not a stopgap until transcripts arrive; it
   stays the only axis with coverage on the hardest population. Complementary, not sequential.
4. **The selection lesson carries forward.** Transcript-derived willingness will be tempting
   to treat as ground truth for a model applied to everyone. That is the same conditional trap
   as field-visit-only labels — design against it now, not after.

The "answered but no meaningful conversation" bucket is where A2 ends and A3 begins, and it is
where transcripts would add most: deflection vs hardship vs dispute.

**A3's DCORE-free alternative:** agreeing a restructure is arguably the cleanest willingness
signal available, and needs no collections-system data. Blocked on recovering the old→new
account link (O13, T18/T19).

---

## 7. How the axes are consumed

**The axes plus segment scores are inputs to strategy, not a replacement for the collector's
screen.** The DCORE front end already shows an officer the account's present state, and
re-explaining that through data is the failure being exited (P1), not one to repeat. The one
thing worth surfacing there is the axis label itself — with its provenance (§5) — because it
is the only genuinely new thing: *how this account got here*.

**PV5 makes risk heads validators, not only consumers.** If a class does not change what
anyone does, it gets merged out. The action-mapping workshop (T16) is a real test of the work,
not a downstream handoff.

**Language guard.** There is no single risk score across the book (R5, S1). 60–180 is an
*exclusion* problem (`futility_60_180`); 180+ under two years is a *selection* problem
(`exp_recovery_aed_180p_lt2y`). One Low/Medium/High label spanning both is what produced the
original complaint.

---

## 8. Open definitional questions

| # | Question | Affects |
|---|---|---|
| 1 | Does the "someone answered" outcome distinguish *the customer deflecting* from *a stranger on a reassigned number*? If it is one undifferentiated code, that cell collapses and `avoiding` / `skip` inherit the ambiguity | A2 states, T12 |
| 2 | Is `skip` the right label for the audience? Native to collections, opaque to risk heads. Surfaces naturally at PV5 | A2 naming, T16 |
| 3 | Can `chronic_marginal` evidence its own name once duration features are recruited, or should it be renamed to something the window carries? | A4 §3.5, T07 |
| 4 | What is the A2 label-timing window — how recent must a contact or visit be to describe the state at `obs`? | A2, T12/T13 |
