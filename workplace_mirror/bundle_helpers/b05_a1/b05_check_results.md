# Bundle 05 check — PROD results (rl_60_180, 2026-10-27)

Bundle 05 applied at work; `kedro run --env=dev --pipeline=crx_rl_a1_ability_b05_check`
completed 9/9 tasks in 773 s. Transcribed from photos by a chat session
(`pics/claude_code_handoff_4.md`), so single digits may be misread; the sums below check out.

## Engine log, latest month 2026-08-31 (n=3,985)

high 1 (0.0%) · low 3,566 (89.5%) · moderate 56 (1.4%) · unknown 362 (9.1%)

## B05 OUTPUT

```
model_id=rl_60_180 months 2026-01-31..2026-08-31 rows=24604 changed=18595 (75.58%)
  distress flag: {None: 873, 1: 4707, 0: 19024}
  EMI anchor present: {None: 873, True: 23731}  p10/p50/p90: [1193.94, 2370.0, 8085.0]
  latest month 2026-08-31: {'moderate': 56, 'low': 3566, 'unknown': 362, 'high': 1}
  income level x liquidity level:
  None x None 873 | none x adequate 308 | none x none 21090 | none x weak 1681
  stable x adequate 29 | stable x none 75 | stable x weak 33
  weak x adequate 26 | weak x none 379 | weak x weak 110
  old state x new state:
  (absent)  x low 346 | (absent) x moderate 23 | (absent) x unknown 56
  high      x (absent) 69 | high x high 9 | high x low 2673 | high x moderate 228 | high x unknown 87
  low       x (absent) 65 | low x low 4091 | low x moderate 13 | low x unknown 152
  moderate  x (absent) 7 | moderate x high 1 | moderate x low 24 | moderate x unknown 2
  unknown   x (absent) 732 | unknown x high 7 | unknown x low 13968 | unknown x moderate 142
  unknown   x unknown 1909
```

## B05 INCOME

```
model_id=rl_60_180 rows=23731 rows with a loan bureau salary in the 3-month window: 3
  income level engine x without feature_retail_loans:
    none x none 23079 | stable x stable 137 | weak x none 3 | weak x weak 512
  state engine x without:
    high x high 17 | low x low 21102 | moderate x low 1 | moderate x moderate 405
    unknown x unknown 2206
```

## Review

**The check runs and is consistent:** 23,731 engine rows in both blocks; every engine row
has an EMI anchor (median AED 2,370, so a median income bar of ~AED 4,740); the old / new
cells sum to 24,604 and to `changed`. The 873 / 425 `(absent)` rows are the two bases
differing (the waterfall ran on the spell spine, the engine on the persona obs base).

1. **Why 75.6% changed — by design, not a defect.**
   - The waterfall's state is `unknown` whenever no rule fires (`.otherwise`), so 16,758 old
     rows (68%) were unknown. The engine's unknown is narrow (0 points, no distress, no CASA
     movement), so 13,968 of them become low.
   - 2,673 waterfall highs become low: the waterfall's high arms compared CASA / payments with
     the EMI and read payment behaviour; the engine needs stable income and adequate
     liquidity for high.
2. **The distribution is almost all Low:** low 89.5%, unknown 9.1%, moderate 1.4%, high 1
   account. Income is none on 97.3% of rows (stable 0.6%), liquidity none on 90.8%, distress
   19.8% (CC: 9.6%). Unknown is far lower than CC (62.7%): RL customers almost all move money
   through a CASA with us.
3. **Suspicious — Low mostly means "CASA moved, nothing qualifies".** 21,090 rows have 0
   points; only 2,206 are unknown, so at least ~14K rows are Low only because of CASA activity
   (`casa_active`) and up to 4,707 because of distress. Two hypotheses make that circular:
   - **H-A** (replaces H-RL1, user 2026-10-27: the CASA flows exclude the loan account, and the
     WM inflow / outflow amounts carry administrative records such as fees): `casa_active`
     fires on fees / charges / system postings, not customer-initiated transactions — for CC
     too;
   - **H-RL2:** the DDS rejects are failed EMI collections, so distress restates the
     delinquency the model is predicting.
   Both go to the Sonnet (A1 v03, RL part) before the RL results reach GRR.
4. **The `feature_retail_loans` salary barely matters** (3 rows in the window, 3 income
   levels weak instead of none, 1 state moderate instead of low) — expected with one pull per
   loan; it grows once the source refreshes more often.

**Next:** Step 8 (`kedro run --env=dev --pipeline=crx_rl_a1_ability_v2`) is safe — a new
dataset nothing reads yet — then bundle 05's cleanup prompt. A1 v03 part D tests H-A (CC and RL) /
H-RL2; a confirmed hypothesis is a rule change for the user to decide (e.g. only customer-initiated
transactions count for `casa_active`; EMI-collection DDS excluded from distress).
