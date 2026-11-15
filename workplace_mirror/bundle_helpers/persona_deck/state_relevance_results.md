# State relevance: which states drive payback, and how many does each case need?

Source: `state_relevance_<model_id>.json/.md`, produced by `state_relevance.py` (PROD run, persona
month Aug 2026, cohorts Jan-May 2026, payments to 2026-08-31), for cc_60_180 and rl_60_180. Out of
time: the main view builds on Jan-Apr pooled and tests on May; the adjacent scheme builds on months
before m and tests m (Feb-May). One estimator for every combination of states: pooled training cell
mean shrunk to the training book mean with weight n/(n+20) (k = 20, fixed), unseen cell = book mean.
Recovery = collected over 3 months / outstanding principal at the cohort month end (cards
`prm_balance.bnp_principal`, loans `int_loan_master.outstanding_balance`). Intervals are bootstrap
90% (200 draws, resampling the May accounts, training estimates held fixed). Cells under 10 accounts
are suppressed. No tier names are used anywhere.

Book (May test cohort): cards 15,890 accounts, recovery 3.05%, paid 18.6%; loans 3,096 accounts,
recovery 3.28%, paid 36.6%. Tree rules fixed in advance: split = largest money-weighted error
reduction on the training months, kept only if each child has at least 300 (cards) / 150 (loans)
training accounts, the children's recovery differs by at least 25% of the parent's, and on May the
children keep the order with a gap of at least half the training gap. Persona names in section D use
the value-map wording: 'departure trail' = Skip location, 'location unknown' = Unknown.

## Findings

### Cards (cc_60_180)

1. **Ranking.** Shapley value for AUC of paid: Deterioration 0.082 (90% 0.077-0.087), Reachability
   0.076 (0.072-0.081), Credibility 0.061 (0.057-0.065), Location 0.045 (0.041-0.048), Ability 0.031
   (0.028-0.034). For money in the top 20%: Reachability 10.2 pp (8.5-12.1), Deterioration 8.0
   (6.7-9.0), Credibility 6.4 (5.2-7.7), Location 2.9 (1.8-3.9), Ability 1.5 (0.8-2.1).
   Deterioration and Reachability lead and are not separable; Location and Ability come last on
   both. Within locatability, reachability does the work: alone AUC 0.687 vs 0.633, and dropping it
   costs 0.022 AUC and 5.1 pp of money against 0.006 and -0.2 pp for location.

2. **Overlap.** Every pair is negative on every metric, so the states share information. Largest:
   Deterioration + Credibility (AUC -0.144, top-20% money -16.4 pp), Deterioration + Reachability
   (-0.129, -15.5), Reachability + Credibility (-0.114, -14.8); smallest are the pairs with Ability
   (Credibility + Ability -0.054, Reachability + Ability -0.061). Deterioration and credibility
   largely carry the same payment history.

3. **What the full persona adds.** AUC 0.795 against 0.768 for the best pair (Deterioration +
   Reachability) and 0.787 for the best triple (Deterioration + Location + Reachability): +0.027 and
   +0.008. Top-20% money: 48.9% against 48.4% (pair) and 50.8% (triple), so nothing, and the best
   triple is higher. Dropping Ability alone (four states) gives AUC 0.795 and 50.6% of money, no
   loss. Best subsets are picked on May and flatter the small sets.

4. **Share decided by few states (tree B, recovery, May).** One state: no leaf. Two states: 9.7% of
   accounts, 6.9% of outstanding, 27.2% of money. Three: 27.2%, 27.0%, 36.1%. Four or more: 63.0%,
   66.1%, 36.6% (August accounts: 6.6%, 25.3%, 68.1%).

5. **Money vs states needed.** No. Leaves needing 4+ states hold 63% of accounts but 37% of money.
   The largest leaf (Never paid / Stopped suddenly, Non-Reachable or Unknown, Skip or Unknown
   location, Low credibility) is 36.9% of accounts, 8.1% of money, recovery 0.64%. Money sits in the
   2- and 3-state groups where Curing now and reachability decide. The state count of the large low-
   recovery leaves is a lower bound: their best split failed a rule (size or out-of-time) while 2-5
   other splits would have passed.

6. **Examples.** (a) Largest leaf with at most 2 states: Curing now, Reachable or Unknown: 1,163
   accounts (7.3%), 22.7% of money, recovery 13.7% in May; yet its 28 personas with 30+ accounts
   range 8.5-24.5% (SD 3.1 pp), and no further split could meet the rules. (b) Most money with 4+
   states: the large leaf above: needs four states to describe, but its 23 personas all collect
   0.0-1.9% (SD 0.4 pp), so the extra states change little.

7. **Action-gated tree.** Same story. 15 leaves, identical 1/2/3/4+ summary (9.7%, 27.2%, 63.0% of
   accounts) and May error 0.07% better than tree B. Inside Reachable, credibility separates
   High/Moderate from Low (7.0% vs 3.6% recovery, a leaf with 15.1% of money) and ability is used in
   two sub-branches; inside Non-Reachable, credibility appears only for Never paid / Stopped
   suddenly with Skip or Unknown location (where the High/Moderate side holds 2.0% of money) and
   ability once. So both matter more for money in the reachable branch.

8. **Stability.** Shapley ranks by AUC are identical in all four folds (Deterioration, Reachability,
   Credibility, Location, Ability); for top-20% money Deterioration is first in Feb-Apr and
   Reachability in May; Ability is last in every fold. The tree's first split is Deterioration in
   every fold (Curing now vs the rest in May) but its size is not stable: 11, 14, 20, 15 leaves;
   share of accounts in 4-state leaves 14-58%; money in 2-state leaves 3-39%.

### Loans (rl_60_180)

1. **Ranking.** Shapley value for AUC of paid: Credibility 0.058 (90% 0.049-0.066), Deterioration
   0.049 (0.041-0.060), Location 0.049 (0.040-0.056), Reachability 0.048 (0.038-0.057), Ability
   0.018 (0.011-0.025). Top-20% money: Deterioration 4.8 pp (3.3-6.3), Reachability 3.9 (1.7-6.0),
   Credibility 3.1 (1.9-4.4), Location 1.5 (0.1-2.5), Ability 0.9 (-0.5-2.1). The top four are not
   separable on AUC; Ability is clearly last and its money interval includes zero. Locatability: on
   AUC location equals reachability (alone 0.616 vs 0.614); for money reachability is ahead (3.9 vs
   1.5 pp; drop loss 2.4 vs 0.6) but the intervals overlap, so no clear winner.

2. **Overlap.** Negative for every pair on AUC. Largest: Deterioration + Credibility (AUC -0.106,
   top-20% money -7.5 pp), Location + Credibility (-0.070), Reachability + Credibility (-0.067).
   Smallest: the pairs with Ability (Credibility + Ability and Location + Ability -0.029). Only one
   cell is not negative (Location + Reachability on top-10% money, +0.6 pp), probably noise.

3. **What the full persona adds.** AUC 0.721 against 0.691 for the best pair (Reachability +
   Credibility) and 0.715 for the best triple (Deterioration + Location + Reachability): +0.030 and
   +0.006. Top-20% money 34.1% against 34.4% (pair) and 33.8% (triple): nothing. Without Ability,
   four states give AUC 0.724 and 35.5% of money, both above the full persona.

4. **Share decided by few states (tree B, recovery, May).** One state (Curing now): 10.6% of
   accounts, 7.4% of outstanding, 17.5% of money. Two states: no leaf. Three: 59.8%, 56.6%, 66.0%.
   Four or more: 29.6%, 36.0%, 16.5% (August accounts: 10.3%, 55.2%, 34.5%). The tree's May error is
   only 0.22% below the no-split root.

5. **Money vs states needed.** No. The 4-state leaves hold 29.6% of accounts but 16.5% of money; the
   biggest (Skip location, Low credibility, Non-Reachable or Unknown) has 24.8% of accounts, 11.3%
   of money, recovery 1.3%. Three-state leaves carry 66% of money. State counts are lower bounds: 6
   of 8 leaves stopped on the 150-account rule, and for 5 of them 3-4 other splits would have
   passed.

6. **Examples.** (a) Largest leaf with at most 2 states: Curing now alone (1 state): 328 accounts
   (10.6%), 17.5% of money, recovery 7.8% in May; its 15 personas with 30+ accounts range 4.5-12.9%
   (SD 1.75 pp), but cells are 30-100 accounts, so much of that is noise and no split met the rules.
   (b) Most money with 4+ states: Skip, Low credibility, Non-Reachable or Unknown: 769 accounts,
   11.3% of money; its 12 personas range 0.04-2.2% (SD 0.45 pp).

7. **Action-gated tree.** Same fit (12 leaves, May error 0.25% below root, 0.03% better than B) but
   a different story on where states act. Inside Reachable only deterioration splits (Curing now /
   Cured before / Never paid or Stopped suddenly); credibility and ability enter only in the Non-
   Reachable branch (credibility under Skip and under Cured before; ability under Cured before).
   That is the opposite of 'ability matters if we can reach them', on thin cells. Summary: 2 states
   35.1% of accounts / 49.3% of money; 3: 22.1% / 22.1%; 4: 31.3% / 17.6%; 5: 11.4% / 10.9%.

8. **Stability.** Loans are less stable. AUC ranks by fold: Deterioration 1, 1, 1, 2; Credibility 2,
   2, 2, 1; Location 3, 3, 4, 3; Reachability 4, 4, 3, 4; Ability 5 in all four. Money ranks move
   more (Reachability 5, 5, 3, 2 on top-10%). The tree always splits first on Deterioration but has
   3, 5, 6, 8 leaves, gains 0.2-4.9% over root, and puts 0-86% of accounts in 3-state leaves. Only
   the first split and Ability being last are stable.

## Tables

Order-free contribution (A), main scheme, 5 states (family version of deterioration).

### A. Cards (cc_60_180): alone, drop-one and Shapley

Alone = metric with that state only. Other four = all five minus that state; Drop loss = all five
minus that. Shapley = average gain from adding the state over all orders; the five add up to all
five minus the empty set (check error under 1e-14). Share = Shapley as % of the total gain.

AUC for paid: empty set 0.500, all five 0.795

```text
State          Alone  Other four  Drop loss  Shapley  Share %    90% interval
-------------  -----  ----------  ---------  -------  -------  --------------
Deterioration  0.711       0.780      0.015    0.082     27.7  0.077 to 0.087
Reachability   0.687       0.773      0.022    0.076     25.8  0.072 to 0.081
Credibility    0.673       0.790      0.006    0.061     20.7  0.057 to 0.065
Location       0.633       0.789      0.006    0.045     15.2  0.041 to 0.048
Ability        0.601       0.795      0.001    0.031     10.6  0.028 to 0.034
```

Money in top 20% of accounts (%): empty set 20.00, all five 48.91

```text
State          Alone  Other four  Drop loss  Shapley  Share %   90% interval
-------------  -----  ----------  ---------  -------  -------  -------------
Reachability   42.46       43.77       5.14    10.15     35.1  8.49 to 12.07
Deterioration  41.48       48.80       0.11     7.99     27.6   6.66 to 9.00
Credibility    39.68       49.51      -0.60     6.36     22.0   5.17 to 7.69
Location       31.60       49.15      -0.24     2.93     10.1   1.76 to 3.90
Ability        28.31       50.64      -1.73     1.48      5.1   0.81 to 2.13
```

Money in top 10% of accounts (%): empty set 10.00, all five 30.01

```text
State          Alone  Other four  Drop loss  Shapley  Share %  90% interval
-------------  -----  ----------  ---------  -------  -------  ------------
Deterioration  28.17       29.91       0.09     7.18     35.9           n/a
Reachability   21.23       27.92       2.09     5.10     25.5           n/a
Credibility    21.98       28.82       1.19     4.93     24.6           n/a
Location       15.80       30.04      -0.03     1.51      7.5           n/a
Ability        15.29       29.67       0.34     1.29      6.5           n/a
```

Spearman vs collected per account: empty set 0.000, all five 0.395

```text
State          Alone  Other four  Drop loss  Shapley  Share %  90% interval
-------------  -----  ----------  ---------  -------  -------  ------------
Reachability   0.299       0.367      0.029    0.107     27.0           n/a
Deterioration  0.310       0.379      0.016    0.103     26.1           n/a
Credibility    0.309       0.390      0.006    0.094     23.8           n/a
Location       0.198       0.387      0.009    0.055     14.0           n/a
Ability        0.154       0.396     -0.001    0.036      9.2           n/a
```

A. Cards (cc_60_180): Shapley in the adjacent scheme (mean, min to max over the four folds; rank 1 =
largest)

AUC for paid, Feb-May folds (all five: 0.820, 0.795 to 0.835)

```text
State          Shapley mean (min to max)  Rank by fold
-------------  -------------------------  ------------
Deterioration     0.093 (0.082 to 0.098)       1 1 1 1
Location          0.045 (0.042 to 0.048)       4 4 4 4
Reachability      0.080 (0.076 to 0.087)       2 2 2 2
Credibility       0.069 (0.061 to 0.075)       3 3 3 3
Ability           0.033 (0.031 to 0.035)       5 5 5 5
```

Money in top 20% of accounts (%), Feb-May folds (all five: 53.14, 48.91 to 55.47)

```text
State          Shapley mean (min to max)  Rank by fold
-------------  -------------------------  ------------
Deterioration      10.26 (7.99 to 11.82)       1 1 1 2
Location             3.10 (2.30 to 3.75)       4 4 4 4
Reachability       10.05 (9.33 to 11.10)       2 2 2 1
Credibility          7.78 (6.36 to 8.44)       3 3 3 3
Ability              1.95 (1.48 to 2.28)       5 5 5 5
```

A. Cards (cc_60_180): Shapley under the raw (unshrunk) estimator and with the 6 deterioration states

```text
State                    AUC main  Top20 main  AUC raw  Top20 raw
-----------------------  --------  ----------  -------  ---------
Deterioration               0.082        7.99    0.082       8.34
Location                    0.045        2.93    0.045       3.11
Reachability                0.076       10.15    0.076      10.33
Credibility                 0.061        6.36    0.061       6.62
Ability                     0.031        1.48    0.031       1.86
Deterioration, 6 states     0.082        7.84
```

A. Cards (cc_60_180): pairwise overlap (gain of the pair minus the two alone; negative = shared
information)

```text
Pair                             AUC  Top10 pp  Top20 pp  Spearman
----------------------------  ------  --------  --------  --------
deterioration + location      -0.092     -5.97     -9.68    -0.165
deterioration + reachability  -0.129    -10.64    -15.52    -0.238
deterioration + credibility   -0.144    -12.24    -16.35    -0.282
deterioration + ability       -0.076     -5.24     -4.69    -0.146
location + reachability       -0.088     -2.77    -10.79    -0.171
location + credibility        -0.078     -4.15    -10.52    -0.187
location + ability            -0.078     -3.45     -6.70    -0.129
reachability + credibility    -0.114     -3.86    -14.83    -0.246
reachability + ability        -0.061     -3.80     -7.13    -0.134
credibility + ability         -0.054     -3.67     -7.18    -0.153
```

A. Cards (cc_60_180): full persona against the best two- and three-state combination (best picked on
the test metric, which favours the small sets)

```text
Metric         n                         Best combination   Best  All five   Gain
-------------  -  ---------------------------------------  -----  --------  -----
AUC            2             Deterioration + Reachability  0.768     0.795  0.027
AUC            3  Deterioration + Location + Reachability  0.787     0.795  0.008
Top-10% money  2               Reachability + Credibility  29.35     30.01   0.66
Top-10% money  3    Location + Reachability + Credibility  30.53     30.01  -0.52
Top-20% money  2             Deterioration + Reachability  48.42     48.91   0.49
Top-20% money  3  Deterioration + Location + Reachability  50.79     48.91  -1.88
Spearman       2             Deterioration + Reachability  0.371     0.395  0.024
Spearman       3  Deterioration + Location + Reachability  0.387     0.395  0.008
```

### A. Loans (rl_60_180): alone, drop-one and Shapley

Alone = metric with that state only. Other four = all five minus that state; Drop loss = all five
minus that. Shapley = average gain from adding the state over all orders; the five add up to all
five minus the empty set (check error under 1e-14). Share = Shapley as % of the total gain.

AUC for paid: empty set 0.500, all five 0.721

```text
State          Alone  Other four  Drop loss  Shapley  Share %    90% interval
-------------  -----  ----------  ---------  -------  -------  --------------
Credibility    0.644       0.714      0.007    0.058     26.0  0.049 to 0.066
Deterioration  0.633       0.717      0.005    0.049     22.3  0.041 to 0.060
Location       0.616       0.714      0.007    0.049     21.9  0.040 to 0.056
Reachability   0.614       0.708      0.013    0.048     21.5  0.038 to 0.057
Ability        0.555       0.724     -0.003    0.018      8.2  0.011 to 0.025
```

Money in top 20% of accounts (%): empty set 20.00, all five 34.06

```text
State          Alone  Other four  Drop loss  Shapley  Share %   90% interval
-------------  -----  ----------  ---------  -------  -------  -------------
Deterioration  28.72       30.86       3.20     4.77     33.9   3.26 to 6.28
Reachability   27.94       31.71       2.35     3.86     27.4   1.72 to 6.01
Credibility    29.21       33.78       0.29     3.09     22.0   1.90 to 4.40
Location       24.58       33.50       0.56     1.48     10.5   0.08 to 2.47
Ability        25.75       35.50      -1.44     0.87      6.2  -0.45 to 2.10
```

Money in top 10% of accounts (%): empty set 10.00, all five 16.55

```text
State          Alone  Other four  Drop loss  Shapley  Share %  90% interval
-------------  -----  ----------  ---------  -------  -------  ------------
Deterioration  16.55       16.47       0.08     2.67     40.7           n/a
Reachability   13.97       16.65      -0.11     1.55     23.7           n/a
Credibility    15.11       17.02      -0.47     1.29     19.8           n/a
Ability        14.38       17.70      -1.15     0.57      8.7           n/a
Location       12.29       16.78      -0.23     0.47      7.2           n/a
```

Spearman vs collected per account: empty set 0.000, all five 0.329

```text
State          Alone  Other four  Drop loss  Shapley  Share %  90% interval
-------------  -----  ----------  ---------  -------  -------  ------------
Credibility    0.294       0.324      0.005    0.097     29.4           n/a
Deterioration  0.250       0.289      0.040    0.090     27.3           n/a
Location       0.218       0.321      0.007    0.071     21.6           n/a
Reachability   0.199       0.322      0.007    0.060     18.2           n/a
Ability        0.114       0.361     -0.033    0.011      3.4           n/a
```

A. Loans (rl_60_180): Shapley in the adjacent scheme (mean, min to max over the four folds; rank 1 =
largest)

AUC for paid, Feb-May folds (all five: 0.752, 0.721 to 0.769)

```text
State          Shapley mean (min to max)  Rank by fold
-------------  -------------------------  ------------
Deterioration     0.075 (0.049 to 0.090)       1 1 1 2
Location          0.047 (0.046 to 0.049)       3 3 4 3
Reachability      0.045 (0.041 to 0.051)       4 4 3 4
Credibility       0.062 (0.057 to 0.068)       2 2 2 1
Ability           0.022 (0.018 to 0.024)       5 5 5 5
```

Money in top 20% of accounts (%), Feb-May folds (all five: 34.72, 32.73 to 36.30)

```text
State          Shapley mean (min to max)  Rank by fold
-------------  -------------------------  ------------
Deterioration        6.10 (4.77 to 7.86)       1 1 1 1
Location             0.86 (0.41 to 1.48)       4 5 5 4
Reachability         3.56 (1.81 to 5.17)       3 2 2 2
Credibility          2.49 (2.20 to 3.09)       2 3 4 3
Ability              1.70 (0.87 to 3.21)       5 4 3 5
```

A. Loans (rl_60_180): Shapley under the raw (unshrunk) estimator and with the 6 deterioration states

```text
State                    AUC main  Top20 main  AUC raw  Top20 raw
-----------------------  --------  ----------  -------  ---------
Deterioration               0.049        4.77    0.047       4.69
Location                    0.049        1.48    0.049       1.40
Reachability                0.048        3.86    0.048       3.96
Credibility                 0.058        3.09    0.059       2.86
Ability                     0.018        0.87    0.018       1.06
Deterioration, 6 states     0.052        5.57
```

A. Loans (rl_60_180): pairwise overlap (gain of the pair minus the two alone; negative = shared
information)

```text
Pair                             AUC  Top10 pp  Top20 pp  Spearman
----------------------------  ------  --------  --------  --------
deterioration + location      -0.059     -2.19     -3.07    -0.169
deterioration + reachability  -0.069     -3.84     -2.21    -0.152
deterioration + credibility   -0.106     -5.18     -7.50    -0.257
deterioration + ability       -0.036     -4.00     -3.59    -0.111
location + reachability       -0.055      0.62     -3.68    -0.142
location + credibility        -0.070     -2.28     -3.99    -0.181
location + ability            -0.029     -3.39     -4.22    -0.098
reachability + credibility    -0.067     -2.31     -6.26    -0.186
reachability + ability        -0.033     -4.79     -4.86    -0.100
credibility + ability         -0.029     -4.95     -5.93    -0.128
```

A. Loans (rl_60_180): full persona against the best two- and three-state combination (best picked on
the test metric, which favours the small sets)

```text
Metric         n                         Best combination   Best  All five    Gain
-------------  -  ---------------------------------------  -----  --------  ------
AUC            2               Reachability + Credibility  0.691     0.721   0.030
AUC            3  Deterioration + Location + Reachability  0.715     0.721   0.006
Top-10% money  2                  Deterioration + Ability  16.93     16.55   -0.38
Top-10% money  3   Deterioration + Reachability + Ability  18.98     16.55   -2.43
Top-20% money  2             Deterioration + Reachability  34.45     34.06   -0.38
Top-20% money  3  Deterioration + Location + Reachability  33.78     34.06    0.29
Spearman       2                   Location + Credibility  0.331     0.329  -0.003
Spearman       3   Deterioration + Location + Credibility  0.344     0.329  -0.016
```

## B. Decision tree on recovery (free), leaves = decision groups

St = distinct states used on the path. %acc, %out, %money = share of May accounts, outstanding
principal and money collected; Aug% = share of August accounts; Rec/Paid tr = Jan-Apr pooled, te =
May; AED/acct is May. SD pp and Persona min-max = account-weighted SD and range of recovery over the
personas with at least 30 accounts inside the leaf (Jan-May pooled); Pers>=30 = personas listed /
personas in the leaf.

### B1. Cards (cc_60_180): 15 leaves, May error 7.87% below the no-split root (optimistic: May also
decides the keep rule)

L1: Deterioration: Curing now · Reachability: Reachable or Unknown
L2: Deterioration: Curing now · Reachability: Non-Reachable
L3: Deterioration: Cured before or Never paid or Stopped suddenly or Deterioration unknown ·
    Reachability: Reachable · Credibility: High or Moderate
L4: Deterioration: Cured before or Deterioration unknown · Reachability: Reachable · Credibility:
    Low · Ability: High or Moderate
L5: Deterioration: Cured before or Deterioration unknown · Reachability: Reachable · Credibility:
    Low · Ability: Low or Unknown
L6: Deterioration: Never paid or Stopped suddenly · Reachability: Reachable · Credibility: Low ·
    Location: In Country
L7: Deterioration: Never paid or Stopped suddenly · Reachability: Reachable · Credibility: Low ·
    Location: Skip or Unknown · Ability: High or Low or Moderate
L8: Deterioration: Never paid or Stopped suddenly · Reachability: Reachable · Credibility: Low ·
    Location: Skip or Unknown · Ability: Unknown
L9: Deterioration: Cured before or Deterioration unknown · Reachability: Non-Reachable or Unknown ·
    Location: In Country
L10: Deterioration: Cured before or Deterioration unknown · Reachability: Non-Reachable or Unknown ·
    Location: Skip or Unknown
L11: Deterioration: Never paid or Stopped suddenly · Reachability: Unknown · Location: In Country
L12: Deterioration: Never paid or Stopped suddenly · Reachability: Non-Reachable · Location: In
    Country · Ability: High or Low or Moderate
L13: Deterioration: Never paid or Stopped suddenly · Reachability: Non-Reachable · Location: In
    Country · Ability: Unknown
L14: Deterioration: Never paid or Stopped suddenly · Reachability: Non-Reachable or Unknown ·
    Location: Skip or Unknown · Credibility: High or Moderate
L15: Deterioration: Never paid or Stopped suddenly · Reachability: Non-Reachable or Unknown ·
    Location: Skip or Unknown · Credibility: Low

```text
Leaf  St  May accts  %acc  Aug%  %out  %money  Rec tr  Rec te  Paid tr  Paid te  AED/acct
----  --  ---------  ----  ----  ----  ------  ------  ------  -------  -------  --------
L1     2      1,163   7.3   4.8   5.1    22.7   14.77   13.71     72.0     66.5     1,984
L2     2        381   2.4   1.8   1.8     4.5    8.25    7.47     48.3     41.5     1,196
L3     3        909   5.7   4.9   6.6    15.1    7.00    7.03     44.3     42.6     1,686
L4     4        221   1.4   1.0   1.2     2.5    6.36    6.32     39.0     30.8     1,145
L5     4        538   3.4   2.6   3.7     5.7    4.33    4.65     28.5     29.9     1,074
L6     4        570   3.6   2.7   4.1     5.7    3.88    4.25     24.7     29.6     1,009
L7     5        399   2.5   2.1   2.9     3.2    3.21    3.44     20.1     18.8       826
L8     5        453   2.9   3.1   3.3     1.9    1.65    1.82     13.0     14.3       436
L9     3      1,075   6.8   5.5   6.5     7.8    3.27    3.67     21.0     20.6       734
L10    3      2,142  13.5  13.8  12.9    11.7    2.18    2.76     12.6     14.1       555
L11    3        202   1.3   1.1   1.0     1.5    3.50    4.62     14.8     20.3       762
L12    4        932   5.9   4.7   6.0     5.5    2.20    2.83     13.3     15.9       604
L13    4        548   3.5   3.3   3.6     2.0    1.55    1.73      9.8     10.2       373
L14    4        494   3.1   3.9   3.1     2.0    1.62    1.91     12.8     13.2       405
L15    4      5,863  36.9  44.6  38.3     8.1    0.59    0.64      3.7      4.4       140
```

Spread of recovery over the personas inside each leaf (30+ accounts):

```text
Leaf  SD pp  Persona min-max %  Personas 30+/all
----  -----  -----------------  ----------------
L1     3.09           8.5-24.5             28/66
L2     2.57           3.5-13.2             21/34
L3     1.38           4.5-11.9             26/60
L4     0.73            5.9-8.2               4/9
L5     0.99            2.7-5.2              6/12
L6     0.67            0.7-5.0               7/8
L7     0.69            0.8-4.3              7/11
L8     0.49            0.7-2.3               4/4
L9     1.10            2.2-7.0             14/38
L10    1.06            1.5-9.0             21/65
L11    1.14            1.6-6.5              6/14
L12    0.77            1.2-6.4              8/13
L13    0.34            0.4-1.9               3/4
L14    0.62            1.0-3.1              9/29
L15    0.41            0.0-1.9             23/32
```

Why each leaf stopped:

```text
Leaf                                        Why it stopped  Other splits passing
----  ----------------------------------------------------  --------------------
L1                   a child has too few training accounts                     0
L2                   a child has too few training accounts                     0
L3                children's gap under 25% of the parent's                     0
L4                   a child has too few training accounts                     0
L5                   a child has too few training accounts                     1
L6    out of time: children change order on the test month                     0
L7    out of time: children change order on the test month                     0
L8                   a child has too few training accounts                     0
L9       out of time: test gap under half the training gap                     1
L10                  a child has too few training accounts                     2
L11                  a child has too few training accounts                     0
L12   out of time: children change order on the test month                     0
L13                  a child has too few training accounts                     0
L14                  a child has too few training accounts                     3
L15      out of time: test gap under half the training gap                     5
```

B1. Cards (cc_60_180): share of May accounts, outstanding and money in leaves using 1, 2, 3 and 4+
states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
1            0      0.0       0.0      0.0          0.0
2            2      9.7       6.9     27.2          6.6
3            4     27.2      27.0     36.1         25.3
4+           9     63.0      66.1     36.6         68.1
```

B2. Cards (cc_60_180): same on collected per account (sensitivity), by exact number of states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
2            1      7.2       5.1     23.3          4.5
3            6     33.3      32.7     46.7         30.0
4            5     54.2      56.0     24.8         60.3
5            2      5.4       6.2      5.2          5.2
```

B3. Cards (cc_60_180): tree B regrown on each adjacent fold (build < m, test m)

```text
Test month  Leaves  First split  Gain vs root %
----------  ------  -----------  --------------
2026-02         11       family           14.77
2026-03         14       family            2.31
2026-04         20       family            2.11
2026-05         15       family            7.87
```

Share of the test month's accounts, outstanding and money in leaves using k states, mean (min to
max) over the folds (rows with no leaf in any fold omitted):

```text
States used           % accounts        % outstanding              % money
-----------  -------------------  -------------------  -------------------
2              8.6 (1.9 to 11.8)     6.3 (1.5 to 8.7)   25.9 (3.3 to 38.5)
3            44.2 (27.2 to 84.0)  44.0 (27.0 to 82.1)  48.2 (36.1 to 78.2)
4            36.6 (14.1 to 57.7)  39.2 (16.4 to 60.0)  21.0 (12.5 to 31.5)
5             10.5 (0.0 to 36.7)   10.4 (0.0 to 35.6)    4.9 (0.0 to 14.3)
```

### B1. Loans (rl_60_180): 8 leaves, May error 0.22% below the no-split root (optimistic: May also
decides the keep rule)

L1: Deterioration: Curing now
L2: Deterioration: Cured before · Location: In Country or Unknown · Reachability: Unknown
L3: Deterioration: Cured before · Location: In Country or Unknown · Reachability: Non-Reachable or
    Reachable
L4: Deterioration: Never paid or Stopped suddenly · Location: In Country or Unknown · Reachability:
    Reachable or Unknown
L5: Deterioration: Never paid or Stopped suddenly · Location: In Country or Unknown · Reachability:
    Non-Reachable
L6: Deterioration: Cured before or Never paid or Stopped suddenly · Location: Skip · Credibility:
    High or Moderate
L7: Deterioration: Cured before or Never paid or Stopped suddenly · Location: Skip · Credibility:
    Low · Reachability: Reachable
L8: Deterioration: Cured before or Never paid or Stopped suddenly · Location: Skip · Credibility:
    Low · Reachability: Non-Reachable or Unknown

```text
Leaf  St  May accts  %acc  Aug%  %out  %money  Rec tr  Rec te  Paid tr  Paid te  AED/acct
----  --  ---------  ----  ----  ----  ------  ------  ------  -------  -------  --------
L1     1        328  10.6  10.3   7.4    17.5    8.15    7.78     72.6     74.1     6,020
L2     3        114   3.7   2.9   1.5     4.3    6.63    9.49     49.1     51.8     4,284
L3     3        684  22.1  18.3  19.5    28.5    4.09    4.80     38.4     44.4     4,690
L4     3        457  14.8  11.3  12.9    14.3    3.19    3.63     34.6     44.0     3,517
L5     3        412  13.3  15.2  16.0    12.4    1.43    2.54     18.9     29.9     3,390
L6     3        185   6.0   7.5   6.7     6.5    2.71    3.19     31.6     30.8     3,954
L7     4        147   4.8   5.0   7.1     5.1    1.96    2.36     18.3     27.2     3,931
L8     4        769  24.8  29.4  28.9    11.3    0.91    1.29      8.6     13.8     1,661
```

Spread of recovery over the personas inside each leaf (30+ accounts):

```text
Leaf  SD pp  Persona min-max %  Personas 30+/all
----  -----  -----------------  ----------------
L1     1.75           4.5-12.9             15/85
L2     1.65            3.9-8.3              5/20
L3     1.68           1.8-10.2             24/42
L4     1.53            1.9-6.8             11/47
L5     0.86            0.7-3.9             10/27
L6     1.21            1.7-5.0              7/31
L7     1.06            1.0-3.9              4/10
L8     0.45            0.0-2.2             12/22
```

Why each leaf stopped:

```text
Leaf                            Why it stopped  Other splits passing
----  ----------------------------------------  --------------------
L1    children's gap under 25% of the parent's                     0
L2       a child has too few training accounts                     0
L3       a child has too few training accounts                     3
L4       a child has too few training accounts                     3
L5       a child has too few training accounts                     4
L6       a child has too few training accounts                     1
L7       a child has too few training accounts                     3
L8       a child has too few training accounts                     4
```

B1. Loans (rl_60_180): share of May accounts, outstanding and money in leaves using 1, 2, 3 and 4+
states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
1            1     10.6       7.4     17.5         10.3
2            0      0.0       0.0      0.0          0.0
3            5     59.8      56.6     66.0         55.2
4+           2     29.6      36.0     16.5         34.5
```

B2. Loans (rl_60_180): same on collected per account (sensitivity), by exact number of states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
1            1     10.6       7.4     17.5         10.3
2            1     24.5      26.8     31.7         20.4
3            1     35.9      32.8     36.0         34.6
4            2     29.0      33.1     14.7         34.7
```

B3. Loans (rl_60_180): tree B regrown on each adjacent fold (build < m, test m)

```text
Test month  Leaves  First split  Gain vs root %
----------  ------  -----------  --------------
2026-02          3       family            0.73
2026-03          5       family            0.63
2026-04          6       family            4.93
2026-05          8       family            0.22
```

Share of the test month's accounts, outstanding and money in leaves using k states, mean (min to
max) over the folds (rows with no leaf in any fold omitted):

```text
States used           % accounts       % outstanding              % money
-----------  -------------------  ------------------  -------------------
1            13.7 (10.6 to 15.1)   9.4 (7.4 to 10.4)  26.1 (17.5 to 33.2)
2             21.2 (0.0 to 84.9)  22.4 (0.0 to 89.6)   16.7 (0.0 to 66.8)
3             57.7 (0.0 to 85.6)  59.1 (0.0 to 90.2)   53.0 (0.0 to 76.8)
4              7.4 (0.0 to 29.6)   9.0 (0.0 to 36.0)    4.1 (0.0 to 16.5)
```

## C. Action-gated tree (first split forced on reachability: Reachable vs the rest)

### C1. Cards (cc_60_180): 15 leaves, May error 7.94% below the no-split root; forced first split
changes the May error by -0.07% against tree B (negative = the gated tree fits slightly better)

L1: Reachability: Reachable · Deterioration: Curing now
L2: Reachability: Reachable · Deterioration: Cured before or Never paid or Stopped suddenly or
    Deterioration unknown · Credibility: High or Moderate
L3: Reachability: Reachable · Deterioration: Cured before or Deterioration unknown · Credibility:
    Low · Ability: High or Moderate
L4: Reachability: Reachable · Deterioration: Cured before or Deterioration unknown · Credibility:
    Low · Ability: Low or Unknown
L5: Reachability: Reachable · Deterioration: Never paid or Stopped suddenly · Credibility: Low ·
    Location: In Country
L6: Reachability: Reachable · Deterioration: Never paid or Stopped suddenly · Credibility: Low ·
    Location: Skip or Unknown · Ability: High or Low or Moderate
L7: Reachability: Reachable · Deterioration: Never paid or Stopped suddenly · Credibility: Low ·
    Location: Skip or Unknown · Ability: Unknown
L8: Reachability: Non-Reachable or Unknown · Deterioration: Curing now
L9: Reachability: Non-Reachable or Unknown · Deterioration: Cured before or Deterioration unknown ·
    Location: In Country
L10: Reachability: Non-Reachable or Unknown · Deterioration: Cured before or Deterioration unknown ·
    Location: Skip or Unknown
L11: Reachability: Unknown · Deterioration: Never paid or Stopped suddenly · Location: In Country
L12: Reachability: Non-Reachable · Deterioration: Never paid or Stopped suddenly · Location: In
    Country · Ability: High or Low or Moderate
L13: Reachability: Non-Reachable · Deterioration: Never paid or Stopped suddenly · Location: In
    Country · Ability: Unknown
L14: Reachability: Non-Reachable or Unknown · Deterioration: Never paid or Stopped suddenly ·
    Location: Skip or Unknown · Credibility: High or Moderate
L15: Reachability: Non-Reachable or Unknown · Deterioration: Never paid or Stopped suddenly ·
    Location: Skip or Unknown · Credibility: Low

```text
Leaf  St  May accts  %acc  Aug%  %out  %money  Rec tr  Rec te  Paid tr  Paid te  AED/acct
----  --  ---------  ----  ----  ----  ------  ------  ------  -------  -------  --------
L1     2      1,117   7.0   4.5   4.8    22.1   14.91   14.02     72.6     66.7     2,004
L2     3        909   5.7   4.9   6.6    15.1    7.00    7.03     44.3     42.6     1,686
L3     4        221   1.4   1.0   1.2     2.5    6.36    6.32     39.0     30.8     1,145
L4     4        538   3.4   2.6   3.7     5.7    4.33    4.65     28.5     29.9     1,074
L5     4        570   3.6   2.7   4.1     5.7    3.88    4.25     24.7     29.6     1,009
L6     5        399   2.5   2.1   2.9     3.2    3.21    3.44     20.1     18.8       826
L7     5        453   2.9   3.1   3.3     1.9    1.65    1.82     13.0     14.3       436
L8     2        427   2.7   2.1   2.1     5.2    8.81    7.54     50.1     43.6     1,229
L9     3      1,075   6.8   5.5   6.5     7.8    3.27    3.67     21.0     20.6       734
L10    3      2,142  13.5  13.8  12.9    11.7    2.18    2.76     12.6     14.1       555
L11    3        202   1.3   1.1   1.0     1.5    3.50    4.62     14.8     20.3       762
L12    4        932   5.9   4.7   6.0     5.5    2.20    2.83     13.3     15.9       604
L13    4        548   3.5   3.3   3.6     2.0    1.55    1.73      9.8     10.2       373
L14    4        494   3.1   3.9   3.1     2.0    1.62    1.91     12.8     13.2       405
L15    4      5,863  36.9  44.6  38.3     8.1    0.59    0.64      3.7      4.4       140
```

Spread of recovery over the personas inside each leaf (30+ accounts):

```text
Leaf  SD pp  Persona min-max %  Personas 30+/all
----  -----  -----------------  ----------------
L1     3.09           8.5-24.5             28/35
L2     1.38           4.5-11.9             26/60
L3     0.73            5.9-8.2               4/9
L4     0.99            2.7-5.2              6/12
L5     0.67            0.7-5.0               7/8
L6     0.69            0.8-4.3              7/11
L7     0.49            0.7-2.3               4/4
L8     2.57           3.5-13.2             21/65
L9     1.10            2.2-7.0             14/38
L10    1.06            1.5-9.0             21/65
L11    1.14            1.6-6.5              6/14
L12    0.77            1.2-6.4              8/13
L13    0.34            0.4-1.9               3/4
L14    0.62            1.0-3.1              9/29
L15    0.41            0.0-1.9             23/32
```

C1. Cards (cc_60_180): share of May accounts, outstanding and money in leaves using 1, 2, 3 and 4+
states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
1            0      0.0       0.0      0.0          0.0
2            2      9.7       6.9     27.2          6.6
3            4     27.2      27.0     36.1         25.3
4+           9     63.0      66.1     36.6         68.1
```

C2. Cards (cc_60_180): collected per account (sensitivity), by exact number of states; change in May
error 0.05%

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
2            3     30.1      26.6     48.0         26.0
3            2     10.3      11.2     22.0          8.5
4            5     54.2      56.0     24.8         60.3
5            2      5.4       6.2      5.2          5.2
```

### C1. Loans (rl_60_180): 12 leaves, May error 0.25% below the no-split root; forced first split
changes the May error by -0.03% against tree B (negative = the gated tree fits slightly better)

L1: Reachability: Reachable · Deterioration: Curing now
L2: Reachability: Reachable · Deterioration: Cured before
L3: Reachability: Reachable · Deterioration: Never paid or Stopped suddenly
L4: Reachability: Non-Reachable or Unknown · Deterioration: Curing now
L5: Reachability: Unknown · Deterioration: Cured before · Location: In Country or Unknown
L6: Reachability: Non-Reachable · Deterioration: Cured before · Location: In Country or Unknown ·
    Ability: High or Moderate
L7: Reachability: Non-Reachable · Deterioration: Cured before · Location: In Country or Unknown ·
    Ability: Low or Unknown · Credibility: Moderate
L8: Reachability: Non-Reachable · Deterioration: Cured before · Location: In Country or Unknown ·
    Ability: Low or Unknown · Credibility: High or Low
L9: Reachability: Unknown · Deterioration: Never paid or Stopped suddenly · Location: In Country or
    Unknown
L10: Reachability: Non-Reachable · Deterioration: Never paid or Stopped suddenly · Location: In
    Country or Unknown
L11: Reachability: Non-Reachable or Unknown · Deterioration: Cured before or Never paid or Stopped
    suddenly · Location: Skip · Credibility: High or Moderate
L12: Reachability: Non-Reachable or Unknown · Deterioration: Cured before or Never paid or Stopped
    suddenly · Location: Skip · Credibility: Low

```text
Leaf  St  May accts  %acc  Aug%  %out  %money  Rec tr  Rec te  Paid tr  Paid te  AED/acct
----  --  ---------  ----  ----  ----  ------  ------  ------  -------  -------  --------
L1     2        186   6.0   5.8   4.6    10.9    8.55    7.77     76.5     75.8     6,598
L2     2        342  11.1   9.7  11.9    19.9    4.36    5.46     43.6     52.9     6,540
L3     2        417  13.5  10.6  14.8    11.9    2.23    2.62     29.4     36.7     3,208
L4     2        142   4.6   4.5   2.8     6.6    7.45    7.78     65.7     71.8     5,264
L5     3        114   3.7   2.9   1.5     4.3    6.63    9.49     49.1     51.8     4,284
L6     4         72   2.3   1.7   1.3     3.0    5.83    7.40     39.5     47.2     4,647
L7     5        151   4.9   4.0   4.4     6.5    3.84    4.84     38.7     48.3     4,860
L8     5        203   6.6   5.4   5.5     4.4    2.88    2.62     24.7     27.1     2,448
L9     3        159   5.1   5.4   4.0     5.4    4.01    4.47     33.6     47.2     3,829
L10    3        412  13.3  15.2  16.0    12.4    1.43    2.54     18.9     29.9     3,390
L11    4        129   4.2   5.3   4.2     3.3    2.13    2.62     25.5     24.0     2,916
L12    4        769  24.8  29.4  28.9    11.3    0.91    1.29      8.6     13.8     1,661
```

Spread of recovery over the personas inside each leaf (30+ accounts):

```text
Leaf  SD pp  Persona min-max %  Personas 30+/all
----  -----  -----------------  ----------------
L1     1.65           5.7-12.9             11/31
L2     1.52            2.5-8.3             16/32
L3     1.16            1.0-6.6             10/35
L4     1.09            4.5-7.7              4/54
L5     1.65            3.9-8.3              5/20
L6     2.25           3.8-10.2               4/9
L7     0.71            2.8-4.9               4/4
L8     0.57            1.8-3.4               4/8
L9     1.49            2.8-6.8              4/22
L10    0.86            0.7-3.9             10/27
L11    0.16            1.7-2.1              4/20
L12    0.45            0.0-2.2             12/22
```

C1. Loans (rl_60_180): share of May accounts, outstanding and money in leaves using 1, 2, 3 and 4+
states

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
1            0      0.0       0.0      0.0          0.0
2            4     35.1      34.2     49.3         30.7
3            3     22.1      21.5     22.1         23.5
4+           5     42.8      44.3     28.6         45.8
```

C2. Loans (rl_60_180): collected per account (sensitivity), by exact number of states; change in May
error -0.17%

```text
States  Leaves  % accts  % outst.  % money  Aug % accts
------  ------  -------  --------  -------  -----------
2            2     29.1      29.6     38.4         24.8
3            3     41.9      37.3     46.9         40.5
4            2     29.0      33.1     14.7         34.7
```

## D. Two contrasting examples (picked by rule from the B1 leaves)

### Cards (cc_60_180)

Rule: largest leaf by May accounts that uses at most 2 states (1 or 2).
L1: Deterioration: Curing now · Reachability: Reachable or Unknown. 2 state(s); 1,163 May accounts
(7.3%), 22.7% of money, recovery 14.77% train / 13.71% May. Personas with at least 30 accounts: 28
of 66; recovery SD 3.09 pp, range 8.51-24.46%.

First 12 personas by accounts (Jan-May pooled; full list in the JSON):

- Curing now · location unknown · reachable · moderate credibility · ability unknown: 358 accts,
  recovery 17.51%, paid 75.4%, AED 2,088/acct
- Curing now · in country · reachable · moderate credibility · moderate ability: 332 accts, recovery
  15.50%, paid 71.9%, AED 2,244/acct
- Curing now · location unknown · reachable · moderate credibility · moderate ability: 278 accts,
  recovery 13.87%, paid 72.4%, AED 1,844/acct
- Curing now · in country · reachable · moderate credibility · ability unknown: 263 accts, recovery
  15.07%, paid 72.4%, AED 2,062/acct
- Curing now · in country · reachable · moderate credibility · low ability: 247 accts, recovery
  12.25%, paid 67.2%, AED 1,973/acct
- Curing now · location unknown · reachable · high credibility · ability unknown: 210 accts,
  recovery 16.28%, paid 75.1%, AED 2,052/acct
- Curing now · location unknown · reachable · moderate credibility · low ability: 193 accts,
  recovery 15.76%, paid 72.3%, AED 2,002/acct
- Curing now · in country · reachable · high credibility · moderate ability: 166 accts, recovery
  14.95%, paid 77.7%, AED 2,033/acct
- Curing now · location unknown · reachable · high credibility · moderate ability: 164 accts,
  recovery 16.61%, paid 77.5%, AED 1,840/acct
- Curing now · in country · reachable · moderate credibility · high ability: 150 accts, recovery
  24.46%, paid 78.5%, AED 2,830/acct
- Curing now · in country · reachable · high credibility · low ability: 143 accts, recovery 13.38%,
  paid 71.4%, AED 2,072/acct
- Curing now · in country · reachable · high credibility · ability unknown: 141 accts, recovery
  13.76%, paid 77.5%, AED 1,766/acct

Rule: leaf with the most money collected in May that uses 4 or more states.
L15: Deterioration: Never paid or Stopped suddenly · Reachability: Non-Reachable or Unknown ·
Location: Skip or Unknown · Credibility: Low. 4 state(s); 5,863 May accounts (36.9%), 8.1% of money,
recovery 0.59% train / 0.64% May. Personas with at least 30 accounts: 23 of 32; recovery SD 0.41 pp,
range 0.00-1.91%.

First 12 personas by accounts (Jan-May pooled; full list in the JSON):

- Stopped suddenly · departure trail · not reachable · low credibility · ability unknown: 4,433
  accts, recovery 0.50%, paid 2.8%, AED 99/acct
- Stopped suddenly · location unknown · not reachable · low credibility · ability unknown: 2,356
  accts, recovery 0.64%, paid 4.0%, AED 114/acct
- Stopped suddenly · departure trail · not reachable · low credibility · low ability: 1,597 accts,
  recovery 0.58%, paid 3.8%, AED 132/acct
- Never paid · location unknown · not reachable · low credibility · ability unknown: 1,144 accts,
  recovery 0.14%, paid 1.4%, AED 47/acct
- Stopped suddenly · departure trail · reachability unknown · low credibility · ability unknown:
  1,067 accts, recovery 1.15%, paid 4.0%, AED 217/acct
- Stopped suddenly · location unknown · not reachable · low credibility · low ability: 951 accts,
  recovery 1.06%, paid 6.9%, AED 199/acct
- Stopped suddenly · location unknown · not reachable · low credibility · moderate ability: 776
  accts, recovery 1.61%, paid 8.6%, AED 258/acct
- Stopped suddenly · departure trail · not reachable · low credibility · moderate ability: 503
  accts, recovery 1.27%, paid 7.4%, AED 237/acct
- Stopped suddenly · location unknown · reachability unknown · low credibility · ability unknown:
  503 accts, recovery 1.24%, paid 4.6%, AED 156/acct
- Never paid · departure trail · not reachable · low credibility · ability unknown: 492 accts,
  recovery 0.12%, paid 1.5%, AED 33/acct
- Stopped suddenly · departure trail · reachability unknown · low credibility · low ability: 438
  accts, recovery 1.49%, paid 5.1%, AED 291/acct
- Never paid · location unknown · reachability unknown · low credibility · ability unknown: 261
  accts, recovery 0.71%, paid 2.4%, AED 193/acct

### Loans (rl_60_180)

Rule: largest leaf by May accounts that uses at most 2 states (1 or 2).
L1: Deterioration: Curing now. 1 state(s); 328 May accounts (10.6%), 17.5% of money, recovery 8.15%
train / 7.78% May. Personas with at least 30 accounts: 15 of 85; recovery SD 1.75 pp, range
4.50-12.93%.

First 12 personas by accounts (Jan-May pooled; full list in the JSON):

- Curing now · in country · reachable · moderate credibility · low ability: 100 accts, recovery
  8.50%, paid 78.0%, AED 8,056/acct
- Curing now · in country · not reachable · moderate credibility · low ability: 69 accts, recovery
  6.36%, paid 61.7%, AED 5,789/acct
- Curing now · location unknown · reachable · moderate credibility · low ability: 58 accts, recovery
  6.59%, paid 68.6%, AED 5,618/acct
- Curing now · in country · reachable · high credibility · low ability: 55 accts, recovery 8.68%,
  paid 82.1%, AED 8,046/acct
- Curing now · location unknown · reachable · moderate credibility · ability unknown: 48 accts,
  recovery 7.50%, paid 77.3%, AED 4,397/acct
- Curing now · in country · reachable · moderate credibility · moderate ability: 46 accts, recovery
  8.96%, paid 85.5%, AED 9,743/acct
- Curing now · location unknown · reachable · high credibility · low ability: 46 accts, recovery
  5.65%, paid 65.2%, AED 3,672/acct
- Curing now · in country · reachable · moderate credibility · ability unknown: 42 accts, recovery
  9.18%, paid 82.4%, AED 4,644/acct
- Curing now · departure trail · reachable · moderate credibility · low ability: 38 accts, recovery
  8.91%, paid 76.3%, AED 7,949/acct
- Curing now · location unknown · reachable · moderate credibility · moderate ability: 37 accts,
  recovery 7.55%, paid 73.6%, AED 5,973/acct
- Curing now · location unknown · reachable · high credibility · ability unknown: 37 accts, recovery
  12.93%, paid 87.5%, AED 7,778/acct
- Curing now · location unknown · not reachable · moderate credibility · low ability: 32 accts,
  recovery 4.50%, paid 64.9%, AED 5,226/acct

Rule: leaf with the most money collected in May that uses 4 or more states.
L8: Deterioration: Cured before or Never paid or Stopped suddenly · Location: Skip · Credibility:
Low · Reachability: Non-Reachable or Unknown. 4 state(s); 769 May accounts (24.8%), 11.3% of money,
recovery 0.91% train / 1.29% May. Personas with at least 30 accounts: 12 of 22; recovery SD 0.45 pp,
range 0.04-2.22%.

First 12 personas by accounts (Jan-May pooled; full list in the JSON):

- Stopped suddenly · departure trail · not reachable · low credibility · low ability: 476 accts,
  recovery 0.98%, paid 11.0%, AED 1,434/acct
- Stopped suddenly · departure trail · not reachable · low credibility · ability unknown: 452 accts,
  recovery 0.98%, paid 8.6%, AED 1,090/acct
- Cured before · departure trail · not reachable · low credibility · ability unknown: 230 accts,
  recovery 1.05%, paid 9.0%, AED 1,267/acct
- Cured before · departure trail · not reachable · low credibility · low ability: 197 accts,
  recovery 1.51%, paid 10.3%, AED 2,373/acct
- Stopped suddenly · departure trail · reachability unknown · low credibility · low ability: 186
  accts, recovery 1.36%, paid 14.7%, AED 1,637/acct
- Stopped suddenly · departure trail · reachability unknown · low credibility · ability unknown: 181
  accts, recovery 0.54%, paid 7.2%, AED 675/acct
- Never paid · departure trail · not reachable · low credibility · low ability: 88 accts, recovery
  0.20%, paid 3.1%, AED 358/acct
- Never paid · departure trail · not reachable · low credibility · ability unknown: 86 accts,
  recovery 0.04%, paid 0.6%, AED 63/acct
- Cured before · departure trail · reachability unknown · low credibility · low ability: 64 accts,
  recovery 2.22%, paid 22.0%, AED 3,384/acct
- Cured before · departure trail · reachability unknown · low credibility · ability unknown: 60
  accts, recovery 1.81%, paid 15.4%, AED 1,542/acct
- Stopped suddenly · departure trail · not reachable · low credibility · moderate ability: 38 accts,
  recovery 0.75%, paid 13.0%, AED 894/acct
- Never paid · departure trail · reachability unknown · low credibility · ability unknown: 31 accts,
  recovery 0.05%, paid 0.0%, AED 80/acct

## Caveats

- Thin loan cells. May has 3,096 loan accounts (5,416 distinct over Jan-May); most persona cells
  hold 30-100 accounts, recovery is heavy-tailed, and loan trees stop on the 150-account rule. Loan
  intervals are wide and the loan state counts are lower bounds.

- Accounts overlap across cohort months. From the book totals, about 72% of May card accounts
  (25,208 + 15,890 - 29,629 distinct) and 66% of May loan accounts (4,380 + 3,096 - 5,416) also
  appear in Jan-Apr, and the 3-month windows of neighbouring cohorts overlap in time. Out of time
  here means a later month, not new customers. Persona listings count accounts over Jan-May pooled,
  so persona counts can add up to more than the leaf's accounts.

- Loan payments are month-grain: paid and collected for loans use monthly payment totals in months
  m+1 to m+3, so timing inside a month is not seen.

- Observed payments reflect today's handling. Payback by state is payback under the current
  strategy, so state importance here is not causal and may shift when the strategy changes.

- Several numbers are optimistic or narrow by construction: the tree's 'gain vs root' is measured on
  May, which also decides the out-of-time keep rule; the best two- and three-state combinations are
  picked on May; bootstrap intervals hold the training estimates fixed, so they ignore training
  noise.

- The estimator penalises large combinations (sparser cells, shrinkage k = 20 fixed). Raw cell means
  and the 6-state deterioration leave the cards ranking unchanged (AUC Shapley 0.082, 0.076, 0.061,
  0.045, 0.031 under both) and the loan top four still overlap.

- Tree rules were applied literally: the largest-error-reduction split is chosen first and kept only
  if the size, gap and out-of-time rules all hold. Where it fails, the node stops even if another
  split would pass (counts in the 'Other splits passing' column), so states-needed is rule-
  dependent. 'Unknown' levels of ability, reachability and location partly measure data coverage,
  not behaviour.

- Recovery is over accounts with positive outstanding principal; shares of money use all accounts.
