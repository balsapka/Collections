# Roadmap — why the tasks exist and what gates them

Orientation only. Executable detail lives in `../TASKS.md` and the cards in
`../tasks/`. Read this when you need to know *why* a task exists or what comes after
it — not to execute.

## Shape of the programme

**Persona axes lead** (S16). They are validated on their own merits, independently of
the risk models, because the whole premise is that they carry information the current
model does not. If that premise fails it should fail early and cheaply, before a model
rebuild depends on it.

```
Phase 0   diagnostics + inventory      → what is true, what already exists
Phase P   persona axes + PV gates      → does the angle work at all?
Phase 1   revised targets              → independent; can interleave
Phase 2   decision models              → only once axes have passed their gates
Phase 3   gated extensions             → each behind an explicit trigger
```

**CC leads throughout.** Loans are separate pipelines with a different data grain
(R3, R15) and follow once the CC axes clear their gates. Loan A4 is a distinct
monthly-grain feature set, not a port.

## The persona validation ladder (PV1–PV5)

Applied per axis, per modelling unit. Cards: T18/T19/T20 for A4, T23 for A2.

| Gate | Question | Fails when |
|---|---|---|
| PV1 buildability | Can we compute it across the book? | Coverage thin, or one class swamps the rest |
| **PV2 novelty** | Is it anything the existing features don't already contain? | The 24-month DPD string predicts it — it is a repackaging |
| PV3 outcome separation | Do the classes differ in what actually happens? | Outcomes flat across classes |
| PV4 incremental lift | Does it improve on the current model? | No gain on capture@k or precision@bottom |
| PV5 action distinctness | Does each class imply a different action? | Two classes map to the same action → merge |

**PV2 is the gate that matters.** T01 established that the current model is
substantially a function of one 24-month DPD vector; an axis reconstructible from that
vector will fail in exactly the way the current score fails. An axis may pass every
other gate and still be worthless if it fails this one.

An axis can also pass PV1–PV3 but fail PV4 — in which case it ships as a
*segmentation* (useful for routing work) but not as a model input. Record the
distinction rather than dropping it.

## Why each Phase 0 item exists

- **T01** (closed) — established the tautology; it is the reason the programme is
  shaped around novelty rather than tuning.
- **T02–T04** — restructures close accounts and open new ones, which may be inflating
  recorded recovery and blinds A4 on successor accounts. Everything label-related
  waits on T02.
- **T05** — sets how far back A4 can actually look.
- **T06** — two specific admissibility risks in current top features.
- **T07/T08** — segment economics and whether 180+ skill is really cohort membership.
- **T09** — decides whether estimating ability (A1) is worth building.
- **T10** — DCORE trust gates the willingness axis entirely and the supervised
  locatability variant.
- **T11** — the reuse map. Highest leverage item before any build (R14).
- **T12** — loan grain feasibility; has lead time if data sourcing must be triggered.

## What comes after the gates

Once axes pass PV4: retrain decision models per segment with the revised labels, extend
reporting to the R4 metric set, then the deployment gates — orthogonality of persona
against score deciles, the proxy check, the priced cutoff curve, and the descriptive
action/outcome crosstab.

## Gated extensions

| Item | Trigger |
|---|---|
| Sequence encoder for A4 | Cheap trajectory features plateau *with* measurable headroom, and T05 confirms event-level depth. Embeddings feed LightGBM — features, not decisions, to keep the model-risk burden light |
| Auto / secured track | T07 shows auto behaves differently enough to justify it |
| A1 ability proxy | T09 shows a real CASA-holder vs card-only gap |
| A3 willingness | T10 clears DCORE — plus T03/T04, since restructure participation is a strong DCORE-free willingness signal |
| Loan A4 | CC axes clear their gates; shape decided by T12 |
| Aged-book trigger monitoring | Bureau monitoring feed obtained (permissible purpose + cost cleared) |

## Standing constraint

The permanent ~1% random holdout below the 180+ cutoff (R12) blocks *deployment*, not
build — but it cannot be retrofitted once accounts start being sold. Raise it with the
business early regardless of where the build has reached.
