# T15 — Proxy check on shipped axes

**Track A** · **Depends:** T08, T14 · **PROD round trip:** Yes

**Goal.** Verify that no axis output acts as a proxy for a protected attribute, before
anything ships.

**Why (R7, compliance).** Nationality, visa/iqama status and gender are prohibited or
restricted for credit decisioning under CBUAE/SAMA consumer-protection rules. An
inferred axis can reproduce a protected attribute without ever using it as an input —
`gone` (left the country) is the highest-risk case, since departure correlates strongly
with residency status. This must be documented **before** compliance asks, not after.

**Load.** `reference/snippet_contract.md`; `reference/domain_and_decisions.md §7` (constraint C3). Outputs of T08, T14.

## Steps

1. For each shipping axis output (A4 class, A2 state, and the continuous features):
   train a model to predict each protected/restricted attribute from the axis output
   alone.
2. Report separability (AUC / accuracy) against the base-rate baseline.
3. Repeat with the axis's underlying features, not just the class — a class may look
   clean while a component feature does not.
   **Features borrowed from another repo get no exemption.** A departure feature reused
   from `wealth_management` or `retail.feature_space` (T06, R14) was cleared — if at all
   — for a different use case and a different population. Include every borrowed feature
   here by name, and check its *inputs* too: one built directly on nationality, visa or
   residency status fails R7 at the source, whatever its output separability looks like.
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
