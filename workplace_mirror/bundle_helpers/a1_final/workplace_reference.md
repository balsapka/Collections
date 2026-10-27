# Workplace reference snippets (handoff 6, 2026-10-27)

Transcribed by a chat session from photos 13–26 (`pics/claude_code_handoff_6.md`), OCR quality;
`▯` = a glyph the photo could not render. Partial files, so they live here and not under `src/`.
They answer REQUESTS R5 (partly), R7 and R8 (partly).

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
