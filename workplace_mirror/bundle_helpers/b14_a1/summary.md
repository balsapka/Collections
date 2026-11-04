**What this bundle does.** A1 counts only real current and savings accounts as CASA, and dates bureau
bounces by the day the cheque bounced. It also adds a check that measures both against the current
output.

- **CASA accounts (spec S16).** `comp_financial_tran_repos_dly` also holds the loan account itself, so
  every RL customer looked like a CASA holder and "No CASA" never fired. New primary
  `prm_casa_accounts` (`nodes/primary/casa/prm_casa.py::build_casa_accounts`): the accounts of
  `raw_casa_acid_to_cif` (the Finacle account master, read as WM reads it) whose scheme code is one of
  the 49 current + savings codes (`casa_primary.current_account_codes` / `saving_account_codes`, WM's
  `current_accounts` + `saving_accounts`). `feat_cif_casa_activity_monthly` and
  `feat_cif_returns_monthly` keep only legs on those accounts (`foracid`). The primaries
  `prm_casa_transactions` / `prm_casa_return_events` still hold all legs. The WM balance arm of
  `casa_held` is unchanged.
- **Bureau bounce date (spec S15).** `feat_cif_bureau_bounces_monthly` dates each bounce by
  `dt_of_return`. One bounce = one `(cif_id, dt_of_return)`, with the largest amount that day. The
  comparison with the previous pull is gone. New column `max_bounce_amount`; `bounce_pulls` is dropped
  (no reader).
- **Check** (`a1_ability/b14_check.py`, pipelines `crx_cc_a1_ability_b14_check`,
  `crx_rl_a1_ability_b14_check`). Blocks:
  - `B14 OUTPUT`: old × new state, and why each row moved;
  - `B14 ACCOUNTS`: the base CIFs' legs by account length × scheme class;
  - `B14 BOUNCES`: the pull rule against the return date.
  The bundle 12 check is not in it: its cleanup is done.
- Expected for `rl_60_180` (the `101` proxy run, handoff 34): about 4% of rows move, mostly Low to
  Unknown. "No CASA" goes from 0 to about 13%, most of it on Auto loans. The exact rule should move
  fewer rows than the proxy, because it keeps 13-character current / savings accounts that `101`
  dropped.
