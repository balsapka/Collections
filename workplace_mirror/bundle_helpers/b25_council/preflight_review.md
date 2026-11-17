# Bundle 25 preflight: review (2026-11-17)

Source: `preflight_results.md` (UAT Sonnet, workplace branch `feature/persona_refactor`; it calls the
workplace checkout "the mirror", but the paths are workplace-only: `src/tests`, `tmp_validation`,
`notebooks`). Read-only greps, no data.

## What it settles

- **No production module outside the rewritten files breaks.** The one non-test caller of a changed
  symbol is `_dpd_journey/anchor.py:50` (`pit_latest`), which does not pass `anchor=` (checked in the
  mirror, same file). `build_cc_acct_windows` outside: docs and a catalog comment only.
- **Workplace tests that break** (tests are the workplace Sonnet's): `test_a1_ability.py`
  (`build_income_signals` old arguments, `cross_product_level`), `test_a3_promise_events.py` (`_cutoff`,
  two-argument `promise_deadline`, `EVENTS` from `.sources`), `test_feat_cif_cross_product.py`
  (`PRODUCT_TYPES`). The bundle's UAT step asks Sonnet to update them after the apply.
- **Old `tmp_validation` snippets break** (`a1_high_whatif`, `a1_aecb_whatif`, `a1_bureau_fill`,
  `a1_bureau_unified`, `a1_payment_cure`, `a1_bulk_pull`, `a1_casa_accounts`, `a3_detail`, `a3_v1h`,
  `a3_v1i`): all from retired prompts. Default: the bundle 25 cleanup deletes them.
- **Catalog:** the workplace `catalog_crx.yml` has 53 + 8 top-level keys; the mirror lacks 8 A3
  entries (`crx_cc_a3_payment_cycles`, `crx_cc_a3_{dlq,pre_dlq}_payment_signals_single_payment_cycle_count`,
  `crx_cc_a3_strong_negative_signals`, the RL four with `crx_rl_a3_dlq_cycles`), between
  `*_a3_commitment_signals` and `*_a3_episode`. Same order otherwise. No `a3_dues` / `a3_payments`
  keys: the nodes exist (memory datasets). Persisting them (decided) = 4 entries in the standard A3
  body; place them after `*_a3_payment_credibility`, away from the workplace-only block, and have UAT
  list removed top-level keys after the apply.
- **Registry:** only the two A3 product pipelines; bundle 25 makes no registry edit.

## For later bundles

- Dead-package deletion also removes `raw_stg_limit` from `cc_raw_extract/pipeline.py`, two registry
  blocks, `test_rl_spell_table.py`, `test_cc_raw_extract_nodes.py`, `test_crx_persona.py` and
  `schema_registry.py` entries.
- `feat_cif_casa_activity_monthly` and `feat_cif_ext_card_payment_monthly` have 0 readers (Q-R-07):
  candidates to drop with the CASA handoff.
