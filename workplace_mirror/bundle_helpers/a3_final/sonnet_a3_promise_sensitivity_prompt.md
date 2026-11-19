# UAT Sonnet prompt: A3 Dimension A — kept-rate floor and recency of broken promises (sensitivity)

Paste everything below the line into the UAT Sonnet session.

---

Goal
A3's Dimension A (promises kept) now reads: Kept = at least 2 concluded events and 80% or more kept (3
points); Partly kept = at least one kept event, short of Kept (2); Promised = an event in the 12 months,
none kept (1); No promise (0). The old 40% floor (below it = Broken) was dropped with Broken on
2026-11-18 after one test (Broken rows with a kept event vs Partly kept). Neither the 40% nor any other
floor was ever chosen on payment outcomes, and the recency of broken promises was never tested on
outcomes. A customer who kept 1 of 10 promises should not need to read as Partly kept. We want the
rule for Dimension A that the data supports, and that holds across all four model_ids:
1. at what kept rate (if any) a customer with a kept event pays like Promised rather than Partly kept;
2. whether recent broken promises (the last event, the last few, a broken streak at the end, time since
   the last kept event) tell us more about future payment than the 12-month rate;
3. whether the Kept rule (2 concluded, 80%) is right.

Decided, to follow
- Everything else in A3 is fixed: events (D-A3-29, a payment on the event day counts), deadlines
  (D-A3-28), 12-month window, points of B and C, refusal, state cut-offs (High from 4, Moderate from 2).
  Only the Dimension A level rule is under test. No Broken level comes back: a customer below a floor
  or caught by a recency rule gets Promised (1 point).
- model_ids: all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus).
- Unit: (account, month end), month ends 2026-01-31 .. 2026-05-31 of crx_<p>_obs_base (3 full months of
  outcome after each). Report n account-months and n distinct accounts in every table.
- Events: crx_<p>_a3_promise_events as persisted (final rules). An event counts at a month end when its
  day is in the 12 months up to the month end; it is concluded when its cutoff is on or before the month
  end; outcome = its judged result (paid = kept; partial and none = not kept). Order events by day. Check
  that your per-month counts reproduce commitments_concluded / commitments_kept on
  crx_<p>_a3_payment_credibility for the same month ends (report mismatches; expected 0).
- Outcome: paid_due (3 months after the month end), exactly as the A3 results run computes it from
  crx_<p>_a3_dues and crx_<p>_a3_payments; paid_any beside it.
- B level, C level, refusal flag and state come from crx_<p>_a3_payment_credibility at the same month end.

Part S1 — kept rate by number of concluded events
S1.1 Rows with at least one concluded event: concluded count (1 / 2 / 3–4 / 5–9 / 10+) × kept rate
     (0 / >0–20% / 20–40% / 40–60% / 60–80% / 80–100%): n, paid_due, paid_any. Beside them the reference
     rows: pending only (no concluded event yet), and no event.
S1.2 The same kept-rate bins within each B level (regular / some / none): promises and payments move
     together, so the floor must hold once payments are held fixed.

Part S2 — recency
S2.1 Among rows with at least one kept event: last concluded event kept vs not kept; pattern of the last
     2 and last 3 concluded events (e.g. kept-broken, broken-broken); broken streak at the end (0 / 1 / 2 /
     3 / 4+); days from the last kept event to the month end (0–30 / 31–90 / 91–180 / 181–365).
S2.2 Does recency add beyond the rate: S2.1's last-event and streak splits within the kept-rate bins of
     S1.1 (collapsed to <40% / 40–80% / ≥80% if cells get thin) and within B level.

Part S3 — candidate rules (same points and state cut-offs; only Dimension A changes)
R0  current.
R1  kept-rate floor f ∈ {20%, 30%, 40%, 50%}: a kept event but rate below f → Promised.
R2  last concluded event not kept, and rate below 80% → Promised.
R3  broken streak at the end ≥ k, k ∈ {2, 3} → Promised.
R4  R1 at 40% plus R3 at k = 2 (and any other combination S1 / S2 point to; say why).
R5  Kept variants: 70% / 90% instead of 80%; "2 concluded" vs "3 concluded"; last 2 events kept.
For each rule and model_id: Dimension A level mix; paid_due per level (is Kept > Partly kept > Promised >
No promise?); state mix; state AUC on paid_due, all rows and per DPD band; rows whose level and whose
state change vs R0, and their paid_due. AUC difference vs R0 with a 95% interval from an account-level
bootstrap (resample accounts, 200 draws) where it runs in reasonable time; otherwise say so.

Part S4 — universal
One table: per rule, in how many of the four model_ids and of the DPD bands (i) the level order holds and
(ii) the state AUC is not below R0 by more than 0.002.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids in any output; cells under 10 as "<10". A part that fails records
its error and the rest still runs. Performance: literal date filters right after catalog.load; one pass
per table group over a localCheckpoint of the joined frame; broadcast small tables; no row-level
collect; AUCs from (score, outcome) counts; the bootstrap on aggregated (account, score, outcome) rows.
New tracked folder tmp_validation/a3_promise_sensitivity/, commit only that. No pipeline, catalog or
registry change.

Deliverables
1. Snippet + README_a3_promise_sensitivity.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_a3_promise_sensitivity_<model_id>.md.
3. Back in UAT: summary_a3_promise_sensitivity.md, which the user pastes back to Claude.
   - All four model_ids together, one markdown table per numbered table with a model_id column, numbers
     only inside tables; under 300 lines.
   - End with one verdict line each: is there a kept-rate floor below which customers pay like Promised
     in all four model_ids, and where (S1); does it hold within B level (S1.2); does recency add beyond
     the rate (S2.2); which candidate rule is simplest while holding the level order everywhere and
     costing no AUC (S3, S4); should the Kept rule change (R5); the count check against the persisted
     commitments columns.
