**What this bundle does.** Adds the UC1 stated block: a new output per product, `crx_cc_uc1_stated` / `crx_rl_uc1_stated`, that condenses UC1's call-transcript signals into two stated axes and two flags beside the four persona axes. A1–A4 are not touched. **Apply after bundle 25** (from bundle 25's branch, once its UAT apply is committed); it is independent of bundle 25's check and cleanup. New files plus 8 catalog entries and 2 registry lines; no existing node changes.

**Inputs.** UC1's outputs, read as they are from the shared file store (`${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/...`, read only): `metadata`, `current/outputs/extracted_signals` (only `model_version`), `current/outputs/timelines/simple_signal_aggregation`, `current/outputs/timelines/signal_level_conflicts`. Plus `crx_<p>_obs_base`.

**Output** at `(account_id, observation_date)`; only the month of `crx_persona.persona_end_date` is scored, other months carry NULL (UC1's customer table has no date):
- `uc1_evidence`: `extracted` / `legacy_only` / `not_extracted` / `no_conversation` / `no_cif`, from the customer's conversations dated strictly before the observation date;
- `a5_state` (stated ability, from `payment_capacity`): `able` / `partly_able` / `unable` / `not_stated` / `no_evidence`; `a5_reason` = the published `delinquency_reason`;
- `a6_state` (stated intent, from `payment_intent`): `pays_in_full` / `partly_or_later` / `refuses` / `not_stated` / `no_evidence`; details `a6_intent_level`, `a6_period`, `a6_amount_named_flag`, `a6_date_named_flag`;
- support: `a5_conversations_n` / `a6_conversations_n` (conversations that detected the signal) and `a5_agree_n` / `a6_agree_n` (those that detected the published level);
- `stated_dispute` (level or `none`), `stated_request_flag`;
- `uc1_conversations_n`, `uc1_extracted_n`, `uc1_last_conversation_date`, `uc1_last_extracted_date`, `uc1_after_obs_flag` (the published level may rest on a conversation on or after the observation date).

An unknown level in UC1's customer table stops the run (their schema changed). Each run logs the latest month's `uc1_evidence`, `a5_state` and `a6_state` distributions.

Tested in the mirror: spec test `checks/uc1_stated_spec.py` (11 cases on UC1-shaped rows, the unscored month, the unknown-level stop, every dataset in the catalog); black, ruff and pylint clean.
