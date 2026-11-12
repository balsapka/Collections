# Claude Code handoff — transcription of phone photo (IMG_9005)

## Context
- Photo of a VS Code window (editor above, integrated terminal below) with a Claude Code session.
- Editor tab: `pipeline_registry.py`; breadcrumb: `src > enbd_collections > pipeline_registry.py > register_pipelines`
- Visible editor lines 105-109:

```python
105        r1_a2_locatability as crx_r1_a2_locatability,
106    )
107    from enbd_collections.pipelines.crx_persona import (
108        r1_a3_payment_credibility as crx_r1_a3_payment_credibility,
109    )
```

- Status bar: Ln 122, Col 72 (275 selected), Spaces: 4, UTF-8, LF, Python. Git blame: "You, 4 months ago" / "vajdab (4 months ago)".
- Claude Code status line: `Sonnet | mode: auto | 4%` — branch `feature/persona_refactor` (modified:1, untracked:2, stash:1) — `retail.collections.risk_profiling` — `tkn: 98.9K in: 94 op: 98.8K`
- Second line: `Today Overall Usage burn: 0.0% tkn: 100.1K in: 96 op: 100.0K`; `auto mode on (shift+tab to cycle)`
- "Update installed · Restart to apply"

## Prompt (shown twice in terminal)
> explain what is alert, salary_credit and bureau_salary in bureau-pipeline-analysis branch (latest)

## Claude Code response

Ran 6 shell commands

In origin/bureau-pipeline-analysis (latest commit 52c7e5af), `alert`, `salary_credit` and `bureau_salary` are the three AECB (credit bureau) sources of a customer's monthly salary. `feat_bureau_salary_unified.py` merges them into one salary per customer per month. I read the code only and ran nothing. This branch exists only on the remote, so I read it as `origin/bureau-pipeline-analysis`.

### The three sources

| salary_source value | Rank | Intermediate table | Where the amount comes from |
|---|---|---|---|
| alert | 1 (highest) | `int_bureau_alert_salary_monthly` | AECB alert feed (`sa_ops_aecb_alert`). Only these alert types carry a salary amount: "Avarege salary changed" (the source's own spelling), "Salary account added", "Salary account is added/closed" and "Salary account closed". The amount is `salary_credit_amount` and is booked to the month of the alert's extract date. |
| salary_credit | 2 | `int_bureau_salary_credit_monthly` | AECB salary-credit history (`prm_bureau_salary_history`, one row per provider per month). The monthly total `subj_salcr_hist_tot_sal_amt` is summed across providers. The reference month arrives as an MMYYYY string and is converted to a month-end date. |
| bureau_salary | 3 (lowest) | `int_bureau_salary_monthly` | AECB subject characteristics (`prm_bureau_subj_charac`, codes 232-235). These are cumulative look-back totals for the last 1, 3, 6 and 12 months. The pipeline spreads them back into per-month amounts, for example `(sal_3m - sal_1m) / 2` for each of months 2-3. Each month is floored at 0. |

Within the alert source, if several alerts land in the same month, only the latest one is kept. Amounts are never added up across alerts.

### How they are unified

`feat_bureau_salary_unified.py` combines the three sources at the grain `cif_id × salary_month_end`, one row per customer per month-end:

1. It unions the three sources.
2. For each customer-month it keeps the best usable amount. A usable amount is non-null and non-zero, and the higher-ranked source wins. So a 0 or null in `alert` is filled from `salary_credit`, and then from `bureau_salary`.
3. If no source has a usable amount, the month stays 0 when any source reported 0, otherwise it is null.
4. Ties inside a source go to the latest load date, then the larger amount.
5. It restricts the output to the CIFs in the model spine (`model_id` scope).
6. The output columns are `cif_id`, `salary_month_end`, `monthly_salary` and `salary_source`. The most recent commit restored `salary_source` so you can see which source supplied each value.

### Not the same thing as the alert features

Alert features also appear elsewhere in this branch, in `feat_bureau_alert.py`. That file computes rolling 3, 6 and 12 month counts of alert types (delinquency moves, bounced cheques, court cases and so on). It also includes `bureau_total_salary_credit_amount_*` and a `salary_credit_stability_ratio`. Those are alert-feed features, separate from the unified salary table above.

I didn't check how the persona A1 (ability) code reads the unified salary table. I can trace that next if you want.

Sautéed for 28s · done 7:18 AM

## Notes
- The photo is angled and slightly blurry; the top editor strip is partly cut off above line 105.
- Worth double-checking against the source: commit hash `52c7e5af`, the field names (`subj_salcr_hist_tot_sal_amt`, `prm_bureau_subj_charac`), and the codes 232-235.
- The photo itself can't be saved as an image file from chat; this is the text transcription only.
