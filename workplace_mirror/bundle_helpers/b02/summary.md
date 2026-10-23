**What this bundle does.** A follow-up to bundle 01 on the same branch, before its cleanup:

- **Internal returns move into the shared engine.** The workplace assistant's
  `build_cc_internal_returns` (`cc_a1_ability_v2/nodes.py`) becomes
  `a1_ability.build_internal_returns`, so RL A1 can reuse it. Same source and filter
  (`comp_financial_tran_repos_dly`, scoped by CIF, 100-day floor, `reason_for_excluding` in
  `CHEQUE RETURNS` / `DDS Rejects/Reversal` / `RETURNS`). Two changes: it now also prunes
  partitions on `edp_load_date`, and it keeps the reason as a column for the check.
  Catalog entry `crx_cc_a1_internal_returns` is unchanged.
- **The observation base takes `cif_id` from `cc_spine`** (no more `prm_contract` →
  `prm_client` bridge; O44).
- **More diagnostics in the temporary check** (`b01_check.py`):
  - `B01 OUTPUT` adds the income level × liquidity level crosstab and the distress-flag
    count;
  - `B01 SALARY` compares recovered salary months with `payroll_flag` in the same month, the
    month before and the month after, plus credit amounts by payroll flag;
  - `B01 DISTRESS` (new) shows rows flagged by bureau bounces vs internal returns, and
    events / rows flagged per internal reason.

The files the workplace assistant edited (`a1_ability/signals.py`,
`cc_a1_ability_v2/nodes.py`, `cc_a1_ability_v2/pipeline.py`) are replaced as a whole via
`--accept`; this bundle already contains that change.
