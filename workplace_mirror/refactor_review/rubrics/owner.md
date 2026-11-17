# R-O rubric: Owner (senior data engineer)

I sign this code off and answer for it in audit and in PROD. I score what the code costs to run,
to ship through a bundle, to trace back to a spec, and to extend into A3. I settle style and design
disputes between R-E and R-I. I cannot override a failed gate (PLAN §6) or a behaviour question
(those go to `questions.md` and the user).

## Criteria (weights sum to 100)

Scores are per Tier-L file and per proposal. 1 / 3 / 5 are anchored; 2 and 4 sit between.

**O1 PROD operability (18).** The code runs cheaply and predictably on PROD volumes, and when it
fails or logs, a PROD reader can act on what it says.
- 1: Spark actions inside node logic for logging (`.count()` on the full lineage), schema guards that
  quietly turn a source off, an error that does not name the table and columns, no state log.
- 3: one action at most per node beyond the always-on `log_latest_month`; required inputs fail
  loud; partition floors derived from the base; some messages lack the dataset or the model_id.
- 5: every pass over data earns its keep (one shuffle per grouping, filters before joins, floors
  pushed down); the only actions are the decided ones (month-end check, `lookback_floor`, state log);
  every error names dataset, columns or dates and the fix; the state log has the same format on
  every axis and is labelled with the model_id.

**O2 Change risk and bundle-ability (18).** The change is safe to apply through `apply_bundle.py`
(three-way `git merge-file`) and cheap for the workplace Sonnet to follow.
- 1: whole-file rewrites or moves with little gain, renames of catalog entries / HDFS paths /
  pipeline names / params / output columns, edits to Tier K/A/X or `_dcore_codes.py`, axes mixed in
  one commit, renamed public functions not listed for the tests.
- 3: the diff is local, but some hunks are cosmetic reflows in files the workplace also edits
  (A1 / A2 signals); the test-churn list is incomplete.
- 5: hunks are minimal and in the place they belong; each commit belongs to one bundle of §8
  (shared+deletion, A4, A1, A2); every renamed or removed public symbol is listed; catalog and HDFS
  are unchanged; the bundle's PROD check is a 0-diff crosstab plus `kedro registry list`.

**O3 Auditability (16).** An auditor can go from a state value to the rule, the spec ID and the
input that fired it, and nothing in the code contradicts what it does now.
- 1: docstrings carry ticket history (T43, R13, RL-A4-3, bundle numbers) or describe removed code;
  thresholds are bare literals; the output drops the evidence that decided the state.
- 3: the rule is findable but scattered; the spec is named at module level only; some reason
  columns missing.
- 5: each rule sits in one named place tied to its spec section; module docstrings name the run
  command and the inputs; the output carries the reason / evidence columns; no history text.

**O4 One engine, thin wrappers (14).** A1, A2, A3 and A4 share one shape: an engine package
(signals → classify, or the A4 two stages), a pipeline factory taking `product`, and per-product
wrappers that hold only what really differs (anchor, scheme, source mapping).
- 1: product logic duplicated in CC and RL modules; wrappers with business rules; each axis logs,
  labels and joins in its own way.
- 3: the engine exists but conventions differ by axis (positional vs dict `inputs`, tag lists,
  two state-log implementations, constants mirrored from Tier-K modules).
- 5: the same pattern is written the same way on every axis; a wrapper is the product node(s) plus
  `create_pipeline`; shared conventions live in `_common.py` only.

**O5 Fits A3 easily (14).** The shared layer and engine pattern make the planned A3 engine
(`a3_credibility/` + CC/RL wrappers; D-A3-1..21) simple to build.
- 1: A3 would have to re-derive the episode anchor, rebuild windows or the obs base, or a shared
  change breaks an A3 import.
- 3: the pieces exist but A3 must reach into `_dpd_journey` internals or copy window logic.
- 5: A3 reads the obs-base grain, gets the latest spell start point-in-time from one shared helper
  built on the A4 engine (`months_before_spell`), and has a shared DCORE window
  `[anchor, observation_date)` and a band-by-`model_id` lookup (`window_months` style); one method
  per dimension fits the signals → classify shape without switches; `a3_handoff.md` is diff-level.

**O6 Contracts and Kedro conformance (10).** PLAN §3 rules 3–4 hold, visibly.
- 1: I/O outside nodes, `model_id` not from `params:model_id`, `node()` without the five keywords,
  mixed layers, `raw_`/`stg_` inputs, optional sources that should be required.
- 3: the rules hold but the contract is implicit (positional inputs, required columns checked late).
- 5: dict `inputs` naming each argument; `require_columns` at the top of every builder for every
  source; optional sources are explicit parameters with a comment saying why.

**O7 Clarity per line (10).** The code is as short as it can be while each business rule stays
visible: my balance of R-E and R-I.
- 1: long functions mixing joins, rules and labels; or one-line helpers that only forward calls.
- 3: readable, with a few needless indirections or a few hidden rules.
- 5: straight-line builders under ~40 lines, names in the spec's words, no dead parameters.

## Blocking objections

A proposal I mark blocking goes to *revise*. I block when a change:
1. changes outputs (rows, columns, types, values) or fails any gate (PLAN §6);
2. renames a catalog dataset, HDFS path, registry pipeline name, parameter key or output column
   without a user decision;
3. adds a Spark action, removes a fail-loud check, or makes a required source optional;
4. makes A3 harder: A3 must duplicate the anchor or window logic, or an A3 import breaks;
5. edits a Tier K/A/X file or `_dcore_codes.py`, or mixes two bundles' scope in one commit;
6. breaks a Kedro hard rule (§3.3) or the CIF-level / month-end contract (§3.4);
7. drops or reformats a PROD log block a bundle check or a GRR report reads, without listing it;
8. moves a spec threshold or reason list somewhere it can no longer be found from the spec ID;
9. renames or removes a public function without adding it to the bundle's test-update list.

## Tie-break policy (R-E vs R-I)

Order of precedence: gates and behaviour → bundle risk (the smaller, more local diff wins) →
spec traceability (R-I wins on any line that encodes a business rule, threshold or date bound) →
brevity (R-E wins everywhere else). I write the reason in `triage.md` every time.

- **Inline a single-use helper?** Inline it when it is private, short, and not a business
  concept. Keep it when its name is a spec term or it shortens three or more call sites:
  `_in_window` (`a1_ability/signals.py:85-87`) forwards to `window_agg` but shortens 6 calls, so it
  stays; `_label` (`a2_locatability/classify.py:46-47`) stays, it is used twice.
- **Named constant vs literal?** A business number or code list gets a module-level name with its
  spec reference, even when used once (`_BALANCE_MAX_AGE_M`, `CASA_HELD_MONTHS`). Structural
  literals stay inline (`_rn == 1`, `fillna(0)`, `range(1, 7)` next to a comment that says why).
  A constant has one home: no copies of a Tier-K module's value.
- **Docstring on a private helper?** None when the name and signature say it. One line when it
  fixes a date bound, a grain or a NULL meaning (`_window_start`, `_cifs`). Public builders and
  pipeline factories always: grain of the output, inputs, what NULL means.
- **Dict vs positional `inputs`:** dict, rename-safe and explicit (R-I), even where R-E counts lines.

## Sign-off at the end of round 3 (consistent with PLAN §5)

I sign off only when all hold:
- all six gates green on the final commit, golden harness identical on every Tier-L pipeline;
- no open blocking objection from any reviewer;
- my score is ≥ 4 on every criterion (weighted by file lines over Tier L) and no Tier-L file
  scores below 3 on O1, O2 or O3;
- R-E and R-I each average ≥ 3.5; no new *revise* items;
- every behaviour finding is in `questions.md` (with an O-number), none in the code;
- the bundle plan (§8) lists base, slug, `--exclude` set, renamed / removed symbols and a
  0-diff crosstab check for each of bundles 2–4;
- S1's target A3 shape scores ≥ 4 on O5 and `a3_handoff.md` is diff-level against current A3 files.
Anything still open after round 3 I decide and log; behaviour stays with the user.

## Examples from this code (baseline `33fcc07`)

1. **`_dpd_journey/logging.py:61-100` vs `_common.py:140-164`** — two state-log implementations
   with different formats; the A4 docstring still cites `cc_a2_locatability_v2`, which no longer
   exists. Today O4 = 3, O3 = 2. A 5: one documented logger in `_common.py`, with the per-account
   dedup A4 needs while `cc_spine` is mid-month stated as a parameter, the log format unchanged or
   the change listed in the bundle.
2. **`cc_a4_deterioration/nodes.py:1-23`** — the docstring carries history ("T43's 2026-10-20
   PROD run", R13, R20) and `_RESTRUCTURE_DLQ_THRESHOLD` mirrors a Tier-K module (`cc_spell`).
   `rl_a4_deterioration/pipeline.py:30-56` uses positional `inputs` and its own tag list, unlike
   A1/A2. Today O3 = 2, O4 = 3, O6 = 3. A 5: the docstring says what the floor params do and why
   180+ has its own; the threshold is named once in the A4 package; dict inputs and shared tags.
3. **`cc_a3_payment_credibility/nodes.py:176-200`** (A3, handoff only) — two full-lineage
   `.count()`s per bridge call for a log line, and `_guarded_feat` turns a missing or empty source
   into NULL columns (P2). Today O1 = 1, O6 = 1, O5 = 1 (spell-table bridge). A 5: the A3 engine
   on the obs base with the shared anchor helper, `require_columns` up front, and one
   `log_latest_month` call as A1/A2 (`a1_ability/classify.py:197`).

For reference, the target shape scores high today: `a1_ability/pipeline.py:40-117` (one factory,
product anchor node injected, dict inputs) is O4 = 4, held back only by A2 / A4 not sharing it.
