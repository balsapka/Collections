# UAT Sonnet prompt: A2 reachability, what a confirmed contact rests on

Paste everything below the line into the UAT Sonnet session. All four model_ids, cc_60_180 first.

---

Goal
A2 counts a "confirmed contact" as an inbound call, an outbound call in category SUC, or a result in
`RIGHT_PARTY_CONTACT` (`crx_persona/a2_locatability/signals.py` `_dcore_days`, codes in `_dcore_codes.py`). The UC1
RPC check (`tmp_validation/uc1_rpc_check/`, README has the class of every result name) found that only ~30% of
right-party days record a conversation, and that at 07-31 38% of reachable cards (1,547 of 4,046) and 42% of reachable
loans are Reachable only on results that are not a conversation (mostly payment postings, which are also category
SUC). Measure what a stricter contact rule would do to A2 before anyone decides. Exploration only: no change to A2,
the pipeline, catalog or registry.

Contact classes (use the RPC check README classes, with these user decisions)
- conversation: as the README.
- E MAIL RECEIVED: counts as contact (user, 2026-11-27: it shows we can reach the customer). Keep it in every variant.
- SETTLEMENT: no verdict; run every variant with and without it.
- unclear: run with and without.
- not a conversation (payment postings: CUSTOMER MADE PAYMENT, ACCOUNT PAID, PARTIALLY PAID; CUSTOMER BEHAVIOUR
  labels; anything else the README puts there apart from E MAIL RECEIVED): dropped in the strict variants, from
  BOTH paths (the right-party list and the SUC-category path: a payment posting in category SUC is not a contact).
- inbound calls and SUC calls outside the list: keep as today, but tag them so their share is visible.

Variants (config block at the top, so names can move between classes without code changes)
- V0 today's rule (must reproduce the A2 output exactly: tie-out).
- V1 strict: conversation + E MAIL RECEIVED + unclear + inbound + other SUC calls; SETTLEMENT kept.
- V1s: V1 without SETTLEMENT.
- V2: V1 without unclear. V2s: V2 without SETTLEMENT.
Everything else in A2 stays as signed off: window W, gone dark (3 failed attempt dates, 6 at 180+, "no contact
since"), ignored codes, location rules, deceased. Note that a dropped contact can also stop resetting gone dark, so
some accounts may move to Non-Reachable, not only to Unknown.

Questions
Q1 Basis flag. For every account Reachable under V0 at the latest month end (and at 07-31): `reachable_basis` = the
   best contact class in W: conversation / e-mail only / unclear only / inbound or other SUC only / settlement only /
   not-a-conversation only. Shares per model_id, cards vs loans.
Q2 Impact. V0 vs each variant: crosstab of `reachability_state` and of `a2_state` (10 values), counts and row %;
   movers split into → Unknown (by `reachability_unknown_reason`) and → Non-Reachable; the change in each state's
   share. Also how many persona keys (A1–A4) change.
Q3 Does the stricter rule separate payers better? At month ends with outcomes available (one with 3 months of
   outcomes, plus 07-31 with 1 month; say which), the outcome the A2 workbook's Results sheet uses (payment in the
   next 1 / 3 months, money collected; reuse its code, name it). Per variant: payment rate by reachability state;
   the movers' rate against those staying Reachable, against Unknown and against Non-Reachable (with 95% intervals);
   AUC / rank order of the three states per variant.
Q4 Overlap with other axes. For the movers: share with a payment or an A3 promise event in W (does A2 today partly
   count what A3 and deterioration already measure?), and their A3 state distribution against the stayers'.

Rules
- Loading: `catalog.load` only. Reuse the A2 engine functions where you can (call `_dcore_days` logic with the class
  sets as parameters in the snippet; do not edit the module) and the RPC check's class table.
- Temporary catalog entries, if any, explicit (no dataset factories) in a `catalog_tmp_a2_contact.yml`; none is
  better.
- model_id = `catalog.load("params:model_id")`, in every output file name.
- Aggregates only: no account, CIF or agreement ids; result names are vocabulary and may appear; cells under 10 as
  "<10".
- A part that fails records its error; the rest still runs.
- New tracked folder `tmp_validation/a2_contact_basis/`; commit only that folder.

Deliverables
1. The snippet in `tmp_validation/a2_contact_basis/`: config block (variants as class sets, month ends, parts
   `q1,q2,q3,q4`); results per model_id (`a2_contact_basis_<model_id>.json` + `.md`) with the V0 tie-out first; a
   README with one command per model_id and the class of every result name used.
2. After the user commits the PROD results: `summary_a2_contact_basis.md`, under 120 lines:
   - a. V0 tie-out per model_id, or "all match".
   - b. Verdict in three lines: how much Reachable rests on non-conversation contacts; whether the strict rule
     separates payers better, worse or the same; SETTLEMENT and unclear: does the choice matter?
   - c. One table per model_id: state shares V0 / V1 / V1s / V2 / V2s, and movers to Unknown / Non-Reachable.
   - d. Q3 payment rates and AUC per variant; the movers' rate against the three states.
   - e. Q4 overlap with A3 / payments.
   - f. Options for the user, each with its cost: keep A2 + `reachable_basis` as a diagnostic; adopt V1 / V2;
     anything the data suggests. No recommendation on SETTLEMENT beyond what the numbers show.
   - g. What could not be computed.
