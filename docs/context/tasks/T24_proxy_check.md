# T24 — Proxy check on shipped axes

**Goal.** Verify that no axis output acts as a proxy for a protected attribute, before
anything ships.

**Why (R7, compliance).** Nationality, visa/iqama status and gender are prohibited or
restricted for credit decisioning under CBUAE/SAMA consumer-protection rules. An
inferred axis can reproduce a protected attribute without ever using it as an input —
`gone` (left the country) is the highest-risk case, since departure correlates strongly
with residency status. This must be documented **before** compliance asks, not after.

**Load.** `reference/domain_and_decisions.md §7` (constraint C3). Outputs of T18, T23.

## Steps

1. For each shipping axis output (A4 class, A2 state, and the continuous features):
   train a model to predict each protected/restricted attribute from the axis output
   alone.
2. Report separability (AUC / accuracy) against the base-rate baseline.
3. Repeat with the axis's underlying features, not just the class — a class may look
   clean while a component feature does not.
4. Where separability is high, identify which features drive it and whether the axis
   survives without them.

## Decision rule

- **High separability** → do not ship pending compliance review. Prepare the evidence
  pack: what predicts what, how strongly, and whether a reduced feature set removes it.
- **Low separability** → document the result as the pre-emptive evidence and ship.
- Either way, this check is **repeated whenever an axis definition changes**.

## Done when

Separability results per axis per attribute logged in `RESULTS.md`, a shareable
summary written for compliance, and any blocked axis marked in `TASKS.md` with the
reason.
