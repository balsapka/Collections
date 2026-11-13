# In-house list check - results (cc_60_180, rl_60_180)

Source: `inhouse_cc_60_180.json`, `inhouse_rl_60_180.json` (PROD run of `inhouse_check.py`; cohort months Jan-May
2026, persona month Aug 2026, 3-month outcomes). Persona = family × location × reach × credibility × ability.
In-house cut: cards AED 1,250, loans AED 6,000 per account over 3 months; a persona needs 10 training accounts.
Schemes: strict (train ≤ m-3; test Apr, May), adjacent (train < m; test Feb-May), grouped 5-fold by account.
Cells under 10 accounts are suppressed. Figures marked *calc* are arithmetic on file numbers.

## Verdict

1. **In-house is mostly Reachable, but not only.** Share of August in-house accounts (May table) that are not
   Reachable: cards **19.0 %** (Non-Reachable 9.9, Unknown 9.1), loans **40.3 %** (27.3 / 13.0). Out-of-sample
   (adjacent): cards 11.4 %, loans 35.9 %. The ten largest card personas are all Reachable (41 % of in-house
   accounts); on loans only 5 of the top 10 are, 3 are Non-Reachable.
2. **Abroad (Skip) customers do reach in-house:** **22.1 %** of cards in-house accounts (≈487, *calc*) and
   **20.2 %** of loans (≈73, *calc*); out-of-sample 16-18 % (cards), 23-28 % (loans).
3. **Credible-or-able, not reachable customers are a large group and mostly stay out.** Non-Reachable + Unknown
   with credibility or ability ≥ Moderate are 22-23 % of accounts in both products. They pay and collect far
   less than Reachable with the same profile (adjacent): cards paid 19.2 % / AED 552 / recovery 2.96 % vs
   53.1 % / 1,676 / 9.30 %; loans 44.4 % / 4,195 / 4.59 % vs 59.7 % / 5,571 / 6.16 %. In-house share: cards 7.8 %,
   loans 13.8 % (Reachable 74.2 % and 33.1 %). Their personas sit at a median 0.36× (cards) / 0.51× (loans) of the
   cut, and only ~5 % are within 20 % below it. Exception: `curing_now` Non-Reachable, ~58-64 % (cards) and
   ~52-59 % (loans) in-house.
4. **Reachability alone is not enough; family × reachability gets most of the way.** AUC for paid (adjacent / strict)
   cards: R .709/.695, FR .796/.782, FRN .811/.796, B .821/.804; loans: R .633/.629, FR .725/.703,
   FRN .749/.729, B .757/.729. Money in the top 20 %: FR 52.5 vs B 54.3 (cards, adjacent). Credibility and ability
   add ~.02-.03 AUC and, above all, separate the bottom: cut from FR only 4.8-7.8 % of accounts fall in the
   non-workable tier, cut from B 25-36 %.
5. **The list moves with the cut far more than with the reachability definition.** Cards R0 cut -20 % → +20 %:
   70 → 44 in-house personas, August in-house share 13.9 → 7.4 %; loans 25 → 10, 15.4 → 4.5 %. At the current cut
   R2/R2b/R3 swap 2-4 personas in and 9-10 out (cards). R1 (6 failed call days) moves most (cards 684 accounts in,
   671 out) and doubles the credible-or-able Non-Reachable in-house share (7.8 → 15.5 %), but those in-house
   members collect AED 1,162 out-of-sample, below the 1,250 cut (R0: 1,400). On loans R1 does not raise it
   (13.1 vs 13.8 %).
6. **The single-month list is not stable, loans badly.** Cards: 21 personas in-house in all 5 months cover
   **37.0 %** of August in-house accounts (48.1 % with the 10 in 4 of 5, *calc*); pairwise Jaccard .37-.54; 52-57 %
   of August in-house accounts stay in-house under another month's table. Loans: **1** persona in all 5 months
   (4.4 %); Jaccard .09-.36; account overlap 15.5-53.0 %.
7. **Pooling and the band stabilise it at little cost on cards, a real cost on loans.** Adjacent, tier changes
   for an unchanged persona: cards 12.9 → 5.9 % (P) → 5.4 % (PB), mean Jaccard .51 → .73 → .80, in-house paid %
   -0.4/-0.3 pt, AED/acct -29/-20, money share +2.4/+1.0 pt. Loans 35.0 → 15.4 → 13.9 %, Jaccard .25 → .56 → .61,
   paid % +2.0/+3.9 pt, AED/acct +245/+169, but money share -4.0/-6.4 pt (fewer accounts listed).
8. **A frozen list holds on the two later months tested** (Apr, May): cards adjacent paid 56.0 % / AED 1,775 /
   money 40.4 % vs P 55.3 / 1,792 / 42.7; loans 64.5 / 5,949 / 17.4 vs P 61.9 / 6,068 / 17.9. Two months and
   overlapping accounts: "no visible deterioration", not a durable result.

## Caveats

- **Loans R0 check not clean:** `r0_check.differences` = 3 of 23,739 rows (cards 0 of 128,927). ~0.01 %, immaterial
  to the numbers, but R0 does not reproduce A2 exactly on loans.
- **In-sample figures:** A1 list paid % / AED, all C1/C2 monthly AED, and the August "expected money share" are the
  table's own values; personas are picked at the cut, so they are biased up. Read as distance to the cut.
- **Thin evidence:** strict has two test months, so C3/C4 strict is one list-overlap pair and frozen = S = P for
  April; k-fold trains on later cohorts than it tests and was not run for P/PB/frozen. Loan personas are thin
  (in-house lists 8-19 personas, many monthly cells < 10 accounts; 4 of the top-15 loan flippers have a < 10 month).
- **Cohort overlap:** an account sits in up to 5 cohort months (cards 74,256 account-months / 29,629 accounts; loans
  12,512 / 5,416), so folds are not independent and spreads understate uncertainty.
- **Loan amounts** come from `int_loan_master.total_paid` (month-end snapshots), so paid and collected carry
  month-grain noise.
- **Observed payments reflect today's handling:** Non-Reachable groups were worked differently, so their low
  payment is not proof they would not pay under another strategy. Call effort was not lower for them (cards
  12.23 call days Non-Reachable vs 12.12 Reachable; loans 10.53 vs 9.40); only Unknown reach was worked less
  (cards 5.63, 32.9 % never called).
- **Threshold:** a persona needs 10 training accounts here; the earlier test used 30. B30 reconciles with
  `oos_results.md` (cards adjacent AUC .820 vs .821; loans .755 vs .755).
- **Cards list is fragile at the cut:** six of the top-10 card in-house personas are within AED 100 of it.

## Key tables

### A1 / A2. In-house list today (May table, August accounts)

| | cards | loans |
|---|---|---|
| personas with a table / in-house | 170 / 62 | 81 / 19 |
| August accounts / in-house / share | 19,292 / 2,205 / 11.4 % | 3,985 / 362 / 9.1 % |
| in-house Non-Reachable / Unknown / Skip % | 9.9 / 9.1 / 22.1 | 27.3 / 13.0 / 20.2 |

In-house account mix by locatability cell, % (OOS = adjacent test rows):

| cell | cards Aug | cards OOS | loans Aug | loans OOS |
|---|---|---|---|---|
| in_country / reachable | 44.8 | 47.7 | 36.5 | 31.5 |
| in_country / non_reachable | 4.3 | 4.1 | 10.5 | 9.4 |
| in_country / unknown | 5.9 | 1.6 | 7.2 | 5.2 |
| skip / reachable | 19.7 | 14.7 | 13.0 | 18.9 |
| skip / non_reachable | <10 | 1.6 | <10 | 6.3 |
| skip / unknown | 2.1 | 0.7 | 5.0 | 3.0 |
| unknown / reachable | 16.5 | 26.3 | 10.2 | 13.7 |
| unknown / non_reachable | 5.3 | 2.9 | 14.6 | 6.4 |
| unknown / unknown | 1.0 | 0.5 | <10 | 5.7 |

Top-10 personas by August accounts (family | location | reach | credibility | ability; Aug accounts; table paid %,
AED/acct; distance to cut):

| # | cards | Aug | paid % | AED | vs cut |
|---|---|---|---|---|---|
| 1 | stopped_suddenly \| skip \| reachable \| low \| low | 154 | 16.3 | 1,282 | +32 |
| 2 | curing_now \| unknown \| reachable \| moderate \| unknown | 97 | 68.5 | 1,738 | +488 |
| 3 | cure_history \| in_country \| reachable \| low \| low | 97 | 32.6 | 1,262 | +12 |
| 4 | cure_history \| in_country \| reachable \| low \| unknown | 96 | 31.3 | 1,318 | +68 |
| 5 | cure_history \| skip \| reachable \| low \| unknown | 96 | 26.4 | 1,278 | +28 |
| 6 | stopped_suddenly \| in_country \| reachable \| moderate \| low | 82 | 45.2 | 1,582 | +332 |
| 7 | cure_history \| in_country \| reachable \| moderate \| low | 79 | 38.6 | 1,348 | +98 |
| 8 | stopped_suddenly \| in_country \| reachable \| moderate \| unknown | 73 | 34.8 | 2,473 | +1,223 |
| 9 | curing_now \| in_country \| reachable \| moderate \| low | 70 | 69.8 | 2,300 | +1,050 |
| 10 | cure_history \| in_country \| reachable \| moderate \| unknown | 65 | 50.0 | 1,668 | +418 |

| # | loans | Aug | paid % | AED | vs cut |
|---|---|---|---|---|---|
| 1 | cure_history \| in_country \| reachable \| low \| low | 50 | 41.4 | 12,848 | +6,848 |
| 2 | cure_history \| unknown \| non_reachable \| moderate \| low | 32 | 65.8 | 7,156 | +1,156 |
| 3 | cure_history \| skip \| reachable \| low \| low | 31 | 45.8 | 8,116 | +2,116 |
| 4 | cure_history \| unknown \| reachable \| moderate \| unknown | 31 | 80.0 | 6,755 | +755 |
| 5 | curing_now \| in_country \| reachable \| moderate \| low | 30 | 73.7 | 9,934 | +3,934 |
| 6 | stopped_suddenly \| in_country \| unknown \| low \| low | 26 | - | 6,323 | +323 |
| 7 | curing_now \| in_country \| non_reachable \| moderate \| low | 22 | 77.8 | 6,946 | +946 |
| 8 | stopped_suddenly \| unknown \| non_reachable \| moderate \| low | 21 | 64.3 | 6,519 | +519 |
| 9 | cure_history \| skip \| unknown \| low \| low | 18 | - | 6,156 | +156 |
| 10 | cure_history \| in_country \| reachable \| low \| unknown | 17 | 47.6 | 6,990 | +990 |

(paid % blank where fewer than 10 payers.) Full list in the JSON (`A_composition.inhouse_today.personas`).

### A3. Credible-or-able (credibility or ability ≥ Moderate), out-of-sample

| model | scheme | group | % of all | paid % | AED/acct | recovery % | in-house % | median persona / cut |
 within 20 % below |
|---|---|---|---|---|---|---|---|---|
| cards | adjacent | Non-Reachable | 18.8 | 19.2 | 550 | 2.87 | 7.0 | 0.372 | 5.3 |
| cards | adjacent | Unknown reach | 3.3 | 18.8 | 564 | 3.67 | 12.2 | 0.263 | 4.3 |
| cards | adjacent | NR + Unknown | 22.1 | 19.2 | 552 | 2.96 | 7.8 | 0.363 | 5.2 |
| cards | adjacent | Reachable | 17.3 | 53.1 | 1,676 | 9.30 | 74.2 | 1.443 | 16.0 |
| cards | strict | NR + Unknown | 22.8 | 19.4 | 588 | 3.08 | 8.6 | 0.374 | 7.4 |
| cards | strict | Reachable | 16.0 | 52.0 | 1,682 | 9.10 | 70.8 | 1.425 | 20.8 |
| loans | adjacent | Non-Reachable | 17.8 | 40.8 | 4,061 | 4.19 | 12.3 | 0.487 | 5.3 |
| loans | adjacent | Unknown reach | 5.0 | 57.4 | 4,674 | 6.59 | 19.5 | 0.622 | 5.1 |
| loans | adjacent | NR + Unknown | 22.8 | 44.4 | 4,195 | 4.59 | 13.8 | 0.510 | 5.3 |
| loans | adjacent | Reachable | 18.7 | 59.7 | 5,571 | 6.16 | 33.1 | 0.794 | 15.5 |
| loans | strict | NR + Unknown | 24.1 | 47.0 | 4,463 | 5.04 | 11.8 | 0.492 | 5.2 |
| loans | strict | Reachable | 17.1 | 61.0 | 5,760 | 6.36 | 31.6 | 0.787 | 16.6 |

By family (adjacent / strict, Non-Reachable vs Reachable): cards `curing_now` paid 48.6/48.5 vs 71.6/70.8, in-house
57.7/63.6 vs 99.2/98.6; `cure_history` paid 19.9/20.0 vs 41.5/40.7, in-house ~0 vs 73.3/70.4; `stopped_suddenly`
12.7/13.0 vs 34.4/34.6, in-house 1.3/2.3 vs 34.8/30.0. Loans `curing_now` paid 66.5/66.7 vs 76.4/77.7, in-house
59.3/52.4 vs 62.1/69.0; `cure_history` 37.6/39.1 vs 51.3/51.6. Credibility-only and ability-only variants, and the
other families, are in the JSON (`A_composition.oos.<scheme>.groups`).

### A4. Ranking: reachability alone vs the full persona (AUC paid; money in the top 10 / 20 / 30 %)

| | cards adjacent | cards strict | loans adjacent | loans strict |
|---|---|---|---|---|
| R | .709; 22.0/44.0/62.6 | .695; 21.5/43.1/59.6 | .633; 14.6/29.2/43.8 | .629; 14.5/28.9/43.3 |
| LR | .755; 24.5/46.3/63.8 | .744; 22.6/44.8/60.9 | .689; 16.1/30.3/43.4 | .676; 15.5/28.6/42.2 |
| FR | .796; 32.7/52.5/66.9 | .782; 30.1/49.3/64.7 | .725; 19.0/35.7/48.5 | .703; 16.5/31.3/44.5 |
| FRN | .811; 33.1/54.2/66.7 | .796; 30.4/51.2/63.1 | .749; 19.1/35.5/49.8 | .729; 16.8/32.1/45.9 |
| B | .821; 31.4/54.3/66.9 | .804; 29.1/49.8/64.3 | .757; 19.8/36.3/49.2 | .729; 16.3/30.7/45.2 |
| B30 | .820; 32.2/54.2/67.0 | .804; 29.2/49.9/64.2 | .755; 20.0/35.4/47.4 | .730; 16.7/29.2/45.0 |

Tiers if cut from FR instead of B (in-house % of accounts / % of money / paid %; adjacent | strict):
cards FR 15.8 / 43.7 / 55.6 | 17.2 / 44.5 / 52.2, B 16.2 / 46.7 / 56.6 | 15.0 / 40.8 / 54.6;
loans FR 12.4 / 22.8 / 72.4 | 10.2 / 16.8 / 75.0, B 11.3 / 21.2 / 63.8 | 9.7 / 15.8 / 68.5.
Cards R and LR have no non-workable tier; on loans R and LR give no in-house tier (98-100 % agency).

### A5. Call days per account (adjacent OOS)

| | in-house | agency | non-workable | Reachable | Non-Reachable | Unknown |
|---|---|---|---|---|---|---|
| cards | 13.41 | 14.59 | 13.75 | 14.52 | 14.75 | 9.14 |
| loans | 12.2 | 12.7 | 13.48 | 13.51 | 13.17 | 10.38 |

Window = observation month and the two before it (A2 `attempt_days_in_window`).

### B. Sensitivity (August in-house share of accounts % / expected money % (table value) / OOS adjacent in-house paid %
and AED/acct / personas / credible-or-able NR+Unknown in-house % (adjacent))

Cards (current cut 1,250):

| variant | -20 % | -10 % | 0 | +10 % | +20 % |
|---|---|---|---|---|---|
| R0 share / money | 13.9 / 44.4 | 13.3 / 43.3 | 11.4 / 39.1 | 8.0 / 30.7 | 7.4 / 29.0 |
| R0 paid %; AED | 51.2; 1,622 | 53.3; 1,683 | 56.6; 1,783 | 58.7; 1,856 | 62.2; 1,884 |
| R0 personas | 70 | 66 | 62 | 50 | 44 |
| R0 NR-able in-house % | 12.9 | 11.2 | 7.8 | 6.2 | 4.2 |
| R1 share / money | 15.4 / 46.9 | 12.8 / 41.7 | 11.5 / 38.7 | 8.2 / 30.6 | 6.6 / 26.3 |
| R1 personas | 65 | 56 | 50 | 44 | 38 |
| R1 NR-able in-house % | 21.1 | 18.2 | 15.5 | 13.2 | 10.6 |
| R2 share / money | 15.7 / 47.9 | 11.6 / 39.4 | 10.3 / 36.4 | 9.8 / 35.1 | 7.4 / 28.6 |
| R2 NR-able in-house % | 15.4 | 13.5 | 9.7 | 7.3 | 5.1 |
| R3 share / money | 13.8 / 42.7 | 10.9 / 37.0 | 10.7 / 36.6 | 8.8 / 31.8 | 7.7 / 28.6 |
| R3 NR-able in-house % | 17.8 | 15.3 | 10.9 | 8.3 | 5.8 |

Loans (current cut 6,000):

| variant | -20 % | -10 % | 0 | +10 % | +20 % |
|---|---|---|---|---|---|
| R0 share / money | 15.4 / 32.6 | 11.1 / 26.2 | 9.1 / 22.7 | 7.3 / 19.3 | 4.5 / 13.6 |
| R0 paid %; AED | 59.9; 6,047 | 63.8; 6,430 | 63.8; 6,510 | 65.7; 6,687 | 69.5; 7,121 |
| R0 personas | 25 | 22 | 19 | 15 | 10 |
| R0 NR-able in-house % | 19.1 | 16.7 | 13.8 | 8.1 | 4.6 |
| R1 share / money | 15.3 / 33.9 | 14.6 / 32.8 | 9.6 / 24.3 | 7.7 / 20.8 | 7.2 / 19.6 |
| R1 NR-able in-house % | 24.4 | 18.0 | 13.1 | 10.9 | 8.2 |
| R2 share / money | 16.6 / 33.6 | 11.5 / 25.9 | 8.4 / 20.5 | 6.5 / 16.9 | 5.6 / 15.1 |
| R2 NR-able in-house % | 18.7 | 16.1 | 12.1 | 7.6 | 4.0 |
| R3 share / money | 18.2 / 36.5 | 13.1 / 28.7 | 10.3 / 24.0 | 7.2 / 18.1 | 5.5 / 14.5 |
| R3 NR-able in-house % | 19.6 | 16.9 | 12.8 | 7.2 | 4.3 |

R2b is within 1 point of R2 throughout (JSON). OOS adjacent in-house paid % / AED at the current cut across variants:
cards 55.8-57.0 % / 1,733-1,783; loans 63.4-65.5 % / 6,395-6,710.

Personas and accounts moving vs R0 at the current cut (personas in / out; accounts in / out):

| | cards | loans |
|---|---|---|
| R1 | 6 / 10; 684 / 671 | 7 / 9; 171 / 150 |
| R2 | 2 / 9; 143 / 362 | 1 / 4; 31 / 58 |
| R2b | 2 / 10; 150 / 384 | 1 / 3; 30 / 48 |
| R3 | 4 / 10; 250 / 387 | 2 / 4; 92 / 43 |

Credible-or-able Non-Reachable personas entering: cards R1 `curing_now | unknown | non_reachable | moderate | moderate`
(12 accounts), `cure_history | in_country | non_reachable | moderate | low` among movers (31); loans R1
`cure_history | in_country | non_reachable | moderate | low` (34). Cut -20 % on R0 brings 4 Non-Reachable personas in
on cards (e.g. `cure_history | unknown | non_reachable | moderate | moderate`, 73 accounts) and 3-4 on loans
(e.g. `stopped_suddenly | unknown | non_reachable | low | low`, 119; `cure_history | in_country | non_reachable |
moderate | low`, 50). No credible-or-able Non-Reachable persona is named entering under R2, R2b or R3 at the current
cut (some rows suppressed). Entering and leaving lists for every variant × cut: `B_sensitivity.grid`.

### C1 / C2. One table per cohort month

| | Jan | Feb | Mar | Apr | May |
|---|---|---|---|---|---|
| cards in-house personas | 54 | 45 | 46 | 57 | 62 |
| loans in-house personas | 9 | 10 | 8 | 16 | 19 |
| cards: % of Aug in-house accounts also in-house | 56.6 | 56.8 | 52.0 | 56.1 | 100 |
| loans: same | 15.5 | 35.4 | 17.1 | 53.0 | 100 |

Jaccard, cards: Jan-Feb .523, Jan-Mar .538, Jan-Apr .480, Jan-May .365, Feb-Mar .517, Feb-Apr .478, Feb-May .390,
Mar-Apr .493, Mar-May .403, Apr-May .469. Loans: .357, .214, .087, .120, .200, .238, .208, .200, .125, .296.

Personas in-house in exactly k of 5 months (cards / loans) and their share of August in-house accounts:

| k | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| cards personas | 41 | 15 | 16 | 10 | 21 |
| cards % of Aug in-house | 29.8 | 4.0 | 18.2 | 11.1 | 37.0 |
| loans personas | 23 | 7 | 4 | 2 | 1 |
| loans % of Aug in-house | 35.9 | 24.3 | 27.1 | 8.3 | 4.4 |

Flippers (1-3 months): cards 72, loans 34. Classified from the file's monthly cells: cards 11 thin only, 31 near the
cut only (a month within ±20 % of it), 17 both, 13 neither; loans 5 / 14 / 14 / 1. Most flippers hover near the cut;
thin months matter more on loans (19 of 34 flippers have a month under 10 accounts, cards 28 of 72). Several loan
flippers swing far beyond ±20 % (e.g. `cure_history | in_country | reachable | low | low`: 2,906 → 6,816 → 2,669 →
7,517 → 12,848). Monthly AED/acct, accounts and distance to the cut for every flipper: `C_stability.single_month_lists.
flippers_1_to_n_minus_2_months`.

### C3 / C4. Single-month (S), pooled (P), pooled + band (PB), frozen - out-of-sample

| model / scheme / rule | in-house accts | share % | paid % | AED/acct | money % | mean list Jaccard |
 tier changed, persona same % |
|---|---|---|---|---|---|---|---|
| cards adjacent S | 8,997 | 15.1 | 57.0 | 1,812 | 44.3 | .511 | 12.9 |
| cards adjacent P | 9,628 | 16.2 | 56.6 | 1,783 | 46.7 | .731 | 5.9 |
| cards adjacent PB | 9,300 | 15.6 | 56.7 | 1,792 | 45.3 | .802 | 5.4 |
| cards strict S | 4,462 | 14.6 | 54.7 | 1,762 | 40.6 | .523 | 16.2 |
| cards strict P | 4,587 | 15.0 | 54.6 | 1,724 | 40.8 | .610 | 9.9 |
| cards strict PB | 4,299 | 14.1 | 54.8 | 1,720 | 38.2 | .727 | 8.6 |
| loans adjacent S | 1,418 | 13.9 | 61.8 | 6,265 | 25.2 | .252 | 35.0 |
| loans adjacent P | 1,147 | 11.3 | 63.8 | 6,510 | 21.2 | .558 | 15.4 |
| loans adjacent PB | 1,032 | 10.1 | 65.7 | 6,434 | 18.8 | .607 | 13.9 |
| loans strict S | 554 | 9.6 | 68.4 | 6,559 | 17.1 | .357 | 27.4 |
| loans strict P | 556 | 9.7 | 68.5 | 6,028 | 15.8 | .438 | 12.8 |
| loans strict PB | 433 | 7.5 | 72.7 | 6,202 | 12.6 | .545 | 10.3 |

Frozen vs rebuilt on the same test months (Apr, May; frozen built from Jan for strict, Jan-Mar for adjacent):

| model / scheme / rule | accounts | paid % | AED/acct | money % |
|---|---|---|---|---|
| cards adjacent frozen / S / P / PB | 4,407 / 4,119 / 4,623 / 4,608 | 56.0 / 56.5 / 55.3 / 54.9 |
 1,775 / 1,854 / 1,792 / 1,778 | 40.4 / 39.4 / 42.7 / 42.3 |
| cards strict frozen / S / P / PB | 4,626 / 4,462 / 4,587 / 4,299 | 53.9 / 54.7 / 54.6 / 54.8 |
 1,722 / 1,762 / 1,724 / 1,720 | 41.1 / 40.6 / 40.8 / 38.2 |
| loans adjacent frozen / S / P / PB | 620 / 865 / 625 / 636 | 64.5 / 60.5 / 61.9 / 63.2 |
 5,949 / 6,209 / 6,068 / 5,802 | 17.4 / 25.3 / 17.9 / 17.4 |
| loans strict frozen / S / P / PB | 505 / 554 / 556 / 433 | 68.7 / 68.4 / 68.5 / 72.7 | 6,020 / 6,559 / 6,028 / 6,202 |
 14.3 / 17.1 / 15.8 / 12.6 |

Strict has one list-overlap pair (Apr → May); frozen and strict S are identical for April.
