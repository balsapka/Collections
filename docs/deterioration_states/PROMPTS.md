# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace repository. Each prompt is
self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 (file mode) → P2**, then P3 / P4 as the results require, then P5.
**P6 (Spark) and P7 (production)** only after the methodology and states are signed off.
**P8 ships the reviewed PySpark pipeline (CC + RL)** into the existing Kedro code — it
replaces P7 for that work. Sonnet has no PROD data access: P8 is code changes and offline
tests only; the user runs the pipelines and `spark/prod_check.py` in PROD.
**P9 runs after P8**: adds the regression tests under `src/tests/{nodes,pipelines}/crx_persona/`
and removes everything unpacked from the bundle (recoverable from BUNDLE.md), plus any dead
code the rewrite left in `src/`.
**P10 fixes the state vocabulary** (after P9): one tree and the same 7 states for 60–180
and 180+ (option B only), no stabilized at 180+, holds at the ceiling are not payments.
**P11 fills in the Results sheet** of the stakeholder workbook from a results file you
specify (e.g. the prod_check JSON).

---

## P0 — Orientation (paste first, every session)

```
You are working in our workplace repository on the "deterioration states" package in
docs/deterioration_states/. Read these first, fully, before doing anything:
  1. docs/deterioration_states/README.md
  2. docs/deterioration_states/METHODOLOGY.md
  3. docs/deterioration_states/REVIEW.md
  4. docs/deterioration_states/dpd_states/config.py
  5. docs/deterioration_states/dpd_states/states.py

What it is: one state per credit-card account in DPD buckets 4–7, assigned from the DPD
bucket-history string (leftmost digit = current month, rightmost = first billed month) by
a short decision tree (options A/B/C). The state logic and thresholds were designed,
validated and independently reviewed elsewhere.

Ground rules — follow all of them:
- Do NOT change the state logic, thresholds or expectations in dpd_states/states.py or
  dpd_states/expectations.py unless a prompt explicitly asks you to. Parameters marked
  [business] in states.py are agreed business definitions: never change them to make a
  share or a check come out right — report and escalate to me instead.
- NEVER invent a dataset, table or column name. Find it in the repo (Kedro catalog
  conf/**/catalog*.yml, pipeline code, notebooks, data/) or ask me. Leave <<FILL-IN>>
  where you cannot confirm a name.
- Run every tool from the repo root as `python docs/deterioration_states/run.py <tool>`
  (validate | selftest | synthetic | bundle). `python -m dpd_states...` only works from
  inside docs/deterioration_states/.
- Results files contain aggregates only — no account keys, CIFs, names, raw DPD strings
  or other row-level data. Do not paste raw DPD strings into this chat.
- Never present a number you have not seen in actual output. If something has not run,
  say it has not run.
- Keep code changes minimal and confined to dpd_states/config.py and the clearly marked
  <<FILL-IN>> spots unless asked otherwise.

Reply with a 5-line summary of what the package does and which names need filling in.
```

---

## P1 — File mode: check the input and do the first run

```
Task: run the package on our DPD-history file, without Spark.

1. The input is data/input/dpd_synthetic_data.xlsx (CC 60–180 DPD segment, Aug 2026),
   DPD string column "dpd_history_str". These are already the defaults in
   dpd_states/config.py (INPUT_FILE, COL_DPD). The file has other derived columns — ignore
   them unless they are one of the optional columns below.
2. Before running, check with a few lines of pandas (print aggregates only, no raw strings):
   - the column reads as TEXT (dtype object/string) when loaded with dtype={"dpd_history_str": str};
     if Excel stored it as a number, digits are lost — stop and tell me;
   - the share of strings whose LEFTMOST digit is 4–7 (today's spine) and the
     distribution of the RIGHTMOST digit (should be mostly 0/1 = first billed month);
   - min / median / max string length (strings are cropped to the reliable window,
     RELIABLE_FROM = 2024-01 to SNAPSHOT_MONTH = 2026-08 = 32 months, inside the package —
     do not crop them yourself; if the snapshot month differs, update SNAPSHOT_MONTH);
   - any characters other than 0–9 (if so, list them with counts; do not guess a mapping).
3. Optional columns: if the file (or another file I point you to) has any of the persona
   scores (credibility total and its three components, ability score, reachability /
   in-country flags), the bank's existing bust-out / stabilized flags, or payment-holiday /
   restructured flags, map them in AXIS_COLS / EXISTING_RULE_COLS / FLAG_COLS in config.py.
   Show me the diff. Do not build joins without asking.
4. Install openpyxl if pandas cannot read .xlsx, then run from the repo root:
       python docs/deterioration_states/run.py selftest     (must end "SELFTEST PASSED")
       python docs/deterioration_states/run.py validate
5. Paste me the block between === DPD_STATES OUTPUT START === and END.
```

---

## P2 — Interpret the run

```
Task: interpret the latest results/dpd_states_file_<file>_<date>.json and .md (file mode)
or results/dpd_states_validation_<model_id>_<date>.json (Spark mode).

Report, in this order:
a. Any FAIL (E01, E02, E03). If present, STOP: diagnose and propose the config fix.
b. In FILE mode, outcome checks (E03, E10–E12, E23–E25) are SKIPPED because a snapshot of
   today's segment has no accounts that left it — say so once; that is expected. E13, E14
   and E26 run on survivors.
c. Each WARN: observed value, expected range, the check's anchor (bank / design /
   synthetic / data) and its "if_not_met" action. Say whether the action needs a config
   change, a decision from me, or nothing. A WARN on a "synthetic" anchor is a prompt to
   look, not proof of a problem.
d. The option-B state shares, and how they compare with the bank's figures (EPD ~6% under
   the bank's broader bust-out rule; stabilized ~6%).
e. E07: which of the four spell definitions comes closest to the bank's ~85%.
f. E04 (histories that start delinquent) and E27 / E28 (padding, calendar artefacts).
g. Which option the data supports, using METHODOLOGY.md §8 "Choosing the option".
Every number you quote must come from the output. Mark anything you infer as an inference.
```

---

## P3 — Fix-up loop for WARNs (bounded)

```
Task: address the WARN checks from the last run, within strict limits.

Allowed without asking me: config.py changes (names, CHAR_MAP, STRIP_CHARS, filters,
optional columns, COL_STRING_AS_OF).

Allowed only after I approve, one at a time: the technical parameter
straight_max_runup, and merging early-life straight roller into straight roller if E16
shows it under 5% (set seasoned_min_months=None in the option — this was pre-agreed).

Never: changing [business] parameters (epd_max_history, epd_max_blips,
stabilized_min_in_band, stabilized_long_run_*, repeat_min_prior_peak,
repeat_window_months, seasoned_min_months) to hit a share; changing the tree; adding or
removing states; editing expectations to make a check pass; using payment-promise /
inflow / ability columns inside states.py. For those, write me the evidence (the sweep
rows in section 6 of the report) and I decide.

After approved changes, re-run and compare old vs new check tables.
```

---

## P4 — Compare with the bank's existing bust-out and stabilized rules

```
Task: compare this package's early_payment_default (the bank calls it bust-out) and
stabilized with the bank's existing implementations.

1. Find the existing bust-out and stabilized logic in this repo (search for "bust",
   "stabil", "dpd", pipeline nodes, SQL). List the files and quote the rules.
2. Translate each into the terms of METHODOLOGY.md §4 (history before the spell, blips,
   earlier spells, "never paid since crossing bucket 2", months within ±1 of today's
   bucket out of the last 6, the long-run clause).
3. List every difference and its likely effect on the shares (E08/E09) and recall
   (E10/E11). If the existing flags are available as columns, wire them into
   EXISTING_RULE_COLS in config.py so the next run measures agreement directly
   (1/0, Y/N and True/False are all read correctly).
4. Do not change states.py. Report the differences to me for a decision.
```

---

## P5 — Short stakeholder report: rules and results

```
Task: write the shortest possible report for the Group Retail Risk stakeholders from the
latest results/dpd_states_file_<file>_<date>.json and .md (or the Spark results file).
Target: one screen. No code, no eta², no ARI, no check IDs.

Write exactly these sections:

1. Title + one sentence: what the states are (one state per credit-card account in
   90–180+ DPD, buckets 4–7, from its DPD history since Jan 2024) and the data used
   (file, snapshot month, number of accounts).

2. The rules — one table, rows in this order (option B), columns: State | Rule (one line,
   plain words) | Share | Action. Use the display names and these rules:
   - Early payment default (EPD, formerly "bust-out"): at most 3 months on book before
     falling in (one paid-off blip allowed) and never paid since — still rolling.
   - Stabilized: paying about one month's due each month — 5 of the last 6 months within
     one bucket of today's, or 6+ months past bucket 4 and at most one bucket higher than
     6 months ago.
   - Repeat delinquent: cured a spell that reached 60+ DPD and fell back in within 12 months.
   - Seasoned straight roller: 12+ months on book, then rolled straight to bucket 4 with no
     payment on the way down.
   - Early-life straight roller: same, within the first 12 months on book.
   - Slow roller (partial payer): paid something on the way down but kept rolling.
   Actions: from METHODOLOGY.md §4. Shares: from the results file only.
   Add one line under the table: states are checked in this order, first match wins, so
   every account gets exactly one state.

3. Results — at most 5 bullets, real numbers only: the biggest state(s), stabilized vs
   the bank's ~6%, EPD vs the bank's ~6% bust-out, data quality in one line (accounts
   excluded and why), and that outcome checks (roll rates, exits) come with the Spark
   backtest.

4. Decisions needed — at most 3 bullets, from METHODOLOGY.md §10.

Every number must come from the results file. If a check FAILED (e.g. unparseable
strings), say so in one line under Results with the count and what is being done.
Write it to docs/deterioration_states/results/stakeholder_report_<date>.md and show it to me.
```

---

## P6 — Spark validation with outcomes (after file-mode sign-off)

```
Task: run the Spark validation, which adds the outcome backtest.

1. Find the dataset with one DPD-history string per credit-card account at the latest
   month. For outcomes it must still contain accounts that have since rolled to 8+ or
   closed, and every string must end in the same month (if strings freeze at charge-off,
   find the column with the string's as-of date for COL_STRING_AS_OF). If several
   candidates exist, list them with their columns and ask me.
2. Fill in DS_STRINGS_TMPL, KEY, COL_SNAPSHOT / ROW_FILTER / COL_STRING_AS_OF as needed in
   config.py, and the globals_dev accessor in snippets/dpd_states_validate.py
   (_resolve_model_id). The string column must be a string type.
3. Give me the notebook cell from the snippet docstring for main(catalog, check_only=True).
   When I paste the CHECK block back, verify: counts plausible, rows == accounts, newest
   digit 4–7 / oldest digit mostly 0/1, no WARNING lines. Then the full run:
   result = main(catalog). Config edits take effect without a kernel restart (the config
   fingerprint is printed).
4. Interpret with P2 (now E03 and the outcome checks run).
```

---

## P7 — Productionise the chosen option (only after sign-off)

*Superseded by **P8** for the CC / RL Kedro pipelines (`crx_persona`), which already exist.*

```
Task: add the deterioration state as a pipeline output, using the option I name:
<A_minimal_4 | B_balanced_6 | C_detailed_7>.

1. Follow this repo's existing pipeline patterns (find a comparable node and copy its
   structure, naming, catalog entries and tests). Do not invent conventions.
2. The node takes the DPD strings and, in this order: cleans them with
   dpd_states.analysis.clean_strings, keeps today's spine (current bucket 4–7), then calls
   dpd_states.features.build_features and dpd_states.states.assign_states — do not
   re-implement the logic. Apply per partition (mapInPandas / applyInPandas).
3. Output: account key, snapshot date, state code, display name
   (dpd_states.states.DISPLAY_NAMES), option name, and the assignment features for
   auditability: left_censored, months_before_spell, n_blips, n_prior_episodes,
   gap_prior_peak3, spell_pay_events, runup_len, runup_pays, last6_in_band,
   months_since_4, chg_6m, n_glitches, n_jumps_repaired.
4. model_id from globals, never hardcoded; new catalog entries model_id-namespaced like
   the existing ones.
5. Ship a validation snippet to the same contract as snippets/dpd_states_validate.py:
   row counts, null rates, share per state, MECE check (exactly one state per account),
   agreement with the last validation run's shares (within 1pp), and banded journey
   shapes (no raw strings, no keys).
6. Show me the diff and the catalog entries before anything runs.
```

---

## P8 — Ship the reviewed PySpark pipeline (CC + RL) into the Kedro repo

Background: `spark/REVIEW_SPARK.md` (findings F1–F12, design, rule changes, §5 roles).
Sonnet runs this prompt (code + offline tests). Afterwards **you** run REVIEW_SPARK.md §5
P1–P2 in PROD and paste the `=== DPD_JOURNEY PROD CHECK START / END ===` block back.

```
Context: I am adding a reviewed PySpark/Kedro rewrite of the DPD-journey deterioration
pipelines (CC + RL) to this repo. Everything is in docs/deterioration_states/BUNDLE.md,
which I have saved raw at that path.

Hard rules:
- You have NO PROD data access. Never call catalog.load, never run kedro run, never
  query any table. Only edit code and run offline tests (synthetic data).
- Never guess a dataset, column or module name: find it in the repo or ask me.
- Do not retype bundled code by hand: use the extractor, which checks SHA-256.
- Stop and wait for my OK where marked STOP.

Step 1 — unpack and verify
1. Create docs/deterioration_states/extract_bundle.py from the "Extractor" section of
   BUNDLE.md, then run:
   python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
   It must end with "N files OK, 0 mismatched". If anything mismatches, stop and tell
   me (the copy was altered); do not hand-fix code.
2. Run: python docs/deterioration_states/spark/tests/test_parity.py
   It must print "PARITY PASSED". If pyspark or another package is missing, tell me
   which; do not change code to work around it.

Step 2 — impact scan (report only, change nothing)
Read docs/deterioration_states/spark/REVIEW_SPARK.md first (findings, design, §5).
Then report:
a) every importer of _dpd_journey under src/ and the names each one imports
   (grep -rn "_dpd_journey" src/);
b) the catalog entries (conf/**/catalog*.yml) for crx_cc_dpd_sequences,
   crx_rl_dpd_sequences, crx_cc_a4_deterioration, crx_rl_a4_deterioration — format,
   partitioning, schema settings;
c) any consumer of those four datasets outside the cc/rl_a4_deterioration pipelines;
d) the current value of _DPD_BUCKET_REGEX and where it is defined;
e) the PySpark version the project pins (the new code needs >= 3.3);
f) the current params:crx_persona block (file path + keys).
STOP — show me the report.

Step 3 — apply (only after my OK)
Replace, keeping this repo's import style, logging and lint conventions:
- src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
    <- docs/deterioration_states/spark/crx_persona/_dpd_journey.py
- cc_full_history/nodes.py: build_cc_full_history
    <- spark/crx_persona/cc_full_history/nodes.py (keep the repo's _DPD_BUCKET_REGEX)
- rl_full_history/nodes.py: build_rl_full_history
    <- spark/crx_persona/rl_full_history/nodes.py
- cc_a4_deterioration/nodes.py and rl_a4_deterioration/nodes.py
    <- the files under spark/crx_persona/
- pipeline.py files: only if the node inputs differ from what is there now.
- Merge spark/conf/parameters_crx_persona_dpd_journey.yml under the existing
  crx_persona: block (do not touch persona_start_date / persona_end_date).
- Catalog: crx_cc_dpd_sequences and crx_rl_dpd_sequences are now ONE ROW PER ACCOUNT
  with an array<int> column dlq_buckets. Propose the catalog change (drop any
  partitioning by month).
If step 2a/2c found anything that still needs resolve_gaps, encode_transitions,
classify_from_grid or old BucketScheme fields, do NOT delete it: STOP and show me.
STOP — show me the full diff before writing files.

Step 4 — offline verification (after the files are written)
1. The repo's lint / test command on the changed files.
2. python -c "from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import create_pipeline as c; from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import create_pipeline as r; print(c().describe()); print(r().describe())"
3. python docs/deterioration_states/spark/tests/test_parity.py  -> PARITY PASSED
4. If Java + local Spark work in the dev container:
   python docs/deterioration_states/spark/tests/test_spark_e2e.py 2000  -> SPARK E2E PASSED
   (synthetic data only; if Java is missing, say so and skip.)
Report every result verbatim. Then list what I must run in PROD (REVIEW_SPARK.md §5
P1-P2) using this repo's real pipeline names.
```

---

## P9 — Add the tests, then clean up (after P8)

Before pasting: replace `docs/deterioration_states/BUNDLE.md` in the workplace repo with
the **latest raw** BUNDLE.md (it now carries the tests). The pipeline code in it is the
same as the bundle P8 used — step 1 checks that.

```
Context: P8 is done — the reviewed DPD-journey deterioration pipelines (CC + RL) are in
src/enbd_collections/pipelines/crx_persona/. I have just replaced
docs/deterioration_states/BUNDLE.md with a newer version that adds regression tests.
Now: (1) check src/ matches the bundle, (2) add the tests under src/tests/, (3) remove
everything else unpacked from the bundle and any dead code, so the repo holds only what
the registered pipelines use, plus their tests. I will re-extract from BUNDLE.md if I
ever need the rest.

Hard rules:
- No PROD data access: never call catalog.load, never run kedro run, never query a table.
- Delete nothing before I approve the plan (STOP below). Use `git rm` / `git mv`.
  Do not commit or push.
- Never delete anything a registered pipeline imports, any test of it, or any file that
  was not unpacked from the bundle without asking me.

Step 1 — re-extract and check src/ is current (report only)
1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
   -> must end with "0 mismatched" (if extract_bundle.py is gone, recreate it from the
   bundle's "Extractor" section first).
2. Compare the bundled engine and nodes with src/, ignoring import lines and formatting:
     docs/deterioration_states/spark/crx_persona/_dpd_journey.py   vs src/.../crx_persona/_dpd_journey.py
     .../spark/crx_persona/cc_full_history/nodes.py                vs src/.../cc_full_history/nodes.py
     .../spark/crx_persona/rl_full_history/nodes.py                vs src/.../rl_full_history/nodes.py
     .../spark/crx_persona/cc_a4_deterioration/nodes.py, pipeline.py vs src/...
     .../spark/crx_persona/rl_a4_deterioration/nodes.py, pipeline.py vs src/...
   Report every LOGIC difference (anything beyond imports, the repo's _DPD_BUCKET_REGEX,
   logging and lint style). Quick check that the latest rules are in src/:
   grep -n "starts_delinquent\|def _stabilized\|\"unknown\"" src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
   must show all three.
If there is any logic difference, STOP and show me before going on.

Step 2 — add the tests (only after step 1 is clean)
Copy, keeping file names:
  docs/deterioration_states/spark/tests/nodes/crx_persona/test_dpd_journey.py
  docs/deterioration_states/spark/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py
  docs/deterioration_states/spark/tests/nodes/crx_persona/conftest.py
      -> src/tests/nodes/crx_persona/
  docs/deterioration_states/spark/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py
      -> src/tests/pipelines/crx_persona/
Create the crx_persona folders; add __init__.py files only if the sibling test folders
under src/tests/nodes and src/tests/pipelines have them. If src/tests (or a parent
conftest) already defines a session-scoped `spark` fixture, do not copy conftest.py — the
tests use the existing fixture. Do NOT copy docs/deterioration_states/spark/tests/conftest.py
or test_parity.py / test_spark_e2e.py (bundle-only: an import shim and the one-time proof
against the numpy reference). If step 1 found that the repo's pipeline uses different
dataset or node names, adapt the EXPECTED table in test_a4_deterioration_pipelines.py to
the repo — never the pipeline to the test.
Run:
  python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona
  -> 96 passed (the Spark node tests need Java + pyspark; if Java is missing, report it
     and run the other two files: 89 passed).

Step 3 — inventory for the clean-up (report only, change nothing)
a) Registered pipelines: from the pipeline registry, list the crx_persona pipelines and
   every module they import, transitively, inside src/enbd_collections/pipelines/crx_persona/.
b) Bundle files: every path in BUNDLE.md's "### FILE: `...`" headers that exists on disk,
   plus extract_bundle.py, results/, validation/, __pycache__/ and .gitkeep files under
   docs/deterioration_states/. Separately: anything under docs/deterioration_states/ that
   is NOT from the bundle (my notes, real-data outputs in results/) -> "ask", never "delete".
c) Dead code in src/enbd_collections/pipelines/crx_persona/ left by the rewrite:
   functions, constants and imports nothing references any more (e.g. old resolve_gaps /
   encode_transitions / classify_from_grid, old _log_* helpers, _CC_HISTORY_FLOOR_DATE,
   _DET_OPTION, _SCHEME, _AUDIT_COLS, unused imports). Confirm each with grep across
   src/ (including src/tests/), conf/ and notebooks/; if available, also run
   `ruff check --select F401,F811,F841` (or the repo's linter) and
   `python -m vulture src/enbd_collections/pipelines/crx_persona` as a hint, not a verdict.
d) Old tests, notebooks and docs that reference removed names (e.g. tests of resolve_gaps /
   encode_transitions) or docs/deterioration_states paths.
e) Parameters and catalog entries no longer read by any node.
Show the plan as one table: path or symbol | evidence it is unused | action
(delete / keep / ask). Defaults:
- docs/deterioration_states/**: delete everything from the bundle EXCEPT BUNDLE.md (the
  archive to re-extract from) — i.e. spark/ (its code is in src/, its tests now in
  src/tests/), dpd_states/, snippets/, run.py, extract_bundle.py, METHODOLOGY.md / .pdf,
  README.md, REVIEW.md, PROMPTS.md, validation/, __pycache__/.
- results/ with real-data outputs: ask.
- src/: delete only symbols with zero references.
STOP — wait for my approval of the table.

Step 4 — apply the approved table only
git rm the files; remove dead symbols and unused imports with minimal edits (no
reformatting of untouched code); remove empty folders. Leave BUNDLE.md unchanged.

Step 5 — verify (offline) and report verbatim
1. The repo's lint command on src/enbd_collections/pipelines/crx_persona/ and
   src/tests/nodes/crx_persona/, src/tests/pipelines/crx_persona/.
2. python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona -> all pass
   (and the rest of src/tests, if it ran green before).
3. kedro registry list   (imports every pipeline; no data) — crx_persona pipelines listed.
4. grep -rn "docs/deterioration_states\|resolve_gaps\|encode_transitions\|classify_from_grid" src/ conf/
   -> nothing (or only what I approved to keep).
5. git status --short and git diff --stat.
```

---

## P10 — One state vocabulary for both segments; no stabilized at 180+ (after P9)

Why: the previous engine had a separate 180+ tree that allowed `stabilized` at CC 8 and
added 180+-only states (`paying_in_default`, `broken_payer`), and it kept the A / C option
states that production never uses (`straight_roller`, `slow_roller_intermittent`,
`slow_roller_erratic`) plus a dead one (`paying_since_4`). Both came from the bundle, not
from Sonnet. Fixed: ONE tree and the same 7 states in both segments — `unknown`,
`early_payment_default`, `stabilized`, `repeat_delinquent`, `straight_roller_seasoned`,
`straight_roller_early_life`, `slow_roller`. Stabilized only up to CC 7 / RL 6 (151–180
DPD), never at 180+. Holds at the ceiling (CC 9, RL 7) are not payments, so EPD still works
at 180+. `det_option` and the `det_state_option` column are removed.

Before pasting: replace `docs/deterioration_states/BUNDLE.md` with the **latest raw**
BUNDLE.md. Changed for the repo: `_dpd_journey.py`, the `dpd_journey` params (no
`det_option`), and the three tests in `src/tests/{nodes,pipelines}/crx_persona/`. The node
and pipeline files are unchanged.

```
Context: src/enbd_collections/pipelines/crx_persona/ holds the DPD-journey deterioration
pipelines (CC + RL) from an earlier bundle, with tests in src/tests/nodes/crx_persona/ and
src/tests/pipelines/crx_persona/. docs/deterioration_states/ holds only BUNDLE.md, which I
have just replaced with a newer version. The new engine has ONE state tree for both
segments (60_180 and 180_plus) with 7 states: unknown, early_payment_default, stabilized,
repeat_delinquent, straight_roller_seasoned, straight_roller_early_life, slow_roller.
No stabilized at 180+, no 180+-only states, no A/C options. Bring src/ and the tests in
line, and remove everything the old vocabulary left behind.

Hard rules:
- No PROD data access: never call catalog.load, never run kedro run, never query a table.
- Extract the bundle OUTSIDE the repo (a temp folder) so nothing is unpacked into
  docs/ again; delete the temp folder at the end.
- STOP where marked. Do not commit or push.
- Never adapt the engine to make a test pass; adapt only repo-specific names in tests.

Step 1 — extract to a temp folder and verify (report only)
1. mkdir a temp folder outside the repo, e.g. T=$(mktemp -d). Create $T/extract_bundle.py
   from the "Extractor" section of docs/deterioration_states/BUNDLE.md, then:
   python $T/extract_bundle.py docs/deterioration_states/BUNDLE.md $T
   -> must end with "0 mismatched".
2. python $T/spark/tests/test_parity.py -> must print "PARITY PASSED" (needs pandas,
   numpy, pyspark importable; no Spark session).

Step 2 — compare (report only)
Diff, ignoring import lines and formatting:
  $T/spark/crx_persona/_dpd_journey.py vs src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
  $T/spark/tests/nodes/crx_persona/*.py vs src/tests/nodes/crx_persona/*.py
  $T/spark/tests/pipelines/crx_persona/*.py vs src/tests/pipelines/crx_persona/*.py
  $T/spark/crx_persona/{cc,rl}_{full_history,a4_deterioration}/*.py vs src/... (expected: no logic change)
Expected engine differences: one assign_state(f, cropped) for both segments;
classify(buckets, cropped, offset, canon_top) without segment/option; STATE_RULES/STATES
replace STATE_DEFAULTS/OPTIONS; features_180 / assign_state_180 / _FEATURES_180 removed;
journey_features(..., canon_top) does not count holds at the ceiling as payments; no
det_option param (an unknown dpd_journey key now raises); no det_state_option column.
List any OTHER difference in src/ — e.g. adaptations made in P8/P9 (logging, import
style, _DPD_BUCKET_REGEX, fixture names, EXPECTED table names) — those must be kept.
Then find every remaining use of the old vocabulary and options:
  grep -rn "det_option\|det_state_option\|segment_180_prototype\|assign_state_180\|features_180\|_FEATURES_180\|STATE_DEFAULTS\|OPTIONS\|paying_in_default\|broken_payer\|history_not_available\|history_starts_delinquent\|paying_since_4\|slow_roller_intermittent\|slow_roller_erratic\|\"straight_roller\"\|A_minimal_4\|C_detailed_7\|B_balanced_6" src/ conf/ notebooks/ 2>/dev/null
including catalog schemas / column lists that name det_state_option or the 180+ extra
columns (all_default, months_in_default, default_left_censored, pay_events_before_top,
paid_in_default, stabilized_months_in_4_7).
STOP — show me the diff summary and the grep results with a proposed action for each.

Step 3 — apply (only after my OK)
- Replace src/enbd_collections/pipelines/crx_persona/_dpd_journey.py with
  $T/spark/crx_persona/_dpd_journey.py, re-applying only the repo adaptations listed in
  step 2 (imports, logging, lint style).
- Remove `det_option` from the crx_persona.dpd_journey params (conf/**/parameters*.yml).
- Replace the three test files with the $T versions, re-applying only the repo
  adaptations from P9 (fixture choice, names in the EXPECTED table).
- Fix or remove every grep hit approved in step 2 (catalog column lists, notebooks, docs).
- Leave the node and pipeline files alone unless step 2 found a logic difference I
  approved.

Step 4 — verify (offline) and report verbatim
1. The repo's lint command on the changed files.
2. python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona
   -> 96 passed (89 if Java is missing: report it).
3. kedro registry list   (imports every pipeline; no data needed).
4. The step-2 grep again -> no hits (or only ones I approved to keep).
5. python -c "from enbd_collections.pipelines.crx_persona import _dpd_journey as J; print(J.STATES)"
   -> the 7 states.
6. Delete $T. Show git status --short and git diff --stat.
Then tell me what to re-run in PROD: Node 2 of both products for segment 60_180 and
180_plus (Node 1 is unchanged and need not be re-run), using this repo's real pipeline
and node names.
```

For the PROD check afterwards: `prod_check.py` is no longer in the repo. Extract the bundle
to a temp folder as in step 1, then in the Kedro session
`sys.path.insert(0, "<temp>/spark"); from prod_check import report; report(catalog)`.

---

## P11 — Fill in the Results sheet of the stakeholder workbook

Before pasting: put the stakeholder workbook in the repo (the reference copy is
`docs/deterioration_states/spark/stakeholder/dpd_deterioration_states_reference.xlsx` on
GitHub) and have the results file ready. Replace the three `<...>` below.

```
Task: fill in the "Results" sheet of <WORKBOOK PATH> from <RESULTS FILE PATH>.
Scoring date: <Mon YYYY>.

Rules:
- Edit ONLY the Results sheet, ONLY the input cells listed below, plus the subtitle in A2.
  Never touch formulas, other cells, other sheets or formatting beyond what is stated.
- Never type or compute shares or totals: they are formulas.
- Never guess a count. If the file has no data for a block, leave that block empty.
- No PROD data access: read only the given file. Save as a NEW file
  <WORKBOOK NAME>_<YYYYMMDD>.xlsx next to the original; keep the original. Do not commit.

Results sheet layout (find rows and columns by these labels, not by number; STOP if one
is missing):
- Count columns (header in row 4): "CC 61–180 DPD accounts" (B), "CC 180+ DPD accounts" (D),
  "RL 61–180 DPD accounts" (F), "RL 180+ DPD accounts" (H). Columns C, E, G, I are
  share formulas — never write there.
- State rows (labels in column A): Unknown · Early payment default (EPD) · Stabilized ·
  Repeat delinquent · Seasoned straight roller · Early-life straight roller ·
  Slow roller (partial payer). Plus the row "In segment, not classified".
  "Classified accounts" and "Coverage (target 99.9%)" are formulas — never write there.

Mapping from the file:
- State codes: unknown -> Unknown; early_payment_default -> Early payment default (EPD);
  stabilized -> Stabilized; repeat_delinquent -> Repeat delinquent;
  straight_roller_seasoned -> Seasoned straight roller; straight_roller_early_life ->
  Early-life straight roller; slow_roller -> Slow roller (partial payer).
- Blocks: product cc / rl; segment 60_180 -> "61–180 DPD", 180_plus -> "180+ DPD".
- If the file is the JSON from prod_check: products.<cc|rl>.segments.<60_180|180_plus>
  .state_counts (a state missing there = 0) and .in_segment_not_classified.
  Several JSON files (one per segment run) are fine: merge them; the same block in two
  files is an error — STOP.
- Any other format: show me how you read it and STOP before writing.

Step 1 — read (report only): print a table product | segment | state | count, the total
per block, and which blocks have no data. STOP for my OK.

Step 2 — write (after my OK):
- Write each count as an integer into its cell; keep the blue font; remove the yellow
  fill from every cell you fill.
- Set A2 to: "Accounts per state, scoring date <Mon YYYY>. Blue = counts from the scoring
  run; shares and coverage are calculated." Add " Yellow = to fill in." only if a block is
  still empty.
- Set wb.calculation.fullCalcOnLoad = True (Excel recalculates on open). Save the new file.

Step 3 — verify and report:
- Reopen the new file: every written cell equals the file; each block's sum equals the
  file's total.
- Every formula on the Results sheet is identical to the original file.
- Stabilized in the two 180+ blocks should be 0 (by design). If not, report it — do not
  change it.
- If LibreOffice is available, recalculate a COPY and confirm no #DIV/0!, #REF!, #NAME?.
- Report the new file's path.
```
