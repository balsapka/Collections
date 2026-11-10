# Persona framework numbers for GRR: refresh run

You are refreshing the aggregate numbers behind a management presentation on the persona framework (the presentation itself is not in this repo; you only produce the numbers), in one pass, for all four model_ids. It is a large job with several independent pieces: plan it, **use subagents for the independent tasks** (each phase below says which can run in parallel), and review your own work before you hand anything back. There is no token limit; correctness matters more than speed.

---

## 1. Context

The numbers go to the head of GRR. Four axes describe each delinquent account every month. In `fill_in.md` use these labels: **A1 Deterioration** (`crx_<p>_a4_deterioration`), **A2 Locatability** (`crx_<p>_a2_locatability`), **A3 Payment credibility** (`crx_<p>_a3_payment_credibility`), **A4 Ability** (`crx_<p>_a1_ability`). Code and catalog keep their own numbering; the labels apply only to `fill_in.md`.

The second half of the analysis answers GRR's allocation question at 61–180 DPD: which customers to work **in-house** (extra cost, higher revenue), which to send to an **agency**, and which are **early-exit candidates** (early sale or write-off instead of being worked until 180+). These are hypotheses for a GRR workshop, not decisions. It also asks whether a risk score is still needed, where the call-transcript work (UC1) adds most, and how to pilot.

The script you wrote earlier, `tmp_validation/persona_deck/persona_deck_numbers.py` (commit 5fc0e8f3 and later), and its `fill_in.md` are the starting point.

## 2. What changes

1. **Four deterioration families** instead of three.
2. **Exposure = outstanding principal** in every AED figure.
3. **Credibility Unknown narrows** (D-A3-27).
4. **Outcome = the risk score's target, a meaningful payment**, instead of any payment of AED 100 or more.
5. **Allocation tiers** (in-house / agency / early exit) built from the four-axis combinations.
6. **Risk score, UC1 and pilot sizing per tier**, plus a ranking comparison (DPD band vs personas).
7. **180+:** does the positive signal pick out payers, and can a score rank within vintages.

## 3. Decided (user, 2026-11-10) — do not re-open

**Families** (`det_state` → `family`):
- `stabilized` → `curing_now`
- `slow_roller`, `repeat_delinquent` → `cure_history`
- `straight_roller_seasoned`, `straight_roller_early_life` → `stopped_suddenly`
- `early_payment_default` → `never_paid`
- anything else → `unknown`

**Exposure** (`exposure_amt`) = outstanding principal in the observation month, cards and loans. It replaces `crx_cc_balance.stmt_balance` and `crx_rl_full_history.outstanding_balance`. Take it from catalog datasets the persona code already reads (prm_ / int_ / crx_, never stg_ or raw_). If a product has no outstanding-principal column, stop and report it; never substitute another balance.

**Credibility (D-A3-27):** an A3 row with `a3_unknown_reason = 'no_evidence'` counts as **Low**; Unknown stays only for `no_episode`. (Bundle 22 makes the same change in the A3 pipeline; until it is applied the script maps it, and afterwards the mapping simply finds nothing.)

**Outcome (the risk score's target):**
- **61–180:** a meaningful payment within **3 months** = in at least one month, the customer paid at least the amount that stabilises the bucket for that month: **cards**, the amount in the oldest overdue bucket (the one that would roll, A1's anchor); **loans**, one EMI (`int_loan_master.installment_due_amount`).
- **180+:** a meaningful payment within **6 months for early-stage charge-offs** (less than 24 months in 180+, `chargeoff_age_months < 24`) and **12 months for late-stage** (24+ months), cumulative payments in the window. The threshold is not settled, so compute three variants: **5% of outstanding principal**, **AED 1,000**, **AED 2,000**. The back-test base moves back 6 / 12 months; if the persona tables don't reach that far, use the longest horizon available and say so.
- `paid` in every table = the meaningful-payment flag (180+: the 5% variant, with `paid_1000` and `paid_2000` beside it). Keep the old "any payment of AED 100+" as `paid_any`, so the change of target is visible.

**Action segments** stay (they are the regression check): `cure_reach_cred` takes family `curing_now` or `cure_history`.

**Allocation tiers:** each combination (family | location | reachability | credibility | ability) gets its back-test paid %; in-house from the first cut, early-exit below the second, agency between (`TIER_CUTS`, per product, provisional: they were set for the old outcome and will need recalibrating). Combinations under `MIN_CELL` back-test accounts are `unassigned`. Loans use higher cuts because their payments come from a monthly field that looks inflated against cards.

## 4. Hard rules

- Edit your version of the script; keep every fix already in it (payments rebuilt from `crx_cc_transactions` / `int_loan_master`, `crx_rl_dpd_sequences_linked`, NULL buckets, the A2 default, `element_at` guards, `bt_accounts` suppression, output folder).
- Catalog loads only. `model_id` from globals, never hardcoded. Aggregates only: no customer rows in any output; cells under `MIN_CELL` stay suppressed.
- No pipeline, catalog or registry changes: this is a validation snippet in `tmp_validation/`.

---

## 5. Phase A — UAT: update the script

**A1. Discovery (run these three subagents in parallel; each returns a short written answer with dataset, columns and evidence from the code or catalog):**
- **A1a Exposure:** which dataset and column hold outstanding principal for cards and for loans in the observation month, and how to join them point-in-time to `(account_id, observation_date)`.
- **A1b Outcome inputs:** for 61–180, where to get per month (i) the amount paid and (ii) the stabilising amount: cards, the oldest overdue bucket amount (look at how the A1 anchor node builds it); loans, `installment_due_amount`. Check whether the A3 payment ledger (due and paid per cycle) is a catalog dataset that already carries this. For 180+, where `chargeoff_age_months` (or equivalent) lives, and how far back the obs base and the payment sources reach.
- **A1c Effort (optional):** does any input the script already loads, or the A2 output, carry call attempts per account (for example call days in the last 3 months)? If not, say so; don't add a source.

**A2. Implement (main agent, using the A1 answers):**
1. `FAMILY` mapping as in section 3, plus `CAN_CURE = ("curing_now", "cure_history")`; in the `action` column, `F.col("family") == "can_cure"` becomes `F.col("family").isin(*CAN_CURE)`.
2. Credibility band: load `a3_unknown_reason`; band = `'low'` where it is `'no_evidence'`, else the band of `a3_state`.
3. `_exposure`: outstanding principal (A1a).
4. Outcomes: `paid` = meaningful payment per section 3, `paid_any` = the old flag, and on 180+ runs `vintage` (`early_stage` / `late_stage`) and `paid_1000`, `paid_2000`. `_rates` reports `paid_pct` and `paid_any_pct` (and the two extra variants on 180+).
5. Next to `a1_family_x_band`: `t["a1_state_outcome"] = _rates(bt, ["det_state"])` and `t["a1_state_x_band"] = _rates(bt, ["dpd_band", "det_state"])`.
6. Combinations: `possible` = number of distinct families in `FAMILY` (4) × 3 × 3 × 4 × 4 = 576; add `non_empty_known_family` (non-empty combinations whose `combo` doesn't start with `unknown`).
7. Allocation tiers. The constant, next to `ABLE`:

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

   this block right after `t["combos_top"] = top` in `main` (it reassigns `latest`, `bt` and `frame`, so every later table sees `tier`):

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

   Adapt names to your version if they differ; the tables and their columns are what matter.
8. Effort (if A1c found a source): average call attempts per tier in `tier_summary` and per combination in `combos_ranked`.
9. 180+ tables (computed on the 180+ model_ids): `positive_signal_outcome` = paid rate (all three variants) with and without a positive signal, per vintage and per signal; `score_vintage` = the score table with `vintage` in place of `dpd_band`, per positive-signal group.
10. `res["score_compare_auc"]` and every new table go into the .json and the .md.

**A3. Review (one subagent, fresh eyes):** read the diff against section 3 and 4 line by line: families, credibility mapping, exposure source, both outcome definitions (windows, thresholds, vintage), tier logic, suppression, no customer rows, `model_id` from globals. It returns a list of issues; fix them, then compile the script (`python -m py_compile`). Commit and push.

## 6. Phase B — PROD (the user)

Run the script for `cc_60_180`, `rl_60_180`, `cc_180_plus` and `rl_180_plus` (switch `model_id` in `globals_dev.yml`), then commit and push the four `deck_<model_id>.md/.json` files.

Optional second pass: if in Phase C you propose tier cut-offs that move any tier's share by more than 5 pts, say so clearly and give the new `TIER_CUTS`; the user may rerun the two 61–180 model_ids before you finish `fill_in.md`.

## 7. Phase C — UAT: analyse and write `fill_in.md`

**C1. Sections (run these five subagents in parallel, each reading the four `deck_*.json` files and returning its section in the format `section · item · value · source table`; cards and loans 61–180 unless noted; mark cells under 10 accounts):**

- **C1a Axes and summary.**
  - Exposure source per product.
  - Summary: % of reachable who are credible or able, with AED m principal; % of 180+ accounts with a positive signal (cards, loans).
  - A1 Deterioration: four family shares; paid in 3 months by family, overall and per DPD band; paid by each of the six states, overall and per DPD band; one-line verdict: does `curing_now` pay at least 5 pts more than `cure_history` in most bands (cards, loans)?
  - A2 Locatability: the 3 × 3 matrix; 180+ reachable / in country / both.
  - A3 Payment credibility: High / Moderate / Low / Unknown at 61–180 and at 180+ (cards, loans); roll % at 91–120, High vs Low (cards); untested share.
  - A4 Ability: High / Moderate / Low / Unknown for the four segments.
- **C1b Tiers and tree.**
  - Combinations: possible / non-empty / non-empty with a known family / empty (= possible − non-empty with a known family) / covering 80% / under 0.5%.
  - Tiers: per tier, share of accounts, principal AED m, paid %, paid-any %, rolled %, cured %, amount collected AED m, share of all payers and of all money collected, call attempts if available (`tier_summary`); who is in each tier, the 3 largest family × nuance groups with their share of the tier (`tier_composition`), in plain words.
  - Capture curve: % of payers and of money collected held by the top 10 / 20 / 30 / 50 / 80% of accounts ranked by paid % (`combos_ranked`).
  - Cut-offs: the ones used, and the ones you'd propose from the curve with one line why (for example where payer capture flattens). Evaluate your proposal offline from `combos_ranked` and give each tier's share under it.
  - Tree: share, paid % and tier for each family × nuance leaf, cards (`tree`).
  - One headline sentence from the curve (for example "the top 20% of card accounts hold X% of payers").
  - Flag that loan amounts come from `int_loan_master.total_paid`.
- **C1c Risk score.** Per tier: size, paid / rolled spread across DPD bands and band-only AUC (`score_tier`), with a verdict: "yes" if spread ≥ 15 pts or AUC ≥ 0.65, "no" if spread < 5 and AUC < 0.58, else "maybe". The AUC comparison (`score_compare_auc`): band alone, tree leaf, tier, band + leaf, band + tier, for paid and rolled, with one line on what it says (in-sample, back-test month).
- **C1d UC1 and pilot.** % with a right-party contact in the last 3 months, overall and per tier (`uc1_contact`, `uc1_by_tier`). Accounts per tier in Jun / Jul / Aug (`tier_volume`); accounts per arm for a 2-arm test (two-sided α 0.05, 80% power) at +5 and +10 pts on the tier's paid %; which tiers fill both arms in one month; the monthly size of a 10% hold-out of early-exit candidates.
- **C1e 180+.** Positive-signal share and each signal (cards, loans); vintage split; meaningful-payment rate with and without a positive signal, per vintage and per signal, for the three thresholds (`positive_signal_outcome`); the score table by vintage (`score_vintage`) with the same verdict rule; which threshold you'd recommend, in one line.

**C2. Checks (main agent, after C1):**
- **Regression:** against the previous run, `never_paid`, `not_reachable`, `cure_reach_cred` and `stopped_reach_means` in `action` keep their shares to the decimal (paid % changes with the new outcome; compare `paid_any_pct` instead, which must match). Only `reach_notcred_means` and `other` may move. List any other difference.
- **Outcome check:** meaningful-payment vs any-payment rate, overall and per tier, cards and loans.
- **Consistency:** shares add to 100 within rounding; tier shares add up; the tree's family totals match the family shares; the four families sum to the old "can cure" + the rest.

**C3. Write** `fill_in.md` in this order: Exposure source · Summary · A1 · A2 · A3 · A4 · Combinations · Tiers · Tree · Risk score · UC1 · Pilot · 180+ · Regression · Outcome check · Notes (up to 5 lines on anything that looks wrong). Commit and push, then **paste back the whole file**.
