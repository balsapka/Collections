**Step 6.** Before committing, give this prompt to the workplace assistant. It works on
the bundle's `TODO(sonnet)` items. UAT has no data, so it only wires a source that the code
base already defines; anything that needs data goes back to you as a question:

````text
Mirror bundle 01 added the A1 engine in src/enbd_collections/pipelines/crx_persona/a1_ability/.
Work on its TODO(sonnet) items (grep "TODO(sonnet)" in a1_ability/signals.py). Rules: Kedro
only — every source is a catalog dataset passed as a node input, never spark.read or a path;
signals are per customer (cif_id) across ALL of the customer's accounts, never the scored
account_id; a missing required column must raise (use _common.require_columns); touch
nothing outside crx_persona/a1_ability/, crx_persona/cc_a1_ability_v2/pipeline.py and the
crx catalog; do not commit.

1. Internal returned cheques / DDS returns (build_distress_signals, argument
   internal_returns). Search this repo and the sibling repos (retail.feature_space,
   wealth_management) and the catalog for an EXISTING definition: a table, feature or
   transaction-code / narration list for returned cheques, cheque bounces, DDS or direct
   debit returns (candidates: comp_financial_tran_repos_dly transaction codes, a DDS mandate
   table).
   - If you find one that the code already uses, add a node in cc_a1_ability_v2 that builds
     (cif_id, event_date) from it at CIF level and pass it to build_distress_signals as
     internal_returns (inputs as a dict, since payment_order stays unset). Remove the TODO.
   - If you find only candidates (no definition already in use), change nothing. Report each
     candidate with dataset name, columns, code values and where you found them, so the
     codes can be checked on data in PROD.
2. Salary months (build_income_signals TODO): nothing to change in UAT. The bundle's PROD
   run logs a B01 SALARY block comparing the recovered months with feat_payroll_indicator.

Finish with: files changed, what you wired, open candidates/questions.
````

Send the report back. If it wired a source, review `git diff`, then check that every
pipeline still loads (lists `crx_cc_a1_ability_b01_check` among the pipelines):

```bash
kedro registry list
```
