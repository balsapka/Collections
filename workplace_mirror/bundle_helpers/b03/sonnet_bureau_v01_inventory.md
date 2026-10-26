# Bureau v01: inventory (Sonnet part A, transcribed)

Source: workplace `tmp_validation/bureau_v01/inventory.md` (photos IMG_8396–8399) and the
Sonnet's end-of-session note (IMG_8400), 2026-10-26. The snippet `bureau_v01_snippet.py`
(tests w1–w8 against hypotheses B0–B4, writes `results_<model_id>.json`) and README are
written; **not run in PROD yet, nothing committed** — part C (`summary.md`) waits on the run.
Condensed; file:line references are the workplace's.

## A.1 Every AECB dataset

- **Raw** (`catalog_raw_aecb.yml`, source `DPL_UAE_OPERATIONS`), daily `edp_load_date`
  partitions 2022-01-01 → 2026-10-13 (`data/input/bureau_partitions.md:6`):
  `sa_ops_aecb_alert` (89.77M rows, 1,540 partitions), `..._alert_othprv_sub` (43.16M/1,539),
  `..._subj_court_case` (77,957/1,311), `..._subj_cntrct_link` (1.30M/2,153),
  `..._subj_pymnt_order` (1.47M/2,239), `..._subj_con_tot_smry` (4.65M/1,352),
  `..._subj_crdt_score` (5.35M/2,142), `..._sub_sal_cr_hist` (148.14M/1,198),
  `..._subj_cntrct_dtl` / `_cntrct_hist` (69.1M/995.2M). 16 more raw entries have zero
  pipeline consumers.
- **Staging** (`catalog_outputs.yml:124-166`, `pipelines/bureau/staging.py:17-89`): credit
  score, consolidated summary, contract history / detail, salary history, contract link,
  court case, payment order, `stg_aecb_alert` (← `sa_ops_aecb_alert` + `scope_cifs`), reference,
  alert other-provider sub.
- **Primary** (`catalog_outputs.yml:479-501`, `prm_bureau.py`, `pipelines/bureau/primary.py:17-55`):
  `prm_bureau_cif_bridge` (`stg_aecb_alert` + contract link; grain `bureau_file_id ×
  edp_load_date → cif_id`), `prm_bureau_alert_enriched` (`build_alert_enriched` + product
  mapping), `prm_bureau_credit_score` / `_consolidated_summary` / `_court_case` /
  `_payment_order` (each staging joined via `_join_cif_bridge` on `bureau_file_id ×
  EDP_LOAD_DATE`, `prm_bureau.py:218-247`).
- **Intermediate** (`pipelines/bureau/intermediate.py:23-42`): `int_bureau_alert_monthly`
  (← `prm_bureau_alert_enriched` + other-provider sub; grain `cif_id × alert_date`,
  `alert_date = to_timestamp(extract_date)`), `int_bureau_pull_monthly` (casts
  `edp_load_date` → `pull_date`, a known mislabel).
- **Feature** (`pipelines/bureau/features.py:35-72`): `feat_bureau_alert`, `feat_bureau_pull`,
  `feat_bureau_snapshot` → joined into `feat_bureau`. **WM:** `fea_monthly_aecb_alerts`
  (`retail.feature_space`'s `aecb_alert_monthly_pipeline.py`, from raw
  `prvdr_subj_num` / `alert_desc` / `contract_type` / `extract_dt` only; `month_number` =
  month end of `extract_dt`; no return / settlement date, no amount-repeat dedup).
- **`feature_retail_loans`' bureau input:** `prm_application_aecb_metric` ← `stg_rr_aecb_metric`
  ← raw `bo_rr_aecb_metric` (RL application only) — see A.4.

## A.2 What the repo says about the alert feed

- `stg_aecb_alert.py:4` says the grain is **`ALERT_PROCESS_ID × edp_load_date`**, "real-time
  event stream" (`:7`); `EXTRACT_DT` "for temporal analysis" (`:14`). The `BureauAlertEnriched`
  docstring: "one row per alert event" (`src/data_engineering/primary/models/bureau.py:844`)
  — the documented position is **B0 (event notification)**, asserted, not derived; nothing
  enforces or tests it.
- Countering evidence (T35, `RESULTS.md:224`): `EXTRACT_DT` / `edp_load_date` /
  `ALERT_PROCESS_ID` take 1,433 / 1,223 / 1,444 distinct values across 66.8M rows — "a near
  1:1 correspondence that is the signature of a shared per-batch stamp, not a per-record pull
  timestamp". Daily partitions fit either B0 or B1; this does not settle it alone.
- `ALERT_DESC` / `alert_type_flag`: 72 distinct raw values; `int_bureau_alert_monthly.py:19-40`
  pivots 19 high-signal types including `"bouncedcheque"` — a dedicated bounce alert type
  exists, not just the amount field.
- `OPN_DT` = open date (`stg_aecb_alert.py:67`), generic contract / alert open.
- **`DT_OF_RETURN` = return date (`:69`)**: same null share as `BOUNCED_CHK_AMT` (98.8% each,
  i.e. populated exactly on bounced rows) but only **1,399 distinct values** across ~801K
  populated rows — low cardinality for a per-event date, the same batch-stamp suspicion as
  `edp_load_date` (unconfirmed; w4/w5 test it). `CONTRACT_STATUS_DT` 99.9% null / 1,057
  distinct, generic.
- **`build_alert_enriched` (`prm_bureau.py:95-146`) renames `DT_OF_RETURN` → `return_date` and
  `CONTRACT_STATUS_DT` → `contract_status_date` (`_ALERT_RENAMES`, lines 105-106), but
  `BureauAlertEnriched` has no such fields, so the final projection silently drops both** —
  confirmed dead end in the output (`a1_v01 summary.md:68-72`).
- `crx_persona/a1_ability/signals.py:293-295` states the working assumption almost verbatim:
  bureau bounces dated by `extract_date`, the pull date, "a bounce can repeat in later pulls" —
  an assumption, not a verified fact.
- **Separately:** `prm_bureau_payment_order` (`stg_aecb_secondary.py:127-150`,
  `prm_bureau.py:470-533`) is a dedicated NSF / bounced-cheque table (1.1M rows) with its own
  dates: `return_date` ← `subj_pymnt_ord_return_dt`, `reference_date` ← `..._ref_dt`,
  `cheque_settlement_date` ← `subj_pymnt_cheq_setl_dt` (92.7% null). `signals.py:311-320`
  already unions it optionally via `return_date` + `reason_code`, flagged "not in PROD yet"
  (`:297`). No null / cardinality check has run on these 3 fields.

## A.3 `stg_aecb_alert` columns (raw names, as staged)

30 kept of 42 source columns (`stg_aecb_alert.py:38-78`); type / null% / distinct from the
66.8M-row `external_aecb` profile (the bureau-domain profile was taken at 0 rows):
`ALERT_PROCESS_ID` string 0.0% / 1,444; `edp_load_date` date 0.0% / 1,223;
`REC_CORR_FLG`, `ENTITY_CD` constant; `ALERT_REC_ID` double 0.0% / 465,399;
`PRVDR_SUBJ_NUM` string 0.0% / 3,242,525 (= CIF); `CB_SUBJ_ID` 0.0% / 2,819,651;
`CB_TRIG_ID` 8.9% / 23,622,722; `PRVDR_CD` 0.0% / 8; `ALERT_TYP_NUM` 0.0% / 55;
`ALERT_DESC` 0.0% / 72; `SUBJ_ROLE` 10.4% / 6; `CONTRACT_TYPE` 39.6% / 118;
`PRD_TYPE_CD` 100% null (sample); `CONTRACT_BAL_AMT` 91.1% null; `OVERDUE_AMT` 91.5%;
`TOTAL_AMT` 86.5%; `CREDIT_LIMIT_AMT` 75.3%; `BILLED_AMT` 97.2%; `BOUNCED_CHK_AMT` 98.8% /
64,859; `SALARY_CRED_AMT` 72.0%; `OPN_DT` timestamp 68.3% / 12,143; `EXTRACT_DT` timestamp
0.0% / 1,433; `DT_OF_RETURN` timestamp 98.8% / 1,399; `CONTRACT_STATUS_DT` 99.9% / 1,057;
`SUSP_ACT_FLG_DT` 100% / 494; `COURT_CASE_CLS_DT` 96.0% / 2,190; `ACCT_STATUS` 100% null
("unusable", `stg_aecb_alert.py:74`); `SUBJ_REL_TYPE` 100% null (sample); `SRC_FILE_NM`
0.0% / 1,557. Dropped: PII (5), metadata (6), confirmed-null (`BRANCH_ID`, `DIRECT_DBT_AMT`,
`COURT_CASE_CTG_CD`, `WARN_ERR_DESC`, `ALERT_DATE`, all 100% null; `stg_aecb_alert.py:93-98`).

**Candidate row key:** none found. `ALERT_PROCESS_ID` alone is not unique per the documented
grain; `ALERT_REC_ID` (465K distinct vs 66.8M rows) looks per-record but its relationship to
`ALERT_PROCESS_ID` / `edp_load_date` is untested. w2 checks `(ALERT_PROCESS_ID,
edp_load_date)`, `(ALERT_PROCESS_ID, ALERT_REC_ID)`, `(PRVDR_SUBJ_NUM, CONTRACT_TYPE,
ALERT_DESC, edp_load_date)`, with and without `EXTRACT_DT`.

## A.4 `feature_retail_loans.aecb_bureau_pull_date` / `aecb_direct_debit_returns_6m`

Both RL-application-only, unrelated to the alert feed. Chain: raw `bo_rr_aecb_metric` (RL-only
AECB application pull; genuine per-record pull date per T35) → `stg_rr_aecb_metric` →
`prm_application_aecb_metric` (`prm_external_risk.py:113-179`) → `feat_loan_application_risk.py`.
`aecb_bureau_pull_date` ← `aecb_report_dt` — a real per-record pull timestamp, not a batch
stamp. `aecb_direct_debit_returns_6m` ← raw `dd_return_6m_cnt` ("Payment behavior (1)") — a
**bureau-supplied count already aggregated over a trailing 6-month window at pull time**; no
window logic here. Both joined to the observation spine by the latest `bureau_pull_date <=
observation_date` (`feat_loan_application_risk.py:1-13`, `build_cif` ~lines 204-214) —
point-in-time correct, a single snapshot per account in practice (0.0277% multi-pull).
