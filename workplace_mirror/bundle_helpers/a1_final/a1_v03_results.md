# A1 v03 — PROD results (cc_60_180, 31 Aug 2026)

Source: `tmp_validation/a1_v03/summary.md` at work (commit "A1 v03 Leg C: results + GRR
summary", ~2026-10-26), transcribed from photos (`pics/claude_code_handoff_7.md`), so single
digits may be misread. The summary was written from the **first version of the v03 prompt**:
it has no v0 (bureau inputs), no v2b / v2c (salary timing, EOS), no part D (activity gate,
RL), and no RL run. Those parts are asked in `sonnet_a1_v03b_prompt.md`.

## Numbers (latest month, n = 19,292)

| | |
|---|---|
| States | unknown 62.7% (12,096) · low 36.2% (6,984) · moderate 1.1% (204) · high 8 (0.04%) |
| High | only path: stable income + adequate liquidity, no distress; 42 accounts have stable income, 196 adequate liquidity |
| Moderate | 109 (53%) adequate liquidity with no income; 18 stable income with no liquidity |
| Low | 92.5% = 0 points: 4,752 (68%) CASA flow and no distress, 1,712 (24.5%) distress; 1 point from income 170, from liquidity 296; 2–3 points knocked down by distress 54 |
| Unknown | 52.7% no CASA with us, 47.3% a dormant CASA; 68% no salary in 24 months, the rest an old internal salary; 88% of their CIFs had a bureau pull in 12 months |
| Income none | 98.5% (18,994): no salary in 24 months 53.6%; stale 45.8% (m4–6 10.3%, m7–12 24.3%, > 12 m 11.2%) |
| Salary sources (18,731 CIFs) | internal only 46.9% · bureau only 0.06% · both 0.12% · neither 53.0% |
| Liquidity none | 97.2% (18,754): CASA held but balance low / missing 62.5%, no CASA 37.5%; any CASA flow in W 34.3%; external card payment 0.6% (median AED 830) |
| Distress (CIFs) | 9.4% (1,764): DDS only 571, bureau only 614, cheque only 430; overlaps 107 / 25 / 16 / 1. 26.4% of Low carry it, 0.5% of Moderate; 35.2% of bureau-only flags repeat an amount from an earlier extract |
| Anchor | present on all rows, p10/p50/p90 AED 128 / 837 / 2,342; raises the income bar above 3,000 for 23.6%, the liquidity floor for 5.5% |
| Stability | 8 persona months: unknown 61.2–64.7%, low 33.0–37.0%, moderate 1.6–2.1%, high 0.18–0.33% |
| Recompute | 128,927 rows, 0 mismatches on state, levels, points and distress |

## Review

1. **The engine does what the spec says** (0 recompute mismatches), and the mix is stable
   month to month. What is left is about the inputs, not the code.
2. **The CC Low state has the same shape as RL:** 68% of Low = 0 points + a CASA flow. So the
   activity-gate question (H-A, admin records in the WM CASA flows) matters for CC as much as
   for RL. It is untested here (part D missing).
3. **Bureau salary is almost absent, yet the bureau pulls exist:** 88% of the Unknown CIFs
   have a pull in 12 months, but only 0.18% of CIFs have any bureau salary in 24 months.
   - The month parse is not the cause: staging documents `subj_salcr_hist_ref_mnth` as MMYYYY
     (`"072023"`, handoff 9), which is what the engine parses; the DE model's "YYYYMM" is the
     wrong one.
   - It could be data scarcity (bureau salary is reported only when an employer pays through a
     reporting bank) or a broken join (the bridge, the file id, the load date). v0 decides this
     and needs the "pull but no salary" count, which the summary does not carry.
4. **Bureau repeats are real:** 35.2% of bureau-only distress flags repeat an earlier amount,
   which is the case for the finish bundle's "identical repeats are the same bounce" rule. That
   rule will lower bureau distress (at most ~216 CIFs).
5. **Liquidity is missing mostly because balances are low, not for lack of a relationship:**
   62.5% hold a CASA. GRR's bureau salary feed does not fix liquidity.

## Still open (v03b)

v0 bureau inputs · v2b salary timing and the S12 window-total rule's effect · v2c EOS spikes ·
the N1 / N2–N4 × pull-without-salary count · part D (H-A for CC and RL, H-RL1, H-RL2) · the RL
run of all of it. The GRR results note waits for these.
