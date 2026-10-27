# Workplace reference snippets (handoffs 6 and 9, 2026-10-27)

Transcribed by a chat session from photos 13–26 (`pics/claude_code_handoff_6.md`), OCR quality;
`▯` = a glyph the photo could not render. Partial files, so they live here and not under `src/`.
They answer REQUESTS R4, R5, R7–R11.

## Catalog entry format (`conf/base/catalog/catalog_outputs.yml`)

Layers `02_stg → 03_int → 04_prm → 05_feat → 06_spine_int → 07_spine → 08_mip → 09_mop`;
path `{model_id}/{layer}/{domain}/entity`.

```yaml
_spark: &spark
  type: spark.SparkDataset
  file_format: parquet
  save_args:
    mode: overwrite
    partitionBy: run_date
_spark_de: &spark_de
  type: spark.SparkDataset
  file_format: parquet
  save_args:
    mode: overwrite
_project:
  hdfs_path: "${globals:nameservice}/${globals:aacoe_prefix}data/${globals:tenant}/${globals:aacoe_prefix}adv/${globals:aacoe_entity_name}/${globals:use_case_name}/${globals:execution_environment}"

prm_bureau_payment_order:
  <<: *spark_de
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/bureau/payment_order"

feat_demographics_cif:
  <<: *spark_de
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/demographics/demographics_cif"
```

Bureau primaries in the catalog: `prm_bureau_cif_bridge`, `_alert_enriched`, `_credit_score`,
`_consolidated_summary`, `_court_case`, `_payment_order` — no salary history. Spines:
`cc_spine`, `cc_cif_obs_spine`, `rl_spine`, `rl_cif_obs_spine`, `rl_spine_dates`, `*_with_target`
(`folders.spine`).

## `nodes/primary/bureau/prm_bureau.py`

`_ALERT_RENAMES` (lines 74–116):

```python
_ALERT_RENAMES = {
    # Grain keys
    "ALERT_PROCESS_ID": "alert_process_id",
    "edp_load_date": "edp_load_date",  # Already lowercase in source
    # Alert identification
    "PRVDR_CD": "provider_code",
    "ALERT_REC_ID": "alert_rec_id",
    "REC_CORR_FLG": "record_correction_flag",
    # Subject identification
    "PRVDR_SUBJ_NUM": "provider_subject_number",
    "CB_SUBJ_ID": "cb_subject_id",
    "CB_TRIG_ID": "cb_trigger_id",
    # Alert classification
    "ALERT_CTG": "alert_category",
    "ALERT_TYP_NUM": "alert_type_number",
    "ALERT_DESC": "alert_description",
    "SUBJ_ROLE": "subject_role",
    # Contract details
    "CONTRACT_TYPE": "contract_type",
    "PRD_TYPE_CD": "product_type_code",
    # Financial amounts
    "CONTRACT_BAL_AMT": "contract_balance_amount",
    "OVERDUE_AMT": "overdue_amount",
    "TOTAL_AMT": "total_amount",
    "CREDIT_LIMIT_AMT": "credit_limit_amount",
    "BILLED_AMT": "billed_amount",
    "BOUNCED_CHK_AMT": "bounced_cheque_amount",
    "SALARY_CRED_AMT": "salary_credit_amount",
    # Dates
    "OPN_DT": "open_date",
    "EXTRACT_DT": "extract_date",
    "DT_OF_RETURN": "return_date",
    "CONTRACT_STATUS_DT": "contract_status_date",
    "SUSP_ACT_FLG_DT": "suspended_active_flag_date",
    "COURT_CASE_CLS_DT": "court_case_close_date",
    # Status and flags
    "ACCT_STATUS": "account_status",
    "SUBJ_REL_TYPE": "subject_relation_type",
    # Metadata
    "SRC_FILE_NM": "source_file_name",
    # Product mapping renames (from join)
    "description": "product_description",
}
```

`_join_cif_bridge` (lines 217–254):

```python
_CIF_BRIDGE_COLS = ["bureau_file_id", "edp_load_date", "cif_id"]


def _join_cif_bridge(
    stg_df: DataFrame,
    cif_bridge: DataFrame,
    grain_file_col: str,
    grain_date_col: str = "EDP_LOAD_DATE",
) -> DataFrame:
    """Inner-join a staged Tier B table with the CIF bridge.

    Args:
        stg_df: Staging DataFrame with source-native column names
        cif_bridge: CIF bridge output (has bureau_file_id, edp_load_date, cif_id)
        grain_file_col: Source column name for file ID
            (e.g., "subj_crd_score_hdr_file_id")
        grain_date_col: Source column name for date (default "EDP_LOAD_DATE")

    Returns:
        DataFrame with cif_id added, source column names preserved.
        Bridge grain columns are dropped after join.

    Rows without CIF resolution are dropped (unusable downstream).
    """
    bridge = cif_bridge.select("bureau_file_id", "edp_load_date", "cif_id")

    # Join on source column names, not renamed names
    df = stg_df.join(
        bridge,
        on=(
            (stg_df[grain_file_col] == bridge["bureau_file_id"])
            & (stg_df[grain_date_col] == bridge["edp_load_date"])
        ),
        how="inner",
    )

    # Drop bridge grain columns (source retains its own grain columns)
    return df.drop(bridge["bureau_file_id"], bridge["edp_load_date"])
```

Line 209 (cut off) ends a builder with `return build_primary_datafra…` — the builders project
onto the pydantic model, which is how `DT_OF_RETURN` was dropped (O58).

## `data_engineering/primary/models/bureau.py`

`BureauSalaryHistory` (lines 465–505) — a model exists, but no primary dataset is built from it:

```python
class BureauSalaryHistory(BaseModel):
    """Monthly salary credit history from AECB (72-month range).

    Unit of observation: One row per month per salary credit source per bureau pull.
    Grain keys: bureau_file_id ▯ reference_month ▯ provider_no ▯ edp_load_date

    This entity captures bank-reported salary credits (72 months), providing
    more reliable income verification than self-declared or employer-reported.

    Notes on interpretation:
    - Bank-reported salary credits (from data providers) are reliable income signals.
    - total_salary_amount: monthly salary total; transfer_count tracks split deposits.
    - 110M rows — second-heaviest AECB table; high-signal for income verification.
    - Used for income stability, payment reliability, and affordability features.
    """

    model_config = PYDANTIC_CONFIG

    bureau_file_id: str = Field(description="Bureau file identifier. Grain key.")
    reference_month: str = Field(
        description="Reference month (YYYYMM). Grain key. Month of salary credit."
    )
    provider_no: str = Field(
        description="Provider number. Grain key. Bank/provider reporting salary."
    )
    edp_load_date: date = Field(description="EDP load date. Grain key.")
    total_salary_amount: Optional[float] = Field(
        default=None,
        description="Total salary amount (AED) for the month. Monthly income total.",
    )
    transfer_count: Optional[float] = Field(
        default=None,
        description="Number of salary transfers/deposits. Tracks split deposits (e.g., salary + allowance).",
    )
    last_update_date: Optional[str] = Field(
        default=None, description="Last update date."
    )
    dp_account_no: Optional[str] = Field(
        default=None,
        description="Data provider account number. Account receiving salary.",
    )
```

`BureauAlertEnriched` (lines 841–916), fields: `alert_process_id`, `edp_load_date` (grain),
`cif_id` (int), `cb_subject_id`, `alert_rec_id`, `alert_category`, `alert_type_number`,
`alert_description`, `alert_type_flag`, `alert_month` (from `extract_date`), `subject_role`,
`contract_type`, `product_description`, `contract_category` (C/I/N/S), `contract_balance_amount`,
`overdue_amount`, `total_amount`, `credit_limit_amount`, `exposure_amount`, `billed_amount`,
`bounced_cheque_amount`, `salary_credit_amount`, `open_date` (str), `extract_date` (str),
`account_status`, `provider_code`. No `return_date` / `contract_status_date` (O58).

## Who reads the A1 outputs (R7, grep over `src conf`, excluding the A1 packages)

No code outside the A1 packages reads them. Mentions only:
- `pipeline_registry.py:90,93,107,109,240,241,249,250,252` (imports + entries);
- tests: `src/tests/pipelines/crx_persona/schema_registry.py:181,219` (`CRX_CC_A1_ABILITY`),
  `test_crx_persona.py:31` (imports `cc_a1_ability.nodes`), `:190` (`cc_a1_ability_empty`
  fixture), `src/tests/README_TEST_STRUCTURE.md:40`;
- comments / docstrings: `cc_spell/nodes.py:10`, `_spine_utils.py:3`, `scoring_engine.py:3`,
  `rl_departure_signature/nodes.py:5,8`, `rl_departure_signature/pipeline.py:6`,
  `conf/base/catalog/catalog_casa_plus_ftr.yml:102`, `a1_ability/README.md:10–11`;
- `catalog_crx.yml`: CC v1 `crx_cc_a1_base`, `_cif_enriched`, `_group_b_income`,
  `_group_b_income_recent`, `_group_b_bureau`, `_group_b_bureau_recent`, `_group_c`,
  `_group_c_recent`, `crx_cc_a1_ability`; RL waterfall `crx_rl_a1_group_a`,
  `_group_b_income_recent`, `_group_b_bureau_recent`, `_group_c_recent`, `_group_d`,
  `crx_rl_a1_ability`; plus the engine entries and `crx_rl_a1_ability_b05_check`.

## Layout (R8)

`src/enbd_collections/nodes/{extract,features,intermediate,model_input,primary,spine,staging,
target,utils}/<domain>`; feature domains today: bureau, cc_way4, dcore, demographics,
retail_loans; primary: bureau, casa, cc_dpl, cc_way4, dcore, demographics, digital_login,
retail_loans. `pipelines/<domain>` (bureau, casa, casa_plus_ftr, credit_card, credit_card_way4,
dcore, demographics, digital_login, retail_loans, …). Catalogs: `catalog_casa.yml`,
`catalog_casa_plus_ftr.yml`, `catalog_crx.yml`, `catalog_modelling.yml`, `catalog_outputs.yml`,
`catalog_raw_{aecb,dcore,demographics,digital,dpl,retail_feature_space,way4}.yml`. Parameters:
`parameters{,_bureau,_casa,_crx_persona,_demographics,_loan,_training,_model_input*}.yml`.


# Handoff 9 — the gathered snippets (R4, R5, R8–R11), 2026-10-27

From `tmp_validation/mirror_requests/snippets.md` at work (photos 30–37,
`pics/claude_code_handoff_9.md`), OCR quality; indentation inside the code blocks is
approximate. The headings are the request numbers.

## Snippet R5

`src/enbd_collections/pipelines/bureau/staging.py` lines 47-53

```
            node(
                func=stg_aecb_salary_history.build,
                inputs="sa_ops_aecb_sub_sal_cr_hist",
                outputs="stg_aecb_salary_history",
                name="stage_aecb_salary_history",
            ),
            # --- Secondary tables (6 functions) ---
```

`src/enbd_collections/nodes/staging/bureau/stg_aecb_salary_history.py` lines 28-41

```
_SELECT_COLS = [
    # — Grain Keys —
    "subj_salcr_hist_hdr_file_id",  # Bureau file UUID
    "subj_salcr_hist_ref_mnth",  # Reference month in MMYYYY format (e.g. "072023" = Jul 2023)
    "subj_salcrdt_prvdr_no",  # Provider organization number
    "EDP_LOAD_DATE",  # EDP ingestion/load timestamp — NOT a bureau pull date; see T35/RL-A1-26
    # — Salary Details —
    "subj_salcr_hist_tot_sal_amt",  # Total salary amount
    "subj_salcr_hist_trnsfr_cnt",  # Salary transfer count
    "subj_salcrdt_lst_upd_dt",  # Last update date
]


def build(raw_df: DataFrame) -> DataFrame:
```

`src/enbd_collections/nodes/staging/bureau/stg_aecb_salary_history.py` lines 42-57 omitted, 58-64 below

```
# … lines 42-57 omitted
    df = raw_df.select(*_SELECT_COLS)

    # Type conversions
    df = df.withColumn("EDP_LOAD_DATE", F.col("EDP_LOAD_DATE").cast(DateType()))

    # Repartition for downstream joins
    return df.repartition("subj_salcr_hist_hdr_file_id")
```

## Snippet R8

`src/enbd_collections/pipelines/demographics/features.py` lines 24-29

```
            node(
                func=feat_demographics_cif.build,
                inputs=["int_customer_demographics", "params:feat_demographics"],
                outputs="feat_demographics_cif",
                name="build_feat_demographics_cif",
            ),
```

`conf/base/catalog/catalog_raw_digital.yml` lines 73-79

```
raw_beneficiary_cards:
  type: enbd_collections.datasets.spark_hive_sql_dataset.SparkHiveSQLDataset
  query: "SELECT instrument_number, instrument_type, institution_name FROM AI_TDV_OMB_UAE_EBI.BENEFICIARY WHERE edp_activeind='Y' AND instrument_type='CARD_NUMBER'"
  database: "AI_TDV_OMB_UAE_EBI"
  table: "BENEFICIARY"
  write_mode: "overwrite"
```

## Snippet R9

`src/enbd_collections/nodes/staging/dcore/stg_dcore_observation_spine.py` lines 24-92

```
def build(
    col_trn_agreement: DataFrame,
    cc_spine: DataFrame,
    spine_contracts_way4: DataFrame,
) -> DataFrame:
    """Build DCORE observation spine at grain (agreement_id × observation_date).

    Join 1: bridge (iagreementseqno, cif_id, szlegacyagreementno aliased as
    personal_account) inner-joins spine_contracts_way4 on personal_account,
    bringing in contract_id (LongType) and observation_date.

    Join 2: result inner-joins cc_spine on (cif_id, contract_id, observation_date)
    to restrict to in-scope agreements and valid observation dates.

    Args:
        col_trn_agreement: Raw DCORE agreement table; iagreementseqno is the PK.
        cc_spine: Way4 CC model spine; used as scope and date filter.
        spine_contracts_way4: Way4 contract spine with personal_account linking
            DCORE agreements to Way4 contracts.

    Returns:
        DataFrame at grain (agreement_id × observation_date) with columns:
            agreement_id  LongType  — DCORE agreement PK (= iagreementseqno)
            cif_id        STRING    — bank 8-digit CIF
            account_id    LongType  — Way4 contract PK (= contract_id / contract_idt)
            observation_date DateType — from cc_spine
    """
    bridge = col_trn_agreement.select(
        F.col("iagreementseqno").cast(LongType()).alias("agreement_id"),
        F.col("szcustomerid").alias("cif_id"),
        F.col("szlegacyagreementno").alias("personal_account"),
    )

    spine_contracts_bridge = spine_contracts_way4.select(
        F.col("contract_idt").cast(LongType()).alias("contract_id"),
        F.col("personal_account"),
        F.col("observation_date"),
    )

    cc_spine_bridge = cc_spine.select(
        "cif_id",
        F.col("contract_id").cast(LongType()),
        "observation_date",
    )

    # Few accounts have more than 1 agreement_id in dcore - takes latest agreement
    _window = Window.partitionBy("contract_id", "observation_date").orderBy(
        F.col("agreement_id").desc()
    )

    return (
        bridge.join(
            F.broadcast(spine_contracts_bridge), on="personal_account", how="inner"
        )
        .join(
            F.broadcast(cc_spine_bridge),
            on=["cif_id", "contract_id", "observation_date"],
            how="inner",
        )
        .withColumn("_rn", F.row_number().over(_window))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
        .select(
            "agreement_id",
            "cif_id",
            F.col("contract_id").alias("account_id"),
            "observation_date",
        )
    )
```

`conf/base/catalog/catalog_raw_dcore.yml` lines 109-114

```
col_trn_agreement:
  type: enbd_collections.datasets.spark_hive_sql_dataset.SparkHiveSQLDataset
  query: "SELECT * FROM ${globals:aacoe_prefix}tdv_dcorecapex_group_collections.col_trn_agreement"
  database: "${globals:aacoe_prefix}tdv_dcorecapex_group_collections"
  table: "col_trn_agreement"
  write_mode: "overwrite"
```

## Snippet R10

Note: build_contract has no explicit select; it ends in build_primary_dataframe(df, ContractSnapshot, _CONTRACT_RENAMES).
Block-code columns (block_code_1, block_code_2, block_code_2_date) are not renamed; they are projected via the ContractSnapshot schema.

`src/enbd_collections/nodes/primary/cc_way4/prm_cc.py` lines 513-521

```
    df = df.withColumn(
        "dlq_bucket_from_hist",
        F.when(
            F.col("dlq_hist").isNotNull() & (F.length(F.col("dlq_hist")) > 0),
            F.substring(F.col("dlq_hist"), 1, 1).cast("int"),
        ).otherwise(F.lit(0)),
    )

    return build_primary_dataframe(df, ContractSnapshot, _CONTRACT_RENAMES)
```

`src/data_engineering/primary/models/flows.py` lines 568-575

```
    block_code_1: Optional[str] = Field(
        default=None,
        description="Primary block code (reason for account restriction/block).",
    )
    block_code_2: Optional[str] = Field(
        default=None,
        description="Secondary block code. Used with block_code_1 for full block reason.",
    )
```

`src/data_engineering/primary/models/flows.py` lines 659-664

```
    block_code_2_date: Optional[date] = Field(
        default=None,
        description="Date block code 2 (W = B2 collector at 61 DPD) was applied "
        "(from BLOCK_CODE_ACC2_% attr_date_from). "
        "Enables 'days since collections entry' feature. Way4 only.",
    )
```

Deceased: node build_customer_individual (key col cust_num -> cif_id; cust_deceased_flg -> deceased_flag)

`src/enbd_collections/nodes/primary/demographics/prm_demographics.py` lines 83-94

```
_CUSTOMER_INDIVIDUAL_RENAMES = {
    "cust_num": "cif_id",
    "cust_dob_doi": "date_of_birth",
    "cust_gender_cd": "gender",
    "cust_nat_ctry_cd": "nationality_code",
    "cust_resi_ctry_cd": "residential_status",
    "cust_resi_start_dt": "residence_start_date",
    "cust_marr_stat_cd": "marital_status",
    "cust_deceased_flg": "deceased_flag",
    "entity_cd": "bank_entity",
    # "group_xref_id": "group_id",
}
```

`src/enbd_collections/nodes/primary/demographics/prm_demographics.py` lines 146-150

```
    return build_primary_dataframe(
        stg_customer_individual,
        CustomerGroupingXref,
        _CUSTOMER_INDIVIDUAL_RENAMES,
    )
```

## Snippet R11

`src/enbd_collections/nodes/primary/cc_way4/prm_cc.py` lines 375-386

```
    # Derive is_international: NULL/empty trans_country_code → domestic (0)
    df = df.withColumn(
        "is_international", F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1)
    )
    df = df.withColumn(
        "is_international", F.when(F.col("is_international") == "N", 1).otherwise(0)
    )

    # Derive direction: Debit: -1, Credit: 1
    df = df.withColumn("direction", F.when(F.col("amount") < 0, -1).otherwise(1))

    return build_primary_dataframe(df, CreditCardTransaction, _TRANSACTION_RENAMES)
```

## Snippet R4

Output of the grep (run from repo root; only src/enbd_collections/pipeline_registry.py matches,
i.e. registry import/registration of the persona pipelines, no other consumers):

```
src/enbd_collections/pipeline_registry.py:75:    cc_payment_trajectory as crx_cc_payment_trajectory,
src/enbd_collections/pipeline_registry.py:118:    rl_departure_signature as crx_rl_departure_signature,
src/enbd_collections/pipeline_registry.py:235:        "crx_cc_payment_trajectory": crx_cc_payment_trajectory.create_pipeline(),
src/enbd_collections/pipeline_registry.py:236:        "crx_cc_utilisation_features": crx_cc_utilisation.create_pipeline(),
src/enbd_collections/pipeline_registry.py:237:        "crx_cc_departure_signature": crx_cc_departure.create_pipeline(),
src/enbd_collections/pipeline_registry.py:253:        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
```


## What handoff 9 settles

- **R5, bureau salary.** `stg_aecb_salary_history` keeps seven columns: file id, reference
  month (**MMYYYY**, `"072023"`), provider number, `EDP_LOAD_DATE` (cast to date; "not a
  bureau pull date"), total amount, transfer count, last-update date. The grain is file ×
  month × provider × load date. `prm_bureau_salary_history` (CC finish bundle) parses the
  month as `MMyyyy` (what the engine already does; the DE model's "YYYYMM" is wrong), keeps
  each (file, month, provider)'s latest load, and sums providers per file × month. It carries
  no `cif_id`; the feature joins `prm_bureau_cif_bridge`.
- **R8.** `feat_demographics_cif` = `feat_demographics_cif.build(int_customer_demographics,
  params:feat_demographics)` in `pipelines/demographics/features.py`.
  `raw_beneficiary_cards` (`catalog_raw_digital.yml`) is a lookup from card number to
  institution (`instrument_number`, `instrument_type`, `institution_name` from
  `AI_TDV_OMB_UAE_EBI.BENEFICIARY`, active `CARD_NUMBER` rows). It has no customer key, so
  `prm_beneficiary_cards` is a lookup table, not a CIF table.
- **R9, DCORE.** The DCORE spine is **CC only**. Its `agreement_id` is
  `col_trn_agreement.iagreementseqno`, `cif_id` is `szcustomerid`, and
  `szlegacyagreementno` = `spine_contracts_way4.personal_account` gives `contract_idt`. The
  spine is then inner-joined with `cc_spine` on (cif, contract, `observation_date`), so it
  carries `cc_spine`'s mid-month dates, and the highest `agreement_id` is kept per contract
  and date. `prm_dcore_account_agreements` = the same bridge without dates. The RL DCORE
  source is not in the snippets (Part 0 shows an RL DCORE spine on month ends) → R9b.
- **R10, deceased.** Block codes are `ContractSnapshot` fields on `prm_contract`
  (`block_code_1`, `block_code_2`, `block_code_2_date`); A2 Part 0: `D` only ever appears in
  `block_code_2`. Demographics: `cust_num → cif_id`, `cust_deceased_flg → deceased_flag` in
  `build_customer_individual`, which projects through the `CustomerGroupingXref` model (O61).
- **R11.** `prm_cc.build_transaction` parses `DOMESTIC=(.)` from `add_info` exactly as
  `cc_raw_extract` does (`N` → international, anything else, missing included → domestic).
  The comment above it talks about `trans_country_code`, which the code does not read. So O59
  applies to `prm_transaction` too.
- **R4 → D1.** Outside `crx_persona/` and `catalog_crx.yml`, only `pipeline_registry.py`
  names the departure / payment-trajectory / utilisation pipelines (imports and
  registration), and `crx_cc_departure_pass` appears nowhere. Nothing else reads them: they
  can go when their persona consumers do.
