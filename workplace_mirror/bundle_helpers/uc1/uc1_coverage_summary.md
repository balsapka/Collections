# UC1 signal export: quick coverage and sample check, summary (cc_60_180, rl_60_180)

Source: `results_uc1_cov_cc_60_180.md`, `results_uc1_cov_rl_60_180.md` (PROD rerun, snippet
2026-11-23b, which fixed the defects of the first run). **cc_180_plus and rl_180_plus were not run**
(the 2026-11-20 follow-up already dropped 180+: those CIFs are not in UC1's sample), so every 180+
statement below is "not run". Unit: account-month (account x month end), month ends 2026-01 ..
2026-08 (rl from 2026-02). Counts under 10 are `<10`.

## Context for the reader: catalog change and two assumptions

1. **Catalog change (`conf/base/catalog/catalog_tmp_uc1_cov.yml`, commit `1a8ffcef`).**
   `crx_uc1_proposer_level_observations` no longer reads the folder root; it reads **one
   partition**:
   `.../timelines/proposer_level_observations/snapshot_date=${globals:crx_persona.persona_end_date}`
   (2026-08-31 in dev/local, so it follows the persona end date). **Why:** the root load failed in
   PROD with `UNABLE_TO_INFER_SCHEMA` (three partition folders exist: 2026-08-31, 09-30, 10-31; at
   least one is probably empty), and we want one consistent snapshot at the persona end date through
   `catalog.load` only. The folder carries no `snapshot_date` column, so the snippet adds it.
   `crx_uc1_customer_signal_export` is unchanged. Both entries are temporary. The later E18
   `uc1_full` work uses separate `crx_uc1_full_*` names, so no clash.
2. **Export = Aug-end (user decision, 2026-11-23).** The export keeps only its latest snapshot
   (2026-10-31); we treat it as what we would have had at 2026-08-31. Support: it holds 5,040 CIFs
   against 5,038 in the 08-31 evidence (all 5,038 are in both), so it did not grow after August.
   Only Q3.4 reads the export.
3. **What the rerun settled.** (a) J3a had been 0 by construction (the evidence has no
   `repayment_specifics` rows); it now uses the intent alone, an upper bound. (b) The "not stated"
   cell is `no_reading_of_signal`. (c) **HIGH confidence is genuinely absent** for capacity and
   intent (Q1.4: every headline estimate is LOW; MEDIUM / HIGH under 10 CIFs); HIGH exists only for
   request (23). (d) Card product now comes from `prm_contract.product_id`. **Open defect:** Q6.7
   (repayment slots in the export) counts every value but not-detected as present, so it shows all
   CIFs (1,055 / 339) and means nothing; the export confidence of all three slots is N/A for all
   5,040 CIFs, i.e. no repayment data in the export either.

## Q1 Size (identical for both runs; evidence at 2026-08-31, export at its latest snapshot)

| model_id | measure |
|---|---|
| both | export rows / CIFs (10 rows each) |
| both | evidence rows / CIFs / customer-days |
| both | conversations of those CIFs in `crx_uc1_metadata` (whole table 147,004) |
| both | levels seen: capacity full / partial / none (customer-days) |
| both | levels seen: intent payback_full / partial / with_delay / no_payment |
| both | dispute system_problem / other / customer_scammed; request; `repayment_specifics` |
| both | export confidence, capacity / intent headline estimates (CIFs) |

| model_id | value |
|---|---|
| both | 50,400 / 5,040 |
| both | 35,098 / 5,038 / 11,043 |
| both | 28,022 |
| both | 2,288 / 3,039 / 667 |
| both | 3,578 / 2,293 / 3,689 / 284 |
| both | 1,742 / 193 / 72; 5,197; absent |
| both | LOW 3,751 / 4,700; MEDIUM and HIGH under 10; N/A = not-detected 1,283 / 331 |

| model_id | month | customer-days | transcript | remark |
|---|---|---|---|---|
| both | 2026-03 | 1,154 | 760 | 499 |
| both | 2026-04 | 1,596 | 1,036 | 721 |
| both | 2026-05 | 1,348 | 924 | 570 |
| both | 2026-06 | 3,133 | 2,513 | 805 |
| both | 2026-07 | 3,517 | 3,222 | 426 |
| both | 2026-08 | 36 | 0 | 36 |

Source: Q1.2 of the results (customer-days by month of `observed_at` and source). Before 2026-03
there are only remark days (under 35 a month); transcript observations are dated March to July 2026
and August has none **in this partition**. This is when the extracted observations are dated, not
proof of when calls happened: whether August calls exist in `crx_uc1_metadata` was not checked.

## Q2 Who they are

| model_id | UC1 CIFs | in base, any month | share | in base at 2026-08-31 | share |
|---|---|---|---|---|---|
| cc_60_180 | 5,038 | 1,513 | 30.0% | 1,001 | 19.9% |
| rl_60_180 | 5,038 | 485 | 9.6% | 309 | 6.1% |

| model_id | UC1 CIFs | not in this base | share |
|---|---|---|---|
| cc_60_180 | 5,038 | 3,525 | 70.0% |
| rl_60_180 | 5,038 | 4,553 | 90.4% |

"In none of the four" is not computable from separate runs. Bounds from the two 60-180 bases: in cc
or rl 60-180 at least 30.0% and at most 39.6% of the CIFs, so **at least 60.4% are in neither 60-180
base** (the 180+ bases were not run, so the share in none of the four is unknown).

| model_id | not-in-base CIFs hold | current | delinquent (a card / loan not current) |
|---|---|---|---|
| cc_60_180 | card only | 1,660 (47.1%) | 968 (27.5%) |
| cc_60_180 | card + loan | 363 (10.3%) | 456 (12.9%) |
| cc_60_180 | loan only | 12 (0.3%) | 58 (1.6%) |
| rl_60_180 | card only | 1,788 (39.3%) | 1,872 (41.1%) |
| rl_60_180 | card + loan | 387 (8.5%) | 476 (10.5%) |
| rl_60_180 | loan only | <10 | 13 (0.3%) |

CASA only / no product: under 10 in both. Source: `feat_cif_cross_product_monthly` (current = 0 DPD,
no DPD value), `feat_cif_casa_balance_monthly`. Loan type of the not-in-base CIFs: Auto 49, Personal
21, Personal Cash 18 (cc run); 10 / 11 / 13 (rl run). Loan product inside the rl base, covered
share: Auto 5.8%, Personal Cash 7.5%, Personal Loans 4.0% (pp gap +0.7 / +10.0 / -10.7). Card
product inside the cc base (`prm_contract.product_id`, 53 ids; the 6 largest by book, pooled):
555775 (28,041 account-months, 2.1% covered, -3.8 pp), 21032 (24,259, 2.4%, -1.4), 81384 (18,713,
2.3%, -1.6), 21003 (6,813, 2.3%), 24715700 (6,615, 3.5%, +1.9), 21010 (6,092, 4.0%, +2.6): no
product is strongly selected.

## Q3 Coverage of the book (covered = any observation of the CIF strictly before the month end)

| model_id | month end | book (accounts) | covered | share | transcript | remark |
|---|---|---|---|---|---|---|
| cc_60_180 | 2026-04-30 | 14,671 | 181 | 1.2% | 158 | 60 |
| cc_60_180 | 2026-06-30 | 16,982 | 698 | 4.1% | 609 | 243 |
| cc_60_180 | 2026-08-31 | 19,292 | 1,055 | 5.5% | 872 | 446 |
| rl_60_180 | 2026-04-30 | 2,661 | 124 | 4.7% | 118 | 51 |
| rl_60_180 | 2026-06-30 | 3,514 | 303 | 8.6% | 285 | 106 |
| rl_60_180 | 2026-08-31 | 3,985 | 339 | 8.5% | 321 | 114 |

Month ends 03, 05, 07 are in the results files; Jan / Feb: under 10 covered (rl Jan 0). Distinct
over Jan-Aug: cc 42,508 CIFs, 1,287 covered at least once (3.0%), 44,077 accounts, 1,376 covered
(3.1%); rl 7,832 CIFs, 458 (5.8%), 8,612 accounts, 511 (5.9%). The Aug-end-only CIF count of the
book is not printed.

| model_id | DPD band (pooled) | book n | covered n | share | pp gap | covered n >= 100 |
|---|---|---|---|---|---|---|
| cc_60_180 | 61-90 | 42,242 | 1,508 | 3.6% | +12.8 | yes |
| cc_60_180 | 91-120 | 33,312 | 919 | 2.8% | +1.9 | yes |
| cc_60_180 | 121-150 | 28,500 | 572 | 2.0% | -4.8 | yes |
| cc_60_180 | 151-180 | 24,873 | 309 | 1.2% | -10.0 | yes |
| rl_60_180 | 61-90 | 8,878 | 615 | 6.9% | +7.8 | yes |
| rl_60_180 | 91-120 | 6,674 | 398 | 6.0% | +1.2 | yes |
| rl_60_180 | 121-150 | 5,467 | 257 | 4.7% | -4.1 | yes |
| rl_60_180 | 151-180 | 2,720 | 90 | 3.3% | -4.8 | no |

Export headline estimates at the Aug-end snapshot (accounts whose CIF has a non-`not-detected`
estimate):

| model_id | book | CIF in export | capacity estimate | HIGH among them | intent estimate |
|---|---|---|---|---|---|
| cc_60_180 | 19,292 | 1,055 (5.5%) | 723 (3.7%) | 0 | 936 (4.9%) |
| rl_60_180 | 3,985 | 339 (8.5%) | 241 (6.0%) | 0 | 309 (7.8%) |

| model_id | book | HIGH among them |
|---|---|---|
| cc_60_180 | 19,292 | 0 |
| rl_60_180 | 3,985 | 0 |

## Q4 Persona coverage

Persona = A1 `a1_state` x A2 reach/loc x A3 `a3_state` x A4 `det_state`; the variant with A3 =
commitments level is in the results files.

| model_id | scope | personas | covered >= 1 | >= 30 | >= 100 | book share in >= 100 |
|---|---|---|---|---|---|---|
| cc_60_180 | Aug-end | 517 | 277 | 0 | 0 | 0.0% |
| cc_60_180 | pooled | 660 | 396 | 21 | 0 | 0.0% |
| rl_60_180 | Aug-end | 366 | 161 | 0 | 0 | 0.0% |
| rl_60_180 | pooled | 470 | 263 | 3 | 0 | 0.0% |

| model_id | scope | if all calls: >= 100 | book share |
|---|---|---|---|
| cc_60_180 | Aug-end | 8 | 23.9% |
| cc_60_180 | pooled | 43 | 46.2% |
| rl_60_180 | Aug-end | 0 | 0.0% |
| rl_60_180 | pooled | 2 | 2.8% |

Top 20 personas by pooled book size (A1 | A2 | A3 | A4) with covered n; the full lists are in the
results files (Q4.2). The biggest personas are the least covered.

- cc_60_180: the largest persona is unknown / non_reachable/skip / low / straight_roller_seasoned
  (11,051 account-months, 19 covered); covered n runs from under 10 to 73 across the top 20, none
  reaches 100.
- rl_60_180: the same persona is the largest (826, under 10 covered); covered n runs from under 10
  to 46 across the top 20.

Single axis states, covered vs book mix (pooled, pp gap): the largest gaps.

| model_id | axis | state | pp gap |
|---|---|---|---|
| cc_60_180 | A3 level | no_promise | -39.8 |
| cc_60_180 | A3 state | low | -30.5 |
| cc_60_180 | A3 level | partly_kept | +28.3 |
| cc_60_180 | A2 location | in_country | +25.9 |
| cc_60_180 | A2 reach | reachable | +23.3 |
| rl_60_180 | A2 location | in_country | +30.6 |
| rl_60_180 | A3 level | no_promise | -25.2 |

## Q5 Selection

paid_due over the next month, covered vs not covered; month ends 2026-01 .. 2026-07 with a complete
window.

| model_id | split | state | covered paid_due (n) |
|---|---|---|---|
| cc_60_180 | all | all | 17.9% (2,253) |
| cc_60_180 | A3 level | kept | 22.2% (81) |
| cc_60_180 | A3 level | partly_kept | 21.6% (1,201) |
| cc_60_180 | A3 level | promised | 15.7% (655) |
| cc_60_180 | A3 level | no_promise | 7.3% (316) |
| cc_60_180 | A1 | high / moderate / low | +1.4 / -3.0 / +4.2 |
| cc_60_180 | A1 | unknown | 17.2% (692) |
| rl_60_180 | all | all | 29.3% (1,021) |
| rl_60_180 | A3 level | kept | 42.4% (59) |
| rl_60_180 | A3 level | partly_kept | 32.7% (321) |
| rl_60_180 | A3 level | promised | 32.7% (263) |
| rl_60_180 | A3 level | no_promise | 22.0% (378) |
| rl_60_180 | A1 | moderate / low / unknown | +8.1 / +8.3 / +9.5 |

| model_id | split | not covered paid_due (n) | gap pp |
|---|---|---|---|
| cc_60_180 | all | 12.3% (107,382) | +5.6 |
| cc_60_180 | A3 level | 30.7% (3,899) | -8.5 |
| cc_60_180 | A3 level | 23.0% (27,503) | -1.4 |
| cc_60_180 | A3 level | 15.6% (18,506) | +0.1 |
| cc_60_180 | A3 level | 4.9% (57,474) | +2.3 |
| cc_60_180 | A1 | n 133 / 582 / 846 | |
| cc_60_180 | A1 | 8.7% (57,422) | +8.5 |
| rl_60_180 | all | 19.2% (18,733) | +10.1 |
| rl_60_180 | A3 level | 38.3% (658) | +4.1 |
| rl_60_180 | A3 level | 30.6% (3,432) | +2.1 |
| rl_60_180 | A3 level | 25.4% (2,871) | +7.3 |
| rl_60_180 | A3 level | 13.3% (11,772) | +8.6 |
| rl_60_180 | A1 | n 186 / 559 / 259 | |

Who gets a conversation (pooled covered share):

| model_id | band / state |
|---|---|
| cc_60_180 | DPD 61-90 / 91-120 / 121-150 / 151-180 |
| cc_60_180 | A2 reachable/in_country; non_reachable/skip |
| cc_60_180 | A4 repeat_delinquent / slow_roller; early_payment_default |
| rl_60_180 | DPD 61-90 / 91-120 / 121-150 / 151-180 |

| model_id | covered share | pp gap |
|---|---|---|
| cc_60_180 | 3.6% / 2.8% / 2.0% / 1.2% | +12.8 / +1.9 / -4.8 / -10.0 |
| cc_60_180 | 6.6%; 1.0% | +18.2; -16.9 |
| cc_60_180 | 4.7% / 3.7%; 1.0% | +7.0 / +8.3; -4.9 |
| rl_60_180 | 6.9% / 6.0% / 4.7% / 3.3% | +7.8 / +1.2 / -4.1 / -4.8 |

## Q6 Readiness

n = covered account-months, pooled; "all calls" = the projection described in the README: scaled by
the A1 / A3 coverage ratio.

J1 cells: able / partly / not stated (= no reading) / unable. J3a: 0 unmatched in Aug itself,
because the evidence has no August transcripts.

| model_id | job | target cells now |
|---|---|---|
| cc_60_180 | J1 A1 Unknown by capacity | 135 / 408 / 360 / 180 |
| rl_60_180 | J1 | 63 / 142 / 94 / 61 |
| cc_60_180 | J2 A3 no_promise by intent | 29 / 214 / 55 |
| rl_60_180 | J2 | 124 / 240 / 35 |
| cc_60_180 | J3a promise, no DCORE +-7 d (upper bound) | 173 of 214 promise rows |
| rl_60_180 | J3a | 169 of 194 |
| cc_60_180 | J3b stated dispute, A3 dispute flag false | 94 |
| rl_60_180 | J3b | 59 |
| cc_60_180 | J4 A1 x A3 pairs all >= 100 | 6 of 16 |
| rl_60_180 | J4 | 3 of 15 |

| model_id | job | target cells if all calls |
|---|---|---|
| cc_60_180 | J1 A1 Unknown by capacity | 878 / 2,655 / 2,343 / 1,171 |
| rl_60_180 | J1 | 196 / 442 / 293 / 190 |
| cc_60_180 | J2 A3 no_promise by intent | 303 / 2,234 / 574 |
| rl_60_180 | J2 | 421 / 816 / 119 |
| cc_60_180 | J3a promise, no DCORE +-7 d (upper bound) | 883 |
| rl_60_180 | J3a | 478 |
| cc_60_180 | J3b stated dispute, A3 dispute flag false | 480 |
| rl_60_180 | J3b | 167 |
| cc_60_180 | J4 A1 x A3 pairs all >= 100 | 12 of 16 |
| rl_60_180 | J4 | 7 of 15 |

| model_id | job | now >= 100 |
|---|---|---|
| cc_60_180 | J1 A1 Unknown by capacity | yes |
| rl_60_180 | J1 | no |
| cc_60_180 | J2 A3 no_promise by intent | no |
| rl_60_180 | J2 | no |
| cc_60_180 | J3a promise, no DCORE +-7 d (upper bound) | yes |
| rl_60_180 | J3a | yes |
| cc_60_180 | J3b stated dispute, A3 dispute flag false | no |
| rl_60_180 | J3b | no |
| cc_60_180 | J4 A1 x A3 pairs all >= 100 | no |
| rl_60_180 | J4 | no |

| model_id | job | projected >= 100 |
|---|---|---|
| cc_60_180 | J1 A1 Unknown by capacity | yes |
| rl_60_180 | J1 | yes |
| cc_60_180 | J2 A3 no_promise by intent | yes |
| rl_60_180 | J2 | yes |
| cc_60_180 | J3a promise, no DCORE +-7 d (upper bound) | yes |
| rl_60_180 | J3a | yes |
| cc_60_180 | J3b stated dispute, A3 dispute flag false | yes |
| rl_60_180 | J3b | yes |
| cc_60_180 | J4 A1 x A3 pairs all >= 100 | partly |
| rl_60_180 | J4 | partly |

Projection of the whole book:

| model_id | book account-months | covered now | covered if all calls | factor |
|---|---|---|---|---|
| cc_60_180 | 128,927 | 3,308 (2.6%) | 16,888 (13.1%) | 5.1 |
| rl_60_180 | 23,739 | 1,360 (5.7%) | 3,845 (16.2%) | 2.8 |

| model_id | book account-months | model CIFs with a call | calls | median calls per CIF |
|---|---|---|---|---|
| cc_60_180 | 128,927 | 7,519 | 26,427 | 2 |
| rl_60_180 | 23,739 | 1,551 | 4,787 | 2 |

## Verdicts

- **Size and who (Q1, Q2):** 5,038 CIFs, 11,043 customer-days, transcript observations dated March
  to July 2026 plus remarks; 28,022 conversations of those CIFs exist in the metadata against 11,043
  extracted customer-days. 30.0% of the CIFs sit in the cc 60-180 base and 9.6% in the rl base; at
  least 60.4% are in neither, mostly card holders (97.8% of the cc not-in-base CIFs hold a card),
  about 42% of them delinquent but outside 60-180 (or outside the obs base). 180+ not run.
- **Coverage of the book (Q3):** at Aug-end 5.5% of cc 60-180 account-months (1,055) and 8.5% of rl
  (339); pooled 2.6% and 5.7%. No transcript observations are dated August in this partition, so
  coverage stops growing at July's observations. Lower DPD bands are over-covered (61-90 +12.8 /
  +7.8 pp).
- **Personas usable (Q4):** none. 0 of 660 cc and 0 of 470 rl personas reach 100 covered
  account-months (21 and 3 reach 30); 0.0% of the book sits in personas at 100. After a full
  extraction: 43 cc personas hold 46.2% of the book, rl 2 personas hold 2.8% (rl stays too thin at
  persona level).
- **Selected sample (Q5):** yes, positively: covered are reachable, in-country, early DPD, non-low
  A3, away from no_promise (-39.8 / -25.2 pp) and A1 Unknown (-20.8 / -12.2 pp). They also pay more
  (cc +5.6 pp, rl +10.1 pp), and within A1 Unknown the covered pay 17.2% vs 8.7% (cc) and 24.7% vs
  15.2% (rl): the covered Unknown are not representative of all Unknown, so a fill rule learned on
  them would be biased.
- **Per integration job:** J1 fill A1 Unknown by capacity: **cc decide now on design** (all four
  cells >= 100), **rl wait for the refresh** (cells 61-142). J2 fill A3 no_promise by intent: **wait
  for the refresh** in both (cc pays_in_full 29, refuses 55; rl refuses 35); the full run lifts all
  cells above 100 (rl refuses 119 is borderline). J3a flag transcript promise vs DCORE: **decide now
  on the idea, with care**: 173 (cc) / 169 (rl) covered account-months are unmatched (81% / 87% of
  the promise rows), but it is an intent-only upper bound (no repayment rows in the evidence or
  export). J3b dispute flag: **wait for the refresh** (94 and 59 now; 480 and 167 projected). J4
  treatment by A1 x A3: **wait for the refresh** (cc 12 of 16, rl 7 of 15 pairs after a full run; rl
  will stay thin in the sparse pairs, e.g. A1 high / moderate-kept).
- **Overall: no, not good enough for persona-level strategic calls; yes for the cc J1 design
  direction and for the feasibility of the signals** (levels are populated and usable). The refresh
  must add: all calls extracted (factor 5.1 cc / 2.8 rl; even then only 13.1% / 16.2% of the book is
  covered), extraction of August and later calls (the metadata call dates by month were not
  checked), dated repayment rows with values, and better confidence: every capacity / intent
  estimate is LOW, so confidence cannot be used as a filter today. Running the persona pipelines to
  end of September would add a month end and the 09-30 evidence partition but cannot add calls; it
  does not change the verdicts above, and it is worth doing together with the refresh, not before.

