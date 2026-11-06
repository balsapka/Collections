"""TEMPORARY (refactor bundle R-B): zero-difference checks for the refactored A1, A2, A4.

Each check pipeline re-runs one axis (with the inputs it rebuilds: obs base, full
history) in its own namespace, writes the new outputs to ``*_rf_check`` entries and
compares them with the outputs persisted before the bundle. Nothing real is
overwritten. Logged blocks: ``RF <NAME> OUTPUT``, ``RF A2 DCORE``, ``RF KEYS``,
``RF STRING KEYS``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_<a4|a2|a1>_rf_check
"""

# pylint: disable=protected-access

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .obs_base import pipeline as obs_base
from ._common import GRAIN, dcore_account_events
from .a2_locatability import signals as a2_signals
from .cc_a1_ability.pipeline import create_pipeline as cc_a1
from .cc_a2_locatability.pipeline import create_pipeline as cc_a2
from .cc_a4_deterioration.pipeline import create_pipeline as cc_a4
from .cc_full_history.pipeline import create_pipeline as cc_full_history
from .rl_a1_ability.pipeline import create_pipeline as rl_a1
from .rl_a2_locatability.pipeline import create_pipeline as rl_a2
from .rl_a4_deterioration.pipeline import create_pipeline as rl_a4
from .rl_full_history.pipeline import create_pipeline as rl_full_history

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "rf_check"]

# Join-key columns of the sources the refactor reads, per product (Q-21 sites).
STRING_KEY_SITES = {
    "cc": {
        "cc_spine": ["contract_id", "cif_id"],
        "prm_balance": ["contract_id"],
        "prm_contract": ["contract_id"],
    },
    "rl": {
        "rl_spine": ["account_id", "cif_id"],
        "int_loan_master": ["account_id"],
        "feature_retail_loans": ["account_id"],
    },
    "both": {
        "dcore_prm_followup_outcomes": ["agreement_id"],
        "prm_dcore_account_agreements": ["account_id", "agreement_id"],
        "feat_demographics_cif": ["cif_id"],
        "feat_cif_internal_salary_monthly": ["cif_id"],
    },
}


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== RF %s START ===\n%s\n=== RF %s END ===", name, body, name)


def compare_outputs(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    old: DataFrame, new: DataFrame, model_id: str, name: str, keys: list, state: str
) -> None:
    """Rows, schema, rows only in one side; old x new ``state`` on ``keys`` if given."""
    lines = [
        f"model_id: {model_id}",
        f"rows old / new: {old.count()} / {new.count()}",
    ]
    same = old.schema.simpleString() == new.schema.simpleString()
    lines.append(f"same schema: {same}")
    if not same:
        o, n = dict(old.dtypes), dict(new.dtypes)
        lines.append(
            f"only old: {sorted(set(o) - set(n))}; only new: {sorted(set(n) - set(o))}"
        )
        lines.append(
            f"type differs: {sorted(c for c in set(o) & set(n) if o[c] != n[c])}"
        )
    # computed_at is the run's timestamp, so it differs on every row by construction.
    cols = [c for c in old.columns if c in new.columns and c != "computed_at"]

    def hashes(df: DataFrame, side: str) -> DataFrame:
        return df.groupBy(F.xxhash64(*cols).alias("h")).agg(F.count("*").alias(side))

    diff = (
        hashes(old, "o")
        .join(hashes(new, "n"), on="h", how="full")
        .agg(
            F.sum(
                F.greatest(
                    F.coalesce("o", F.lit(0)) - F.coalesce("n", F.lit(0)), F.lit(0)
                )
            ).alias("o"),
            F.sum(
                F.greatest(
                    F.coalesce("n", F.lit(0)) - F.coalesce("o", F.lit(0)), F.lit(0)
                )
            ).alias("n"),
        )
        .first()
    )
    lines.append(f"rows only in old: {diff['o'] or 0}")
    lines.append(f"rows only in new: {diff['n'] or 0}")
    if state:
        both = old.select(*keys, F.col(state).alias("old")).join(
            new.select(*keys, F.col(state).alias("new")), on=keys, how="full"
        )
        moved = both.filter(~F.col("old").eqNullSafe(F.col("new"))).count()
        lines.append(f"rows whose {state} differs: {moved}")
        for r in both.groupBy("old", "new").count().orderBy("old", "new").collect():
            lines.append(f"  {r['old']} -> {r['new']}: {r['count']}")
    _block(f"{name} OUTPUT", lines)


def describe_a2_inputs(
    obs: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> None:
    """N-3: rows into the DCORE aggregate and the non-attempt share; N-4: key counts."""
    days = (
        obs.select(*GRAIN)
        .join(
            a2_signals._dcore_days(dcore_account_events(obs, followup, agreements)),
            "account_id",
        )
        .filter(F.col("day") <= F.col("observation_date"))
    )
    r = days.agg(
        F.count("*").alias("n"),
        F.avg((F.col("_attempt") != 1).cast("double")).alias("p"),
    ).first()
    _block(
        "A2 DCORE",
        [
            f"model_id: {model_id}",
            f"rows into the DCORE aggregate: {r['n']}",
            f"share of non-attempt days: {r['p']}",
            "stage spill / shuffle read of build_*_a2_dcore_signals: read from the Spark UI",
        ],
    )
    k = obs.agg(
        F.countDistinct("cif_id").alias("c"), F.countDistinct("account_id").alias("a")
    ).first()
    _block(
        "KEYS",
        [
            f"model_id: {model_id}",
            f"distinct cif_id: {k['c']}",
            f"distinct account_id: {k['a']}",
        ],
    )


def describe_string_keys(model_id: str, **sources: DataFrame) -> None:
    """Per source key: its type and how many values change under trim."""
    sites = {
        **STRING_KEY_SITES["cc"],
        **STRING_KEY_SITES["rl"],
        **STRING_KEY_SITES["both"],
    }
    lines = [f"model_id: {model_id}"]
    for name, df in sources.items():
        types = dict(df.dtypes)
        present = [c for c in sites[name] if c in types]
        lines += [f"{name}.{c}: missing" for c in sites[name] if c not in types]
        if not present:
            continue
        aggs = []
        for c in present:
            s = F.col(c).cast("string")
            aggs.append(F.sum((s != F.trim(s)).cast("int")).alias(c))
        row = df.agg(*aggs).first()
        lines += [f"{name}.{c} ({types[c]}): {row[c] or 0} padded" for c in present]
    _block("STRING KEYS", lines)


def _scoped(pipe: Pipeline, product: str, rename: dict) -> Pipeline:
    """``pipe`` in the ``rf_<p>`` namespace: free inputs and params keep their names,
    ``rename`` maps outputs to their check entries, the rest stays in memory."""
    inputs = {i for i in pipe.inputs() if not i.startswith("params:")}
    params = {i for i in pipe.all_inputs() if i.startswith("params:")}
    return pipeline(
        pipe,
        namespace=f"rf_{product}",
        inputs=inputs,
        outputs=rename,
        parameters=params,
    )


def _compare(name: str, real: str, keys, state: str = "") -> Pipeline:
    return Pipeline(
        [
            node(
                func=partial(compare_outputs, name=name, keys=list(keys), state=state),
                inputs={
                    "old": real,
                    "new": f"{real}_rf_check",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name=f"compare_{real}_rf",
                tags=TAGS,
            )
        ]
    )


def create_a4_rf_check_pipeline(product: str) -> Pipeline:
    """Full history + A4 into check entries; compares both."""
    history, state = f"crx_{product}_full_history", f"crx_{product}_a4_deterioration"
    build = (
        (cc_full_history() + cc_a4())
        if product == "cc"
        else (rl_full_history() + rl_a4())
    )
    rename = {history: f"{history}_rf_check", state: f"{state}_rf_check"}
    return (
        _scoped(build, product, rename)
        + _compare("FULL HISTORY", history, ())
        + _compare("A4", state, GRAIN, "det_state")
    )


def create_a2_rf_check_pipeline(product: str) -> Pipeline:
    """Obs base + A2 into check entries; compares A2, logs DCORE and key counts."""
    obs, out = f"crx_{product}_obs_base", f"crx_{product}_a2_locatability"
    base = (
        obs_base.create_cc_pipeline()
        if product == "cc"
        else obs_base.create_rl_pipeline()
    )
    axis = cc_a2() if product == "cc" else rl_a2()
    describe = node(
        func=describe_a2_inputs,
        inputs={
            "obs": obs,
            "followup": "dcore_prm_followup_outcomes",
            "agreements": "prm_dcore_account_agreements",
            "model_id": "params:model_id",
        },
        outputs=None,
        name=f"describe_{out}_rf",
        tags=TAGS,
    )
    return (
        _scoped(base + axis, product, {out: f"{out}_rf_check"})
        + _compare("A2", out, GRAIN, "a2_state")
        + Pipeline([describe])
    )


def create_a1_rf_check_pipeline(product: str) -> Pipeline:
    """Obs base + A1 into check entries; compares both, logs the string-key counts."""
    obs, out = f"crx_{product}_obs_base", f"crx_{product}_a1_ability"
    base = (
        obs_base.create_cc_pipeline()
        if product == "cc"
        else obs_base.create_rl_pipeline()
    )
    axis = cc_a1() if product == "cc" else rl_a1()
    sources = {**STRING_KEY_SITES[product], **STRING_KEY_SITES["both"]}
    keys = node(
        func=describe_string_keys,
        inputs={"model_id": "params:model_id", **{s: s for s in sources}},
        outputs=None,
        name=f"describe_crx_{product}_rf_string_keys",
        tags=TAGS,
    )
    return (
        _scoped(base + axis, product, {obs: f"{obs}_rf_check", out: f"{out}_rf_check"})
        + _compare("OBS BASE", obs, GRAIN)
        + _compare("A1", out, GRAIN, "a1_state")
        + Pipeline([keys])
    )
