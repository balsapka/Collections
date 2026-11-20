**What this bundle does.** Removes the spell (T0) tables and the code that only they fed. Every axis is keyed on `(account_id, observation_date)` through the obs base, and A3 reads the episode start from A4 (`months_before_spell`), so nothing reads the spell tables any more (DESIGN_REVIEW §6, D5, steps 6–7). **Apply on top of bundles 25–29 and their cleanups.** No persona output changes.

Removed:
- packages `crx_persona/cc_spell/`, `crx_persona/rl_spell_table/`, `crx_persona/rl_a4_spine/` and `crx_persona/_spine_utils.py`;
- the node `build_crx_cc_limits` in `cc_raw_extract` (credit limits on the spell window; no reader);
- catalog entries `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine`, `crx_cc_limits`;
- registry entries `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine` and their imports.

Kept: `crx_cc_full_history` / `crx_rl_full_history` (A4 reads them) and `cc_raw_extract`'s account windows, transactions, balance and billing (A3 reads them). Comments that still described T0 windows now describe what the code does.

Tested in the mirror: the golden harness (`checks/refactor_golden.py`) reproduces every persona output of the previous head; smoke import check; black, ruff and pylint clean on the touched files.
