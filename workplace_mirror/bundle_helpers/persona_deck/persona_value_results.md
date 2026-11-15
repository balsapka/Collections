# Persona value map: results (cc_60_180 and rl_60_180)

Source: `persona_value_<model_id>.json/.md`, produced by `persona_value_map.py` (PROD run, persona
month Aug 2026, cohorts Jan-May 2026, payments to 2026-08-31). Headline = May 2026 cohort (payments
Jun-Aug); robustness = pooled Jan-May. Recovery = collected over 3 months / outstanding principal at
the cohort month end (cards `prm_balance.bnp_principal`, loans
`int_loan_master.outstanding_balance`), over accounts with a positive outstanding principal.
Intervals are bootstrap 90% (500 draws, resampling accounts). Cells under 10 accounts are
suppressed.

**Outstanding principal coverage (non-null / positive):** cards 100.0% / 97.6% of account-months;
loans 100.0% / 99.6-99.7%.

## Book totals

```text
model: cc_60_180
window: May
accounts: 15,890
account-months: 15,890
outstanding AED: 332,142,561
collected AED: 10,146,493
recovery %: 3.0
paid %: 18.6
AED collected / acct: 638.5
mean outstanding: 21,426
median outstanding: 15,928

model: cc_60_180
window: Jan-May pooled
accounts: 29,629
account-months: 74,256
outstanding AED: 1,498,769,516
collected AED: 46,779,352
recovery %: 3.1
paid %: 19.5
AED collected / acct: 630.0
mean outstanding: 20,681
median outstanding: 15,920

model: rl_60_180
window: May
accounts: 3,096
account-months: 3,096
outstanding AED: 343,416,531
collected AED: 11,261,370
recovery %: 3.3
paid %: 36.6
AED collected / acct: 3,637.4
mean outstanding: 111,282
median outstanding: 64,172

model: rl_60_180
window: Jan-May pooled
accounts: 5,416
account-months: 12,512
outstanding AED: 1,417,553,626
collected AED: 42,514,152
recovery %: 3.0
paid %: 33.3
AED collected / acct: 3,397.9
mean outstanding: 113,732
median outstanding: 65,663
```

Pooled mean/median outstanding are per account-month; May is per account.

## Findings

### Cards (cc_60_180)

1. **Concentration.** 17 personas hold 50% of outstanding principal and 63 hold 80% in May (pooled
   18 and 66), out of 337 personas in May; the 102 personas with 30+ accounts hold 89.4%. One
   persona (Stopped suddenly, departure trail, not reachable, low credibility, ability unknown)
   holds 11.6% (pooled).
2. **Biggest is not best.** Top-10 lists by outstanding and by collected share 3 personas in May (2
   pooled). The top 10 by outstanding hold 39.5% of outstanding but 10.3% of collected (pooled). The
   'large, not paying back' quadrant is 50 personas, 68.1% of outstanding, 27.6% of collected,
   recovery 1.27% against a book 3.12%.
3. **Best-recovering personas.** Of the 19 personas with at least 1% of outstanding (together
   51.8%), only 3 recover above the book average, all in-country and reachable: Cured before, low
   credibility, low ability 5.1% (1.0% of outstanding); Stopped suddenly, low credibility, ability
   unknown 4.0% (1.2%); Stopped suddenly, low credibility, low ability 3.6% (1.6%). Far higher
   recoveries sit in small Curing-now, reachable personas, e.g. moderate credibility / high ability
   24.5%, moderate credibility / ability unknown 17.5%, each 0.2-0.6% of outstanding.
4. **High-credibility / High-ability.** Pooled recovery, High credibility 11.9% [11.2, 12.6] vs
   2.84% for everyone else; High ability 9.1% [8.0, 10.2] vs 2.99%; either High 10.6% [10.0, 11.3]
   vs 2.72% (6.5% of accounts, 5.0% of outstanding, 16.9% of collected). Paid: 66% / 40% / 55% vs
   17-19%. It holds inside each family (either-High minus rest, recovery pp, 90% CI): Curing now
   +2.5 [1.4, 3.5], Cured before +2.8 [1.9, 3.7], Stopped suddenly +3.8 [2.9, 4.9]; Never paid (23
   accounts) and Unknown (19) are too thin. The gap is smallest in Curing now, where recovery is
   already high.
5. **Slide examples** (two largest High-band personas by outstanding, 20+ pooled accounts): Curing
   now, location unknown, reachable, high credibility, ability unknown: 210 accounts, recovery 16.3%
   [14.2, 18.6], paid 75%, AED 2,052 per account; Curing now, in country, reachable, high
   credibility, moderate ability: 166 accounts, 14.95% [13.3, 16.7], paid 78%, AED 2,033 per
   account. Both are small in outstanding (0.3% and 0.2%).
6. **Stability.** Spearman of persona recovery, Jan-Apr vs May, 0.91 over 102 personas (share of
   outstanding 0.95). 88.2% of personas stay on the same side of the book-average line; the full
   quadrant is the same for 62.7% (the median-share cut moves, so quadrant agreement understates
   it). 36 of 102 personas have a May recovery outside their Jan-Apr monthly range (21 above, 15
   below), and the median bootstrap interval is 3.3pp wide: single-month recoveries of one persona
   are noisy, the ranking is not.

### Loans (rl_60_180)

1. **Concentration.** 18 personas hold 50% and 54 hold 80% of outstanding in May (pooled 20 and 65),
   out of 231 personas in May (284 pooled). Only 24 personas reach 30 accounts in May (55.7% of
   outstanding); 88 pooled (86.4%).
2. **Biggest is not best.** Top-10 lists by outstanding and by collected share 5 personas (May and
   pooled). Top 10 by outstanding hold 34.2% of outstanding and 15.6% of collected (pooled). 'Large,
   not paying back': 30 personas, 54.9% of outstanding, 25.6% of collected, recovery 1.40% vs book
   3.00%.
3. **Best-recovering personas.** Of 23 personas with at least 1% of outstanding (53.5% in total), 5
   recover above the book average, all Cured-before personas with low or moderate ability: 3.0-4.3%,
   so only slightly above 3.0%. The best large-share persona is Curing now, in country, reachable,
   high credibility, low ability: 8.7% on 0.6% of outstanding (55 accounts).
4. **High-credibility / High-ability.** May, either High: 188 accounts (6.1%; 3.6% of outstanding,
   10.2% of collected), recovery 9.4% [8.3, 10.6] vs 3.05% [2.8, 3.3] for the rest; paid 72% vs 34%.
   Pooled High ability (73 accounts): 10.4% [7.7, 13.3] vs 2.96%. The other pooled High groups are
   suppressed (small cells, see caveats). Within families (pooled, either-High minus rest): Curing
   now +1.9pp [0.6, 3.3], Cured before +3.5 [1.8, 5.1], Stopped suddenly +5.7 [2.6, 9.8] (60
   accounts); Never paid under 10.
5. **Slide examples** (two largest High-band personas by outstanding, 20+ pooled accounts; 9
   qualify, all High credibility, none High ability): Curing now, in country, reachable, high
   credibility, low ability: 55 accounts, recovery 8.7%, paid 82%, AED 8,046 per account; Cured
   before, in country, reachable, high credibility, low ability: 32 accounts, 8.35%, paid 59%, AED
   9,627 per account. These are thin; use as illustration, not as a segment size.
6. **Stability.** Spearman 0.80 over only 24 personas; 79.2% on the same side of the book-average
   line, 54.2% in the same quadrant. 7 of 24 personas have a May recovery outside their earlier
   range (6 above, 1 below); May paid % is above range for 13 of 24.

## Caveats

- **'Large' is relative.** The quadrant cut is the median persona's share of outstanding (cards
  0.21%, loans 0.58%), so 'large, paying back' contains small personas (e.g. 0.2% of outstanding).
  In absolute money the big personas pay poorly. The 1%-of-outstanding view in finding 3 is the
  plain-language alternative; the slide should say which cut it uses.
- **Thin loan personas.** Only 24 loan personas reach 30 accounts in May; the May-only loan map and
  its quadrants are fragile, use the pooled map.
- **Loan High groups partly suppressed.** In the loan JSON the pooled High-credibility, either-High
  and both-High rows (and May High-credibility, High-ability) are suppressed: cells under 10
  accounts in the grid and the families table would otherwise be recoverable by subtraction. The May
  either-High row and the pooled High-ability row are shown. If the slide needs the pooled
  either-High loan number, say so and the suppression rule can be relaxed for that row.
- **Loan payments are month-grain.** Paid and collected for loans come from month-end snapshots, so
  timing within months is unseen.
- **Observed payments reflect today's handling.** Recovery is what was collected under the current
  collections treatment, not what would be collected under a different one; low recovery in 'not
  reachable' personas partly reflects that they are not worked.
- **Credibility is a payment-history axis.** High credibility paying more is expected; the useful
  content is that it holds out-of-time and within each deterioration family.
- **Pooled windows repeat accounts.** An account can enter several cohort months; point estimates
  are per account-month, intervals resample whole accounts. Pooled 'accounts' are distinct accounts,
  pooled mean/median outstanding are per account-month.
- **Recovery is small in absolute terms.** Book recovery is about 3% of outstanding in 3 months, so
  a 1pp difference is a third of the book rate.

## cc_60_180: value-map table (pooled Jan-May, personas with 30+ distinct accounts)

Book recovery (reference line) 3.12%; median share of outstanding 0.207%; 187 personas hold 97.2% of
outstanding and 94.2% of collected. Size = average monthly accounts.

**Quadrants**

```text
quadrant: large, paying back
personas: 43
avg monthly accounts: 3,128.8
% outstanding: 19.7
% collected: 46.0
recovery %: 7.3
three largest by outstanding (x % / y %): Stopped suddenly · in country · reachable · low
                                          credibility · low ability (1.588 / 3.59); Stopped suddenly
                                          · in country · reachable · low credibility · ability
                                          unknown (1.186 / 4.04); Cured before · in country ·
                                          reachable · low credibility · low ability (1.006 / 5.13)

quadrant: large, not paying back
personas: 50
avg monthly accounts: 9,664.0
% outstanding: 68.1
% collected: 27.6
recovery %: 1.3
three largest by outstanding (x % / y %): Stopped suddenly · departure trail · not reachable · low
                                          credibility · ability unknown (11.609 / 0.5); Never paid ·
                                          location unknown · not reachable · low credibility ·
                                          ability unknown (5.586 / 0.14); Stopped suddenly ·
                                          location unknown · not reachable · low credibility ·
                                          ability unknown (5.08 / 0.64)

quadrant: small, paying back
personas: 71
avg monthly accounts: 1,251.2
% outstanding: 7.2
% collected: 19.4
recovery %: 8.4
three largest by outstanding (x % / y %): Curing now · location unknown · reachable · high
                                          credibility · moderate ability (0.207 / 16.61); Stopped
                                          suddenly · departure trail · reachable · moderate
                                          credibility · low ability (0.205 / 7.2); Cured before ·
                                          location unknown · reachability unknown · low credibility
                                          · ability unknown (0.194 / 4.53)

quadrant: small, not paying back
personas: 23
avg monthly accounts: 382.4
% outstanding: 2.3
% collected: 1.1
recovery %: 1.5
three largest by outstanding (x % / y %): Never paid · departure trail · reachable · low credibility
                                          · ability unknown (0.2 / 1.3); Stopped suddenly ·
                                          departure trail · reachability unknown · moderate
                                          credibility · ability unknown (0.197 / 1.67); Stopped
                                          suddenly · location unknown · reachability unknown · low
                                          credibility · low ability (0.187 / 0.55)
```

**Points**

x = share of outstanding (%), y = recovery (%), size = average monthly accounts, accts = distinct
accounts.

```text
persona                                                        x      y     size  accts  quadrant
----------------------------------------------------------------------------------------------------------
Stopped suddenly · departure trail · not reachable ·        11.6    0.5  1,750.2  4,433  large not paying
low credibility · ability unknown
Never paid · location unknown · not reachable · low          5.6    0.1    512.0  1,144  large not paying
credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        5.1    0.6    851.6  2,356  large not paying
low credibility · ability unknown
Stopped suddenly · departure trail · not reachable ·         3.7    0.6    484.8  1,597  large not paying
low credibility · low ability
Stopped suddenly · in country · not reachable · low          2.8    2.1    359.6  1,352  large not paying
credibility · low ability
Stopped suddenly · in country · not reachable · low          2.8    1.6    405.0  1,385  large not paying
credibility · ability unknown
Cured before · departure trail · not reachable · low         2.4    1.9    367.4  1,025  large not paying
credibility · ability unknown
Stopped suddenly · departure trail · reachability            1.9    1.1    305.8  1,067  large not paying
unknown · low credibility · ability unknown
Never paid · departure trail · not reachable · low           1.9    0.1    202.4    492  large not paying
credibility · ability unknown
Stopped suddenly · departure trail · reachable · low         1.8    1.7    220.4    891  large not paying
credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        1.7    1.1    273.8    951  large not paying
low credibility · low ability
Cured before · location unknown · not reachable · low        1.6    1.8    307.2    979  large not paying
credibility · ability unknown
Stopped suddenly · in country · reachable · low              1.6    3.6    197.4    820  large paying
credibility · low ability
Stopped suddenly · in country · not reachable · low          1.4    2.5    243.8    898  large not paying
credibility · moderate ability
Cured before · in country · not reachable · low              1.4    2.9    180.0    672  large not paying
credibility · low ability
Stopped suddenly · in country · reachable · low              1.2    4.0    165.0    659  large paying
credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        1.2    1.6    221.2    776  large not paying
low credibility · moderate ability
Cured before · in country · not reachable · low              1.1    2.2    170.2    624  large not paying
credibility · ability unknown
Cured before · in country · reachable · low                  1.0    5.1    122.8    485  large paying
credibility · low ability
Stopped suddenly · departure trail · not reachable ·         1.0    1.0    130.8    400  large not paying
moderate credibility · ability unknown
Stopped suddenly · departure trail · reachable · low         1.0    3.1    109.0    459  large not paying
credibility · low ability
Cured before · departure trail · not reachable · low         1.0    1.5    119.2    410  large not paying
credibility · low ability
Stopped suddenly · in country · reachable · low              1.0    4.7    142.2    578  large paying
credibility · moderate ability
Cured before · departure trail · not reachable ·             0.9    2.3    112.6    419  large not paying
moderate credibility · ability unknown
Stopped suddenly · location unknown · reachable · low        0.9    2.3    132.6    522  large not paying
credibility · ability unknown
Stopped suddenly · departure trail · not reachable ·         0.9    1.3    142.4    503  large not paying
low credibility · moderate ability
Never paid · location unknown · not reachable · low          0.9    0.2     64.6    200  large not paying
credibility · low ability
Cured before · location unknown · not reachable · low        0.8    2.7    141.0    526  large not paying
credibility · low ability
Cured before · in country · not reachable · low              0.8    2.9    130.8    515  large not paying
credibility · moderate ability
Stopped suddenly · departure trail · reachability            0.7    1.5    113.4    438  large not paying
unknown · low credibility · low ability
Cured before · location unknown · not reachable · low        0.7    2.2    138.8    498  large not paying
credibility · moderate ability
Cured before · departure trail · reachable · low             0.7    2.7     81.6    330  large not paying
credibility · ability unknown
Cured before · in country · not reachable · moderate         0.7    4.2     99.2    408  large paying
credibility · low ability
Cured before · location unknown · not reachable ·            0.7    2.1    102.6    382  large not paying
moderate credibility · ability unknown
Cured before · in country · reachable · moderate             0.7    7.6     80.0    353  large paying
credibility · low ability
Cured before · in country · reachable · low                  0.6    6.5    100.8    402  large paying
credibility · moderate ability
Cured before · in country · not reachable · moderate         0.6    3.1     84.2    332  large not paying
credibility · ability unknown
Cured before · in country · reachable · low                  0.6    5.2     88.2    357  large paying
credibility · ability unknown
Stopped suddenly · location unknown · reachability           0.6    1.2    143.2    503  large not paying
unknown · low credibility · ability unknown
Stopped suddenly · in country · not reachable ·              0.6    1.9     85.6    309  large not paying
moderate credibility · ability unknown
Never paid · location unknown · reachability unknown ·       0.6    0.7     65.8    261  large not paying
low credibility · ability unknown
Curing now · location unknown · reachable · moderate         0.6   17.5    147.4    358  large paying
credibility · ability unknown
Stopped suddenly · in country · not reachable ·              0.6    2.9     74.0    290  large not paying
moderate credibility · low ability
Cured before · location unknown · reachable · low            0.6    3.8     86.0    337  large paying
credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        0.6    1.7     98.0    334  large not paying
moderate credibility · ability unknown
Curing now · in country · reachable · moderate               0.5   15.5    109.8    332  large paying
credibility · moderate ability
Cured before · in country · reachable · moderate             0.5    6.9     67.6    289  large paying
credibility · moderate ability
Stopped suddenly · in country · reachable · moderate         0.5    6.7     68.6    300  large paying
credibility · low ability
Cured before · departure trail · not reachable ·             0.5    2.0     58.2    244  large not paying
moderate credibility · low ability
Never paid · location unknown · reachable · low              0.5    0.7     46.4    192  large not paying
credibility · ability unknown
Stopped suddenly · departure trail · not reachable ·         0.5    1.9     55.6    203  large not paying
moderate credibility · low ability
Cured before · in country · not reachable · moderate         0.5    4.0     78.2    321  large paying
credibility · moderate ability
Cured before · location unknown · not reachable ·            0.5    2.3     61.0    249  large not paying
moderate credibility · low ability
Cured before · departure trail · reachability unknown        0.5    1.8     64.0    220  large not paying
· low credibility · ability unknown
Curing now · location unknown · reachable · moderate         0.4   13.9     97.8    278  large paying
credibility · moderate ability
Cured before · departure trail · reachable · low             0.4    3.2     43.2    178  large paying
credibility · low ability
Cured before · in country · reachable · moderate             0.4    7.6     65.2    256  large paying
credibility · ability unknown
Never paid · departure trail · not reachable · low           0.4    0.7     48.8    164  large not paying
credibility · low ability
Stopped suddenly · in country · reachable · moderate         0.4    8.8     65.0    269  large paying
credibility · ability unknown
Curing now · in country · reachable · moderate               0.4   15.1     89.8    263  large paying
credibility · ability unknown
Cured before · departure trail · reachable · moderate        0.4    6.0     48.0    205  large paying
credibility · ability unknown
Stopped suddenly · location unknown · reachable · low        0.4    3.1     63.8    260  large not paying
credibility · low ability
Curing now · in country · reachable · moderate               0.4   12.2     70.2    247  large paying
credibility · low ability
Never paid · location unknown · not reachable · low          0.4    0.4     57.2    183  large not paying
credibility · moderate ability
Stopped suddenly · departure trail · reachable ·             0.4    5.0     48.4    205  large paying
moderate credibility · ability unknown
Stopped suddenly · in country · not reachable ·              0.4    2.3     59.4    229  large not paying
moderate credibility · moderate ability
Cured before · departure trail · reachable · moderate        0.4    6.8     34.6    150  large paying
credibility · low ability
Cured before · location unknown · reachable · low            0.4    5.9     60.4    243  large paying
credibility · moderate ability
Cured before · location unknown · reachable · moderate       0.3    6.3     60.6    248  large paying
credibility · ability unknown
Stopped suddenly · departure trail · reachable · low         0.3    4.3     45.0    189  large paying
credibility · moderate ability
Curing now · location unknown · reachable · high             0.3   16.3     81.0    210  large paying
credibility · ability unknown
Cured before · departure trail · not reachable · low         0.3    3.0     52.2    187  large not paying
credibility · moderate ability
Stopped suddenly · in country · reachable · moderate         0.3    8.3     53.6    231  large paying
credibility · moderate ability
Stopped suddenly · location unknown · reachable · low        0.3    3.7     59.6    244  large paying
credibility · moderate ability
Cured before · location unknown · reachable · moderate       0.3    4.5     30.2    126  large paying
credibility · low ability
Cured before · location unknown · reachable · low            0.3    5.1     53.0    220  large paying
credibility · low ability
Never paid · departure trail · reachability unknown ·        0.3    0.1     25.2     98  large not paying
low credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        0.3    2.1     47.8    178  large not paying
moderate credibility · low ability
Stopped suddenly · in country · reachability unknown ·       0.3    3.3     52.0    216  large paying
low credibility · ability unknown
Curing now · departure trail · reachable · moderate          0.3   12.3     48.8    132  large paying
credibility · ability unknown
Stopped suddenly · in country · reachability unknown ·       0.3    4.7     49.4    205  large paying
low credibility · low ability
Cured before · location unknown · not reachable ·            0.3    4.1     47.4    194  large paying
moderate credibility · moderate ability
Never paid · in country · not reachable · low                0.3    0.4     33.0    135  large not paying
credibility · ability unknown
Curing now · in country · reachable · high credibility       0.2   14.9     53.0    166  large paying
· moderate ability
Stopped suddenly · location unknown · reachable ·            0.2    5.5     40.8    170  large paying
moderate credibility · ability unknown
Curing now · location unknown · reachable · moderate         0.2   15.8     55.6    193  large paying
credibility · low ability
Stopped suddenly · departure trail · reachability            0.2    0.8     44.2    147  large not paying
unknown · low credibility · moderate ability
Cured before · location unknown · reachable · moderate       0.2    6.6     37.2    160  large paying
credibility · moderate ability
Stopped suddenly · location unknown · not reachable ·        0.2    3.1     40.0    145  large paying
moderate credibility · moderate ability
Curing now · in country · reachable · high credibility       0.2   13.4     42.0    143  large paying
· low ability
Curing now · in country · reachable · moderate               0.2   24.5     55.0    150  large paying
credibility · high ability
Curing now · in country · reachable · high credibility       0.2   13.8     48.8    141  large paying
· ability unknown
Never paid · in country · not reachable · low                0.2    1.2     21.6     92  large not paying
credibility · low ability
Curing now · location unknown · reachable · high             0.2   16.6     56.0    164  small paying
credibility · moderate ability
Stopped suddenly · departure trail · reachable ·             0.2    7.2     20.0     91  small paying
moderate credibility · low ability
Never paid · departure trail · reachable · low               0.2    1.3     19.8     82  small not paying
credibility · ability unknown
Stopped suddenly · departure trail · reachability            0.2    1.7     21.8     82  small not paying
unknown · moderate credibility · ability unknown
Cured before · location unknown · reachability unknown       0.2    4.5     38.2    153  small paying
· low credibility · ability unknown
Stopped suddenly · in country · reachability unknown ·       0.2    3.5     39.8    167  small paying
low credibility · moderate ability
Cured before · departure trail · reachable · low             0.2    5.9     24.6    109  small paying
credibility · moderate ability
Stopped suddenly · location unknown · reachability           0.2    0.6     48.2    193  small not paying
unknown · low credibility · low ability
Cured before · in country · not reachable · low              0.2    4.7     33.6    123  small paying
credibility · high ability
Curing now · departure trail · reachable · moderate          0.2   10.2     23.6     91  small paying
credibility · low ability
Curing now · location unknown · not reachable ·              0.2   11.3     38.6    157  small paying
moderate credibility · ability unknown
Cured before · departure trail · reachability unknown        0.2    3.2     20.0     84  small paying
· moderate credibility · ability unknown
Curing now · departure trail · reachable · moderate          0.2   14.1     31.4    105  small paying
credibility · moderate ability
Never paid · departure trail · not reachable · low           0.2    0.2     24.8     83  small not paying
credibility · moderate ability
Cured before · in country · reachable · low                  0.2    8.2     28.8    114  small paying
credibility · high ability
Stopped suddenly · in country · reachable · low              0.2    5.0     26.8     99  small paying
credibility · high ability
Cured before · in country · reachability unknown · low       0.2    4.1     17.8     77  small paying
credibility · low ability
Curing now · in country · reachable · low credibility        0.2   20.2     24.2     84  small paying
· moderate ability
Curing now · location unknown · not reachable ·              0.2    8.8     29.0    119  small paying
moderate credibility · moderate ability
Curing now · in country · reachable · low credibility        0.1    9.1     19.4     72  small paying
· low ability
Never paid · in country · not reachable · low                0.1    1.9     19.0     69  small not paying
credibility · moderate ability
Cured before · departure trail · not reachable ·             0.1    4.2     22.4     91  small paying
moderate credibility · moderate ability
Curing now · in country · not reachable · moderate           0.1    5.7     21.4     94  small paying
credibility · low ability
Cured before · departure trail · reachability unknown        0.1    2.2     24.4     97  small not paying
· low credibility · low ability
Curing now · location unknown · reachable · low              0.1    8.5     20.8     81  small paying
credibility · ability unknown
Stopped suddenly · departure trail · reachable ·             0.1    5.7     15.8     67  small paying
moderate credibility · moderate ability
Curing now · in country · reachable · high credibility       0.1   15.4     26.0     71  small paying
· high ability
Curing now · location unknown · reachable · high             0.1   16.4     33.8    107  small paying
credibility · low ability
Stopped suddenly · location unknown · reachability           0.1    1.9     48.0    175  small not paying
unknown · low credibility · moderate ability
Curing now · in country · not reachable · moderate           0.1   10.3     22.6     98  small paying
credibility · moderate ability
Stopped suddenly · location unknown · reachable ·            0.1    8.2     20.4     87  small paying
moderate credibility · low ability
Stopped suddenly · departure trail · reachability            0.1    1.0     11.0     45  small not paying
unknown · moderate credibility · low ability
Cured before · in country · reachability unknown · low       0.1    4.9     18.8     84  small paying
credibility · ability unknown
Stopped suddenly · location unknown · reachable ·            0.1    7.5     21.6     93  small paying
moderate credibility · moderate ability
Never paid · location unknown · reachable · low              0.1    2.4     10.2     46  small not paying
credibility · low ability
Stopped suddenly · in country · not reachable · low          0.1    6.4     20.6     85  small paying
credibility · high ability
Cured before · in country · reachability unknown · low       0.1    4.8     23.0     91  small paying
credibility · moderate ability
Curing now · departure trail · not reachable ·               0.1    4.7     20.0     82  small paying
moderate credibility · ability unknown
Cured before · in country · reachable · moderate             0.1    6.0     18.4     80  small paying
credibility · high ability
Cured before · departure trail · reachable · moderate        0.1    5.8     15.4     65  small paying
credibility · moderate ability
Stopped suddenly · departure trail · not reachable ·         0.1    2.1     16.0     66  small not paying
moderate credibility · moderate ability
Cured before · in country · reachability unknown ·           0.1    7.0     12.6     58  small paying
moderate credibility · low ability
Curing now · in country · not reachable · moderate           0.1    9.6     21.4     90  small paying
credibility · ability unknown
Curing now · departure trail · reachable · high              0.1    9.7     18.6     63  small paying
credibility · ability unknown
Curing now · location unknown · reachable · low              0.1   17.4     20.6     76  small paying
credibility · moderate ability
Curing now · departure trail · reachable · high              0.1   10.9     12.6     44  small paying
credibility · low ability
Curing now · location unknown · not reachable ·              0.1    8.3     16.6     69  small paying
moderate credibility · low ability
Curing now · location unknown · reachable · low              0.1   10.9     15.6     66  small paying
credibility · low ability
Cured before · departure trail · reachability unknown        0.1    1.6      8.6     39  small not paying
· moderate credibility · low ability
Curing now · departure trail · not reachable ·               0.1    5.4     11.2     50  small paying
moderate credibility · low ability
Curing now · in country · reachable · low credibility        0.1   11.9     16.8     63  small paying
· ability unknown
Cured before · location unknown · reachability unknown       0.1    9.0     22.6     86  small paying
· low credibility · low ability
Cured before · in country · not reachable · moderate         0.1    6.7     14.6     58  small paying
credibility · high ability
Never paid · departure trail · reachable · low               0.1    0.8      7.6     32  small not paying
credibility · low ability
Cured before · location unknown · reachability unknown       0.1    4.6     10.8     46  small paying
· moderate credibility · ability unknown
Never paid · in country · reachable · low credibility        0.1    4.1      6.6     31  small paying
· low ability
Never paid · location unknown · reachable · low              0.1    1.9     13.4     53  small not paying
credibility · moderate ability
Curing now · departure trail · reachable · high              0.1   13.8     12.2     37  small paying
credibility · moderate ability
Cured before · location unknown · reachability unknown       0.1    2.3     19.2     78  small not paying
· low credibility · moderate ability
Curing now · in country · reachable · low credibility        0.1   15.6     11.0     37  small paying
· high ability
Cured before · in country · reachable · high                 0.1   11.2      7.2     33  small paying
credibility · low ability
Never paid · in country · reachable · low credibility        0.1    1.8      7.4     36  small not paying
· moderate ability
Curing now · location unknown · not reachable · high         0.1    9.7     13.2     57  small paying
credibility · ability unknown
Stopped suddenly · in country · reachable · moderate         0.1    8.6     10.4     45  small paying
credibility · high ability
Cured before · in country · reachable · high                 0.1    9.4      7.0     31  small paying
credibility · moderate ability
Curing now · departure trail · not reachable ·               0.1    6.3      9.6     39  small paying
moderate credibility · moderate ability
Stopped suddenly · in country · not reachable ·              0.1    3.6      8.8     34  small paying
moderate credibility · high ability
Stopped suddenly · location unknown · reachability           0.1    2.4     13.0     51  small not paying
unknown · moderate credibility · ability unknown
Stopped suddenly · in country · reachability unknown ·       0.1    3.1      9.0     42  small not paying
moderate credibility · low ability
Curing now · in country · not reachable · high               0.1    8.9      8.8     39  small paying
credibility · low ability
Never paid · in country · reachable · low credibility        0.1    0.7      7.0     32  small not paying
· ability unknown
Curing now · departure trail · reachable · low               0.1   10.4     10.4     37  small paying
credibility · ability unknown
Curing now · location unknown · not reachable · low          0.1    6.5      9.6     43  small paying
credibility · low ability
Curing now · location unknown · not reachable · low          0.0    3.9     10.6     42  small paying
credibility · moderate ability
Curing now · in country · not reachable · low                0.0    4.0      7.0     30  small paying
credibility · low ability
Cured before · in country · reachability unknown ·           0.0    4.3      7.6     32  small paying
moderate credibility · ability unknown
Cured before · departure trail · reachability unknown        0.0    1.9     12.4     42  small not paying
· low credibility · moderate ability
Curing now · in country · not reachable · high               0.0   10.2      9.0     40  small paying
credibility · moderate ability
Stopped suddenly · in country · reachability unknown ·       0.0    1.6      7.2     31  small not paying
moderate credibility · ability unknown
Curing now · in country · not reachable · moderate           0.0   13.2      9.6     40  small paying
credibility · high ability
Never paid · location unknown · reachability unknown ·       0.0    0.6     14.8     59  small not paying
low credibility · moderate ability
Cured before · in country · reachable · high                 0.0   10.8      7.4     32  small paying
credibility · ability unknown
Curing now · location unknown · not reachable · high         0.0    9.2      9.0     34  small paying
credibility · moderate ability
Curing now · location unknown · not reachable · low          0.0    3.5     10.8     44  small paying
credibility · ability unknown
Stopped suddenly · in country · reachable · high             0.0   10.5      7.4     32  small paying
credibility · ability unknown
Never paid · location unknown · reachability unknown ·       0.0    0.0      7.2     33  small not paying
low credibility · low ability
Cured before · location unknown · reachable · high           0.0   11.9      6.6     30  small paying
credibility · ability unknown
Curing now · in country · not reachable · low                0.0    6.0      8.2     39  small paying
credibility · ability unknown
Stopped suddenly · in country · reachable · high             0.0   10.2      7.6     32  small paying
credibility · low ability
Curing now · departure trail · not reachable · low           0.0    5.8      8.8     34  small paying
credibility · ability unknown
Cured before · in country · reachability unknown · low       0.0    7.0      9.6     36  small paying
credibility · high ability
Curing now · in country · not reachable · low                0.0    7.6      7.2     31  small paying
credibility · moderate ability
Stopped suddenly · departure trail · reachability            0.0    0.0     12.4     41  small not paying
unknown · low credibility · high ability
Stopped suddenly · in country · reachability unknown ·       0.0    6.5     23.2     79  small paying
low credibility · high ability
```

## rl_60_180: value-map table (pooled Jan-May, personas with 30+ distinct accounts)

Book recovery (reference line) 3.0%; median share of outstanding 0.575%; 88 personas hold 86.4% of
outstanding and 76.9% of collected. Size = average monthly accounts.

**Quadrants**

```text
quadrant: large, paying back
personas: 14
avg monthly accounts: 394.6
% outstanding: 15.4
% collected: 22.6
recovery %: 4.4
three largest by outstanding (x % / y %): Cured before · in country · not reachable · low
                                          credibility · low ability (1.982 / 3.05); Cured before ·
                                          in country · reachable · low credibility · low ability
                                          (1.939 / 3.72); Cured before · departure trail · reachable
                                          · low credibility · low ability (1.538 / 3.92)

quadrant: large, not paying back
personas: 30
avg monthly accounts: 1,145.6
% outstanding: 54.9
% collected: 25.6
recovery %: 1.4
three largest by outstanding (x % / y %): Stopped suddenly · departure trail · not reachable · low
                                          credibility · low ability (7.232 / 0.98); Stopped suddenly
                                          · departure trail · not reachable · low credibility ·
                                          ability unknown (5.905 / 0.98); Stopped suddenly · in
                                          country · not reachable · low credibility · low ability
                                          (3.369 / 1.6)

quadrant: small, paying back
personas: 37
avg monthly accounts: 459.2
% outstanding: 12.8
% collected: 26.9
recovery %: 6.3
three largest by outstanding (x % / y %): Stopped suddenly · location unknown · not reachable ·
                                          moderate credibility · low ability (0.541 / 3.91); Cured
                                          before · location unknown · reachable · moderate
                                          credibility · low ability (0.53 / 8.29); Curing now · in
                                          country · reachable · moderate credibility · moderate
                                          ability (0.529 / 8.96)

quadrant: small, not paying back
personas: 7
avg monthly accounts: 79.0
% outstanding: 3.3
% collected: 1.9
recovery %: 1.7
three largest by outstanding (x % / y %): Cured before · in country · not reachable · moderate
                                          credibility · ability unknown (0.529 / 2.75); Stopped
                                          suddenly · location unknown · reachable · low credibility
                                          · ability unknown (0.527 / 1.92); Never paid · departure
                                          trail · reachability unknown · low credibility · ability
                                          unknown (0.479 / 0.05)
```

**Points**

x = share of outstanding (%), y = recovery (%), size = average monthly accounts, accts = distinct
accounts.

```text
persona                                                        x      y     size  accts  quadrant
----------------------------------------------------------------------------------------------------------
Stopped suddenly · departure trail · not reachable · low     7.2    1.0    139.6    476  large not paying
credibility · low ability
Stopped suddenly · departure trail · not reachable · low     5.9    1.0    150.8    452  large not paying
credibility · ability unknown
Stopped suddenly · in country · not reachable · low          3.4    1.6     67.2    261  large not paying
credibility · low ability
Cured before · departure trail · not reachable · low         3.3    1.1     77.4    230  large not paying
credibility · ability unknown
Cured before · departure trail · not reachable · low         3.0    1.5     54.4    197  large not paying
credibility · low ability
Stopped suddenly · in country · reachable · low              2.8    2.4     51.2    205  large not paying
credibility · low ability
Stopped suddenly · departure trail · reachable · low         2.5    1.7     34.8    133  large not paying
credibility · low ability
Stopped suddenly · departure trail · reachability unknown    2.2    0.5     49.8    181  large not paying
· low credibility · ability unknown
Cured before · in country · not reachable · low              2.0    3.0     49.8    186  large paying
credibility · low ability
Stopped suddenly · location unknown · not reachable · low    1.9    1.2     45.2    151  large not paying
credibility · ability unknown
Cured before · in country · reachable · low credibility ·    1.9    3.7     32.6    130  large paying
low ability
Stopped suddenly · departure trail · reachability unknown    1.9    1.4     44.8    186  large not paying
· low credibility · low ability
Never paid · departure trail · not reachable · low           1.8    0.0     31.0     86  large not paying
credibility · ability unknown
Never paid · departure trail · not reachable · low           1.7    0.2     26.2     88  large not paying
credibility · low ability
Stopped suddenly · location unknown · not reachable · low    1.6    2.2     35.2    123  large not paying
credibility · low ability
Cured before · departure trail · reachable · low             1.5    3.9     22.8     87  large paying
credibility · low ability
Stopped suddenly · departure trail · reachable · low         1.5    1.0     26.8    108  large not paying
credibility · ability unknown
Cured before · in country · not reachable · moderate         1.4    4.3     38.0    153  large paying
credibility · low ability
Stopped suddenly · in country · not reachable · low          1.3    0.7     27.4     96  large not paying
credibility · ability unknown
Cured before · in country · reachable · moderate             1.2    4.1     33.2    139  large paying
credibility · low ability
Cured before · location unknown · not reachable · low        1.1    2.6     26.2    101  large not paying
credibility · low ability
Cured before · departure trail · not reachable · moderate    1.1    1.9     24.6     98  large not paying
credibility · low ability
Stopped suddenly · in country · reachable · moderate         1.1    2.8     21.2     86  large not paying
credibility · low ability
Cured before · location unknown · not reachable · low        1.0    3.4     37.2    125  large paying
credibility · ability unknown
Cured before · in country · not reachable · low              1.0    1.8     27.0    101  large not paying
credibility · ability unknown
Cured before · departure trail · reachable · moderate        0.9    5.0     18.0     66  large paying
credibility · low ability
Cured before · location unknown · not reachable ·            0.9    4.9     28.4    109  large paying
moderate credibility · low ability
Stopped suddenly · departure trail · not reachable ·         0.9    1.8     16.8     63  large not paying
moderate credibility · low ability
Stopped suddenly · in country · not reachable · moderate     0.9    2.5     20.0     77  large not paying
credibility · low ability
Cured before · departure trail · reachability unknown ·      0.9    2.2     16.4     64  large not paying
low credibility · low ability
Curing now · in country · reachable · moderate               0.9    8.5     26.4    100  large paying
credibility · low ability
Cured before · in country · reachable · low credibility ·    0.8    4.4     20.0     70  large paying
ability unknown
Never paid · location unknown · not reachable · low          0.8    0.9     17.0     54  large not paying
credibility · ability unknown
Stopped suddenly · in country · reachability unknown ·       0.8    2.8     17.4     76  large not paying
low credibility · low ability
Never paid · location unknown · not reachable · low          0.8    0.7     12.8     30  large not paying
credibility · low ability
Cured before · location unknown · reachable · low            0.8    3.5     16.2     66  large paying
credibility · low ability
Stopped suddenly · in country · reachable · low              0.8    1.9     15.2     60  large not paying
credibility · ability unknown
Cured before · departure trail · not reachable · moderate    0.7    2.1     18.2     72  large not paying
credibility · ability unknown
Stopped suddenly · location unknown · reachability           0.7    4.3     28.0    102  large paying
unknown · low credibility · ability unknown
Cured before · departure trail · reachable · low             0.7    2.5     16.0     66  large not paying
credibility · ability unknown
Stopped suddenly · location unknown · reachable · low        0.7    2.8     23.8    105  large not paying
credibility · low ability
Cured before · location unknown · not reachable ·            0.6    3.8     25.0     85  large paying
moderate credibility · ability unknown
Curing now · in country · reachable · high credibility ·     0.6    8.7     19.0     55  large paying
low ability
Stopped suddenly · departure trail · not reachable ·         0.6    1.7     11.2     41  large not paying
moderate credibility · ability unknown
Stopped suddenly · location unknown · not reachable ·        0.5    3.9     15.0     60  small paying
moderate credibility · low ability
Cured before · location unknown · reachable · moderate       0.5    8.3     17.2     73  small paying
credibility · low ability
Cured before · in country · not reachable · moderate         0.5    2.8     16.4     68  small not paying
credibility · ability unknown
Curing now · in country · reachable · moderate               0.5    9.0     13.8     46  small paying
credibility · moderate ability
Stopped suddenly · location unknown · reachable · low        0.5    1.9     13.8     55  small not paying
credibility · ability unknown
Curing now · in country · not reachable · moderate           0.5    6.4     16.2     69  small paying
credibility · low ability
Curing now · location unknown · reachable · moderate         0.5    6.6     17.2     58  small paying
credibility · low ability
Stopped suddenly · location unknown · reachability           0.5    6.8     18.6     72  small paying
unknown · low credibility · low ability
Cured before · in country · not reachable · moderate         0.5    3.8     16.2     63  small paying
credibility · moderate ability
Cured before · departure trail · reachable · moderate        0.5    4.1     12.8     45  small paying
credibility · ability unknown
Never paid · departure trail · reachability unknown · low    0.5    0.1      8.8     31  small not paying
credibility · ability unknown
Cured before · in country · not reachable · low              0.5    5.1     17.4     70  small paying
credibility · moderate ability
Cured before · departure trail · reachability unknown ·      0.5    1.8     15.6     60  small not paying
low credibility · ability unknown
Stopped suddenly · departure trail · reachable · moderate    0.5    2.0      8.4     34  small not paying
credibility · low ability
Cured before · in country · reachable · low credibility ·    0.5    6.0     12.6     48  small paying
moderate ability
Cured before · location unknown · reachable · low            0.4    3.5     14.4     64  small paying
credibility · ability unknown
Cured before · location unknown · reachable · moderate       0.4    6.0     16.0     59  small paying
credibility · ability unknown
Stopped suddenly · in country · not reachable · low          0.4    3.0     13.2     54  small paying
credibility · moderate ability
Cured before · in country · reachable · moderate             0.4    4.5     14.6     55  small paying
credibility · ability unknown
Never paid · in country · not reachable · low credibility    0.4    2.6      6.8     31  small not paying
· low ability
Stopped suddenly · departure trail · not reachable · low     0.4    0.8      9.2     38  small not paying
credibility · moderate ability
Cured before · in country · reachable · moderate             0.4    4.2     14.0     61  small paying
credibility · moderate ability
Curing now · departure trail · reachable · moderate          0.4    8.9     11.8     38  small paying
credibility · low ability
Stopped suddenly · in country · reachable · low              0.3    4.7     10.2     44  small paying
credibility · moderate ability
Cured before · in country · reachable · high credibility     0.3    8.3      8.2     32  small paying
· low ability
Curing now · location unknown · reachable · high             0.3    5.7     13.8     46  small paying
credibility · low ability
Cured before · location unknown · reachability unknown ·     0.3    3.9     13.6     52  small paying
low credibility · low ability
Curing now · location unknown · reachable · moderate         0.3    7.5     15.0     48  small paying
credibility · ability unknown
Curing now · location unknown · reachable · high             0.3   12.9     14.4     37  small paying
credibility · ability unknown
Curing now · location unknown · not reachable · moderate     0.3    4.5      7.4     32  small paying
credibility · low ability
Curing now · location unknown · reachable · moderate         0.3    7.5     10.6     37  small paying
credibility · moderate ability
Stopped suddenly · in country · reachability unknown ·       0.3    5.5      6.4     32  small paying
low credibility · ability unknown
Stopped suddenly · location unknown · reachable ·            0.3    6.6      9.8     34  small paying
moderate credibility · low ability
Cured before · location unknown · reachability unknown ·     0.3    5.2     16.6     62  small paying
low credibility · ability unknown
Curing now · in country · reachable · moderate               0.3    9.2     14.8     42  small paying
credibility · ability unknown
Curing now · in country · not reachable · moderate           0.2    7.4      8.2     31  small paying
credibility · ability unknown
Cured before · in country · reachability unknown · low       0.2    5.8     11.0     45  small paying
credibility · low ability
Cured before · location unknown · not reachable · low        0.2   10.2      8.8     34  small paying
credibility · moderate ability
Curing now · in country · not reachable · high               0.2    7.7      7.0     30  small paying
credibility · low ability
Cured before · location unknown · reachability unknown ·     0.2    8.3     10.2     45  small paying
moderate credibility · low ability
Curing now · in country · reachable · high credibility ·     0.2    9.6      8.6     30  small paying
moderate ability
Cured before · location unknown · not reachable ·            0.1    7.2      8.4     35  small paying
moderate credibility · moderate ability
Cured before · location unknown · reachability unknown ·     0.1    8.1      8.0     30  small paying
moderate credibility · ability unknown
Cured before · location unknown · reachable · moderate       0.1    7.2      7.2     33  small paying
credibility · moderate ability
```

## cc_60_180: credibility x ability grid (pooled Jan-May)


```text
credibility  ability   accounts % accounts             %             %   recovery %   paid %  AED / acct
                                             outstanding     collected
--------------------------------------------------------------------------------------------------------
high         high           100        0.3           0.2           1.0         14.2     67.3     2,253.9
high         moderate       501        1.2           0.9           3.5         12.5     69.1     1,793.9
high         low            443        1.0           0.8           3.0         11.6     64.2     1,951.7
high         unknown        593        1.6           1.2           4.2         11.3     64.9     1,694.8
moderate     high           436        1.0           0.8           3.0         11.7     50.6     1,801.0
moderate     moderate     2,407        5.5           4.7          11.7          7.7     45.7     1,329.8
moderate     low          3,025        6.1           6.8          12.0          5.5     35.0     1,231.5
moderate     unknown      3,823        9.5           9.1          16.1          5.5     35.1     1,067.2
low          high           642        1.5           1.1           2.2          6.3     27.7       971.5
low          moderate     5,275       12.0          10.3          11.4          3.4     18.9       597.5
low          low          8,204       18.0          20.0          14.5          2.3     13.5       505.6
low          unknown     14,723       42.2          44.0          17.5          1.2      7.6       260.4
unknown      high           <10
unknown      moderate       <10
unknown      low            <10
unknown      unknown        <10
```

## cc_60_180: credibility x ability grid (May)


```text
credibility  ability   accounts % accounts             %             %   recovery %   paid %  AED / acct
                                             outstanding     collected
--------------------------------------------------------------------------------------------------------
high         high            46        0.3           0.3           1.2         13.5     65.2     2,550.0
high         moderate       175        1.1           0.7           3.0         12.5     66.3     1,716.8
high         low            154        1.0           0.7           2.9         12.4     62.3     1,922.0
high         unknown        223        1.4           1.1           3.9         11.0     65.5     1,774.1
moderate     high           144        0.9           0.7           2.1          9.2     40.3     1,480.4
moderate     moderate       767        4.8           4.3           9.6          6.9     40.0     1,272.7
moderate     low            997        6.3           7.0          11.7          5.1     32.3     1,187.5
moderate     unknown      1,429        9.0           8.5          13.8          5.0     31.2       979.6
low          high           229        1.4           1.0           2.4          7.1     27.5     1,081.1
low          moderate     1,923       12.1          10.4          10.9          3.2     18.1       575.1
low          low          3,124       19.7          21.6          19.3          2.7     15.3       627.3
low          unknown      6,679       42.0          43.7          19.2          1.3      8.1       292.1
unknown      high           <10
unknown      moderate       <10
unknown      low            <10
unknown      unknown        <10
```

## rl_60_180: credibility x ability grid (pooled Jan-May)


```text
credibility  ability   accounts          %             %             %   recovery %   paid %  AED / acct
                                  accounts   outstanding     collected
--------------------------------------------------------------------------------------------------------
high         high           <10
high         moderate       108        1.5           0.8           2.5          9.2     73.5     5,524.6
high         low            242        3.3           2.5           6.0          7.3     64.6     6,265.4
high         unknown        130        2.0           1.1           3.1          8.8     63.2     5,410.6
moderate     high      suppressed
moderate     moderate       386        4.8           3.2           7.2          6.7     59.1     5,120.5
moderate     low          1,137       15.2          14.5          22.4          4.6     48.4     5,013.0
moderate     unknown        639        9.1           6.8          10.0          4.4     50.2     3,728.9
low          high            44        0.5           0.3           1.1         11.1     60.3     7,122.8
low          moderate       453        5.6           4.8           6.3          3.9     37.3     3,787.8
low          low          2,312       30.5          38.6          26.8          2.1     22.6     2,981.1
low          unknown      1,778       27.0          27.3          13.9          1.5     16.3     1,742.4
unknown      high           <10
unknown      moderate       <10
unknown      low            <10
unknown      unknown        <10
```

## rl_60_180: credibility x ability grid (May)


```text
credibility  ability   accounts          %             %             %   recovery %   paid %  AED / acct
                                  accounts   outstanding     collected
--------------------------------------------------------------------------------------------------------
high         high           <10
high         moderate        29        0.9           0.6           2.2         12.0     86.2     8,594.6
high         low             80        2.6           1.9           4.5          7.7     71.2     6,290.5
high         unknown         46        1.5           0.5           1.5          9.4     65.2     3,635.1
moderate     high           <10
moderate     moderate       150        4.8           3.0           7.3          8.1     60.0     5,510.3
moderate     low            447       14.4          13.8          20.9          5.0     48.3     5,271.2
moderate     unknown        269        8.7           6.9          10.2          4.9     55.4     4,272.5
low          high            21        0.7           0.2           0.7         11.2     66.7     3,532.2
low          moderate       163        5.3           4.2           5.7          4.4     42.3     3,907.6
low          low          1,091       35.2          43.3          30.7          2.3     26.4     3,168.5
low          unknown        788       25.5          25.2          14.9          1.9     23.6     2,134.6
unknown      high           <10
unknown      moderate       <10
unknown      low            <10
unknown      unknown        <10
```

## cc_60_180: High-band personas (pooled, 20+ accounts; 45 personas, largest outstanding first)


```text
persona               accounts  recovery %  recovery 90% CI   paid %  AED / acct  % outstanding (of
                                                                                  pooled book)
---------------------------------------------------------------------------------------------------
Curing now ·               210        16.3  14.22 to 18.58      75.1     2,051.8                 0.3
location unknown ·
reachable · high
credibility ·
ability unknown
Curing now · in            166        14.9  13.34 to 16.65      77.7     2,032.6                 0.2
country · reachable
· high credibility
· moderate ability
Curing now · in            143        13.4  11.36 to 15.6       71.4     2,071.9                 0.2
country · reachable
· high credibility
· low ability
Curing now · in            150        24.5  21.6 to 27.5        78.5     2,830.3                 0.2
country · reachable
· moderate
credibility · high
ability
Curing now · in            141        13.8  12.19 to 15.46      77.5     1,765.9                 0.2
country · reachable
· high credibility
· ability unknown
Curing now ·               164        16.6  14.77 to 18.44      77.5     1,839.6                 0.2
location unknown ·
reachable · high
credibility ·
moderate ability
Cured before · in          123         4.7  3.43 to 6.01        28.0       773.8                 0.2
country · not
reachable · low
credibility · high
ability
Cured before · in          114         8.2  6.24 to 10.76       41.7     1,402.5                 0.2
country · reachable
· low credibility ·
high ability
Stopped suddenly ·          99         5.0  3.2 to 6.87         31.3       905.6                 0.2
in country ·
reachable · low
credibility · high
ability
Curing now · in             71        15.4  11.84 to 18.75      72.3     2,412.0                 0.1
country · reachable
· high credibility
· high ability
Curing now ·               107        16.4  14.02 to 18.58      74.0     1,952.3                 0.1
location unknown ·
reachable · high
credibility · low
ability
Stopped suddenly ·          85         6.4  3.23 to 10.07       23.3     1,077.8                 0.1
in country · not
reachable · low
credibility · high
ability
Cured before · in           80         6.0  3.81 to 8.38        33.7     1,094.9                 0.1
country · reachable
· moderate
credibility · high
ability
Curing now ·                63         9.7  6.97 to 12.37       55.9     1,586.8                 0.1
departure trail ·
reachable · high
credibility ·
ability unknown
Curing now ·                44        10.9  7.03 to 15.2        66.7     2,434.2                 0.1
departure trail ·
reachable · high
credibility · low
ability
Cured before · in           58         6.7  3.57 to 10.66       27.4     1,147.9                 0.1
country · not
reachable ·
moderate
credibility · high
ability
Curing now ·                37        13.8  10.42 to 18.45      70.5     2,215.9                 0.1
departure trail ·
reachable · high
credibility ·
moderate ability
Curing now · in             37        15.6  11.66 to 20.5       67.3     2,684.0                 0.1
country · reachable
· low credibility ·
high ability
Cured before · in           33        11.2  5.3 to 18.09        55.6     2,861.9                 0.1
country · reachable
· high credibility
· low ability
Curing now ·                57         9.7  6.8 to 12.93        51.5     1,318.6                 0.1
location unknown ·
not reachable ·
high credibility ·
ability unknown
Stopped suddenly ·          45         8.6  5.48 to 11.93       44.2     1,485.0                 0.1
in country ·
reachable ·
moderate
credibility · high
ability
Stopped suddenly ·          34         3.6  1.01 to 6.15        18.2       721.0                 0.1
in country · not
reachable ·
moderate
credibility · high
ability
Cured before · in           31         9.4  6.53 to 11.98       60.0     2,384.6                 0.1
country · reachable
· high credibility
· moderate ability
Stopped suddenly ·          25         0.6  0.03 to 2.07         9.7       145.5                 0.1
departure trail ·
not reachable · low
credibility · high
ability
Curing now · in             39         8.9  5.27 to 11.68       47.7     1,632.2                 0.1
country · not
reachable · high
credibility · low
ability
Curing now · in             40        10.2  7.57 to 12.72       57.8     1,543.1                 0.0
country · not
reachable · high
credibility ·
moderate ability
Curing now · in             40        13.2  8.8 to 17.52        60.4     1,816.1                 0.0
country · not
reachable ·
moderate
credibility · high
ability
Curing now ·                28        16.0  9.1 to 24.47        64.9     2,777.0                 0.0
departure trail ·
reachable ·
moderate
credibility · high
ability
Stopped suddenly ·          32        10.5  7.19 to 13.96       70.3     1,761.8                 0.0
in country ·
reachable · high
credibility ·
ability unknown
Curing now ·                34         9.2  5.83 to 13.45       57.8     1,253.0                 0.0
location unknown ·
not reachable ·
high credibility ·
moderate ability
Cured before · in           32        10.8  6.96 to 15.38       59.5     1,793.9                 0.0
country · reachable
· high credibility
· ability unknown
Cured before ·              30        11.9  8.36 to 15.94       78.8     2,092.4                 0.0
location unknown ·
reachable · high
credibility ·
ability unknown
Stopped suddenly ·          32        10.2  7.1 to 13.19        63.2     1,539.7                 0.0
in country ·
reachable · high
credibility · low
ability
Cured before · in           25         3.8  1.98 to 6.25        31.0       726.6                 0.0
country · not
reachable · high
credibility ·
ability unknown
Curing now ·                26         6.8  2.95 to 12.44       48.4     1,154.2                 0.0
departure trail ·
not reachable ·
high credibility ·
ability unknown
Cured before ·              20         1.2  0.42 to 2.3         26.1       263.0                 0.0
location unknown ·
not reachable ·
high credibility ·
ability unknown
Stopped suddenly ·          27        11.2  8.94 to 13.64       83.9     1,782.6                 0.0
in country ·
reachable · high
credibility ·
moderate ability
Cured before · in           36         7.0  3.03 to 12.96       31.2       761.4                 0.0
country ·
reachability
unknown · low
credibility · high
ability
Cured before ·              29         9.3  5.86 to 13.29       50.0     1,362.4                 0.0
location unknown ·
reachable · high
credibility ·
moderate ability
Cured before · in           20         6.2  3.43 to 9.59        38.5     1,045.6                 0.0
country · not
reachable · high
credibility ·
moderate ability
Curing now · in             29         9.1  5.34 to 14.52       45.5     1,206.4                 0.0
country · not
reachable · high
credibility ·
ability unknown
Stopped suddenly ·          41         0.0  0.0 to 0.0           9.7       118.2                 0.0
departure trail ·
reachability
unknown · low
credibility · high
ability
Curing now ·                24        13.1  8.91 to 18.52       63.0     1,445.9                 0.0
location unknown ·
not reachable ·
high credibility ·
low ability
Stopped suddenly ·          79         6.5  2.19 to 12.2        13.8       204.1                 0.0
in country ·
reachability
unknown · low
credibility · high
ability
Cured before ·              20         0.2  0.0 to 0.96          3.0        51.0                 0.0
departure trail ·
reachability
unknown · low
credibility · high
ability
```

## rl_60_180: High-band personas (pooled, 20+ accounts; 9 personas, largest outstanding first)


```text
persona               accounts  recovery %  recovery 90% CI   paid %  AED / acct  % outstanding (of
                                                                                  pooled book)
---------------------------------------------------------------------------------------------------
Curing now · in             55         8.7  7.63 to 9.82        82.1     8,046.1                 0.6
country · reachable
· high credibility
· low ability
Cured before · in           32         8.3  3.65 to 16.34       58.5     9,627.3                 0.3
country · reachable
· high credibility
· low ability
Curing now ·                46         5.7  3.96 to 7.55        65.2     3,671.9                 0.3
location unknown ·
reachable · high
credibility · low
ability
Curing now ·                37        12.9  9.83 to 17.04       87.5     7,778.2                 0.3
location unknown ·
reachable · high
credibility ·
ability unknown
Cured before · in           21         2.7  1.47 to 4.72        50.0     2,987.2                 0.2
country · not
reachable · high
credibility · low
ability
Curing now · in             30         7.7  4.15 to 11.16       62.9     6,042.9                 0.2
country · not
reachable · high
credibility · low
ability
Cured before ·              27         6.4  3.5 to 10.33        56.7     5,719.2                 0.2
location unknown ·
reachable · high
credibility · low
ability
Curing now · in             30         9.6  5.77 to 14.04       83.7     5,773.0                 0.2
country · reachable
· high credibility
· moderate ability
Curing now ·                24        10.7  8.32 to 14.14       76.9     5,466.2                 0.1
location unknown ·
reachable · high
credibility ·
moderate ability
```
