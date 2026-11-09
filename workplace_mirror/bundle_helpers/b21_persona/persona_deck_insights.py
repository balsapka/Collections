"""Persona deck insights: aggregates for the GRR deck from crx_<p>_persona_master.

Run in PROD in a Kedro notebook (``catalog`` in scope) or as a script from the repo
root (bootstraps a session). model_id comes from globals; switch it in globals_dev.yml
for the other model_ids. Writes aggregates only (no customer rows; cells under
MIN_CELL accounts are suppressed) to
tmp_validation/persona_deck/results_<model_id>.{json,md}.

Sections
  S1  latest month: axis states, segment x contact route, journey, reasons, product
  S2  trend: monthly shares of the persona layer and each axis state
  S3  back-test: states HORIZON months before the latest month vs what happened next
      (bucket move, cure, any payment), by axis, segment, route, and segment within the
      DPD band; AUC of the DPD band alone vs band + segment
  S4  overlap: Cramer's V between the axes (and the DPD band) in the latest month
"""

# pylint: disable=invalid-name,too-many-locals,import-outside-toplevel
import json
import math
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

HORIZON = 3  # months between the back-test base month and the outcome
MIN_CELL = 10  # smallest account count shown
MIN_PAYMENT_AED = 100  # "any payment", as A3 (D-A3-5)
OFFSET = {"cc": 0, "rl": 1}  # native bucket + offset = canonical (A4 constants)
OUT_DIR = Path("tmp_validation/persona_deck")
AXES = {
    "a1": "a1_state",
    "a2": "a2_state",
    "location": "location_state",
    "reachability": "reachability_state",
    "a3": "a3_state",
    "a4": "det_state",
}
PERSONA = [
    "persona_segment",
    "persona_contact_route",
    "persona_journey_group",
    "persona_ability_band",
    "persona_credibility_band",
]
REASONS = [
    "a1_unknown_reason",
    "a1_income_source",
    "a1_income_level",
    "a1_liquidity_level",
    "a1_distress_flag",
    "a1_salary_stopped",
    "location_rule",
    "location_unknown_reason",
    "reachability_unknown_reason",
    "deceased_source",
    "a3_reason",
    "a3_unknown_reason",
    "a3_commitments_level",
    "a3_dlq_payment_level",
    "a3_pre_dlq_payment_level",
    "a3_refusal_flag",
]


def _catalog():
    g = globals()
    if "catalog" in g:
        return g["catalog"]
    from kedro.framework.session import KedroSession
    from kedro.framework.startup import bootstrap_project

    bootstrap_project(Path.cwd())
    return KedroSession.create().load_context().catalog


def _band(canon: F.Column) -> F.Column:
    """DPD band of a canonical bucket (4 = 61-90 ... 8+ = 181+)."""
    return (
        F.when(canon <= 3, "<=60")
        .when(canon == 4, "061-090")
        .when(canon == 5, "091-120")
        .when(canon == 6, "121-150")
        .when(canon == 7, "151-180")
        .otherwise("181+")
    )


def _table(df: DataFrame, by: list[str], extra: list | None = None) -> pd.DataFrame:
    """Accounts, share and exposure per ``by`` cell (+ ``extra`` aggregates)."""
    aggs = [
        F.count("*").alias("accounts"),
        F.sum(F.coalesce("exposure_amt", F.lit(0.0))).alias("exposure_aed"),
    ] + (extra or [])
    pdf = df.groupBy(*by).agg(*aggs).toPandas()
    pdf = pdf.fillna({c: "NULL" for c in by})
    total = pdf["accounts"].sum()
    pdf["share_pct"] = (100.0 * pdf["accounts"] / max(total, 1)).round(1)
    pdf["exposure_aed"] = pdf["exposure_aed"].round(0)
    return pdf.sort_values(by).reset_index(drop=True)


def _suppress(pdf: pd.DataFrame) -> pd.DataFrame:
    """Blank every value of a cell with fewer than MIN_CELL accounts."""
    out = pdf.copy()
    small = out["accounts"] < MIN_CELL
    for c in out.columns:
        if c not in out.columns[: list(out.columns).index("accounts")]:
            out[c] = out[c].astype(object)
            out.loc[small, c] = f"<{MIN_CELL}" if c == "accounts" else None
    return out


def _markdown(pdf: pd.DataFrame) -> str:
    """``pdf`` as a markdown table (no tabulate dependency)."""
    head = "| " + " | ".join(map(str, pdf.columns)) + " |"
    rule = "|" + "---|" * len(pdf.columns)
    rows = [
        "| " + " | ".join("" if v is None else str(v) for v in r) + " |"
        for r in pdf.itertuples(index=False)
    ]
    return "\n".join([head, rule, *rows])


def _auc(pdf: pd.DataFrame, cell: list[str], pos: str, n: str) -> float | None:
    """AUC of ranking cells by their observed ``pos`` rate (in sample; ties = 0.5)."""
    g = pdf.groupby(cell)[[pos, n]].sum()
    g["neg"] = g[n] - g[pos]
    g = g[g[n] > 0].assign(rate=lambda x: x[pos] / x[n]).sort_values("rate")
    P, N = g[pos].sum(), g["neg"].sum()
    if not P or not N:
        return None
    below, acc = 0.0, 0.0
    for _, r in g.iterrows():
        acc += r[pos] * (below + 0.5 * r["neg"])
        below += r["neg"]
    return round(acc / (P * N), 3)


def _cramers_v(df: DataFrame, a: str, b: str) -> float | None:
    ct = df.groupBy(a, b).count().toPandas().fillna("NULL")
    t = ct.pivot_table(index=a, columns=b, values="count", fill_value=0)
    n = t.values.sum()
    if n == 0 or min(t.shape) < 2:
        return None
    exp = t.sum(1).values[:, None] * t.sum(0).values[None, :] / n
    chi2 = (((t.values - exp) ** 2) / exp).sum()
    return round(math.sqrt(chi2 / (n * (min(t.shape) - 1))), 3)


def _outcomes(base: DataFrame, seq: DataFrame, pay: DataFrame, p: str) -> DataFrame:
    """Base rows + canonical bucket now and HORIZON months later, the move, any
    payment of MIN_PAYMENT_AED or more in the HORIZON months after the base date."""
    off = OFFSET[p]
    s = seq.select(
        F.col("account_id").cast("string").alias("account_id"),
        "first_month",
        "last_month",
        "dlq_buckets",
    )
    later = F.last_day(F.add_months("observation_date", HORIZON))
    idx = F.months_between(later, F.col("first_month")).cast("int") + 1
    canon_later = F.greatest(F.element_at("dlq_buckets", idx) + off, F.lit(1))
    df = base.join(s, on="account_id", how="left").withColumn(
        "canon_now", F.greatest(F.col("current_bucket") + off, F.lit(1))
    )
    df = df.withColumn(
        "canon_later",
        F.when(
            F.col("dlq_buckets").isNotNull() & (later <= F.col("last_month")),
            canon_later,
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
        df.select("account_id", "observation_date")
        .join(
            pay.select(F.col("account_id").cast("string"), "pay_date", "amount"),
            "account_id",
        )
        .filter(
            (F.col("pay_date") > F.col("observation_date"))
            & (F.col("pay_date") <= later)
        )
        .groupBy("account_id", "observation_date")
        .agg(F.sum("amount").alias("paid_next"))
    )
    return (
        df.withColumn("move", move)
        .withColumn("dpd_band", _band(F.col("canon_now")))
        .join(paid, on=["account_id", "observation_date"], how="left")
        .withColumn(
            "pay_any",
            (F.coalesce("paid_next", F.lit(0.0)) >= MIN_PAYMENT_AED).cast("int"),
        )
        .drop("dlq_buckets")
    )


def _rates(df: DataFrame, by: list[str]) -> pd.DataFrame:
    has = F.col("move") != "no_history"
    extra = [
        F.sum(has.cast("int")).alias("with_history"),
        *[
            F.sum((F.col("move") == m).cast("int")).alias(m)
            for m in ("cured", "improved", "held", "rolled")
        ],
        F.sum("pay_any").alias("paid_any"),
    ]
    pdf = _table(df, by, extra)
    h = pdf["with_history"].clip(lower=1)
    for m in ("cured", "improved", "held", "rolled"):
        pdf[f"{m}_pct"] = (100.0 * pdf[m] / h).round(1)
    pdf["better_pct"] = (100.0 * (pdf["cured"] + pdf["improved"]) / h).round(1)
    pdf["paid_any_pct"] = (100.0 * pdf["paid_any"] / pdf["accounts"]).round(1)
    return pdf


def main() -> None:
    """Build every section, write results_<model_id>.json and .md."""
    catalog = _catalog()
    model_id = catalog.load("params:model_id")
    p = model_id[:2]
    end = str(catalog.load("params:crx_persona")["persona_end_date"])
    master = catalog.load(f"crx_{p}_persona_master").cache()
    month = F.trunc("observation_date", "month")
    latest = master.filter(month == F.trunc(F.lit(end), "month")).withColumn(
        "dpd_band",
        _band(F.greatest(F.col("current_bucket") + OFFSET[p], F.lit(1))),
    )
    res: dict = {"model_id": model_id, "persona_end_date": end, "tables": {}}
    t = res["tables"]

    # S1 latest month
    res["latest_accounts"] = latest.count()
    for name, col in AXES.items():
        t[f"S1_{name}"] = _table(latest, [col])
    for col in PERSONA + ["product", "dpd_band"]:
        t[f"S1_{col}"] = _table(latest, [col])
    t["S1_segment_x_route"] = _table(
        latest, ["persona_segment", "persona_contact_route"]
    )
    t["S1_segment_x_journey"] = _table(
        latest, ["persona_segment", "persona_journey_group"]
    )
    t["S1_segment_x_product"] = _table(latest, ["persona_segment", "product"])
    t["S1_segment_x_band"] = _table(latest, ["persona_segment", "dpd_band"])
    t["S1_ability_x_credibility"] = _table(latest, ["a1_state", "a3_state"])
    for col in REASONS:
        if col in latest.columns:
            t[f"S1_reason_{col}"] = _table(latest, [col])

    # S2 trend
    for col in PERSONA[:3] + list(AXES.values()):
        t[f"S2_trend_{col}"] = _table(master.withColumn("month", month), ["month", col])

    # S3 back-test
    base_month = F.add_months(F.trunc(F.lit(end), "month"), -HORIZON)
    seq = catalog.load(f"crx_{p}_dpd_sequences")
    pay = catalog.load(f"crx_{p}_a3_payments")
    bt = _outcomes(master.filter(month == base_month), seq, pay, p).cache()
    res["backtest_base_month"] = str(bt.select(F.min("observation_date")).first()[0])
    t["S3_overall"] = _rates(bt.withColumn("all", F.lit("all")), ["all"])
    t["S3_by_band"] = _rates(bt, ["dpd_band"])
    for name, col in AXES.items():
        t[f"S3_by_{name}"] = _rates(bt, [col])
    for col in PERSONA:
        t[f"S3_by_{col}"] = _rates(bt, [col])
    t["S3_segment_x_band"] = _rates(bt, ["dpd_band", "persona_segment"])
    t["S3_route_x_band"] = _rates(bt, ["dpd_band", "persona_contact_route"])
    sb = t["S3_segment_x_band"]
    res["S3_auc"] = {
        f"{target}_{key}": _auc(sb, cells, target, "with_history")
        for target in ("cured", "rolled")
        for key, cells in (
            ("band_only", ["dpd_band"]),
            ("band_plus_segment", ["dpd_band", "persona_segment"]),
        )
    }
    res["S3_auc"].update(
        {
            f"paid_any_{key}": _auc(sb, cells, "paid_any", "accounts")
            for key, cells in (
                ("band_only", ["dpd_band"]),
                ("band_plus_segment", ["dpd_band", "persona_segment"]),
            )
        }
    )

    # S4 overlap
    cols = list(AXES.values()) + ["dpd_band", "persona_segment"]
    res["S4_cramers_v"] = {
        f"{a}~{b}": _cramers_v(latest, a, b)
        for i, a in enumerate(cols)
        for b in cols[i + 1 :]
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shown = {k: _suppress(v) for k, v in t.items()}
    payload = {**res, "tables": {k: v.to_dict("records") for k, v in shown.items()}}
    (OUT_DIR / f"results_{model_id}.json").write_text(
        json.dumps(payload, default=str, indent=1)
    )
    lines = [f"# Persona deck results — {model_id}, {end}", ""]
    for k in ("latest_accounts", "backtest_base_month", "S3_auc", "S4_cramers_v"):
        lines += [f"**{k}**: `{json.dumps(res[k], default=str)}`", ""]
    for k, v in shown.items():
        lines += [f"## {k}", "", _markdown(v), ""]
    (OUT_DIR / f"results_{model_id}.md").write_text("\n".join(lines))
    print(f"wrote {OUT_DIR}/results_{model_id}.json and .md")


if __name__ == "__main__" or "catalog" in globals():
    main()
