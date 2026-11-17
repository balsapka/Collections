# UC1 call-transcript signals in the persona framework: proposed structure

> **Superseded for the built logic by `uc1_stated_block.md`** (bundle 26, 2026-11-17: the
> as-built mapping, kept / left-out signals and the agenda for integrating the full UC1 delivery).
> This note predates the timelines handoff; its §10 parked ideas still stand.

Answer to the UC1 ideation brief (`uc1_ideation_prompt.md`), fourth version, 2026-11-16. Directions
from the user:
- **A1–A4 and their states are fixed and are not touched.**
- UC1 is condensed into its own structure beside them.
- **We take what the UC1 team delivers as it is.** Extraction, conflict rules and the handling of a
  customer's signals over time are theirs; we do not build a parallel version and do not ask them
  for changes.

Sources: the UC1 data knowledge base (`uc1_data_kb.md`, cited as KB §n). Nothing here is built or
measured. `SAMPLE` = rests on a number from the 8% sample; `ASSUMPTION` = my choice, not verified.

## 1. The structure in short

| Step | What | Owner |
|---|---|---|
| Extraction, conflict resolution, aggregation over time | per customer and observation date: each signal level detected or not, with a confidence | UC1 team |
| **Condensation** | their fields mapped to two stated axes and two flags (about 10 columns) | ours |
| **Persona master** | A1–A4 as the persona key, the stated block beside them | ours |

Our whole job is a mapping from their delivery table and a join. No parser, no time rules.

**The stated block:**

| Piece | Question | Pairs with | States / values |
|---|---|---|---|
| **A5 Stated ability** | Can they pay, by their own account? | A1 ability (observed) | Able · Partly able · Unable |
| **A6 Stated intent** | What do they say they will do? | A3 credibility (observed) | Firm plan · Open intent · Refuses |
| **Open issues** (flags) | Is something waiting on the bank? | none | dispute (type) · relief request |

Both axes also have **Not stated** (the customer has transcripts, this signal is not detected) and
**No conversation** (no transcripts).

## 2. What they deliver (as far as the KB shows)

The target table (`data/input/UC1/output_schema.md` in the workplace; **not seen here**), KB §6:
- grain `(cif_id, account_id, observation_date)`, 55 fields;
- `persona`, `collection_action` (value sets due Dec 11), `SF_1..4` (our four states);
- `last_transcript_date`, `transcript_count`;
- for each level of each signal, a **detected / not detected** field and a **high / medium / low
  confidence** field: `payment_capacity`, `payment_intent`, `delinquency_reason`, `dispute`,
  `request`, `payment_period`, `repayment_specifics`, `fraudulent_customer`.

Not in the store we read today: this table and the `timelines/*` tables behind it. Only the
per-conversation extraction is there. **So nothing can be built until they deliver**; what can be
done now is the mapping below, to be finalised against the real schema.

## 3. The mapping

Several levels of one signal can be detected for a customer at once (each level has its own field),
so each axis needs one rule to pick. I use the order the UC1 team and GRR signed off for conflicts
inside a transcript (KB §6): **higher confidence first, then the more conservative level.**

### A5 Stated ability

| State | Rule |
|---|---|
| Unable / Partly able / Able | the `payment_capacity` level picked by the rule above (conservative order: none, partial, full) |
| Not stated | `transcript_count` > 0 and no capacity level detected |
| No conversation | no row, or `transcript_count` = 0 |

Columns: `a5_state`, `a5_support`, `a5_reason` (lost income · reduced income · more obligations ·
income intact: the detected `delinquency_reason` level with the highest confidence).

### A6 Stated intent

| State | Rule |
|---|---|
| Refuses | `no_payment` is the picked intent level |
| Firm plan | a paying level is picked (`payback_full`, `partial`, `with_delay`) **and** `amount_mentioned` or `date_specific` is detected |
| Open intent | a paying level is picked, neither of the two detected |
| Not stated / No conversation | as A5 |

Columns: `a6_state`, `a6_support`, `a6_scope` (full / part or later), `a6_when` (the detected
`payment_period` level).

"Concrete or not" is the cut because `payback_full` is the usual answer (45% of intent detections
against 2% `no_payment`, `SAMPLE`), so the level alone says little. `ASSUMPTION`

### Open issues

| Flag | Value |
|---|---|
| `open_dispute` | the detected dispute level (system problem · scammed · other) |
| `open_relief_request` | `request` detected. The type (restructure, settlement, deferral, waiver) only if their table carries `request_type`; the KB does not say |

### Support

`firm` = their confidence is high; `weak` = medium or low. One column per axis.

### Shared

`uc1_transcripts_n` (= `transcript_count`), `uc1_last_transcript_date`.

`fraudulent_customer` is left out (user, 2026-11-17): detected in 0 transcript rows in the sample.
Add it as a pass-through if UC1 starts detecting it.

## 4. How it fits the persona framework

- **The persona key stays A1–A4.** It is observed, covers every account, and decides allocation.
- **The stated block is a second block of the persona master**, for the reached customers. This is
  what UC1 was built for: tactics inside a group that is already assigned (KB §1). Reach is
  single-digit percent of spine rows even after full extraction (KB §8), so the block cannot be part
  of the key.
- **Each stated axis is read beside its observed twin**, never merged with it:

  | | A1 observed: able | A1 observed: not able / unknown |
  |---|---|---|
  | **A5: Able** | agrees | income we cannot see |
  | **A5: Unable** | says no, money shows yes | agrees |

  The same holds for A6 against A3: a Firm plan means more from a customer whose promises have held.
  GRR owns what each cell means for action.
- **Join.** Their table is already at account and observation date; if it comes at customer level
  instead, every account of the customer gets the same values (UC1 has no account link, KB §2).

## 5. Customers with no UC1 evidence

- **No conversation** on both axes, no flags. Never read as Unable, Refuses or "no issue".
- Nothing is filled in or modelled for them. A1–A4 are the same for everyone.
- Results always show called and uncalled customers apart, and comparisons are made among called
  customers.

## 6. What taking it as-is means

We accept their choices and do not correct for them. Three properties of the delivery decide how far
the block can be used; we **check** them and report, we do not change them:

| Property | Why it matters | If it does not hold |
|---|---|---|
| **Point in time:** a row for an observation date uses only conversations before it (R2) | Without it, past months are scored with later calls | The block is used for the latest month only, and no back-test on past months is possible |
| **Recency:** how old a detection can be and still count | A plan stated three months ago may still show as detected | A6 is read with `uc1_last_transcript_date` beside it; we add no rule |
| **Coverage:** the delivery covers the full extraction, not the 8% sample | On the sample, "No conversation" mostly means "not read yet" | The block is a pilot; no sizes are reported as population figures |

What we give up compared with the third version: validity periods by kind of signal, contact
episodes, the count of separate plan episodes, and telling "plan ran out" from "never stated". That
design stays in git history (commit of this file's third version, if committed) and is not put to
the UC1 team.

## 7. Checks on our side (after delivery)

Aggregates only, `model_id` from globals, by product and band (R3).

| # | Question | What to return |
|---|---|---|
| C1 | The three properties of §6 | Max conversation date against observation date; age of `last_transcript_date`; rows and customers against the call list |
| C2 | Sizes | Rows per A5 / A6 state and support, flags; how often several levels of one signal are detected together (how much the picking rule decides) |
| C3 | Do the states order payments? (the validation number, R6) | Payment in the month after the observation date (100 AED or more; the month's due) by state and support; called customers only. Needs C1's point-in-time to hold |
| C4 | Overlaps | A5 × A6; A5 × A1 and A6 × A3 with payment rates; Cramér's V against A1–A4 |
| C5 | The key | Join rate of their `cif_id` / `account_id` to the obs base |

States that pay alike are merged; `weak` rows that order nothing go to Not stated. Those are changes
to our mapping, not to their data.

## 8. Alternatives considered and rejected

| Alternative | Why not |
|---|---|
| Our own parser and time layer on the per-conversation table (third version) | The user: no parallel version, no interference with UC1 |
| Pass their ~45 signal fields into the master unchanged | No reduction; the point of the exercise |
| One combined stated axis | Capacity and intent are defined independently (`none` with `payback_full` is valid, KB §4.1); merge only if C4 says so |
| A third axis for dispute / request | Not mutually exclusive; the type decides the action |
| Most recent level instead of confidence-then-conservative | Their table does not say which detected level is newer |
| Clustering or MCA for the states | Already rejected as an axis |
| The stated block inside the persona key | Single-digit reach |
| Filling states for customers without calls | Rejected already; the conditional-label trap |

## 9. Needed before this can be finalised

1. The delivery schema (`data/input/UC1/output_schema.md`) as an `.md` or photo: exact field names,
   whether `request_type` is carried, the grain, and how "not detected" differs from "no transcript".
2. The delivery itself in a store we can read.

## 10. Parked: feeding A1–A4 later

Out of scope now (user, 2026-11-16): an A6 plan as an A3 promise event; A6 Refuses beside A3's
refusal rule; A5 for A1 Unknown customers who state an income elsewhere; `open_dispute` for A3's
dispute column on rl_60_180; a Genesys conversation as a contact for A2.

## 11. Assumptions

1. The delivery has one detected field and one confidence field per signal level (KB §6), and
   several levels can be detected at once.
2. The picking rule: confidence, then the more conservative level.
3. A6 is cut by "concrete or not".
4. Medium confidence counts as weak support.
5. `transcript_count` = 0 or no row means No conversation.
