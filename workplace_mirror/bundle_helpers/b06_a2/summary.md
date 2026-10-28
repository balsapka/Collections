**What this bundle does.** The A2 locatability rebuild (spec `A2_locatability_spec.md`, §11):
one engine shared by CC and RL on the observation base, fed by new primary and feature
datasets, plus a temporary check against the old A2.

- **Login fixes** (`digital_login`, shared with the DE code): a login without any country
  is no longer foreign (`is_foreign_login` NULL, O53); rows without a `sessionid` are no
  longer collapsed into one (O54). `prm_digital_login_monthly` keeps its grain and columns
  and adds `last_uae_login_date`, `last_foreign_login_date`, `unknown_country_login_cnt`; a
  same-day tie takes the foreign login (O55, O56).
- **New primary `prm_casa_card_transactions`** (pipeline `casa_primary`, beside
  `prm_casa_return_events`): debit-card rows of `comp_financial_tran_repos_dly` that can
  place a customer, all CIFs, 36 months — in-person POS (`merchant_type_desc` Machine /
  Offline), ATM withdrawals, and travel purchases on any POS type. `place_country` =
  `merchant_country` (POS) or the narration's country code, else
  `counter_party_bank_cntry` (ATM). Debits only, dedup on the key, CIF 13339117 dropped
  (the A2 v03 rule, D-A2-19).
- **New pipeline `location_features`**: `prm_dcore_account_agreements` (account → DCORE
  agreement from `dcore_observation_spine`, no dates) and `feat_cif_location_monthly`
  (per CIF and month: latest UAE / foreign evidence + source, latest travel purchase) from
  logins, debit cards (reason and remote-MCC lists applied), credit cards (`prm_transaction`
  purchase / cash debits, C2 categories, `is_international`) and DCORE departure notes.
- **New engine `crx_persona/a2_locatability/`**: location L1–L4 (latest evidence wins,
  travel rule GAP 3 m / SILENCE 1 m, In Country within W), reachability (gone dark = last
  3 call days all failed, oldest in W, no contact since; Reachable = contact in W; DCORE
  vocabulary per D-A2-17 in `codes.py`), deceased (DCORE, Way4 `block_code_2 = D` on the
  latest snapshot of any card, demographics). Output `crx_<p>_a2_locatability`: `a2_state`
  (`deceased` or `<location>__<reachability>`), `a2_state_label`, both dimensions,
  `deceased_flag` / `deceased_source` and diagnostics. RL reads Way4 too.
- **Old A2 retired**: `cc_a2_locatability/` and `rl_a2_locatability/` become thin wrappers
  (same pipeline and output names); their `nodes.py` / `constants.py` and the
  `crx_*_a2_base` / `_login_presence` / `_contact_signals` catalog entries are deleted. The
  departure signatures stay until the A1 finish bundle (the A1 waterfall / v1 read them).
- **Check** (`a2_locatability/b06_check.py`, pipelines `crx_cc_a2_locatability_b06_check`,
  `crx_rl_a2_locatability_b06_check`): old vs new crosstabs, rules and sources, debit rows by
  month / type / place, RL by product. Removed by the cleanup prompt.
- Expect a large move on CC Skip: the old A2 counted every Way4 `DOMESTIC=N` row (online
  included) as a departure trail (O59). That is a correction.
