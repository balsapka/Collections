# UC1 integration inputs — prompt for the workplace Sonnet (UAT)

Paste this whole file. You work in UAT (no data). One part of the job is a PROD snippet that the
user runs and whose aggregate results you then read.

## Goal

We are about to build a small **UC1 "stated" block** in the `crx_persona` pipelines: two stated axes
(stated ability, stated intent) and two open-issue flags (dispute, relief request), per customer and
observation date, placed beside the four existing persona states in the persona output. It is built
by a different Claude session that **cannot see this repository, the UC1 team's repo or any data**.
Everything it knows about UC1 is `docs/context/reference/uc1_data_kb.md`.

Your job is to produce **one handoff file** that gives that session everything it needs to write the
pipeline without guessing a single name, column, value or path.

## Decisions already made (do not reopen)

- The four persona axes (A1–A4 / `SF_1..4`) and their states are fixed. Nothing in this job changes
  them.
- **We take the UC1 team's outputs as they are.** We do not re-implement their extraction, conflict
  resolution or aggregation over time, and we do not ask them to change anything. If something looks
  wrong in their logic, report it as a fact; do not fix it and do not propose a fix to them.
- The input level we want is the UC1 team's **customer-level aggregation**: the three tables
  `timelines/latest_flags`, `timelines/simple_signal_aggregation` and
  `timelines/signal_level_conflicts`. The user has asked the UC1 team to copy them into the shared
  store. The final 55-field output table is the fallback.
- We read **only** the shared copy
  `hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev/shared/05_feat/file_store`,
  never the UC1 team's own write locations.

## Hard rules

- No customer rows, ids, transcript or remark text anywhere: aggregates only. Mask any count below
  10 as `<10`.
- `model_id` only from `catalog.load("params:model_id")`; never hardcoded, no override argument. Put
  it in the results filename.
- Our own datasets are loaded through the catalog. The shared UC1 store has no catalog entries, so
  the snippet may read it with `spark.read.parquet` (as `tmp_validation/uc1_profile` did).
- Do not change any pipeline, node, catalog entry or parameter. The only files you add are the
  snippet, its results and the handoff, in the temporary tracked folder
  `tmp_validation/uc1_timelines/`.
- Never invent a name. If something cannot be found, write `NOT FOUND` and say where you looked.
- Mark every statement `[V]` (measured in PROD by the snippet), `[code]` (read in code, with
  `path:line` and the repo / branch / commit) or `[doc]` (from a document, with the path).

## Part A — from code and documents (UAT, now)

Find the code and answer these. Read the UC1 team's repo at whatever branch is current and state the
commit; the knowledge base was written from `origin/eda/explore-dcore @ dc75eb7e`.

**A1. The three `timelines` tables.** For each: the module and function that writes it, its write
path under `current/outputs/`, and then

- grain (the key columns), every column with type and meaning, every categorical column's full
  value set;
- which inputs it reads (transcript signals, remark signals, both; legacy-format rows in or out);
- **how time enters:** is a row "as of" a date (which column: an observation date, a run date, a
  parameter) or only the current state; which window lengths or recency parameters exist, their
  defaults and where they are set; whether past dates can be reproduced;
- how one value per signal is picked across a customer's conversations (latest, modal, ties,
  confidence, conservative order), exactly as coded;
- how these are told apart in the output: the signal was not detected in the customer's
  conversations / the customer has conversations but none was extracted / the customer has no
  conversation. Is there a row at all in each case?
- how `repayment_specifics` (amount, date, plan) and `request_type` are carried;
- how confidence is carried (high / low from extraction, or an aggregated high / medium / low);
- its build status: built and run, built but not run on current data, or designed only.

**A2. The final output table.** Paste `data/input/UC1/output_schema.md` **verbatim** into the
handoff (it is a schema, not data). Say whether any code builds this table yet, from which of the
tables above, and where its `SF_1..4` and `persona` columns come from (which of our datasets).

**A3. Our side.** From this repository:

- the node, pipeline and catalog entry that build the persona output (the table with the `SF_`
  columns); its grain and current column list; the registry name(s) it runs under; whether it is
  per `model_id`;
- the type of `cif_id` in `crx_cc_obs_base` and `crx_rl_obs_base` (string or numeric, padded or
  not);
- how a catalog entry could point at the shared store: is there a globals key for the `shared` root
  or for another project's root; is there any existing entry that reads outside this project's own
  model_id folders; which catalog file such entries belong in. Do not add one, just report the
  pattern and propose the exact entry text for the three tables;
- the current branch and `git log -1 --oneline`, and whether bundle 25 has been applied.

## Part B — PROD snippet (you write it, the user runs it)

Write a Kedro-notebook snippet in `tmp_validation/uc1_timelines/` that saves one aggregates-only
results file `uc1_timelines_results_<model_id>.md` into the same folder. Commit and push the
snippet; the user runs it in PROD and commits the results back.

The table profile is independent of `model_id`; the joins to our data are not. The user runs it for
`cc_60_180` first. Make the model-dependent blocks (B4–B6) cheap enough to repeat for the other
three model_ids.

If any of the three tables is missing from the shared store, the snippet says so for that table and
carries on with the rest. If all three are missing, it stops after B1.

**B1. Presence.** For each of the three paths: exists or not, number of files, latest modification
time.

**B2. Profile of each table.** Row count, distinct `cif_id`s, the physical schema as Spark reads
it, whether the grain found in A1 is unique (rows vs distinct keys), null share per column, min and
max of every date / timestamp column, and for every categorical column all values with counts.

**B3. Relation to the tables we already know.**
- `cif_id`s in `extracted_signals` (through `index`) that are missing from each timelines table, and
  the reverse.
- Whether legacy-format conversations (`model_version = 'legacy'`) and remark-only customers are
  represented.
- Per signal: customers with more than one level present at once, and how the table shows it.
- `cif_id` format: length distribution, share with a leading zero, any non-digit values.

**B4. Point in time (the deciding check).** With the `as of` column found in A1 (or, if there is
none, the latest conversation date behind each row, rebuilt from `index` / `metadata`): how many
rows rest on a conversation dated on or after a given month end, for each month end of the persona
window. State plainly whether a customer's value for a past observation date can be had without
later conversations.

**B5. Reach on the persona spine.** Load the obs base and the A1 and A3 outputs of the `model_id`
through the catalog. For the latest observation month and for each earlier persona month:
- rows and customers; share with a row in each timelines table; share with a non-empty capacity
  value; share with a non-empty intent value;
- the join rate of `cif_id` between the obs base and each timelines table, using the key format
  that B3 shows is right (report what you had to do to make the types match).

**B6. First sizes (latest month only, counts).**
- capacity value × `a1_state`;
- intent value × `a3_state`;
- dispute present / not, request present / not (with `request_type` if carried);
- for intent: with and without an amount or a date from `repayment_specifics`;
- each of the above split by the confidence value the table carries.

## Part C — the handoff (after the results are back)

Write `tmp_validation/uc1_timelines/uc1_timelines_handoff.md`. The user copies it out as it is, so it
must stand alone. Keep the knowledge base's style: short sections, `[V]` / `[code]` / `[doc]` on
every fact, numbers in tables, the sample warning where a number is a sample statistic.

Sections, in this order:

1. **What arrived.** Which of the three tables are in the shared store, with size and date (B1,
   B2).
2. **Table reference.** For each table the full answer to A1 with the measured schema and value
   sets from B2 next to the coded ones; every difference between code and data listed.
3. **Time.** The answer to "as of a date, or current only", with the B4 numbers. One sentence
   verdict: usable for every persona month / usable for the latest month only / not usable as is.
4. **No evidence.** How the three cases of A1 are told apart, confirmed on data.
5. **Key and join.** `cif_id` format on both sides, the join rate, what conversion is needed (B3,
   B5).
6. **Reach and first sizes.** B5 and B6 tables.
7. **Final output table.** The verbatim schema and the A2 answers.
8. **Our side.** The A3 answers: persona output node / pipeline / catalog entry and columns, obs
   base key type, the proposed catalog entry text for the shared tables, branch and head.
9. **Anything that would surprise the builder.** Facts that contradict
   `docs/context/reference/uc1_data_kb.md` or that a reader of that file would get wrong. Facts
   only, no design advice.
10. **Not found / not measured.**

Then tell the user the three files to commit (snippet, results, handoff) and that the folder
`tmp_validation/uc1_timelines/` is temporary.
