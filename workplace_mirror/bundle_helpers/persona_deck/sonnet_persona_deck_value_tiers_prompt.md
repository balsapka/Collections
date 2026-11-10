# Persona framework numbers for GRR: allocation tiers on expected collections (follow-up)

This follows the refresh run (`fill_in.md`, refresh run 2026-11-10). Only the allocation tiers change; everything else in `fill_in.md` stays as it is. Use subagents where the steps below say so, and review your own work before handing it back.

## 1. Why

The tiers were cut on each combination's **probability** of a meaningful payment. For an allocation decision (in-house, agency or early exit) the expected **money** matters more: a customer with a 20% chance of paying on a large balance can be worth more effort than one with a 40% chance on a small one. So the tiers are now cut on **expected collections per account**: the amount collected in the 3 months after the back-test month, averaged over the combination's accounts. Outstanding principal stays in the picture through the **recovery rate** (collected ÷ outstanding principal), the figure to compare with a sale price.

## 2. Decided (user, 2026-11-11)

- Tier metric = `collected_per_account` (AED, 3 months, back-test May 2026); `recovery_pct` reported beside it; `paid_pct` (meaningful payment) kept as a column.
- Exposure: `prm_balance.bnp_principal` (cards) and `int_loan_master.outstanding_balance` (loans) are both the **outstanding principal**; call them that in `fill_in.md` (not "billed-not-paid", not "ENR").
- Cut-offs (`TIER_CUTS`, AED per account, per product) are set by you **before** the PROD run, from the previous run's `combos_ranked` (section 4). The script refuses to run while they are unset.
- Only `cc_60_180` and `rl_60_180` are rerun. 180+ results stay as they are.
- GRR has not given cost per in-house account, agency commission or sale price; the cut-offs come from the data and are hypotheses.

## 3. Hard rules

As before: your version of `tmp_validation/persona_deck/persona_deck_numbers.py`, catalog loads only, `model_id` from globals, aggregates only, cells under `MIN_CELL` suppressed, no pipeline changes.

## 4. Phase A — UAT

**A1. Choose the cut-offs (subagent, works only from the committed `deck_cc_60_180.json` and `deck_rl_60_180.json`).** From `combos_ranked` (accounts, `collected_aed`, `exposure_aed`, `paid_n` per combination), compute `collected_per_account` and `recovery_pct` per combination, rank by `collected_per_account`, and propose two cut-offs per product:
- **in-house from:** where the top of the ranking stops adding much money per account (look at the capture curve of money collected against accounts);
- **early exit below:** where the bottom combinations together hold only a small share of the money collected (aim for a group that holds about 5% or less of the money; say what it holds).

Return, per product: the two cut-offs in AED, and for each tier the share of accounts, principal, payers and money collected, `collected_per_account` and `recovery_pct`. Also say how this differs from the previous paid-% tiers (how many accounts change tier).

**A2. Implement (main agent).** Set `TIER_CUTS` to the A1 values and replace the tier code with the code below (adapt names if yours differ).

The constant (replaces the old one):

````python
# allocation tiers from a combination's expected collections: the back-test amount
# collected in the next 3 months per account (AED). In-house from the first cut,
# early-exit candidates below the second, agency in between. Set per product from the
# previous run's combos_ranked before running (see the prompt).
TIER_CUTS = {"cc": (None, None), "rl": (None, None)}
````

New and changed helpers (`_values` is new; `_with_tier`, `_tier_of` and `_ranked` replace the old ones):

````python
def _values(bt: DataFrame, by: list) -> pd.DataFrame:
    """``_rates`` + amount collected in the next 3 months, per account and as a share of
    outstanding principal (recovery)."""
    pdf = _rates(bt, by).merge(
        _table(
            bt, by, [F.sum(F.coalesce("paid_next", F.lit(0.0))).alias("collected_aed")]
        )[by + ["collected_aed"]],
        on=by,
    )
    pdf["collected_per_account"] = (pdf["collected_aed"] / pdf["accounts"]).round(0)
    pdf["recovery_pct"] = (
        100.0
        * pdf["collected_aed"]
        / pdf["exposure_aed"].where(pdf["exposure_aed"] > 0)
    ).round(2)
    return pdf


def _with_tier(df: DataFrame, values: pd.DataFrame, p: str, spark) -> DataFrame:
    """``df`` + ``tier`` from its combination's expected collections per account
    (TIER_CUTS); combinations under MIN_CELL back-test accounts are ``unassigned``."""
    ok = values[values["accounts"] >= MIN_CELL]
    tiers = [
        (c, _tier_of(v, p)) for c, v in zip(ok["combo"], ok["collected_per_account"])
    ]
    m = spark.createDataFrame(tiers, "combo string, tier string")
    return df.join(F.broadcast(m), "combo", "left").fillna("unassigned", ["tier"])


def _tier_of(value, p: str) -> str | None:
    hi, lo = TIER_CUTS[p]
    if hi is None or lo is None:
        raise ValueError(f"set TIER_CUTS for {p} first (see the prompt)")
    if value is None or pd.isna(value):
        return None
    return "in_house" if value >= hi else "early_exit" if value < lo else "agency"


def _ranked(bt: DataFrame) -> pd.DataFrame:
    """Combinations ranked by expected collections per account, with cumulative capture:
    the basis for the in-house / agency / early-exit tiers."""
    pdf = _values(bt, ["combo"])
    pdf = pdf[pdf["accounts"] >= MIN_CELL].sort_values(
        "collected_per_account", ascending=False
    )
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
            "collected_per_account",
            "recovery_pct",
            "cum_accounts_pct",
            "cum_principal_pct",
            "cum_payers_pct",
            "cum_collected_pct",
        ]
    ].reset_index(drop=True)
````

The tier block in `main` (replaces the old block from `t["combos_ranked"] = _ranked(bt)` up to the AUC comparison):

````python
    t["combos_ranked"] = _ranked(bt)
    # allocation tiers (in-house / agency / early exit), from expected collections
    spark = latest.sparkSession
    combo_rates = _values(bt, ["combo"])
    latest = _with_tier(latest, combo_rates, p, spark).cache()
    bt = _with_tier(bt, combo_rates, p, spark).cache()
    frame = _with_tier(frame, combo_rates, p, spark)
    tier_bt = _values(bt, ["tier"])
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
                "collected_per_account",
                "recovery_pct",
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
````

The tree (replaces the old tree block):

````python
    tree = _table(latest, ["family", "nuance"]).merge(
        _values(bt, ["family", "nuance"])[
            ["family", "nuance", "paid_pct", "rolled_pct", "collected_per_account"]
        ],
        on=["family", "nuance"],
        how="left",
    )
    tree["tier"] = [_tier_of(v, p) for v in tree["collected_per_account"]]
    t["tree"] = tree
````

**A3. Review (subagent):** check the diff against sections 2 and 3, check that `TIER_CUTS` holds the A1 values, compile. Commit and push.

## 5. Phase B — PROD (the user)

Run the script for `cc_60_180` and `rl_60_180`; commit and push the two refreshed `deck_*` files.

## 6. Phase C — UAT

**C1. Two subagents in parallel**, each reading the two refreshed `deck_*.json` files:
- **C1a Tiers and tree.**
  - Cut-offs used (AED per account), with one line on how they were chosen.
  - Per tier, cards and loans: share of accounts, outstanding principal AED m, `collected_per_account`, `recovery_pct`, paid %, rolled %, amount collected AED m, share of all payers and of all money collected, call days (`tier_summary`).
  - Who is in each tier: the 3 largest family × nuance groups with their share of the tier, in plain words (`tier_composition`).
  - Capture curve: % of money collected, of payers and of outstanding principal held by the top 10 / 20 / 30 / 50 / 80% of accounts ranked by expected collections (`combos_ranked`).
  - Tree: share, paid %, `collected_per_account` and tier for each family × nuance leaf, cards (`tree`).
  - One headline sentence (for example "the top 20% of card accounts hold X% of the money collected").
- **C1b Score, UC1, pilot.**
  - Risk score per tier (`score_tier`), with the verdict rule as before, and the AUC comparison (`score_compare_auc`).
  - UC1 contact per tier (`uc1_by_tier`).
  - Pilot: accounts per tier Jun / Jul / Aug (`tier_volume`); accounts per arm at +5 and +10 pts on the tier's paid %; which tiers fill both arms in one month; the monthly 10% hold-out of early-exit candidates.

**C2. Check (main agent):** tier shares add to 100; money and payer shares add to 100; the tree's family totals still match the family shares; nothing outside the tier sections changed.

**C3.** Replace only the Tiers, Tree, Risk score, UC1 and Pilot sections of `fill_in.md` and fix the exposure wording (section 2). Commit and push, then paste back those sections plus the cut-off note from A1.
