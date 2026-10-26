# Bundle 03 check — PROD results (cc_60_180, 2026-10-26)

Bundle 04 applied at work; `kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check`
completed 9/9 tasks in 816 s. Transcribed from photos by a chat session
(`pics/claude_code_handoff.md`), so single digits may be misread; the sums below all check out.

## B03 OUTPUT

```
model_id=cc_60_180 months 2026-01-31..2026-08-31 rows=128927 changed=14393 (11.16%)
  distress flag: {1: 12414, 0: 116513}
  latest month 2026-08-31: {'moderate': 204, 'low': 6984, 'unknown': 12096, 'high': 8}
  income level x liquidity level:
  none     x adequate    1099 | none     x none   122797 | none     x weak   2091
  stable   x adequate     340 | stable   x none      800 | stable   x weak    304
  weak     x adequate     157 | weak     x none     1080 | weak     x weak    259
  old state x new state:
  high     x high         169 | high     x low         3 | high     x moderate   58
  low      x high          16 | low      x low     41860 | low      x moderate  532
  low      x unknown    10430
  moderate x high          90 | moderate x low       888 | moderate x moderate 1650
  moderate x unknown       80
  unknown  x low         2294 | unknown  x moderate    2 | unknown  x unknown 70855
```

Engine log, latest month 2026-08-31 (n=19,292): high 8 (0.0%), low 6,984 (36.2%),
moderate 204 (1.1%), unknown 12,096 (62.7%).

## B03 INCOME

```
model_id=cc_60_180 rows=128927 engine-level mismatches=0 (must be 0)
  bar raised above 3000: 28869 (22.39%)  bar p50/p90/p99 where raised: [4390.8, 9460.74, 22052.14]
  2 of 3 months reach the bar: 1766  reach the flat floor: 1807
  2 of 3 months reach the bar but weakening fails: 322  (flat floor: 331)
  flat floor            levels: weak->stable 32          states: low->moderate 19
  no weakening check    levels: weak->stable 322         states: low->moderate 178, moderate->high 65
  flat floor + no weak. levels: weak->stable 363         states: low->moderate 201, moderate->high 65
  (every other cell on the diagonal: none 125987, stable 1444, high 275, low ~44.9K,
   moderate ~2.2K, unknown 81365)
```

## Review

**The check passes.** The engine reproduces its own income level (0 mismatches); the old and
new outputs match one-to-one by account and month (no `(absent)` rows, both sides 128,927);
the crosstab cells sum to the `changed` count.

1. **What moved (11.2%).** Two cells carry 87% of the changes: low → unknown 10,430 (8.1% of
   rows) and unknown → low 2,294. Unknown needs 0 points, no distress and no CASA transaction
   in the window, so both cells come from the two intended bundle 03 changes, not from the
   ladder: (a) the window moved forward one month (bundle 02: the 3 complete months before
   the billing month; now the observation month + 2 before), and a 60–180 customer's CASA
   keeps drying up, so the later window finds no activity more often than it finds new
   activity; (b) POS reversals (`RETURNS`) no longer count as distress, so a customer whose
   only evidence was a reversal now falls to unknown (Sonnet v01 measured ~1.1K state flips
   from this alone). The aggregates cannot split (a) from (b); the CC A1 final report (Sonnet
   v03) should.
2. **The distribution is thin at the top.** Latest month: unknown 62.7%, low 36.2%,
   moderate 1.1%, high 8 accounts. Income is `none` on 97.7% of rows and liquidity `none` on
   96.7% (v01: 94.6%), so almost no one reaches 2+ points. This is the known coverage gap
   (~34% hold no CASA with us, few recent salaries), not a defect; the GRR bureau salary feed
   is the planned fix. Unknown (62.7%) is well above the no-CASA share (~34%) because a
   dormant CASA with a balance under AED 1,000 also gives 0 points and no activity.
3. **Distress fires on 9.6% of rows** (12,414).
4. **Income rules, as specified, matter little at today's coverage.** The 2 × anchor bar is
   above AED 3,000 on 22% of rows (median bar AED 4,391), but only 41 rows reach the flat
   floor and miss the raised bar: 32 income levels, 19 states. The weakening check demotes
   322 of the 1,766 qualifying rows (18%) to weak: 243 states (178 low → moderate and 65
   moderate → high without it). Both rules stay (workbook S-rules); worth one line in the
   final report.

**Next:** bundle 03 Step 9 (`crx_cc_a1_ability_v2`), then bundle 03's cleanup prompt.
