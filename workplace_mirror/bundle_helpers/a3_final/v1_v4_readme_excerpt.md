# A3 V1–V4 snippet README, excerpt (handoff 40, 2026-11-04)

Partial: lines 1, 34 and 48–78 of `tmp_validation/a3_v1_v4/README.md` as photographed (written in chat
from 1 photo). Companion to `v1_v4_summary_60_180.md`. Editor line numbers kept; `...` = lines not shown.

```
1   # A3 payment credibility - V1-V4 measurements before the redesign
...
34  ## Population and anchor
...
48    and the anchor is its first day. Where A4 has no row for the account the anchor falls back to
49    the month of the A3 output's `t0` (`anchor source` table in the result). With neither, the event
50    look-back is 24 months (the RL strong-negative floor); that count is also shown.
51    The result also compares the A4 spell-start month with the month of the A3 `t0`.
52  - "In the delinquency" = `[anchor, observation_date)` for DCORE events; plan starts and payments
53    "after" a contact run up to and including the observation date (as A3's own refusal rule does).
54  - Account -> agreement: `prm_dcore_account_agreements` (distinct `account_id`, `agreement_id`, strings).
55
56  ## Output columns of the other axes that were used
57
58  | Axis | Dataset | Columns |
59  |---|---|---|
60  | A4 | `crx_<p>_a4_deterioration` | `account_id`, `observation_date`, `det_state`, `months_before_spell`, `history_months`, `n_prior_episodes` (and `clean_gap_before_current` **if present** - it is not in the engine's persisted feature list, so V3 reports it as not persisted) |
61  | A2 | `crx_<p>_a2_locatability` | `account_id`, `observation_date`, `reachability_state` (`non_reachable` / `reachable` / `unknown`) |
62  | A1 | `crx_<p>_a1_ability` | `account_id`, `observation_date`, `a1_state` (`high` / `moderate` / `low` / `unknown`) |
63
64  Other datasets: `crx_<p>_a3_payment_credibility` (state, levels, points, evidence columns),
65  `crx_<p>_a3_commitment_signals`, `_strong_negative_signals`, `_dlq_payment_signals_<shipped method>`,
66  `_pre_dlq_payment_signals_<shipped method>` (V4, V2-N0); `dcore_int_ptp`, `dcore_prm_promise_instalments`,
67  `dcore_int_settlement`, `dcore_prm_settlement_schedule_instalments`, `dcore_feat_ptp`,
68  `dcore_feat_settlement`, `dcore_prm_followup_outcomes`, `prm_dcore_account_agreements`; CC
69  `crx_cc_transactions`, `crx_cc_a3_payment_cycles`; RL `int_loan_master`, `crx_rl_a3_dlq_cycles`.
70  Catalog layers: `dcore_int_*` intermediate, `dcore_prm_*` primary, `dcore_feat_*` feature,
71  `dcore_observation_spine` spine; `prm_dcore_account_agreements` primary (`catalog_location.yml`).
72
73  ## Definitions the snippet fixes (read these before the numbers)
74
75  **V1b.** Concluded = non-cancelled PTP or settlement instalment with `due_date <= observation_date` that
76  is paid (`payment_amount >= due_amount`) or overdue (`due_date < obs` and not fully paid) - dcore's own
77  `instalment_amount_flags`; cancelled instalments (status `C`) are nulled with dcore's own helper.
78  Window = `due_date` in `[max(anchor, obs - 12 months), obs]`. The dcore features count every
```

## Transcription notes (handoff 40)
- Line numbers are the editor's own. The `...` rows stand for unseen lines 2-33 and 35-47; they are not in the file.
- Lines 48-51 are indented 2 spaces in the photo (the tail of a bullet that starts above line 48, so the opening of that bullet is not visible). Lines 52-53 and 54 start with `- `; line 53 is a continuation indented 2.
- Line 60: the OCR-sensitive part is "`**if present**` - it is not in the engine's persisted feature list, so V3 reports it as not persisted". The dash characters in lines 54, 60, 76, 77 are plain hyphens as shown (the photo does not render an em dash).
- `<p>` in dataset names (`crx_<p>_a4_deterioration` etc.) is a literal placeholder as printed. `<shipped method>` (lines 65-66) is also literal.
- Line 66: "(V4, V2-N0)" is as printed; "N0" could be a zero or an O.
- Line 62: the four A1 states match handoff 20/34 (`high` / `moderate` / `low` / `unknown`).
- Line 75-78: `due_date <= observation_date`, `payment_amount >= due_amount`, `due_date < obs` are OCR-risk comparison operators; "12 months" in line 78 is as shown; line 78 is cut at the bottom of the photo and ends mid-sentence ("The dcore features count every").
- Line 49: `anchor source` is a backtick-quoted table name as shown; "24 months" (line 50) is as shown.
