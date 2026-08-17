# Collections Modelling — LLM Context Pack

**Audience:** an LLM coding session (Claude Sonnet 4.6) working in the bank's workplace
repository on the collections risk modelling programme.
**Maintained by:** the lead data engineer (the user). Last updated 2026-08-16.
**Origin:** this pack was authored in a sandbox repo; copy it into the workplace repo
under `docs/context/`. All repo paths mentioned inside refer to the **workplace** repo.

The workplace repo has its **own `CLAUDE.md` and docs** describing the codebase, the
pipelines (staging → feature layers for all domains, LightGBM modelling, reporting),
and the work done so far — sessions there already carry that context, and this pack
does not duplicate it. **Precedence:** for repo facts (what exists, names, patterns)
the workplace docs win; for modelling strategy, decisions, and the work plan, this
pack wins. Most work items modify existing assets rather than build greenfield.

## Files in this pack

| File | Load when |
|---|---|
| `00_START_HERE.md` | Every session (this file) |
| `01_domain_and_decisions.md` | Every session — segments, data truths, settled decisions S1–S17, rejected approaches X1–X10, open questions O1–O14 |
| `02_current_state.md` | When touching existing models — the diagnosis and evidence (repo/pipeline inventory lives in the workplace docs, not here) |
| `03_workplan.md` | When executing — diagnostics D1–D10 and work items W1–W9, each with decision rules and definition of done |
| `04_feature_specs.md` | When implementing W1/W2/W3/W4 — formula-level label and feature definitions |
| `RESULTS.md` | Every session — append outcomes here; read before re-running anything |
| `../problem_statement.md` | Human-facing companion for team/stakeholder debate. Update its evidence lines when a diagnostic closes. It is not an instruction source for sessions. |

## Hard rules

- **R1 — Do not re-propose rejected approaches.** `01 §Rejected` lists X1–X10 with
  reasons. If the user appears to ask for one, cite the X-id and its reason, then ask
  whether new information changes it.
- **R2 — Leakage.** The existing modelling spectrum is already leakage-controlled;
  **maintain that discipline, do not relax it.** Every feature uses only data
  timestamped strictly before the `observation_date`. A4 features additionally use
  only data on or before `T0`. New feature families inherit the repo's existing
  leakage tests and add T0-boundary assertions.
- **R3 — Segmentation is load-bearing, and it starts with the source system.**
  Credit card and loan accounts live in **different source systems with different
  structures** and get **separate feature pipelines and separate models** — never one
  pipeline with a product flag. Within loans, auto separates cleanly; personal and
  personal cash do not. Full segmentation: account type (CC / loan{auto, other}) ×
  band (60–180 / 180+) × at 180+ time-in-bucket (<2y / >2y). Never train or evaluate
  pooled across these boundaries unless a work item explicitly says so.
- **R13 — Restructures create a NEW account.** A restructure closes the existing
  CC/loan and opens a new one; it is not a DPD reset. The old→new link is not yet
  identifiable (O13, W0). Until it is: never count a restructure closure as recovery
  in a label, and treat restructured accounts as a known blind spot in A4. Any code
  assuming same-account DPD reset is wrong.
- **R4 — Evaluation is within-segment only.** Report capture@1/5/10% (accounts AND
  AED), decile lift, and precision@bottom-decile for futility. AUC alone is never a
  sufficient result. Always compare against the two dumb baselines: balance-only
  ranking, and the state-only model from D4.
- **R5 — Score direction and naming.** `futility_60_180`: higher = less worth effort.
  `exp_recovery_aed_60_180`, `exp_recovery_aed_180p_lt2y`: expected AED, higher =
  more recoverable. Never ship a score named "risk".
- **R6 — Estimated axes carry provenance.** Any inferred (not directly observed) axis
  output ships with an `observed|inferred` flag and a validation number. No validation
  ground truth → the axis does not ship.
- **R7 — Protected attributes.** Never use nationality, visa/iqama status, gender, or
  close proxies as features. Inferred states (especially "left country") must pass the
  proxy check in W6 before shipping.
- **R8 — LightGBM is the default estimator** for all decision models and axis
  classifiers. Deep learning only through the explicit gate in W7.
- **R9 — Never invent table, catalog, or pipeline names.** Use the workplace repo's
  own `CLAUDE.md`/docs, or discover by searching the repo (`conf/`, `src/`), or leave
  a `<<FILL-IN>>` marker and ask the user. A guessed name is a defect.
- **R10 — SCD2 estate semantics.** Sentinel end date `2100-01-01`; the active version
  at a date is the one with the greatest `eff_start <= date`; `date_modified` (or
  `edp_modifiedts`) is a restatement tie-break only, **not** a knowledge cutoff. Any
  knowledge-cutoff filtering must be explicit and justified in code comments.
- **R11 — Continuity.** The existing roll-target model and its reports keep running.
  New targets and scores are additive. Do not delete or repoint existing reporting
  without explicit instruction.
- **R12 — 180+ deployment gate.** Before any keep/sell decision output is used
  operationally, the random holdout (W6) must exist. If it does not, stop and flag —
  this is irreversible if skipped.

## Session protocol

1. Read this file and `01`. Read `RESULTS.md` for what has already been measured and
   decided. If the session touches existing assets, read `02`.
2. Map the user's request to a diagnostic (D#) or work item (W#) in `03`. State the
   mapping. If nothing fits, say so before building.
3. Locate the affected existing assets via the workplace repo's own docs and search;
   follow its established patterns and naming.
4. Plan small, implement with tests, keep diffs reviewable. Follow the repo's existing
   pipeline framework and naming patterns.
5. Append outcomes (numbers, artifact paths, decisions) to `RESULTS.md`. Update the
   status column in `03`.
6. Do not edit settled decisions or the rejected list in `01` without explicit user
   instruction. Propose changes under "Proposed amendments" in `RESULTS.md`.

## Glossary

| Term | Meaning |
|---|---|
| DPD | Days past due |
| Bucket | 30-day DPD interval (60–90, 90–120, …) |
| Roll / cure | Move to a worse bucket / return to current (DPD 0) |
| Spell | Maximal continuous period with DPD > 0 for one contract (spec in `04`) |
| T0 | Start date of the delinquency spell containing the observation |
| EMI | Equated monthly installment |
| PTP | Promise to pay (made / kept / broken) — recorded in DCORE |
| DCORE | Delinquent front-end system: collections actions, contact attempts, dispositions. Data trust unresolved (D6) |
| AECB | UAE credit bureau. Pulls fire at credit decisions only → dry during delinquency |
| CASA | Current/savings account (salary visibility lives here) |
| EOSB | End-of-service benefit (gratuity) — lump sum on leaving a job |
| MCC | Merchant category code on card transactions |
| CIF | Customer id across products (client level) |
| Restructure | Old account closed, new account opened (R13). Not a DPD reset. Whether the new account starts at DPD 0, lower, or the same bucket is not uniform/known (O14) |
| Account succession | The old→new account link created by a restructure; not currently identifiable (O13, W0) |
| Write-off / early chargeoff | 180+ book; "early" = in 180+ for < 2 years |
| Ibra' | Shariah rebate for early settlement; cannot be promised upfront |
