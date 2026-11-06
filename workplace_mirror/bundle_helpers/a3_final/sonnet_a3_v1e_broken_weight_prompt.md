# A3: V1e, how much should a Broken promise record weigh? (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet in the same `tmp_validation/a3_v1_v4/` work. It can run in the
same PROD session as V1d and reuses V1c's instalment list. Run for cc_60_180 and rl_60_180, then paste
`summary_v1e.md` back here.

Why: today a Broken promise record scores 0 points and also fires the `broken_commitments` strong
negative. Without Dimension A the most a customer can score is 3 (Regular 2 + Clean 1), below High's 4,
so the negative always ends in Low, even for a customer who pays regularly. Thin and Broken both score 0,
so without the override a Broken record would say no more than having no promises. Proposal (2026-11-05):
Broken scores negative points and leaves the strong-negative list (refusal stays the only one). V1e
picks the weight from the outcome.

````text
Goal
Decide how a Broken promise record should count in the A3 state. Compare four variants on PROD,
aggregates only. Change no pipeline code.

Rules (A3 redesign, decided)
- Dimension A (promises), per account, from the PTP + settlement instalments as in V1c: agreements
  through prm_dcore_account_agreements, non-cancelled, window = due date in
  [max(latest spell start, obs - 12 months), obs], concluded = due on or before obs and paid or overdue
  (pending ones do not count). Level, in this order: Broken (last 3 concluded all broken, or >= 2
  concluded and kept rate < 40%), Kept (>= 2 concluded and kept rate >= 80%), Partly kept (>= 1 kept),
  else Thin. Points: Kept 2, Partly kept 1, Thin 0; Broken per variant below.
- Judge kept / broken two ways and report both side by side (the choice is still open):
  J1 DCORE instalment status (paid = kept, overdue = broken);
  J2 payments, V1c's corrected allocation (CC: card payments up to due date + 5 days; RL: total_paid in
     the due month).
- Dimension B (payments while delinquent, 61-180 rules): Regular 2 (2 of the last 3 months / cycles
  with payments >= max(one month's due, 100 AED)), Some 1 (any month / cycle >= 100 AED in the last 3),
  None 0; the window starts no earlier than the latest spell start. Dimension C (the 12 months before
  the latest spell start, paid as billed before the next statement): Clean 1 (>= 3 months due, >= 80%
  paid), else 0. Reuse the existing A3 cycle / month datasets; if you must approximate (e.g. read the
  current A3 output's B / C levels), say exactly how in the README.
- State: Unknown = Thin, B None, C no record, no negative (a Broken record is never Unknown); High from
  4 points; Moderate from 1; else Low. Refusal stays a strong negative as today (with a negative:
  Moderate if >= 4 points, else Low); no-response is gone.

Variants
  V0 today: Broken = 0 points + broken_commitments strong negative (always Low);
  V1 drop: Broken = 0 points, no negative (scores like Thin);
  V2 Broken = -1 point, no negative;
  V3 Broken = -2 points, no negative.

Part 1 - size (latest month = the month of params crx_persona.persona_end_date)
Per model and judge: Broken rows (n, % of population); Broken x B level x C level (counts); the state
distribution under V0-V3; rows that change against V0 (n, % of population, % of Broken), split by the
B / C points they carry (1 / 2 / 3).

Part 2 - outcome (an earlier month, so there is a future to observe)
Take obs = persona_end_date - 3 months, same rules. Outcome over the 3 months after obs: any payment
>= 100 AED (CC cycle / RL month), share of months with such a payment, and the DPD path at obs + 3
months (cured / improved / held / rolled, from the A4 / dpd sequences). Per model and judge, compare:
  a) Broken, by B + C points (0 / 1 / 2 / 3);
  b) Thin with the same B + C points;
  c) Moderate and Low rows that are not Broken (the reference levels).
n and rates per cell, "<10" rules apply; flag cells with n < 30.
Reading: at each B + C level, the gap between a) and b) is what Broken adds. No gap: V1. A gap that
makes a) look like the next level down: V2. Two levels down: V3. a) at every level like Low: V0.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids, cells under 10 as "<10". A part that fails records its error and
the rest still runs. Follow the V1d performance rules (instalment list built once and persisted,
literal date filters on every source right after catalog.load, broadcast join to the population, no
looped plan chains, no row-level collect, check PartitionFilters).

Deliverables
1. Snippet + README_v1e.md in tmp_validation/a3_v1_v4/, pushed from UAT.
2. The user runs it in PROD for cc_60_180 and rl_60_180 and commits results_v1e_<model_id>.md.
3. Back in UAT: summary_v1e.md, under 40 lines: Broken share and rows each variant moves, per model and
   judge; the a) / b) / c) outcome table; one paragraph recommending V0-V3 from the numbers, and whether
   the answer differs between J1 and J2.
````
