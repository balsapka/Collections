**What this bundle does.** The A1 ability finish (spec `A1_ability_spec.md` S1–S13): the
engine reads monthly feature tables only, the known input defects are fixed, the activity
gate counts only money the customer moved, the old CC v1 and the RL waterfall are removed,
and a temporary check logs every table of the A1 report to GRR.

- **New primaries** (pipeline `casa_primary`): `prm_casa_transactions` — every CASA leg of
  `comp_financial_tran_repos_dly`, all CIFs, 12 months before the persona start onwards,
  deduplicated on the transaction key, CIF 13339117 dropped; `prm_beneficiary_cards` — the
  card numbers registered as payment beneficiaries (`raw_beneficiary_cards`).
- **New pipeline `casa_features`**: `feat_cif_internal_salary_monthly` (WM salary, **dated
  correctly**: `week_number` is `yyyyMM0W`, not a date — the old engine put every salary one
  month early, O64), `feat_cif_casa_balance_monthly`, `feat_cif_casa_activity_monthly` (CASA
  legs per lane, after the FTR row-handling reference), `feat_cif_ext_card_payment_monthly`,
  `feat_cif_returns_monthly`.
- **New pipeline `bureau_salary_bounces`** (own file in `pipelines/bureau/`):
  `prm_bureau_salary_history` (typed `stg_aecb_salary_history`), `feat_cif_bureau_salary_monthly`
  (joined to `prm_bureau_cif_bridge` on the file, as today), `feat_cif_bureau_bounces_monthly`
  (pulls with a bounce, and **new** bounce events: a bounce repeated unchanged counts once).
  Catalog entries in a new `catalog_bureau.yml`.
- **Engine `crx_persona/a1_ability/`**: signals read the observation base + these features
  (+ `dcore_prm_followup_outcomes` / `prm_dcore_account_agreements` for the EOSB diagnostic);
  **S12** Stable income = the window's salary total ≥ 2 × the threshold (3 × at 180+) and
  ≥ 75% of the prior window; **S11** Unknown = 0 points, no distress and no
  customer-initiated CASA movement (own-loan recovery, own-account wash, fees, interest,
  reversals do not count), with `a1_unknown_reason` `no_casa` / `dormant_casa`; distress parts
  `distress_cheque` / `_dds` / `_bureau`; diagnostic `a1_eosb_flag`. `pipeline.py` builds the
  axis for either product.
- **Renames and deletions**: `cc_a1_ability_v2` → `cc_a1_ability`, `rl_a1_ability_v2` →
  `rl_a1_ability` (the old CC v1 and RL waterfall packages are replaced); outputs
  `crx_cc_a1_ability` / `crx_rl_a1_ability` (the old v1 / waterfall paths, overwritten);
  `crx_*_a1_internal_returns` and the v1 / waterfall catalog entries deleted. The
  `crx_*_a1_ability_v2` entries stay until the cleanup as the check's baseline. The
  departure-signature packages stay (`rl_a4_spine` imports one).
- **Check** (`a1_ability/b08_check.py`, pipelines `crx_cc_a1_ability_b08_check`,
  `crx_rl_a1_ability_b08_check`): blocks `B08 OUTPUT`, `REPORT`, `SOURCES`, `CHANGES` — the
  GRR report metrics M1–M12 and each state change attributed to salary dating, S12, the gate
  or bureau repeats. Removed by the cleanup prompt.
- Expected moves (A1 v03b): Low → Moderate / Moderate → High from the salary dating and S12
  (CC ~100 / ~30), Low → Unknown from the gate (CC 15–31% of Low, RL Low 89.5% → ~45–60%).
