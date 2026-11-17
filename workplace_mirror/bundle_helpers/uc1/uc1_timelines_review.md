# Review: UC1 timelines handoff (`uc1_timelines_handoff.md`, cc_60_180, 2026-11-17)

Read against the stated-block proposal (`docs/context/results/uc1_integration_proposal.md`, fourth
version: two stated axes + two flags, UC1 outputs taken as-is). Section numbers are the handoff's.

## 1. What the delivery is

| Table | Grain | What it holds | Use for us |
|---|---|---|---|
| `simple_signal_aggregation` | one row per customer (5,751) | per signal **one level**: the most frequent detection over the customer's whole extracted history, ties to the more recent; `"NA"` = not detected | **the input**: the only customer-level table |
| `latest_flags` | one row per extracted conversation | `is_latest` only | none needed |
| `signal_level_conflicts` | conversation × 22 level slots | detected / not detected per slot, the conversation's resolved level | optional: counts per customer (§3, D2) |

Not carried by any of the three (§2, §9): a date, a confidence, a count, `request_type`. Legacy-format
conversations and agent remarks contribute nothing. The dated tables (`time_weighted_*`, 60-day
half-life, remarks included) exist in UC1's code but were never run and are not in the store (§2.4).

Good news:
- `cif_id` is an 8-digit string on both sides; exact join, no conversion (§5).
- The tables were written on 2026-11-16 on the full 11,920-conversation ledger: not stale (§2.1).
- The detection counts reproduce the knowledge base's (§2.5).

## 2. What this changes in the proposal

| Proposal piece | Holds? | Why |
|---|---|---|
| A5 Stated ability from capacity | **yes** | one capacity level per customer: partial 1,797 / full 1,649 / none 256 / NA 2,049 customers (`SAMPLE`) |
| A5 reason from `delinquency_reason` | **yes** | one modal level |
| A6 Stated intent: Firm plan / Open intent / Refuses | **weakens** | `repayment_specifics` is one modal string across amount, date and plan; amounts are part of the level, so two different amounts are two levels. 79% of paying-intent rows have one, so "concrete" barely splits (§6, B6) |
| Support firm / weak from confidence | **no** | no confidence in any table |
| `open_dispute` with type | **yes** | |
| `open_relief_request` with type | **no** | `request_type` is dropped; "detected" includes information / callback / escalation asks (about 40% of request detections in the knowledge base) |
| Evidence status (no conversation / not extracted / not detected) | **only with two more inputs** | the tables cannot tell "no conversation" from "not extracted" (both: no row), nor "legacy only" from "not detected" (both: all `NA`). `metadata` / `index` and the `model_version` of `extracted_signals` from the same store separate them (§4) |
| Every persona month | **no** | no date: see D1 |

The intent mix is less lopsided per customer than per detection: payback_full 2,284 / with_delay
1,143 / partial 902 / no_payment 59 customers. The reason the "concrete or not" cut was proposed (pay
in full is the usual answer) is weaker here.

## 3. Decisions for the user

**D1. Time.** `simple_signal_aggregation` is every call the customer ever had. It is point-in-time only
for 2026-07-31 and 2026-08-31 (calls end 2026-07-16; §3, B4). For 2026-03..06, 55–94% of rows rest on
a later call; for Jan / Feb no call precedes the date at all.
- (a) **Latest month only, from the table as is** *(recommended)*. Past persona months get the block
  blank. PROD scores the latest month from 2026-11 anyway. A row whose latest conversation is on or
  after the observation date is flagged, since R2 asks for strictly before.
- (b) Run UC1's own pick (`_select_aggregated_level`) on the conversations before each observation
  date. Their rule, our filter. It gives every month, but it means porting their code: a parallel copy
  that drifts when they change it.
- (c) Ask the UC1 team to run and copy `time_weighted_signal_aggregation` (dated by month end, their
  own recency method). Not run yet, includes evidence on the as-of day itself (`<=`), and asks them for
  a run, not just a copy.

  (a) now; (c) when they run it themselves.

**D2. Support.** There is no confidence column.
- (a) **Two counts per customer from `signal_level_conflicts`** *(recommended)*: conversations that
  carry the signal, and how many of them detected the published level (agreement). Descriptive only;
  the published level is not changed. Note the grid is also timeless, so it follows D1.
- (b) No support column.

**D3. A6 states.** Specifics no longer split the paying intents.
- (a) **A6 = the intent level as published, collapsed**: Pays in full / Partly or later
  (`partial`, `with_delay`) / Refuses *(recommended)*. A detail flag says whether an amount or a date
  was named in any conversation (from the grid).
- (b) Keep Firm plan / Open intent from the modal specifics (79% Firm).

**D4. Relief request.**
- (a) **A plain `request_raised` flag** *(recommended)*, typed later if UC1 ever carries
  `request_type`.
- (b) Ask the UC1 team to carry `request_type`. That is a change to their output, against the
  as-is decision.

**D5. Extra inputs.** The evidence status needs `metadata` (conversation dates, `cif_id`) and the
`model_version` of `extracted_signals`, both already in the shared store. Catalog entries for them in
`catalog_crx.yml`, same pattern as the three proposed in §8 *(recommended)*.

## 4. Other facts for the build

- **No persona output table exists in the workplace** (§8). The persona output schema (86 fields,
  `bundle_helpers/persona_output/`) is a document; fields 10–55 are the UC1 team's own uncondensed
  columns. So the stated block ships as its own dataset per `model_id` on `(account_id,
  observation_date)`, and the persona output picks it up when that table is built.
- **SF numbering is not A numbering:** SF_1 = A4, SF_2 = A2, SF_3 = A3, SF_4 = A1 (§7). The stated
  block's place in that schema is a naming choice for later.
- A1's output has no `cif_id`; join through the obs base (§8).
- The workplace branch is `feature/persona_refactor` at `3625b14d`; bundle 25 is not applied there
  yet (§8), as expected (built 2026-11-17). A UC1 bundle would take the next number and be independent
  of 25 (new files plus catalog entries only).
- Reach, cc_60_180, 2026-08: 69% of rows no conversation, 25% conversations not extracted, 1.9% a
  row with capacity `NA`, 3.6% a capacity level (`SAMPLE` for the last three).
- Not run: B4–B6 for `cc_180_plus`, `rl_60_180`, `rl_180_plus` (the prompt's model-dependent blocks;
  same snippet, `model_id` switched).

## 5. First sizes, read with care

Latest month, cc_60_180, rows with a level (B6). Counts are small and from the 8% sample; nothing here
is a result.
- Capacity `none`: 49 A1 Low, 26 Moderate, 68 Unknown, <10 High. Capacity `full`: 36 Low, 35
  Moderate, 51 Unknown.
- Intent: every level sits mostly in A3 Low, as all rows do (A3 Low is 62% of the spine). `no_payment`
  28 of ~35 in A3 Low.
