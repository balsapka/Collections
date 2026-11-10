# Persona deck numbers: refresh run (four families, outstanding principal, credibility rule, allocation tiers)

## Goal
Refresh every number of the persona deck in one run, for all four model_ids, after five changes:
1. **Four deterioration families.** Stabilized customers are curing now; slow rollers and repeat delinquents have cured or paid before but are falling now. GRR will see these as different groups.
2. **Exposure = outstanding principal** in every AED figure, never statement balance or total outstanding.
3. **Credibility Unknown narrows (D-A3-27):** an account with an observed delinquency episode but no evidence is Low; Unknown is left only for accounts with no episode.
4. **Allocation tiers.** Part 2 now answers GRR's allocation question at 61–180: which customers to work in-house (extra cost, higher revenue), which to send to an agency, and which are candidates for early sale or write-off instead of being worked until 180+. These are hypotheses for GRR, not decisions.
5. **Risk score and UC1 by tier**, and a check of how well the personas rank customers against the DPD band alone.
6. **Outcome = the risk score's target: a meaningful payment**, not any payment of AED 100 or more (definitions below).

Then rewrite `tmp_validation/persona_deck/fill_in.md` from the refreshed results.

## Decided (user, 2026-11-10)
- **Families** (`det_state` → `family`): `stabilized` → `curing_now`; `slow_roller`, `repeat_delinquent` → `cure_history`; `straight_roller_seasoned`, `straight_roller_early_life` → `stopped_suddenly`; `early_payment_default` → `never_paid`; anything else → `unknown`, as now.
- **Exposure** (`exposure_amt`) = outstanding principal in the observation month, cards and loans alike. It replaces `crx_cc_balance.stmt_balance` (cards) and `crx_rl_full_history.outstanding_balance` (loans). Find the principal column in the catalog datasets the persona code already reads (prm_ / int_ / crx_, never stg_ or raw_), and report the dataset and column per product. If none exists for a product, stop and say so; don't substitute another balance.
- **Credibility (D-A3-27):** an A3 row with `a3_unknown_reason = 'no_evidence'` counts as Low; Unknown stays only for `no_episode`. The A3 pipeline gets the same change in bundle 22; until it is applied, the snippet maps it.
- **Action segments** stay as they are (needed for the regression check): `cure_reach_cred` takes family `curing_now` or `cure_history`.
- **Allocation tiers** come from each combination's back-test paid % (`TIER_CUTS`, per product, provisional): in-house from the first cut, early-exit candidates below the second, agency in between; combinations with fewer than `MIN_CELL` back-test accounts are `unassigned`. Loans use higher cuts because their paid measure (`int_loan_master.total_paid`, monthly) looks inflated against cards. You propose better cut-offs from the capture curve.
- **Outcome (the risk score's target):**
  - **61–180:** a *meaningful payment* within 3 months = in at least one month, the customer paid at least the amount that stabilises the bucket for that month: cards, the amount in the oldest overdue bucket (the one that would roll; A1's anchor); loans, one EMI (`int_loan_master.installment_due_amount`). Use the A3 payment ledger (due and paid per cycle) if it is a catalog dataset; otherwise derive it from the sources the script already reads. Say what you used.
  - **180+:** a meaningful payment within **6 months for early-stage charge-offs** (less than 24 months in 180+, `chargeoff_age_months < 24`) and **12 months for late-stage** (24+ months). The threshold is not settled: compute three variants, **5% of outstanding principal**, **AED 1,000** and **AED 2,000** (cumulative payments in the window). The back-test base moves back 6 / 12 months; if the persona tables don't reach that far, use the longest horizon available and say so.
  - `paid` in every table becomes the meaningful-payment flag; keep the old "any payment of AED 100 or more" as a second column `paid_any_pct` so the two can be compared.
- **All four model_ids** are rerun (the credibility change touches 180+ too). Part 2 is about 61–180; at 180+ only the mixes and the positive signal matter.

## Hard rules
- Edit **your** version of `tmp_validation/persona_deck/persona_deck_numbers.py` (commit 5fc0e8f3 and later). Keep every fix you made to it: payments rebuilt from `crx_cc_transactions` / `int_loan_master`, `crx_rl_dpd_sequences_linked`, NULL buckets, the A2 default, `element_at` guards, the `bt_accounts` suppression and the output folder.
- Catalog loads only. `model_id` comes from globals. Aggregates only: no customer rows in any output; cells under `MIN_CELL` accounts stay suppressed.

## Changes to the script
1. `FAMILY` mapping as above, plus `CAN_CURE = ("curing_now", "cure_history")`; the `action` column's `F.col("family") == "can_cure"` becomes `F.col("family").isin(*CAN_CURE)`.
2. Credibility band: load `a3_unknown_reason` with the A3 output; band = `'low'` where it is `'no_evidence'`, else the band of `a3_state` as now.
3. `_exposure`: outstanding principal as above, same point-in-time join.
4. Next to `a1_family_x_band`: `t["a1_state_outcome"] = _rates(bt, ["det_state"])` and `t["a1_state_x_band"] = _rates(bt, ["dpd_band", "det_state"])`.
5. Combinations: `possible` = number of distinct families in `FAMILY` (4) × 3 × 3 × 4 × 4 = 576; add `non_empty_known_family` (non-empty combinations whose `combo` doesn't start with `unknown`).
6. Allocation tiers. Add the constant next to `ABLE`:

````python
# allocation tiers from a combination's back-test paid %: in-house from the first cut,
# early-exit candidates below the second, agency in between (provisional, per product;
# loans are higher because their paid measure is monthly, see the prompt)
TIER_CUTS = {"cc": (30.0, 5.0), "rl": (60.0, 25.0)}
````

   these helpers before `_flags`:

````python
def _with_tier(df: DataFrame, rates: pd.DataFrame, p: str, spark) -> DataFrame:
    """``df`` + ``tier`` from its combination's back-test paid % (TIER_CUTS);
    combinations under MIN_CELL back-test accounts are ``unassigned``."""
    hi, lo = TIER_CUTS[p]
    ok = rates[rates["accounts"] >= MIN_CELL]
    tiers = [
        (c, "in_house" if r >= hi else "early_exit" if r < lo else "agency")
        for c, r in zip(ok["combo"], ok["paid_pct"])
    ]
    m = spark.createDataFrame(tiers, "combo string, tier string")
    return df.join(F.broadcast(m), "combo", "left").fillna("unassigned", ["tier"])


def _tier_of(rate, p: str) -> str | None:
    hi, lo = TIER_CUTS[p]
    if rate is None or pd.isna(rate):
        return None
    return "in_house" if rate >= hi else "early_exit" if rate < lo else "agency"


def _ranked(bt: DataFrame) -> pd.DataFrame:
    """Combinations ranked by back-test paid %, with cumulative capture: the basis for the
    in-house / agency / early-exit tiers (accounts, principal, payers, amount collected).
    """
    pdf = _rates(bt, ["combo"]).merge(
        _table(
            bt,
            ["combo"],
            [F.sum(F.coalesce("paid_next", F.lit(0.0))).alias("collected_aed")],
        )[["combo", "collected_aed"]],
        on="combo",
    )
    pdf = pdf[pdf["accounts"] >= MIN_CELL].sort_values("paid_pct", ascending=False)
    for col, out in (
        ("accounts", "cum_accounts_pct"),
        ("exposure_aed", "cum_principal_pct"),
        ("paid_n", "cum_payers_pct"),
        ("collected_aed", "cum_collected_pct"),
    ):
        pdf[out] = (100.0 * pdf[col].cumsum() / max(pdf[col].sum(), 1)).round(1)
    pdf["collected_aed"] = pdf["collected_aed"].round(0)
    return pdf[
        [
            "combo",
            "accounts",
            "share_pct",
            "exposure_aed",
            "paid_pct",
            "rolled_pct",
            "cured_pct",
            "collected_aed",
            "cum_accounts_pct",
            "cum_principal_pct",
            "cum_payers_pct",
            "cum_collected_pct",
        ]
    ].reset_index(drop=True)
````

   this block right after `t["combos_top"] = top` in `main` (it reassigns `latest`, `bt` and `frame`, so everything after it sees `tier`):

````python
    t["combos_ranked"] = _ranked(bt)
    # allocation tiers (in-house / agency / early exit), from combination paid %
    spark = latest.sparkSession
    combo_rates = _rates(bt, ["combo"])
    latest = _with_tier(latest, combo_rates, p, spark).cache()
    bt = _with_tier(bt, combo_rates, p, spark).cache()
    frame = _with_tier(frame, combo_rates, p, spark)
    collected = [F.sum(F.coalesce("paid_next", F.lit(0.0))).alias("collected_aed")]
    tier_bt = _rates(bt, ["tier"]).merge(
        _table(bt, ["tier"], collected)[["tier", "collected_aed"]], on="tier"
    )
    for col, out in (
        ("paid_n", "payers_share_pct"),
        ("collected_aed", "collected_share_pct"),
    ):
        tier_bt[out] = (100.0 * tier_bt[col] / max(tier_bt[col].sum(), 1)).round(1)
    t["tier_summary"] = _table(latest, ["tier"]).merge(
        tier_bt[
            [
                "tier",
                "paid_pct",
                "rolled_pct",
                "cured_pct",
                "collected_aed",
                "payers_share_pct",
                "collected_share_pct",
            ]
        ],
        on="tier",
        how="left",
    )
    t["tier_composition"] = _table(latest, ["tier", "family", "nuance"])
    t["tier_volume"] = _table(
        frame.withColumn("month", month), ["month", "tier"]
    ).sort_values(["month", "tier"])
    t["score_tier"] = _score(bt, "tier")
    t["uc1_by_tier"] = _table(
        latest, ["tier"], [F.sum("contact_3m").alias("contact_3m")]
    ).assign(contact_pct=lambda x: (100.0 * x["contact_3m"] / x["accounts"]).round(1))
    leaf = bt.withColumn("leaf", F.concat_ws(" | ", "family", "nuance"))
    auc = {}
    for name, by in (
        ("band", ["dpd_band"]),
        ("tree_leaf", ["leaf"]),
        ("tier", ["tier"]),
        ("band_and_leaf", ["dpd_band", "leaf"]),
        ("band_and_tier", ["dpd_band", "tier"]),
    ):
        cells = _rates(leaf, by)
        auc[name] = {
            "paid": _auc(cells, "paid_n", "accounts"),
            "rolled": _auc(cells, "rolled", "with_history"),
        }
    res["score_compare_auc"] = auc  # in-sample, back-test month
````

   and the tier tag on the tree, just before `t["tree"] = tree`:

````python
tree["tier"] = [_tier_of(r, p) for r in tree["paid_pct"]]
    t["tree"] = tree
````

   If your version names things differently, adapt the code; the tables and their columns are what matter.
7. Collections effort (optional): if an input the script already loads, or the A2 output, carries call attempts per account (for example call days in the last 3 months), add the average per tier to `tier_summary` and per combination to `combos_ranked`. If none is available, say so; don't add a new source.
8. Make sure `res["score_compare_auc"]` is written to the .json and printed in the .md.
9. Outcomes as in Decided: `paid` = meaningful payment (61–180: 3 months, stabilising amount; 180+: 6 / 12 months by vintage, three threshold variants as `paid_5pct`, `paid_1000`, `paid_2000`, with `paid` = the 5% variant), plus `paid_any`. Add `vintage` (`early_stage` / `late_stage`) on the 180+ runs.
10. 180+ tables (on the 180+ model_ids): `positive_signal_outcome` = paid rate (all three variants) for accounts with and without a positive signal, per vintage and per signal; `score_vintage` = the score table with `vintage` in place of `dpd_band` (spread across vintages and vintage-only AUC, per positive-signal group).

## Deliverables
1. **UAT:** apply the changes, check that the script compiles, commit and push.
2. **PROD (user):** run it for `cc_60_180`, `rl_60_180`, `cc_180_plus` and `rl_180_plus`; commit and push the four `deck_<model_id>.md/.json` files.
3. **UAT:** rewrite `fill_in.md` (format `slide · item · value · source table`), commit and push, and paste back the whole file. Sections in this order (cards and loans 61–180 unless noted; mark cells under 10 accounts):
   - **Exposure source:** dataset and column per product.
   - **Summary:** % of reachable who are credible or able, with AED m principal; paid % range across tree leaves at 91–120 (cards); % of 180+ accounts with a positive signal (cards, loans); and the one capture-curve sentence you'd put on the summary slide (for example "the top 20% of card accounts hold X% of payers").
   - **A1 Deterioration:** four family shares; paid in 3 months by family, overall and per DPD band; paid by each of the six states, overall and per DPD band; one-line verdict: does `curing_now` pay at least 5 pts more than `cure_history` in most bands (cards, loans)?
   - **A2 Locatability:** the 3 × 3 matrix; 180+ reachable / in country / both.
   - **A3 Payment credibility:** High / Moderate / Low / Unknown for cards and loans at 61–180 and at 180+; roll % at 91–120, High vs Low (cards); untested share.
   - **A4 Ability:** High / Moderate / Low / Unknown for the four segments.
   - **Part 2, combinations:** possible / non-empty / non-empty with a known family / empty (= possible − non-empty with a known family) / covering 80% / under 0.5%.
   - **Part 2, allocation tiers:**
     - the cut-offs used, and the ones you would propose from the curve with one line why (for example where payer capture flattens). If yours differ from `TIER_CUTS`, say how much each tier's share would move;
     - per tier: share of accounts, principal AED m, paid %, rolled %, cured %, amount collected AED m, share of all payers and of all money collected, call attempts if available (`tier_summary`);
     - per tier, who is in it: the 3 largest family × nuance groups with their share of the tier (`tier_composition`), in plain words;
     - 5 points of the capture curve: % of payers and of money collected held by the top 10 / 20 / 30 / 50 / 80% of accounts ranked by paid % (`combos_ranked`);
     - flag the loan amounts as using `int_loan_master.total_paid`.
   - **Part 2, tree:** share, paid % and tier for each family × nuance leaf, cards (`tree`).
   - **Part 2, risk score:** per tier, size, paid / rolled spread across DPD bands and band-only AUC (`score_tier`), with a verdict: "yes" if spread ≥ 15 pts or AUC ≥ 0.65, "no" if spread < 5 and AUC < 0.58, else "maybe". Then the AUC table (`score_compare_auc`): band alone, tree leaf, tier, band + leaf, band + tier, for paid and rolled, with one line on what it says (in-sample, back-test month).
   - **Part 2, UC1:** % with a right-party contact in the last 3 months, overall and per tier (`uc1_contact`, `uc1_by_tier`).
   - **Part 2, pilot:** accounts per tier in Jun / Jul / Aug (`tier_volume`); accounts per arm for a 2-arm test (two-sided α 0.05, 80% power) at +5 and at +10 pts on the tier's paid %; which tiers fill both arms in one month. Also the size of a 10% hold-out of early-exit candidates per month.
   - **180+:** positive-signal share and each signal (cards, loans); vintage split (early / late stage); meaningful-payment rate with and without a positive signal, per vintage and per signal, for the three thresholds (`positive_signal_outcome`); the score table by vintage (`score_vintage`), with the same verdict rule; and which threshold you'd recommend from the results, in one line.
   - **Outcome check:** for cards and loans 61–180, the meaningful-payment rate next to the old any-payment rate, overall and per tier, so the change of target is visible.
   - **Regression check:** against the previous run, `never_paid`, `not_reachable`, `cure_reach_cred` and `stopped_reach_means` in `action` keep their shares and paid % to the decimal; only `reach_notcred_means` and `other` may move. List any other difference.
   - **Notes:** up to 5 lines on anything that looks wrong.
