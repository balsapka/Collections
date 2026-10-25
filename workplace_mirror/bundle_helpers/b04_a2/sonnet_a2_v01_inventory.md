# A2 v01 — inventory (part A), workplace Sonnet, 2026-10-25

Transcribed from photos of `tmp_validation/a2_v01/inventory.md` (35 lines; condensed only where
the screen wrapped). File:line references are the workplace repo's.

## A.1 Location features — existing datasets

- `feat_cc_txns_rfs` = `fea_cc_inflow_outflow_txns_monthly` (retail.feature_space). Grain
  `cif_id` × `month_number` (yyyyMMdd last day). Cols `outflow_cc_mcc_travel_and_tours_amt` /
  `_count` (`cc_departure_signature/nodes.py:144-145`, Pass H2 `nodes.py:1719-1836`). Catalog
  `catalog_raw_retail_feature_space.yml:39-42`. "Foreign" = MCC category "Travel and Tours"
  (`retail.feature_space/.../transactions.py:370-376`).
- `feat_fx_leakage` = `fea_monthly_agg_fx_leakage` (retail.feature_space). Same grain. Col
  `ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum` (`nodes.py:136`, Pass H
  `nodes.py:1603-1713`). Catalog `catalog_raw_retail_feature_space.yml:52-55`. "Foreign" =
  currency mismatch (`country_native_currency != actual_tran_crncy`,
  `fx_leakage_detection.py:491,707-709`). No count column.
- `prm_digital_login_monthly` is built **in-repo** from raw OMB tables, not from
  retail.feature_space's intermediate: "retail.feature_space drops `countrylocation` /
  `countrycode` at its intermediate step — no reuse possible" (`RESULTS.md:434`). Builder: A.5.
- **New, unassessed (R14 gap, never screened):** `fea_credit_card_international_transactions_by_cif`
  (WM) — `cif_idxweek_number`; foreign = `txn_code == foreign_currency_transactions_code`
  (`casa_cc_transaction.py:1824-1930`; catalog `wealth_management/conf/base/catalog.yml:1902-1905`).
  `fea_casa_cc_international_spend_by_cif` + `fea_days_since_last_international_case_cc_txns` —
  `cif_idxweek_number`; foreign = `intl_flag_by_iban` OR `intl_flag_by_loc` (col
  `transaction_location`) (`casa_cc_transaction.py:182-271`; catalog `:1972-1974` / `:2140-2142`).
  Both live in WM's own model (`pipeline_staging.py:132,148-149`); no CC-coverage / T0 screen
  exists for either.
- RL CASA travel MCC (mirrors CC Pass A): `rl_departure_signature/nodes.py:522-654`, source
  `comp_financial_tran_repos_dly.merchant_category`, reuses CC's `_TRAVEL_MCCS`.
- R7-blocked: `ft_isexpat` (both sibling repos), `ft_nationality_group`.
- In-repo `is_international` (Way4) is **not** country-code based despite `feature_specs.md:339-340`
  saying so — actual `regexp_extract(add_info, "DOMESTIC=(.)")` (`prm_cc.py:375-381`);
  `trans_country_code` dropped at staging, < 1% fill (`stg_transaction.py:37`). Spec / impl
  mismatch, not fixed here (R19).
- NOT FOUND: no merchant-country column anywhere in retail.feature_space (grep clean); no
  dormancy / offshore location feature in either sibling repo.
- "Unfit" quotes: `RESULTS.md:434` (login, above). `T01_reuse_map.md` A4§3.3
  `travel_mcc_flag_90`: "Sibling repo… uses a different category grouping and cannot be changed —
  sibling source dropped; derive from raw MCC." `T01_reuse_map.md` A2§4.1/A4§3.3
  `foreign_login_flag`: "Geographic login data absent from both repos. Confirmed BUILD."
  `RESULTS.md:363` (T06 PASS): "`ft_isexpat` found in both repos but R7-blocked."
  `domain_and_decisions.md:79-80`: WM "serves an affluent population that may barely intersect
  ours" (general coverage caveat). The 3 new WM candidates have **no** unfit verdict — a genuine
  T01 gap, not screened-and-dropped.

## A.2 Transaction sources

- **Card:** `crx_cc_transactions` (`catalog_crx.yml:19-24`), built by `build_cc_transactions`
  (`cc_raw_extract/nodes.py:34-123`) from `raw_transaction` (Way4, `catalog_raw_way4.yml:35-38`)
  + `crx_cc_spell_table`. Cols `contract_id`, `observation_date` (= txn date, ← `banking_date`),
  `is_international` (regex on `add_info`), `merchant_category_code` (← `trans_mcc`),
  `txn_description`, `txn_amount_aed` (sign: > 0 purchase / < 0 payment, no D/C col),
  `txn_category`. **No merchant-country column.** `prm_transaction`
  (`catalog_outputs.yml:429-431`) exists but isn't this table's input.
- **CASA (a):** `wm_pri_labelled_transactions_indicators_by_week`
  (`catalog_casa_plus_ftr.yml:28-31`, `week_number`-partitioned). Cols (schema-intelligence
  profile): `cif_id`, `acid` / `transaction_acid`, `tran_date`, `channel_desc` /
  `channel_tran_type`, `mcc_country` / `receiver_ctry` / `sender_ctry` / `home_country_flag`,
  `mcc_code` / `mcc_type`, `in_out_flow`, `tran_amt`.
- **CASA (b):** `comp_financial_tran_repos_dly` (`catalog_raw_dpl.yml:9-14`,
  `dpl_uae_compliance.COMP_FINANCIAL_TRAN_REPOS_DLY`). Pass B today selects only `cif_id` /
  `tran_date` / `tran_amt_aed` / `tran_dc` / `tran_particular_code` / `tran_narration_1`
  (`nodes.py:828-873`) — `merchant_category` / `merchant_country` / `counter_party_bank_cntry` /
  `channel_desc` exist on the source (~49–93% null) but no current node pulls them.
- **Supplementary cards:** `stg_card.py:29,37` `sequence_number` (1 = primary, 2+ =
  supplementary) + `main_card_flag`; `prm_cc.py:523-539` derives `is_main_card`.
  `crx_cc_transactions` / `prm_transaction` are **contract-grain** — supplementary spend is not
  separable there. WM's `credit_card_master` (`business_filters.py:435-465`) collapses multiple
  cardholders per account to one primary before the CIF join — `wm_pri_labelled_transactions.cif_id`
  is already primary-resolved. `comp_financial_tran_repos_dly` has no card / role column (CASA grain).

## A.3 DCORE

- `dcore_observation_spine` (`catalog_outputs.yml:1168-1170`; builder
  `stg_dcore_observation_spine.py:24-92`). Cols `agreement_id`, `cif_id`, `account_id`
  (← `contract_id`), `observation_date` (sourced from `cc_spine` / `rl_spine` directly —
  billing / spine dates, not independently computed). **Grain = one row per (account_id,
  observation_date)**: a window dedups multi-agreement accounts to the latest `agreement_id`
  (lines 69-84) — never fans out. RL reuses the **same catalog slot** (`retail_loans/spine.py:225`),
  adding only a 24-month floor on followup. Pipeline docstrings
  (`cc_a2_locatability/pipeline.py:21`, `cc_a3_payment_credibility/pipeline.py:15`) still say
  "contract_id" — stale vs. real `account_id` (doc defect, R19, not fixed here).
- `dcore_stg_scope_agreements` (`catalog_outputs.yml:170-172`; `stg_dcore_scope_agreements.py:22-37`)
  — single col `iagreementseqno`, distinct `agreement_id` from the spine. No `observation_date`.
- `dcore_prm_followup_outcomes` (`catalog_outputs.yml:535-537`; `prm_dcore.py:217-257`
  `build_followup_outcomes`). Cols `agreement_id`, `activity_seqno`, `action_code`
  (← `szactioncode`), `action_ts` (← `dtaction`), `result_code`, `result_name`,
  `result_category`, `result_ts`, `contact_mode`, `contact_place`, `agent_id`, `updated_at`.
  `result_name` / `result_category` **are** on disk — decoded via a join to
  `stg_dcore_mst_result` once at build time (`prm_dcore.py:249-255`); no downstream join needed.

## A.4 Deceased sources

- `prm_contract` (`catalog_outputs.yml:441-443`, Way4 / CC only). Builder
  `credit_card_way4/primary.py:34-44` → `prm_cc.py:473-521`. Grain `ContractSnapshot`
  (`flows.py:523-544`) — **one row per contract per `observation_date`** (SCD2-style; no dedup in
  this node). `block_code_1/2` pass through untouched (`prm_cc.py:81-90`). Vocabulary:
  X = B0, V = B1, W = B2 (blocked), Y = B3, U = B4, Q = B5, Z = writeoff (`flows.py:536`) — `D`
  not in this documented set (org-specific suffix, per `constants.py`). **Open anomaly (T34):**
  `cc_180_plus` join matched **0 / 318,663** rows (`RESULTS.md:336,470`); root cause
  undetermined, not re-diagnosed here.
- `feat_demographics_cif` (`catalog_outputs.yml:1127-1129`; `feat_demographics_cif.py:29-130`).
  Grain: **`cif_id`, one row** — pure static select, **no `observation_date` column at all**, no
  window / dedup. `ft_deceased_flag` ← `deceased_flag` (`prm_demographics.py:91`) ←
  `cust_deceased_flg` (`stg_customer_individual.py:50,99`), source `ec_customer_indv_corp`,
  filtered `edp_activeind = 'Y'`, no SCD2. A `dedup_latest` import exists but its call is
  commented out (lines 85-94) — grain is assumption-based, not enforced.

## A.5 `prm_digital_login_monthly`

Pipeline `digital_login/pipeline.py:22-39`: raw `raw_digital_login_data`
(`cl_omb_group_reports.login_data_ebi`), `raw_digital_login_data_history`
(`tdv_omb_uae_ebi.loginlog`), `raw_digital_user_data` (`tdv_pdm_uae_ebi.users`) —
`catalog_raw_digital.yml:48-67`. Staging (`stg_digital_login.py`): raw is **one row per login
session** (`dropDuplicates(["sessionid"])`, ~105-108) — not pre-aggregated. Primary
`prm_digital_login_monthly.py:29`: `month_number = date_format(last_day(login_date), "yyyyMMdd")`
(40-43) — **month-end**, string. `last_login_date` / `last_login_foreign_flag` /
`last_login_country` via `row_number()` over `partitionBy(cif_id, month_number).orderBy(login_date
desc)`, `rn = 1` (46-59); `foreign_login_cnt` / `total_login_cnt` / `any_foreign_login_flag` are
separate monthly aggregates joined back (62-68, 71). Confirms `cc_a2_locatability/nodes.py:383`'s
`to_date(month_number, "yyyyMMdd")` parse is correct.

## A.6 RL splits

- **Product:** `rl_spine.loan_type` (`spine_builders.py:136`), keyword match on `ra_prod_typ_nm`
  (`spine_builders.py:56-64`): `PERSONAL CASH` → Personal Cash, `PERSONAL` → Personal,
  `AUTO/VEHICLE/FLEET` → Auto, else `Other`; `rl_spine` keeps only {Personal, Personal Cash,
  Auto} (25, 29-47). Primary `prm_loan_contract.loan_type` (`prm_loan.py:167-210`) adds `Home` +
  a `prod_cd` fallback (`parameters_loan.yml:14-27`): 20 = Personal Cash, 30 = Personal,
  70 = Home, 40/41/45 = Auto. **RL-D4 result** (`RESULTS_RL.md:283,528`): cure6m Personal 11.1%,
  Personal Cash 7.2%, Auto 34.6% — flagged `SPLIT FLAG`, logged decision "continue combined by
  default". `domain_and_decisions.md:124` (S15) later states Auto **does** split out as its own
  unit — apparent supersession, not cross-referenced anywhere found; flagging the ambiguity, not
  resolving it (R19).
- **Vintage:** `chargeoff_age_months` — CC: `spine_builders.py:309,333-342` (leading `[8,9]`
  run-length in `dlq_hist`); RL: `spine_builders.py:72-94` `_add_chargeoff_age_months`
  (consecutive DLQ-7 streak via window). 24-month threshold applied downstream in
  `nodes/target/recovery.py:266,272,354,360` (`<24` → "early" / else "late", col
  `chargeoff_segment`); RL mirror `feat_loan_chargeoff_segment.py:12,100,104`. "gt2y" / "lt2y"
  are **doc shorthand only**, not code values (`_dpd_journey/params.py:16-21`, `TASKS.md:47`,
  `domain_and_decisions.md:116` S5). CC-only floor-date blind spot saturates `cc_180_plus` `gt2y`
  to "unknown" (T43); RL has no equivalent (`rl_history_floor_date: None`). Shared engine:
  `_dpd_journey` package used by both CC and RL A4 (`RESULTS.md:31`).
