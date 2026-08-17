# Snippet Contract — how UAT sessions get data answers

**Claude runs in UAT, which has no data access.** Every question about the data is
answered by a snippet the user runs in PROD and pastes back. This file is the contract
for those snippets. Load it whenever a task needs data.

## The loop

```
UAT session  →  emits snippet  →  user runs in PROD  →  results return (see below)
                                                      →  UAT session interprets,
                                                         applies decision rule,
                                                         logs to RESULTS.md
```

Each leg costs a session, so **a snippet should answer the whole task in one round
wherever possible.** Build in schema guards so a column surprise does not cost a
round trip.

## Two return channels — pick deliberately

| Channel | Use when | Mechanism |
|---|---|---|
| **A — paste-back** | Result fits in roughly 30 printed lines | Print between markers; user copies into the UAT session |
| **B — file hand-off** | Bigger, structured, or needed by later sessions | Snippet **writes a results file into the repo**; user commits and pushes from PROD, pulls in UAT; the next session reads the file directly |

**Always do both:** write the file *and* print a short headline summary. The summary
gives immediate feedback and often answers the decision rule on its own, so the user
can skip the commit when it is not worth it.

### File hand-off conventions

- **Location:** `docs/context/results/` (create if absent).
- **Name:** `T##_<short_name>_<YYYYMMDD>.json` — stable and sortable.
- **Format:** JSON for anything a later session must parse; add a `.md` sibling only
  if a human needs to read it directly.
- **Envelope:** always include `task`, `run_date`, `scope` (filters, sampling, date
  range) and `results`. Scope travels with the numbers so they cannot be misread later.
- **Size:** aggregates only. Cap at a few hundred rows — this goes into git, not a
  data lake. If a result is genuinely larger, aggregate harder or sample.

### ⚠ Data governance — aggregates only

These files get committed to a repository. **Never write customer-identifiable or
row-level data into them** — no account ids, CIFs, names, contact details, or
individual transactions. Aggregates, distributions, rates and counts only. Where a
sample of rows is genuinely needed for eyeballing (e.g. validating the spell table),
use surrogate ids or redact keys, and keep it to a handful of rows.

Confirm with the user that the repo is an approved location for portfolio-level metrics
before the first file hand-off.

## Hard requirements

1. **`catalog.load()` only.** Never hardcode paths, never construct readers directly.
   Put every dataset name in a named constant at the top so the user can correct them
   in one place.
2. **Never invent catalog names** (R9). Use `<<FILL-IN: description>>` and say in the
   preamble which names need filling.
3. **Schema-guard before computing.** Check required columns exist; if not, print the
   available columns and stop. This turns a failed round trip into a useful one.
4. **Aggregate in Spark; collect only the small result.** Never `.toPandas()` or
   `.collect()` a large frame — these are billion-row tables. Aggregate, then collect.
5. **Cap printed output.** Print aggregates, not rows; hard-limit any row listing
   (≤ ~50 lines). If the full result is larger, use channel B (file hand-off) and print
   only the headline summary.
6. **Read-only by default.** No writes, no table creation, no catalog saves unless the
   task explicitly calls for materialisation — and if it does, say so prominently in
   the preamble.
7. **Delimit the output** with `=== T## OUTPUT START ===` / `=== T## OUTPUT END ===`
   so the user knows exactly what to copy.
8. **Sample when a full scan is not needed.** State the sampling in the output so the
   result is interpretable. Prefer a bounded date range or a fraction sample over a
   full historical scan for exploratory questions.
9. **Self-contained.** One file, runnable top to bottom, no dependency on prior
   session state.

## Absolute rule: never fabricate results

If the user has not pasted output back, the task is **not done**. Never write plausible
numbers into `RESULTS.md`, never reason as if a query had run, never present an
expected result as an actual one. An un-run snippet is an open task.

## Template

```python
# ==============================================================================
# T## — <task name>
# Generated in UAT (no data access). RUN IN PROD.
# Paste everything between the OUTPUT markers back into the UAT session.
# READ-ONLY: this snippet writes nothing.
# FILL IN: <list the <<FILL-IN>> constants the user must set>
# ==============================================================================
from pyspark.sql import functions as F

# --- inputs -------------------------------------------------------------------
DS_ACCOUNT = "<<FILL-IN: catalog name for the account master>>"
DS_PAYMENT = "<<FILL-IN: catalog name for payments/postings>>"

acct = catalog.load(DS_ACCOUNT)
pay  = catalog.load(DS_PAYMENT)

# --- schema guard -------------------------------------------------------------
REQUIRED = {"acct": ["account_id", "account_type", "close_date"],
            "pay":  ["account_id", "posting_date", "amount", "posting_type"]}
for name, df in (("acct", acct), ("pay", pay)):
    missing = [c for c in REQUIRED[name] if c not in df.columns]
    if missing:
        print(f"SCHEMA MISMATCH in {name}. missing={missing}")
        print(f"available={sorted(df.columns)}")
        raise SystemExit

# --- computation (aggregate in Spark, collect small) --------------------------
res = (acct
       .where(F.col("close_date").isNotNull())
       .groupBy("account_type")
       .agg(F.count("*").alias("n_closed"))
       .orderBy("account_type"))

# --- output: file hand-off + printed summary ----------------------------------
import json, datetime, pathlib

rows = [r.asDict() for r in res.limit(500).collect()]   # aggregates only, capped

OUT_DIR = pathlib.Path("<<FILL-IN: repo path, e.g. docs/context/results>>")
OUT_DIR.mkdir(parents=True, exist_ok=True)
run_date = datetime.date.today().isoformat()
out_path = OUT_DIR / f"T##_<short_name>_{run_date.replace('-','')}.json"
out_path.write_text(json.dumps({
    "task": "T##",
    "run_date": run_date,
    "scope": "<filters, sampling, date range actually used>",
    "results": rows,
}, indent=2, default=str))

print("=== T## OUTPUT START ===")
print(f"scope: <state filters/sampling used>")
print(f"wrote: {out_path}  ({len(rows)} rows)  -> commit & push from PROD, pull in UAT")
for r in rows[:20]:            # headline only; full detail is in the file
    print(r)
print("=== T## OUTPUT END ===")
```

If the whole result comfortably fits in the printed block, the file write is optional —
say so in the preamble so the user does not commit for nothing.

## Interpreting returned output

When results come back — pasted, or as a file pulled into UAT:

1. If a file, **read it directly** from `docs/context/results/`. Check its `scope`
   field before using the numbers.
2. Restate what was measured and over what scope, so a misread scope surfaces early.
3. Apply the card's **decision rule** explicitly — name which branch was taken.
4. Log to `RESULTS.md`: the headline number, the decision, and either the raw output
   (small results) or the **path to the results file** (large ones), under "Returned
   outputs" — so later sessions never need a re-run.
4. Update the task status in `TASKS.md`.
5. If the result invalidates a plan assumption, add a note under "Proposed amendments"
   rather than silently re-planning.

## Build tasks (pipeline code, not diagnostics)

Code for the build tasks is written blind in UAT and cannot be executed there. So each
build task ships **two** things:

1. The pipeline code itself, following the repo's existing patterns.
2. A **validation snippet** to the same contract, which the user runs in PROD to check
   it: row counts, null rates per column, the card's invariant tests, and a small
   sample of output rows for eyeballing.

The build task is not done until the validation snippet's output has come back clean.
Expect at least one fix round — write the validation snippet to surface *what* broke,
not just that something did.
