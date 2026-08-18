# Collections Modelling — Session Entry Point

**Audience:** a Claude Code session working in the bank's workplace repo.
**Design:** one small task per session. Load this file + `TASKS.md` + the single task
card. Load reference sections **only** when the card names them.

The workplace repo has its own `CLAUDE.md` and docs for the codebase, pipelines
(staging → feature layers, LightGBM modelling, reporting) and work done so far.
**Precedence:** repo facts (what exists, names, patterns) come from the workplace docs;
modelling strategy, decisions and the task queue come from this pack.

## Environment — read this before anything else

**This session runs in UAT and has NO data access.** You cannot query, profile, or
verify anything against real data. Any question about the data is answered by writing
a **snippet the user runs in PROD** and pastes back.

- Load `reference/snippet_contract.md` whenever a task touches data. It has the
  template and rules.
- **Snippets are modules under `docs/context/snippets/`** named `t##_<short_name>.py`,
  each exposing **`main(catalog, ...)`** — the user runs them in a Kedro notebook where
  `catalog` already exists. No session bootstrap, no `__main__` block.
- **Scope before anything else (R20).** Spine datasets first (they already carry the
  spine id, dates and delinquency info, and are scoped by construction), then the
  `model_id` scope datasets, then scoped raw. **Never an unscoped raw scan** — these
  are billion-row tables and we want a small population.
- Snippets use `catalog.load()` only, are read-only by default, aggregate in Spark and
  collect only small results, and print between `=== T## OUTPUT START/END ===` markers.
- **Two return channels.** Small results (≲30 lines) are pasted back. Anything larger
  or structured is **written to `results/` as JSON**, which the user commits and pushes
  from PROD and pulls in UAT — the next session reads the file directly. Always print a
  headline summary too, so the user can skip the commit when it is not worth it.
- **Aggregates only in results files.** Portfolio-level aggregates in the repo are
  approved; customer-identifiable or row-level data is not — no account ids, CIFs,
  names, contact details or individual transactions.
- **Never fabricate results.** If output has not come back, the task is not done. Do
  not write plausible numbers into `RESULTS.md` or reason as if a query had run.

## Reversibility — this is an experiment, not a rewrite

The current solution is not ideal, but **it works end to end**: data pipelines run,
modelling pipelines run, reports are produced. That working system must keep working
whatever happens to this programme, and if the strategy does not pan out, everything
built here must be removable without a trace.

**Isolation:** work on a dedicated branch. Additive-only discipline (R18) is what makes
that branch *safe to merge*, so it does not have to be long-lived — merge early rather
than accumulating a divergent branch. If the user chooses to stay on their active
development branch instead, R18 alone still protects the running system.

**The acid test for every change:** *if I deleted every file I added and every catalog
entry I added, would the repo behave exactly as it does today?* If not, something was
modified rather than added — undo it and find the additive path.

**Side effect worth exploiting:** because old and new coexist, they can be run in
parallel on the same population and compared directly. That comparison is the evidence
that the new approach is better — or the early warning that it is not.

## Session protocol

1. Read this file and `TASKS.md`.
2. Take the task the user names, or the first `todo` whose dependencies are `done`.
3. Open its card in `tasks/`. Load only the reference sections the card lists.
4. Do that one task, in whichever leg it is at:
   - **Leg A** — write the snippet (diagnostics) or the pipeline code plus its
     validation snippet (build tasks). Hand it over. Set status `in-progress`.
   - **Leg B** — the user pastes PROD output back. Interpret it, apply the card's
     decision rule explicitly, log it, and set status `done`.
   Do not start the next task in either leg.
5. Append to `RESULTS.md`: headline number, decision taken, and the raw returned
   output under "Returned outputs" so no later session needs a re-run.
6. If a result changes a plan assumption, note it in `RESULTS.md` under "Proposed
   amendments" — do not silently re-plan.

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
- **R18 — Additive only. Never modify existing pipelines, logic or assets.**
  - **Never:** change an existing node function, repoint or alter an existing catalog
    entry, add columns to an existing table, change an existing model config, or
    change an existing report.
  - **Always:** new modules, new nodes, new pipelines registered under new names, new
    catalog entries with new paths, new output tables, new reports beside the old.
  - **Isolate new assets so they can be deleted in one sweep.** For code: a dedicated
    module directory and a dedicated catalog file (`conf/base/catalog_<name>.yml`) —
    deletion is `rm -r` plus one file. For physical paths and warehouse tables, where
    that structure is not available: a single agreed prefix, default `crx_`
    (collections-risk experimental). Use the repo's own convention for experimental
    assets if one exists. **CONFIRM the marker with the user before first use.**
  - Record every new asset in the manifest in `RESULTS.md` as you create it. The
    abandon path must stay mechanical, not archaeological.
  - Adding a *new* label table is additive; adding columns to the existing one is not.
    Prefer a new table joined on keys.
- **R19 — Report defects, do not fix them.** If a diagnostic finds a problem in the
  existing system (leakage, a contaminated label, a broken feature), **report it and
  stop**. Do not repair it as part of this work — that is a modification to a running
  system and a separate decision for the user, with its own testing and timing. Log it
  in `RESULTS.md` under "Defects found in existing system" and continue the task.
- **R20 — Scope first, always.** Filtering to the target population is the *first*
  operation in any data code, before any other logic. Prefer the spine datasets (they
  carry spine id, dates and delinquency info and are scoped by construction) — they
  often answer a question with no raw table touched at all. Otherwise semi-join raw
  down to the `model_id` scope datasets (`scope_accounts`, `scope_cifs` or whatever
  they are actually called — discover, do not guess, R9) before anything else. An
  unscoped scan of a raw table is a **defect**.
- **R16 — No data access in UAT.** Never write code that assumes you can execute it,
  and never state a data fact you have not been shown. Data questions are answered by
  a PROD snippet per `reference/snippet_contract.md`. A task whose snippet has not been
  run is `in-progress`, not `done`.
- **R17 — Build tasks ship a validation snippet.** Pipeline code is written blind, so
  every build task also produces a snippet that checks it in PROD (row counts, null
  rates, the card's invariant tests, a small output sample). Not done until that comes
  back clean.
- **R14 — Reuse before build.** The repo has full end-to-end pipelines for most
  domains and hundreds of existing features. **Before implementing any feature, search
  the repo for an existing equivalent or near-equivalent** (see the reuse map from
  T01). Use it if it matches, adapt it if it nearly matches, and build new only when
  nothing does — recording which of the three applied. Rebuilding a feature that
  already existed is a defect. This applies to feature logic, spell/window helpers,
  evaluation code and reporting alike.
- **R15 — Data granularity differs by source.** CC has payment, balance and
  utilisation tables plus transaction history — rich, sub-monthly. **Loans have only
  month-end snapshots**, so intra-month timing features are not portable to them
  (T25). Never assume a CC feature has a loan equivalent; state the grain a feature
  needs and check it exists for that unit.

## Files

| Path | Load when |
|---|---|
| `00_START_HERE.md` | Every session |
| `TASKS.md` | Every session — the queue |
| `tasks/T##_*.md` | The one task being worked |
| `reference/domain_and_decisions.md` | When a card names a section (segments, data truths, S/X/O lists) |
| `reference/current_state.md` | When a card names it (model diagnosis, contamination risks) |
| `reference/snippet_contract.md` | **Whenever a task touches data** — PROD snippet template, return channels, governance |
| `snippets/` | Generated PROD snippets — modules with `main(catalog)`, run in a Kedro notebook |
| `results/` | PROD run outputs (JSON), pushed from PROD and pulled into UAT |
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
