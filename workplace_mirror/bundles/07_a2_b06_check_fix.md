# Mirror bundle 07 — A2 — bundle 06 check fix (old single-state schema) + reachability attribution

apply_bundle version: 6 · built 2026-10-29 from `840e3f5..3ac0310` · source: 0 added, 2 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/07_a2_b06_check_fix.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '07_a2_b06_check_fix.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/07_a2_b06_check_fix.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A2: b06 check compares on the old single-state schema + B06 REACH" && git push
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/07_a2_b06_check_fix.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Only the log nodes are re-run; everything upstream is already written (the earlier runs stopped
at the comparison node). First **`cc_60_180`** (the default), then **`rl_60_180`**. Switch
`model_id` back to `cc_60_180` when done.

**Step 6.** CC — the three log nodes:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check --nodes "compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules,explain_crx_cc_a2_b06_reach"
```

**Step 7.** RL (`model_id: rl_60_180`) — the log nodes, including the debit and product blocks:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check --nodes "compare_crx_rl_a2_b06,describe_crx_rl_a2_b06_rules,explain_crx_rl_a2_b06_reach,describe_crx_rl_a2_b06_debit,split_crx_rl_a2_b06_product"
```

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: CC `OUTPUT`,
`RULES` and `REACH` (DEBIT already received); RL `OUTPUT`, `RULES`, `REACH`, `DEBIT`, `PRODUCT`. Then continue with
bundle 06 step 8 and its cleanup only after the review.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

Fixes the temporary bundle 06 check so it finishes in PROD. The old A2 output in PROD still has the
earlier single-state schema (`a2_state_v1`), so `compare_a2_outputs` could not find
`location_state`; it now compares on whichever schema the old output has (old `a2_state_v1` ×
new location and × new reachability). `describe_a2_rules` also logs reachability × last contact
(in the window / before it / never), to show how many Non-Reachable rows had a contact in the
window. A new log node `explain_crx_<p>_a2_b06_reach` (`B06 REACH`) explains the reachability move: it
rebuilds reachability from the same DCORE calls under the earlier rule (any contact ever is
Reachable unless the last 3 call days only rang out, admin entries kept as calls), then applies
each change in turn — dead lines / invalid numbers / LEFT_MSG count as failed, admin and legal
entries ignored, the contact must fall in the window — logging the state mix and the moves at
every step, and checks that the last step equals the engine's `reachability_state`. Only
`b06_check.py` and the check pipeline change; the engine and its output are untouched.

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
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/b06_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/b06_check.py`
action: replace · base sha256 `d62bab99dddd4d6b7e6c430529b40bedc937c6ad8e064dc0b6ae0c4763fd99d1` · base trailing newline: yes · new sha256 `e5353dcc27094c25e703df1c15fa0d04a64cad319da006ecad2b0eb4b6c6a0c1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (mirror bundle 06): the old A2 vs the new engine, run in PROD.

Log blocks, aggregates only:

* ``compare_a2_outputs`` (``B06 OUTPUT``): the old output (``crx_<p>_a2_locatability``)
  against the new one (``crx_<p>_a2_locatability_b06_check``) in the latest month — an
  old row is matched to the new row of the same account and month (the month's latest
  old observation) — plus the new location / reachability shares per month.
* ``describe_a2_rules`` (``B06 RULES``): which rule fires, which source holds the
  deciding evidence, unknown reasons, call days, deceased sources.
* ``describe_debit_evidence`` (``B06 DEBIT``): the base customers' rows in
  ``prm_casa_card_transactions`` by month, channel / type and place (the Offline → Machine
  change, ATM placement), and their ``reason_for_excluding`` values.
* ``split_by_product`` (``B06 PRODUCT``, RL only): the latest month by ``loan_type``.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_uae

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B06 {name} START === [{model_id}]",
        *lines,
        f"=== B06 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<24}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _snake(col: str) -> F.Column:
    """'In Country' → 'in_country', 'Non-Reachable' → 'non_reachable'."""
    return F.regexp_replace(F.lower(F.trim(col)), "[ -]+", "_")


def compare_a2_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new location, reachability and deceased in the latest month; new shares
    per month."""
    latest_new = _latest_month(new)
    month = latest_new.agg(F.trunc(F.max("observation_date"), "month")).first()[0]
    in_month = Window.partitionBy("account_id").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.filter(F.trunc("observation_date", "month") == F.lit(month))
        .withColumn("_rn", F.row_number().over(in_month))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string").alias("account_id"),
            _snake("location_state").alias("old_location"),
            _snake("reachability_state").alias("old_reachability"),
            F.col("deceased_flag_v2").cast("int").alias("old_deceased"),
        )
    )
    both = latest_new.join(old_m, on="account_id", how="full")
    lines = [
        (
            f"month {month}: new rows {latest_new.count()}, old rows {old_m.count()}, "
            f"new only {both.filter(F.col('old_location').isNull()).count()}, "
            f"old only {both.filter(F.col('a2_state').isNull()).count()}"
        ),
        "new a2_state:",
        *_table(latest_new, "a2_state"),
        "location old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_location", "location_state"
        ),
        "reachability old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()),
            "old_reachability",
            "reachability_state",
        ),
        "deceased old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_deceased", "deceased_flag"
        ),
        "new location_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "location_state",
        ),
        "new reachability_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "reachability_state",
        ),
    ]
    _log("OUTPUT", model_id, lines)


def describe_a2_rules(new: DataFrame, model_id: str) -> None:
    """Rules, deciding sources, unknown reasons, call days and deceased sources in the
    latest month."""
    df = _latest_month(new)
    days = F.col("attempt_days_in_window")
    lines = [
        "location_rule x deciding source (L1: latest foreign, else latest UAE):",
        *_table(
            df.withColumn(
                "source",
                F.when(
                    F.col("location_rule") == "L1", F.col("last_foreign_source")
                ).otherwise(F.col("last_uae_source")),
            ),
            "location_rule",
            "source",
        ),
        "location_unknown_reason:",
        *_table(
            df.filter(F.col("location_state") == "unknown"), "location_unknown_reason"
        ),
        "L2 rows by months since the latest UAE evidence:",
        *_table(
            df.filter(F.col("location_rule") == "L2").withColumn(
                "months",
                F.floor(F.months_between("observation_date", "last_uae_date")).cast(
                    "int"
                ),
            ),
            "months",
        ),
        "reachability_state x reason:",
        *_table(df, "reachability_state", "reachability_unknown_reason"),
        "call days in the window:",
        *_table(
            df.withColumn(
                "call_days",
                F.when(days == 0, "0")
                .when(days < 3, "1-2")
                .when(days < 6, "3-5")
                .otherwise("6+"),
            ),
            "call_days",
        ),
        "skip-trace status ever (diagnostic) x location_state:",
        *_table(
            df.withColumn("skip_trace", F.col("last_skip_trace_date").isNotNull()),
            "skip_trace",
            "location_state",
        ),
        "deceased_source:",
        *_table(df.filter(F.col("deceased_flag") == 1), "deceased_source"),
    ]
    _log("RULES", model_id, lines)


def describe_debit_evidence(
    obs_base: DataFrame, casa_cards: DataFrame, model_id: str
) -> None:
    """The latest month's base customers' debit-card rows by month, type and place."""
    cifs = (
        _latest_month(obs_base)
        .select("cif_id")
        .filter(F.col("cif_id").isNotNull())
        .distinct()
    )
    uae = is_uae(F.col("place_country"))
    rows = (
        casa_cards.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .withColumn(
            "type",
            F.when(F.col("channel_desc") == "ATM Transactions", F.lit("ATM")).otherwise(
                F.coalesce(F.col("merchant_type_desc"), F.lit("NULL"))
            ),
        )
        .withColumn("place", F.when(uae, "uae").when(~uae, "abroad").otherwise("none"))
        .withColumn("month", F.trunc(F.coalesce("value_date", "tran_date"), "month"))
    )
    lines = [
        "rows by month x type x place:",
        *_table(rows, "month", "type", "place"),
        "place_source by type:",
        *_table(rows, "type", "place_source"),
        "reason_for_excluding (all months):",
        *_table(rows, "reason_for_excluding"),
    ]
    _log("DEBIT", model_id, lines)


def split_by_product(new: DataFrame, rl_spine: DataFrame, model_id: str) -> None:
    """The latest month's states by ``loan_type`` (RL)."""
    products = rl_spine.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(["account_id", "observation_date"])
    df = _latest_month(new).join(
        products, on=["account_id", "observation_date"], how="left"
    )
    lines = [
        "loan_type x location_state:",
        *_table(df, "loan_type", "location_state"),
        "loan_type x reachability_state:",
        *_table(df, "loan_type", "reachability_state"),
        "loan_type x deceased_flag:",
        *_table(df, "loan_type", "deceased_flag"),
    ]
    _log("PRODUCT", model_id, lines)
`````

New:

`````python
"""TEMPORARY (mirror bundle 06): the old A2 vs the new engine, run in PROD.

Log blocks, aggregates only:

* ``compare_a2_outputs`` (``B06 OUTPUT``): the old output (``crx_<p>_a2_locatability``)
  against the new one (``crx_<p>_a2_locatability_b06_check``) in the latest month — an
  old row is matched to the new row of the same account and month (the month's latest
  old observation) — plus the new location / reachability shares per month.
* ``describe_a2_rules`` (``B06 RULES``): which rule fires, which source holds the
  deciding evidence, unknown reasons, call days, deceased sources.
* ``describe_debit_evidence`` (``B06 DEBIT``): the base customers' rows in
  ``prm_casa_card_transactions`` by month, channel / type and place (the Offline → Machine
  change, ATM placement), and their ``reason_for_excluding`` values.
* ``split_by_product`` (``B06 PRODUCT``, RL only): the latest month by ``loan_type``.
* ``explain_reachability`` (``B06 REACH``): reachability rebuilt under the earlier rule,
  then each change in turn, with the moves at every step.

Removed by the bundle's cleanup.
"""

import logging
from itertools import pairwise

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_uae

from .._common import GRAIN, window_months
from .codes import (
    CALL_CODES,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SUCCESS_CATEGORY,
)
from .signals import GONE_DARK_DAYS, _dcore_events

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B06 {name} START === [{model_id}]",
        *lines,
        f"=== B06 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<24}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _snake(col: str) -> F.Column:
    """'In Country' → 'in_country', 'Non-Reachable' → 'non_reachable'."""
    return F.regexp_replace(F.lower(F.trim(col)), "[ -]+", "_")


def compare_a2_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new in the latest month; new shares per month.

    The PROD old output may still carry the earlier single-state schema
    (``a2_state_v1``) instead of ``location_state`` / ``reachability_state``; the old
    side is compared on whichever it has.
    """
    latest_new = _latest_month(new)
    month = latest_new.agg(F.trunc(F.max("observation_date"), "month")).first()[0]
    in_month = Window.partitionBy("account_id").orderBy(
        F.col("observation_date").desc()
    )
    two_dim = "location_state" in old.columns
    old_cols = (
        [
            _snake("location_state").alias("old_location"),
            _snake("reachability_state").alias("old_reachability"),
        ]
        if two_dim
        else [_snake("a2_state_v1").alias("old_state")]
    )
    old_m = (
        old.filter(F.trunc("observation_date", "month") == F.lit(month))
        .withColumn("_rn", F.row_number().over(in_month))
        .filter(F.col("_rn") == 1)
        .select(F.col("account_id").cast("string").alias("account_id"), *old_cols)
        .withColumn("_old", F.lit(1))
    )
    both = latest_new.join(old_m, on="account_id", how="full")
    matched = both.filter(F.col("a2_state").isNotNull())
    if two_dim:
        compare = [
            "location old x new:",
            *_table(matched, "old_location", "location_state"),
            "reachability old x new:",
            *_table(matched, "old_reachability", "reachability_state"),
        ]
    else:
        compare = [
            "old a2_state_v1:",
            *_table(old_m, "old_state"),
            "old a2_state_v1 x new location:",
            *_table(matched, "old_state", "location_state"),
            "old a2_state_v1 x new reachability:",
            *_table(matched, "old_state", "reachability_state"),
        ]
    lines = [
        (
            f"month {month}: new rows {latest_new.count()}, old rows {old_m.count()}, "
            f"new only {both.filter(F.col('_old').isNull()).count()}, "
            f"old only {both.filter(F.col('a2_state').isNull()).count()}"
        ),
        "new a2_state:",
        *_table(latest_new, "a2_state"),
        *compare,
        "new location_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "location_state",
        ),
        "new reachability_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "reachability_state",
        ),
    ]
    _log("OUTPUT", model_id, lines)


def describe_a2_rules(new: DataFrame, model_id: str) -> None:
    """Rules, deciding sources, unknown reasons, call days and deceased sources in the
    latest month."""
    df = _latest_month(new)
    days = F.col("attempt_days_in_window")
    lines = [
        "location_rule x deciding source (L1: latest foreign, else latest UAE):",
        *_table(
            df.withColumn(
                "source",
                F.when(
                    F.col("location_rule") == "L1", F.col("last_foreign_source")
                ).otherwise(F.col("last_uae_source")),
            ),
            "location_rule",
            "source",
        ),
        "location_unknown_reason:",
        *_table(
            df.filter(F.col("location_state") == "unknown"), "location_unknown_reason"
        ),
        "L2 rows by months since the latest UAE evidence:",
        *_table(
            df.filter(F.col("location_rule") == "L2").withColumn(
                "months",
                F.floor(F.months_between("observation_date", "last_uae_date")).cast(
                    "int"
                ),
            ),
            "months",
        ),
        "reachability_state x reason:",
        *_table(df, "reachability_state", "reachability_unknown_reason"),
        "reachability_state x last contact (in W / before W / never):",
        *_table(
            df.withColumn(
                "last_contact",
                F.when(F.col("last_contact_date").isNull(), "never")
                .when(
                    F.col("last_contact_date")
                    >= F.add_months(
                        F.trunc("observation_date", "month"),
                        1 - window_months(model_id),
                    ),
                    "in_W",
                )
                .otherwise("before_W"),
            ),
            "reachability_state",
            "last_contact",
        ),
        "call days in the window:",
        *_table(
            df.withColumn(
                "call_days",
                F.when(days == 0, "0")
                .when(days < 3, "1-2")
                .when(days < 6, "3-5")
                .otherwise("6+"),
            ),
            "call_days",
        ),
        "skip-trace status ever (diagnostic) x location_state:",
        *_table(
            df.withColumn("skip_trace", F.col("last_skip_trace_date").isNotNull()),
            "skip_trace",
            "location_state",
        ),
        "deceased_source:",
        *_table(df.filter(F.col("deceased_flag") == 1), "deceased_source"),
    ]
    _log("RULES", model_id, lines)


def describe_debit_evidence(
    obs_base: DataFrame, casa_cards: DataFrame, model_id: str
) -> None:
    """The latest month's base customers' debit-card rows by month, type and place."""
    cifs = (
        _latest_month(obs_base)
        .select("cif_id")
        .filter(F.col("cif_id").isNotNull())
        .distinct()
    )
    uae = is_uae(F.col("place_country"))
    rows = (
        casa_cards.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .withColumn(
            "type",
            F.when(F.col("channel_desc") == "ATM Transactions", F.lit("ATM")).otherwise(
                F.coalesce(F.col("merchant_type_desc"), F.lit("NULL"))
            ),
        )
        .withColumn("place", F.when(uae, "uae").when(~uae, "abroad").otherwise("none"))
        .withColumn("month", F.trunc(F.coalesce("value_date", "tran_date"), "month"))
    )
    lines = [
        "rows by month x type x place:",
        *_table(rows, "month", "type", "place"),
        "place_source by type:",
        *_table(rows, "type", "place_source"),
        "reason_for_excluding (all months):",
        *_table(rows, "reason_for_excluding"),
    ]
    _log("DEBIT", model_id, lines)


def split_by_product(new: DataFrame, rl_spine: DataFrame, model_id: str) -> None:
    """The latest month's states by ``loan_type`` (RL)."""
    products = rl_spine.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(["account_id", "observation_date"])
    df = _latest_month(new).join(
        products, on=["account_id", "observation_date"], how="left"
    )
    lines = [
        "loan_type x location_state:",
        *_table(df, "loan_type", "location_state"),
        "loan_type x reachability_state:",
        *_table(df, "loan_type", "reachability_state"),
        "loan_type x deceased_flag:",
        *_table(df, "loan_type", "deceased_flag"),
    ]
    _log("PRODUCT", model_id, lines)


# Rang out / no answer only: the narrow failure set of the earlier rule.
_RINGING = frozenset({"RINGING NO REPLY", "RINGING NO RESPONSE", "NO ANSWER"})


def _gone_dark(
    calls: DataFrame, failed_names: frozenset, w_start: F.Column
) -> DataFrame:
    """Per row: gone dark (last GONE_DARK_DAYS call days all failed, oldest in W, no
    contact since) with ``failed_names`` as the failure set and the given calls."""
    outbound = F.col("action_code").isin(*OUTBOUND_CODES)
    days = calls.groupBy(*GRAIN, "day").agg(
        F.max(outbound.cast("int")).alias("_attempt"),
        F.max(F.col("_contact").cast("int")).alias("_c"),
        F.min(F.when(outbound, F.col("name").isin(*failed_names).cast("int"))).alias(
            "_all_failed"
        ),
    )
    days = days.withColumn(
        "_failed", ((F.col("_c") == 0) & (F.col("_all_failed") == 1)).cast("int")
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= GONE_DARK_DAYS)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n"),
            F.sum("_failed").alias("_f"),
            F.min("day").alias("_oldest"),
        )
    )
    contact = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_c") == 1, F.col("day"))).alias("_last_contact")
    )
    return last.join(contact, on=list(GRAIN), how="left").select(
        *GRAIN,
        (
            (F.col("_n") == GONE_DARK_DAYS)
            & (F.col("_f") == GONE_DARK_DAYS)
            & (F.col("_oldest") >= w_start)
            & (
                F.col("_last_contact").isNull()
                | (F.col("_last_contact") < F.col("_oldest"))
            )
        ).alias("gd"),
    )


def explain_reachability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    new: DataFrame,
    model_id: str,
) -> None:
    """Reachability rebuilt from the same DCORE calls under the earlier rule, then each
    change applied in turn, latest month: the state mix after every step and the moves
    between steps.

    R0 earlier rule: any contact ever → reachable, unless the last 3 call days only rang
       out (admin entries kept as calls) → non_reachable
    R1 + dead lines, invalid numbers and LEFT_MSG count as failed (D-A2-7, D-A2-17)
    R2 + admin / legal entries ignored (D-A2-17)
    R3 + the contact must be in W (= the new rule; checked against ``new``)
    """
    obs = _latest_month(obs_base).select(*GRAIN)
    events = _dcore_events(obs, followup, agreements)
    name, code = F.col("name"), F.col("action_code")
    events = events.withColumn(
        "_contact",
        code.isin(*INBOUND_CODES)
        | (code.isin(*OUTBOUND_CODES) & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT),
    )
    calls_all = events.filter(code.isin(*CALL_CODES))
    calls_new = calls_all.filter(
        ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    w_start = F.add_months(
        F.trunc("observation_date", "month"), 1 - window_months(model_id)
    )
    contact = calls_new.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact"), F.col("day"))).alias("last_contact")
    )
    variants = {
        "gd_r0": (calls_all, _RINGING),
        "gd_r1": (calls_all, FAILED_CALL),
        "gd_r2": (calls_new, FAILED_CALL),
    }
    df = obs.join(contact, on=list(GRAIN), how="left").withColumn("_w", w_start)
    for col, (calls, failed) in variants.items():
        gd = _gone_dark(calls, failed, w_start).withColumnRenamed("gd", col)
        df = df.join(gd, on=list(GRAIN), how="left")

    def state(gd: str, in_window: bool) -> F.Column:
        has_contact = (
            F.col("last_contact") >= F.col("_w")
            if in_window
            else F.col("last_contact").isNotNull()
        )
        return (
            F.when(F.coalesce(F.col(gd), F.lit(False)), "non_reachable")
            .when(has_contact, "reachable")
            .otherwise("unknown")
        )

    df = (
        df.withColumn("R0", state("gd_r0", False))
        .withColumn("R1", state("gd_r1", False))
        .withColumn("R2", state("gd_r2", False))
        .withColumn("R3", state("gd_r2", True))
        .cache()
    )
    steps = ["R0", "R1", "R2", "R3"]
    lines = []
    for step in steps:
        lines += [f"{step} state:", *_table(df, step)]
    for before, after in pairwise(steps):
        lines += [
            f"moves {before} -> {after}:",
            *_table(df.filter(F.col(before) != F.col(after)), before, after),
        ]
    engine = _latest_month(new).select(
        *GRAIN, F.col("reachability_state").alias("_engine")
    )
    mismatches = (
        df.join(engine, on=list(GRAIN), how="inner")
        .filter(F.col("R3") != F.col("_engine"))
        .count()
    )
    lines += [
        "R0 -> R3 (all changes):",
        *_table(df, "R0", "R3"),
        f"R3 vs the engine's reachability_state: {mismatches} mismatches",
    ]
    _log("REACH", model_id, lines)
    df.unpersist()
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py`
action: replace · base sha256 `af38bc9e38fec005ef836d670dd2a55d88320031abbfb3d4b39bc1167d7d184c` · base trailing newline: yes · new sha256 `1c4d86c21f83daa41f7f1f71a2d2c919417b5a5c97873640baf2c9d6c6b65a26` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` runs the observation base,
``location_features`` and the same nodes, writes the axis to
``crx_<p>_a2_locatability_b06_check`` and logs the comparison with the old A2
(``b06_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.location.pipeline import (
    create_pipeline as create_location_pipeline,
)

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b06_check import (
    compare_a2_outputs,
    describe_a2_rules,
    describe_debit_evidence,
    split_by_product,
)
from .classify import build_a2_locatability
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)


def create_a2_pipeline(product: str, output: str) -> Pipeline:
    """Signal nodes and the state node of ``product``'s A2 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a2"
    tags = ["crx_persona", "crx", "a2", "locatability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_location_signals,
                inputs={
                    "obs_base": obs,
                    "location_features": "feat_cif_location_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_location_signals",
                name=f"build_{prefix}_location_signals",
                tags=tags,
            ),
            node(
                func=build_dcore_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_dcore_signals",
                name=f"build_{prefix}_dcore_signals",
                tags=tags,
            ),
            node(
                func=build_way4_deceased,
                inputs={
                    "obs_base": obs,
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                },
                outputs=f"{prefix}_way4_deceased",
                name=f"build_{prefix}_way4_deceased",
                tags=tags,
            ),
            node(
                func=build_demographics_deceased,
                inputs={"obs_base": obs, "demographics": "feat_demographics_cif"},
                outputs=f"{prefix}_demographics_deceased",
                name=f"build_{prefix}_demographics_deceased",
                tags=tags,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "obs_base": obs,
                    "location": f"{prefix}_location_signals",
                    "dcore": f"{prefix}_dcore_signals",
                    "way4_deceased": f"{prefix}_way4_deceased",
                    "demographics_deceased": f"{prefix}_demographics_deceased",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_locatability",
                tags=tags,
            ),
        ],
    )


def create_b06_check_pipeline(product: str) -> Pipeline:
    """TEMPORARY: observation base + location inputs + the A2 pipeline writing to
    crx_<p>_a2_locatability_b06_check + the log-only comparison nodes.
    Remove with b06_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    check = f"crx_{product}_a2_locatability_b06_check"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a2_outputs,
            inputs=[f"crx_{product}_a2_locatability", check, "params:model_id"],
            outputs=None,
            name=f"compare_crx_{product}_a2_b06",
            tags=tags,
        ),
        node(
            func=describe_a2_rules,
            inputs=[check, "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_rules",
            tags=tags,
        ),
        node(
            func=describe_debit_evidence,
            inputs=[obs, "prm_casa_card_transactions", "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_debit",
            tags=tags,
        ),
    ]
    if product == "rl":
        checks.append(
            node(
                func=split_by_product,
                inputs=[check, "rl_spine", "params:model_id"],
                outputs=None,
                name="split_crx_rl_a2_b06_product",
                tags=tags,
            )
        )
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_location_pipeline()
        + create_a2_pipeline(product, output=check)
        + Pipeline(checks)
    )
`````

New:

`````python
"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` runs the observation base,
``location_features`` and the same nodes, writes the axis to
``crx_<p>_a2_locatability_b06_check`` and logs the comparison with the old A2
(``b06_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.location.pipeline import (
    create_pipeline as create_location_pipeline,
)

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b06_check import (
    compare_a2_outputs,
    describe_a2_rules,
    describe_debit_evidence,
    explain_reachability,
    split_by_product,
)
from .classify import build_a2_locatability
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)


def create_a2_pipeline(product: str, output: str) -> Pipeline:
    """Signal nodes and the state node of ``product``'s A2 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a2"
    tags = ["crx_persona", "crx", "a2", "locatability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_location_signals,
                inputs={
                    "obs_base": obs,
                    "location_features": "feat_cif_location_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_location_signals",
                name=f"build_{prefix}_location_signals",
                tags=tags,
            ),
            node(
                func=build_dcore_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_dcore_signals",
                name=f"build_{prefix}_dcore_signals",
                tags=tags,
            ),
            node(
                func=build_way4_deceased,
                inputs={
                    "obs_base": obs,
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                },
                outputs=f"{prefix}_way4_deceased",
                name=f"build_{prefix}_way4_deceased",
                tags=tags,
            ),
            node(
                func=build_demographics_deceased,
                inputs={"obs_base": obs, "demographics": "feat_demographics_cif"},
                outputs=f"{prefix}_demographics_deceased",
                name=f"build_{prefix}_demographics_deceased",
                tags=tags,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "obs_base": obs,
                    "location": f"{prefix}_location_signals",
                    "dcore": f"{prefix}_dcore_signals",
                    "way4_deceased": f"{prefix}_way4_deceased",
                    "demographics_deceased": f"{prefix}_demographics_deceased",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_locatability",
                tags=tags,
            ),
        ],
    )


def create_b06_check_pipeline(product: str) -> Pipeline:
    """TEMPORARY: observation base + location inputs + the A2 pipeline writing to
    crx_<p>_a2_locatability_b06_check + the log-only comparison nodes.
    Remove with b06_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    check = f"crx_{product}_a2_locatability_b06_check"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a2_outputs,
            inputs=[f"crx_{product}_a2_locatability", check, "params:model_id"],
            outputs=None,
            name=f"compare_crx_{product}_a2_b06",
            tags=tags,
        ),
        node(
            func=describe_a2_rules,
            inputs=[check, "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_rules",
            tags=tags,
        ),
        node(
            func=explain_reachability,
            inputs=[
                obs,
                "dcore_prm_followup_outcomes",
                "prm_dcore_account_agreements",
                check,
                "params:model_id",
            ],
            outputs=None,
            name=f"explain_crx_{product}_a2_b06_reach",
            tags=tags,
        ),
        node(
            func=describe_debit_evidence,
            inputs=[obs, "prm_casa_card_transactions", "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_debit",
            tags=tags,
        ),
    ]
    if product == "rl":
        checks.append(
            node(
                func=split_by_product,
                inputs=[check, "rl_spine", "params:model_id"],
                outputs=None,
                name="split_crx_rl_a2_b06_product",
                tags=tags,
            )
        )
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_location_pipeline()
        + create_a2_pipeline(product, output=check)
        + Pipeline(checks)
    )
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

APPLY_VERSION = 6
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
            else:
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
Clean up after mirror bundle 07_a2_b06_check_fix.md, on the bundle's branch.
Nothing of its own: `b06_check.py` is removed by bundle 06's cleanup prompt.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
