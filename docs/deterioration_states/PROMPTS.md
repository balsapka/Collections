# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace repository. Each prompt is
self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 (file mode) → P2**, then P3 / P4 as the results require, then P5.
**P6 (Spark) and P7 (production)** only after the methodology and states are signed off.

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
   - min / median / max string length;
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

## P5 — One-page summary for the risk team

```
Task: write a one-page summary for the Group Retail Risk team from the latest results
file (and its .md).

Audience: risk managers, not data scientists. No code, no eta², no ARI.
Structure:
1. What the states are (one line each, display names) and the action each points to —
   use the table in METHODOLOGY.md §4 and §4.1 (EPD was formerly called bust-out; slow
   roller is also called partial payer), with the REAL shares from the results.
2. What the run shows — real numbers only. In file mode: shares, stability, data quality;
   say that outcomes need the Spark backtest.
3. How this fits with locatability, ability and credibility: where it adds information
   and where it overlaps (stabilized ↔ money coming in; repeat delinquent ↔ clean history).
4. The option we recommend (A/B/C) and why, in two sentences.
5. Open decisions for the risk team (METHODOLOGY.md §10), as questions.
Write it to docs/deterioration_states/results/risk_summary_<date>.md.
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
