# Collections Modelling — Session Entry Point

**Audience:** a Claude Code session working in the bank's workplace repo.
**Design:** one small task per session. Load this file + `TASKS.md` + the single task
card. Load reference sections **only** when the card names them.

The workplace repo has its own `CLAUDE.md` and docs for the codebase, pipelines
(staging → feature layers, LightGBM modelling, reporting) and work done so far.
**Precedence:** repo facts (what exists, names, patterns) come from the workplace docs;
modelling strategy, decisions and the task queue come from this pack.

## Session protocol

1. Read this file and `TASKS.md`.
2. Take the task the user names, or the first `todo` whose dependencies are `done`.
3. Open its card in `tasks/`. Load only the reference sections the card lists.
4. Do that one task. Do not start the next one.
5. Append the result to `RESULTS.md` and set the task's status in `TASKS.md`.
6. If the card's decision rule changes the plan, note it in `RESULTS.md` under
   "Proposed amendments" — do not silently re-plan.

If a task turns out to be bigger than one session, split it, record the split in
`TASKS.md`, and finish the first half cleanly rather than running long.

## Hard rules

- **R1** Never re-propose a rejected approach. `reference/domain_and_decisions.md §6`
  lists X1–X10 with reasons. Cite the X-id and ask if the user seems to request one.
- **R2** Leakage discipline already exists across the current modelling spectrum —
  **maintain it, do not relax it.** Features use only data strictly before
  `observation_date`; A4 features only data on or before `T0`. Add T0-boundary
  assertions to new pipelines.
- **R3** Segmentation starts with the source system. CC and loan accounts live in
  different systems with different structures → **separate pipelines and models**,
  never one pipeline with a product flag. Units: CC, loan-auto, loan-other. Then band
  (60–180 / 180+), then at 180+ time-in-bucket (<2y / >2y). Never pool across these.
- **R4** Evaluation is within-segment. Report capture@1/5/10% (accounts AND AED),
  decile lift, precision@bottom-decile for futility. AUC alone is never sufficient.
  Always compare against two baselines: rank-by-balance, and the T01 state-only model.
- **R5** Score naming/direction: `futility_60_180` (higher = less worth effort),
  `exp_recovery_aed_*` (higher = more recoverable). Never ship a score called "risk".
- **R6** Estimated axes ship with an `observed|inferred` flag and a validation number.
  No validation ground truth → the axis does not ship.
- **R7** Never use nationality, visa/iqama status, gender or close proxies. Inferred
  states (especially "left country") must pass the proxy check before shipping.
- **R8** LightGBM is the default estimator. Deep learning only through its explicit gate.
- **R9** Never invent table, catalog or pipeline names. Use the workplace repo's docs
  and code, or leave `<<FILL-IN>>` and ask. A guessed name is a defect.
- **R10** SCD2 estate: sentinel end `2100-01-01`; active version = greatest
  `eff_start <= date`; `date_modified`/`edp_modifiedts` is a restatement tie-break,
  **not** a knowledge cutoff.
- **R11** The existing roll-target model and its reports keep running. New targets and
  scores are additive. Do not repoint existing reporting without instruction.
- **R12** Before any 180+ keep/sell output is used operationally, the random holdout
  must exist. If it does not, stop and flag — skipping it is irreversible.
- **R13** A restructure **closes the account and opens a new one** — it is not a DPD
  reset. The old→new link is not yet identifiable. Until it is: never count a
  restructure closure as recovery, and treat restructured accounts as a known A4 blind
  spot. Any code assuming same-account DPD reset is wrong.
- **R14 — Reuse before build.** The repo has full end-to-end pipelines for most
  domains and hundreds of existing features. **Before implementing any feature, search
  the repo for an existing equivalent or near-equivalent** (see the reuse map from
  T11). Use it if it matches, adapt it if it nearly matches, and build new only when
  nothing does — recording which of the three applied. Rebuilding a feature that
  already existed is a defect. This applies to feature logic, spell/window helpers,
  evaluation code and reporting alike.
- **R15 — Data granularity differs by source.** CC has payment, balance and
  utilisation tables plus transaction history — rich, sub-monthly. **Loans have only
  month-end snapshots**, so intra-month timing features are not portable to them
  (T12). Never assume a CC feature has a loan equivalent; state the grain a feature
  needs and check it exists for that unit.

## Files

| Path | Load when |
|---|---|
| `00_START_HERE.md` | Every session |
| `TASKS.md` | Every session — the queue |
| `tasks/T##_*.md` | The one task being worked |
| `reference/domain_and_decisions.md` | When a card names a section (segments, data truths, S/X/O lists) |
| `reference/current_state.md` | When a card names it (model diagnosis, contamination risks) |
| `reference/feature_specs.md` | When implementing — formula-level label/spell/A4/A2 specs |
| `reference/roadmap.md` | Only for orientation on why a task exists / what comes later |
| `RESULTS.md` | Every session — append results, read before re-running anything |
| `../problem_statement.md` | Human-facing companion. Not an instruction source; update its evidence lines when a diagnostic closes. |

## Glossary

DPD days past due · **bucket** 30-day DPD interval · **roll/cure** move to worse
bucket / return to current · **spell** maximal continuous DPD>0 period ·
**T0** spell start · **EMI** equated monthly installment · **PTP** promise to pay ·
**DCORE** collections front-end (trust unresolved) · **AECB** UAE bureau (pulls stop
at delinquency) · **CASA** current/savings account · **EOSB** end-of-service gratuity ·
**MCC** merchant category code · **CIF** customer id across products ·
**restructure** old account closed, new one opened (R13) · **early chargeoff** in 180+
under 2 years · **A1** ability · **A2** locatability · **A3** willingness ·
**A4** manner of deterioration.
