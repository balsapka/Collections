# A2 contact basis: summary (cc_60_180, cc_180_plus, rl_60_180, rl_180_plus)

Results: `a2_contact_basis_<model_id>.md` and `.json` in this folder (snippet 2026-11-27a, run 2026-11-27).
Exploration only: no change to A2, the pipeline, the catalog or the registry. Figures are at 07-31 unless
stated. Variants: V1 drops "not a conversation"; V1s also drops SETTLEMENT; V2 drops "not a conversation"
and "unclear"; V2s drops all three. Inbound and other SUC calls and e-mail received stay in every variant.

## Verdict

- A stricter contact rule does not separate payers better. It lowers the payment AUC of A2 in every model,
  variant, month and horizon that was computed.
- The cause is what the rules drop. 49-97% of the accounts that move had a payment of AED 100 or more in
  the window, so most dropped "contacts" are payment postings. A3 and the payments already count those.
- So the AUC loss is not proof that those contacts show we can reach the customer. It shows that A2
  Reachable overlaps with payment. Whether payment postings belong in A2 is a definition decision.
- Stricter rules only move Reachable accounts to Unknown. None moves to Non-Reachable, in any model.
- Not tested: dropping inbound and other SUC calls, the biggest class in cc_60_180 (46.5% of Reachable).

## Run status

- V0 reproduces the persisted A2 row for row: 0 mismatches in every month present, all four models.
- cc_60_180 has 05-31, 07-31 and 10-31. The other three have 05-31 and 07-31 only: their e2e rerun for
  Sep and Oct was not finished. Their header says "tie-out not computed"; that is the missing month only.
- Their payments end 08-31, so the 07-31 3-month outcome is not computed for them (Q3 only).
- cc_60_180 V0 Reachable at 07-31 is 7,524, not the 4,046 of the earlier RPC check. A2 was rerun since,
  so that expectation is stale. The old 38% (1,547 of 4,046) does not carry over to the new output.

## Q1: what V0 Reachable rests on (best contact class in the window, share of V0 Reachable)

| model | Reachable | conv. | e-mail | unclear | call | settle | not conv. | no conv. |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | 7,524 | 29.3% | 12.6% | 5.5% | 46.5% | 1.9% | 4.3% | 70.7% |
| cc_180_plus | 12,062 | 20.6% | 32.0% | 3.4% | 13.1% | 11.2% | 19.7% | 79.4% |
| rl_60_180 | 1,064 | 40.0% | 30.2% | 13.9% | 3.3% | <10 | 12.2% | 60.0% |
| rl_180_plus | 2,701 | 20.7% | 30.6% | 4.1% | 13.0% | 18.1% | 13.4% | 79.3% |

"call" = inbound or other SUC call. "no conv." = no conversation at all in the window, so it includes
the call class. cc_60_180 at 10-31: conversation 22.6%, call 52.7%, no conversation 77.4%.

## Q2: share of V0 Reachable that moves to Unknown (no contact in window)

| model | V0 Reach. | V1 | V1s | V2 | V2s |
|---|---|---|---|---|---|
| cc_60_180 | 40.9% | 4.3% | 6.2% | 5.5% | 7.7% |
| cc_180_plus | 3.8% | 19.7% | 30.9% | 22.3% | 33.7% |
| rl_60_180 | 28.5% | 12.2% | 12.6% | 25.2% | 25.8% |
| rl_180_plus | 4.9% | 13.4% | 31.6% | 15.9% | 34.7% |

"V0 Reach." is the share of all rows. Moves to Non-Reachable and any other change are 0 in every cell.
cc_60_180 at 10-31 is the same: 4.6%, 6.4%, 5.7%, 7.7%.

## Q3: AUC of the three states (Reachable > Unknown > Non-Reachable), payment in the next month

| model | V0 AUC | V1 | V1s | V2 | V2s |
|---|---|---|---|---|---|
| cc_60_180 | 0.667 | -0.010 | -0.017 | -0.011 | -0.019 |
| cc_180_plus | 0.672 | -0.064 | -0.088 | -0.072 | -0.096 |
| rl_60_180 | 0.629 | -0.010 | -0.011 | -0.023 | -0.024 |
| rl_180_plus | 0.687 | -0.032 | -0.095 | -0.036 | -0.102 |

Columns V1 to V2s are the change against V0. Every other computed row has the same sign: 05-31 1 month,
05-31 3 months and cc_60_180 07-31 3 months. Outcome: paid at least AED 100 in the k calendar months after
the date (ported from `a3_results_snippet._outcomes`; the A2 workbook code is not in the repo).

- Payment rate in the next month by state, V0 against V2s, cc_60_180: Reachable 19.8% / 17.9%, Unknown
  5.8% / 15.6%, Non-Reachable 5.7% / 5.7%. The movers lift Unknown to nearly Reachable.
- cc_60_180 movers to Unknown under V1 pay 41.1% in the next month against 18.8% for the stayers
  (+22.2 pp [+16.9, +27.8]) and 5.7-5.8% for the accounts that were Unknown or Non-Reachable already.
- Under V2s the order of states by rate turns Unknown above Reachable in cc_60_180 and rl_60_180 (05-31).

## Q4: do the movers overlap with payments and A3? (07-31, V1 and V2s)

| model | movers V1 | pay in W | stayers | movers V2s | pay in W | stayers |
|---|---|---|---|---|---|---|
| cc_60_180 | 319 | 91.5% | 42.0% | 580 | 86.6% | 40.5% |
| cc_180_plus | 2,372 | 67.4% | 36.1% | 4,048 | 60.3% | 33.2% |
| rl_60_180 | 130 | 96.9% | 59.3% | 275 | 82.2% | 57.5% |
| rl_180_plus | 360 | 48.9% | 44.0% | 932 | 52.4% | 40.6% |

"pay in W" = a payment of AED 100 or more in the window. Stayers are V0 Reachable accounts that stay.
cc_60_180 V1 movers also hold an A3 promise event less often than stayers (21.9% against 28.4%) and sit
in A3 payment_credibility_high more often (43.3% against 20.5%). The `.md` files hold the other variants.
The "not a conversation" class includes ACCOUNT PAID, CUSTOMER MADE PAYMENT, PARTIALLY PAID and CUSTOMER
KEPT PROMISE MADE, which is why the movers are recent payers.

## Reading

- The payment outcome is not independent of the rule here: an account whose contact is a payment posting
  paid recently and tends to pay again. The Q3 drop therefore says little about whether the dropped
  contacts are real reach. It does say A2 Reachable carries payment information that A3 also carries.
- A2 is meant to measure locatability. Counting payment postings as contact makes A2 and A3 overlap.
  Stricter rules make A2 purer but weaker as a payment predictor. This is a design call for GRR.
- Smallest groups: rl_60_180 movers (130 to 275) and rl_180_plus V1 movers (360). Their intervals are wide.

## Open points

- No variant separates payment postings (ACCOUNT PAID, CUSTOMER MADE PAYMENT, PARTIALLY PAID) from the rest
  of "not a conversation". A variant that drops only those would test the overlap directly.
- No variant drops inbound and other SUC calls, 46.5% of cc_60_180 Reachable and 52.7% at 10-31.
- Rerun the three models once the Sep and Oct e2e data lands, to get 10-31 and the 07-31 3-month outcome.
