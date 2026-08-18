# PROD run results

Results files written by PROD snippets (channel B in
`../reference/snippet_contract.md`). Flow:

1. A UAT session emits a snippet that writes its results here.
2. You run it in PROD, then **commit and push** from PROD.
3. **Pull in UAT** — the next session reads the file directly instead of you pasting
   it by hand.

Naming: `T##_<short_name>_<model_id>_<YYYYMMDD>.json`

The **model_id is in the filename** so the same script can be run across every model_id
variant without one run overwriting another — several files per task is normal and is
how the full cross-variant picture gets assembled.

Every file carries `task`, `run_date`, `model_id`, `scope` and `results`. **Check
`model_id` and `scope` before using the numbers** — they record which variant was run
and the filters, sampling and date range actually used.

## ⚠ Aggregates only

**Portfolio-level aggregates in this repo are approved** (confirmed 2026-08-16).

What that permits: distributions, rates, counts, segment grids, metric tables.

What it does **not** permit: customer-identifiable or row-level data — no account ids,
CIFs, names, contact details or individual transactions. Where a few sample rows are
genuinely needed (e.g. eyeballing derived spells), use surrogate ids or redact keys.
