# A1 ability — weak spots to investigate with EDA

The places where the CC A1 logic rests on an assumption that PROD data has not yet confirmed.
Each entry gives the risk, what to measure, and the rule it could change. Marked: **[B03]**
already measured by the bundle 03 check, **[v02]** in the Sonnet v02 prompt, **[bureau v01]**
in the bureau prompt; the rest are open.

## 0. Validity and stability (do these first)

1. **Does A1 rank risk?** Next-month cure and roll rate by A1 state (High > Moderate > Low;
   where does Unknown sit?), per segment. If the states do not separate outcomes, threshold
   tuning is wasted effort. *Changes:* everything below, and the order to work on it.
2. **Month-to-month churn.** State transition matrix from one month to the next per account.
   High flip rates mean the rules react to noise (paydays, snapshot timing), not ability.
   *Changes:* MIN_MONTHS, the weakening checks.
3. **What drives each state.** For every state, the share reached through each path:
   income-only, CASA-only, card payment, distress demotion, unknown gate. A state that is
   mostly one path is really that one signal. *Changes:* point weights.

## 1. Income

4. **2 × anchor raises the bar** [B03]. Share of rows where the bar is above AED 3,000, its
   distribution, and how many stable incomes it removes. *Changes:* K_INC or a flat floor.
5. **Payday around the month boundary.** Day of month of the recovered salary credit. Pay
   on the 28th–2nd (weekends, Eid, early pay) can put two credits in one month and none in
   the next: one month then counts 0, which can fail "2 of 3" and the weakening check (missing
   months count as 0). *Changes:* tolerate one empty month next to a double month, or use
   30-day credit cycles instead of calendar months.
6. **The weakening check** [B03]. How often it turns Stable into Weak, and whether those
   rows behave like Weak in outcomes (item 1). *Changes:* D_INC, or drop the check.
7. **WM salary recovery is consistent.** Snapshots that see the same credit should agree on
   its date (snapshot − days_since). Measure the spread of the recovered date per credit,
   NULL `ft_days_since_salary_transaction` rates, and capped values. *Changes:* the
   recovery rule in `_internal_salary`.
8. **Largest, not sum, per month.** Share of CIF-months with two or more distinct salary
   credits (salary + allowance). *Changes:* sum within the month.
9. **Bureau vs internal salary.** Where both exist: does the bureau month line up with the
   credit month (lag?), and do the amounts agree? `subj_salcr_hist_ref_mnth` parse failures
   (`MMyyyy`, lost leading zero) give NULL months silently. *Changes:* month shift, parsing.
10. **The salary floor.** Salary distribution of the collections population versus F_INC =
    3,000 and DEMIN = 1,000. *Changes:* F_INC, DEMIN.
11. **Income is mostly absent.** 32.7% ever had salary and 94% of them stopped 4+ months
    ago, so income is "none" for most rows and A1 is in effect a liquidity axis. Check the
    income level distribution per segment. *Changes:* expectations; the GRR bureau feed.

## 2. Liquidity

12. **CASA month value depends on snapshot timing.** The month's balance is the 4-week
    average at its last weekly snapshot; if `week_number` is a week start, the last snapshot
    can cover mostly the next month or miss the month's last days. Check which day
    `week_number` falls on and the day of the month's last snapshot. *Changes:* which
    snapshot represents the month.
13. **94.6% "none".** For the 61% with a real low balance: the balance distribution against
    F_CASA = 3,000. *Changes:* F_CASA, K_CASA.
14. **One card payment = adequate (2 points).** Share of adequate liquidity reached only via
    `ext_card_payment_max`, and its outcomes versus CASA-adequate. *Changes:* weight it
    lower (weak only) or require two payments.
15. **Card matching.** Match rate of `transaction_acid` against `raw_beneficiary_cards`
    (masked or formatted card numbers would match nothing), and cards registered after the
    observation date (the live-snapshot look-ahead). *Changes:* the match key.
16. **CASA weakening with missing months.** Months without a snapshot are skipped, so one
    month of data can stand for the whole window. Count of rows whose recent or prior mean
    rests on one month. *Changes:* a minimum number of months for the comparison.

## 3. Distress

17. **Whose cheque bounced?** `CHEQUE RETURNS` covers both the customer's own cheque bouncing
    (distress) and a cheque the customer deposited bouncing on them (not their distress).
    Split by `tran_dc`, `tran_type` / `tran_sub_type` and leg. *Changes:* keep the
    customer-issued side only. Probably the largest single risk in distress.
18. **DDS retries and reversals** [v02]. One failed direct debit retried several times;
    "Reversal" may include customer- or bank-initiated reversals that are not failures.
    *Changes:* count a DDS failure once per mandate and month, drop non-failure reversals.
19. **DDS on the card itself.** At 60+ DPD a failed DDS for this very card is almost the
    definition of being delinquent. Share of DDS returns whose beneficiary is the bank's own
    card, and the distress fire rate per segment. If it fires for nearly everyone, it does
    not separate anyone. *Changes:* exclude the scored product's own DDS.
20. **Bureau bounce dating** [bureau v01]. `extract_date` is the pull date; the same amount
    repeats across pulls for 55% of bounced CIFs, so one old bounce can keep the flag on.
    *Changes:* date by `DT_OF_RETURN` or by the first pull of an amount.
21. **One event = one rung.** Distress has no count or size. The outcome of 1 versus 3+
    events. *Changes:* a minimum count, or a stronger demotion for repeat events.

## 4. Unknown gate

22. **What makes `casa_active`.** Any inflow or outflow > 0 counts: interest credits and fee
    debits on a dormant account make it "active", which turns Unknown into Low. Split
    active rows by transaction type (customer-initiated or system). *Changes:* count
    customer-initiated transactions only.
23. **Unknown versus Low outcomes.** If Unknown cures like Low, the split adds nothing; if
    like Moderate, Low is overloaded with dormant customers. (Item 1.)

## 5. Anchor (CC 60–180)

24. **Anchor coverage and size.** NULL anchor rate (no snapshot in the month, all buckets
    empty) and the anchor distribution by DPD bucket. **Month-end versus cycle.** A
    month-end snapshot sits mid-billing-cycle, so its buckets may differ from the cycle
    date's. *Changes:* the snapshot rule, or the anchor definition.

## 6. Architecture and serving

25. **Data available on the 2nd.** PROD runs on the 2nd for the previous month end. Check
    whether the WM weekly snapshots, labelled transactions, `comp_financial_tran_repos_dly`
    and the bureau extract for the month's last days are loaded by then. If not, m1 is
    complete in history but partial in PROD (training/serving skew). *Changes:* run
    later, or end the window at the last complete week.
26. **Persona start versus spine start.** `prm_casa_return_events` starts 6 months before
    `crx_persona.persona_start_date` (2026-01-01 in dev). `cc_spine` may begin earlier
    (model start 2025-01-01); the A1 run now stops in that case. Confirm the spine range.
27. **Month-end shift (temporary).** Until `cc_spine` is month-end, several billing dates
    collapse to one month-end row (largest `cif_id`). Count accounts with more than one
    billing date or more than one `cif_id` in a month.
28. **180+ untested on PROD.** 3 of 6 months with flat floors on a dry segment: expect
    mostly none / Unknown. Run cc_180_plus and look at the distribution before tuning.
