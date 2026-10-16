# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace (PROD) repository. Each prompt
is self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 → P2**, then P3 / P4 as the results require, then P5. P6 only once an
option is chosen.

---

## P0 — Orientation (paste first, every session)

```
You are working in our workplace repository on the "deterioration states" package in
docs/deterioration_states/. Read these first, fully, before doing anything:
  1. docs/deterioration_states/README.md
  2. docs/deterioration_states/METHODOLOGY.md
  3. docs/deterioration_states/dpd_states/config.py
  4. docs/deterioration_states/snippets/dpd_states_validate.py

What it is: one state per credit-card account in DPD buckets 4–7, assigned from the DPD
bucket-history string by a short decision tree (options A/B/C). The state logic and
thresholds are FINAL for this round — they were designed and validated elsewhere.

Ground rules — follow all of them:
- Do NOT change the state logic, thresholds or expectations in dpd_states/states.py or
  dpd_states/expectations.py unless a prompt explicitly asks you to. If you think one is
  wrong, say so and explain why; do not edit it.
- NEVER invent a dataset, table or column name. Find it in the repo (Kedro catalog
  conf/**/catalog*.yml, pipeline code, existing notebooks) or ask me. Leave <<FILL-IN>>
  where you cannot confirm a name.
- model_id is never hardcoded. It comes from the caller or the project globals
  (globals_dev). Find the real accessor in this repo.
- Read-only: nothing may be written to the warehouse. Results files contain aggregates
  only — no account keys, CIFs, names or row-level data.
- Never present a number you have not seen in actual output. If something has not run,
  say it has not run.
- Keep code changes minimal and confined to config.py and the clearly marked
  <<FILL-IN>> spots unless asked otherwise.

Reply with a 5-line summary of what the package does and which names need filling in.
```

---

## P1 — Wire up names and do the dry run

```
Task: make docs/deterioration_states runnable in this repo, then run the dry run.

1. Find the dataset that holds one DPD bucket-history string per credit-card account.
   Requirements (from config.py): it must have the account key and the DPD string; for
   the backtest it must still contain accounts that have since rolled to bucket 8+ or
   closed — not only today's bucket 4–7 spine. Search the Kedro catalog and pipelines.
   If several candidates exist, list them with their columns and ask me which to use.
2. Fill in dpd_states/config.py:
   - DS_STRINGS_TMPL (keep the "{model_id}." prefix only if the dataset is model_id
     namespaced), KEY, COL_DPD
   - COL_SNAPSHOT if the dataset has several snapshots per account; ROW_FILTER if it
     mixes products (we want credit cards only)
   - LEFTMOST_IS_CURRENT: check on real strings — the leftmost digit must be the
     current month. Verify against a current-bucket column if one exists.
   - CHAR_MAP / STRIP_CHARS if strings contain anything other than digits
   - DS_STRINGS_HAS_EXITED: False if the dataset only has today's spine
   - Optional columns, ONLY if they exist on the same dataset (or tell me they live
     elsewhere — do not build joins yet): credibility score and its three components,
     ability score, reachability and in-country flags, the bank's existing bust-out and
     stabilized flags, payment-holiday / restructuring flags. Flags must be 1/0.
3. Fill in _resolve_model_id in snippets/dpd_states_validate.py with the real
   globals_dev accessor from this repo.
4. Show me the diff of config.py and the snippet, then give me the notebook cell for
   main(catalog, check_only=True) (it is in the snippet docstring).
5. When I paste back the CHECK output, verify: counts are plausible, rows == accounts,
   example strings look right (leftmost = today, digits only), no WARNING lines. Fix
   config and repeat until clean. Do not start the full run until I say so.
```

---

## P2 — Full run and interpretation

```
Task: run the full validation and interpret it against the written expectations.

1. Give me the notebook cell: result = main(catalog)   (model_id from globals), or
   main(catalog, model_id="<variant>") for a specific variant.
2. When I paste back the block between === DPD_STATES OUTPUT START === and END (or point
   you to results/dpd_states_validation_<model_id>_<date>.json), read the JSON and .md.
3. Report, in this order:
   a. Any FAIL (E01, E02, E03). If present, STOP: diagnose and propose the config fix.
      Nothing else is trustworthy until these pass.
   b. Each WARN: the observed value, the expected range, and the "if_not_met" action
      written in the check. Say whether the action needs a config change, a decision from
      me, or nothing.
   c. The recommended option (B_balanced_6) scorecard from the backtest: share,
      roll_next_month, exit_8plus_within_k, same_state_next_month per state.
   d. Orthogonality: the eta² table and holding-vs-money-in. Name the largest overlap.
   e. Which option the data supports, using METHODOLOGY.md §8 "Choosing the option":
      E19b (relapse vs credibility clean point), E17 (gradual split size), E22 (residual
      clusters), E25 (outcome spread across the fixed states).
4. Keep it factual: every number you quote must come from the output. Mark anything
   you infer as an inference.
```

---

## P3 — Fix-up loop for WARNs (bounded)

```
Task: address the WARN checks from the last run, within strict limits.

Allowed without asking me:
- config.py changes (names, CHAR_MAP, STRIP_CHARS, filters, flags).

Allowed only after I approve, one at a time, each justified by a sweep table in the
report (section 6) and the check's "if_not_met" text:
- bust_max_history (sweep: bust_max_history), hold_min_in_band, relapse_min_prior_peak
  (spell from 3 vs 4, see E07), established_min.

Not allowed: changing the tree structure, adding or removing states, editing
expectations to make a check pass, using payment-promise / inflow / ability columns
inside states.py.

For each WARN: propose the smallest change, show the sweep row that supports it, predict
which checks it affects, and wait for my OK. After approved changes, give me the cell to
re-run and compare old vs new check tables.
```

---

## P4 — Compare with the bank's existing bust-out and stabilized rules

```
Task: compare this package's bust_out and holding with the bank's existing
implementations.

1. Find the existing bust-out and stabilized logic in this repo (search for
   "bust", "stabil", "dpd", pipeline nodes, SQL). List the files and quote the rules.
2. Translate each into the terms of METHODOLOGY.md §4 (history before the spell, earlier
   peak, run-up length, months within ±1 of today's bucket out of the last 6).
3. List every difference and its likely effect on the shares (E08/E09) and recall
   (E10/E11). If the existing flags are available as columns, wire them into
   EXISTING_RULE_COLS in config.py so the next run measures agreement directly.
4. Do not change states.py. If our definition should move toward the bank's, propose
   the parameter change for P3.
```

---

## P5 — One-page summary for the risk team

```
Task: write a one-page summary for the Group Retail Risk team from the latest
results/dpd_states_validation_<model_id>_<date>.json (and .md).

Audience: risk managers, not data scientists. No code, no eta², no ARI.
Structure:
1. What the states are (one line each) and the action each points to — use the table
   in METHODOLOGY.md §4, with the REAL shares from the results.
2. What the backtest shows: which states roll, which hold, how stable they are month to
   month — real numbers only.
3. How this fits with locatability, ability and credibility: where it adds information
   and where it overlaps (holding ↔ money coming in; relapse ↔ clean history).
4. The option we recommend (A/B/C) and why, in two sentences.
5. Open decisions for the risk team (METHODOLOGY.md §10), as questions.
Every number must come from the results file. Write it to
docs/deterioration_states/results/risk_summary_<model_id>_<date>.md.
```

---

## P6 — Productionise the chosen option (only after a decision)

```
Task: add the deterioration state as a pipeline output, using the option I name:
<A_minimal_4 | B_balanced_6 | C_detailed_7>.

1. Follow this repo's existing pipeline patterns (find a comparable node and copy its
   structure, naming, catalog entries and tests). Do not invent conventions.
2. The node takes the spine's DPD strings and returns: account key, snapshot date,
   state, option name, and the five assignment features (months_before_spell,
   max_prior_bucket, runup_len, runup_pays, last6_in_band) for auditability.
   Call dpd_states.features.build_features and dpd_states.states.assign_states — do not
   re-implement the logic. If the data is large, apply them per partition
   (mapInPandas / applyInPandas).
3. model_id from globals, never hardcoded; new catalog entries model_id-namespaced like
   the existing ones.
4. Ship a validation snippet to the same contract as snippets/dpd_states_validate.py:
   row counts, null rates, share per state, MECE check (exactly one state per account),
   agreement with the last validation run's shares (within 1pp), and a few example
   strings without keys.
5. Show me the diff and the catalog entries before anything runs.
```
