"""TEMPORARY (bundle 25): the shipped code rerun next to the persisted outputs.

``crx_<p>_b25_check`` runs the product's pipelines as they ship (CC raw extract, A4, A2,
A1, A3, plus product primaries / features and the bureau features) with every output
renamed ``<name>__b25`` (one catalog pattern, ``tmp_b25_check.yml``), so no real output
is touched; inputs they do not build are the persisted ones. Then it logs, for
``model_id``:

- ``B25 DIFF``: per dataset, rows old / new and rows only on one side (``exceptAll``,
  doubles rounded to 2 decimals). The refactor must give 0; datasets a behaviour step
  changes are marked, with the columns outside that step compared on their own;
- ``B25 A3 EVENTS``: promise events old / new (kind, outcome, 31-day cap, 100 AED floor);
- ``B25 A3 LEVELS``: latest month, Dimension A / B levels, refusal and latest contact
  old x new, refusals lifted by a later payment or plan;
- ``B25 A3 MOVES``: the state step by step: old -> new events and dues (old points, old
  refusal) -> new refusal -> new points (D-A3-33);
- ``B25 A3 DUES``: cards: statements with bucket 08 open and no baseline (no due);
  loans: B-window months with EMI 0 / NULL / > 0;
- ``B25 A1``: latest month, state and family levels old x new, the sweepable balance
  flag, and F1 / F2 / F3 strong (8 cells) with paid a due in the next 3 months;
- ``B25 PARENT LINK`` (cards): what ``parent_contract_id`` links on the card contracts.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b25_check
"""

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.bureau import salary_bounces
from enbd_collections.pipelines.products import features as product_features
from enbd_collections.pipelines.products import primary as product_primary

from . import (
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_raw_extract,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
)
from ._common import GRAIN, window_months
from .a3_credibility.constants import DISPLAY_NAMES, HIGH_FROM, MODERATE_FROM
from .cc_a4_deterioration import pipeline as cc_a4_deterioration

logger = logging.getLogger(__name__)
NEW = "__b25"
TAGS = ["crx_persona", "crx", "b25_check"]
OLD_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}  # before D-A3-33
NEW_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
B_POINTS, C_POINTS = {"regular": 2, "some": 1}, {"clean": 1}
CONTACT_STEP = [  # contact columns D-A3-30 / D-A3-32 may change
    "last_rpc_disposition",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
]


def _parts(product: str) -> list[Pipeline]:
    """The pipelines step 8 reruns for ``product``, in run order."""
    shared = [
        product_primary.create_pipeline(),
        product_features.create_pipeline(),
        salary_bounces.create_pipeline(),
    ]
    if product == "cc":
        axes = [cc_raw_extract, cc_a4_deterioration, cc_a2_locatability]
        axes += [cc_a1_ability, cc_a3_payment_credibility]
    else:
        axes = [rl_a4_deterioration, rl_a2_locatability, rl_a1_ability]
        axes += [rl_a3_payment_credibility]
    return shared + [m.create_pipeline() for m in axes]


def _expected(product: str) -> dict[str, list[str] | None]:
    """Datasets a behaviour step changes: name -> the columns it may change (None =
    every column). Datasets with no old version (new outputs) map to ``[]``."""
    p = f"crx_{product}"
    out: dict[str, list[str] | None] = {
        f"{p}_a3_promise_events": None,
        f"{p}_a3_commitment_signals": None,
        f"{p}_a3_payment_credibility": None,
        f"{p}_a1_ability": None,
        f"{p}_a3_strong_negative_signals": CONTACT_STEP,
        f"{p}_a3_dues": [],
        f"{p}_a3_payments": [],
    }
    if product == "cc":  # D-A3-31 changes card dues at bucket 08
        out["crx_cc_a3_payment_cycles"] = ["due_amount"]
        out["crx_cc_a3_dlq_payment_signals_single_payment_cycle_count"] = None
    return out


# ── Logging helpers ───────────────────────────────────────────────────────────


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], changed_only: bool = False) -> list[str]:
    """``cols`` value counts (``old_x`` / ``new_x`` pairs may be filtered to changes)."""
    if changed_only:
        df = df.filter(~F.col(cols[0]).eqNullSafe(F.col(cols[1])))
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "    " + " | ".join(str(r[c]) for c in cols) + f": {r['count']}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ] or ["    none"]


# ── B25 DIFF ──────────────────────────────────────────────────────────────────


def _comparable(df: DataFrame, cols: list[str]) -> DataFrame:
    """``cols`` with doubles rounded to 2 decimals; map columns cannot be compared."""
    kinds = {f.name: f.dataType for f in df.schema.fields}
    return df.select(
        *[
            (
                F.round(c, 2).alias(c)
                if isinstance(kinds[c], (T.DoubleType, T.FloatType))
                else F.col(c)
            )
            for c in cols
            if not isinstance(kinds[c], T.MapType)
        ]
    )


def _one_sided(old: DataFrame, new: DataFrame, cols: list[str]) -> tuple[int, int]:
    a, b = _comparable(old, cols), _comparable(new, cols)
    return a.exceptAll(b).count(), b.exceptAll(a).count()


def _diff_line(name: str, old: DataFrame, new: DataFrame, step) -> list[str]:
    common = [c for c in new.columns if c in old.columns]
    gone = sorted(set(old.columns) - set(new.columns))
    added = sorted(set(new.columns) - set(old.columns))
    only_old, only_new = _one_sided(old, new, common)
    tag = {False: "refactor, expect 0", None: "behaviour step"}.get(
        step if step is None or step is False else "cols", "behaviour step on columns"
    )
    line = (
        f"  {name} [{tag}]: rows old {old.count()} new {new.count()}; only old "
        f"{only_old}, only new {only_new}"
    )
    lines = [line]
    if gone or added:
        lines.append(f"      columns dropped {gone or '-'}, added {added or '-'}")
    if step:  # the columns outside the behaviour step must match
        rest = [c for c in common if c not in step]
        o, n = _one_sided(old, new, rest)
        lines.append(f"      without {step}: only old {o}, only new {n} (expect 0)")
    return lines


def compare_datasets(model_id: str, names: list[str], expected: dict, **frames) -> None:
    """``B25 DIFF``: every rerun dataset against its persisted version."""
    lines = []
    for i, name in enumerate(names):
        try:
            step = expected.get(name, False)
            lines += _diff_line(name, frames[f"o{i}"], frames[f"n{i}"], step)
        except Exception as err:  # noqa: BLE001  # pylint: disable=broad-except
            lines.append(f"  {name}: FAILED {type(err).__name__}: {err}")
    _block("B25 DIFF", model_id, lines)


# ── A3 ────────────────────────────────────────────────────────────────────────


def _events_lines(events: DataFrame, side: str) -> list[str]:
    days = F.datediff("promise_cutoff", "event_date")
    s = events.agg(
        F.count(F.lit(1)).alias("n"),
        F.sum((days == 31).cast("int")).alias("cap"),
        F.sum((F.col("promise_amount") <= 100).cast("int")).alias("floor"),
    ).collect()[0]
    return [
        (
            f"  {side}: events {s['n']}, deadline 31 days after {s['cap']}, amount at "
            f"the 100 AED floor {s['floor']}"
        ),
        "   kind | outcome:",
    ] + _counts(events, ["event_kind", "promise_outcome"])


def _points(levels: dict[str, int], col: str) -> Column:
    expr = F.lit(0)
    for level, pts in levels.items():
        expr = F.when(F.col(col) == level, F.lit(pts)).otherwise(expr)
    return expr


def _state(a_points: dict[str, int], refusal: str) -> Column:
    """The A3 state from the level columns, ``a_points`` for Dimension A and the
    ``refusal`` flag column (a refusal takes one rung off)."""
    pts = (
        _points(a_points, "a3_commitments_level")
        + _points(B_POINTS, "a3_dlq_payment_level")
        + _points(C_POINTS, "a3_pre_dlq_payment_level")
    )
    rung = F.when(pts >= HIGH_FROM, 2).when(pts >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(
        rung - F.coalesce(F.col(refusal), F.lit(False)).cast("int"), F.lit(0)
    )
    label = (
        F.when(rung == 2, DISPLAY_NAMES["high"])
        .when(rung == 1, DISPLAY_NAMES["moderate"])
        .otherwise(DISPLAY_NAMES["low"])
    )
    return F.when(F.col("episode_start").isNull(), DISPLAY_NAMES["unknown"]).otherwise(
        label
    )


def _dues_lines(ledger: DataFrame, base: DataFrame, model_id: str) -> list[str]:
    if "rl" not in model_id:
        no_due = ledger.filter(F.col("due_amount").isNull())
        return [
            (
                f"  card statements with no due (bucket 08 open, no baseline): "
                f"{no_due.count()} on {no_due.select('account_id').distinct().count()} "
                "accounts"
            ),
        ]
    since = F.add_months(F.col("observation_date"), -window_months(model_id))
    window = base.select("account_id", "observation_date").join(ledger, "account_id")
    window = window.filter(
        (F.col("cycle_end") > since) & (F.col("cycle_end") <= F.col("observation_date"))
    )
    emi = (
        F.when(F.col("due_amount").isNull(), "NULL")
        .when(F.col("due_amount") == 0, "0")
        .otherwise("> 0")
    )
    return ["  loan B-window months by EMI:"] + _counts(
        window.withColumn("emi", emi), ["emi"]
    )


def compare_a3(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old_events: DataFrame,
    new_events: DataFrame,
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A3 EVENTS / LEVELS / MOVES / DUES``."""
    _block(
        "B25 A3 EVENTS",
        model_id,
        _events_lines(old_events, "old") + _events_lines(new_events, "new"),
    )
    cols = [
        "a3_commitments_level",
        "a3_dlq_payment_level",
        "a3_pre_dlq_payment_level",
        "a3_refusal_flag",
        "last_rpc_disposition",
        "a3_state",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols]
    )
    rows = (
        _latest(new, persona_end_date)
        .join(o, list(GRAIN), "left")
        .withColumn("s_events", _state(OLD_POINTS, "old_a3_refusal_flag"))
        .withColumn("s_refusal", _state(OLD_POINTS, "a3_refusal_flag"))
        .withColumn("s_points", _state(NEW_POINTS, "a3_refusal_flag"))
        .localCheckpoint()
    )
    lines = []
    for c in cols[:5]:
        lines += [f"  {c}, old | new (changed rows):"]
        lines += _counts(rows, [f"old_{c}", c], changed_only=True)
    lines += ["  latest contact a refusal: followed by a payment | by a plan:"]
    lines += _counts(
        rows.filter(F.col("last_rpc_disposition") == "refusal"),
        ["refusal_followed_by_payment", "refusal_followed_by_plan"],
    )
    _block("B25 A3 LEVELS", model_id, lines)
    moves = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a3_state"])
    for step, a, b in (
        ("events and dues", "old_a3_state", "s_events"),
        ("refusal", "s_events", "s_refusal"),
        ("points", "s_refusal", "s_points"),
    ):
        moves += [f"  step {step}, from | to (changed rows):"]
        moves += _counts(rows, [a, b], changed_only=True)
    check = rows.filter(~F.col("s_points").eqNullSafe(F.col("a3_state"))).count()
    moves += [
        f"  rows whose recomputed state differs from a3_state: {check} (expect 0)"
    ]
    _block("B25 A3 MOVES", model_id, moves)
    _block(
        "B25 A3 DUES",
        model_id,
        _dues_lines(ledger, _latest(new, persona_end_date), model_id),
    )


# ── A1 ────────────────────────────────────────────────────────────────────────


def _paid_due(base: DataFrame, ledger: DataFrame) -> DataFrame:
    """Per base row: paid a due = payments of the cycles ending in the 3 months after
    the observation date reach max(the latest due on or before it, 100 AED)."""
    obs = F.col("observation_date")
    joined = base.select(*GRAIN).join(ledger, "account_id")
    due = F.max(F.when(F.col("cycle_end") <= obs, F.struct("cycle_end", "due_amount")))[
        "due_amount"
    ]
    paid = F.sum(
        F.when(
            (F.col("cycle_end") > obs) & (F.col("cycle_end") <= F.add_months(obs, 3)),
            F.col("paid_amount"),
        )
    )
    agg = joined.groupBy(*GRAIN).agg(due.alias("_due"), paid.alias("_paid"))
    hit = F.coalesce("_paid", F.lit(0.0)) >= F.greatest(
        F.coalesce("_due", F.lit(0.0)), F.lit(100.0)
    )
    return agg.select(*GRAIN, hit.cast("int").alias("paid_due"))


def compare_a1(  # pylint: disable=too-many-arguments
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A1``: old x new, and F1 / F2 / F3 strong with paid a due."""
    cols = [
        "a1_state",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        "a1_sweepable_balance_flag",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols if c in old.columns]
    )
    rows = _latest(new, persona_end_date).join(o, list(GRAIN), "left").localCheckpoint()
    lines = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a1_state"])
    for c in cols:
        if f"old_{c}" in rows.columns:
            lines += [f"  {c}, old | new (changed rows):"]
            lines += _counts(rows, [f"old_{c}", c], changed_only=True)
        else:
            lines += [f"  {c} (new column):"] + _counts(rows, [c])
    strong = [
        F.coalesce(F.col("a1_income_level") == "stable", F.lit(False))
        .cast("int")
        .alias("f1"),
        F.coalesce(F.col("a1_money_in_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f2"),
        F.coalesce(F.col("a1_money_out_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f3"),
    ]
    lines += ["  F1 | F2 | F3 strong, latest month:"]
    lines += _counts(rows.select(*strong), ["f1", "f2", "f3"])
    end = F.add_months(F.lit(str(persona_end_date)), -3)
    pooled = new.filter(F.col("observation_date") <= end).select(*GRAIN, *strong)
    outcome = pooled.join(_paid_due(pooled, ledger), list(GRAIN), "left")
    rates = (
        outcome.groupBy("f1", "f2", "f3")
        .agg(F.count(F.lit(1)).alias("n"), F.avg("paid_due").alias("rate"))
        .orderBy("f1", "f2", "f3")
        .collect()
    )
    lines += ["  F1 | F2 | F3 strong, pooled months with 3 months after: n, paid a due"]
    lines += [
        f"    {r['f1']} | {r['f2']} | {r['f3']}: {r['n']}, "
        f"{100 * (r['rate'] or 0):.1f}%"
        for r in rates
    ] or ["    none"]
    _block("B25 A1", model_id, lines)


# ── Card parent link (Q-S6-14) ────────────────────────────────────────────────


def _share(part: int, whole: int) -> str:
    return f"{part} ({100 * part / max(whole, 1):.1f}%)"


def compare_parent_link(  # pylint: disable=too-many-locals
    contracts: DataFrame,
    month_end: DataFrame,
    obs_base: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 PARENT LINK``: what ``parent_contract_id`` links on the card contracts."""
    c = contracts.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("contract_id").cast("string").alias("contract_id"),
        F.col("parent_contract_id").cast("string").alias("parent_id"),
    ).localCheckpoint()
    n = c.count()
    parents = c.filter(F.col("parent_id").isNotNull()).select(
        F.col("parent_id").alias("contract_id")
    )
    kids = parents.groupBy("contract_id").count()
    bands = F.when(F.col("count") >= 4, "4+").otherwise(F.col("count").cast("string"))
    pairs = c.filter(F.col("parent_id").isNotNull()).join(
        c.select(
            F.col("contract_id").alias("parent_id"), F.col("cif_id").alias("parent_cif")
        ),
        "parent_id",
        "left",
    )
    n_pairs = pairs.count()
    month = F.last_day(F.lit(str(persona_end_date)))
    live = (
        month_end.filter(F.col("month_end") == month)
        .select(F.col("contract_id").cast("string").alias("contract_id"))
        .distinct()
    )
    both_live = pairs.join(live, "contract_id").join(
        live.withColumnRenamed("contract_id", "parent_id"), "parent_id"
    )
    scored = (
        _latest(obs_base, persona_end_date)
        .select(F.col("account_id").cast("string").alias("contract_id"))
        .distinct()
    )
    n_scored = scored.count()
    named = scored.join(parents.distinct(), "contract_id").count()
    with_parent = scored.join(
        c.filter(F.col("parent_id").isNotNull()).select("contract_id"), "contract_id"
    ).count()
    no_parent_row = pairs.filter(F.col("parent_cif").isNull()).count()
    same_cif = pairs.filter(F.col("cif_id") == F.col("parent_cif")).count()
    lines = [
        (
            f"  card contracts {n}; with a parent {_share(n_pairs, n)}; named as a parent "
            f"{_share(kids.count(), n)}"
        ),
        "  children per parent:",
        *_counts(kids.withColumn("children", bands), ["children"]),
        (
            f"  pairs: parent not a card contract {_share(no_parent_row, n_pairs)}; same CIF "
            f"{_share(same_cif, n_pairs)}; both with a month-end row in the latest month "
            f"{_share(both_live.count(), n_pairs)}"
        ),
        (
            f"  scored accounts {n_scored}: named as a parent {_share(named, n_scored)}; "
            f"with a parent {_share(with_parent, n_scored)}"
        ),
    ]
    _block("B25 PARENT LINK", model_id, lines)


# ── Pipeline ──────────────────────────────────────────────────────────────────


def create_pipeline(product: str, parts: list[Pipeline] | None = None) -> Pipeline:
    """The shipped pipelines into ``<name>__b25``, then the comparisons. ``parts``
    replaces the pipelines rerun (a local test runs one axis at a time)."""
    real = sum(parts if parts is not None else _parts(product), Pipeline([]))
    outputs = sorted(real.all_outputs())
    rerun = pipeline(real, outputs={o: f"{o}{NEW}" for o in outputs})
    expected = _expected(product)
    names = [o for o in outputs if expected.get(o) != []]
    common = {"model_id": "params:model_id"}
    end = {**common, "persona_end_date": "params:crx_persona.persona_end_date"}
    nodes = [
        node(
            func=partial(compare_datasets, names=names, expected=expected),
            inputs={
                **common,
                **{f"o{i}": o for i, o in enumerate(names)},
                **{f"n{i}": f"{o}{NEW}" for i, o in enumerate(names)},
            },
            outputs=None,
            name=f"crx_{product}_b25_diff",
            tags=TAGS,
        )
    ]
    p = f"crx_{product}_a3"
    ledger = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}[product]
    if f"{p}_payment_credibility" in outputs:
        nodes.append(
            node(
                func=compare_a3,
                inputs={
                    "old_events": f"{p}_promise_events",
                    "new_events": f"{p}_promise_events{NEW}",
                    "old": f"{p}_payment_credibility",
                    "new": f"{p}_payment_credibility{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a3",
                tags=TAGS,
            )
        )
    if (
        f"crx_{product}_a1_ability" in outputs
        and f"{ledger}{NEW}" in rerun.all_outputs()
    ):
        nodes.append(
            node(
                func=compare_a1,
                inputs={
                    "old": f"crx_{product}_a1_ability",
                    "new": f"crx_{product}_a1_ability{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a1",
                tags=TAGS,
            )
        )
    if product == "cc" and "prm_card_contracts" in outputs:
        nodes.append(
            node(
                func=compare_parent_link,
                inputs={
                    "contracts": f"prm_card_contracts{NEW}",
                    "month_end": f"prm_card_month_end{NEW}",
                    "obs_base": "crx_cc_obs_base",
                    **end,
                },
                outputs=None,
                name="crx_cc_b25_parent_link",
                tags=TAGS,
            )
        )
    return rerun + Pipeline(nodes)
