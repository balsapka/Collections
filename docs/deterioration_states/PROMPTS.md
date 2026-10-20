# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace repository. Each prompt is
self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 (file mode) → P2**, then P3 / P4 as the results require, then P5.
**P6 (Spark) and P7 (production)** only after the methodology and states are signed off.
**P8 ships the reviewed PySpark pipeline (CC + RL)** into the existing Kedro code — it
replaces P7 for that work. Sonnet has no PROD data access: P8 is code changes and offline
tests only; the user runs the pipelines and `spark/prod_check.py` in PROD.

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
