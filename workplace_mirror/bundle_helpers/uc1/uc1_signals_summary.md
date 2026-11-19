# UC1 transcript signals - summary (cc_60_180, rl_60_180)

Source: `results_uc1_signals_cc_60_180.md`, `results_uc1_signals_rl_60_180.md` (snippet 2026-11-19a; no errors; CASA
inflow read from
`feat_cif_inflow_outflow_salary_monthly`, the CASA-only variant is not built). **cc_180_plus and rl_180_plus were not
run**, so the
180+ part of A and any 180+ B-F are open. Unit = pair (conversation x account at the prior month end); outcomes after
the call date
(30 / 45 days, payments to 2026-08-31). Rate cells are `rate (n with outcome)`; `<10` masked. Sample sizes are small
(table S1):
most differences below are within noise unless stated; the tables carry the full outcome set where the source table
does.

### S1 sample for Parts B-F

| model_id | conversations (legacy dropped) | extracted | extracted with an account at prior month end | pairs |
|---|---|---|---|---|
| cc_60_180 | 19,319 | 3,555 | 597 | 643 |
| rl_60_180 | 3,578 | 1,311 | 335 | 358 |

_(same table, columns part 2 of 2)_

| model_id | distinct accounts |
|---|---|
| cc_60_180 | 333 |
| rl_60_180 | 148 |

## Part A - coverage

### A1 account-months with a conversation in the prior 90 days (store starts 2026-03-06, so a full 90 days exist only
from June)

| model_id | month_end | account_months | any_conv_90d | share_any | extracted_90d | share_extracted |
|---|---|---|---|---|---|---|
| cc_60_180 | 2026-03-31 | 14,455 | 70 | 0.5% | 40 | 0.3% |
| cc_60_180 | 2026-04-30 | 14,671 | 626 | 4.3% | 208 | 1.4% |
| cc_60_180 | 2026-05-31 | 15,890 | 2,058 | 13.0% | 455 | 2.9% |
| cc_60_180 | 2026-06-30 | 16,982 | 2,191 | 12.9% | 559 | 3.3% |
| cc_60_180 | 2026-07-31 | 18,397 | 1,872 | 10.2% | 489 | 2.7% |
| rl_60_180 | 2026-03-31 | 2,218 | 74 | 3.3% | 60 | 2.7% |
| rl_60_180 | 2026-04-30 | 2,661 | 294 | 11.0% | 160 | 6.0% |
| rl_60_180 | 2026-05-31 | 3,096 | 577 | 18.6% | 265 | 8.6% |
| rl_60_180 | 2026-06-30 | 3,514 | 621 | 17.7% | 277 | 7.9% |
| rl_60_180 | 2026-07-31 | 3,728 | 454 | 12.2% | 199 | 5.3% |

### A1b by a1_state (month end 2026-06-30 and 2026-07-31)

| model_id | month_end | a1_state | account_months | any_conv_90d | share_any | extracted_90d | share_extracted |
|---|---|---|---|---|---|---|---|
| cc_60_180 | 2026-06-30 | high | 321 | 69 | 21.5% | 32 | 10.0% |
| cc_60_180 | 2026-06-30 | moderate | 3,023 | 507 | 16.8% | 151 | 5.0% |
| cc_60_180 | 2026-06-30 | low | 4,728 | 827 | 17.5% | 203 | 4.3% |
| cc_60_180 | 2026-06-30 | unknown | 8,910 | 788 | 8.8% | 173 | 1.9% |
| cc_60_180 | 2026-07-31 | high | 299 | 45 | 15.1% | 20 | 6.7% |
| cc_60_180 | 2026-07-31 | moderate | 2,840 | 381 | 13.4% | 106 | 3.7% |
| cc_60_180 | 2026-07-31 | low | 5,257 | 745 | 14.2% | 193 | 3.7% |
| cc_60_180 | 2026-07-31 | unknown | 10,001 | 701 | 7.0% | 170 | 1.7% |
| rl_60_180 | 2026-06-30 | high | 31 | <10 | <10 | <10 | <10 |
| rl_60_180 | 2026-06-30 | moderate | 362 | 72 | 19.9% | 41 | 11.3% |
| rl_60_180 | 2026-06-30 | low | 1,791 | 365 | 20.4% | 157 | 8.8% |
| rl_60_180 | 2026-06-30 | unknown | 1,330 | 178 | 13.4% | 74 | 5.6% |
| rl_60_180 | 2026-07-31 | high | 27 | <10 | <10 | 0 | 0.0% |
| rl_60_180 | 2026-07-31 | moderate | 353 | 52 | 14.7% | 32 | 9.1% |
| rl_60_180 | 2026-07-31 | low | 1,855 | 285 | 15.4% | 114 | 6.1% |
| rl_60_180 | 2026-07-31 | unknown | 1,493 | 116 | 7.8% | 53 | 3.5% |

### A1c by a3_commitments_level (month end 2026-06-30 and 2026-07-31)

| model_id | month_end | a3_commitments_level | account_months | any_conv_90d | share_any | extracted_90d |
|---|---|---|---|---|---|---|
| cc_60_180 | 2026-06-30 | kept | 649 | 87 | 13.4% | 22 |
| cc_60_180 | 2026-06-30 | no_promise | 8,913 | 519 | 5.8% | 102 |
| cc_60_180 | 2026-06-30 | partly_kept | 4,594 | 928 | 20.2% | 289 |
| cc_60_180 | 2026-06-30 | promised | 2,826 | 657 | 23.2% | 146 |
| cc_60_180 | 2026-07-31 | kept | 638 | 53 | 8.3% | 19 |
| cc_60_180 | 2026-07-31 | no_promise | 10,207 | 496 | 4.9% | 77 |
| cc_60_180 | 2026-07-31 | partly_kept | 4,649 | 781 | 16.8% | 269 |
| cc_60_180 | 2026-07-31 | promised | 2,903 | 542 | 18.7% | 124 |
| rl_60_180 | 2026-06-30 | kept | 116 | 18 | 15.5% | 13 |
| rl_60_180 | 2026-06-30 | no_promise | 2,210 | 280 | 12.7% | 110 |
| rl_60_180 | 2026-06-30 | partly_kept | 655 | 162 | 24.7% | 88 |
| rl_60_180 | 2026-06-30 | promised | 533 | 161 | 30.2% | 66 |
| rl_60_180 | 2026-07-31 | kept | 117 | 21 | 17.9% | 14 |
| rl_60_180 | 2026-07-31 | no_promise | 2,412 | 202 | 8.4% | 75 |
| rl_60_180 | 2026-07-31 | partly_kept | 655 | 104 | 15.9% | 55 |
| rl_60_180 | 2026-07-31 | promised | 544 | 127 | 23.3% | 55 |

_(same table, columns part 2 of 2)_

| model_id | month_end | a3_commitments_level | share_extracted |
|---|---|---|---|
| cc_60_180 | 2026-06-30 | kept | 3.4% |
| cc_60_180 | 2026-06-30 | no_promise | 1.1% |
| cc_60_180 | 2026-06-30 | partly_kept | 6.3% |
| cc_60_180 | 2026-06-30 | promised | 5.2% |
| cc_60_180 | 2026-07-31 | kept | 3.0% |
| cc_60_180 | 2026-07-31 | no_promise | 0.8% |
| cc_60_180 | 2026-07-31 | partly_kept | 5.8% |
| cc_60_180 | 2026-07-31 | promised | 4.3% |
| rl_60_180 | 2026-06-30 | kept | 11.2% |
| rl_60_180 | 2026-06-30 | no_promise | 5.0% |
| rl_60_180 | 2026-06-30 | partly_kept | 13.4% |
| rl_60_180 | 2026-06-30 | promised | 12.4% |
| rl_60_180 | 2026-07-31 | kept | 12.0% |
| rl_60_180 | 2026-07-31 | no_promise | 3.1% |
| rl_60_180 | 2026-07-31 | partly_kept | 8.4% |
| rl_60_180 | 2026-07-31 | promised | 10.1% |

### A1d by DPD band (month end 2026-06-30 and 2026-07-31)

| model_id | month_end | dpd_band | account_months | any_conv_90d | share_any | extracted_90d | share_extracted |
|---|---|---|---|---|---|---|---|
| cc_60_180 | 2026-06-30 | 61-90 | 5,913 | 1,517 | 25.7% | 322 | 5.4% |
| cc_60_180 | 2026-06-30 | 91-120 | 4,524 | 574 | 12.7% | 178 | 3.9% |
| cc_60_180 | 2026-06-30 | 121-150 | 3,469 | 69 | 2.0% | 40 | 1.2% |
| cc_60_180 | 2026-06-30 | 151-180 | 3,076 | 31 | 1.0% | 19 | 0.6% |
| cc_60_180 | 2026-07-31 | 61-90 | 6,240 | 1,278 | 20.5% | 258 | 4.1% |
| cc_60_180 | 2026-07-31 | 91-120 | 4,912 | 469 | 9.5% | 159 | 3.2% |
| cc_60_180 | 2026-07-31 | 121-150 | 4,091 | 104 | 2.5% | 57 | 1.4% |
| cc_60_180 | 2026-07-31 | 151-180 | 3,154 | 21 | 0.7% | 15 | 0.5% |
| rl_60_180 | 2026-06-30 | 61-90 | 1,384 | 331 | 23.9% | 133 | 9.6% |
| rl_60_180 | 2026-06-30 | 91-120 | 992 | 198 | 20.0% | 85 | 8.6% |
| rl_60_180 | 2026-06-30 | 121-150 | 823 | 79 | 9.6% | 51 | 6.2% |
| rl_60_180 | 2026-06-30 | 151-180 | 315 | 13 | 4.1% | <10 | <10 |
| rl_60_180 | 2026-07-31 | 61-90 | 1,272 | 225 | 17.7% | 89 | 7.0% |
| rl_60_180 | 2026-07-31 | 91-120 | 1,148 | 147 | 12.8% | 69 | 6.0% |
| rl_60_180 | 2026-07-31 | 121-150 | 898 | 72 | 8.0% | 34 | 3.8% |
| rl_60_180 | 2026-07-31 | 151-180 | 410 | 10 | 2.4% | <10 | <10 |

### A2 which conversations were extracted

| model_id | call month | conversations | share extracted |
|---|---|---|---|
| cc_60_180 | 2026-03 | 5,684 | 14.1% |
| cc_60_180 | 2026-04 | 6,702 | 15.1% |
| cc_60_180 | 2026-05 | 3,984 | 21.3% |
| cc_60_180 | 2026-06 | 2,378 | 29.1% |
| cc_60_180 | 2026-07 | 571 | 35.9% |
| rl_60_180 | 2026-03 | 945 | 30.4% |
| rl_60_180 | 2026-04 | 1,197 | 32.7% |
| rl_60_180 | 2026-05 | 649 | 39.0% |
| rl_60_180 | 2026-06 | 637 | 43.5% |
| rl_60_180 | 2026-07 | 150 | 68.0% |

### A2b extracted share by the conversation-month worst DPD bucket (the strongest selector found)

| model_id | bucket | conversations | share extracted |
|---|---|---|---|
| cc_60_180 | 0 DPD | 1,167 | 6.2% |
| cc_60_180 | 1-30 DPD | 10,475 | 10.8% |
| cc_60_180 | 31-60 DPD | 6,278 | 24.6% |
| cc_60_180 | 61-90 DPD | 829 | 50.9% |
| cc_60_180 | 91-120 DPD | 219 | 63.9% |
| cc_60_180 | 121-150 DPD | 117 | 77.8% |
| cc_60_180 | 151-180 DPD | 57 | 77.2% |
| cc_60_180 | 180+ DPD | 165 | 66.1% |
| rl_60_180 | 0 DPD | 189 | 22.8% |
| rl_60_180 | 1-30 DPD | 866 | 18.8% |
| rl_60_180 | 31-60 DPD | 1,404 | 31.8% |
| rl_60_180 | 61-90 DPD | 646 | 52.0% |
| rl_60_180 | 91-120 DPD | 175 | 67.4% |
| rl_60_180 | 121-150 DPD | 95 | 75.8% |
| rl_60_180 | 151-180 DPD | 25 | 80.0% |
| rl_60_180 | 180+ DPD | 156 | 66.7% |

### A2c other metadata fields: extracted share by value

| model_id | field | value | conversations | extracted | share_extracted |
|---|---|---|---|---|---|
| cc_60_180 | completeness | -1 | 959 | 173 | 18.0% |
| cc_60_180 | completeness | -2 | 836 | 144 | 17.2% |
| cc_60_180 | completeness | -3 | 1,067 | 239 | 22.4% |
| cc_60_180 | completeness | -4 | 1,083 | 237 | 21.9% |
| cc_60_180 | completeness | -5 | 2,759 | 430 | 15.6% |
| cc_60_180 | completeness | -6 | 4,349 | 616 | 14.2% |
| cc_60_180 | completeness | -7 | 5,570 | 1,165 | 20.9% |
| cc_60_180 | completeness | 0 | 2,592 | 524 | 20.2% |
| cc_60_180 | completeness | 1 | 90 | 27 | 30.0% |
| cc_60_180 | completeness | 2 | <10 | 0 | <10 |
| cc_60_180 | completeness | 3 | <10 | 0 | <10 |
| cc_60_180 | entry_rank | 0 | 18,869 | 3,403 | 18.0% |
| cc_60_180 | entry_rank | 1 | 392 | 138 | 35.2% |
| cc_60_180 | entry_rank | 2 | 44 | <10 | <10 |
| cc_60_180 | entry_rank | 3 | <10 | <10 | <10 |
| cc_60_180 | entry_rank | 4 | <10 | <10 | <10 |
| cc_60_180 | entry_rank | 5 | <10 | <10 | <10 |
| cc_60_180 | entry_rank_at_response_delinquent | 0 | 268 | 75 | 28.0% |
| cc_60_180 | entry_rank_at_response_delinquent | 1 | 11,728 | 2,486 | 21.2% |
| cc_60_180 | entry_rank_at_response_delinquent | 2 | 1,482 | 254 | 17.1% |
| cc_60_180 | entry_rank_at_response_delinquent | 3 | 1,442 | 220 | 15.3% |
| cc_60_180 | entry_rank_at_response_delinquent | 4 | 448 | 97 | 21.7% |
| cc_60_180 | entry_rank_at_response_delinquent | 5 | 203 | 56 | 27.6% |
| cc_60_180 | entry_rank_at_response_delinquent | 6 | 86 | 30 | 34.9% |
| cc_60_180 | entry_rank_at_response_delinquent | 7 | <10 | 0 | <10 |
| cc_60_180 | entry_rank_at_response_delinquent | null | 3,661 | 337 | 9.2% |
| cc_60_180 | final_rank | 0 | 2,669 | 546 | 20.5% |
| cc_60_180 | final_rank | 1 | 954 | 168 | 17.6% |
| cc_60_180 | final_rank | 2 | 839 | 140 | 16.7% |
| cc_60_180 | final_rank | 3 | 1,051 | 235 | 22.4% |
| cc_60_180 | final_rank | 4 | 1,057 | 241 | 22.8% |
| cc_60_180 | final_rank | 5 | 2,737 | 405 | 14.8% |
| cc_60_180 | final_rank | 6 | 4,330 | 605 | 14.0% |
| cc_60_180 | final_rank | 7 | 5,682 | 1,215 | 21.4% |
| cc_60_180 | fully_repaid | false | 16,650 | 3,009 | 18.1% |
| cc_60_180 | fully_repaid | true | 2,669 | 546 | 20.5% |
| cc_60_180 | future_ptp_count | 0 | 13,579 | 2,570 | 18.9% |
| cc_60_180 | future_ptp_count | 1 | 3,391 | 540 | 15.9% |
| cc_60_180 | future_ptp_count | 10 | <10 | <10 | <10 |
| cc_60_180 | future_ptp_count | 2 | 1,203 | 222 | 18.5% |
| cc_60_180 | future_ptp_count | 3 | 561 | 128 | 22.8% |
| cc_60_180 | future_ptp_count | 4 | 252 | 38 | 15.1% |
| cc_60_180 | future_ptp_count | 5 | 157 | 32 | 20.4% |
| cc_60_180 | future_ptp_count | 6 | 97 | 16 | 16.5% |
| cc_60_180 | future_ptp_count | 7 | 46 | <10 | <10 |
| cc_60_180 | future_ptp_count | 8 | 27 | <10 | <10 |
| cc_60_180 | future_ptp_count | 9 | <10 | 0 | <10 |
| cc_60_180 | future_settlement_count | 0 | 16,493 | 2,956 | 17.9% |
| cc_60_180 | future_settlement_count | 1 | 2,441 | 477 | 19.5% |
| cc_60_180 | future_settlement_count | 2 | 299 | 100 | 33.4% |
| cc_60_180 | future_settlement_count | 3 | 49 | 14 | 28.6% |
| cc_60_180 | future_settlement_count | 4 | 31 | <10 | <10 |
| cc_60_180 | future_settlement_count | 5 | <10 | 0 | <10 |
| cc_60_180 | future_settlement_count | 6 | <10 | 0 | <10 |
| cc_60_180 | group_ids | null | 19,319 | 3,555 | 18.4% |
| cc_60_180 | had_product_credit_card | true | 19,319 | 3,555 | 18.4% |
| cc_60_180 | had_product_loan | false | 17,085 | 2,694 | 15.8% |
| cc_60_180 | had_product_loan | true | 2,234 | 861 | 38.5% |
| cc_60_180 | has_current_while_delinquent | false | 19,319 | 3,555 | 18.4% |
| cc_60_180 | has_future_ptp_or_settlement | false | 11,853 | 2,156 | 18.2% |
| cc_60_180 | has_future_ptp_or_settlement | true | 7,466 | 1,399 | 18.7% |
| cc_60_180 | has_prior_ptp_or_settlement | false | 6,667 | 782 | 11.7% |
| cc_60_180 | has_prior_ptp_or_settlement | true | 12,652 | 2,773 | 21.9% |
| cc_60_180 | has_ptp_or_settlement_within_window | false | 13,307 | 2,382 | 17.9% |
| cc_60_180 | has_ptp_or_settlement_within_window | true | 6,012 | 1,173 | 19.5% |
| cc_60_180 | last_observed_date | 2026-09-12 | 860 | 182 | 21.2% |
| cc_60_180 | last_observed_date | 2026-09-14 | <10 | 0 | <10 |
| cc_60_180 | last_observed_date | 2026-09-15 | 1,032 | 109 | 10.6% |
| cc_60_180 | last_observed_date | 2026-09-16 | 879 | 140 | 15.9% |
| cc_60_180 | last_observed_date | 2026-09-20 | 787 | 152 | 19.3% |
| cc_60_180 | last_observed_date | 2026-09-21 | <10 | 0 | <10 |
| cc_60_180 | last_observed_date | 2026-09-22 | 14 | <10 | <10 |
| cc_60_180 | last_observed_date | 2026-09-23 | 227 | 23 | 10.1% |
| cc_60_180 | last_observed_date | 2026-09-24 | 28 | <10 | <10 |
| cc_60_180 | last_observed_date | 2026-09-25 | 1,763 | 308 | 17.5% |
| cc_60_180 | last_observed_date | 2026-09-27 | 875 | 162 | 18.5% |
| cc_60_180 | last_observed_date | 2026-09-28 | 1,030 | 173 | 16.8% |
| cc_60_180 | last_observed_date | 2026-09-30 | 180 | 65 | 36.1% |
| cc_60_180 | last_observed_date | 2026-10-01 | 44 | <10 | <10 |
| cc_60_180 | last_observed_date | 2026-10-02 | 1,441 | 276 | 19.2% |
| cc_60_180 | last_observed_date | 2026-10-03 | 208 | 47 | 22.6% |
| cc_60_180 | last_observed_date | 2026-10-04 | <10 | 0 | <10 |
| cc_60_180 | last_observed_date | 2026-10-05 | 243 | 62 | 25.5% |
| cc_60_180 | last_observed_date | 2026-10-06 | 1,082 | 202 | 18.7% |
| cc_60_180 | last_observed_date | 2026-10-07 | 37 | <10 | <10 |
| cc_60_180 | last_observed_date | 2026-10-08 | 44 | <10 | <10 |
| cc_60_180 | last_observed_date | 2026-10-09 | 6,879 | 1,230 | 17.9% |
| cc_60_180 | last_observed_date | 2026-10-10 | 1,653 | 412 | 24.9% |
| cc_60_180 | last_observed_date | 2026-10-11 | <10 | 0 | <10 |
| cc_60_180 | prior_settlement_count | 0 | 17,982 | 3,071 | 17.1% |
| cc_60_180 | prior_settlement_count | 1 | 1,025 | 362 | 35.3% |
| cc_60_180 | prior_settlement_count | 10 | <10 | 0 | <10 |
| cc_60_180 | prior_settlement_count | 2 | 237 | 82 | 34.6% |
| cc_60_180 | prior_settlement_count | 3 | 35 | 18 | 51.4% |
| cc_60_180 | prior_settlement_count | 4 | 30 | 19 | 63.3% |
| cc_60_180 | prior_settlement_count | 5 | <10 | <10 | <10 |
| cc_60_180 | prior_settlement_count | 6 | <10 | 0 | <10 |
| cc_60_180 | ptp_30d_has_broken | false | 15,901 | 2,708 | 17.0% |
| cc_60_180 | ptp_30d_has_broken | true | 3,418 | 847 | 24.8% |
| cc_60_180 | ptp_30d_has_fulfilled | false | 18,641 | 3,402 | 18.3% |
| cc_60_180 | ptp_30d_has_fulfilled | true | 678 | 153 | 22.6% |
| cc_60_180 | ptp_30d_has_no_event | false | 4,012 | 953 | 23.8% |
| cc_60_180 | ptp_30d_has_no_event | true | 15,307 | 2,602 | 17.0% |
| cc_60_180 | ptp_30d_has_other | false | 18,862 | 3,403 | 18.0% |
| cc_60_180 | ptp_30d_has_other | true | 457 | 152 | 33.3% |
| cc_60_180 | ptp_within_window_count | 0 | 13,584 | 2,456 | 18.1% |
| cc_60_180 | ptp_within_window_count | 1 | 4,082 | 721 | 17.7% |
| cc_60_180 | ptp_within_window_count | 2 | 1,109 | 247 | 22.3% |
| cc_60_180 | ptp_within_window_count | 3 | 363 | 97 | 26.7% |
| cc_60_180 | ptp_within_window_count | 4 | 112 | 24 | 21.4% |
| cc_60_180 | ptp_within_window_count | 5 | 46 | <10 | <10 |
| cc_60_180 | ptp_within_window_count | 6 | 13 | <10 | <10 |
| cc_60_180 | ptp_within_window_count | 7 | <10 | <10 | <10 |
| cc_60_180 | ptp_within_window_count | 8 | <10 | 0 | <10 |
| cc_60_180 | settlement_within_window_count | 0 | 18,975 | 3,458 | 18.2% |
| cc_60_180 | settlement_within_window_count | 1 | 302 | 79 | 26.2% |
| cc_60_180 | settlement_within_window_count | 2 | 33 | 13 | 39.4% |
| cc_60_180 | settlement_within_window_count | 3 | <10 | <10 | <10 |
| rl_60_180 | completeness | -1 | 93 | 22 | 23.7% |
| rl_60_180 | completeness | -2 | 142 | 58 | 40.8% |
| rl_60_180 | completeness | -3 | 342 | 136 | 39.8% |
| rl_60_180 | completeness | -4 | 468 | 171 | 36.5% |
| rl_60_180 | completeness | -5 | 691 | 206 | 29.8% |
| rl_60_180 | completeness | -6 | 536 | 195 | 36.4% |
| rl_60_180 | completeness | -7 | 1,024 | 408 | 39.8% |
| rl_60_180 | completeness | 0 | 243 | 100 | 41.2% |
| rl_60_180 | completeness | 1 | 29 | 13 | 44.8% |
| rl_60_180 | completeness | 2 | <10 | <10 | <10 |
| rl_60_180 | completeness | 3 | <10 | 0 | <10 |
| rl_60_180 | completeness | 4 | <10 | <10 | <10 |
| rl_60_180 | entry_rank | 0 | 3,209 | 1,136 | 35.4% |
| rl_60_180 | entry_rank | 1 | 261 | 120 | 46.0% |
| rl_60_180 | entry_rank | 2 | 57 | 28 | 49.1% |
| rl_60_180 | entry_rank | 3 | 33 | 14 | 42.4% |
| rl_60_180 | entry_rank | 4 | 10 | <10 | <10 |
| rl_60_180 | entry_rank | 5 | <10 | <10 | <10 |
| rl_60_180 | entry_rank | 6 | <10 | <10 | <10 |
| rl_60_180 | entry_rank_at_response_delinquent | 0 | 145 | 51 | 35.2% |
| rl_60_180 | entry_rank_at_response_delinquent | 1 | 2,645 | 1,030 | 38.9% |
| rl_60_180 | entry_rank_at_response_delinquent | 2 | 191 | 48 | 25.1% |
| rl_60_180 | entry_rank_at_response_delinquent | 3 | 169 | 66 | 39.1% |
| rl_60_180 | entry_rank_at_response_delinquent | 4 | 36 | 21 | 58.3% |
| rl_60_180 | entry_rank_at_response_delinquent | 5 | <10 | <10 | <10 |
| rl_60_180 | entry_rank_at_response_delinquent | 6 | <10 | <10 | <10 |
| rl_60_180 | entry_rank_at_response_delinquent | null | 380 | 91 | 23.9% |
| rl_60_180 | final_rank | 0 | 244 | 102 | 41.8% |
| rl_60_180 | final_rank | 1 | 96 | 25 | 26.0% |
| rl_60_180 | final_rank | 2 | 130 | 40 | 30.8% |
| rl_60_180 | final_rank | 3 | 332 | 135 | 40.7% |
| rl_60_180 | final_rank | 4 | 439 | 164 | 37.4% |
| rl_60_180 | final_rank | 5 | 675 | 178 | 26.4% |
| rl_60_180 | final_rank | 6 | 504 | 180 | 35.7% |
| rl_60_180 | final_rank | 7 | 1,158 | 487 | 42.1% |
| rl_60_180 | fully_repaid | false | 3,334 | 1,209 | 36.3% |
| rl_60_180 | fully_repaid | true | 244 | 102 | 41.8% |
| rl_60_180 | future_ptp_count | 0 | 2,359 | 915 | 38.8% |
| rl_60_180 | future_ptp_count | 1 | 641 | 243 | 37.9% |
| rl_60_180 | future_ptp_count | 10 | <10 | 0 | <10 |
| rl_60_180 | future_ptp_count | 13 | <10 | <10 | <10 |
| rl_60_180 | future_ptp_count | 14 | <10 | <10 | <10 |
| rl_60_180 | future_ptp_count | 2 | 291 | 64 | 22.0% |
| rl_60_180 | future_ptp_count | 3 | 115 | 40 | 34.8% |
| rl_60_180 | future_ptp_count | 4 | 76 | 27 | 35.5% |
| rl_60_180 | future_ptp_count | 5 | 55 | 12 | 21.8% |
| rl_60_180 | future_ptp_count | 6 | 16 | <10 | <10 |
| rl_60_180 | future_ptp_count | 7 | <10 | <10 | <10 |
| rl_60_180 | future_ptp_count | 8 | <10 | 0 | <10 |
| rl_60_180 | future_ptp_count | 9 | <10 | 0 | <10 |
| rl_60_180 | future_settlement_count | 0 | 3,175 | 1,152 | 36.3% |
| rl_60_180 | future_settlement_count | 1 | 321 | 137 | 42.7% |
| rl_60_180 | future_settlement_count | 2 | 71 | 21 | 29.6% |
| rl_60_180 | future_settlement_count | 3 | 10 | 0 | 0.0% |
| rl_60_180 | future_settlement_count | 4 | <10 | <10 | <10 |
| rl_60_180 | group_ids | null | 3,578 | 1,311 | 36.6% |
| rl_60_180 | had_product_credit_card | false | 1,229 | 413 | 33.6% |
| rl_60_180 | had_product_credit_card | true | 2,349 | 898 | 38.2% |
| rl_60_180 | had_product_loan | true | 3,578 | 1,311 | 36.6% |
| rl_60_180 | has_current_while_delinquent | false | 3,578 | 1,311 | 36.6% |
| rl_60_180 | has_future_ptp_or_settlement | false | 2,148 | 813 | 37.8% |
| rl_60_180 | has_future_ptp_or_settlement | true | 1,430 | 498 | 34.8% |
| rl_60_180 | has_prior_ptp_or_settlement | false | 1,104 | 263 | 23.8% |
| rl_60_180 | has_prior_ptp_or_settlement | true | 2,474 | 1,048 | 42.4% |
| rl_60_180 | has_ptp_or_settlement_within_window | false | 2,510 | 892 | 35.5% |
| rl_60_180 | has_ptp_or_settlement_within_window | true | 1,068 | 419 | 39.2% |
| rl_60_180 | last_observed_date | 2026-02-28 | <10 | <10 | <10 |
| rl_60_180 | last_observed_date | 2026-03-31 | 16 | 0 | 0.0% |
| rl_60_180 | last_observed_date | 2026-04-30 | 15 | <10 | <10 |
| rl_60_180 | last_observed_date | 2026-05-31 | <10 | 0 | <10 |
| rl_60_180 | last_observed_date | 2026-06-30 | 76 | 29 | 38.2% |
| rl_60_180 | last_observed_date | 2026-07-31 | 16 | <10 | <10 |
| rl_60_180 | last_observed_date | 2026-08-31 | 1,104 | 375 | 34.0% |
| rl_60_180 | last_observed_date | 2026-09-12 | 176 | 68 | 38.6% |
| rl_60_180 | last_observed_date | 2026-09-15 | 128 | 34 | 26.6% |
| rl_60_180 | last_observed_date | 2026-09-16 | 127 | 44 | 34.6% |
| rl_60_180 | last_observed_date | 2026-09-20 | 103 | 49 | 47.6% |
| rl_60_180 | last_observed_date | 2026-09-23 | <10 | 0 | <10 |
| rl_60_180 | last_observed_date | 2026-09-25 | 227 | 96 | 42.3% |
| rl_60_180 | last_observed_date | 2026-09-27 | 204 | 90 | 44.1% |
| rl_60_180 | last_observed_date | 2026-09-28 | 52 | 18 | 34.6% |
| rl_60_180 | last_observed_date | 2026-09-30 | 24 | 13 | 54.2% |
| rl_60_180 | last_observed_date | 2026-10-01 | <10 | 0 | <10 |
| rl_60_180 | last_observed_date | 2026-10-02 | 172 | 73 | 42.4% |
| rl_60_180 | last_observed_date | 2026-10-03 | 17 | <10 | <10 |
| rl_60_180 | last_observed_date | 2026-10-05 | 50 | 16 | 32.0% |
| rl_60_180 | last_observed_date | 2026-10-06 | 124 | 35 | 28.2% |
| rl_60_180 | last_observed_date | 2026-10-07 | <10 | 0 | <10 |
| rl_60_180 | last_observed_date | 2026-10-08 | <10 | 0 | <10 |
| rl_60_180 | last_observed_date | 2026-10-09 | 673 | 242 | 36.0% |
| rl_60_180 | last_observed_date | 2026-10-10 | 252 | 116 | 46.0% |
| rl_60_180 | prior_settlement_count | 0 | 3,411 | 1,177 | 34.5% |
| rl_60_180 | prior_settlement_count | 1 | 134 | 110 | 82.1% |
| rl_60_180 | prior_settlement_count | 2 | 25 | 20 | 80.0% |
| rl_60_180 | prior_settlement_count | 3 | <10 | <10 | <10 |
| rl_60_180 | prior_settlement_count | 5 | <10 | 0 | <10 |
| rl_60_180 | ptp_30d_has_broken | false | 2,993 | 1,039 | 34.7% |
| rl_60_180 | ptp_30d_has_broken | true | 585 | 272 | 46.5% |
| rl_60_180 | ptp_30d_has_fulfilled | false | 3,434 | 1,238 | 36.1% |
| rl_60_180 | ptp_30d_has_fulfilled | true | 144 | 73 | 50.7% |
| rl_60_180 | ptp_30d_has_no_event | false | 702 | 329 | 46.9% |
| rl_60_180 | ptp_30d_has_no_event | true | 2,876 | 982 | 34.1% |
| rl_60_180 | ptp_30d_has_other | false | 3,487 | 1,252 | 35.9% |
| rl_60_180 | ptp_30d_has_other | true | 91 | 59 | 64.8% |
| rl_60_180 | ptp_within_window_count | 0 | 2,540 | 907 | 35.7% |
| rl_60_180 | ptp_within_window_count | 1 | 699 | 281 | 40.2% |
| rl_60_180 | ptp_within_window_count | 2 | 237 | 87 | 36.7% |
| rl_60_180 | ptp_within_window_count | 3 | 71 | 21 | 29.6% |
| rl_60_180 | ptp_within_window_count | 4 | 21 | 11 | 52.4% |
| rl_60_180 | ptp_within_window_count | 5 | <10 | 0 | <10 |
| rl_60_180 | ptp_within_window_count | 6 | <10 | <10 | <10 |
| rl_60_180 | ptp_within_window_count | 7 | <10 | <10 | <10 |
| rl_60_180 | settlement_within_window_count | 0 | 3,504 | 1,262 | 36.0% |
| rl_60_180 | settlement_within_window_count | 1 | 70 | 45 | 64.3% |
| rl_60_180 | settlement_within_window_count | 2 | <10 | <10 | <10 |

### A2d numeric fields (p10 / median / p90)

| model_id | field | extracted | not_extracted |
|---|---|---|---|
| cc_60_180 | call_duration | 109/273/681 | 112/277/680 |
| cc_60_180 | utterance_count | 10/35/92 | 10/36/95 |
| cc_60_180 | n_observed_months | 16/34/74 | 12/32/56 |
| cc_60_180 | prior_ptp_count | 0/2/11 | 0/1/7 |
| cc_60_180 | nearest_ptp_or_settlement_abs_days | 0/27/222 | 0/26/210 |
| rl_60_180 | call_duration | 132/280/674 | 119/300/734 |
| rl_60_180 | utterance_count | 11/36/95 | 11/40/105 |
| rl_60_180 | n_observed_months | 15/44/87 | 12/41/78 |
| rl_60_180 | prior_ptp_count | 0/2/10 | 0/1/6 |
| rl_60_180 | nearest_ptp_or_settlement_abs_days | 0/34/362 | 0/30/305 |

### A3 180+

| model_id | status | note |
|---|---|---|
| cc_180_plus | not run | Part A needed |
| rl_180_plus | not run | Part A needed |
| cc_60_180 | store holds 180+-bucket conversations of these customers | 165 conversations, 109 extracted (A2b) |
| rl_60_180 | store holds 180+-bucket conversations of these customers | 156 conversations, 104 extracted (A2b) |

## Part B - other signals vs payment after the call (pairs)

### B1 all signal levels, all confidence

| model_id | slot | level | n_conv | n_acct | n_pairs | pay30_due | pay30_any |
|---|---|---|---|---|---|---|---|
| cc_60_180 | delinquency_reason | has_employment | 89 | 73 | 92 | 23.9% (92) | 33.7% (92) |
| cc_60_180 | delinquency_reason | increased_obligations | 43 | 35 | 44 | <10 | <10 |
| cc_60_180 | delinquency_reason | lost_employment | 31 | 26 | 32 | <10 | <10 |
| cc_60_180 | delinquency_reason | reduced_employment | 27 | 26 | 28 | <10 | <10 |
| cc_60_180 | delinquency_reason | (not detected) [reference] | 407 | 255 | 447 | 15.4% (447) | 18.3% (447) |
| cc_60_180 | payment_period | months_or_longer | 12 | 12 | 13 | <10 | <10 |
| cc_60_180 | payment_period | salary_cycle_dependent | 89 | 80 | 92 | 21.7% (92) | 25.0% (92) |
| cc_60_180 | payment_period | weeks | 100 | 88 | 107 | 15.9% (107) | 20.6% (107) |
| cc_60_180 | payment_period | (not detected) [reference] | 396 | 248 | 431 | 15.3% (431) | 18.6% (431) |
| cc_60_180 | amount_mentioned | detected | 202 | 158 | 215 | 15.8% (215) | 19.5% (215) |
| cc_60_180 | amount_mentioned | (not detected) [reference] | 395 | 258 | 428 | 17.5% (428) | 21.0% (428) |
| cc_60_180 | date_specific | detected | 119 | 97 | 127 | 17.3% (127) | 22.0% (127) |
| cc_60_180 | date_specific | (not detected) [reference] | 478 | 285 | 516 | 16.9% (516) | 20.2% (516) |
| cc_60_180 | plan_structure_mentioned | detected | 49 | 42 | 51 | <10 | 21.6% (51) |
| cc_60_180 | plan_structure_mentioned | (not detected) [reference] | 548 | 319 | 592 | 16.9% (592) | 20.4% (592) |
| cc_60_180 | request (any) | detected | 256 | 176 | 268 | 17.5% (268) | 20.1% (268) |
| cc_60_180 | request (any) | (not detected) [reference] | 341 | 238 | 375 | 16.5% (375) | 20.8% (375) |
| cc_60_180 | request_type | (type missing) | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | request_type | callback | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | request_type | deferral | 45 | 46 | 49 | 20.4% (49) | 22.4% (49) |
| cc_60_180 | request_type | escalation | 11 | 10 | 11 | <10 | <10 |
| cc_60_180 | request_type | information | 80 | 79 | 85 | 20.0% (85) | 24.7% (85) |
| cc_60_180 | request_type | restructure | 46 | 38 | 47 | 21.3% (47) | 23.4% (47) |
| cc_60_180 | request_type | settlement | 75 | 47 | 76 | 13.2% (76) | 14.5% (76) |
| cc_60_180 | request_type | waiver | <10 | <10 | 10 | 0.0% (10) | 0.0% (10) |
| cc_60_180 | request_type | (not detected) [reference] | 341 | 238 | 375 | 16.5% (375) | 20.8% (375) |
| cc_60_180 | dispute | customer_scammed | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | dispute | other | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | dispute | system_problem | 150 | 113 | 164 | 12.8% (164) | 18.3% (164) |
| cc_60_180 | dispute | (not detected) [reference] | 440 | 278 | 472 | 18.6% (472) | 21.6% (472) |
| rl_60_180 | delinquency_reason | has_employment | 42 | 28 | 43 | 55.8% (43) | 65.1% (43) |
| rl_60_180 | delinquency_reason | increased_obligations | 27 | 21 | 29 | 41.4% (29) | 48.3% (29) |
| rl_60_180 | delinquency_reason | lost_employment | 50 | 23 | 50 | 40.0% (50) | 44.0% (50) |
| rl_60_180 | delinquency_reason | reduced_employment | 18 | 16 | 18 | <10 | 77.8% (18) |
| rl_60_180 | delinquency_reason | (not detected) [reference] | 198 | 114 | 218 | 33.5% (218) | 46.3% (218) |
| rl_60_180 | payment_period | months_or_longer | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | payment_period | salary_cycle_dependent | 41 | 29 | 41 | 46.3% (41) | 61.0% (41) |
| rl_60_180 | payment_period | weeks | 57 | 39 | 57 | 45.6% (57) | 59.6% (57) |
| rl_60_180 | payment_period | (not detected) [reference] | 232 | 119 | 255 | 35.3% (255) | 45.9% (255) |
| rl_60_180 | amount_mentioned | detected | 87 | 57 | 89 | 48.3% (89) | 60.7% (89) |
| rl_60_180 | amount_mentioned | (not detected) [reference] | 248 | 126 | 269 | 34.9% (269) | 46.5% (269) |
| rl_60_180 | date_specific | detected | 41 | 32 | 41 | 53.7% (41) | 61.0% (41) |
| rl_60_180 | date_specific | (not detected) [reference] | 294 | 137 | 317 | 36.3% (317) | 48.6% (317) |
| rl_60_180 | plan_structure_mentioned | detected | 10 | 10 | 10 | <10 | <10 |
| rl_60_180 | plan_structure_mentioned | (not detected) [reference] | 325 | 148 | 348 | 38.2% (348) | 50.0% (348) |
| rl_60_180 | request (any) | detected | 127 | 78 | 137 | 43.8% (137) | 55.5% (137) |
| rl_60_180 | request (any) | (not detected) [reference] | 208 | 101 | 221 | 34.8% (221) | 46.6% (221) |
| rl_60_180 | request_type | (type missing) | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | request_type | deferral | <10 | <10 | 10 | <10 | <10 |
| rl_60_180 | request_type | escalation | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | request_type | information | 50 | 44 | 57 | 35.1% (57) | 52.6% (57) |
| rl_60_180 | request_type | restructure | 23 | 16 | 23 | 65.2% (23) | 65.2% (23) |
| rl_60_180 | request_type | settlement | 37 | 15 | 38 | 55.3% (38) | 65.8% (38) |
| rl_60_180 | request_type | waiver | 21 | 13 | 21 | 52.4% (21) | 57.1% (21) |
| rl_60_180 | request_type | (not detected) [reference] | 208 | 101 | 221 | 34.8% (221) | 46.6% (221) |
| rl_60_180 | dispute | other | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | dispute | system_problem | 41 | 33 | 43 | 39.5% (43) | 51.2% (43) |
| rl_60_180 | dispute | (not detected) [reference] | 289 | 133 | 310 | 37.4% (310) | 49.4% (310) |

_(same table, columns part 2 of 2)_

| model_id | slot | level | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|---|
| cc_60_180 | delinquency_reason | has_employment | 28.3% (92) | 40.2% (92) | 19 |
| cc_60_180 | delinquency_reason | increased_obligations | <10 | 22.7% (44) | 21 |
| cc_60_180 | delinquency_reason | lost_employment | <10 | <10 | <10 |
| cc_60_180 | delinquency_reason | reduced_employment | <10 | 35.7% (28) | 25 |
| cc_60_180 | delinquency_reason | (not detected) [reference] | 19.5% (447) | 22.8% (447) | 18 |
| cc_60_180 | payment_period | months_or_longer | <10 | <10 | <10 |
| cc_60_180 | payment_period | salary_cycle_dependent | 28.3% (92) | 35.9% (92) | 16 |
| cc_60_180 | payment_period | weeks | 19.6% (107) | 24.3% (107) | 25 |
| cc_60_180 | payment_period | (not detected) [reference] | 19.5% (431) | 23.2% (431) | 18 |
| cc_60_180 | amount_mentioned | detected | 19.1% (215) | 24.2% (215) | 21 |
| cc_60_180 | amount_mentioned | (not detected) [reference] | 22.4% (428) | 26.9% (428) | 18 |
| cc_60_180 | date_specific | detected | 22.0% (127) | 29.1% (127) | 25 |
| cc_60_180 | date_specific | (not detected) [reference] | 21.1% (516) | 25.2% (516) | 18 |
| cc_60_180 | plan_structure_mentioned | detected | 19.6% (51) | 27.5% (51) | 18 |
| cc_60_180 | plan_structure_mentioned | (not detected) [reference] | 21.5% (592) | 25.8% (592) | 20 |
| cc_60_180 | request (any) | detected | 23.1% (268) | 28.0% (268) | 23 |
| cc_60_180 | request (any) | (not detected) [reference] | 20.0% (375) | 24.5% (375) | 18 |
| cc_60_180 | request_type | (type missing) | <10 | <10 | - |
| cc_60_180 | request_type | callback | <10 | <10 | <10 |
| cc_60_180 | request_type | deferral | 34.7% (49) | 36.7% (49) | 26 |
| cc_60_180 | request_type | escalation | <10 | <10 | <10 |
| cc_60_180 | request_type | information | 23.5% (85) | 29.4% (85) | 23 |
| cc_60_180 | request_type | restructure | 23.4% (47) | 27.7% (47) | 16 |
| cc_60_180 | request_type | settlement | 15.8% (76) | 21.1% (76) | 13 |
| cc_60_180 | request_type | waiver | <10 | <10 | <10 |
| cc_60_180 | request_type | (not detected) [reference] | 20.0% (375) | 24.5% (375) | 18 |
| cc_60_180 | dispute | customer_scammed | <10 | <10 | - |
| cc_60_180 | dispute | other | <10 | <10 | - |
| cc_60_180 | dispute | system_problem | 16.5% (164) | 24.4% (164) | 21 |
| cc_60_180 | dispute | (not detected) [reference] | 23.3% (472) | 26.9% (472) | 19 |
| rl_60_180 | delinquency_reason | has_employment | 55.8% (43) | 65.1% (43) | 18 |
| rl_60_180 | delinquency_reason | increased_obligations | 41.4% (29) | 51.7% (29) | 18 |
| rl_60_180 | delinquency_reason | lost_employment | 40.0% (50) | 44.0% (50) | 21 |
| rl_60_180 | delinquency_reason | reduced_employment | <10 | 77.8% (18) | 22 |
| rl_60_180 | delinquency_reason | (not detected) [reference] | 38.5% (218) | 50.5% (218) | 19 |
| rl_60_180 | payment_period | months_or_longer | <10 | <10 | <10 |
| rl_60_180 | payment_period | salary_cycle_dependent | 46.3% (41) | 61.0% (41) | 16 |
| rl_60_180 | payment_period | weeks | 45.6% (57) | 59.6% (57) | 14 |
| rl_60_180 | payment_period | (not detected) [reference] | 39.6% (255) | 49.8% (255) | 20 |
| rl_60_180 | amount_mentioned | detected | 51.7% (89) | 64.0% (89) | 21 |
| rl_60_180 | amount_mentioned | (not detected) [reference] | 37.9% (269) | 49.1% (269) | 19 |
| rl_60_180 | date_specific | detected | 53.7% (41) | 61.0% (41) | 21 |
| rl_60_180 | date_specific | (not detected) [reference] | 39.7% (317) | 51.7% (317) | 19 |
| rl_60_180 | plan_structure_mentioned | detected | <10 | <10 | <10 |
| rl_60_180 | plan_structure_mentioned | (not detected) [reference] | 41.1% (348) | 52.6% (348) | 19 |
| rl_60_180 | request (any) | detected | 45.3% (137) | 57.7% (137) | 21 |
| rl_60_180 | request (any) | (not detected) [reference] | 38.9% (221) | 49.8% (221) | 18 |
| rl_60_180 | request_type | (type missing) | <10 | <10 | - |
| rl_60_180 | request_type | deferral | <10 | <10 | <10 |
| rl_60_180 | request_type | escalation | <10 | <10 | <10 |
| rl_60_180 | request_type | information | 36.8% (57) | 54.4% (57) | 21 |
| rl_60_180 | request_type | restructure | 65.2% (23) | 69.6% (23) | 22 |
| rl_60_180 | request_type | settlement | 57.9% (38) | 68.4% (38) | 18 |
| rl_60_180 | request_type | waiver | 52.4% (21) | 57.1% (21) | 18 |
| rl_60_180 | request_type | (not detected) [reference] | 38.9% (221) | 49.8% (221) | 18 |
| rl_60_180 | dispute | other | <10 | <10 | <10 |
| rl_60_180 | dispute | system_problem | 41.9% (43) | 53.5% (43) | 13 |
| rl_60_180 | dispute | (not detected) [reference] | 40.6% (310) | 52.3% (310) | 19 |

### B1b all signal levels, high-confidence only

| model_id | slot | level | n_conv | n_acct | n_pairs | pay30_due | pay30_any |
|---|---|---|---|---|---|---|---|
| cc_60_180 | delinquency_reason | has_employment | 79 | 67 | 82 | 23.2% (82) | 30.5% (82) |
| cc_60_180 | delinquency_reason | increased_obligations | 38 | 32 | 39 | <10 | <10 |
| cc_60_180 | delinquency_reason | lost_employment | 31 | 26 | 32 | <10 | <10 |
| cc_60_180 | delinquency_reason | reduced_employment | 27 | 26 | 28 | <10 | <10 |
| cc_60_180 | delinquency_reason | (not detected) [reference] | 407 | 255 | 447 | 15.4% (447) | 18.3% (447) |
| cc_60_180 | payment_period | months_or_longer | 11 | 11 | 12 | <10 | <10 |
| cc_60_180 | payment_period | salary_cycle_dependent | 87 | 78 | 89 | 22.5% (89) | 25.8% (89) |
| cc_60_180 | payment_period | weeks | 88 | 81 | 95 | 15.8% (95) | 21.1% (95) |
| cc_60_180 | payment_period | (not detected) [reference] | 396 | 248 | 431 | 15.3% (431) | 18.6% (431) |
| cc_60_180 | amount_mentioned | detected | 189 | 151 | 202 | 16.8% (202) | 20.8% (202) |
| cc_60_180 | amount_mentioned | (not detected) [reference] | 395 | 258 | 428 | 17.5% (428) | 21.0% (428) |
| cc_60_180 | date_specific | detected | 108 | 89 | 116 | 17.2% (116) | 22.4% (116) |
| cc_60_180 | date_specific | (not detected) [reference] | 478 | 285 | 516 | 16.9% (516) | 20.2% (516) |
| cc_60_180 | plan_structure_mentioned | detected | 49 | 42 | 51 | <10 | 21.6% (51) |
| cc_60_180 | plan_structure_mentioned | (not detected) [reference] | 548 | 319 | 592 | 16.9% (592) | 20.4% (592) |
| cc_60_180 | request (any) | detected | 248 | 174 | 259 | 18.1% (259) | 20.8% (259) |
| cc_60_180 | request (any) | (not detected) [reference] | 341 | 238 | 375 | 16.5% (375) | 20.8% (375) |
| cc_60_180 | request_type | callback | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | request_type | deferral | 43 | 45 | 47 | 21.3% (47) | 23.4% (47) |
| cc_60_180 | request_type | escalation | 11 | 10 | 11 | <10 | <10 |
| cc_60_180 | request_type | information | 80 | 79 | 85 | 20.0% (85) | 24.7% (85) |
| cc_60_180 | request_type | restructure | 45 | 38 | 46 | 21.7% (46) | 23.9% (46) |
| cc_60_180 | request_type | settlement | 71 | 43 | 71 | 14.1% (71) | 15.5% (71) |
| cc_60_180 | request_type | waiver | <10 | <10 | 10 | 0.0% (10) | 0.0% (10) |
| cc_60_180 | request_type | (not detected) [reference] | 341 | 238 | 375 | 16.5% (375) | 20.8% (375) |
| cc_60_180 | dispute | customer_scammed | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | dispute | other | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | dispute | system_problem | 135 | 100 | 148 | 13.5% (148) | 18.9% (148) |
| cc_60_180 | dispute | (not detected) [reference] | 440 | 278 | 472 | 18.6% (472) | 21.6% (472) |
| rl_60_180 | delinquency_reason | has_employment | 36 | 23 | 36 | 55.6% (36) | 63.9% (36) |
| rl_60_180 | delinquency_reason | increased_obligations | 20 | 15 | 20 | <10 | <10 |
| rl_60_180 | delinquency_reason | lost_employment | 49 | 22 | 49 | 40.8% (49) | 44.9% (49) |
| rl_60_180 | delinquency_reason | reduced_employment | 16 | 15 | 16 | <10 | 75.0% (16) |
| rl_60_180 | delinquency_reason | (not detected) [reference] | 198 | 114 | 218 | 33.5% (218) | 46.3% (218) |
| rl_60_180 | payment_period | months_or_longer | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | payment_period | salary_cycle_dependent | 41 | 29 | 41 | 46.3% (41) | 61.0% (41) |
| rl_60_180 | payment_period | weeks | 52 | 37 | 52 | 44.2% (52) | 59.6% (52) |
| rl_60_180 | payment_period | (not detected) [reference] | 232 | 119 | 255 | 35.3% (255) | 45.9% (255) |
| rl_60_180 | amount_mentioned | detected | 73 | 45 | 73 | 52.1% (73) | 65.8% (73) |
| rl_60_180 | amount_mentioned | (not detected) [reference] | 248 | 126 | 269 | 34.9% (269) | 46.5% (269) |
| rl_60_180 | date_specific | detected | 35 | 27 | 35 | 60.0% (35) | 65.7% (35) |
| rl_60_180 | date_specific | (not detected) [reference] | 294 | 137 | 317 | 36.3% (317) | 48.6% (317) |
| rl_60_180 | plan_structure_mentioned | detected | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | plan_structure_mentioned | (not detected) [reference] | 325 | 148 | 348 | 38.2% (348) | 50.0% (348) |
| rl_60_180 | request (any) | detected | 121 | 74 | 130 | 46.2% (130) | 58.5% (130) |
| rl_60_180 | request (any) | (not detected) [reference] | 208 | 101 | 221 | 34.8% (221) | 46.6% (221) |
| rl_60_180 | request_type | deferral | <10 | <10 | 10 | <10 | <10 |
| rl_60_180 | request_type | escalation | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | request_type | information | 49 | 44 | 56 | 35.7% (56) | 53.6% (56) |
| rl_60_180 | request_type | restructure | 23 | 16 | 23 | 65.2% (23) | 65.2% (23) |
| rl_60_180 | request_type | settlement | 33 | 12 | 33 | 63.6% (33) | 75.8% (33) |
| rl_60_180 | request_type | waiver | 21 | 13 | 21 | 52.4% (21) | 57.1% (21) |
| rl_60_180 | request_type | (not detected) [reference] | 208 | 101 | 221 | 34.8% (221) | 46.6% (221) |
| rl_60_180 | dispute | other | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | dispute | system_problem | 35 | 26 | 36 | 44.4% (36) | 58.3% (36) |
| rl_60_180 | dispute | (not detected) [reference] | 289 | 133 | 310 | 37.4% (310) | 49.4% (310) |

_(same table, columns part 2 of 2)_

| model_id | slot | level | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|---|
| cc_60_180 | delinquency_reason | has_employment | 28.0% (82) | 36.6% (82) | 18 |
| cc_60_180 | delinquency_reason | increased_obligations | <10 | <10 | <10 |
| cc_60_180 | delinquency_reason | lost_employment | <10 | <10 | <10 |
| cc_60_180 | delinquency_reason | reduced_employment | <10 | 35.7% (28) | 25 |
| cc_60_180 | delinquency_reason | (not detected) [reference] | 19.5% (447) | 22.8% (447) | 18 |
| cc_60_180 | payment_period | months_or_longer | <10 | <10 | <10 |
| cc_60_180 | payment_period | salary_cycle_dependent | 29.2% (89) | 37.1% (89) | 16 |
| cc_60_180 | payment_period | weeks | 20.0% (95) | 25.3% (95) | 25 |
| cc_60_180 | payment_period | (not detected) [reference] | 19.5% (431) | 23.2% (431) | 18 |
| cc_60_180 | amount_mentioned | detected | 20.3% (202) | 25.7% (202) | 21 |
| cc_60_180 | amount_mentioned | (not detected) [reference] | 22.4% (428) | 26.9% (428) | 18 |
| cc_60_180 | date_specific | detected | 20.7% (116) | 28.4% (116) | 25 |
| cc_60_180 | date_specific | (not detected) [reference] | 21.1% (516) | 25.2% (516) | 18 |
| cc_60_180 | plan_structure_mentioned | detected | 19.6% (51) | 27.5% (51) | 18 |
| cc_60_180 | plan_structure_mentioned | (not detected) [reference] | 21.5% (592) | 25.8% (592) | 20 |
| cc_60_180 | request (any) | detected | 23.9% (259) | 29.0% (259) | 23 |
| cc_60_180 | request (any) | (not detected) [reference] | 20.0% (375) | 24.5% (375) | 18 |
| cc_60_180 | request_type | callback | <10 | <10 | <10 |
| cc_60_180 | request_type | deferral | 36.2% (47) | 38.3% (47) | 26 |
| cc_60_180 | request_type | escalation | <10 | <10 | <10 |
| cc_60_180 | request_type | information | 23.5% (85) | 29.4% (85) | 23 |
| cc_60_180 | request_type | restructure | 23.9% (46) | 28.3% (46) | 16 |
| cc_60_180 | request_type | settlement | 16.9% (71) | 22.5% (71) | 13 |
| cc_60_180 | request_type | waiver | <10 | <10 | <10 |
| cc_60_180 | request_type | (not detected) [reference] | 20.0% (375) | 24.5% (375) | 18 |
| cc_60_180 | dispute | customer_scammed | <10 | <10 | - |
| cc_60_180 | dispute | other | <10 | <10 | - |
| cc_60_180 | dispute | system_problem | 17.6% (148) | 25.7% (148) | 18 |
| cc_60_180 | dispute | (not detected) [reference] | 23.3% (472) | 26.9% (472) | 19 |
| rl_60_180 | delinquency_reason | has_employment | 55.6% (36) | 63.9% (36) | 18 |
| rl_60_180 | delinquency_reason | increased_obligations | <10 | <10 | <10 |
| rl_60_180 | delinquency_reason | lost_employment | 40.8% (49) | 44.9% (49) | 21 |
| rl_60_180 | delinquency_reason | reduced_employment | <10 | 75.0% (16) | 21 |
| rl_60_180 | delinquency_reason | (not detected) [reference] | 38.5% (218) | 50.5% (218) | 19 |
| rl_60_180 | payment_period | months_or_longer | <10 | <10 | <10 |
| rl_60_180 | payment_period | salary_cycle_dependent | 46.3% (41) | 61.0% (41) | 16 |
| rl_60_180 | payment_period | weeks | 44.2% (52) | 59.6% (52) | 14 |
| rl_60_180 | payment_period | (not detected) [reference] | 39.6% (255) | 49.8% (255) | 20 |
| rl_60_180 | amount_mentioned | detected | 56.2% (73) | 69.9% (73) | 18 |
| rl_60_180 | amount_mentioned | (not detected) [reference] | 37.9% (269) | 49.1% (269) | 19 |
| rl_60_180 | date_specific | detected | 60.0% (35) | 65.7% (35) | 19 |
| rl_60_180 | date_specific | (not detected) [reference] | 39.7% (317) | 51.7% (317) | 19 |
| rl_60_180 | plan_structure_mentioned | detected | <10 | <10 | <10 |
| rl_60_180 | plan_structure_mentioned | (not detected) [reference] | 41.1% (348) | 52.6% (348) | 19 |
| rl_60_180 | request (any) | detected | 47.7% (130) | 60.8% (130) | 21 |
| rl_60_180 | request (any) | (not detected) [reference] | 38.9% (221) | 49.8% (221) | 18 |
| rl_60_180 | request_type | deferral | <10 | <10 | <10 |
| rl_60_180 | request_type | escalation | <10 | <10 | <10 |
| rl_60_180 | request_type | information | 37.5% (56) | 55.4% (56) | 21 |
| rl_60_180 | request_type | restructure | 65.2% (23) | 69.6% (23) | 22 |
| rl_60_180 | request_type | settlement | 66.7% (33) | 78.8% (33) | 18 |
| rl_60_180 | request_type | waiver | 52.4% (21) | 57.1% (21) | 18 |
| rl_60_180 | request_type | (not detected) [reference] | 38.9% (221) | 49.8% (221) | 18 |
| rl_60_180 | dispute | other | <10 | <10 | <10 |
| rl_60_180 | dispute | system_problem | 47.2% (36) | 61.1% (36) | 10 |
| rl_60_180 | dispute | (not detected) [reference] | 40.6% (310) | 52.3% (310) | 19 |

B2 (within a1_state / a3_state, both confidence versions) is in the results files; nearly every cell is masked or under
50 pairs.

### B3.1 stated capacity

| model_id | basis | capacity | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | able | 88 | 83 | 99 | 19.2% (99) | 26.3% (99) | 23.2% (99) | 31.3% (99) |
| cc_60_180 | all | partly_able | 152 | 114 | 156 | 19.9% (156) | 23.7% (156) | 25.6% (156) | 32.7% (156) |
| cc_60_180 | all | not_stated | 336 | 225 | 367 | 15.5% (367) | 18.3% (367) | 19.3% (367) | 22.1% (367) |
| cc_60_180 | all | unable | 21 | 18 | 21 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | able | 61 | 62 | 67 | 14.9% (67) | 19.4% (67) | 19.4% (67) | 25.4% (67) |
| cc_60_180 | high conf | partly_able | 72 | 60 | 74 | 16.2% (74) | 21.6% (74) | 17.6% (74) | 24.3% (74) |
| cc_60_180 | high conf | not_stated | 336 | 225 | 367 | 15.5% (367) | 18.3% (367) | 19.3% (367) | 22.1% (367) |
| cc_60_180 | high conf | unable | 20 | 18 | 20 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | able | 41 | 29 | 41 | 34.1% (41) | 51.2% (41) | 46.3% (41) | 58.5% (41) |
| rl_60_180 | all | partly_able | 85 | 51 | 87 | 52.9% (87) | 60.9% (87) | 52.9% (87) | 62.1% (87) |
| rl_60_180 | all | not_stated | 190 | 106 | 211 | 31.8% (211) | 44.1% (211) | 34.6% (211) | 46.9% (211) |
| rl_60_180 | all | unable | 19 | 13 | 19 | 52.6% (19) | 63.2% (19) | 52.6% (19) | 63.2% (19) |
| rl_60_180 | high conf | able | 23 | 18 | 23 | <10 | 52.2% (23) | 52.2% (23) | 65.2% (23) |
| rl_60_180 | high conf | partly_able | 38 | 25 | 38 | 60.5% (38) | 71.1% (38) | 60.5% (38) | 71.1% (38) |
| rl_60_180 | high conf | not_stated | 190 | 106 | 211 | 31.8% (211) | 44.1% (211) | 34.6% (211) | 46.9% (211) |
| rl_60_180 | high conf | unable | 19 | 13 | 19 | 52.6% (19) | 63.2% (19) | 52.6% (19) | 63.2% (19) |

_(same table, columns part 2 of 2)_

| model_id | basis | capacity | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | all | able | 20 |
| cc_60_180 | all | partly_able | 21 |
| cc_60_180 | all | not_stated | 18 |
| cc_60_180 | all | unable | <10 |
| cc_60_180 | high conf | able | 18 |
| cc_60_180 | high conf | partly_able | 10 |
| cc_60_180 | high conf | not_stated | 18 |
| cc_60_180 | high conf | unable | <10 |
| rl_60_180 | all | able | 21 |
| rl_60_180 | all | partly_able | 21 |
| rl_60_180 | all | not_stated | 19 |
| rl_60_180 | all | unable | 13 |
| rl_60_180 | high conf | able | 24 |
| rl_60_180 | high conf | partly_able | 22 |
| rl_60_180 | high conf | not_stated | 19 |
| rl_60_180 | high conf | unable | 13 |

### B3.2 stated capacity within a1_state (cell tables: pay30_due / pay30_any / pay45_any %, (n pairs))

| model_id | basis | cap_s | All | high | moderate |
|---|---|---|---|---|---|
| cc_60_180 | all | able | 19.2/26.3/31.3 (99) | <10/<10/<10 (10) | <10/<10/34.4 (32) |
| cc_60_180 | all | partly_able | 19.9/23.7/32.7 (156) | <10/<10/41.7 (24) | 20.0/22.0/28.0 (50) |
| cc_60_180 | all | not_stated | 15.5/18.3/22.1 (367) | 25.0/27.1/33.3 (48) | 13.3/16.8/18.6 (113) |
| cc_60_180 | all | unable | <10/<10/<10 (21) | <10 | <10 |
| cc_60_180 | high conf | able | 14.9/19.4/25.4 (67) | <10 | <10/<10/<10 (23) |
| cc_60_180 | high conf | partly_able | 16.2/21.6/24.3 (74) | <10/<10/<10 (12) | <10/<10/<10 (23) |
| cc_60_180 | high conf | not_stated | 15.5/18.3/22.1 (367) | 25.0/27.1/33.3 (48) | 13.3/16.8/18.6 (113) |
| cc_60_180 | high conf | unable | <10/<10/<10 (20) | <10 | <10 |
| rl_60_180 | all | able | 34.1/51.2/58.5 (41) | <10 | <10 |
| rl_60_180 | all | partly_able | 52.9/60.9/62.1 (87) | <10 | 72.2/88.9/88.9 (18) |
| rl_60_180 | all | not_stated | 31.8/44.1/46.9 (211) | <10 | <10/47.1/52.9 (34) |
| rl_60_180 | all | unable | 52.6/63.2/63.2 (19) | 0 | <10 |
| rl_60_180 | high conf | able | <10/52.2/65.2 (23) | <10 | 0 |
| rl_60_180 | high conf | partly_able | 60.5/71.1/71.1 (38) | <10 | <10 |
| rl_60_180 | high conf | not_stated | 31.8/44.1/46.9 (211) | <10 | <10/47.1/52.9 (34) |
| rl_60_180 | high conf | unable | 52.6/63.2/63.2 (19) | 0 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | cap_s | low | unknown |
|---|---|---|---|---|
| cc_60_180 | all | able | <10/<10/<10 (32) | <10/<10/<10 (25) |
| cc_60_180 | all | partly_able | <10/<10/<10 (35) | <10/23.4/38.3 (47) |
| cc_60_180 | all | not_stated | 17.0/19.6/22.3 (112) | 11.7/13.8/20.2 (94) |
| cc_60_180 | all | unable | 0.0/0.0/<10 (10) | <10 |
| cc_60_180 | high conf | able | <10/<10/<10 (21) | 0.0/0.0/<10 (14) |
| cc_60_180 | high conf | partly_able | <10/<10/<10 (16) | <10/<10/<10 (23) |
| cc_60_180 | high conf | not_stated | 17.0/19.6/22.3 (112) | 11.7/13.8/20.2 (94) |
| cc_60_180 | high conf | unable | <10 | <10 |
| rl_60_180 | all | able | <10/42.9/46.4 (28) | <10 |
| rl_60_180 | all | partly_able | 51.3/59.0/61.5 (39) | 38.5/42.3/42.3 (26) |
| rl_60_180 | all | not_stated | 37.0/47.2/48.8 (127) | <10/30.4/34.8 (46) |
| rl_60_180 | all | unable | <10 | <10/<10/<10 (10) |
| rl_60_180 | high conf | able | <10/55.6/61.1 (18) | <10 |
| rl_60_180 | high conf | partly_able | <10/<10/<10 (12) | <10/<10/<10 (13) |
| rl_60_180 | high conf | not_stated | 37.0/47.2/48.8 (127) | <10/30.4/34.8 (46) |
| rl_60_180 | high conf | unable | <10 | <10/<10/<10 (10) |

### B3.3 stated capacity within a3_state (cell tables: pay30_due / pay30_any / pay45_any %, (n pairs))

| model_id | basis | cap_s | All | high | moderate |
|---|---|---|---|---|---|
| cc_60_180 | all | able | 19.2/26.3/31.3 (99) | <10/33.3/41.7 (36) | 19.6/23.5/27.5 (51) |
| cc_60_180 | all | partly_able | 19.9/23.7/32.7 (156) | 22.9/25.7/38.6 (70) | 16.4/21.9/28.8 (73) |
| cc_60_180 | all | not_stated | 15.5/18.3/22.1 (367) | 16.5/18.2/24.7 (170) | 13.7/18.0/18.7 (139) |
| cc_60_180 | all | unable | <10/<10/<10 (21) | <10/<10/<10 (10) | <10 |
| cc_60_180 | high conf | able | 14.9/19.4/25.4 (67) | <10/<10/<10 (21) | <10/<10/<10 (35) |
| cc_60_180 | high conf | partly_able | 16.2/21.6/24.3 (74) | <10/<10/<10 (25) | <10/<10/<10 (39) |
| cc_60_180 | high conf | not_stated | 15.5/18.3/22.1 (367) | 16.5/18.2/24.7 (170) | 13.7/18.0/18.7 (139) |
| cc_60_180 | high conf | unable | <10/<10/<10 (20) | <10/<10/<10 (10) | <10 |
| rl_60_180 | all | able | 34.1/51.2/58.5 (41) | <10 | <10/<10/52.6 (19) |
| rl_60_180 | all | partly_able | 52.9/60.9/62.1 (87) | <10/<10/<10 (10) | 55.8/67.3/67.3 (52) |
| rl_60_180 | all | not_stated | 31.8/44.1/46.9 (211) | <10/44.4/51.9 (27) | 34.4/48.0/51.2 (125) |
| rl_60_180 | all | unable | 52.6/63.2/63.2 (19) | <10 | <10/78.6/78.6 (14) |
| rl_60_180 | high conf | able | <10/52.2/65.2 (23) | <10 | <10/<10/<10 (12) |
| rl_60_180 | high conf | partly_able | 60.5/71.1/71.1 (38) | <10 | 69.6/82.6/82.6 (23) |
| rl_60_180 | high conf | not_stated | 31.8/44.1/46.9 (211) | <10/44.4/51.9 (27) | 34.4/48.0/51.2 (125) |
| rl_60_180 | high conf | unable | 52.6/63.2/63.2 (19) | <10 | <10/78.6/78.6 (14) |

_(same table, columns part 2 of 2)_

| model_id | basis | cap_s | low |
|---|---|---|---|
| cc_60_180 | all | able | <10/<10/<10 (12) |
| cc_60_180 | all | partly_able | <10/<10/<10 (13) |
| cc_60_180 | all | not_stated | 17.2/19.0/22.4 (58) |
| cc_60_180 | all | unable | <10 |
| cc_60_180 | high conf | able | <10/<10/<10 (11) |
| cc_60_180 | high conf | partly_able | <10/<10/<10 (10) |
| cc_60_180 | high conf | not_stated | 17.2/19.0/22.4 (58) |
| cc_60_180 | high conf | unable | <10 |
| rl_60_180 | all | able | <10/<10/<10 (13) |
| rl_60_180 | all | partly_able | 44.0/44.0/44.0 (25) |
| rl_60_180 | all | not_stated | 25.4/35.6/35.6 (59) |
| rl_60_180 | all | unable | <10 |
| rl_60_180 | high conf | able | <10 |
| rl_60_180 | high conf | partly_able | <10 |
| rl_60_180 | high conf | not_stated | 25.4/35.6/35.6 (59) |
| rl_60_180 | high conf | unable | <10 |

### B3.4 stated intent, raw levels

| model_id | basis | intent | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | payback_full | 140 | 118 | 151 | 17.9% (151) | 23.2% (151) | 22.5% (151) | 27.8% (151) |
| cc_60_180 | all | partial | 109 | 72 | 111 | 18.9% (111) | 24.3% (111) | 22.5% (111) | 31.5% (111) |
| cc_60_180 | all | with_delay | 107 | 92 | 110 | 20.9% (110) | 22.7% (110) | 24.5% (110) | 29.1% (110) |
| cc_60_180 | all | no_payment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | not_stated | 232 | 180 | 262 | 14.5% (262) | 17.2% (262) | 19.1% (262) | 21.8% (262) |
| cc_60_180 | high conf | payback_full | 131 | 113 | 142 | 18.3% (142) | 23.9% (142) | 23.2% (142) | 28.2% (142) |
| cc_60_180 | high conf | partial | 106 | 70 | 108 | 19.4% (108) | 25.0% (108) | 23.1% (108) | 32.4% (108) |
| cc_60_180 | high conf | with_delay | 100 | 87 | 103 | 21.4% (103) | 23.3% (103) | 25.2% (103) | 30.1% (103) |
| cc_60_180 | high conf | no_payment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | not_stated | 232 | 180 | 262 | 14.5% (262) | 17.2% (262) | 19.1% (262) | 21.8% (262) |
| rl_60_180 | all | payback_full | 55 | 36 | 55 | 40.0% (55) | 56.4% (55) | 49.1% (55) | 61.8% (55) |
| rl_60_180 | all | partial | 51 | 33 | 53 | 56.6% (53) | 66.0% (53) | 58.5% (53) | 67.9% (53) |
| rl_60_180 | all | with_delay | 74 | 43 | 74 | 45.9% (74) | 55.4% (74) | 47.3% (74) | 56.8% (74) |
| rl_60_180 | all | no_payment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | not_stated | 153 | 90 | 174 | 28.7% (174) | 40.8% (174) | 31.0% (174) | 43.7% (174) |
| rl_60_180 | high conf | payback_full | 50 | 34 | 50 | 40.0% (50) | 58.0% (50) | 50.0% (50) | 64.0% (50) |
| rl_60_180 | high conf | partial | 49 | 29 | 49 | 61.2% (49) | 71.4% (49) | 63.3% (49) | 73.5% (49) |
| rl_60_180 | high conf | with_delay | 68 | 40 | 68 | 44.1% (68) | 52.9% (68) | 44.1% (68) | 54.4% (68) |
| rl_60_180 | high conf | no_payment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | not_stated | 153 | 90 | 174 | 28.7% (174) | 40.8% (174) | 31.0% (174) | 43.7% (174) |

_(same table, columns part 2 of 2)_

| model_id | basis | intent | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | all | payback_full | 20 |
| cc_60_180 | all | partial | 16 |
| cc_60_180 | all | with_delay | 21 |
| cc_60_180 | all | no_payment | <10 |
| cc_60_180 | all | not_stated | 20 |
| cc_60_180 | high conf | payback_full | 19 |
| cc_60_180 | high conf | partial | 16 |
| cc_60_180 | high conf | with_delay | 21 |
| cc_60_180 | high conf | no_payment | <10 |
| cc_60_180 | high conf | not_stated | 20 |
| rl_60_180 | all | payback_full | 21 |
| rl_60_180 | all | partial | 21 |
| rl_60_180 | all | with_delay | 18 |
| rl_60_180 | all | no_payment | <10 |
| rl_60_180 | all | not_stated | 19 |
| rl_60_180 | high conf | payback_full | 21 |
| rl_60_180 | high conf | partial | 21 |
| rl_60_180 | high conf | with_delay | 19 |
| rl_60_180 | high conf | no_payment | <10 |
| rl_60_180 | high conf | not_stated | 19 |

### B3.5 stated intent, mapped

| model_id | basis | intent | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | pays_in_full | 140 | 118 | 151 | 17.9% (151) | 23.2% (151) | 22.5% (151) | 27.8% (151) |
| cc_60_180 | all | partly_or_later | 216 | 146 | 221 | 19.9% (221) | 23.5% (221) | 23.5% (221) | 30.3% (221) |
| cc_60_180 | all | not_stated | 232 | 180 | 262 | 14.5% (262) | 17.2% (262) | 19.1% (262) | 21.8% (262) |
| cc_60_180 | all | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | pays_in_full | 131 | 113 | 142 | 18.3% (142) | 23.9% (142) | 23.2% (142) | 28.2% (142) |
| cc_60_180 | high conf | partly_or_later | 206 | 141 | 211 | 20.4% (211) | 24.2% (211) | 24.2% (211) | 31.3% (211) |
| cc_60_180 | high conf | not_stated | 232 | 180 | 262 | 14.5% (262) | 17.2% (262) | 19.1% (262) | 21.8% (262) |
| cc_60_180 | high conf | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | pays_in_full | 55 | 36 | 55 | 40.0% (55) | 56.4% (55) | 49.1% (55) | 61.8% (55) |
| rl_60_180 | all | partly_or_later | 125 | 63 | 127 | 50.4% (127) | 59.8% (127) | 52.0% (127) | 61.4% (127) |
| rl_60_180 | all | not_stated | 153 | 90 | 174 | 28.7% (174) | 40.8% (174) | 31.0% (174) | 43.7% (174) |
| rl_60_180 | all | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | pays_in_full | 50 | 34 | 50 | 40.0% (50) | 58.0% (50) | 50.0% (50) | 64.0% (50) |
| rl_60_180 | high conf | partly_or_later | 117 | 56 | 117 | 51.3% (117) | 60.7% (117) | 52.1% (117) | 62.4% (117) |
| rl_60_180 | high conf | not_stated | 153 | 90 | 174 | 28.7% (174) | 40.8% (174) | 31.0% (174) | 43.7% (174) |
| rl_60_180 | high conf | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | intent | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | all | pays_in_full | 20 |
| cc_60_180 | all | partly_or_later | 18 |
| cc_60_180 | all | not_stated | 20 |
| cc_60_180 | all | refuses | <10 |
| cc_60_180 | high conf | pays_in_full | 19 |
| cc_60_180 | high conf | partly_or_later | 17 |
| cc_60_180 | high conf | not_stated | 20 |
| cc_60_180 | high conf | refuses | <10 |
| rl_60_180 | all | pays_in_full | 21 |
| rl_60_180 | all | partly_or_later | 19 |
| rl_60_180 | all | not_stated | 19 |
| rl_60_180 | all | refuses | <10 |
| rl_60_180 | high conf | pays_in_full | 21 |
| rl_60_180 | high conf | partly_or_later | 21 |
| rl_60_180 | high conf | not_stated | 19 |
| rl_60_180 | high conf | refuses | <10 |

### B3.6 stated intent (raw) within a3_state (cell tables: pay30_due / pay30_any / pay45_any %, (n pairs))

| model_id | basis | int_raw | All | high | moderate |
|---|---|---|---|---|---|
| cc_60_180 | all | payback_full | 17.9/23.2/27.8 (151) | 20.9/26.9/32.8 (67) | 17.1/21.4/25.7 (70) |
| cc_60_180 | all | partial | 18.9/24.3/31.5 (111) | <10/<10/34.9 (43) | <10/27.5/31.4 (51) |
| cc_60_180 | all | with_delay | 20.9/22.7/29.1 (110) | 26.9/28.8/38.5 (52) | <10/<10/21.7 (46) |
| cc_60_180 | all | no_payment | <10 | <10 | <10 |
| cc_60_180 | all | not_stated | 14.5/17.2/21.8 (262) | 14.0/16.5/24.0 (121) | 13.9/16.8/17.8 (101) |
| cc_60_180 | high conf | payback_full | 18.3/23.9/28.2 (142) | 20.6/27.0/31.7 (63) | 18.5/23.1/27.7 (65) |
| cc_60_180 | high conf | partial | 19.4/25.0/32.4 (108) | <10/<10/35.7 (42) | <10/28.0/32.0 (50) |
| cc_60_180 | high conf | with_delay | 21.4/23.3/30.1 (103) | 26.0/28.0/38.0 (50) | <10/<10/23.3 (43) |
| cc_60_180 | high conf | no_payment | <10 | <10 | <10 |
| cc_60_180 | high conf | not_stated | 14.5/17.2/21.8 (262) | 14.0/16.5/24.0 (121) | 13.9/16.8/17.8 (101) |
| rl_60_180 | all | payback_full | 40.0/56.4/61.8 (55) | <10/<10/<10 (10) | <10/53.3/60.0 (30) |
| rl_60_180 | all | partial | 56.6/66.0/67.9 (53) | <10 | 62.2/73.0/75.7 (37) |
| rl_60_180 | all | with_delay | 45.9/55.4/56.8 (74) | <10/<10/<10 (10) | 46.5/58.1/58.1 (43) |
| rl_60_180 | all | no_payment | <10 | 0 | <10 |
| rl_60_180 | all | not_stated | 28.7/40.8/43.7 (174) | <10/<10/47.6 (21) | 31.6/45.9/49.0 (98) |
| rl_60_180 | high conf | payback_full | 40.0/58.0/64.0 (50) | <10/<10/<10 (10) | <10/51.9/59.3 (27) |
| rl_60_180 | high conf | partial | 61.2/71.4/73.5 (49) | <10 | 65.7/77.1/80.0 (35) |
| rl_60_180 | high conf | with_delay | 44.1/52.9/54.4 (68) | <10 | 45.0/57.5/57.5 (40) |
| rl_60_180 | high conf | no_payment | <10 | 0 | <10 |
| rl_60_180 | high conf | not_stated | 28.7/40.8/43.7 (174) | <10/<10/47.6 (21) | 31.6/45.9/49.0 (98) |

_(same table, columns part 2 of 2)_

| model_id | basis | int_raw | low |
|---|---|---|---|
| cc_60_180 | all | payback_full | <10/<10/<10 (14) |
| cc_60_180 | all | partial | <10/<10/<10 (17) |
| cc_60_180 | all | with_delay | <10/<10/<10 (12) |
| cc_60_180 | all | no_payment | <10 |
| cc_60_180 | all | not_stated | <10/<10/25.0 (40) |
| cc_60_180 | high conf | payback_full | <10/<10/<10 (14) |
| cc_60_180 | high conf | partial | <10/<10/<10 (16) |
| cc_60_180 | high conf | with_delay | <10/<10/<10 (10) |
| cc_60_180 | high conf | no_payment | <10 |
| cc_60_180 | high conf | not_stated | <10/<10/25.0 (40) |
| rl_60_180 | all | payback_full | <10/<10/<10 (15) |
| rl_60_180 | all | partial | <10/<10/<10 (10) |
| rl_60_180 | all | with_delay | 47.6/47.6/47.6 (21) |
| rl_60_180 | all | no_payment | 0 |
| rl_60_180 | all | not_stated | 21.8/32.7/32.7 (55) |
| rl_60_180 | high conf | payback_full | <10/<10/<10 (13) |
| rl_60_180 | high conf | partial | <10 |
| rl_60_180 | high conf | with_delay | <10/<10/<10 (20) |
| rl_60_180 | high conf | no_payment | 0 |
| rl_60_180 | high conf | not_stated | 21.8/32.7/32.7 (55) |

### B3.7 stated intent (raw) within a1_state (cell tables: pay30_due / pay30_any / pay45_any %, (n pairs))

| model_id | basis | int_raw | All | high | moderate |
|---|---|---|---|---|---|
| cc_60_180 | all | payback_full | 17.9/23.2/27.8 (151) | <10/<10/<10 (14) | <10/22.2/29.6 (54) |
| cc_60_180 | all | partial | 18.9/24.3/31.5 (111) | <10/<10/<10 (16) | <10/<10/<10 (35) |
| cc_60_180 | all | with_delay | 20.9/22.7/29.1 (110) | <10/<10/<10 (20) | <10/<10/<10 (31) |
| cc_60_180 | all | no_payment | <10 | <10 | <10 |
| cc_60_180 | all | not_stated | 14.5/17.2/21.8 (262) | <10/27.0/32.4 (37) | <10/15.6/16.9 (77) |
| cc_60_180 | high conf | payback_full | 18.3/23.9/28.2 (142) | <10/<10/<10 (13) | <10/22.0/28.0 (50) |
| cc_60_180 | high conf | partial | 19.4/25.0/32.4 (108) | <10/<10/<10 (16) | <10/<10/<10 (34) |
| cc_60_180 | high conf | with_delay | 21.4/23.3/30.1 (103) | <10/<10/<10 (19) | <10/<10/<10 (29) |
| cc_60_180 | high conf | no_payment | <10 | <10 | <10 |
| cc_60_180 | high conf | not_stated | 14.5/17.2/21.8 (262) | <10/27.0/32.4 (37) | <10/15.6/16.9 (77) |
| rl_60_180 | all | payback_full | 40.0/56.4/61.8 (55) | <10 | <10 |
| rl_60_180 | all | partial | 56.6/66.0/67.9 (53) | <10 | 78.6/85.7/85.7 (14) |
| rl_60_180 | all | with_delay | 45.9/55.4/56.8 (74) | <10 | <10/<10/<10 (11) |
| rl_60_180 | all | no_payment | <10 | 0 | 0 |
| rl_60_180 | all | not_stated | 28.7/40.8/43.7 (174) | <10 | <10/40.7/48.1 (27) |
| rl_60_180 | high conf | payback_full | 40.0/58.0/64.0 (50) | <10 | <10 |
| rl_60_180 | high conf | partial | 61.2/71.4/73.5 (49) | <10 | 78.6/85.7/85.7 (14) |
| rl_60_180 | high conf | with_delay | 44.1/52.9/54.4 (68) | <10 | <10/<10/<10 (10) |
| rl_60_180 | high conf | no_payment | <10 | 0 | 0 |
| rl_60_180 | high conf | not_stated | 28.7/40.8/43.7 (174) | <10 | <10/40.7/48.1 (27) |

_(same table, columns part 2 of 2)_

| model_id | basis | int_raw | low | unknown |
|---|---|---|---|---|
| cc_60_180 | all | payback_full | <10/<10/23.3 (43) | <10/<10/<10 (40) |
| cc_60_180 | all | partial | <10/40.0/40.0 (25) | <10/<10/31.4 (35) |
| cc_60_180 | all | with_delay | <10/<10/<10 (31) | <10/<10/<10 (28) |
| cc_60_180 | all | no_payment | <10 | 0 |
| cc_60_180 | all | not_stated | 15.5/16.7/20.2 (84) | <10/<10/23.4 (64) |
| cc_60_180 | high conf | payback_full | <10/<10/23.8 (42) | <10/<10/<10 (37) |
| cc_60_180 | high conf | partial | <10/41.7/41.7 (24) | <10/<10/32.4 (34) |
| cc_60_180 | high conf | with_delay | <10/<10/<10 (29) | <10/<10/<10 (26) |
| cc_60_180 | high conf | no_payment | <10 | 0 |
| cc_60_180 | high conf | not_stated | 15.5/16.7/20.2 (84) | <10/<10/23.4 (64) |
| rl_60_180 | all | payback_full | 35.0/50.0/52.5 (40) | <10 |
| rl_60_180 | all | partial | <10/66.7/66.7 (15) | <10/50.0/55.0 (20) |
| rl_60_180 | all | with_delay | 43.6/53.8/56.4 (39) | <10/<10/<10 (21) |
| rl_60_180 | all | no_payment | <10 | <10 |
| rl_60_180 | all | not_stated | 36.4/44.9/46.7 (107) | <10/28.2/30.8 (39) |
| rl_60_180 | high conf | payback_full | 34.3/51.4/54.3 (35) | <10 |
| rl_60_180 | high conf | partial | <10/66.7/66.7 (15) | <10/62.5/68.8 (16) |
| rl_60_180 | high conf | with_delay | 40.0/48.6/51.4 (35) | <10/<10/<10 (20) |
| rl_60_180 | high conf | no_payment | <10 | <10 |
| rl_60_180 | high conf | not_stated | 36.4/44.9/46.7 (107) | <10/28.2/30.8 (39) |

### B3.8 stated intent (mapped) within a3_state (cell tables: pay30_due / pay30_any / pay45_any %, (n pairs))

| model_id | basis | int_m | All | high | moderate |
|---|---|---|---|---|---|
| cc_60_180 | all | pays_in_full | 17.9/23.2/27.8 (151) | 20.9/26.9/32.8 (67) | 17.1/21.4/25.7 (70) |
| cc_60_180 | all | partly_or_later | 19.9/23.5/30.3 (221) | 23.2/25.3/36.8 (95) | 16.5/22.7/26.8 (97) |
| cc_60_180 | all | not_stated | 14.5/17.2/21.8 (262) | 14.0/16.5/24.0 (121) | 13.9/16.8/17.8 (101) |
| cc_60_180 | all | refuses | <10 | <10 | <10 |
| cc_60_180 | high conf | pays_in_full | 18.3/23.9/28.2 (142) | 20.6/27.0/31.7 (63) | 18.5/23.1/27.7 (65) |
| cc_60_180 | high conf | partly_or_later | 20.4/24.2/31.3 (211) | 22.8/25.0/37.0 (92) | 17.2/23.7/28.0 (93) |
| cc_60_180 | high conf | not_stated | 14.5/17.2/21.8 (262) | 14.0/16.5/24.0 (121) | 13.9/16.8/17.8 (101) |
| cc_60_180 | high conf | refuses | <10 | <10 | <10 |
| rl_60_180 | all | pays_in_full | 40.0/56.4/61.8 (55) | <10/<10/<10 (10) | <10/53.3/60.0 (30) |
| rl_60_180 | all | partly_or_later | 50.4/59.8/61.4 (127) | <10/62.5/68.8 (16) | 53.8/65.0/66.2 (80) |
| rl_60_180 | all | not_stated | 28.7/40.8/43.7 (174) | <10/<10/47.6 (21) | 31.6/45.9/49.0 (98) |
| rl_60_180 | all | refuses | <10 | 0 | <10 |
| rl_60_180 | high conf | pays_in_full | 40.0/58.0/64.0 (50) | <10/<10/<10 (10) | <10/51.9/59.3 (27) |
| rl_60_180 | high conf | partly_or_later | 51.3/60.7/62.4 (117) | <10/<10/<10 (14) | 54.7/66.7/68.0 (75) |
| rl_60_180 | high conf | not_stated | 28.7/40.8/43.7 (174) | <10/<10/47.6 (21) | 31.6/45.9/49.0 (98) |
| rl_60_180 | high conf | refuses | <10 | 0 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | int_m | low |
|---|---|---|---|
| cc_60_180 | all | pays_in_full | <10/<10/<10 (14) |
| cc_60_180 | all | partly_or_later | <10/<10/<10 (29) |
| cc_60_180 | all | not_stated | <10/<10/25.0 (40) |
| cc_60_180 | all | refuses | <10 |
| cc_60_180 | high conf | pays_in_full | <10/<10/<10 (14) |
| cc_60_180 | high conf | partly_or_later | <10/<10/<10 (26) |
| cc_60_180 | high conf | not_stated | <10/<10/25.0 (40) |
| cc_60_180 | high conf | refuses | <10 |
| rl_60_180 | all | pays_in_full | <10/<10/<10 (15) |
| rl_60_180 | all | partly_or_later | 45.2/45.2/45.2 (31) |
| rl_60_180 | all | not_stated | 21.8/32.7/32.7 (55) |
| rl_60_180 | all | refuses | 0 |
| rl_60_180 | high conf | pays_in_full | <10/<10/<10 (13) |
| rl_60_180 | high conf | partly_or_later | 46.4/46.4/46.4 (28) |
| rl_60_180 | high conf | not_stated | 21.8/32.7/32.7 (55) |
| rl_60_180 | high conf | refuses | 0 |

## Part C - stated vs observed (consistency, not truth)

Income = larger of internal and bureau salary (A1's rule); tables end 2026-08-31.

### C1 share of conversations whose CIF has income, by month relative to the call month

| model_id | claim | conversations | -6 | -5 | -4 | -3 | -2 |
|---|---|---|---|---|---|---|---|
| cc_60_180 | (all conversations) | 597 | 45.6% (597) | 43.6% (597) | 45.7% (597) | 43.7% (597) | 40.9% (597) |
| cc_60_180 | reason=lost_employment | 31 | 35.5% (31) | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | 27 | 40.7% (27) | 48.1% (27) | <10 | 44.4% (27) | 48.1% (27) |
| cc_60_180 | reason=has_employment | 89 | 61.8% (89) | 56.2% (89) | 51.7% (89) | 51.7% (89) | 50.6% (89) |
| cc_60_180 | reason=increased_obligations | 43 | 55.8% (43) | 39.5% (43) | 41.9% (43) | 39.5% (43) | 44.2% (43) |
| cc_60_180 | capacity=none | 21 | 66.7% (21) | 61.9% (21) | 57.1% (21) | 52.4% (21) | 61.9% (21) |
| cc_60_180 | capacity=full | 88 | 45.5% (88) | 44.3% (88) | 47.7% (88) | 43.2% (88) | 40.9% (88) |
| rl_60_180 | (all conversations) | 335 | 38.5% (335) | 27.5% (335) | 29.0% (335) | 20.0% (335) | 20.6% (335) |
| rl_60_180 | reason=lost_employment | 50 | 54.0% (50) | 34.0% (50) | 38.0% (50) | <10 | 0.0% (50) |
| rl_60_180 | reason=reduced_employment | 18 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=has_employment | 42 | 47.6% (42) | 38.1% (42) | 45.2% (42) | 35.7% (42) | 33.3% (42) |
| rl_60_180 | reason=increased_obligations | 27 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | 19 | 63.2% (19) | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | 41 | 29.3% (41) | 29.3% (41) | 24.4% (41) | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | claim | -1 | +0 | +1 | +2 |
|---|---|---|---|---|---|
| cc_60_180 | (all conversations) | 42.2% (597) | 43.2% (597) | 43.6% (597) | 39.7% (526) |
| cc_60_180 | reason=lost_employment | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | 51.9% (27) | 44.4% (27) | 40.7% (27) | <10 |
| cc_60_180 | reason=has_employment | 52.8% (89) | 49.4% (89) | 51.7% (89) | 51.2% (80) |
| cc_60_180 | reason=increased_obligations | 39.5% (43) | 32.6% (43) | 34.9% (43) | 35.1% (37) |
| cc_60_180 | capacity=none | 61.9% (21) | <10 | <10 | <10 |
| cc_60_180 | capacity=full | 44.3% (88) | 42.0% (88) | 50.0% (88) | 42.9% (77) |
| rl_60_180 | (all conversations) | 26.9% (335) | 27.5% (335) | 28.7% (335) | 30.4% (286) |
| rl_60_180 | reason=lost_employment | <10 | <10 | 24.0% (50) | 30.8% (39) |
| rl_60_180 | reason=reduced_employment | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=has_employment | 50.0% (42) | 50.0% (42) | 45.2% (42) | 51.4% (35) |
| rl_60_180 | reason=increased_obligations | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | <10 | <10 | 31.7% (41) | 40.0% (35) |

### C2 claim x income class x CASA with us (conversations)

| model_id | claim | casa_with_us | conversations | income_stopped | income_dropped | income_continues |
|---|---|---|---|---|---|---|
| cc_60_180 | (all conversations) | has_casa | 576 | 108 (18.8%) | 33 (5.7%) | 255 (44.3%) |
| cc_60_180 | (all conversations) | no_casa | 21 | <10 (<10) | <10 (<10) | <10 (<10) |
| cc_60_180 | reason=lost_employment | has_casa | 31 | <10 (<10) | <10 (<10) | <10 (<10) |
| cc_60_180 | reason=reduced_employment | has_casa | 25 | <10 (<10) | 0 | 13 (52.0%) |
| cc_60_180 | reason=reduced_employment | no_casa | <10 | 0 | 0 | <10 (<10) |
| cc_60_180 | reason=has_employment | has_casa | 85 | 19 (22.4%) | <10 (<10) | 48 (56.5%) |
| cc_60_180 | reason=has_employment | no_casa | <10 | <10 (<10) | 0 | 0 |
| cc_60_180 | reason=increased_obligations | has_casa | 41 | <10 (<10) | 0 | 17 (41.5%) |
| cc_60_180 | reason=increased_obligations | no_casa | <10 | 0 | 0 | <10 (<10) |
| cc_60_180 | capacity=none | has_casa | 21 | <10 (<10) | <10 (<10) | 10 (47.6%) |
| cc_60_180 | capacity=full | has_casa | 84 | 15 (17.9%) | <10 (<10) | 38 (45.2%) |
| cc_60_180 | capacity=full | no_casa | <10 | <10 (<10) | 0 | 0 |
| rl_60_180 | (all conversations) | has_casa | 326 | 60 (18.4%) | 27 (8.3%) | 96 (29.4%) |
| rl_60_180 | (all conversations) | no_casa | <10 | 0 | 0 | 0 |
| rl_60_180 | reason=lost_employment | has_casa | 49 | 22 (44.9%) | <10 (<10) | <10 (<10) |
| rl_60_180 | reason=lost_employment | no_casa | <10 | 0 | 0 | 0 |
| rl_60_180 | reason=reduced_employment | has_casa | 18 | <10 (<10) | <10 (<10) | <10 (<10) |
| rl_60_180 | reason=has_employment | has_casa | 42 | <10 (<10) | 10 (23.8%) | 17 (40.5%) |
| rl_60_180 | reason=increased_obligations | has_casa | 26 | <10 (<10) | <10 (<10) | <10 (<10) |
| rl_60_180 | reason=increased_obligations | no_casa | <10 | 0 | 0 | 0 |
| rl_60_180 | capacity=none | has_casa | 19 | 10 (52.6%) | <10 (<10) | <10 (<10) |
| rl_60_180 | capacity=full | has_casa | 39 | <10 (<10) | <10 (<10) | <10 (<10) |
| rl_60_180 | capacity=full | no_casa | <10 | 0 | 0 | 0 |

_(same table, columns part 2 of 2)_

| model_id | claim | casa_with_us | income_only_m2 | never_visible | not_covered |
|---|---|---|---|---|---|
| cc_60_180 | (all conversations) | has_casa | <10 (<10) | 178 (30.9%) | 0 |
| cc_60_180 | (all conversations) | no_casa | 0 | <10 (<10) | 0 |
| cc_60_180 | reason=lost_employment | has_casa | 0 | 14 (45.2%) | 0 |
| cc_60_180 | reason=reduced_employment | has_casa | <10 (<10) | <10 (<10) | 0 |
| cc_60_180 | reason=reduced_employment | no_casa | 0 | 0 | 0 |
| cc_60_180 | reason=has_employment | has_casa | 0 | 16 (18.8%) | 0 |
| cc_60_180 | reason=has_employment | no_casa | 0 | <10 (<10) | 0 |
| cc_60_180 | reason=increased_obligations | has_casa | 0 | 16 (39.0%) | 0 |
| cc_60_180 | reason=increased_obligations | no_casa | 0 | <10 (<10) | 0 |
| cc_60_180 | capacity=none | has_casa | 0 | <10 (<10) | 0 |
| cc_60_180 | capacity=full | has_casa | 0 | 27 (32.1%) | 0 |
| cc_60_180 | capacity=full | no_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | (all conversations) | has_casa | <10 (<10) | 142 (43.6%) | 0 |
| rl_60_180 | (all conversations) | no_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | reason=lost_employment | has_casa | 0 | 18 (36.7%) | 0 |
| rl_60_180 | reason=lost_employment | no_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | reason=reduced_employment | has_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | reason=has_employment | has_casa | 0 | 11 (26.2%) | 0 |
| rl_60_180 | reason=increased_obligations | has_casa | 0 | 14 (53.8%) | 0 |
| rl_60_180 | reason=increased_obligations | no_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | capacity=none | has_casa | 0 | <10 (<10) | 0 |
| rl_60_180 | capacity=full | has_casa | 0 | 21 (53.8%) | 0 |
| rl_60_180 | capacity=full | no_casa | 0 | <10 (<10) | 0 |

### C3 payment by claim x income class

| model_id | claim | income_class | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | (all conversations) | income_stopped | 110 | 62 | 126 | 19.0% (126) | 28.6% (126) | 23.8% (126) |
| cc_60_180 | (all conversations) | income_dropped | 35 | 19 | 38 | <10 | <10 | <10 |
| cc_60_180 | (all conversations) | income_continues | 263 | 148 | 282 | 14.2% (282) | 17.0% (282) | 18.4% (282) |
| cc_60_180 | (all conversations) | income_only_m2 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | (all conversations) | never_visible | 187 | 109 | 195 | 20.5% (195) | 21.5% (195) | 25.6% (195) |
| cc_60_180 | reason=lost_employment | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=lost_employment | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=lost_employment | income_continues | <10 | <10 | 10 | <10 | <10 | <10 |
| cc_60_180 | reason=lost_employment | never_visible | 14 | 11 | 14 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_continues | 15 | 15 | 16 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_only_m2 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | never_visible | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=has_employment | income_stopped | 21 | 15 | 23 | <10 | 43.5% (23) | <10 |
| cc_60_180 | reason=has_employment | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=has_employment | income_continues | 48 | 39 | 48 | 27.1% (48) | 33.3% (48) | 31.2% (48) |
| cc_60_180 | reason=has_employment | never_visible | 18 | 17 | 19 | <10 | <10 | <10 |
| cc_60_180 | reason=increased_obligations | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | reason=increased_obligations | income_continues | 18 | 15 | 18 | <10 | <10 | <10 |
| cc_60_180 | reason=increased_obligations | never_visible | 17 | 14 | 18 | 0.0% (18) | <10 | <10 |
| cc_60_180 | capacity=none | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | income_continues | 10 | <10 | 10 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | never_visible | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | income_stopped | 17 | 17 | 21 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | income_continues | 38 | 34 | 41 | <10 | 26.8% (41) | 24.4% (41) |
| cc_60_180 | capacity=full | never_visible | 29 | 28 | 33 | <10 | <10 | <10 |
| rl_60_180 | (all conversations) | income_stopped | 60 | 25 | 60 | 36.7% (60) | 51.7% (60) | 41.7% (60) |
| rl_60_180 | (all conversations) | income_dropped | 27 | <10 | 27 | 40.7% (27) | 51.9% (27) | 44.4% (27) |
| rl_60_180 | (all conversations) | income_continues | 96 | 46 | 97 | 42.3% (97) | 63.9% (97) | 45.4% (97) |
| rl_60_180 | (all conversations) | income_only_m2 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | (all conversations) | never_visible | 151 | 76 | 173 | 36.4% (173) | 41.6% (173) | 38.7% (173) |
| rl_60_180 | reason=lost_employment | income_stopped | 22 | <10 | 22 | 50.0% (22) | 59.1% (22) | 50.0% (22) |
| rl_60_180 | reason=lost_employment | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=lost_employment | income_continues | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=lost_employment | never_visible | 19 | 11 | 19 | <10 | <10 | <10 |
| rl_60_180 | reason=reduced_employment | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=reduced_employment | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=reduced_employment | income_continues | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=reduced_employment | never_visible | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=has_employment | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=has_employment | income_dropped | 10 | <10 | 10 | <10 | <10 | <10 |
| rl_60_180 | reason=has_employment | income_continues | 17 | 14 | 18 | 66.7% (18) | 83.3% (18) | 66.7% (18) |
| rl_60_180 | reason=has_employment | never_visible | 11 | <10 | 11 | <10 | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_continues | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | reason=increased_obligations | never_visible | 15 | 11 | 17 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | income_stopped | 10 | <10 | 10 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | income_continues | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | never_visible | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | income_stopped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | income_dropped | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | income_continues | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity=full | never_visible | 23 | 16 | 23 | 43.5% (23) | 47.8% (23) | 56.5% (23) |

_(same table, columns part 2 of 2)_

| model_id | claim | income_class | pay45_any | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | (all conversations) | income_stopped | 34.9% (126) | 22 |
| cc_60_180 | (all conversations) | income_dropped | <10 | <10 |
| cc_60_180 | (all conversations) | income_continues | 22.7% (282) | 19 |
| cc_60_180 | (all conversations) | income_only_m2 | <10 | <10 |
| cc_60_180 | (all conversations) | never_visible | 27.2% (195) | 18 |
| cc_60_180 | reason=lost_employment | income_stopped | <10 | <10 |
| cc_60_180 | reason=lost_employment | income_dropped | <10 | - |
| cc_60_180 | reason=lost_employment | income_continues | <10 | <10 |
| cc_60_180 | reason=lost_employment | never_visible | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_stopped | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_continues | <10 | <10 |
| cc_60_180 | reason=reduced_employment | income_only_m2 | <10 | <10 |
| cc_60_180 | reason=reduced_employment | never_visible | <10 | <10 |
| cc_60_180 | reason=has_employment | income_stopped | 52.2% (23) | 25 |
| cc_60_180 | reason=has_employment | income_dropped | <10 | - |
| cc_60_180 | reason=has_employment | income_continues | 39.6% (48) | 17 |
| cc_60_180 | reason=has_employment | never_visible | <10 | <10 |
| cc_60_180 | reason=increased_obligations | income_stopped | <10 | <10 |
| cc_60_180 | reason=increased_obligations | income_continues | <10 | <10 |
| cc_60_180 | reason=increased_obligations | never_visible | <10 | <10 |
| cc_60_180 | capacity=none | income_stopped | <10 | - |
| cc_60_180 | capacity=none | income_dropped | <10 | - |
| cc_60_180 | capacity=none | income_continues | <10 | <10 |
| cc_60_180 | capacity=none | never_visible | <10 | <10 |
| cc_60_180 | capacity=full | income_stopped | <10 | <10 |
| cc_60_180 | capacity=full | income_dropped | <10 | <10 |
| cc_60_180 | capacity=full | income_continues | 34.1% (41) | 19 |
| cc_60_180 | capacity=full | never_visible | <10 | <10 |
| rl_60_180 | (all conversations) | income_stopped | 53.3% (60) | 13 |
| rl_60_180 | (all conversations) | income_dropped | 55.6% (27) | 19 |
| rl_60_180 | (all conversations) | income_continues | 66.0% (97) | 21 |
| rl_60_180 | (all conversations) | income_only_m2 | <10 | - |
| rl_60_180 | (all conversations) | never_visible | 45.1% (173) | 17 |
| rl_60_180 | reason=lost_employment | income_stopped | 59.1% (22) | 13 |
| rl_60_180 | reason=lost_employment | income_dropped | <10 | - |
| rl_60_180 | reason=lost_employment | income_continues | <10 | <10 |
| rl_60_180 | reason=lost_employment | never_visible | <10 | <10 |
| rl_60_180 | reason=reduced_employment | income_stopped | <10 | <10 |
| rl_60_180 | reason=reduced_employment | income_dropped | <10 | - |
| rl_60_180 | reason=reduced_employment | income_continues | <10 | <10 |
| rl_60_180 | reason=reduced_employment | never_visible | <10 | <10 |
| rl_60_180 | reason=has_employment | income_stopped | <10 | <10 |
| rl_60_180 | reason=has_employment | income_dropped | <10 | <10 |
| rl_60_180 | reason=has_employment | income_continues | 83.3% (18) | 21 |
| rl_60_180 | reason=has_employment | never_visible | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_stopped | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_dropped | <10 | <10 |
| rl_60_180 | reason=increased_obligations | income_continues | <10 | <10 |
| rl_60_180 | reason=increased_obligations | never_visible | <10 | <10 |
| rl_60_180 | capacity=none | income_stopped | <10 | <10 |
| rl_60_180 | capacity=none | income_dropped | <10 | <10 |
| rl_60_180 | capacity=none | income_continues | <10 | <10 |
| rl_60_180 | capacity=none | never_visible | <10 | <10 |
| rl_60_180 | capacity=full | income_stopped | <10 | <10 |
| rl_60_180 | capacity=full | income_dropped | <10 | - |
| rl_60_180 | capacity=full | income_continues | <10 | <10 |
| rl_60_180 | capacity=full | never_visible | 60.9% (23) | 16 |

### C4.1 stated capacity none / full: CASA balance at the prior month end vs one month's due

| model_id | claim | casa_balance_vs_due | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | capacity=none | balance>=due | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | balance<due | 15 | 14 | 15 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | no_balance_row | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | balance>=due | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | balance<due | 59 | 57 | 65 | 20.0% (65) | 26.2% (65) | 21.5% (65) | 29.2% (65) |
| cc_60_180 | capacity=full | no_balance_row | 23 | 20 | 26 | <10 | <10 | <10 | 42.3% (26) |
| rl_60_180 | capacity=none | balance<due | 19 | 13 | 19 | 52.6% (19) | 63.2% (19) | 52.6% (19) | 63.2% (19) |
| rl_60_180 | capacity=full | balance<due | 38 | 26 | 38 | 36.8% (38) | 55.3% (38) | 47.4% (38) | 60.5% (38) |
| rl_60_180 | capacity=full | no_balance_row | <10 | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | claim | casa_balance_vs_due | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | capacity=none | balance>=due | - |
| cc_60_180 | capacity=none | balance<due | <10 |
| cc_60_180 | capacity=none | no_balance_row | - |
| cc_60_180 | capacity=full | balance>=due | <10 |
| cc_60_180 | capacity=full | balance<due | 18 |
| cc_60_180 | capacity=full | no_balance_row | 25 |
| rl_60_180 | capacity=none | balance<due | 13 |
| rl_60_180 | capacity=full | balance<due | 21 |
| rl_60_180 | capacity=full | no_balance_row | <10 |

### C4.2 stated capacity none / full: CASA inflow in the call month

| model_id | claim | casa_inflow_call_month | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | capacity=none | inflow>0 | 12 | 11 | 12 | <10 | <10 | <10 |
| cc_60_180 | capacity=none | no_inflow | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity=full | inflow>0 | 56 | 56 | 65 | 23.1% (65) | 30.8% (65) | 26.2% (65) |
| cc_60_180 | capacity=full | no_inflow | 32 | 29 | 34 | <10 | <10 | <10 |
| rl_60_180 | capacity=none | inflow>0 | 19 | 13 | 19 | 52.6% (19) | 63.2% (19) | 52.6% (19) |
| rl_60_180 | capacity=full | inflow>0 | 32 | 23 | 32 | 40.6% (32) | 62.5% (32) | 56.2% (32) |
| rl_60_180 | capacity=full | no_inflow | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | claim | casa_inflow_call_month | pay45_any | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | capacity=none | inflow>0 | <10 | <10 |
| cc_60_180 | capacity=none | no_inflow | <10 | <10 |
| cc_60_180 | capacity=full | inflow>0 | 35.4% (65) | 18 |
| cc_60_180 | capacity=full | no_inflow | <10 | <10 |
| rl_60_180 | capacity=none | inflow>0 | 63.2% (19) | 13 |
| rl_60_180 | capacity=full | inflow>0 | 71.9% (32) | 21 |
| rl_60_180 | capacity=full | no_inflow | <10 | <10 |

## Part D - where UC2 has no evidence

### D1.1 a1_state = unknown: stated capacity

| model_id | basis | capacity | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | able | 21 | 21 | 25 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | partly_able | 45 | 34 | 47 | <10 | 23.4% (47) | 25.5% (47) | 38.3% (47) |
| cc_60_180 | all | not_stated | 85 | 60 | 94 | 11.7% (94) | 13.8% (94) | 18.1% (94) | 20.2% (94) |
| cc_60_180 | all | unable | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | able | 13 | 13 | 14 | 0.0% (14) | 0.0% (14) | <10 | <10 |
| cc_60_180 | high conf | partly_able | 21 | 18 | 23 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | not_stated | 85 | 60 | 94 | 11.7% (94) | 13.8% (94) | 18.1% (94) | 20.2% (94) |
| cc_60_180 | high conf | unable | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | able | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | partly_able | 24 | 16 | 26 | 38.5% (26) | 42.3% (26) | 38.5% (26) | 42.3% (26) |
| rl_60_180 | all | not_stated | 44 | 24 | 46 | <10 | 30.4% (46) | 23.9% (46) | 34.8% (46) |
| rl_60_180 | all | unable | 10 | <10 | 10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | able | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | partly_able | 13 | <10 | 13 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | not_stated | 44 | 24 | 46 | <10 | 30.4% (46) | 23.9% (46) | 34.8% (46) |
| rl_60_180 | high conf | unable | 10 | <10 | 10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | capacity | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | all | able | <10 |
| cc_60_180 | all | partly_able | 25 |
| cc_60_180 | all | not_stated | 19 |
| cc_60_180 | all | unable | - |
| cc_60_180 | high conf | able | <10 |
| cc_60_180 | high conf | partly_able | <10 |
| cc_60_180 | high conf | not_stated | 19 |
| cc_60_180 | high conf | unable | - |
| rl_60_180 | all | able | <10 |
| rl_60_180 | all | partly_able | 21 |
| rl_60_180 | all | not_stated | 23 |
| rl_60_180 | all | unable | <10 |
| rl_60_180 | high conf | able | <10 |
| rl_60_180 | high conf | partly_able | <10 |
| rl_60_180 | high conf | not_stated | 23 |
| rl_60_180 | high conf | unable | <10 |

### D1.2 a1_state = unknown: stated reason

| model_id | basis | reason | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | (not detected) | 96 | 63 | 108 | 11.1% (108) | 14.8% (108) | 16.7% (108) | 20.4% (108) |
| cc_60_180 | all | has_employment | 25 | 21 | 27 | <10 | <10 | <10 | 44.4% (27) |
| cc_60_180 | all | increased_obligations | 14 | 12 | 15 | 0.0% (15) | 0.0% (15) | <10 | <10 |
| cc_60_180 | all | lost_employment | 10 | <10 | 10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | reduced_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | (not detected) | 96 | 63 | 108 | 11.1% (108) | 14.8% (108) | 16.7% (108) | 20.4% (108) |
| cc_60_180 | high conf | has_employment | 23 | 20 | 25 | <10 | <10 | <10 | 40.0% (25) |
| cc_60_180 | high conf | increased_obligations | 13 | 12 | 14 | 0.0% (14) | 0.0% (14) | <10 | <10 |
| cc_60_180 | high conf | lost_employment | 10 | <10 | 10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | reduced_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | (not detected) | 44 | 26 | 46 | 21.7% (46) | 34.8% (46) | 30.4% (46) | 43.5% (46) |
| rl_60_180 | all | has_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | increased_obligations | <10 | <10 | 10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | lost_employment | 22 | <10 | 22 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | reduced_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | (not detected) | 44 | 26 | 46 | 21.7% (46) | 34.8% (46) | 30.4% (46) | 43.5% (46) |
| rl_60_180 | high conf | has_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | increased_obligations | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | lost_employment | 22 | <10 | 22 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | reduced_employment | <10 | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | reason | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | all | (not detected) | 19 |
| cc_60_180 | all | has_employment | 24 |
| cc_60_180 | all | increased_obligations | <10 |
| cc_60_180 | all | lost_employment | <10 |
| cc_60_180 | all | reduced_employment | <10 |
| cc_60_180 | high conf | (not detected) | 19 |
| cc_60_180 | high conf | has_employment | 24 |
| cc_60_180 | high conf | increased_obligations | <10 |
| cc_60_180 | high conf | lost_employment | <10 |
| cc_60_180 | high conf | reduced_employment | <10 |
| rl_60_180 | all | (not detected) | 23 |
| rl_60_180 | all | has_employment | <10 |
| rl_60_180 | all | increased_obligations | <10 |
| rl_60_180 | all | lost_employment | <10 |
| rl_60_180 | all | reduced_employment | <10 |
| rl_60_180 | high conf | (not detected) | 23 |
| rl_60_180 | high conf | has_employment | <10 |
| rl_60_180 | high conf | increased_obligations | <10 |
| rl_60_180 | high conf | lost_employment | <10 |
| rl_60_180 | high conf | reduced_employment | <10 |

### D1.3 AUC among Unknown conversation holders

| model_id | basis | order | pairs_with_45d_outcome | pay45_any_positives | AUC_pay45_any | AUC_pay30_due |
|---|---|---|---|---|---|---|
| cc_60_180 | all | able > partly_able > not_stated > unable | 167 | 43 | 0.572 | 0.542 |
| cc_60_180 | high conf | able > partly_able > not_stated > unable | 132 | 28 | 0.514 | 0.502 |
| rl_60_180 | all | able > partly_able > not_stated > unable | 89 | 40 | 0.528 | 0.493 |
| rl_60_180 | high conf | able > partly_able > not_stated > unable | 73 | 34 | 0.533 | 0.477 |

### D2.1 a3_state = low: a3_group x stated intent

| model_id | basis | a3_group | intent | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | no_promise | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | partly_or_later | 16 | 12 | 16 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | not_stated | 22 | 17 | 22 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | partly_or_later | 13 | <10 | 13 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | not_stated | 16 | 13 | 18 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | 15 | 11 | 15 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | not_stated | 22 | 17 | 22 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | refuses | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | partly_or_later | 11 | <10 | 11 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | not_stated | 16 | 13 | 18 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | partly_or_later | 13 | 12 | 14 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | not_stated | 42 | 25 | 47 | 25.5% (47) | 38.3% (47) | 25.5% (47) | 38.3% (47) |
| rl_60_180 | all | promise_level | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | partly_or_later | 17 | <10 | 17 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | not_stated | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | partly_or_later | 11 | <10 | 11 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | not_stated | 42 | 25 | 47 | 25.5% (47) | 38.3% (47) | 25.5% (47) | 38.3% (47) |
| rl_60_180 | high conf | promise_level | pays_in_full | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | 17 | <10 | 17 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | not_stated | <10 | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | a3_group | intent | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | all | no_promise | pays_in_full | <10 |
| cc_60_180 | all | no_promise | partly_or_later | <10 |
| cc_60_180 | all | no_promise | not_stated | <10 |
| cc_60_180 | all | no_promise | refuses | - |
| cc_60_180 | all | promise_level | pays_in_full | <10 |
| cc_60_180 | all | promise_level | partly_or_later | <10 |
| cc_60_180 | all | promise_level | not_stated | <10 |
| cc_60_180 | high conf | no_promise | pays_in_full | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | <10 |
| cc_60_180 | high conf | no_promise | not_stated | <10 |
| cc_60_180 | high conf | no_promise | refuses | - |
| cc_60_180 | high conf | promise_level | pays_in_full | <10 |
| cc_60_180 | high conf | promise_level | partly_or_later | <10 |
| cc_60_180 | high conf | promise_level | not_stated | <10 |
| rl_60_180 | all | no_promise | pays_in_full | <10 |
| rl_60_180 | all | no_promise | partly_or_later | <10 |
| rl_60_180 | all | no_promise | not_stated | 14 |
| rl_60_180 | all | promise_level | pays_in_full | <10 |
| rl_60_180 | all | promise_level | partly_or_later | <10 |
| rl_60_180 | all | promise_level | not_stated | - |
| rl_60_180 | high conf | no_promise | pays_in_full | <10 |
| rl_60_180 | high conf | no_promise | partly_or_later | <10 |
| rl_60_180 | high conf | no_promise | not_stated | 14 |
| rl_60_180 | high conf | promise_level | pays_in_full | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | <10 |
| rl_60_180 | high conf | promise_level | not_stated | - |

### D2.2 a3_state = low: a3_group x repayment specifics

| model_id | basis | a3_group | specifics | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | no_promise | amount_or_date_named | 22 | 15 | 22 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | none_named | 26 | 21 | 26 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | none_named | 30 | 21 | 32 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | amount_or_date_named | 22 | 15 | 22 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | none_named | 26 | 21 | 26 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | none_named | 30 | 21 | 32 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | amount_or_date_named | 13 | 12 | 14 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | none_named | 48 | 29 | 53 | 26.4% (53) | 37.7% (53) | 26.4% (53) | 37.7% (53) |
| rl_60_180 | all | promise_level | amount_or_date_named | 15 | <10 | 15 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | none_named | 19 | 10 | 19 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | amount_or_date_named | 11 | <10 | 11 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | none_named | 48 | 29 | 53 | 26.4% (53) | 37.7% (53) | 26.4% (53) | 37.7% (53) |
| rl_60_180 | high conf | promise_level | amount_or_date_named | 12 | <10 | 12 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | none_named | 19 | 10 | 19 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | a3_group | specifics | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | all | no_promise | amount_or_date_named | <10 |
| cc_60_180 | all | no_promise | none_named | <10 |
| cc_60_180 | all | promise_level | amount_or_date_named | <10 |
| cc_60_180 | all | promise_level | none_named | <10 |
| cc_60_180 | high conf | no_promise | amount_or_date_named | <10 |
| cc_60_180 | high conf | no_promise | none_named | <10 |
| cc_60_180 | high conf | promise_level | amount_or_date_named | <10 |
| cc_60_180 | high conf | promise_level | none_named | <10 |
| rl_60_180 | all | no_promise | amount_or_date_named | <10 |
| rl_60_180 | all | no_promise | none_named | 14 |
| rl_60_180 | all | promise_level | amount_or_date_named | <10 |
| rl_60_180 | all | promise_level | none_named | <10 |
| rl_60_180 | high conf | no_promise | amount_or_date_named | <10 |
| rl_60_180 | high conf | no_promise | none_named | 14 |
| rl_60_180 | high conf | promise_level | amount_or_date_named | <10 |
| rl_60_180 | high conf | promise_level | none_named | <10 |

### D2.3 a3_state = low: a3_group x intent x specifics

| model_id | basis | a3_group | intent | specifics | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due |
|---|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | all | no_promise | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | partly_or_later | amount_or_date_named | 14 | 11 | 14 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | not_stated | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | not_stated | none_named | 21 | 16 | 21 | <10 | <10 | <10 |
| cc_60_180 | all | no_promise | refuses | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | partly_or_later | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | all | promise_level | not_stated | none_named | 16 | 13 | 18 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | amount_or_date_named | 13 | 10 | 13 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | not_stated | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | not_stated | none_named | 21 | 16 | 21 | <10 | <10 | <10 |
| cc_60_180 | high conf | no_promise | refuses | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | partly_or_later | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | high conf | promise_level | not_stated | none_named | 16 | 13 | 18 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | partly_or_later | amount_or_date_named | 10 | <10 | 10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | no_promise | not_stated | none_named | 42 | 25 | 47 | 25.5% (47) | 38.3% (47) | 25.5% (47) |
| rl_60_180 | all | promise_level | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | partly_or_later | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | all | promise_level | not_stated | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | partly_or_later | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | no_promise | not_stated | none_named | 42 | 25 | 47 | 25.5% (47) | 38.3% (47) | 25.5% (47) |
| rl_60_180 | high conf | promise_level | pays_in_full | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | pays_in_full | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | amount_or_date_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | none_named | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | high conf | promise_level | not_stated | none_named | <10 | <10 | <10 | <10 | <10 | <10 |

_(same table, columns part 2 of 2)_

| model_id | basis | a3_group | intent | specifics | pay45_any | median_days_to_pay |
|---|---|---|---|---|---|---|
| cc_60_180 | all | no_promise | pays_in_full | amount_or_date_named | <10 | - |
| cc_60_180 | all | no_promise | pays_in_full | none_named | <10 | <10 |
| cc_60_180 | all | no_promise | partly_or_later | amount_or_date_named | <10 | <10 |
| cc_60_180 | all | no_promise | partly_or_later | none_named | <10 | - |
| cc_60_180 | all | no_promise | not_stated | amount_or_date_named | <10 | - |
| cc_60_180 | all | no_promise | not_stated | none_named | <10 | <10 |
| cc_60_180 | all | no_promise | refuses | amount_or_date_named | <10 | - |
| cc_60_180 | all | promise_level | pays_in_full | amount_or_date_named | <10 | <10 |
| cc_60_180 | all | promise_level | pays_in_full | none_named | <10 | - |
| cc_60_180 | all | promise_level | partly_or_later | amount_or_date_named | <10 | - |
| cc_60_180 | all | promise_level | partly_or_later | none_named | <10 | <10 |
| cc_60_180 | all | promise_level | not_stated | none_named | <10 | <10 |
| cc_60_180 | high conf | no_promise | pays_in_full | amount_or_date_named | <10 | - |
| cc_60_180 | high conf | no_promise | pays_in_full | none_named | <10 | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | amount_or_date_named | <10 | <10 |
| cc_60_180 | high conf | no_promise | partly_or_later | none_named | <10 | - |
| cc_60_180 | high conf | no_promise | not_stated | amount_or_date_named | <10 | - |
| cc_60_180 | high conf | no_promise | not_stated | none_named | <10 | <10 |
| cc_60_180 | high conf | no_promise | refuses | amount_or_date_named | <10 | - |
| cc_60_180 | high conf | promise_level | pays_in_full | amount_or_date_named | <10 | <10 |
| cc_60_180 | high conf | promise_level | pays_in_full | none_named | <10 | - |
| cc_60_180 | high conf | promise_level | partly_or_later | amount_or_date_named | <10 | - |
| cc_60_180 | high conf | promise_level | partly_or_later | none_named | <10 | <10 |
| cc_60_180 | high conf | promise_level | not_stated | none_named | <10 | <10 |
| rl_60_180 | all | no_promise | pays_in_full | amount_or_date_named | <10 | <10 |
| rl_60_180 | all | no_promise | pays_in_full | none_named | <10 | - |
| rl_60_180 | all | no_promise | partly_or_later | amount_or_date_named | <10 | <10 |
| rl_60_180 | all | no_promise | partly_or_later | none_named | <10 | <10 |
| rl_60_180 | all | no_promise | not_stated | none_named | 38.3% (47) | 14 |
| rl_60_180 | all | promise_level | pays_in_full | amount_or_date_named | <10 | <10 |
| rl_60_180 | all | promise_level | pays_in_full | none_named | <10 | <10 |
| rl_60_180 | all | promise_level | partly_or_later | amount_or_date_named | <10 | <10 |
| rl_60_180 | all | promise_level | partly_or_later | none_named | <10 | <10 |
| rl_60_180 | all | promise_level | not_stated | none_named | <10 | - |
| rl_60_180 | high conf | no_promise | pays_in_full | amount_or_date_named | <10 | <10 |
| rl_60_180 | high conf | no_promise | pays_in_full | none_named | <10 | - |
| rl_60_180 | high conf | no_promise | partly_or_later | amount_or_date_named | <10 | <10 |
| rl_60_180 | high conf | no_promise | partly_or_later | none_named | <10 | <10 |
| rl_60_180 | high conf | no_promise | not_stated | none_named | 38.3% (47) | 14 |
| rl_60_180 | high conf | promise_level | pays_in_full | amount_or_date_named | <10 | <10 |
| rl_60_180 | high conf | promise_level | pays_in_full | none_named | <10 | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | amount_or_date_named | <10 | <10 |
| rl_60_180 | high conf | promise_level | partly_or_later | none_named | <10 | <10 |
| rl_60_180 | high conf | promise_level | not_stated | none_named | <10 | - |

### D3 month-end view, a1_state = unknown, latest stated capacity of the prior 90 days, 1-month outcomes

| model_id | basis | latest stated capacity (prior 90 d) | account_months | paid_due_1m | paid_any_1m | 2026-05 n |
|---|---|---|---|---|---|---|
| cc_60_180 | all | able | 45 | 22.2% (45) | 22.2% (45) | 19 |
| cc_60_180 | all | partly_able | 163 | 16.6% (163) | 24.5% (163) | 40 |
| cc_60_180 | all | not_stated | 176 | 17.6% (176) | 21.6% (176) | 51 |
| cc_60_180 | all | unable | 78 | 12.8% (78) | 15.4% (78) | <10 |
| cc_60_180 | all | no_reading | 26,718 | 7.8% (26,718) | 8.8% (26,718) | 8,150 |
| cc_60_180 | high conf | able | 29 | <10 | <10 | 12 |
| cc_60_180 | high conf | partly_able | 57 | 17.5% (57) | 24.6% (57) | 20 |
| cc_60_180 | high conf | not_stated | 238 | 19.3% (238) | 23.9% (238) | 64 |
| cc_60_180 | high conf | unable | 95 | 12.6% (95) | 16.8% (95) | 11 |
| cc_60_180 | high conf | no_reading | 26,761 | 7.8% (26,761) | 8.8% (26,761) | 8,162 |
| rl_60_180 | all | able | 28 | <10 | <10 | 13 |
| rl_60_180 | all | partly_able | 68 | 29.4% (68) | 38.2% (68) | 24 |
| rl_60_180 | all | not_stated | 65 | 26.2% (65) | 35.4% (65) | 15 |
| rl_60_180 | all | unable | 27 | <10 | 40.7% (27) | <10 |
| rl_60_180 | all | no_reading | 3,740 | 16.3% (3,740) | 21.8% (3,740) | 1,044 |
| rl_60_180 | high conf | able | 11 | <10 | <10 | <10 |
| rl_60_180 | high conf | partly_able | 22 | <10 | 45.5% (22) | 12 |
| rl_60_180 | high conf | not_stated | 82 | 25.6% (82) | 34.1% (82) | 20 |
| rl_60_180 | high conf | unable | 33 | 30.3% (33) | 45.5% (33) | 10 |
| rl_60_180 | high conf | no_reading | 3,780 | 16.5% (3,780) | 21.9% (3,780) | 1,059 |

_(same table, columns part 2 of 4)_

| model_id | basis | latest stated capacity (prior 90 d) | 2026-05 paid_due | 2026-05 paid_any | 2026-06 n |
|---|---|---|---|---|---|
| cc_60_180 | all | able | <10 | <10 | 15 |
| cc_60_180 | all | partly_able | <10 | 30.0% (40) | 68 |
| cc_60_180 | all | not_stated | 19.6% (51) | 27.5% (51) | 58 |
| cc_60_180 | all | unable | <10 | <10 | 32 |
| cc_60_180 | all | no_reading | 8.6% (8,150) | 9.6% (8,150) | 8,737 |
| cc_60_180 | high conf | able | <10 | <10 | <10 |
| cc_60_180 | high conf | partly_able | <10 | <10 | 21 |
| cc_60_180 | high conf | not_stated | 21.9% (64) | 31.2% (64) | 86 |
| cc_60_180 | high conf | unable | <10 | <10 | 40 |
| cc_60_180 | high conf | no_reading | 8.6% (8,162) | 9.6% (8,162) | 8,755 |
| rl_60_180 | all | able | <10 | <10 | 10 |
| rl_60_180 | all | partly_able | <10 | <10 | 24 |
| rl_60_180 | all | not_stated | <10 | <10 | 28 |
| rl_60_180 | all | unable | <10 | <10 | 12 |
| rl_60_180 | all | no_reading | 15.4% (1,044) | 22.9% (1,044) | 1,256 |
| rl_60_180 | high conf | able | <10 | <10 | <10 |
| rl_60_180 | high conf | partly_able | <10 | <10 | <10 |
| rl_60_180 | high conf | not_stated | <10 | <10 | 33 |
| rl_60_180 | high conf | unable | <10 | <10 | 14 |
| rl_60_180 | high conf | no_reading | 15.5% (1,059) | 22.9% (1,059) | 1,272 |

_(same table, columns part 3 of 4)_

| model_id | basis | latest stated capacity (prior 90 d) | 2026-06 paid_due | 2026-06 paid_any | 2026-07 n |
|---|---|---|---|---|---|
| cc_60_180 | all | able | <10 | <10 | 11 |
| cc_60_180 | all | partly_able | 20.6% (68) | 29.4% (68) | 55 |
| cc_60_180 | all | not_stated | <10 | <10 | 67 |
| cc_60_180 | all | unable | <10 | <10 | 37 |
| cc_60_180 | all | no_reading | 8.3% (8,737) | 9.5% (8,737) | 9,831 |
| cc_60_180 | high conf | able | <10 | <10 | <10 |
| cc_60_180 | high conf | partly_able | <10 | <10 | 16 |
| cc_60_180 | high conf | not_stated | 18.6% (86) | 22.1% (86) | 88 |
| cc_60_180 | high conf | unable | <10 | <10 | 44 |
| cc_60_180 | high conf | no_reading | 8.3% (8,755) | 9.5% (8,755) | 9,844 |
| rl_60_180 | all | able | <10 | <10 | <10 |
| rl_60_180 | all | partly_able | <10 | <10 | 20 |
| rl_60_180 | all | not_stated | <10 | 39.3% (28) | 22 |
| rl_60_180 | all | unable | <10 | <10 | <10 |
| rl_60_180 | all | no_reading | 17.4% (1,256) | 22.5% (1,256) | 1,440 |
| rl_60_180 | high conf | able | <10 | <10 | <10 |
| rl_60_180 | high conf | partly_able | <10 | <10 | <10 |
| rl_60_180 | high conf | not_stated | <10 | 36.4% (33) | 29 |
| rl_60_180 | high conf | unable | <10 | <10 | <10 |
| rl_60_180 | high conf | no_reading | 17.7% (1,272) | 22.6% (1,272) | 1,449 |

_(same table, columns part 4 of 4)_

| model_id | basis | latest stated capacity (prior 90 d) | 2026-07 paid_due | 2026-07 paid_any |
|---|---|---|---|---|
| cc_60_180 | all | able | <10 | <10 |
| cc_60_180 | all | partly_able | <10 | <10 |
| cc_60_180 | all | not_stated | 19.4% (67) | 22.4% (67) |
| cc_60_180 | all | unable | <10 | <10 |
| cc_60_180 | all | no_reading | 6.6% (9,831) | 7.4% (9,831) |
| cc_60_180 | high conf | able | <10 | <10 |
| cc_60_180 | high conf | partly_able | <10 | <10 |
| cc_60_180 | high conf | not_stated | 18.2% (88) | 20.5% (88) |
| cc_60_180 | high conf | unable | <10 | <10 |
| cc_60_180 | high conf | no_reading | 6.6% (9,844) | 7.4% (9,844) |
| rl_60_180 | all | able | <10 | <10 |
| rl_60_180 | all | partly_able | <10 | <10 |
| rl_60_180 | all | not_stated | <10 | <10 |
| rl_60_180 | all | unable | <10 | <10 |
| rl_60_180 | all | no_reading | 16.0% (1,440) | 20.4% (1,440) |
| rl_60_180 | high conf | able | <10 | <10 |
| rl_60_180 | high conf | partly_able | <10 | <10 |
| rl_60_180 | high conf | not_stated | <10 | <10 |
| rl_60_180 | high conf | unable | <10 | <10 |
| rl_60_180 | high conf | no_reading | 16.1% (1,449) | 20.4% (1,449) |

## Part E - discrepancy flags (flag vs concordant)

### E1 says able / full or pays in full, while a1_state = low

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any |
|---|---|---|---|---|---|---|
| cc_60_180 | capacity full & a1 low [flag] | 28 | 27 | 32 | <10 | <10 |
| cc_60_180 | capacity full & a1 high/moderate [concordant] | 39 | 37 | 42 | 23.8% (42) | 31.0% (42) |
| cc_60_180 | intent payback_full & a1 low [flag] | 39 | 36 | 43 | <10 | <10 |
| cc_60_180 | intent payback_full & a1 high/moderate [concordant] | 64 | 56 | 68 | 22.1% (68) | 27.9% (68) |
| cc_60_180 | a1 low, neither claim [context] | 137 | 84 | 146 | 15.8% (146) | 19.2% (146) |
| rl_60_180 | capacity full & a1 low [flag] | 28 | 18 | 28 | <10 | 42.9% (28) |
| rl_60_180 | capacity full & a1 high/moderate [concordant] | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | intent payback_full & a1 low [flag] | 40 | 27 | 40 | 35.0% (40) | 50.0% (40) |
| rl_60_180 | intent payback_full & a1 high/moderate [concordant] | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | a1 low, neither claim [context] | 143 | 81 | 161 | 39.1% (161) | 49.1% (161) |

_(same table, columns part 2 of 2)_

| model_id | group | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | capacity full & a1 low [flag] | <10 | <10 | <10 |
| cc_60_180 | capacity full & a1 high/moderate [concordant] | 28.6% (42) | 38.1% (42) | 15 |
| cc_60_180 | intent payback_full & a1 low [flag] | <10 | 23.3% (43) | 23 |
| cc_60_180 | intent payback_full & a1 high/moderate [concordant] | 27.9% (68) | 33.8% (68) | 17 |
| cc_60_180 | a1 low, neither claim [context] | 20.5% (146) | 23.3% (146) | 16 |
| rl_60_180 | capacity full & a1 low [flag] | 35.7% (28) | 46.4% (28) | 16 |
| rl_60_180 | capacity full & a1 high/moderate [concordant] | <10 | <10 | <10 |
| rl_60_180 | intent payback_full & a1 low [flag] | 40.0% (40) | 52.5% (40) | 18 |
| rl_60_180 | intent payback_full & a1 high/moderate [concordant] | <10 | <10 | <10 |
| rl_60_180 | a1 low, neither claim [context] | 41.6% (161) | 50.9% (161) | 16 |

### E2 says capacity none, while a1_state high/moderate or CASA balance >= one month's due

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due |
|---|---|---|---|---|---|---|---|
| cc_60_180 | capacity none & a1 high/moderate [flag] | 10 | <10 | 10 | <10 | <10 | <10 |
| cc_60_180 | capacity none & CASA balance >= due [flag] | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity none & (a1 high/moderate or balance >= due) [flag, either] | 12 | 10 | 12 | <10 | <10 | <10 |
| cc_60_180 | capacity none & a1 low & balance < due or no row [concordant] | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | capacity none (all) [context] | 21 | 18 | 21 | <10 | <10 | <10 |
| rl_60_180 | capacity none & a1 high/moderate [flag] | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity none & CASA balance >= due [flag] | 0 | 0 | 0 | - | - | - |
| rl_60_180 | capacity none & (a1 high/moderate or balance >= due) [flag, either] | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity none & a1 low & balance < due or no row [concordant] | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | capacity none (all) [context] | 19 | 13 | 19 | 52.6% (19) | 63.2% (19) | 52.6% (19) |

_(same table, columns part 2 of 2)_

| model_id | group | pay45_any | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | capacity none & a1 high/moderate [flag] | <10 | <10 |
| cc_60_180 | capacity none & CASA balance >= due [flag] | <10 | - |
| cc_60_180 | capacity none & (a1 high/moderate or balance >= due) [flag, either] | <10 | <10 |
| cc_60_180 | capacity none & a1 low & balance < due or no row [concordant] | <10 | <10 |
| cc_60_180 | capacity none (all) [context] | <10 | <10 |
| rl_60_180 | capacity none & a1 high/moderate [flag] | <10 | <10 |
| rl_60_180 | capacity none & CASA balance >= due [flag] | - | - |
| rl_60_180 | capacity none & (a1 high/moderate or balance >= due) [flag, either] | <10 | <10 |
| rl_60_180 | capacity none & a1 low & balance < due or no row [concordant] | <10 | <10 |
| rl_60_180 | capacity none (all) [context] | 63.2% (19) | 13 |

### E3 says has_employment, while A1 salary stopped or income stopped

| model_id | group | n_conv | n_acct | n_pairs | pay30_due |
|---|---|---|---|---|---|
| cc_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 | <10 | <10 |
| cc_60_180 | has_employment & income_stopped (C2) [flag] | 21 | 15 | 23 | <10 |
| cc_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | 24 | 18 | 26 | <10 |
| cc_60_180 | has_employment & salary not stopped & income_continues [concordant] | 45 | 36 | 45 | 26.7% (45) |
| cc_60_180 | has_employment (all) [context] | 89 | 73 | 92 | 23.9% (92) |
| rl_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 | <10 | <10 |
| rl_60_180 | has_employment & income_stopped (C2) [flag] | <10 | <10 | <10 | <10 |
| rl_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | 12 | <10 | 12 | <10 |
| rl_60_180 | has_employment & salary not stopped & income_continues [concordant] | 15 | 12 | 16 | 62.5% (16) |
| rl_60_180 | has_employment (all) [context] | 42 | 28 | 43 | 55.8% (43) |

_(same table, columns part 2 of 3)_

| model_id | group | pay30_any | pay45_due |
|---|---|---|---|
| cc_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 |
| cc_60_180 | has_employment & income_stopped (C2) [flag] | 43.5% (23) | <10 |
| cc_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | 42.3% (26) | <10 |
| cc_60_180 | has_employment & salary not stopped & income_continues [concordant] | 33.3% (45) | 31.1% (45) |
| cc_60_180 | has_employment (all) [context] | 33.7% (92) | 28.3% (92) |
| rl_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 |
| rl_60_180 | has_employment & income_stopped (C2) [flag] | <10 | <10 |
| rl_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | <10 | <10 |
| rl_60_180 | has_employment & salary not stopped & income_continues [concordant] | 81.2% (16) | 62.5% (16) |
| rl_60_180 | has_employment (all) [context] | 65.1% (43) | 55.8% (43) |

_(same table, columns part 3 of 3)_

| model_id | group | pay45_any | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 |
| cc_60_180 | has_employment & income_stopped (C2) [flag] | 52.2% (23) | 25 |
| cc_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | 50.0% (26) | 27 |
| cc_60_180 | has_employment & salary not stopped & income_continues [concordant] | 40.0% (45) | 14 |
| cc_60_180 | has_employment (all) [context] | 40.2% (92) | 19 |
| rl_60_180 | has_employment & a1_salary_stopped [flag] | <10 | <10 |
| rl_60_180 | has_employment & income_stopped (C2) [flag] | <10 | <10 |
| rl_60_180 | has_employment & (a1_salary_stopped or income_stopped) [flag, either] | <10 | <10 |
| rl_60_180 | has_employment & salary not stopped & income_continues [concordant] | 81.2% (16) | 22 |
| rl_60_180 | has_employment (all) [context] | 65.1% (43) | 18 |

### E4 says lost_employment, while income continues

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due |
|---|---|---|---|---|---|---|---|
| cc_60_180 | lost_employment & income_continues [flag] | <10 | <10 | 10 | <10 | <10 | <10 |
| cc_60_180 | lost_employment & income_stopped [concordant] | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | lost_employment & income_dropped [context] | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | lost_employment & never_visible [context] | 14 | 11 | 14 | <10 | <10 | <10 |
| cc_60_180 | lost_employment (all) [context] | 31 | 26 | 32 | <10 | <10 | <10 |
| rl_60_180 | lost_employment & income_continues [flag] | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | lost_employment & income_stopped [concordant] | 22 | <10 | 22 | 50.0% (22) | 59.1% (22) | 50.0% (22) |
| rl_60_180 | lost_employment & income_dropped [context] | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | lost_employment & never_visible [context] | 19 | 11 | 19 | <10 | <10 | <10 |
| rl_60_180 | lost_employment (all) [context] | 50 | 23 | 50 | 40.0% (50) | 44.0% (50) | 40.0% (50) |

_(same table, columns part 2 of 2)_

| model_id | group | pay45_any | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | lost_employment & income_continues [flag] | <10 | <10 |
| cc_60_180 | lost_employment & income_stopped [concordant] | <10 | <10 |
| cc_60_180 | lost_employment & income_dropped [context] | <10 | - |
| cc_60_180 | lost_employment & never_visible [context] | <10 | <10 |
| cc_60_180 | lost_employment (all) [context] | <10 | <10 |
| rl_60_180 | lost_employment & income_continues [flag] | <10 | <10 |
| rl_60_180 | lost_employment & income_stopped [concordant] | 59.1% (22) | 13 |
| rl_60_180 | lost_employment & income_dropped [context] | <10 | - |
| rl_60_180 | lost_employment & never_visible [context] | <10 | <10 |
| rl_60_180 | lost_employment (all) [context] | 44.0% (50) | 21 |

### E5.1 transcript promises vs DCORE promises within +-3 days

| model_id | group | n_conv | n_acct | n_pairs | pay30_due |
|---|---|---|---|---|---|
| cc_60_180 | transcript promise (all) [base] | 240 | 181 | 255 | 16.9% (255) |
| cc_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 187 | 146 | 201 | 17.9% (201) |
| cc_60_180 | transcript promise, DCORE promise within +-3 days [matched] | 54 | 51 | 54 | <10 |
| cc_60_180 | DCORE promise within +-3 days (all) [base] | 121 | 96 | 128 | 14.1% (128) |
| cc_60_180 | DCORE promise, stated intent no_payment [reverse flag] | 0 | 0 | 0 | - |
| cc_60_180 | DCORE promise, stated intent not stated [reverse flag] | 44 | 42 | 51 | <10 |
| cc_60_180 | DCORE promise, stated intent a promise [concordant] | 77 | 66 | 77 | 13.0% (77) |
| cc_60_180 | neither a transcript nor a DCORE promise [context] | 200 | 158 | 220 | 13.6% (220) |
| rl_60_180 | transcript promise (all) [base] | 109 | 66 | 111 | 49.5% (111) |
| rl_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 99 | 61 | 101 | 48.5% (101) |
| rl_60_180 | transcript promise, DCORE promise within +-3 days [matched] | 10 | <10 | 10 | <10 |
| rl_60_180 | DCORE promise within +-3 days (all) [base] | 24 | 22 | 31 | 35.5% (31) |
| rl_60_180 | DCORE promise, stated intent no_payment [reverse flag] | 0 | 0 | 0 | - |
| rl_60_180 | DCORE promise, stated intent not stated [reverse flag] | <10 | 15 | 16 | <10 |
| rl_60_180 | DCORE promise, stated intent a promise [concordant] | 15 | 11 | 15 | <10 |
| rl_60_180 | neither a transcript nor a DCORE promise [context] | 147 | 79 | 160 | 29.4% (160) |

_(same table, columns part 2 of 3)_

| model_id | group | pay30_any | pay45_due |
|---|---|---|---|
| cc_60_180 | transcript promise (all) [base] | 21.2% (255) | 21.2% (255) |
| cc_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 23.4% (201) | 22.9% (201) |
| cc_60_180 | transcript promise, DCORE promise within +-3 days [matched] | <10 | <10 |
| cc_60_180 | DCORE promise within +-3 days (all) [base] | 14.8% (128) | 17.2% (128) |
| cc_60_180 | DCORE promise, stated intent no_payment [reverse flag] | - | - |
| cc_60_180 | DCORE promise, stated intent not stated [reverse flag] | <10 | 21.6% (51) |
| cc_60_180 | DCORE promise, stated intent a promise [concordant] | 13.0% (77) | 14.3% (77) |
| cc_60_180 | neither a transcript nor a DCORE promise [context] | 16.4% (220) | 18.2% (220) |
| rl_60_180 | transcript promise (all) [base] | 60.4% (111) | 52.3% (111) |
| rl_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 60.4% (101) | 51.5% (101) |
| rl_60_180 | transcript promise, DCORE promise within +-3 days [matched] | <10 | <10 |
| rl_60_180 | DCORE promise within +-3 days (all) [base] | 35.5% (31) | 35.5% (31) |
| rl_60_180 | DCORE promise, stated intent no_payment [reverse flag] | - | - |
| rl_60_180 | DCORE promise, stated intent not stated [reverse flag] | <10 | <10 |
| rl_60_180 | DCORE promise, stated intent a promise [concordant] | <10 | <10 |
| rl_60_180 | neither a transcript nor a DCORE promise [context] | 42.5% (160) | 31.9% (160) |

_(same table, columns part 3 of 3)_

| model_id | group | pay45_any | median_days_to_pay |
|---|---|---|---|
| cc_60_180 | transcript promise (all) [base] | 27.5% (255) | 21 |
| cc_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 29.4% (201) | 20 |
| cc_60_180 | transcript promise, DCORE promise within +-3 days [matched] | 20.4% (54) | 28 |
| cc_60_180 | DCORE promise within +-3 days (all) [base] | 21.1% (128) | 22 |
| cc_60_180 | DCORE promise, stated intent no_payment [reverse flag] | - | - |
| cc_60_180 | DCORE promise, stated intent not stated [reverse flag] | 23.5% (51) | 21 |
| cc_60_180 | DCORE promise, stated intent a promise [concordant] | 19.5% (77) | 23 |
| cc_60_180 | neither a transcript nor a DCORE promise [context] | 20.9% (220) | 19 |
| rl_60_180 | transcript promise (all) [base] | 63.1% (111) | 19 |
| rl_60_180 | transcript promise, no DCORE promise within +-3 days [unmatched] | 63.4% (101) | 19 |
| rl_60_180 | transcript promise, DCORE promise within +-3 days [matched] | <10 | <10 |
| rl_60_180 | DCORE promise within +-3 days (all) [base] | 35.5% (31) | 18 |
| rl_60_180 | DCORE promise, stated intent no_payment [reverse flag] | - | - |
| rl_60_180 | DCORE promise, stated intent not stated [reverse flag] | <10 | <10 |
| rl_60_180 | DCORE promise, stated intent a promise [concordant] | <10 | <10 |
| rl_60_180 | neither a transcript nor a DCORE promise [context] | 45.6% (160) | 19 |

### E5.2 shares (pairs)

| model_id | share | numerator | denominator | share_value |
|---|---|---|---|---|
| cc_60_180 | transcript promises with no DCORE promise | 201 | 255 | 78.8% |
| cc_60_180 | DCORE promises with stated intent no_payment or not stated | 51 | 128 | 39.8% |
| rl_60_180 | transcript promises with no DCORE promise | 101 | 111 | 91.0% |
| rl_60_180 | DCORE promises with stated intent no_payment or not stated | 16 | 31 | 51.6% |

### E5.3 DCORE promise events anchored on the promise day (n_conv = events)

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any |
|---|---|---|---|---|---|---|
| cc_60_180 | DCORE promise, no conversation within +-3 days | 3,978 | 3,176 | 3,978 | 41.2% (3,978) | 47.7% (3,978) |
| cc_60_180 | DCORE promise, with a conversation within +-3 days | 246 | 237 | 246 | 14.6% (246) | 15.4% (246) |
| rl_60_180 | DCORE promise, no conversation within +-3 days | 592 | 505 | 592 | 45.8% (592) | 61.8% (592) |
| rl_60_180 | DCORE promise, with a conversation within +-3 days | 25 | 25 | 25 | 44.0% (25) | 48.0% (25) |

_(same table, columns part 2 of 2)_

| model_id | group | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | DCORE promise, no conversation within +-3 days | 46.5% (3,978) | 52.4% (3,978) | 10 |
| cc_60_180 | DCORE promise, with a conversation within +-3 days | 15.9% (246) | 17.5% (246) | 12 |
| rl_60_180 | DCORE promise, no conversation within +-3 days | 51.5% (592) | 66.6% (592) | 18 |
| rl_60_180 | DCORE promise, with a conversation within +-3 days | 44.0% (25) | 48.0% (25) | 20 |

### E6 stated dispute vs a3_dispute_flag at the next month end

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any |
|---|---|---|---|---|---|---|
| cc_60_180 | stated dispute & a3 flag false [flag] | 65 | 53 | 72 | 19.4% (72) | 31.9% (72) |
| cc_60_180 | stated dispute & a3 flag true [concordant] | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | stated dispute & no A3 row at the next month end [context] | 95 | 72 | 98 | <10 | <10 |
| cc_60_180 | no stated dispute & a3 flag true [flag, reverse] | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | no stated dispute & a3 flag false [concordant] | 219 | 145 | 226 | 31.4% (226) | 37.2% (226) |
| rl_60_180 | stated dispute & a3 flag false [flag] | 36 | 27 | 37 | 45.9% (37) | 54.1% (37) |
| rl_60_180 | stated dispute & a3 flag true [concordant] | 0 | 0 | 0 | - | - |
| rl_60_180 | stated dispute & no A3 row at the next month end [context] | 10 | <10 | 11 | <10 | <10 |
| rl_60_180 | no stated dispute & a3 flag true [flag, reverse] | 0 | 0 | 0 | - | - |
| rl_60_180 | no stated dispute & a3 flag false [concordant] | 227 | 111 | 238 | 35.7% (238) | 48.7% (238) |

_(same table, columns part 2 of 2)_

| model_id | group | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|
| cc_60_180 | stated dispute & a3 flag false [flag] | 25.0% (72) | 37.5% (72) | 18 |
| cc_60_180 | stated dispute & a3 flag true [concordant] | <10 | <10 | - |
| cc_60_180 | stated dispute & no A3 row at the next month end [context] | <10 | 13.3% (98) | 28 |
| cc_60_180 | no stated dispute & a3 flag true [flag, reverse] | <10 | <10 | <10 |
| cc_60_180 | no stated dispute & a3 flag false [concordant] | 37.2% (226) | 43.8% (226) | 18 |
| rl_60_180 | stated dispute & a3 flag false [flag] | 48.6% (37) | 56.8% (37) | 12 |
| rl_60_180 | stated dispute & a3 flag true [concordant] | - | - | - |
| rl_60_180 | stated dispute & no A3 row at the next month end [context] | <10 | <10 | <10 |
| rl_60_180 | no stated dispute & a3 flag true [flag, reverse] | - | - | - |
| rl_60_180 | no stated dispute & a3 flag false [concordant] | 39.5% (238) | 52.1% (238) | 21 |

### E7 says intent no_payment, while a3_state = high

| model_id | group | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any | median_days_to_pay |
|---|---|---|---|---|---|---|---|---|---|
| cc_60_180 | no_payment & a3 high [flag] | <10 | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | no_payment & a3 low [concordant] | <10 | <10 | <10 | <10 | <10 | <10 | <10 | - |
| cc_60_180 | no_payment & a3 moderate [context] | <10 | <10 | <10 | <10 | <10 | <10 | <10 | - |
| cc_60_180 | no_payment & a3 unknown [context] | <10 | <10 | <10 | <10 | <10 | <10 | <10 | - |
| rl_60_180 | no_payment & a3 high [flag] | 0 | 0 | 0 | - | - | - | - | - |
| rl_60_180 | no_payment & a3 low [concordant] | 0 | 0 | 0 | - | - | - | - | - |
| rl_60_180 | no_payment & a3 moderate [context] | <10 | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | no_payment & a3 unknown [context] | 0 | 0 | 0 | - | - | - | - | - |

## Part F - requests

### F1 request_type x a1_state x a3_state (a conversation with two request types counts under both)

| model_id | request_type | a1_state | a3_state | n_conv | n_acct |
|---|---|---|---|---|---|
| cc_60_180 | (type missing) | low | high | <10 | <10 |
| cc_60_180 | callback | moderate | high | <10 | <10 |
| cc_60_180 | deferral | high | high | <10 | <10 |
| cc_60_180 | deferral | high | moderate | <10 | <10 |
| cc_60_180 | deferral | moderate | high | <10 | <10 |
| cc_60_180 | deferral | moderate | moderate | <10 | <10 |
| cc_60_180 | deferral | low | high | <10 | <10 |
| cc_60_180 | deferral | low | moderate | <10 | 10 |
| cc_60_180 | deferral | low | low | <10 | <10 |
| cc_60_180 | deferral | unknown | high | <10 | <10 |
| cc_60_180 | deferral | unknown | moderate | <10 | <10 |
| cc_60_180 | escalation | high | high | <10 | <10 |
| cc_60_180 | escalation | moderate | high | <10 | <10 |
| cc_60_180 | escalation | moderate | moderate | <10 | <10 |
| cc_60_180 | escalation | low | high | <10 | <10 |
| cc_60_180 | escalation | low | moderate | <10 | <10 |
| cc_60_180 | escalation | unknown | moderate | <10 | <10 |
| cc_60_180 | information | high | high | <10 | <10 |
| cc_60_180 | information | high | moderate | <10 | <10 |
| cc_60_180 | information | high | low | <10 | <10 |
| cc_60_180 | information | moderate | high | 14 | 14 |
| cc_60_180 | information | moderate | moderate | 16 | 12 |
| cc_60_180 | information | moderate | low | <10 | <10 |
| cc_60_180 | information | low | high | <10 | <10 |
| cc_60_180 | information | low | moderate | <10 | <10 |
| cc_60_180 | information | low | low | <10 | <10 |
| cc_60_180 | information | unknown | high | 11 | 11 |
| cc_60_180 | information | unknown | moderate | <10 | <10 |
| cc_60_180 | information | unknown | low | <10 | <10 |
| cc_60_180 | restructure | high | high | <10 | <10 |
| cc_60_180 | restructure | high | moderate | <10 | <10 |
| cc_60_180 | restructure | moderate | high | <10 | <10 |
| cc_60_180 | restructure | moderate | moderate | <10 | <10 |
| cc_60_180 | restructure | moderate | low | <10 | <10 |
| cc_60_180 | restructure | low | high | <10 | <10 |
| cc_60_180 | restructure | low | moderate | 10 | <10 |
| cc_60_180 | restructure | unknown | high | <10 | <10 |
| cc_60_180 | restructure | unknown | moderate | <10 | <10 |
| cc_60_180 | restructure | unknown | low | <10 | <10 |
| cc_60_180 | settlement | high | high | <10 | <10 |
| cc_60_180 | settlement | high | moderate | <10 | <10 |
| cc_60_180 | settlement | moderate | high | 10 | <10 |
| cc_60_180 | settlement | moderate | moderate | 11 | <10 |
| cc_60_180 | settlement | moderate | low | <10 | <10 |
| cc_60_180 | settlement | low | high | <10 | <10 |
| cc_60_180 | settlement | low | moderate | 13 | <10 |
| cc_60_180 | settlement | low | low | <10 | <10 |
| cc_60_180 | settlement | unknown | high | <10 | <10 |
| cc_60_180 | settlement | unknown | moderate | <10 | <10 |
| cc_60_180 | settlement | unknown | low | <10 | <10 |
| cc_60_180 | waiver | high | high | <10 | <10 |
| cc_60_180 | waiver | high | moderate | <10 | <10 |
| cc_60_180 | waiver | moderate | high | <10 | <10 |
| cc_60_180 | waiver | moderate | moderate | <10 | <10 |
| cc_60_180 | waiver | low | moderate | <10 | <10 |
| cc_60_180 | waiver | low | low | <10 | <10 |
| cc_60_180 | waiver | unknown | low | <10 | <10 |
| rl_60_180 | (type missing) | low | moderate | <10 | <10 |
| rl_60_180 | deferral | low | high | <10 | <10 |
| rl_60_180 | deferral | low | moderate | <10 | <10 |
| rl_60_180 | deferral | low | low | <10 | <10 |
| rl_60_180 | deferral | unknown | moderate | <10 | <10 |
| rl_60_180 | deferral | unknown | low | <10 | <10 |
| rl_60_180 | escalation | moderate | moderate | <10 | <10 |
| rl_60_180 | escalation | low | low | <10 | <10 |
| rl_60_180 | escalation | unknown | moderate | <10 | <10 |
| rl_60_180 | information | moderate | high | <10 | <10 |
| rl_60_180 | information | moderate | moderate | <10 | <10 |
| rl_60_180 | information | moderate | low | <10 | <10 |
| rl_60_180 | information | low | high | <10 | <10 |
| rl_60_180 | information | low | moderate | 12 | 11 |
| rl_60_180 | information | low | low | <10 | <10 |
| rl_60_180 | information | unknown | high | <10 | <10 |
| rl_60_180 | information | unknown | moderate | <10 | <10 |
| rl_60_180 | information | unknown | low | <10 | <10 |
| rl_60_180 | restructure | high | moderate | <10 | <10 |
| rl_60_180 | restructure | moderate | moderate | <10 | <10 |
| rl_60_180 | restructure | low | high | <10 | <10 |
| rl_60_180 | restructure | low | moderate | <10 | <10 |
| rl_60_180 | restructure | low | low | <10 | <10 |
| rl_60_180 | restructure | unknown | moderate | <10 | <10 |
| rl_60_180 | restructure | unknown | low | <10 | <10 |
| rl_60_180 | settlement | high | low | <10 | <10 |
| rl_60_180 | settlement | moderate | moderate | 14 | <10 |
| rl_60_180 | settlement | low | high | <10 | <10 |
| rl_60_180 | settlement | low | moderate | <10 | <10 |
| rl_60_180 | settlement | low | low | <10 | <10 |
| rl_60_180 | settlement | unknown | high | <10 | <10 |
| rl_60_180 | settlement | unknown | moderate | 12 | <10 |
| rl_60_180 | settlement | unknown | low | <10 | <10 |
| rl_60_180 | waiver | moderate | moderate | <10 | <10 |
| rl_60_180 | waiver | low | high | <10 | <10 |
| rl_60_180 | waiver | low | moderate | <10 | <10 |
| rl_60_180 | waiver | low | low | <10 | <10 |
| rl_60_180 | waiver | unknown | moderate | <10 | <10 |
| rl_60_180 | waiver | unknown | low | <10 | <10 |

### F2 pay45_any per request type within a1_state

| model_id | rtype | All | high | moderate | low | unknown |
|---|---|---|---|---|---|---|
| cc_60_180 | (type missing) | <10 | 0 | 0 | <10 | 0 |
| cc_60_180 | callback | <10 | 0 | <10 | 0 | 0 |
| cc_60_180 | deferral | 36.7 (49) | <10 | <10 (12) | <10 (20) | <10 (12) |
| cc_60_180 | escalation | <10 (11) | <10 | <10 | <10 | <10 |
| cc_60_180 | information | 29.4 (85) | <10 (10) | <10 (31) | <10 (21) | <10 (23) |
| cc_60_180 | restructure | 27.7 (47) | <10 | <10 (12) | <10 (15) | <10 (15) |
| cc_60_180 | settlement | 21.1 (76) | <10 (15) | <10 (23) | <10 (22) | <10 (16) |
| cc_60_180 | waiver | <10 (10) | <10 | <10 | <10 | <10 |
| rl_60_180 | (type missing) | <10 | 0 | 0 | <10 | 0 |
| rl_60_180 | deferral | <10 (10) | 0 | 0 | <10 | <10 |
| rl_60_180 | escalation | <10 | 0 | <10 | <10 | <10 |
| rl_60_180 | information | 54.4 (57) | 0 | <10 (10) | 37.5 (32) | 66.7 (15) |
| rl_60_180 | restructure | 69.6 (23) | <10 | <10 | 76.9 (13) | <10 |
| rl_60_180 | settlement | 68.4 (38) | <10 | <10 (14) | <10 | 71.4 (14) |
| rl_60_180 | waiver | 57.1 (21) | 0 | <10 | <10 (12) | <10 |

### F2.2 request type, all outcomes

| model_id | request_type | n_conv | n_acct | n_pairs | pay30_due | pay30_any | pay45_due | pay45_any |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | (type missing) | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | callback | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| cc_60_180 | deferral | 45 | 46 | 49 | 20.4% (49) | 22.4% (49) | 34.7% (49) | 36.7% (49) |
| cc_60_180 | escalation | 11 | 10 | 11 | <10 | <10 | <10 | <10 |
| cc_60_180 | information | 80 | 79 | 85 | 20.0% (85) | 24.7% (85) | 23.5% (85) | 29.4% (85) |
| cc_60_180 | restructure | 46 | 38 | 47 | 21.3% (47) | 23.4% (47) | 23.4% (47) | 27.7% (47) |
| cc_60_180 | settlement | 75 | 47 | 76 | 13.2% (76) | 14.5% (76) | 15.8% (76) | 21.1% (76) |
| cc_60_180 | waiver | <10 | <10 | 10 | 0.0% (10) | 0.0% (10) | <10 | <10 |
| rl_60_180 | (type missing) | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | deferral | <10 | <10 | 10 | <10 | <10 | <10 | <10 |
| rl_60_180 | escalation | <10 | <10 | <10 | <10 | <10 | <10 | <10 |
| rl_60_180 | information | 50 | 44 | 57 | 35.1% (57) | 52.6% (57) | 36.8% (57) | 54.4% (57) |
| rl_60_180 | restructure | 23 | 16 | 23 | 65.2% (23) | 65.2% (23) | 65.2% (23) | 69.6% (23) |
| rl_60_180 | settlement | 37 | 15 | 38 | 55.3% (38) | 65.8% (38) | 57.9% (38) | 68.4% (38) |
| rl_60_180 | waiver | 21 | 13 | 21 | 52.4% (21) | 57.1% (21) | 52.4% (21) | 57.1% (21) |

_(same table, columns part 2 of 2)_

| model_id | request_type | median_days_to_pay |
|---|---|---|
| cc_60_180 | (type missing) | - |
| cc_60_180 | callback | <10 |
| cc_60_180 | deferral | 26 |
| cc_60_180 | escalation | <10 |
| cc_60_180 | information | 23 |
| cc_60_180 | restructure | 16 |
| cc_60_180 | settlement | 13 |
| cc_60_180 | waiver | <10 |
| rl_60_180 | (type missing) | - |
| rl_60_180 | deferral | <10 |
| rl_60_180 | escalation | <10 |
| rl_60_180 | information | 21 |
| rl_60_180 | restructure | 22 |
| rl_60_180 | settlement | 18 |
| rl_60_180 | waiver | 18 |

### F3 RL restructure after a restructure request

| model_id | restructure flag data reaches | chains reach | calls with a full 90-day window | restructure requests |
|---|---|---|---|---|
| rl_60_180 | 2026-05-31 | 2025-12-31 | 0 | 23 |

## Verdicts

- **A (coverage):** a full run over all transcripts would cover only a minority of 60-180 account-months, a little more
  for RL than CC, and the extracted share is highest in the lower DPD bands and by call month rises through the window;
  extraction was clearly targeted at delinquent, PTP-history and loan-holding customers (A2b, A2c), so extracted
  conversations are not a random sample; at 180+ not answered (the two 180+ model_ids were not run), only that the store
  holds 180+-bucket conversations of these customers (A3).
- **B (other signals beyond UC2 states):** at this sample size only has_employment as a stated reason, a named
  salary-cycle or weeks period, a named amount (RL) and request types separate payers from the reference, always in the
  direction of "any stated content pays more than none", with settlement requests the exception in CC (lower); within A1
  / A3 states the cells are too thin to read.
- **B3 (call-anchored, 45-day basis vs first validation):** capacity and intent still add little between their stated
  levels (able, partly, full, partial and with_delay look alike, refuses and unable stay masked), while stated vs not
  stated is a visible gap that the 45-day basis widens slightly; in CC the capacity gap shrinks with high-confidence
  detections only (so it is partly carried by low-confidence readings) whereas intent and RL hold up.
- **C (stated job / income vs our income data):** claims are only loosely consistent: more than half of has_employment
  claims in CC show income continuing but a visible minority show it stopped, lost_employment claims mostly show no
  visible income at all (so our income data cannot test them), and capacity none is not testable (masked); consistency
  matters little: has_employment with stopped income pays at least as well as with continuing income in CC, and in RL
  continuing income pays best, so the direction is not stable.
- **D (inside Unknown and no_promise):** stated ability does separate inside A1 Unknown on the month-end view (able /
  partly / not stated above unable, all above no reading, both models), but the call-anchored AUC is only slightly above
  chance and drops to chance with high-confidence only, and the large gap is stated-or-not rather than able-or-unable;
  stated intent inside A3 low / no_promise is unreadable (masked in CC, one cell in RL).
- **E (discrepancy flags):** the only flags with readable groups that differ from their concordant group are E1
  payback_full while A1 low (CC, lower), E3 has_employment with stopped income (CC, higher, opposite to the
  expectation), and E6 stated dispute with the A3 flag false (CC, lower than no dispute); E2, E4 and E7 are masked or
  too small, and E6 compares at the next month end so it conditions on the account still being in the base.
- **E5 (transcript promises vs DCORE):** transcript promises carry evidence DCORE misses: most transcript promises have
  no DCORE promise within the call window (E5), and a large share of DCORE promises have no stated intent or none
  stated; the transcript-promise payers are not worse than the matched ones (CC), but DCORE promises made without any
  conversation pay best of all (E5.3, a different population anchored on the promise day), so the transcript adds
  coverage, not a better payment signal than a DCORE promise.
- **F (requests):** requests are rare and spread over information, settlement, restructure, deferral (and waiver in RL),
  demand sits mostly in A1 moderate / low and A3 moderate; payment after the call is highest for deferral (CC) and for
  restructure / settlement requests (RL), lowest for settlement requests in CC; the restructure follow-up (F3) cannot be
  answered because the restructure data ends 2026-05-31, before any call in range could have a full follow-up window.

## Open items

- Run cc_180_plus and rl_180_plus (Part A first) to close A3 and the 180+ verdict.
- The pair samples (CC and RL) are small because most extracted calls hit customers outside 60-180 at the prior month
  end; a longer window or more extraction would be needed for B2, D2 and E.
- CASA inflow used the WM-based `feat_cif_inflow_outflow_salary_monthly`; the CASA-scheme-only table does not exist for
  these model_ids.

