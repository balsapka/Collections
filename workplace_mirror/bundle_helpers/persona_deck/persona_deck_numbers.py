"""Persona deck numbers: the aggregates for the management presentation, from the axes.

Reads the axis outputs directly (no persona master needed): crx_<p>_obs_base,
crx_<p>_a1_ability, crx_<p>_a2_locatability, crx_<p>_a3_payment_credibility,
crx_<p>_a4_deterioration, the exposure source (cards: crx_cc_balance; loans:
crx_rl_full_history) and, for outcomes, crx_<p>_dpd_sequences and crx_<p>_a3_payments.

Run in PROD in a Kedro notebook (``catalog`` in scope) or as a script from the repo root.
model_id comes from globals; switch it in globals_dev.yml for the other model_ids.
Aggregates only: no customer rows, cells under MIN_CELL accounts are suppressed.
Writes tmp_validation/persona_deck/deck_<model_id>.{json,md}.

Deck axis names: A1 deterioration (code A4), A2 locatability, A3 payment credibility,
A4 ability (code A1). Tables are named after the slide they fill:
  mix_*        August mix per axis (latest month)
  a2_positive  180+ positives: reachable, in country, both
  a3_*         untested share; outcomes by credibility band within DPD band
  a1_*         outcomes by deterioration family and state (overall and within DPD band)
  uc1_contact  share with a right-party contact in the last 3 months
  positive_*   180+ positive-signal flag, overall and per signal
  combos_*     how concentrated the four-axis combinations are; the largest ones
  tree         the decision-path tree: family > reachable > nuance, share and outcome
  action       the six action segments: share, exposure, outcome
  score_*      outcome spread inside each segment across DPD bands; band-only AUC
  summary_*    the three summary-slide numbers
  volume       monthly accounts per action segment (pilot sample sizes)
"""

# pylint: disable=invalid-name,too-many-locals,import-outside-toplevel,too-many-statements
import json
from pathlib import Path

import pandas as pd
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

HORIZON = 3  # months between the back-test base month and the outcome
MIN_CELL = 10  # smallest account count shown
MIN_PAYMENT_AED = 100  # "any payment" (D-A3-5)
SMALL_COMBO_PCT = 0.5  # a combination under this share counts as (almost) empty
OFFSET = {"cc": 0, "rl": 1}  # native bucket + offset = canonical (A4 constants)
OUT_DIR = Path("tmp_validation/persona_deck")
GRAIN = ["account_id", "observation_date"]

FAMILY = {  # deck A1 families (user, 2026-11-10: stabilized is its own family)
    "stabilized": "curing_now",
    "slow_roller": "cure_history",
    "repeat_delinquent": "cure_history",
    "straight_roller_seasoned": "stopped_suddenly",
    "straight_roller_early_life": "stopped_suddenly",
    "early_payment_default": "never_paid",
}
CAN_CURE = ("curing_now", "cure_history")
ABLE = ("high", "moderate")


def _catalog():
    g = globals()
    if "catalog" in g:
        return g["catalog"]
    from kedro.framework.session import KedroSession
    from kedro.framework.startup import bootstrap_project

    bootstrap_project(Path.cwd())
    return KedroSession.create().load_context().catalog


def _key(col: str = "account_id") -> Column:
    """``col`` as a string ``account_id``."""
    return F.col(col).cast("string").alias("account_id")


def _band_of(state: Column) -> Column:
    """high / moderate / low / unknown from an A1 or A3 state code."""
    s = F.lower(state)
    return (
        F.when(s.contains("high"), "high")
        .when(s.contains("moderate"), "moderate")
        .when(s.contains("low"), "low")
        .otherwise("unknown")
    )


def _dpd_band(canon: Column) -> Column:
    return (
        F.when(canon <= 3, "<=60")
        .when(canon == 4, "061-090")
        .when(canon == 5, "091-120")
        .when(canon == 6, "121-150")
        .when(canon == 7, "151-180")
        .otherwise("181+")
    )


def _in_month(base: DataFrame, src: DataFrame, date_col: str, cols: list) -> DataFrame:
    """The latest ``src`` row in each base row's month (on or before its date)."""
    s = src.select(_key(), F.col(date_col).cast("date").alias("_d"), *cols)
    j = (
        base.select(*GRAIN)
        .join(s, "account_id")
        .filter(
            (F.col("_d") <= F.col("observation_date"))
            & (F.trunc("_d", "month") == F.trunc("observation_date", "month"))
        )
    )
    w = Window.partitionBy(*GRAIN).orderBy(F.col("_d").desc())
    return j.withColumn("_r", F.row_number().over(w)).filter("_r = 1").drop("_r", "_d")


def _exposure(catalog, base: DataFrame, p: str) -> DataFrame:
    if p == "cc":
        bal = catalog.load("crx_cc_balance")
        src = bal.select(
            F.col("contract_id").alias("account_id"),
            "observation_date",
            F.col("stmt_balance").cast("double").alias("exposure_amt"),
            F.lit("credit_card").alias("product"),
        )
        return _in_month(base, src, "observation_date", ["exposure_amt", "product"])
    fh = catalog.load("crx_rl_full_history")
    src = fh.select(
        "account_id",
        F.col("month_end_date").alias("observation_date"),
        F.col("outstanding_balance").cast("double").alias("exposure_amt"),
        F.col("loan_type").cast("string").alias("product"),
    )
    return _in_month(base, src, "observation_date", ["exposure_amt", "product"])


def _frame(catalog, p: str) -> DataFrame:
    """One row per observation: the axis fields the deck needs, exposure, DPD band."""
    base = catalog.load(f"crx_{p}_obs_base").select(_key(), "observation_date")
    a1 = catalog.load(f"crx_{p}_a1_ability")  # deck A4 ability
    a2 = catalog.load(f"crx_{p}_a2_locatability")
    a3 = catalog.load(f"crx_{p}_a3_payment_credibility")
    a4 = catalog.load(f"crx_{p}_a4_deterioration")  # deck A1 deterioration
    parts = [
        a1.select(_key(), "observation_date", F.col("a1_state")),
        a2.select(
            _key(),
            "observation_date",
            "location_state",
            "reachability_state",
            "deceased_flag",
        ),
        a3.select(
            _key(),
            "observation_date",
            "a3_state",
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
            "dlq_payment_any_flag",
            "last_rpc_date",
        ),
        _in_month(base, a4, "observation_date", ["det_state", "current_bucket"]),
        _exposure(catalog, base, p),
    ]
    df = base
    for part in parts:
        df = df.join(part, GRAIN, "left")
    fam = F.create_map(*[F.lit(x) for kv in FAMILY.items() for x in kv])
    canon = F.greatest(F.col("current_bucket") + OFFSET[p], F.lit(1))
    reach = F.col("reachability_state") == "reachable"
    a3b, a4b = _band_of(F.col("a3_state")), _band_of(F.col("a1_state"))
    return (
        df.withColumn("family", F.coalesce(fam[F.col("det_state")], F.lit("unknown")))
        .withColumn("location", F.coalesce("location_state", F.lit("unknown")))
        .withColumn("reach", F.coalesce("reachability_state", F.lit("unknown")))
        .withColumn("credibility", a3b)
        .withColumn("ability", a4b)
        .withColumn("dpd_band", _dpd_band(canon))
        .withColumn("is_reachable", reach)
        .withColumn(
            "nuance",
            F.when(~reach, "not_reachable")
            .when(a3b.isin(*ABLE) | a4b.isin(*ABLE), "credible_or_able")
            .otherwise("neither"),
        )
        .withColumn(
            "action",
            F.when(F.col("family") == "never_paid", "never_paid")
            .when(~reach, "not_reachable")
            .when(F.col("family").isin(*CAN_CURE) & a3b.isin(*ABLE), "cure_reach_cred")
            .when(
                (F.col("family") == "stopped_suddenly") & a4b.isin(*ABLE),
                "stopped_reach_means",
            )
            .when((a3b == "low") & a4b.isin(*ABLE), "reach_notcred_means")
            .otherwise("other"),
        )
        .withColumn(
            "sig_payment",
            (F.coalesce("dlq_payment_any_flag", F.lit(0)) > 0).cast("int"),
        )
        .withColumn(
            "sig_promise",
            (
                F.coalesce("commitments_kept", F.lit(0))
                + F.coalesce("commitments_partial", F.lit(0))
                > 0
            ).cast("int"),
        )
        .withColumn("sig_reachable", reach.cast("int"))
        .withColumn("sig_ability", a4b.isin(*ABLE).cast("int"))
        .withColumn(
            "positive_signal",
            F.greatest("sig_payment", "sig_promise", "sig_reachable", "sig_ability"),
        )
        .withColumn(
            "untested", (F.coalesce("commitments_concluded", F.lit(0)) == 0).cast("int")
        )
        .withColumn(
            "contact_3m",
            (
                F.col("last_rpc_date").isNotNull()
                & (F.col("last_rpc_date") > F.add_months("observation_date", -3))
            ).cast("int"),
        )
        .withColumn(
            "combo",
            F.concat_ws(" | ", "family", "location", "reach", "credibility", "ability"),
        )
    )


def _outcomes(base: DataFrame, seq: DataFrame, pay: DataFrame, p: str) -> DataFrame:
    """Bucket HORIZON months later (cured / improved / held / rolled) and any payment
    of MIN_PAYMENT_AED or more in the HORIZON months after the observation date."""
    off = OFFSET[p]
    s = seq.select(_key(), "first_month", "last_month", "dlq_buckets")
    later = F.last_day(F.add_months("observation_date", HORIZON))
    idx = F.months_between(later, F.col("first_month")).cast("int") + 1
    df = base.join(s, "account_id", "left").withColumn(
        "canon_now", F.greatest(F.col("current_bucket") + off, F.lit(1))
    )
    df = df.withColumn(
        "canon_later",
        F.when(
            F.col("dlq_buckets").isNotNull() & (later <= F.col("last_month")),
            F.greatest(F.element_at("dlq_buckets", idx) + off, F.lit(1)),
        ),
    )
    move = (
        F.when(F.col("canon_later").isNull(), "no_history")
        .when(F.col("canon_later") <= 1, "cured")
        .when(F.col("canon_later") < F.col("canon_now"), "improved")
        .when(F.col("canon_later") == F.col("canon_now"), "held")
        .otherwise("rolled")
    )
    paid = (
        df.select(*GRAIN)
        .join(pay.select(_key(), "pay_date", "amount"), "account_id")
        .filter(
            (F.col("pay_date") > F.col("observation_date"))
            & (F.col("pay_date") <= later)
        )
        .groupBy(*GRAIN)
        .agg(F.sum("amount").alias("paid_next"))
    )
    return (
        df.withColumn("move", move)
        .join(paid, GRAIN, "left")
        .withColumn(
            "paid", (F.coalesce("paid_next", F.lit(0.0)) >= MIN_PAYMENT_AED).cast("int")
        )
        .drop("dlq_buckets")
    )


def _table(df: DataFrame, by: list, extra: list | None = None) -> pd.DataFrame:
    aggs = [
        F.count("*").alias("accounts"),
        F.sum(F.coalesce("exposure_amt", F.lit(0.0))).alias("exposure_aed"),
    ] + (extra or [])
    pdf = df.groupBy(*by).agg(*aggs).toPandas().fillna({c: "NULL" for c in by})
    pdf["share_pct"] = (100.0 * pdf["accounts"] / max(pdf["accounts"].sum(), 1)).round(
        1
    )
    pdf["exposure_aed"] = pdf["exposure_aed"].round(0)
    return pdf.sort_values("accounts", ascending=False).reset_index(drop=True)


def _rates(df: DataFrame, by: list) -> pd.DataFrame:
    has = F.col("move") != "no_history"
    extra = [
        F.sum(has.cast("int")).alias("with_history"),
        *[
            F.sum((F.col("move") == m).cast("int")).alias(m)
            for m in ("cured", "improved", "held", "rolled")
        ],
        F.sum("paid").alias("paid_n"),
    ]
    pdf = _table(df, by, extra)
    h = pdf["with_history"].clip(lower=1)
    for m in ("cured", "rolled"):
        pdf[f"{m}_pct"] = (100.0 * pdf[m] / h).round(1)
    pdf["paid_pct"] = (100.0 * pdf["paid_n"] / pdf["accounts"]).round(1)
    return pdf


def _flags(df: DataFrame, cols: list) -> pd.DataFrame:
    n = df.count()
    row = df.agg(*[F.sum(c).alias(c) for c in cols]).first().asDict()
    return pd.DataFrame(
        [
            {
                "flag": c,
                "accounts": int(row[c] or 0),
                "share_pct": round(100.0 * (row[c] or 0) / max(n, 1), 1),
            }
            for c in cols
        ]
    )


def _auc(pdf: pd.DataFrame, pos: str, n: str) -> float | None:
    """AUC of ranking the rows of ``pdf`` (cells) by their observed ``pos`` rate."""
    g = pdf[pdf[n] > 0].assign(
        neg=lambda x: x[n] - x[pos], rate=lambda x: x[pos] / x[n]
    )
    g = g.sort_values("rate")
    P, N = g[pos].sum(), g["neg"].sum()
    if not P or not N:
        return None
    below, acc = 0.0, 0.0
    for _, r in g.iterrows():
        acc += r[pos] * (below + 0.5 * r["neg"])
        below += r["neg"]
    return round(acc / (P * N), 3)


def _score(bt: DataFrame, seg: str) -> pd.DataFrame:
    """Per segment: outcome spread across DPD bands and the band-only AUC inside it."""
    r = _rates(bt, [seg, "dpd_band"])
    out = []
    for s, g in r.groupby(seg):
        ok = g[g["accounts"] >= MIN_CELL]
        out.append(
            {
                seg: s,
                "accounts": int(g["accounts"].sum()),
                "paid_pct": round(
                    100.0 * g["paid_n"].sum() / max(g["accounts"].sum(), 1), 1
                ),
                "paid_spread_pts": (
                    round(ok["paid_pct"].max() - ok["paid_pct"].min(), 1)
                    if len(ok) > 1
                    else None
                ),
                "rolled_spread_pts": (
                    round(ok["rolled_pct"].max() - ok["rolled_pct"].min(), 1)
                    if len(ok) > 1
                    else None
                ),
                "auc_band_paid": _auc(g, "paid_n", "accounts"),
                "auc_band_rolled": _auc(g, "rolled", "with_history"),
            }
        )
    return pd.DataFrame(out).sort_values("accounts", ascending=False)


def _suppress(pdf: pd.DataFrame) -> pd.DataFrame:
    if "accounts" not in pdf.columns:
        return pdf
    out = pdf.copy().astype(object)
    small = pdf["accounts"] < MIN_CELL
    keys = list(pdf.columns[: list(pdf.columns).index("accounts")])
    for c in out.columns:
        if c not in keys:
            out.loc[small, c] = f"<{MIN_CELL}" if c == "accounts" else None
    return out


def _markdown(pdf: pd.DataFrame) -> str:
    head = "| " + " | ".join(map(str, pdf.columns)) + " |"
    rule = "|" + "---|" * len(pdf.columns)
    rows = [
        "| "
        + " | ".join(
            "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
            for v in r
        )
        + " |"
        for r in pdf.itertuples(index=False)
    ]
    return "\n".join([head, rule, *rows])


def main() -> None:
    """Build every table and write deck_<model_id>.json and .md."""
    catalog = _catalog()
    model_id = catalog.load("params:model_id")
    p = model_id[:2]
    end = str(catalog.load("params:crx_persona")["persona_end_date"])
    month = F.trunc("observation_date", "month")
    frame = _frame(catalog, p).cache()
    latest = frame.filter(month == F.trunc(F.lit(end), "month")).cache()
    bt = _outcomes(
        frame.filter(month == F.add_months(F.trunc(F.lit(end), "month"), -HORIZON)),
        catalog.load(f"crx_{p}_dpd_sequences"),
        catalog.load(f"crx_{p}_a3_payments"),
        p,
    ).cache()
    t: dict[str, pd.DataFrame] = {}
    res: dict = {"model_id": model_id, "persona_end_date": end}

    # August mix per axis (deck A1..A4)
    t["mix_a1_family"] = _table(latest, ["family"])
    t["mix_a1_state"] = _table(latest, ["det_state"])
    t["mix_a2_matrix"] = _table(latest, ["location", "reach"])
    t["mix_a2_deceased"] = _table(latest, ["deceased_flag"])
    t["mix_a3_band"] = _table(latest, ["credibility"])
    t["mix_a4_band"] = _table(latest, ["ability"])
    t["a2_positive"] = _flags(
        latest.withColumn(
            "in_country", (F.col("location") == "in_country").cast("int")
        ).withColumn(
            "in_country_and_reachable",
            ((F.col("location") == "in_country") & F.col("is_reachable")).cast("int"),
        ),
        ["sig_reachable", "in_country", "in_country_and_reachable"],
    )
    # outcomes (deck A1 and A3 insights)
    t["a1_family_outcome"] = _rates(bt, ["family"])
    t["a1_family_x_band"] = _rates(bt, ["dpd_band", "family"])
    t["a1_state_outcome"] = _rates(bt, ["det_state"])
    t["a1_state_x_band"] = _rates(bt, ["dpd_band", "det_state"])
    t["a3_band_x_band"] = _rates(bt, ["dpd_band", "credibility"])
    t["a3_untested"] = _flags(latest, ["untested"])
    t["uc1_contact"] = _flags(latest, ["contact_3m"])
    # 180+ positive signal (meaningful on the 180+ model_ids)
    t["positive_signal"] = _flags(
        latest,
        [
            "positive_signal",
            "sig_payment",
            "sig_promise",
            "sig_reachable",
            "sig_ability",
        ],
    )
    # combinations
    combos = _table(latest, ["combo"])
    cum = combos["share_pct"].cumsum()
    res["combos"] = {
        "possible": len(set(FAMILY.values()))
        * 3
        * 3
        * 4
        * 4,  # families x location x reach x credibility x ability
        "non_empty": int((combos["accounts"] > 0).sum()),
        "non_empty_known_family": int(
            (
                (combos["accounts"] > 0) & ~combos["combo"].str.startswith("unknown")
            ).sum()
        ),
        "cover_80pct": int((cum < 80).sum() + 1),
        "under_small_pct": int((combos["share_pct"] < SMALL_COMBO_PCT).sum()),
        "small_pct": SMALL_COMBO_PCT,
    }
    top = combos.head(10).merge(
        _rates(bt, ["combo"])[["combo", "paid_pct", "rolled_pct"]],
        on="combo",
        how="left",
    )
    t["combos_top"] = top
    # tree, action segments, score
    tree = _table(latest, ["family", "nuance"]).merge(
        _rates(bt, ["family", "nuance"])[
            ["family", "nuance", "paid_pct", "rolled_pct"]
        ],
        on=["family", "nuance"],
        how="left",
    )
    t["tree"] = tree
    t["tree_x_band"] = _rates(bt, ["dpd_band", "family", "nuance"])
    t["action"] = _table(latest, ["action"]).merge(
        _rates(bt, ["action"])[["action", "paid_pct", "rolled_pct"]],
        on="action",
        how="left",
    )
    t["score_action"] = _score(bt, "action")
    t["score_tree"] = _score(
        bt.withColumn("leaf", F.concat_ws(" | ", "family", "nuance")), "leaf"
    )
    t["volume"] = _table(
        frame.withColumn("month", month), ["month", "action"]
    ).sort_values(["month", "action"])
    # summary numbers
    reach = latest.filter("is_reachable")
    good = reach.filter(F.col("nuance") == "credible_or_able")
    n_all, n_reach, n_good = latest.count(), reach.count(), good.count()
    expo = good.agg(F.sum(F.coalesce("exposure_amt", F.lit(0.0)))).first()[0] or 0.0
    leaves = t["tree_x_band"]
    b = leaves[(leaves["dpd_band"] == "091-120") & (leaves["accounts"] >= MIN_CELL)]
    res["summary"] = {
        "reachable_pct_of_all": round(100.0 * n_reach / max(n_all, 1), 1),
        "credible_or_able_pct_of_reachable": round(100.0 * n_good / max(n_reach, 1), 1),
        "credible_or_able_exposure_aed_m": round(expo / 1e6, 1),
        "paid_pct_range_091_120": (
            [float(b["paid_pct"].min()), float(b["paid_pct"].max())] if len(b) else None
        ),
        "positive_signal_pct": float(t["positive_signal"].iloc[0]["share_pct"]),
        "latest_accounts": n_all,
        "backtest_base": str(bt.select(F.min("observation_date")).first()[0]),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shown = {k: _suppress(v) for k, v in t.items()}
    payload = {**res, "tables": {k: v.to_dict("records") for k, v in shown.items()}}
    (OUT_DIR / f"deck_{model_id}.json").write_text(
        json.dumps(payload, default=str, indent=1)
    )
    lines = [f"# Persona deck numbers — {model_id}, {end}", ""]
    for k in ("summary", "combos"):
        lines += [f"**{k}**: `{json.dumps(res[k], default=str)}`", ""]
    for k, v in shown.items():
        lines += [f"## {k}", "", _markdown(v), ""]
    (OUT_DIR / f"deck_{model_id}.md").write_text("\n".join(lines))
    print(f"wrote {OUT_DIR}/deck_{model_id}.json and .md")


if __name__ == "__main__" or "catalog" in globals():
    main()
