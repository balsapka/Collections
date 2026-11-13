# crx_persona code review and refactor: multi-agent workflow plan

Status: **approved 2026-11-04, Phase 0 running** (recommended answers in §10 taken, A3 included). The session that runs it reads this file,
`CLAUDE.local.md` and `DESIGN_REVIEW.md` §2, §6 and §7 first. The open questions in §10 must be
answered before Phase 0 starts.

## 1. Goal

Raise the live persona code to a standard someone can audit:
- readable;
- well designed;
- as short as clarity allows;
- docstrings only where they help;
- validated as correct and consistent across axes.

The refactor **preserves behaviour**. Any logic change it uncovers becomes a question for the user
and is never applied silently.

## 2. Scope (from the import graph and the catalog, 2026-11-04)

| Tier | What | Lines | Treatment |
|---|---|---|---|
| **L — live, review and refactor** | `_common.py`, `scoring_engine.py`, `obs_base/`, `a1_ability/` (except `b14_check.py`), `cc_a1_ability/`, `rl_a1_ability/`, `a2_locatability/`, `cc_a2_locatability/pipeline.py`, `rl_a2_locatability/pipeline.py`, `_dpd_journey/`, `cc_a4_deterioration/`, `rl_a4_deterioration/` (except `b13_check.py`), `cc_full_history/`, `rl_full_history/`, the crx part of `catalog_crx.yml` and `pipeline_registry.py` | ~3,900 | full workflow |
| **D — dead, delete rather than polish** | `cc_a2_locatability/nodes.py` + `constants.py` and `rl_a2_locatability/nodes.py` (orphaned since bundle 06; the wrappers call the engine) · `cc_departure_signature/` · `cc_payment_trajectory/` · `cc_utilisation/` (no consumer outside this T0 cluster) | ~7,000 | dead-code agent confirms each one; user approves the list (Q2) |
| **K — kept for A3, frozen** | `cc_spell/`, `rl_spell_table/`, `rl_a4_spine/`, `_spine_utils.py`, `cc_raw_extract/` (A3 reads `crx_cc_balance/billing/transactions`), plus `build_rl_depart_spine` in `rl_departure_signature/nodes.py` (`rl_a4_spine` imports it) | — | not touched; may be moved only if a deletion requires it, keeping the same behaviour |
| **A — A3, design-in (user, 2026-11-04)** | `cc_a3_payment_credibility/`, `rl_a3_payment_credibility/`, `specs/A3_credibility_spec.md` (D-A3-1..21), `bundle_helpers/a3_final/` | ~4,200 today | reviewed and redesigned; edits go to `a3_handoff.md`, see below |
| **X — out of scope** | `_dcore_codes.py` (only partly mirrored, read-only), `b13_check.py` / `b14_check.py` (removed by their cleanups), test modules (workplace Sonnet) | — | read only, for context |

`rl_departure_signature/` is deleted except `build_rl_depart_spine`. That function moves into
`rl_a4_spine/` unchanged, so A3 keeps its input until A3 is on the obs base (D-A3-1).

**A3 in the review.** The A3 rebuild (obs-base grain, anchor from the A4 engine, one method per
dimension, D-A3-1..21) is in progress in another session on `feature/persona_redesign`. Two writers
on the same files is not allowed, so:
- every agent reads the A3 spec and the A3 code;
- S1 designs the **target A3 shape** on the refactored shared layer: an `a3_credibility/` engine
  plus thin CC/RL wrappers, the same shape as A1/A2/A4. It names the shared helpers A3 needs (the
  episode anchor from `_dpd_journey`, the DCORE window, the cycle ledger) and puts them in the
  shared layer in this refactor;
- all other A3 proposals (readability, Spark, Kedro, docstrings) are reviewed and scored like any
  other, but are written to `a3_handoff.md` (diff-level, against the current A3 files) instead of
  being applied;
- the A3 session applies `a3_handoff.md` while building the A3 bundle; the new A3 then gets one
  check pass against the frozen rubrics;
- **"Fits A3 easily"** is a scored criterion for every reviewer (§4): a shared-layer change that
  makes A3 harder is a blocking objection.

## 3. Hard rules (every agent's prompt includes them verbatim)

1. **No behaviour change.**
   - Outputs must be identical: the same rows, columns, types and values.
   - A suspected bug or spec mismatch is written up as a finding (§7 format), never fixed.
2. **Decisions are not re-litigated.** Specs A1/A2, DESIGN_REVIEW §6/§7 and the "Working rules"
   and "Decided" lists in `CLAUDE.local.md` are final. Rejected approaches X1–X10 in
   `docs/context/` are not proposed again.
3. **Kedro.**
   - I/O only through node inputs and outputs.
   - `model_id` comes from `params:model_id`.
   - Every `node()` has explicit `func=, inputs=, outputs=, name=, tags=`.
   - One layer per node; no `raw_` / `stg_` inputs in persona nodes.
4. **Contracts.**
   - Required columns go through `require_columns`.
   - Customer signals stay at CIF level.
   - Observation dates are month ends.
5. **Names that must not change** without a user decision:
   - catalog dataset names and HDFS paths;
   - pipeline names in the registry;
   - parameter keys;
   - output column names.

   Function and module renames inside crx_persona are allowed, but each one is listed so the
   workplace Sonnet can update the tests.
6. **No new Spark actions** (`count`, `collect`, `show`, `toPandas`). `log_latest_month` stays as
   it is (always on, a decision).
7. **Docstrings.**
   - They say what the code does now and why when that is not obvious.
   - No ticket or bundle history and no O-numbers.
   - Module docstrings name the run command and the inputs.
8. **Tiers.** Tier K, A and X files are never edited here (A3 changes go to `a3_handoff.md`).
   Tier L changes must not break imports from A3 modules.

## 4. Roles

| Agent | Kind | Model / effort | Job |
|---|---|---|---|
| **Master** | the running session | Opus 5.5, high | Runs the phases, merges proposals, runs the gates, keeps `decisions.md` and `questions.md`, writes the final report |
| **Cartographer** | subagent, Phase 0 | Opus 5.5, medium | Inventory, baseline metrics, golden-output harness |
| **S1 Architecture** | specialist | Opus 5.5, high | Module and engine boundaries, helper extraction, duplication across axes, wrapper thinness, public surface |
| **S2 Spark efficiency** | specialist | Sonnet 5.5, high | Joins, shuffles, windows, repeated scans, partition pruning, caching, UDFs, plan size |
| **S3 Kedro and contracts** | specialist | Sonnet 5.5, medium | Node and pipeline style, catalog and registry consistency, params, `require_columns`, layer rule, optional inputs |
| **S4 Readability** | specialist | Sonnet 5.5, high | Names, function size and shape, control flow, constants, type hints, module layout |
| **S5 Docstrings** | specialist | Sonnet 5.5, medium | Least text that is still enough; runs **last** each round, on the merged code |
| **S6 Correctness** | specialist | Opus 5.5, high | Validates against the specs: dates and point-in-time bounds, nulls, joins that drop or duplicate rows, CIF grain, consistency across axes. Outputs **findings, not edits** |
| **S7 Dead code** | specialist, round 1 only | Sonnet 5.5, medium | Unused functions, params, catalog entries and constants; confirms tier D |
| **R-E Efficiency engineer** | reviewer | Sonnet 5.5, high | Persona below |
| **R-I Interpretability advocate** | reviewer | Sonnet 5.5, high | Persona below |
| **R-O Owner (senior data engineer)** | reviewer | Opus 5.5, high | Persona below; final say |

**Reviewer personas.** Each reviewer's prompt opens with its persona.
- **R-E:** "You are a principal engineer who measures code by what can be removed. You favour
  fewer lines, fewer concepts, fewer passes over data, idiomatic PySpark and no indirection that
  does not pay for itself. You distrust comments that repeat the code."
- **R-I:** "You review for the analyst who joins next year and the auditor who must trace a
  state back to a rule. You favour explicit names, one idea per function, named constants tied
  to the spec, a straight-line flow, and a docstring at every boundary. You accept extra lines
  when they make a business rule visible."
- **R-O:** "You are the senior data engineer who signs this code off and answers for it in
  review and audit. You weigh R-E against R-I, and also how it runs in PROD, the risk of the
  change, how easy it is to apply through bundles, test impact, and consistency with the A4
  engine shape. Your verdict decides style and design questions. You cannot override a failed
  gate or a behaviour question."

## 5. Phases

### Phase 0: baseline (Master + Cartographer)

1. **Worktree.** Create `../Collections-refactor` on branch `refactor/persona_review` from
   `33fcc07` (bundle 14 head, which matches the workplace). The A3 session on
   `feature/persona_redesign` is not touched.
2. **Inventory.** The Cartographer writes `00_baseline/inventory.md`:
   - the per-file tier;
   - the import graph;
   - the catalog datasets each node reads and writes;
   - the public functions each file exposes.
3. **Metrics.** The Cartographer writes `00_baseline/metrics.json`, per file:
   - lines;
   - docstring and comment share;
   - functions over 40 lines;
   - maximum nesting;
   - Spark actions;
   - `pylint` score;
   - number of `ruff` findings.
4. **Golden harness.** The Cartographer writes `workplace_mirror/checks/refactor_golden.py`:
   - It builds small synthetic inputs for every Tier-L pipeline. It reuses the builders in the
     three spec tests and adds cases so that every rule branch fires; branch coverage is
     reported.
   - It runs the pipelines through Kedro's `SequentialRunner` with in-memory datasets and Spark
     local.
   - It writes each output to `00_baseline/golden/<pipeline>/<dataset>.parquet` (gitignored)
     with a hash manifest that is committed.
   - On later runs it compares schema plus `exceptAll` both ways and fails on any difference.
5. **Gate run on the baseline.** Every later round must stay at or above this result.
6. **Checkpoint U0 (user).** The user confirms scope, tier D and the rubrics (step 7), and
   answers §10.
7. **Rubrics.** R-E, R-I and R-O each write `rubrics/<persona>.md` independently:
   - 5–8 criteria, each with a 1–5 anchored scale and a weight;
   - what is a **blocking objection**;
   - 2–3 examples from this codebase.

   The Master then writes `rubrics/scorecard.md`: the union of criteria with each reviewer's
   weights side by side. The rubrics stay separate (three voices); the scorecard only aligns
   the vocabulary. The rubrics are frozen after U0.

### Rounds 1–3: propose → merge → gate → review → triage

Each round produces one commit on `refactor/persona_review`
(`Refactor R<n>: <summary>`) and a folder `round_<n>/`.

| Step | Who | Output |
|---|---|---|
| a. Propose | Specialists, in parallel, each on the round's input commit | `round_n/proposals/S<k>.md` |
| b. Merge | Master: dedupe, order, apply, fix conflicts | the round commit + `round_n/merge_log.md` |
| c. Docstrings | S5 on the merged code | folded into the round commit |
| d. Gates | Master (§6) | `round_n/gates.md`; a failing change is reverted, not patched over |
| e. Review | R-E, R-I, R-O in parallel, blind to each other | `round_n/reviews/R-*.md` |
| f. Triage | Master, then R-O's verdict | `round_n/triage.md` = the next round's brief |

**Merge order:** deletions (S7) → architecture (S1) → contracts (S3) → efficiency (S2) →
readability (S4) → docstrings (S5). If two proposals touch the same lines, the earlier stage
wins and the later one is re-based by the Master or sent back. S6 findings go to
`questions.md` and never into the code.

**What each round does:**
- **Round 1, broad.** S1–S4, S6 and S7 cover all of Tier L. Each specialist caps its proposals
  at about 25, ranked by value.
- **Round 2, targeted.** Only items marked *revise*, plus new issues the reviewers raised. Only
  the specialists that own them are re-run. User answers to round 1 questions that ask for a
  behaviour change are **not** applied here; they go to a separate fix bundle (§8).
- **Round 3, convergence.**
  - A cross-axis consistency pass by S1 and S4 with a narrow brief: the same patterns are
    written the same way in A1, A2 and A4.
  - A final review by all three reviewers.
  - R-O's sign-off.

**Triage rules:**
- Accepted by R-O with no blocking objection → **keep**.
- A blocking objection from any reviewer → **revise** in the next round. The objection is
  quoted in the brief.
- Rejected by R-O → **revert**.
- Rejected in two rounds → **dropped** and logged; it is not proposed again.
- R-E and R-I disagree and R-O has no objection → R-O's verdict decides. Its reasoning is
  written down, because the final report shows these disputes.

**Convergence (stop early if met after round 2):**
- all gates green;
- no open blocking objection;
- R-O scores at least 4 on every criterion of its rubric;
- R-E and R-I each average at least 3.5;
- no new *revise* items.

After round 3, R-O decides whatever is still open. Questions about behaviour go to the user
and stay out of the code either way.

## 6. Gates (run by the Master after every merge; all must pass)

1. `python -m py_compile` on every changed file.
2. `black --check -l 88`, `ruff check --select F,E,W,I,B,SIM,UP`, and
   `PYTHONPATH=src pylint --disable=relative-beyond-top-level`. The pylint score may not fall
   below the baseline for any file.
3. Spec tests:

   ```bash
   JAVA_HOME=/opt/homebrew/opt/openjdk@17 python checks/a1_engine_spec.py
   ```

   and the same for `a2_engine_spec.py` and `a4_chain_spec.py`. Imports of the temporary check
   pipelines are kept or re-pointed, never deleted.
4. `checks/refactor_golden.py`: identical outputs on every Tier-L pipeline.
5. Import smoke test:
   - every module in `pipeline_registry.py`, including A3, imports;
   - `kedro registry list` resolves;
   - every node's inputs and outputs exist in the catalog.
6. Rule checks with grep:
   - no `spark.read`;
   - no hard-coded `model_id`;
   - no new `.count()` or `.collect()`;
   - every `node(` call has all five keywords.

## 7. Formats

**Proposal record**, one per change in `proposals/S<k>.md`:

```
### S2-07  <title>
Files: a2_locatability/signals.py:120-168
Behaviour: none | possible (why)
Change: <one paragraph>
Diff: <unified diff against the round input commit>
Gain: <lines, Spark jobs or concepts removed; or what reads more clearly>
Risk: <what could break, and which gate catches it>
```

**Review record**, per proposal and then per file:

```
S2-07: accept | revise | reject (blocking: yes/no), criterion IDs, one-paragraph reason
File a2_locatability/signals.py: score per criterion (1-5) + one line
```

**Question for the user** (`questions.md`):

```
Q-07 [A2 · a2_locatability/signals.py:211] Travel rule uses `<` where spec §4 says `≤`.
Now: … Spec: … Options: (a) keep code, amend spec (b) fix code in a fix bundle.
Recommendation: … Impact estimate: … rows / which check would show it.
```

The questions are sent to the user once, after round 1, and anything raised later goes at the
end. A new finding also gets an O-number in `REVIEW_OBSERVATIONS.md`.

## 8. From the branch to the workplace

- **Bundle sequence.** The Master proposes the split. The default runs lowest risk first, so
  that each PROD check isolates one axis:
  1. **Shared and deletion** (tier D removal, `_common.py`, `scoring_engine.py`, obs base,
     catalog and registry). PROD check: `kedro registry list` plus a run of each obs-base
     pipeline.
  2. **A4** (`_dpd_journey` and its wrappers).
  3. **A1.**
  4. **A2.**
- **PROD check for bundles 2–4.** A temporary node computes the old-vs-new crosstab of the axis
  output and the expected answer is **0 differing rows**. That is stronger than the usual D4
  distribution check because nothing is meant to change. Any difference becomes a question for
  the user before step 8.
- **Building.**
  - Numbers are the next free ones at build time; `make_bundle.py` numbers by file count, so
    check the name.
  - The base is the latest workplace-equivalent head. If bundle 14 or an A3 bundle lands first,
    the branch is rebased onto it and all gates are run again.
  - `--exclude` covers `_dcore_codes.py`, the A3 modules and any other-axis work.
  - Every file shipped passes black, ruff and pylint.
  - Each bundle lists the renamed and removed public functions for the workplace Sonnet's test
    updates.
  - Each bundle ends with a cleanup prompt.
- **Behaviour fixes.** Questions the user answers as "fix the code" ship in their own fix
  bundle, after the matching refactor bundle, with a D4 distribution and crosstab check.
- **A3.** The A3 session ships its bundle with `a3_handoff.md` applied, after the shared bundle;
  then one check pass with the frozen rubrics (S1, S4, S5, then R-O).

## 9. Folder layout and final deliverables

```
workplace_mirror/refactor_review/
  PLAN.md                 this file
  00_baseline/            inventory.md, metrics.json, golden/ (parquet gitignored, manifest committed)
  rubrics/                efficiency.md, interpretability.md, owner.md, scorecard.md
  round_1/ .. round_3/    proposals/, merge_log.md, gates.md, reviews/, triage.md
  decisions.md            Master's running log (what, why, who decided)
  questions.md            Q-list for the user, with answers once given
  FINAL_REPORT.md         see below
workplace_mirror/checks/refactor_golden.py
```

`FINAL_REPORT.md` contains:
- metrics before and after, per file;
- the change log grouped by theme, each change with its reviewer scores;
- disputes and how R-O settled them;
- dropped proposals;
- the questions for the user and their answers;
- the bundle plan with bases and slugs.

Planning artifacts are committed on the refactor branch. Code goes back to
`feature/persona_redesign` only through the bundle flow, after the user approves.

## 10. Decisions needed before Phase 0

1. **A3** (answered 2026-11-04): included as design-in (§2): reviewed, target shape built into the shared layer, A3 file edits handed to the A3 session.
2. **Tier D deletion** (~7,000 lines: old A2 nodes, departure signatures, payment trajectory,
   utilisation). Recommended: delete in the first bundle, keep `build_rl_depart_spine` for A3,
   and leave `cc_raw_extract` and the spell tables until A3 moves off them (D5).
3. **Start now or after bundle 14 closes?** Recommended: start Phase 0 and round 1 now from
   `33fcc07` in the worktree, and rebase before building bundles. Bundle 14 only touches A1
   signals; if it needs a code change after review, round 2 picks it up.
4. **Golden harness.** It adds about one agent-hour but is the only gate that proves "no
   behaviour change" for code the spec tests do not reach (most of A4 and the obs base).
   Recommended: build it.
5. **Cost.** About 22–26 agent runs in total: Phase 0 needs 4; round 1 needs 7 specialists
   plus 3 reviewers; rounds 2 and 3 need about 5–6 each. Ways to cut cost:
   - merge S5 into S4;
   - stop after round 2 if it converges;
   - run R-O on Sonnet.

   The specialists that should stay on Opus are S1, S6 and R-O.
