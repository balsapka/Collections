# Open requests for the workplace repo

Things the mirror still needs from `retail.collections.risk_profiling`
(branch `feature/persona_redesign_b01`; mirror branch `feature/persona_redesign`). Photograph the result and drop it in `pics/`.
Done requests are removed; their results are logged in `TRANSCRIPTION_NOTES.md`.

The A1 test modules (`src/tests/pipelines/crx_persona/schema_registry.py`,
`test_crx_persona.py`) are left to the workplace Sonnet, via the A1 bundle prompt.

## How to send these

Photos (breadcrumb visible) or a transcription `.md` in `pics/`, as before. For shell output,
run the command from the workplace repo root and photograph the terminal. Ordered by what each
request unblocks.

## A1 — CC finish bundle (relayer + rename + delete v1, S12 salary rule, bureau bounces)

### R5 — bureau pipeline (blocks `prm_bureau_salary_history`, `prm_bureau_bounce_events`)

- `src/enbd_collections/nodes/primary/bureau/prm_bureau.py` — the whole file (`_join_cif_bridge`,
  `build_cif_bridge`, `build_alert_enriched`, `_ALERT_RENAMES`, the payment-order / court-case
  builders);
- `src/enbd_collections/pipelines/bureau/primary.py` and `pipelines/bureau/staging.py` (the
  salary-history and `stg_aecb_alert` nodes);
- `data_engineering/primary/models/bureau.py`: `BureauAlertEnriched` and any salary model;
- `conf/base/catalog/catalog_outputs.yml`: the `stg_aecb_*` (~124–166) and `prm_bureau_*`
  (~479–501) entries.

### R7 — who reads the A1 outputs (before v1 and the RL waterfall are deleted)

```bash
grep -rnE "crx_cc_a1_|crx_rl_a1_|cc_a1_ability|rl_a1_ability" src conf | grep -vE "pipelines/crx_persona/(cc|rl)_a1_ability(_v2)?/"
```

### R8 — layer conventions (where new primary / feature nodes and catalog entries go)

```bash
find src/enbd_collections -maxdepth 3 -type d -not -path "*/__pycache__*" | sort && ls conf/base/catalog conf/base/parameters
```

Plus one existing feature node as the style reference: `feat_demographics_cif.py` and its
pipeline file, and the `raw_beneficiary_cards` and `wm_pri_labelled_transactions` catalog
entries (for `prm_beneficiary_cards`).

### R6 — retail loan pipeline (low priority: RL A1 already ships with `installment_due_amount`)

The node building `int_loan_master` (`monthly_emi_due` / `total_paid` / `emi_*_flag`, the
tolerance parameters), its pipeline file and catalog entry; `feat_loan_emi` for reference (A3).

## A2 — the refactor bundle (login fixes, location layer, engine, reachability, deceased)

### R9 — DCORE (blocks reachability and `prm_dcore_account_agreements`)

- `pipelines/dcore/*.py` (staging + primary pipeline files);
- `nodes/staging/dcore/stg_dcore_observation_spine.py`, `stg_dcore_scope_agreements.py`;
- `nodes/primary/dcore/prm_dcore.py` (`build_followup_outcomes`, ~217–257);
- the `dcore_*` entries in `catalog_outputs.yml` and the raw DCORE catalog file — in particular
  the raw table that maps an agreement to its account / contract.

### R10 — deceased sources

- `pipelines/credit_card_way4/primary.py` and `nodes/primary/.../prm_cc.py` `build_contract`
  (~473–521, block codes) + the `prm_contract` catalog entry;
- `prm_demographics.py` (the `deceased_flag`, ~91) + the `prm_demographics` catalog entry.

### R11 — card spend (location evidence; v02 picks the fields)

`prm_cc.py` `build_transaction` (~330–420, including the `DOMESTIC=` parse ~375–381) + the
`prm_transaction` catalog entry.

### R12 — CASA spend sources (v02 picks the route; the entries are small, send both now)

The catalog entries of `wm_pri_labelled_transactions_indicators_by_week`
(`catalog_casa_plus_ftr.yml`) and `comp_financial_tran_repos_dly`.

### R4 — who reads the departure / CC feature tables (decision D1 in DESIGN_REVIEW.md)

Run from the workplace repo root and photograph the output:

```bash
grep -rnE "crx_cc_departure_signature|crx_cc_payment_trajectory|crx_cc_utilisation_features|crx_rl_departure_signature|crx_cc_departure_pass" src conf notebooks 2>/dev/null | grep -v "\.pyc" | grep -vE "/crx_persona/|catalog_crx\.yml"
```

Empty output means nothing outside the persona code reads them.

### R13 — results splits on the obs base

`spine_builders.py`: where `cc_spine` / `rl_spine` get `loan_type` (~56–64, 136) and
`chargeoff_age_months` (CC ~309–342, RL ~72–94), and the `cc_spine` / `rl_spine` catalog entries.
