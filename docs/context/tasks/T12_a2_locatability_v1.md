# T12 — A2 locatability (derivation)

**Track A** · **Depends:** T03b, T01, T06 · **PROD round trip:** Yes — validation snippet

**Goal.** Assign each delinquent account a contact state — `reachable`, `avoiding`, `skip`,
`gone`, `unknown` — by crossing **contact-outcome status** against **presence evidence**
(`feature_specs §4.0`).

**Why.** This is the axis with the cleanest action mapping: `gone` means field visits are
wasted, `skip` means tracing works and is the cheapest state to fix, `avoiding` means the
customer is reachable and choosing not to pay (an escalation case, not a locating one).
Plain-language definitions in `personas.md §4`.

**Why derived rather than trained (S18).** Field visits are dispatched *because* contact
already failed, so a model trained on visited accounts learns
P(state | features, already-failed-contact) and cannot be applied to the book. `reachable`
is near-absent from that sample. The cross in `§4.0` resolves the states without any visit
label; visits adjudicate one cell and validate `gone` precision (T13).

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §4` (the derivation
matrix, signals, rules and guards); `personas.md §4`. T01 reuse map; T06's departure features.

## Steps

1. **Reuse first (R14):** the departure signals overlap heavily with T06's output and the
   features it sourced from the workspace (`retail.feature_space`, `wealth_management`, and
   the working repo's own feature layer). Take T06's screened set rather than recomputing —
   and if T06 rejected a candidate on coverage, anchoring or protected inputs, it stays
   rejected here; do not re-adopt it by another route. Check the same repos for
   **contactability** logic specifically (address quality, returned-mail, phone-reachability,
   KYC-refresh failures) — A2 is a contact-state problem, and that flavour of feature may
   exist there even where departure does not.
2. **Resolve the contact-outcome code list first (O15).** Do not build against the assumed
   vocabulary in `§4.1b` — get the actual codes (R9). The decisive question: does "answered
   but no meaningful conversation" distinguish *the customer deflecting* from *a stranger on
   a reassigned number*? If it is one undifferentiated code, that row of the matrix collapses
   and `avoiding` / `skip` both inherit the ambiguity. Record the answer either way.
3. Build the presence signals in `§4.1a`, including `observable_channel_cnt`.
4. Build the attempt-normalised contact signals in `§4.1b` — rates over `contact_attempts_n`,
   never raw flags. Include these **only** if T11 cleared DCORE.
5. Apply the `§4.2` derivation rules.
6. **Implement all three guards in `§4.4`** — they are not optional polish:
   - `gone` only on a positive departure trail, never on absence (§4.4a)
   - `unknown` below τ_a attempts; `unknown` below τ_c observable channels (§4.4b)
   - the labelling window (§4.4c) — fix the number, do not leave "recent" undefined
7. Emit state + confidence + `observed|inferred` + the guard columns (R6, §4.6).

## Important limitations to respect

**Without trustworthy DCORE**, channel status is unavailable and the axis degrades to three
states (`gone` / `active-but-not-paying` / `unknown`). Say so in the output schema and
documentation. Do not fabricate a fourth state to make the grid look complete.

**Silence is not departure.** ~80% of the delinquent CC book is card-only, and once the card
is blocked there may be no channel left to observe presence on. For those accounts, absence
of presence evidence measures our blindness, not their location — and they are exactly the
population the axis exists to sort. Report the `unknown` share driven by §4.4a separately
from the share driven by §4.4b; they mean different things and have different fixes.

## Done when

State assigned across the CC delinquent book with confidence and provenance flags; state
distribution per segment logged in `RESULTS.md`, **with the `unknown` share broken down by
which guard triggered it**; O15 answered; face-validity table produced (do the states differ
in observable behaviour in the expected direction?); the DCORE-dependent portion clearly
marked as included or excluded.
