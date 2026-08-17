# Snippet Contract — how UAT sessions get data answers

**Claude runs in UAT, which has no data access.** Every question about the data is
answered by a snippet the user runs in PROD and pastes back. This file is the contract
for those snippets. Load it whenever a task needs data.

## The loop

```
UAT session  →  emits snippet  →  user runs in PROD  →  pastes output back
                                                      →  UAT session interprets,
                                                         applies decision rule,
                                                         logs to RESULTS.md
```

Each leg costs a session, so **a snippet should answer the whole task in one round
wherever possible.** Build in schema guards so a column surprise does not cost a
round trip.

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
5. **Cap printed output.** The user is copying results by hand. Print aggregates, not
   rows; hard-limit any row listing (≤ ~50 lines). If a result is inherently large,
   print a summary and say what a follow-up snippet could drill into.
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

# --- output -------------------------------------------------------------------
print("=== T## OUTPUT START ===")
print("scope: <state filters/sampling used>")
for r in res.limit(50).collect():
    print(r.asDict())
print("=== T## OUTPUT END ===")
```

## Interpreting returned output

When the user pastes results back:

1. Restate what was measured and over what scope, so a misread scope surfaces early.
2. Apply the card's **decision rule** explicitly — name which branch was taken.
3. Log to `RESULTS.md`: the headline number, the decision, and the **raw output**
   (under "Returned outputs") so later sessions do not need a re-run.
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
