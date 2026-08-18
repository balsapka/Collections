# T14 — A2 gates PV1–PV4

**Track A** · **Depends:** T12 (or T13) · **PROD round trip:** Yes

**Goal.** Put the locatability axis through the same four gates as A4.

**Why.** Locatability feels obviously useful, which is exactly why it should be tested
rather than assumed. In particular it may be substantially predictable from existing
recency features (days since last payment already encodes some of "we cannot reach
them"), which would make it a partial repackaging.

**Load.** `reference/snippet_contract.md`; Outputs of T12 (or T13). Gate definitions below; T08/T09/T10 for the
equivalent A4 procedure.

## PV1 — Buildability
Coverage and state distribution per segment. **Pass:** assignable for ≥ ~80%; no state
below ~5% or above ~60%; `unknown` not dominant.

## PV2 — Novelty  ·  the gate that matters
Predict the state from the existing feature set (state features + production features).
**Pass:** poorly predicted. **Fail:** well predicted — likely because recency features
already encode contactability. On failure, isolate the states that *were* novel
(`gone` is the most likely to survive, since departure signatures are not in the
current feature set) and keep only those.

## PV3 — Outcome separation
Realised cure/recovery rate and mean recovered AED by state, within segment.
**Pass:** extreme-state ratio ≥ ~1.5×, stable across two periods. Expect `gone` to be
near-zero recovery — if it is not, the state is mis-assigned.

## PV4 — Incremental lift
Production model vs production + A2, on the R4 metric set, within segment. Also test
A4 + A2 together — they may be complementary or redundant, and that determines whether
both ship.

## Done when

PASS/FAIL per gate with numbers logged in `RESULTS.md`; explicit statement of which
states ship and whether A2 ships as a model input, a segmentation, or both.
