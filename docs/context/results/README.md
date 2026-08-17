# PROD run results

Results files written by PROD snippets (channel B in
`../reference/snippet_contract.md`). Flow:

1. A UAT session emits a snippet that writes its results here.
2. You run it in PROD, then **commit and push** from PROD.
3. **Pull in UAT** — the next session reads the file directly instead of you pasting
   it by hand.

Naming: `T##_<short_name>_<YYYYMMDD>.json`

Every file carries `task`, `run_date`, `scope` and `results`. **Check `scope` before
using the numbers** — it records the filters, sampling and date range actually used.

## ⚠ Aggregates only

These files are committed to a repository. They must contain **no customer-identifiable
or row-level data** — no account ids, CIFs, names, contact details or individual
transactions. Aggregates, distributions, rates and counts only. Where a few sample rows
are genuinely needed (e.g. eyeballing derived spells), use surrogate ids or redact keys.

Confirm this repo is an approved location for portfolio-level metrics before the first
file lands here.
