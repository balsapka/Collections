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

**Portfolio-level aggregates in the repo are approved** (confirmed 2026-08-16) —
distributions, rates, counts, segment grids, metric tables.

**Never write customer-identifiable or row-level data into them** — no account ids,
CIFs, names, contact details, or individual transactions. Where a sample of rows is
genuinely needed for eyeballing (e.g. validating the spell table), use surrogate ids or
redact keys, and keep it to a handful of rows.

## Where snippets live and how they run

**Every snippet is a module under `docs/context/snippets/`**, named
`t##_<short_name>.py`. Never loose scripts, never inline-only code in chat.

**Each module exposes `main(catalog, ...)`.** The user runs it in a **Kedro notebook**,
where `catalog` is already defined:

```python
import sys; sys.path.insert(0, "docs/context/snippets")
from t02_transaction_retention import main
result = main(catalog)
```

So: no `KedroSession` bootstrap, no path juggling, no `if __name__ == "__main__"`
entry point. `catalog` arrives as an argument. `main()` prints the summary, writes the
results file when the result warrants it, **and returns the payload** so the user can
inspect it in the notebook without a re-run.

Put the run instructions in the module docstring — the user should not have to
reconstruct the import line.

## Scope first — never scan raw tables unscoped

These are billion-row tables and we care only about a small target population.
**Filtering to scope is the first operation, before any other logic.** An unscoped scan
is a defect, not an inefficiency.

Preference order — take the earliest that answers the question:

1. **The spine datasets.** They already carry the spine id, date columns and
   delinquency info, and are scoped by construction. Many diagnostics can be answered
   from the spine alone with no raw table touched at all. **Check this first.**
2. **Scoped outputs from the spine pipelines** — the `model_id`-namespaced datasets
   (`scope_accounts`, `scope_cifs`, or whatever they are actually called). Semi-join
   raw down to these before anything else.
3. **Raw tables, scoped.** Only for columns the above do not carry, and only after the
   semi-join.
4. **Raw unscoped** — never.

Discover the real dataset names in the repo catalog (R9); do not guess them. Put the
`model_id` and scope dataset names in `<<FILL-IN>>` constants at the top so the user
corrects them in one place.

### Two exceptions to be deliberate about

**1. Retail loans 180+ has no spine/scope pipeline yet.** Every other segment does.
For that segment, build an **ad-hoc scope** in the snippet from explicit filters
(product, DPD band, date), keep it as a named DataFrame at the top exactly where a
`catalog.load` would have been, and state `"ad-hoc scope: <filters>"` in the payload's
`scope` field. Never silently fall back to an unscoped scan, and never present its
numbers as comparable to spine-scoped ones without saying so.

**2. Pick the scope that matches the question.** A modelling spine may already carry
modelling exclusions, which makes it the wrong denominator for a *sizing* question —
"how much is recoverable in this segment" needs the business population, not the
modelled one. Use the spine for model-related diagnostics; use a business-population
filter for sizing, and **always record which in the `scope` field.** If both are cheap,
report both and note the difference — the gap between them is itself informative.

```python
scope = catalog.load(DS_SCOPE).select("account_id").distinct()
raw   = catalog.load(DS_RAW)
df    = raw.join(F.broadcast(scope), "account_id", "leftsemi")   # scope FIRST
```

Broadcast the scope side when it is small enough (a few hundred thousand keys usually
is); otherwise let Spark plan the semi-join normally.

## Hard requirements

1. **`catalog.load()` only.** Never hardcode paths, never construct readers directly.
   Put every dataset name in a named constant at the top so the user can correct them
   in one place. `catalog` is a parameter of `main()`, never a global lookup.
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
9. **Self-contained.** One module under `docs/context/snippets/`, importable and
   runnable via `main(catalog)`, with no dependency on prior session state.
10. **Scope before anything else.** Spine first, then `model_id` scope datasets, then
    scoped raw. Never an unscoped raw scan.

## Absolute rule: never fabricate results

If the user has not pasted output back, the task is **not done**. Never write plausible
numbers into `RESULTS.md`, never reason as if a query had run, never present an
expected result as an actual one. An un-run snippet is an open task.

## Template

`docs/context/snippets/t##_<short_name>.py`

```python
"""T## — <task name>.

Generated in UAT (no data access). Run in a Kedro notebook where `catalog` exists:

    import sys; sys.path.insert(0, "docs/context/snippets")
    from t##_<short_name> import main
    result = main(catalog)

READ-ONLY: writes nothing to the warehouse.
FILL IN before running: MODEL_ID, DS_SCOPE, DS_RAW
"""
import datetime
import json
import pathlib

from pyspark.sql import functions as F

# --- catalog names — FILL IN (discover in the repo catalog, never guess) -------
MODEL_ID = "<<FILL-IN: model_id namespace used by the spine pipelines>>"
DS_SCOPE = f"{MODEL_ID}.<<FILL-IN: spine or scope_accounts dataset>>"
DS_RAW = "<<FILL-IN: raw table — only if the spine cannot answer this>>"

OUT_DIR = pathlib.Path("docs/context/results")
KEY = "account_id"


def main(catalog, sample_frac=None):
    # 1. SCOPE FIRST — never touch a raw table before this ---------------------
    scope = catalog.load(DS_SCOPE).select(KEY).distinct()
    if sample_frac:
        scope = scope.sample(fraction=sample_frac, seed=42)

    # 2. filter raw down to scope before any other logic -----------------------
    raw = catalog.load(DS_RAW)
    required = [KEY, "<<col_a>>", "<<col_b>>"]
    missing = [c for c in required if c not in raw.columns]
    if missing:                                   # schema guard: fail usefully
        print(f"SCHEMA MISMATCH. missing={missing}")
        print(f"available={sorted(raw.columns)}")
        return None
    df = raw.join(F.broadcast(scope), KEY, "leftsemi")

    # 3. aggregate in Spark; collect only the small result ---------------------
    res = df.groupBy("<<col_a>>").agg(F.count("*").alias("n"))
    rows = [r.asDict() for r in res.limit(500).collect()]

    scope_note = f"scoped to {DS_SCOPE}" + (f", sampled {sample_frac}" if sample_frac else "")
    payload = {
        "task": "T##",
        "run_date": datetime.date.today().isoformat(),
        "scope": scope_note,
        "results": rows,
    }

    # 4. file hand-off + printed summary --------------------------------------
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"T##_<short_name>_{payload['run_date'].replace('-', '')}.json"
    out.write_text(json.dumps(payload, indent=2, default=str))

    print("=== T## OUTPUT START ===")
    print(f"scope: {scope_note}")
    print(f"wrote: {out} ({len(rows)} rows) -> commit & push from PROD, pull in UAT")
    for r in rows[:20]:                           # headline only; detail in the file
        print(r)
    print("=== T## OUTPUT END ===")

    return payload
```

If the whole result comfortably fits in the printed block, skip the file write and say
so in the docstring, so the user does not commit for nothing.

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
