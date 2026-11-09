# Mirror bundle 19 — A3 — check pipelines without dotted dataset names (Kedro warnings)

apply_bundle version: 7 · built 2026-11-09 from `5b2c0d2..243289a` · source: 0 added, 1 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/19_a3_check_dataset_names.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '19_a3_check_dataset_names.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/19_a3_check_dataset_names.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Check that the warnings are gone and nothing else moved:

```bash
kedro registry list 2>&1 | grep -c "contains '.'"
```

It prints `0`. `git status` shows only `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py`.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A3: check pipelines without dotted dataset names" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/19_a3_check_dataset_names.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

**Step 7.** Nothing to run: the check blocks you already have stand. Use this version for any re-run of `crx_<p>_a3_check`.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Silences the Kedro warnings `Dataset name 'a3_check.<name>' contains '.' characters` that the A3 check pipelines print. The check's in-memory datasets are now named `a3_check__<name>`; the namespace only prefixes the node names. One file (`a3_credibility/check.py`); the check computes and logs exactly the same blocks. The real A3 pipelines are unchanged.

Not changed, on purpose: the Spark warning `ExtractPythonUDFFromJoinCondition … turned to cross join` seen in `crx_cc_a4_rf_check` (bundle 16). It appears only when the A4 sequences stay in memory, as they did inside that check; the real A4 pipeline writes `crx_<p>_dpd_sequences` to parquet and reads it back, so the Python UDF never reaches the join. The check is cleaned up, and its outputs were identical.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. A `MERGED` file differed from the copy
   this bundle was built from; show the user its `git diff` before committing.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py`
action: replace · base sha256 `9ea7c4c22ea3c1dd41508197e2a84759c3c365fa8a61dbba14e1cd36980789f3` · base trailing newline: yes · new sha256 `787bf77cc4bc931427b64671f5c6ca5478402041ee44bd34c445078b54cfce7b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (A3 bundle): the new A3 on the latest month, with both Dimension A judges,
against the A3 output persisted before the bundle. Logs ``A3 OUTPUT``, ``A3 COMMITMENTS``,
``A3 BROKEN``, ``A3 CONTACTS``, ``A3 EPISODE``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals, build_contact_signals
from .constants import GRACE

logger = logging.getLogger(__name__)
NS = "a3_check"


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The base rows of persona_end_date's month."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _state(
    points_a: Column,
    points_bc: Column,
    refusal: Column,
    override: Column,
    unknown: Column,
) -> Column:
    """The A3 ladder for a what-if of the Broken weight."""
    pts = points_a + points_bc
    demote = refusal | override
    rung = (
        F.when(pts >= 4, F.when(demote, "moderate").otherwise("high"))
        .when((pts >= 1) & ~demote, "moderate")
        .otherwise("low")
    )
    return F.when(unknown, "unknown").otherwise(rung)


def compare_a3(
    old: DataFrame,
    pay: DataFrame,
    dcore: DataFrame,
    uncapped: DataFrame,
    model_id: str,
    persona_end_date: str,
    floor: str | None,
) -> None:
    """The check blocks (latest month)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    old_m = old.filter(F.trunc("observation_date", "month") == month)
    keep = ["a3_state_v1", "a3_commitments_level", "a3_strong_negative_reason"]
    old_m = old_m.select(
        "account_id", "observation_date", *[c for c in keep if c in old_m.columns]
    )
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    old_m = (
        old_m.withColumn("_r", newest).where("_r = 1").drop("_r", "observation_date")
    )
    n = pay.count()
    p, d = pay.alias("p"), dcore.alias("d")
    both = p.join(d, "account_id").join(old_m.alias("o"), "account_id", "left")
    head = [
        f"model_id: {model_id}",
        f"rows new: {n}, old (latest per account): {old_m.count()}",
    ]

    lines = head + ["old a3_state_v1 x new (payments):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("p.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["old x new (dcore):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("d.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["new dcore x new payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_state").alias("dcore"), F.col("p.a3_state").alias("payments")
        ),
        ["dcore", "payments"],
        n,
    )
    _block("A3 OUTPUT", lines)

    lines = head + ["Dimension A level, dcore x payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_commitments_level").alias("dcore"),
            F.col("p.a3_commitments_level").alias("payments"),
        ),
        ["dcore", "payments"],
        n,
    )
    s = both.agg(
        *[
            F.sum(f"{j}.{c}").alias(f"{j}_{c}")
            for j in ("d", "p")
            for c in ("commitments_concluded", "commitments_kept")
        ]
    ).first()
    lines += [
        f"instalments concluded / kept: dcore {s['d_commitments_concluded']} / "
        f"{s['d_commitments_kept']}, payments {s['p_commitments_concluded']} / "
        f"{s['p_commitments_kept']}"
    ]
    if "a3_commitments_level" in old_m.columns:
        lines += ["old level x new (payments):"]
        lines += _counts(
            both.select(
                F.col("o.a3_commitments_level").alias("old"),
                F.col("p.a3_commitments_level").alias("new"),
            ),
            ["old", "new"],
            n,
        )
    _block("A3 COMMITMENTS", lines)

    lines = list(head)
    for j, frame in (("payments", pay), ("dcore", dcore)):
        lvl = F.col("a3_commitments_level")
        pa = F.when(lvl == "kept", 2).when(lvl == "partly_kept", 1).otherwise(0)
        bc = F.col("a3_dlq_payments_points") + F.col("a3_pre_dlq_record_points")
        broken = lvl == "broken"
        unknown = F.col("a3_state") == "payment_credibility_unknown"
        f = frame.select(
            broken.alias("broken"),
            bc.alias("bc"),
            _state(pa, bc, F.col("a3_refusal_flag"), broken, unknown).alias(
                "v0_override"
            ),
            _state(pa, bc, F.col("a3_refusal_flag"), F.lit(False), unknown).alias(
                "v1_zero"
            ),
            _state(
                pa - broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v2_minus1"),
            _state(
                pa - 2 * broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v3_minus2"),
        )
        lines += [f"[{j}] Broken rows by B + C points:"]
        lines += _counts(f.where("broken"), ["bc"], n)
        for v in ("v0_override", "v1_zero", "v2_minus1", "v3_minus2"):
            lines += [f"[{j}] state {v}:"] + _counts(f, [v], n)
    _block("A3 BROKEN", lines)

    u = uncapped.select("account_id", F.col("a3_refusal_flag").alias("uncapped"))
    c = pay.join(u, "account_id", "left")
    lines = head + [
        f"{col}: {c.where(F.col(col)).count()}"
        for col in (
            "a3_refusal_flag",
            "refusal_followed_by_plan",
            "refusal_followed_by_payment",
            "a3_dispute_flag",
            "a3_hung_up_last",
            "a3_no_pickup_after_contact",
        )
    ]
    lines += [
        f"refusal without the 24-month cap: {c.where(F.col('uncapped')).count()}",
        "last right-party disposition:",
    ]
    lines += _counts(pay, ["last_rpc_disposition"], n)
    if "a3_strong_negative_reason" in old_m.columns:
        lines += ["old strong negative x new refusal:"]
        lines += _counts(
            both.select(
                F.col("o.a3_strong_negative_reason").alias("old"),
                F.col("p.a3_refusal_flag").alias("refusal"),
            ),
            ["old", "refusal"],
            n,
        )
    _block("A3 CONTACTS", lines)

    lines = head + ["unknown reason:"] + _counts(pay, ["a3_unknown_reason"], n)
    lines += ["Dimension C reason x level:"]
    lines += _counts(pay, ["pre_dlq_reason", "a3_pre_dlq_payment_level"], n)
    if floor:
        cut = pay.where(
            (F.col("pre_dlq_window_start") < F.lit(floor).cast("date"))
            & (F.col("a3_pre_dlq_payment_level") == "no_record")
            & F.col("pre_dlq_reason").isNull()
        )
        lines += [
            f"no record with the window starting before the floor {floor}: {cut.count()}"
        ]
    lines += ["Dimension B level:"] + _counts(pay, ["a3_dlq_payment_level"], n)
    _block("A3 EPISODE", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): payments judge, DCORE judge and uncapped contacts, then the blocks.
    """
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    base = create_a3_pipeline(
        product, f"{p}_check_payments", dues, payments, kept_by="payments"
    )
    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: f"{NS}.obs_latest"},
        outputs={f"{p}_check_payments": f"{p}_check_payments"},
        parameters=params,
    )

    def ns(name: str) -> str:
        return f"{NS}.{name}"

    signals = {
        "episode": ns(f"{p}_episode"),
        "instalments": ns(f"{p}_instalments"),
        "payments": ns(f"{p}_payments"),
        "dues": ns(f"{p}_dues"),
    }
    extra = [
        node(
            func=latest_month,
            inputs={
                "obs_base": obs,
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=ns("obs_latest"),
            name=f"{p}_check_latest",
            tags=TAGS,
        ),
        node(
            func=partial(
                build_commitment_signals, kept_by="dcore", grace=GRACE[product]
            ),
            inputs=signals,
            outputs=ns("commitments_dcore"),
            name=f"{p}_check_commitments_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, kept_by="dcore"),
            inputs={
                "episode": signals["episode"],
                "commitments": ns("commitments_dcore"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_dcore",
            name=f"{p}_check_state_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_contact_signals, max_months=None),
            inputs={
                "episode": signals["episode"],
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": signals["instalments"],
                "payments": signals["payments"],
                "dues": signals["dues"],
                "model_id": "params:model_id",
            },
            outputs=ns("contacts_uncapped"),
            name=f"{p}_check_contacts_uncapped",
            tags=TAGS,
        ),
        node(
            func=partial(compare_a3, floor=None) if product == "rl" else compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "pay": f"{p}_check_payments",
                "dcore": f"{p}_check_dcore",
                "uncapped": ns("contacts_uncapped"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
                **(
                    {}
                    if product == "rl"
                    else {"floor": "params:cc_a3_history_floor_date"}
                ),
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
`````

New:

`````python
"""TEMPORARY (A3 bundle): the new A3 on the latest month, with both Dimension A judges,
against the A3 output persisted before the bundle. Logs ``A3 OUTPUT``, ``A3 COMMITMENTS``,
``A3 BROKEN``, ``A3 CONTACTS``, ``A3 EPISODE``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals, build_contact_signals
from .constants import GRACE

logger = logging.getLogger(__name__)
NS = "a3_check"


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The base rows of persona_end_date's month."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _state(
    points_a: Column,
    points_bc: Column,
    refusal: Column,
    override: Column,
    unknown: Column,
) -> Column:
    """The A3 ladder for a what-if of the Broken weight."""
    pts = points_a + points_bc
    demote = refusal | override
    rung = (
        F.when(pts >= 4, F.when(demote, "moderate").otherwise("high"))
        .when((pts >= 1) & ~demote, "moderate")
        .otherwise("low")
    )
    return F.when(unknown, "unknown").otherwise(rung)


def compare_a3(
    old: DataFrame,
    pay: DataFrame,
    dcore: DataFrame,
    uncapped: DataFrame,
    model_id: str,
    persona_end_date: str,
    floor: str | None,
) -> None:
    """The check blocks (latest month)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    old_m = old.filter(F.trunc("observation_date", "month") == month)
    keep = ["a3_state_v1", "a3_commitments_level", "a3_strong_negative_reason"]
    old_m = old_m.select(
        "account_id", "observation_date", *[c for c in keep if c in old_m.columns]
    )
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    old_m = (
        old_m.withColumn("_r", newest).where("_r = 1").drop("_r", "observation_date")
    )
    n = pay.count()
    p, d = pay.alias("p"), dcore.alias("d")
    both = p.join(d, "account_id").join(old_m.alias("o"), "account_id", "left")
    head = [
        f"model_id: {model_id}",
        f"rows new: {n}, old (latest per account): {old_m.count()}",
    ]

    lines = head + ["old a3_state_v1 x new (payments):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("p.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["old x new (dcore):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("d.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["new dcore x new payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_state").alias("dcore"), F.col("p.a3_state").alias("payments")
        ),
        ["dcore", "payments"],
        n,
    )
    _block("A3 OUTPUT", lines)

    lines = head + ["Dimension A level, dcore x payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_commitments_level").alias("dcore"),
            F.col("p.a3_commitments_level").alias("payments"),
        ),
        ["dcore", "payments"],
        n,
    )
    s = both.agg(
        *[
            F.sum(f"{j}.{c}").alias(f"{j}_{c}")
            for j in ("d", "p")
            for c in ("commitments_concluded", "commitments_kept")
        ]
    ).first()
    lines += [
        f"instalments concluded / kept: dcore {s['d_commitments_concluded']} / "
        f"{s['d_commitments_kept']}, payments {s['p_commitments_concluded']} / "
        f"{s['p_commitments_kept']}"
    ]
    if "a3_commitments_level" in old_m.columns:
        lines += ["old level x new (payments):"]
        lines += _counts(
            both.select(
                F.col("o.a3_commitments_level").alias("old"),
                F.col("p.a3_commitments_level").alias("new"),
            ),
            ["old", "new"],
            n,
        )
    _block("A3 COMMITMENTS", lines)

    lines = list(head)
    for j, frame in (("payments", pay), ("dcore", dcore)):
        lvl = F.col("a3_commitments_level")
        pa = F.when(lvl == "kept", 2).when(lvl == "partly_kept", 1).otherwise(0)
        bc = F.col("a3_dlq_payments_points") + F.col("a3_pre_dlq_record_points")
        broken = lvl == "broken"
        unknown = F.col("a3_state") == "payment_credibility_unknown"
        f = frame.select(
            broken.alias("broken"),
            bc.alias("bc"),
            _state(pa, bc, F.col("a3_refusal_flag"), broken, unknown).alias(
                "v0_override"
            ),
            _state(pa, bc, F.col("a3_refusal_flag"), F.lit(False), unknown).alias(
                "v1_zero"
            ),
            _state(
                pa - broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v2_minus1"),
            _state(
                pa - 2 * broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v3_minus2"),
        )
        lines += [f"[{j}] Broken rows by B + C points:"]
        lines += _counts(f.where("broken"), ["bc"], n)
        for v in ("v0_override", "v1_zero", "v2_minus1", "v3_minus2"):
            lines += [f"[{j}] state {v}:"] + _counts(f, [v], n)
    _block("A3 BROKEN", lines)

    u = uncapped.select("account_id", F.col("a3_refusal_flag").alias("uncapped"))
    c = pay.join(u, "account_id", "left")
    lines = head + [
        f"{col}: {c.where(F.col(col)).count()}"
        for col in (
            "a3_refusal_flag",
            "refusal_followed_by_plan",
            "refusal_followed_by_payment",
            "a3_dispute_flag",
            "a3_hung_up_last",
            "a3_no_pickup_after_contact",
        )
    ]
    lines += [
        f"refusal without the 24-month cap: {c.where(F.col('uncapped')).count()}",
        "last right-party disposition:",
    ]
    lines += _counts(pay, ["last_rpc_disposition"], n)
    if "a3_strong_negative_reason" in old_m.columns:
        lines += ["old strong negative x new refusal:"]
        lines += _counts(
            both.select(
                F.col("o.a3_strong_negative_reason").alias("old"),
                F.col("p.a3_refusal_flag").alias("refusal"),
            ),
            ["old", "refusal"],
            n,
        )
    _block("A3 CONTACTS", lines)

    lines = head + ["unknown reason:"] + _counts(pay, ["a3_unknown_reason"], n)
    lines += ["Dimension C reason x level:"]
    lines += _counts(pay, ["pre_dlq_reason", "a3_pre_dlq_payment_level"], n)
    if floor:
        cut = pay.where(
            (F.col("pre_dlq_window_start") < F.lit(floor).cast("date"))
            & (F.col("a3_pre_dlq_payment_level") == "no_record")
            & F.col("pre_dlq_reason").isNull()
        )
        lines += [
            f"no record with the window starting before the floor {floor}: {cut.count()}"
        ]
    lines += ["Dimension B level:"] + _counts(pay, ["a3_dlq_payment_level"], n)
    _block("A3 EPISODE", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): payments judge, DCORE judge and uncapped contacts, then the blocks.
    """
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    base = create_a3_pipeline(
        product, f"{p}_check_payments", dues, payments, kept_by="payments"
    )

    def ns(
        name: str,
    ) -> str:  # a check-only dataset name (no dots: Kedro reserves them)
        return f"{NS}__{name}"

    final = f"{p}_check_payments"
    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    # Every intermediate gets an explicit check name, so the namespace only prefixes
    # the node names.
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: ns("obs_latest")},
        outputs={o: o if o == final else ns(o) for o in base.all_outputs()},
        parameters=params,
    )

    signals = {
        "episode": ns(f"{p}_episode"),
        "instalments": ns(f"{p}_instalments"),
        "payments": ns(f"{p}_payments"),
        "dues": ns(f"{p}_dues"),
    }
    extra = [
        node(
            func=latest_month,
            inputs={
                "obs_base": obs,
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=ns("obs_latest"),
            name=f"{p}_check_latest",
            tags=TAGS,
        ),
        node(
            func=partial(
                build_commitment_signals, kept_by="dcore", grace=GRACE[product]
            ),
            inputs=signals,
            outputs=ns("commitments_dcore"),
            name=f"{p}_check_commitments_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, kept_by="dcore"),
            inputs={
                "episode": signals["episode"],
                "commitments": ns("commitments_dcore"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_dcore",
            name=f"{p}_check_state_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_contact_signals, max_months=None),
            inputs={
                "episode": signals["episode"],
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": signals["instalments"],
                "payments": signals["payments"],
                "dues": signals["dues"],
                "model_id": "params:model_id",
            },
            outputs=ns("contacts_uncapped"),
            name=f"{p}_check_contacts_uncapped",
            tags=TAGS,
        ),
        node(
            func=partial(compare_a3, floor=None) if product == "rl" else compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "pay": f"{p}_check_payments",
                "dcore": f"{p}_check_dcore",
                "uncapped": ns("contacts_uncapped"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
                **(
                    {}
                    if product == "rl"
                    else {"floor": "params:cc_a3_history_floor_date"}
                ),
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
`````

## Apply script

Written to `data/input/mirror_bundles/apply_bundle.py` by step 3.

`````python
"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

When a repo file differs from the copy the bundle was built from (an edit made at work, a
lint fix, a photo slip), the bundle still applies — it never stops on a difference:
  * replace: three-way merge (git merge-file) of this repo's file, the bundle's base copy and
    the bundle's new version. Edits made here survive wherever the bundle did not change the
    same lines; where both changed the same lines, the bundle's version wins.
  * delete: the file is deleted (git history keeps it).
  * add over an existing file: the bundle's version is written.
Each such file is listed as MERGED; review it with `git diff <path>` before committing.

Safety rules:
  * refuses to write on main/master, or when a touched file has uncommitted changes, so
    `git diff` shows exactly what the bundle did and --revert restores HEAD.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

APPLY_VERSION = 7
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


# Separator lines in comments (``# ── Node 1 ─────``, ``#######``) are transcribed from
# photos, where their exact length cannot be read. Runs of 4+ identical separator
# characters therefore compare equal whatever their length; so do trailing spaces.
_RULE_RUN = re.compile(r"([─━═=\-#*~_])\1{3,}")


def _loose(text: str) -> str:
    return "\n".join(
        _RULE_RUN.sub(r"\1\1\1\1", line.rstrip()) for line in _norm(text).split("\n")
    )


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _same_code(path: str, a: str, b: str) -> bool:
    """Same Python code (comments and docstrings aside) or the same YAML content."""
    try:
        if path.endswith(".py"):
            return ast.dump(_strip_docstrings(ast.parse(a))) == ast.dump(
                _strip_docstrings(ast.parse(b))
            )
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(
        e["path"], current, e["new"]
    )


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_dump(yaml.safe_load(text), sort_keys=True)
    except Exception:  # pylint: disable=broad-except
        pass
    return _loose(text)


def _matches_base(current: str | None, e: dict) -> bool:
    """The repo file is the version the bundle was built from: identical up to
    separator lengths and trailing spaces, or — since comments and docstrings are
    transcribed from photos — the same code / YAML content."""
    if current is None:
        return False
    if _loose(current) == _loose(e["base"]):
        return True
    return _same_code(e["path"], current, e["base"])


def _rebase(new: str, base: str, current: str) -> str:
    """``new`` with every line the bundle did not change taken from ``current``.

    ``current`` matches ``base`` line by line up to separator lengths (``_matches_base``),
    so the repo's own separators survive and ``git diff`` shows only real changes.
    """
    base_l, new_l, cur_l = (_norm(t).split("\n") for t in (base, new, current))
    if len(cur_l) != len(base_l):  # comments wrapped differently: no line alignment
        return new
    out: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, base_l, new_l, autojunk=False
    ).get_opcodes():
        out += cur_l[i1:i2] if tag == "equal" else new_l[j1:j2]
    return "\n".join(out)


def _merge3(current: str, base: str, new: str) -> str:
    """Three-way merge: this repo's edits on top of the bundle's change (git merge-file;
    on overlapping lines the bundle's version wins). Without git: the bundle's version.
    """
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, text in (("current", current), ("base", base), ("new", new)):
            f = pathlib.Path(tmp) / name
            f.write_text(_norm(text), encoding="utf-8")
            paths.append(str(f))
        try:
            out = subprocess.run(
                ["git", "merge-file", "-p", "--theirs", *paths],
                capture_output=True,
                check=False,
            )
        except OSError:
            return new
    return out.stdout.decode("utf-8") if out.returncode >= 0 else new


def _sha(text: str) -> str:
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_bytes().decode("utf-8")


# ── Parsing ──────────────────────────────────────────────────────────────────


def parse_bundle(md: str) -> list[dict]:
    """Return one dict per file: path, action, base/new sha and text."""
    lines = _norm(md).split("\n")
    entries, i = [], 0
    while i < len(lines):
        m = re.match(r"^### FILE: `([^`]+)`\s*$", lines[i])
        if not m:
            i += 1
            continue
        meta = lines[i + 1]
        entry = {
            "path": m.group(1),
            "action": re.search(r"action: (add|replace|delete)", meta).group(1),
            "base_sha": None,
            "new_sha": None,
            "base": None,
            "new": None,
        }
        for kind in ("base", "new"):
            sm = re.search(kind + r" sha256 `([0-9a-f]{64})`", meta)
            if sm:
                entry[kind + "_sha"] = sm.group(1)
        j = i + 2
        for kind in ("base", "new"):
            if entry[kind + "_sha"] is None:
                continue
            while not FENCE.match(lines[j]):
                j += 1
            fence = FENCE.match(lines[j]).group(1)
            k = j + 1
            while lines[k] != fence:
                k += 1
            body = "\n".join(lines[j + 1 : k])
            if re.search(kind + r" trailing newline: yes", meta) and body:
                body += "\n"
            entry[kind] = body
            j = k + 1
        entries.append(entry)
        i = j
    return entries


def verify_bundle(entries: list[dict]) -> list[str]:
    """Blocks whose content no longer matches the checksum (a damaged copy)."""
    errors = []
    for e in entries:
        for kind in ("base", "new"):
            if e[kind + "_sha"] and _sha(e[kind]) != e[kind + "_sha"]:
                errors.append(f"{e['path']}: {kind} block does not match its checksum")
    return errors


# ── Git guards ───────────────────────────────────────────────────────────────


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _head_version(path: str) -> str | None:
    """The committed (HEAD) content of a file, byte-exact, or None."""
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("utf-8")


def git_problems(entries: list[dict]) -> list[str]:
    """Reasons to refuse: a protected branch, or uncommitted edits in a touched file."""
    problems = []
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch is not None:
        branch = branch.strip()
    if branch is None:
        print("note: not a git repository (or git missing) — branch checks skipped")
        return problems
    if branch in PROTECTED_BRANCHES:
        problems.append(
            f"you are on '{branch}' — create a branch first: git checkout -b <name>"
        )
    # Files already in their final state may be uncommitted (applied, not yet committed).
    pending = [e["path"] for e in entries if file_status(e) != "done"]
    dirty = _git("status", "--porcelain", "--", *pending) if pending else ""
    for line in (dirty or "").splitlines():
        if line[:2] != "??":  # untracked files are compared by content below
            problems.append(f"uncommitted change in a touched file: {line[3:]}")
    return problems


# ── Status ───────────────────────────────────────────────────────────────────


def file_status(e: dict) -> str:  # pylint: disable=too-many-return-statements
    """One of: todo, done, merge (the repo file differs from the bundle's base copy)."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "merge"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "merge"
    # delete
    if current is None:
        return "done"
    return "todo" if _matches_base(current, e) else "merge"


def explain_merge(e: dict) -> None:
    """One line on what happened to a file that differed from the bundle's copy."""
    what = {
        "replace": "merged with this repo's own edits",
        "delete": "deleted, although it had edits the bundle's copy lacks (git keeps them)",
        "add": "already existed with other content; replaced by the bundle's version",
    }[e["action"]]
    print(f"MERGED {e['path']}: {what} — review: git diff -- {e['path']}")


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    """One line per bundle file: its action and status."""
    word = {
        "todo": "will apply",
        "done": "already applied",
        "merge": "will apply — MERGED (differs from the bundle's copy)",
    }
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        note = ""
        if s == "todo" and _comment_only(e):
            note = "  (comments differ from the bundle's copy — fine)"
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}{note}")


# ── Post-apply checks ────────────────────────────────────────────────────────


def _module_name(path: str) -> str | None:
    p = pathlib.PurePosixPath(path)
    if p.suffix != ".py" or p.parts[0] != "src":
        return None
    parts = list(p.with_suffix("").parts[1:])
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def compile_and_import(entries: list[dict], do_import: bool) -> list[str]:
    """Compile every touched .py file and import its module (plus the registry)."""
    failures = []
    existing = [
        e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")
    ]
    for e in existing:
        try:
            compile(_read(pathlib.Path(e["path"])), e["path"], "exec")
        except SyntaxError as exc:
            failures.append(f"compile: {e['path']}: {exc}")
    if not do_import or failures:
        return failures
    modules = [m for m in (_module_name(e["path"]) for e in existing) if m]
    if pathlib.Path("src/enbd_collections/pipeline_registry.py").is_file():
        modules.append("enbd_collections.pipeline_registry")
    env = dict(os.environ)
    env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")
    for mod in dict.fromkeys(modules):
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    """Dry run: what --apply would do; False only when git refuses."""
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for p in problems:
        print("REFUSED: " + p)
    print(
        f"\n{statuses.count('todo') + statuses.count('merge')} to apply "
        f"({statuses.count('merge')} merged), {statuses.count('done')} already applied"
    )
    print("CHECK FAILED — nothing was written" if problems else "CHECK PASSED")
    return not problems


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    """Write every file (merging where this repo differs), then verify and import."""
    if not cmd_check(entries):
        return False
    merged = []
    for e in entries:
        status = file_status(e)
        if status == "done":
            continue
        path = pathlib.Path(e["path"])
        if status == "merge":
            merged.append(e)
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
            continue
        new = e["new"]
        if e["action"] == "replace":
            current = _read(path)
            if status == "todo":
                new = _rebase(new, e["base"], current)
            elif current is not None:  # a file missing here gets the bundle's version
                new = _merge3(current, e["base"], new)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(new.encode("utf-8"))
    print()
    for e in merged:
        explain_merge(e)
    # a merged file keeps this repo's own edits, so it need not equal the bundle's version
    merged_paths = {e["path"] for e in merged if e["action"] == "replace"}
    bad = [
        e["path"]
        for e in entries
        if e["path"] not in merged_paths and file_status(e) != "done"
    ]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(
        f"{len(entries)} files in their new state, compile OK"
        + (", imports OK" if do_import else " (imports skipped)")
    )
    print(
        "APPLY PASSED — review with `git status` / `git diff`"
        + (f" (look closely at the {len(merged)} MERGED files)" if merged else "")
    )
    return True


def cmd_revert(entries: list[dict]) -> bool:
    """Put every touched file back to HEAD (apply refuses to run over uncommitted changes,
    so HEAD is the state before --apply); files the bundle added are removed."""
    for e in entries:
        path = pathlib.Path(e["path"])
        committed = _head_version(e["path"])
        if committed is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(committed.encode("utf-8"))
        elif path.exists():
            path.unlink()
            _prune_empty_dirs(path.parent)
    print("REVERT DONE — `git status` should show none of the bundle's files")
    return True


def main() -> int:
    """Parse the arguments, verify the bundle's checksums and run the chosen mode."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--revert", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    args = ap.parse_args()

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(
            f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
            f"{APPLY_VERSION}. Redo step 3 of the bundle."
        )
        return 1
    entries = parse_bundle(md)
    if not entries:
        print("No files found — was the raw markdown copied (not the rendered page)?")
        return 1
    errors = verify_bundle(entries)
    if errors:
        for err in errors:
            print("DAMAGED: " + err)
        print("The bundle copy is damaged — recopy the RAW file. Nothing was written.")
        return 1
    if not pathlib.Path("src").is_dir():
        print("Run this from the workplace repo root (no src/ folder here).")
        return 1
    print(f"{len(entries)} files in bundle, all checksums OK\n")
    if args.check:
        ok = cmd_check(entries)
    elif args.apply:
        ok = cmd_apply(entries, do_import=not args.no_import)
    else:
        ok = cmd_revert(entries)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
`````

## Cleanup prompt

Copy this to the workplace assistant in UAT once the bundle's PROD checks are done:

````text
Clean up after mirror bundle 19_a3_check_dataset_names.md, on the bundle's branch.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
