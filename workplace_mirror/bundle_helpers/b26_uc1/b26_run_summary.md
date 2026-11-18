# UC1 stated block (A5 / A6) - PROD run summary

Run: `kedro run --env=dev --pipeline=crx_{cc,rl}_uc1_stated`, 2026-11-18, one run per `model_id`.
Evidence below is the pipeline log for observation month **2026-08-31** only. Other months were not
inspected. Output tables: `crx_{cc,rl}_uc1_conversation_signals` and `crx_{cc,rl}_uc1_stated`
(paths include `model_id`, so runs do not overwrite each other).

## Evidence coverage (`uc1_evidence`)

| model_id | n | extracted | legacy_only | not_extracted | no_conversation |
|---|---|---|---|---|---|
| cc_60_180 | 19,292 | 991 (5.1%) | 66 | 4,848 (25.1%) | 13,387 (69.4%) |
| rl_60_180 | 3,985 | 364 (9.1%) | 24 | 755 (18.9%) | 2,842 (71.3%) |
| cc_180_plus | 318,663 | 184 (0.1%) | 82 | 389 (0.1%) | 318,008 (99.8%) |
| rl_180_plus | 55,371 | 145 (0.3%) | 21 | 173 (0.3%) | 55,032 (99.4%) |

## A5 stated ability

| model_id | able | partly_able | unable | not_stated | no_evidence |
|---|---|---|---|---|---|
| cc_60_180 | 127 | 419 | 144 | 301 | 18,301 |
| rl_60_180 | 34 | 156 | 49 | 125 | 3,621 |
| cc_180_plus | 36 | 47 | 15 | 86 | 318,479 |
| rl_180_plus | 24 | 35 | 17 | 69 | 55,226 |

## A6 stated intent

| model_id | pays_in_full | partly_or_later | refuses | not_stated | no_evidence |
|---|---|---|---|---|---|
| cc_60_180 | 191 | 543 | 38 | 219 | 18,301 |
| rl_60_180 | 74 | 210 | 6 | 74 | 3,621 |
| cc_180_plus | 50 | 63 | 5 | 66 | 318,479 |
| rl_180_plus | 29 | 50 | 6 | 60 | 55,226 |

## Checks (all four models pass)

- Evidence classes sum to n.
- A5 states other than `no_evidence` = `extracted`; the same holds for A6.
- `no_evidence` = `no_conversation` + `legacy_only` + `not_extracted`.

## Findings

1. **Only the 60-180 models carry usable signal.** About 30% of accounts have a conversation and A6 has
   real mass. At 180+ about 99.5% of accounts are `no_evidence`; this is a data limit, not a defect.
2. **`not_extracted` caps coverage.** Accounts with a conversation but no extraction outnumber
   `extracted` by about 4.9:1 on cc_60_180, about 2:1 on rl_60_180 and cc_180_plus, and about 1.2:1 on
   rl_180_plus. They all become `no_evidence` in A5/A6; only `uc1_evidence` keeps the distinction.
   Open question for the UC1 team: unprocessed calls, or filtered by the Stage 0 gate?
3. **`legacy_only` rows also map to `no_evidence`** (21-82 per model). Confirm that is intended.

## Run notes

- The rl_60_180 run hit JVM `pthread_create failed (EAGAIN)` / `OutOfMemoryError: unable to create
  native thread` in `build_crx_rl_uc1_stated`. Three Spark sessions were running concurrently on the
  host (SparkUI ports up to 4045), which is the likely cause. The node completed and the counts
  reconcile. A quiet rerun of rl_60_180 on its own is still pending.
- The cc_60_180 run logged a YARN executor loss (`User balzsv not found` on node `lvencdpdta059b`).
  Spark rescheduled and the run completed. Node-level infrastructure issue only.
