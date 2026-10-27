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

### R5 — bureau, three snippets (blocks `prm_bureau_salary_history`, `prm_bureau_bounce_events`)

- `nodes/primary/bureau/prm_bureau.py`: `_ALERT_RENAMES` (~95–110), `_join_cif_bridge`
  (~218–247) and one builder that calls it (e.g. the payment-order one);
- `data_engineering/primary/models/bureau.py`: the `BureauAlertEnriched` class only (~844);
- `pipelines/bureau/primary.py`: the `node(...)` block of that same builder;
- `catalog_outputs.yml`: the anchors at the top, one `prm_bureau_*` entry, `feat_demographics_cif`.

### R7 — who reads the A1 outputs (before v1 and the RL waterfall are deleted)

```bash
grep -rnE "crx_cc_a1_|crx_rl_a1_|cc_a1_ability|rl_a1_ability" src conf | grep -vE "pipelines/crx_persona/(cc|rl)_a1_ability(_v2)?/"
```

### R8 — layer conventions (where new primary / feature nodes and catalog entries go)

```bash
find src/enbd_collections -maxdepth 3 -type d -not -path "*/__pycache__*" | sort && ls conf/base/catalog conf/base/parameters
```

Plus the `node(...)` block that builds `feat_demographics_cif` (its pipeline file), and the
`raw_beneficiary_cards` catalog entry (for `prm_beneficiary_cards`).

## A2 — the refactor bundle (login fixes, location layer, engine, reachability, deceased)

### R9 — DCORE, one file + one entry (blocks `prm_dcore_account_agreements`)

`nodes/staging/dcore/stg_dcore_observation_spine.py` (~24–92: where `agreement_id` comes from and
how it joins the spine), and the raw catalog entry of the DCORE table it reads for that.

### R10 — deceased, two output selects

The final `select` of `prm_cc.build_contract` (~473–521: the block-code column names) and of
`prm_demographics.py` (~85–95: key and `deceased_flag`).

### R11 — card spend, after v02

The final `select` of `prm_cc.build_transaction` and the `DOMESTIC=` parse (~375–381).

### R12 — CASA spend source, after v02 (only the entry of the route v02 picks)

The catalog entries of `wm_pri_labelled_transactions_indicators_by_week`
(`catalog_casa_plus_ftr.yml`) and `comp_financial_tran_repos_dly`.

### R4 — who reads the departure / CC feature tables (decision D1 in DESIGN_REVIEW.md)

Run from the workplace repo root and photograph the output:

```bash
grep -rnE "crx_cc_departure_signature|crx_cc_payment_trajectory|crx_cc_utilisation_features|crx_rl_departure_signature|crx_cc_departure_pass" src conf notebooks 2>/dev/null | grep -v "\.pyc" | grep -vE "/crx_persona/|catalog_crx\.yml"
```

Empty output means nothing outside the persona code reads them.

(R13 dropped: the v01 inventory already gives `rl_spine.loan_type` and
`chargeoff_age_months` on both spines.)
