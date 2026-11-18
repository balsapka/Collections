# Mirror bundle 28 — A3 same-day payments + no Broken, A1 F4 card parent link + point-in-time card CIF, with bundle 25's step 8

apply_bundle version: 7 · built 2026-11-18 from `b4a1a8a..bef9cba` · source: 2 added, 8 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/persona_b28
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/28_rules_a1_a3.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '28_rules_a1_a3.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/28_rules_a1_a3.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

1. **Registry and catalog merge.** `pipeline_registry.py` is `MERGED` (four `crx_<p>_b28_*` lines and one import added next to the workplace's own entries): show its `git diff` and confirm no workplace entry was dropped. List any top-level key the apply removed from `conf/base/catalog/*.yml` or from the registry dict compared with the last commit (expected: none).
2. **Catalog.** In a `kedro ipython` session, `type(catalog._get_dataset("crx_cc_b28_old_states")).__name__` and the same for `crx_rl_b28_old_states` must print `SparkDataset`. If not, stop and report.
3. **Raw columns.** If UAT can read the schemas of `raw_stg_contract` and `raw_stg_client` (`catalog.load(...).columns`, no data needed), confirm `record_date_from` and `edp_modifiedts` on the contract table and `edp_effectivestartdate` and `edp_modifiedts` on the client table; report any missing. If UAT cannot read them, say so (PROD then fails loud on a missing column).
4. **Other readers.** `grep -rn "commitments_last_broken_n\|prm_card_contracts" src conf` and report any reader outside the files in the manifest and the catalog.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Bundle 28: A3 same-day payments + no Broken level, A1 F4 card parent link + point-in-time card CIF, temporary b28 check" && git push -u origin feature/persona_b28
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/28_rules_a1_a3.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_b28 && git pull
```

Set `model_id` in `conf/dev/globals_dev.yml` before each run; `cc` pipeline names for cc_60_180 / cc_180_plus, `rl` for rl_60_180 / rl_180_plus.

**Step 6 (before step 7).** Snapshot the persisted A1 / A3 states, **all four model_ids** (seconds each):

```bash
kedro run --env=dev --pipeline=crx_cc_b28_snapshot
```

```bash
kedro run --env=dev --pipeline=crx_rl_b28_snapshot
```

**Step 7.** Write the real tables, **per model_id, in this order** (all four):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

Not needed: `crx_cc_raw_extract`, A4, `crx_cc_a2_locatability`, and bureau for cc_180_plus / rl_60_180 / rl_180_plus (bundle 25's check showed them identical). Only if not run since bundle 25: `bureau_salary_bounces` for cc_60_180 and `crx_rl_a2_locatability` for rl_60_180 / rl_180_plus (before A1).

**Step 8 (after step 7).** Compare, **all four model_ids**:

```bash
kedro run --env=dev --pipeline=crx_cc_b28_compare
```

```bash
kedro run --env=dev --pipeline=crx_rl_b28_compare
```

Paste back, per model_id, the `=== B28 ROWS / B28 A1 / B28 A3 … START ===` … `END ===` blocks, the `a1_ability` and `a3` state distributions step 7 logged, and the run time of step 7's A1 and A3 runs (cc_180_plus above all). The old tables predate bundle 25's rules too, so the crosstabs show bundles 25 and 28 together. Then the cleanup prompt, then the A3 results prompt run 2 (`workplace_mirror/bundle_helpers/a3_final/sonnet_a3_results_prompt.md` in the mirror).

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The A3 and A1 changes decided after bundle 25's check, with bundle 25's step 8 folded into this bundle's step 7 (one A1 / A3 run). **Apply on top of bundles 25, 26, 27 and bundle 27's cleanup.** Before step 1, stand on a branch that has all of them: if bundle 26 (`feature/uc1_stated`) is not yet merged into bundle 25 / 27's branch (`feature/council_a1_a3_refactor`), merge it first; step 1 then branches from there.

- **A3: a payment on the promise day counts toward the promise** (D-A3-29 amended, user 2026-11-18). `promise_paid_amount` sums the payments from the event day on; event chaining uses the payments before the start day. Loans are unaffected (RL cash is month-end dated). Run 1 of the results: cards keep 777 (60–180) and 1,329 (180+) more events.
- **A3: no Broken level** (D-A3-34, user 2026-11-18). Dimension A = Kept 3 / Partly kept 2 / Promised 1 / No promise 0; the 40% rate, the streak of 3 and the column `commitments_last_broken_n` go (from `crx_<p>_a3_commitment_signals` and `crx_<p>_a3_payment_credibility`).
- **A1 F4: every card contract kept** (Q-S6-14: a Way4 parent stays live beside its child). `feat_cif_cross_product_monthly` gains `linked_account_id`; the A1 engine leaves out the scored account and the cards linked to it either way.
- **Card CIF point in time** (user 2026-11-18). `prm_card_contracts` becomes one row per contract and CIF span, with `valid_from` / `valid_to` (NULL = open), built from the Way4 change logs (`raw_stg_contract.record_date_from`, `raw_stg_client.edp_effectivestartdate`, `edp_modifiedts` on a tie); F4 card rows take the CIF holding the contract at the month end. 1.6% of card contracts sat under more than one CIF; under 10 scored accounts change.
- **Temporary check** `b28_check.py`: `crx_<p>_b28_snapshot` copies the persisted A1 / A3 states before step 8 (`catalog_tmp_b28_check.yml`, 2 explicit entries); `crx_<p>_b28_compare` logs old x new after it. 4 registry lines.

Local checks: A3 spec, A1 spec (96 cases), card CIF spec, golden harness 188 datasets (only changes: the A3 tables lose `commitments_last_broken_n`, `prm_card_contracts` gains the two span columns).

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
| add | `conf/base/catalog/catalog_tmp_b28_check.yml` |
| replace | `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` |
| replace | `src/enbd_collections/nodes/primary/products/prm_products.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/promises.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py` |
| add | `src/enbd_collections/pipelines/crx_persona/b28_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_tmp_b28_check.yml`
action: add · new sha256 `495830084537abfc5779d0259b5b45d342f11f5b744edea9a507335ccd19f129` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundle 28): the A1 / A3 states before step 8; removed by the bundle's cleanup.
crx_cc_b28_old_states:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b28_check/crx_cc_b28_old_states"
  save_args:
    mode: overwrite

crx_rl_b28_old_states:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b28_check/crx_rl_b28_old_states"
  save_args:
    mode: overwrite
`````

### FILE: `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py`
action: replace · base sha256 `2260aec4aeedf4fba767af62e0aa2eb8b4aaf049560e6de3cd534acec5e79887` · base trailing newline: yes · new sha256 `9aa7059487625e9c589c0675a3342fef1965148a7c1f8d6b71d801226113bf1b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets
  under management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1
engine can leave out the scored account itself. The WM asset sources are per customer,
not per account: their rows carry the fixed ids ``ASSET_IDS`` (never a spine account).
Supplementary cards post to their contract and never appear as a product of their own; a
card that a newer card replaced is left out, so the scored card's predecessor is not
"another card". CASA balances are never a product here (they are A1's money held,
``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    history_floor,
    require_columns,
    wm_month,
)

COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
ASSET_TYPES = tuple(ASSET_IDS)
CREDIT_TYPES = ("card", "loan")
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the
    month's last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series;
    a balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: a live contract (not replaced by a newer one) with a billing row
    in the month; current = billing level at most ``CARD_CURRENT_MAX_LEVEL``; the
    instalment is the month's minimum due."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    replaced = card_contracts.select(
        F.col("parent_contract_id").alias("contract_id")
    ).distinct()
    live = card_contracts.join(replaced, "contract_id", "left_anti")
    return card_month_end.join(
        live.select("cif_id", "contract_id"), "contract_id"
    ).select(
        "cif_id",
        "month_end",
        F.col("contract_id").cast("string").alias("product_account_id"),
        F.lit("card").alias("product_type"),
        _null("double").alias("balance_aed"),
        (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
        F.col("minimum_due").alias("instalment_aed"),
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days
    and not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from ``history_floor(persona_start_date, history_months)`` on, for
    all customers (the A1 engine's join on the observation base applies the persona
    scope). The primaries are already bounded to that floor by ``product_primary`` (same
    parameters).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = history_floor(persona_start_date, history_months)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

New:

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets
  under management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets);
* ``linked_account_id`` - cards: the contract Way4 links this one to
  (``parent_contract_idt``; NULL for every other row).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1
engine can leave out the scored account itself. The WM asset sources are per customer,
not per account: their rows carry the fixed ids ``ASSET_IDS`` (never a spine account).
Supplementary cards post to their contract and never appear as a product of their own.
A card counts for the CIF that held its contract at the month end (point in time,
``prm_card_contracts``). Every card contract is kept: a Way4 parent stays live beside its
child (Q-S6-14), so the link is carried for the A1 engine to leave out the cards linked
to the scored account. CASA balances are never a product here (they are A1's money
held, ``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    history_floor,
    require_columns,
    wm_month,
)

COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
    "linked_account_id",
)
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
ASSET_TYPES = tuple(ASSET_IDS)
CREDIT_TYPES = ("card", "loan")
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the
    month's last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series;
    a balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
        _null("string").alias("linked_account_id"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: every contract with a billing row in the month, under the CIF
    that held it at the month end; current = billing level at most
    ``CARD_CURRENT_MAX_LEVEL``; the instalment is the month's minimum due;
    ``linked_account_id`` = its parent contract."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id", "valid_from", "valid_to"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    month_end, start, end = F.col("month_end"), F.col("valid_from"), F.col("valid_to")
    held = (start.isNull() | (start <= month_end)) & (end.isNull() | (month_end < end))
    return (
        card_month_end.join(card_contracts, "contract_id")
        .filter(held)
        .select(
            "cif_id",
            "month_end",
            F.col("contract_id").cast("string").alias("product_account_id"),
            F.lit("card").alias("product_type"),
            _null("double").alias("balance_aed"),
            (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
            F.col("minimum_due").alias("instalment_aed"),
            F.col("parent_contract_id").cast("string").alias("linked_account_id"),
        )
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days
    and not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
        _null("string").alias("linked_account_id"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from ``history_floor(persona_start_date, history_months)`` on, for
    all customers (the A1 engine's join on the observation base applies the persona
    scope). The primaries are already bounded to that floor by ``product_primary`` (same
    parameters).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = history_floor(persona_start_date, history_months)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

### FILE: `src/enbd_collections/nodes/primary/products/prm_products.py`
action: replace · base sha256 `420ce6096fa7ae422a8efbeded8f8857fb381d488249b480b940f4e720145cd8` · base trailing newline: yes · new sha256 `cb2e8abec1ecd00581a4ea0aa9b09926ac67c6a2a9278ea8c5450ad5fdd2a82a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per ``(cif_id, contract_id)``: every Way4 card
  contract of a client, with ``parent_contract_id`` (the contract a newer one replaced;
  NULL for none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row
  in the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 =
  not overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off
  date.

All customers, from ``history_floor(persona_start_date, history_months)`` on; values as
in the source (which level or bucket is "current" is decided by the consumers). The
spine-scoped ``prm_contract`` / ``prm_balance`` hold only the model's own accounts, so
they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import (
    history_floor,
    require_columns,
    string_key,
)

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _load_bound(floor: datetime.date) -> datetime.date:
    """The ``edp_load_date`` bound that covers the month of ``floor`` (load lag)."""
    return floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str, value: str) -> DataFrame:
    """``key``, ``month_end`` (the month end of ``day``) and ``value`` of each ``key``'s
    latest ``day`` row per month; two rows on that day: the larger ``value``."""
    return (
        df.groupBy(key, F.last_day(day).alias("month_end"))
        .agg(F.max(F.struct(day, value)).alias("_latest"))
        .select(key, "month_end", F.col(f"_latest.{value}").alias(value))
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id`` of every card contract whose
    client is known (``ident_number`` is the CIF)."""
    require_columns(client, ["client_idt", "ident_number"], "raw_stg_client")
    require_columns(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", string_key(client, "ident_number").alias("cif_id")
    ).distinct()
    return (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_contract_id"),
        )
        .distinct()
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date", "level")


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot
    in the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the
    repo's own minimum-due derivation)."""
    require_columns(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return (
        _latest_in_month(amounts, "contract_idt", "banking_date", "minimum_due")
        .withColumnRenamed("contract_idt", "contract_id")
        .withColumn("minimum_due", F.col("minimum_due").cast("double"))
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card
    contract with a billing row in the month."""
    floor = history_floor(persona_start_date, history_months)
    lo = _load_bound(floor)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``,
    ``overdue_days``, ``instalment_due_aed`` and ``write_off_date`` of every monthly
    loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor = history_floor(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        string_key(loan_portfolio, "cust_num").alias("cif_id"),
        string_key(loan_portfolio, "acct_num").alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
`````

New:

`````python
"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per card contract and span ``[valid_from,
  valid_to)`` over which its client and that client's CIF held (point in time: a
  contract that moved client, or whose client's CIF changed, has one row per owner;
  NULL ``valid_from`` = from the first record, NULL ``valid_to`` = still current), with
  ``parent_contract_id`` (Way4's linked contract, which stays live beside it; NULL for
  none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row
  in the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 =
  not overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off
  date.

All customers, from ``history_floor(persona_start_date, history_months)`` on; values as
in the source (which level or bucket is "current" is decided by the consumers). The
spine-scoped ``prm_contract`` / ``prm_balance`` hold only the model's own accounts, so
they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from functools import reduce

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import (
    history_floor,
    require_columns,
    string_key,
)

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _load_bound(floor: datetime.date) -> datetime.date:
    """The ``edp_load_date`` bound that covers the month of ``floor`` (load lag)."""
    return floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str, value: str) -> DataFrame:
    """``key``, ``month_end`` (the month end of ``day``) and ``value`` of each ``key``'s
    latest ``day`` row per month; two rows on that day: the larger ``value``."""
    return (
        df.groupBy(key, F.last_day(day).alias("month_end"))
        .agg(F.max(F.struct(day, value)).alias("_latest"))
        .select(key, "month_end", F.col(f"_latest.{value}").alias(value))
    )


def _versions(df: DataFrame, key: str, start: str, values: list[str]) -> DataFrame:
    """``key``, ``values``, ``valid_from``, ``valid_to``: one row per change of
    ``values`` in a Way4 change log, ordered by ``start`` (the version's valid-from day;
    on one day the latest ``edp_modifiedts`` wins). The first version is open at the start
    (``valid_from`` NULL), the last at the end (``valid_to`` NULL)."""
    latest = (
        df.groupBy(key, F.col(start).cast(DateType()).alias("_from"))
        .agg(F.max(F.struct("edp_modifiedts", *values)).alias("_v"))
        .select(key, "_from", *(F.col(f"_v.{c}").alias(c) for c in values))
    )
    order = Window.partitionBy(key).orderBy("_from")
    first = F.row_number().over(order) == 1
    same = reduce(
        lambda x, y: x & y, (F.lag(c).over(order).eqNullSafe(F.col(c)) for c in values)
    )
    return (
        latest.withColumn("_change", first | ~same)
        .filter("_change")
        .select(
            key,
            *values,
            F.when(~first, F.col("_from")).alias("valid_from"),
            F.lead("_from").over(order).alias("valid_to"),
        )
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id``, ``valid_from``, ``valid_to``
    of every card contract whose client is known (``ident_number`` is the CIF), point
    in time: the contract's client from the contract log (``record_date_from``), that
    client's CIF from the client log (``edp_effectivestartdate``); each row is a span
    where both held."""
    require_columns(
        client,
        ["client_idt", "ident_number", "edp_effectivestartdate", "edp_modifiedts"],
        "raw_stg_client",
    )
    require_columns(
        contract,
        [
            "contract_idt",
            "client_idt",
            "parent_contract_idt",
            "record_date_from",
            "edp_modifiedts",
        ],
        "raw_stg_contract",
    )
    owner = _versions(
        contract,
        "contract_idt",
        "record_date_from",
        ["client_idt", "parent_contract_idt"],
    ).alias("o")
    cif = _versions(
        client.withColumn("cif_id", string_key(client, "ident_number")),
        "client_idt",
        "edp_effectivestartdate",
        ["cif_id"],
    ).alias("c")
    start, end = F.lit(datetime.date.min), F.lit(datetime.date.max)
    overlaps = (F.coalesce("o.valid_from", start) < F.coalesce("c.valid_to", end)) & (
        F.coalesce("c.valid_from", start) < F.coalesce("o.valid_to", end)
    )
    return owner.join(
        cif, (F.col("o.client_idt") == F.col("c.client_idt")) & overlaps
    ).select(
        "c.cif_id",
        F.col("o.contract_idt").cast("long").alias("contract_id"),
        F.col("o.parent_contract_idt").cast("long").alias("parent_contract_id"),
        F.greatest("o.valid_from", "c.valid_from").alias("valid_from"),
        F.least("o.valid_to", "c.valid_to").alias("valid_to"),
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date", "level")


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot
    in the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the
    repo's own minimum-due derivation)."""
    require_columns(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return (
        _latest_in_month(amounts, "contract_idt", "banking_date", "minimum_due")
        .withColumnRenamed("contract_idt", "contract_id")
        .withColumn("minimum_due", F.col("minimum_due").cast("double"))
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card
    contract with a billing row in the month."""
    floor = history_floor(persona_start_date, history_months)
    lo = _load_bound(floor)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``,
    ``overdue_days``, ``instalment_due_aed`` and ``write_off_date`` of every monthly
    loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor = history_floor(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        string_key(loan_portfolio, "cust_num").alias("cif_id"),
        string_key(loan_portfolio, "acct_num").alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `7043b331aeda16ea19f75be354a9ae9af5651ab28aa246d9f96c808b9fc4187d` · base trailing newline: yes · new sha256 `ef0926359c3867f6fddf6f77ef057ea5309d119110a60e378b1442f740361138` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import cc_spell as crx_cc_spell
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
    rl_spell_table as crx_rl_spell_table,
)
from enbd_collections.pipelines.crx_persona import rl_a4_spine as crx_rl_a4_spine
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_spell_table": crx_cc_spell.create_pipeline(),
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

New:

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import cc_spell as crx_cc_spell
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base
from enbd_collections.pipelines.crx_persona import b28_check  # TEMPORARY

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
    rl_spell_table as crx_rl_spell_table,
)
from enbd_collections.pipelines.crx_persona import rl_a4_spine as crx_rl_a4_spine
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_spell_table": crx_cc_spell.create_pipeline(),
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 28): removed by the cleanup
        "crx_cc_b28_snapshot": b28_check.create_snapshot_pipeline("cc"),
        "crx_rl_b28_snapshot": b28_check.create_snapshot_pipeline("rl"),
        "crx_cc_b28_compare": b28_check.create_compare_pipeline("cc"),
        "crx_rl_b28_compare": b28_check.create_compare_pipeline("rl"),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `8fdd80a7dd1fb5e52d1de5539661c421880bc189bf7c514138af629c8237e0e1` · base trailing newline: yes · new sha256 `3640ab7dc3cee6a07038fc0430c3eb587462039f37ff1aeaf087d42ad01d1e2b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a bureau row counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month,
             whether any counted leg falls in the window (the Unknown gate) and whether
             the customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    ASSET_TYPES,
    CREDIT_TYPES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)
from enbd_collections.nodes.utils.frames import cif_column, history_floor

from .._common import (
    GRAIN,
    left_join_all,
    require_columns,
    scoped,
    string_key,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"
# S14: a bureau salary also counts in the next N months that have no row of their own.
BUREAU_CARRY_MONTHS = 1


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", string_key(obs_base, "cif_id")
    )


def persona_floor(crx_persona: dict, months: int) -> str:
    """ISO first day of the earliest observation's ``months``-month window: the obs base
    starts in the persona start month, so no window reaches older source rows."""
    return history_floor(crx_persona["persona_start_date"], months).isoformat()


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months``
    months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _with_carry(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: the month's own row, else the
    newest row of the ``BUREAU_CARRY_MONTHS`` months before it (never before a row;
    pulls every 2 months make a continuous series). A row of 0 ends the carry.
    """
    ages = range(BUREAU_CARRY_MONTHS + 1)  # 0: the row's own month
    rows = reduce(
        DataFrame.unionByName,
        [
            bureau.select(
                "cif_id",
                F.last_day(F.add_months("month_end", age)).alias("month_end"),
                F.lit(age).alias("_age"),
                "bureau_salary",
            )
            for age in ages
        ],
    )
    newest = [F.max(F.when(F.col("_age") == a, F.col("bureau_salary"))) for a in ages]
    # the newest non-NULL amount wins: a 0 row is a value, so it hides the older rows
    return rows.groupBy("cif_id", "month_end").agg(
        F.coalesce(*newest).alias("bureau_salary")
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried ``BUREAU_CARRY_MONTHS`` months
    forward); NULL: no salary that month. Also the largest month per source:
    ``internal_salary_w`` / ``bureau_salary_w`` in the window, ``internal_salary_prior``
    in the prior window.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    sources = internal.unionByName(
        _with_carry(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` /
    ``money_out`` (AED of the counted classes; NULL on a balance row), ``balance`` (NULL
    on a flow row), ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a
    positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money
    in), ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active``
    (a counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code
    accounts of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= F.lit(persona_floor(crx_persona, CASA_HELD_MONTHS))
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account itself left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin(*ASSET_TYPES)
    current_credit = F.col("product_type").isin(*CREDIT_TYPES) & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    mine = scoped(
        products.select(
            cif_column(),
            F.col("month_end").alias("observation_date"),
            string_key(products, "product_account_id").alias("_acct"),
            "product_type",
            F.col("balance_aed").cast("double").alias("_bal"),
            "is_current",
            F.col("instalment_aed").cast("double").alias("_inst"),
        ),
        obs,
        "cif_id",
    )
    joined = obs.join(mine, on=["cif_id", "observation_date"])
    rows = (
        joined.filter(F.col("_acct") != string_key(joined))
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after "
            "changing crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                cif_column(),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, w)
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    mine = scoped(
        agreements.select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            cif_column(),
        ).distinct(),
        obs,
        "cif_id",
    )
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(F.broadcast(mine), on="agreement_id")
        .filter(F.col("day") >= F.lit(persona_floor(crx_persona, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a bureau row counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month,
             whether any counted leg falls in the window (the Unknown gate) and whether
             the customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from functools import reduce

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    ASSET_TYPES,
    CREDIT_TYPES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)
from enbd_collections.nodes.utils.frames import cif_column, history_floor

from .._common import (
    GRAIN,
    left_join_all,
    require_columns,
    scoped,
    string_key,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"
# S14: a bureau salary also counts in the next N months that have no row of their own.
BUREAU_CARRY_MONTHS = 1


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", string_key(obs_base, "cif_id")
    )


def persona_floor(crx_persona: dict, months: int) -> str:
    """ISO first day of the earliest observation's ``months``-month window: the obs base
    starts in the persona start month, so no window reaches older source rows."""
    return history_floor(crx_persona["persona_start_date"], months).isoformat()


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months``
    months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _with_carry(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: the month's own row, else the
    newest row of the ``BUREAU_CARRY_MONTHS`` months before it (never before a row;
    pulls every 2 months make a continuous series). A row of 0 ends the carry.
    """
    ages = range(BUREAU_CARRY_MONTHS + 1)  # 0: the row's own month
    rows = reduce(
        DataFrame.unionByName,
        [
            bureau.select(
                "cif_id",
                F.last_day(F.add_months("month_end", age)).alias("month_end"),
                F.lit(age).alias("_age"),
                "bureau_salary",
            )
            for age in ages
        ],
    )
    newest = [F.max(F.when(F.col("_age") == a, F.col("bureau_salary"))) for a in ages]
    # the newest non-NULL amount wins: a 0 row is a value, so it hides the older rows
    return rows.groupBy("cif_id", "month_end").agg(
        F.coalesce(*newest).alias("bureau_salary")
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried ``BUREAU_CARRY_MONTHS`` months
    forward); NULL: no salary that month. Also the largest month per source:
    ``internal_salary_w`` / ``bureau_salary_w`` in the window, ``internal_salary_prior``
    in the prior window.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    sources = internal.unionByName(
        _with_carry(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` /
    ``money_out`` (AED of the counted classes; NULL on a balance row), ``balance`` (NULL
    on a flow row), ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a
    positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money
    in), ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active``
    (a counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code
    accounts of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= F.lit(persona_floor(crx_persona, CASA_HELD_MONTHS))
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account and the cards Way4 links
    to it (``linked_account_id``, either way) left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin(*ASSET_TYPES)
    current_credit = F.col("product_type").isin(*CREDIT_TYPES) & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    mine = scoped(
        products.select(
            cif_column(),
            F.col("month_end").alias("observation_date"),
            string_key(products, "product_account_id").alias("_acct"),
            "product_type",
            F.col("balance_aed").cast("double").alias("_bal"),
            "is_current",
            F.col("instalment_aed").cast("double").alias("_inst"),
            string_key(products, "linked_account_id").alias("_link"),
        ),
        obs,
        "cif_id",
    )
    joined = obs.join(mine, on=["cif_id", "observation_date"])
    scored = string_key(joined)
    # the contracts the scored account's own rows link to (its Way4 parents)
    scored_links = F.collect_set(F.when(F.col("_acct") == scored, F.col("_link"))).over(
        Window.partitionBy(*GRAIN)
    )
    linked = F.coalesce(
        (F.col("_link") == scored) | F.array_contains("_scored_links", F.col("_acct")),
        F.lit(False),
    )
    rows = (
        joined.withColumn("_scored_links", scored_links)
        .filter((F.col("_acct") != scored) & ~linked)
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after "
            "changing crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                cif_column(),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = persona_floor(crx_persona, w)
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    mine = scoped(
        agreements.select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            cif_column(),
        ).distinct(),
        obs,
        "cif_id",
    )
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(F.broadcast(mine), on="agreement_id")
        .filter(F.col("day") >= F.lit(persona_floor(crx_persona, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py`
action: replace · base sha256 `6d8861e832a286fba567eefc8776f0197bbd28b13653d4888504b36a17d54bfb` · base trailing newline: yes · new sha256 `8326a5d7b035c497a77d37ac2ac91dc18d0bd2f261e37263c4eda1091c9c19f8` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD, promise_deadline

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_n",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    model_id: str,
    persona_end_date: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27, -33).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off.
    Unknown: no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode
    with no evidence scores 0 points and is Low.
    """
    df = episode
    for part in (commitments, dlq_payments, pre_dlq, contacts):
        df = df.join(part, on=list(GRAIN), how="left")
    df = df.withColumn(
        "a3_promise_deadline", F.lit(promise_deadline(product, model_id, deadline))
    )
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", f"a3_credibility [{model_id}]", persona_end_date)
    return out
`````

New:

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD, promise_deadline

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_n",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    model_id: str,
    persona_end_date: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27, -33).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off.
    Unknown: no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode
    with no evidence scores 0 points and is Low.
    """
    df = episode
    for part in (commitments, dlq_payments, pre_dlq, contacts):
        df = df.join(part, on=list(GRAIN), how="left")
    df = df.withColumn(
        "a3_promise_deadline", F.lit(promise_deadline(product, model_id, deadline))
    )
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", f"a3_credibility [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py`
action: replace · base sha256 `c1516bc2c8039ccb628e2885be0ac97a4701779e86d735ce525376af4a9447d8` · base trailing newline: yes · new sha256 `16ef6a9a9ff281b3ee471a14b024aa49b73e5f3b174b9be5c557c992c726f82b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS, segment
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
# The deadline a promise is judged by, whatever date was promised (D-A3-28): at 60-180 a
# card promise by the next statement after the promise day, however close; a loan
# promise, and every promise at 180+, by the end of the promise month. The options and
# their cutoffs: promises.CUTOFFS.
PROMISE_DEADLINE = {
    SEG_60_180: {"cc": "next_statement", "rl": "month_end"},
    SEG_180_PLUS: {"cc": "month_end", "rl": "month_end"},
}
# next-statement deadline: at most 31 days after the promise (no statement on record by
# then: statements are missing from the history) (D-A3-29)
NEXT_STATEMENT_MAX_DAYS = 31
PROMISE_DAYS = 30  # the "30_days" options: 30 days after the promise


def promise_deadline(product: str, model_id: str, override: str | None = None) -> str:
    """``override`` if given, else the ``PROMISE_DEADLINE`` of ``product`` in
    ``model_id``'s segment."""
    return override or PROMISE_DEADLINE[segment(model_id)][product]


# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
# Dimension A: the smallest promised amount and a partial payment (D-A3-29); the same
# 100 AED today, kept apart so the two can move separately.
PROMISE_MIN_AED = MIN_PAYMENT_AED
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20, -32; Q-29, Q-30) ──────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── Source history ────────────────────────────────────────────────────────────
# Months of payment history read before the earliest window a dimension opens (the
# episode start, or the first observation month): the longest window and one cycle.
HISTORY_MONTHS = (
    max(PRE_DLQ_MONTHS, COMMITMENT_MONTHS, *ANY_PAYMENT_MONTHS.values()) + 1
)

# ── State (D-A3-16, -19, -20, -22, -24, -33) ───────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
# a promise counts even when broken; never promising scores 0 (D-A3-33)
COMMITMENT_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension(
            "commitments", "a3_commitments_level", COMMITMENT_POINTS, ("no_promise",)
        ),
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

New:

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS, segment
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
# The deadline a promise is judged by, whatever date was promised (D-A3-28): at 60-180 a
# card promise by the next statement after the promise day, however close; a loan
# promise, and every promise at 180+, by the end of the promise month. The options and
# their cutoffs: promises.CUTOFFS.
PROMISE_DEADLINE = {
    SEG_60_180: {"cc": "next_statement", "rl": "month_end"},
    SEG_180_PLUS: {"cc": "month_end", "rl": "month_end"},
}
# next-statement deadline: at most 31 days after the promise (no statement on record by
# then: statements are missing from the history) (D-A3-29)
NEXT_STATEMENT_MAX_DAYS = 31
PROMISE_DAYS = 30  # the "30_days" options: 30 days after the promise


def promise_deadline(product: str, model_id: str, override: str | None = None) -> str:
    """``override`` if given, else the ``PROMISE_DEADLINE`` of ``product`` in
    ``model_id``'s segment."""
    return override or PROMISE_DEADLINE[segment(model_id)][product]


# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
# Dimension A: the smallest promised amount and a partial payment (D-A3-29); the same
# 100 AED today, kept apart so the two can move separately.
PROMISE_MIN_AED = MIN_PAYMENT_AED
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20, -32; Q-29, Q-30) ──────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── Source history ────────────────────────────────────────────────────────────
# Months of payment history read before the earliest window a dimension opens (the
# episode start, or the first observation month): the longest window and one cycle.
HISTORY_MONTHS = (
    max(PRE_DLQ_MONTHS, COMMITMENT_MONTHS, *ANY_PAYMENT_MONTHS.values()) + 1
)

# ── State (D-A3-16, -19, -20, -22, -24, -33) ───────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
# a promise counts even when not kept; never promising scores 0 (D-A3-33, -34)
COMMITMENT_POINTS = {"kept": 3, "partly_kept": 2, "promised": 1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension(
            "commitments", "a3_commitments_level", COMMITMENT_POINTS, ("no_promise",)
        ),
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/promises.py`
action: replace · base sha256 `99a56fdb6ec759625bff1d75abdfb53412de3391d488d524e1b4ecc6de3fb32e` · base trailing newline: yes · new sha256 `d5e9a6324dcc3be21c8a7c2ec3ebc2c13ee53dfd2228e8279cca6d8ed2ad17d1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 promise events (D-A3-25, -28, -29): DCORE plans and follow-up promises grouped
into events, each judged by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    NEXT_STATEMENT_MAX_DAYS,
    PROMISE_DAYS,
    PROMISE_MIN_AED,
    promise_deadline,
)
from .sources import DUES, INSTALMENTS, PAYMENTS

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]
# What a promise day decides for an event that starts on it (D-A3-29).
_TERMS = ("promise_cutoff", "promise_amount", "promise_paid_amount")
_DAY_TERMS = ("event_date", *_TERMS)


def _next_statement(day: Column, next_cycle_end: Column) -> Column:
    """The first cycle end after ``day``, at most ``NEXT_STATEMENT_MAX_DAYS`` days after
    it (no statement on record by then: that day)."""
    fallback = F.date_add(day, NEXT_STATEMENT_MAX_DAYS)
    return F.least(F.coalesce(next_cycle_end, fallback), fallback)


# ``promise_cutoff``, the last day a payment still counts, per deadline option
# (D-A3-28), from the promise day and the first cycle end after it.
CUTOFFS = {
    "next_statement": _next_statement,
    "month_end": lambda day, _: F.last_day(day),
    "next_month_end": lambda day, _: F.last_day(F.add_months(day, 1)),
    "30_days": lambda day, _: F.date_add(day, PROMISE_DAYS),
    "30_days_month_end": lambda day, _: F.last_day(F.date_add(day, PROMISE_DAYS)),
}
DEADLINES = tuple(CUTOFFS)


def _promise_rows(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
) -> DataFrame:
    """Every promise of the base's accounts, one row each: a DCORE plan dated at its
    start, a follow-up promise (``_dcore_codes.PROMISE_EVENT``) at its call day."""
    calls = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select(
            "account_id",
            F.col("day").alias("event_date"),
            F.col("name").alias("event_name"),
            F.lit(None).cast("string").alias("plan_id"),
            F.lit("followup").alias("event_source"),
        )
        .distinct()
    )
    plans = instalments.select(
        "account_id",
        F.col("plan_start").alias("event_date"),
        F.lit(None).cast("string").alias("event_name"),
        "plan_id",
        F.col("plan_type").alias("event_source"),
    ).distinct()
    return plans.unionByName(calls)


def _with_terms(days: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``days`` (``account_id``, ``event_date``) + ``promise_cutoff`` (``CUTOFFS``) and
    ``promise_amount``: the latest due on or before the day (cycles without a due amount
    skipped), at least ``PROMISE_MIN_AED`` (D-A3-29). One pass over the account's
    cycles."""
    day = F.col("event_date")
    known_due = F.col("due_amount").isNotNull() & (F.col("cycle_start") <= day)
    cycles = (
        days.join(
            dues.select("account_id", "cycle_start", "cycle_end", "due_amount"),
            on="account_id",
            how="left",
        )
        .groupBy("account_id", "event_date")
        .agg(
            F.min(F.when(F.col("cycle_end") > day, F.col("cycle_end"))).alias("_next"),
            F.max(F.when(known_due, F.struct("cycle_start", "due_amount")))[
                "due_amount"
            ].alias("_due"),
        )
    )
    return cycles.select(
        "account_id",
        "event_date",
        CUTOFFS[deadline](day, F.col("_next")).alias("promise_cutoff"),
        F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(PROMISE_MIN_AED))).alias(
            "promise_amount"
        ),
    )


def _after(day: Column) -> Column:
    """A payment counted as made after ``day``: dated later, or dated that day when its
    period started earlier (RL cash is dated at the month end)."""
    return (F.col("pay_date") > day) | (
        (F.col("pay_date") == day) & (F.col("pay_from") < F.col("pay_date"))
    )


def _with_payments(days: DataFrame, payments: DataFrame) -> DataFrame:
    """``days`` + three sums from one pass over the payments up to the day's
    ``promise_cutoff``: ``_paid_before`` (dated before the day), ``_paid_not_after``
    (not after it, ``_after``) and ``promise_paid_amount`` (after the day; NULL: none).
    Only a payment after the promise can keep it, so an event starting that day counts
    the last and never the money in ``_paid_not_after``."""
    day = F.col("event_date")
    pays = payments.select(
        F.col("account_id").alias("_p_account"),
        "pay_from",
        "pay_date",
        F.col("amount").alias("_amount"),
    )

    def total(counted: Column) -> Column:
        return F.coalesce(F.sum(F.when(counted, F.col("_amount"))), F.lit(0.0))

    return (
        days.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & (F.col("pay_date") <= F.col("promise_cutoff")),
            "left",
        )
        .groupBy(*days.columns)
        .agg(
            total(F.col("pay_date") < day).alias("_paid_before"),
            total(~_after(day)).alias("_paid_not_after"),
            F.sum(F.when(_after(day), F.col("_amount"))).alias("promise_paid_amount"),
        )
    )


def _event_step(live: Column, day: Column) -> Column:
    """Fold one promise day into ``live``, the event alive so far (D-A3-29). The day
    joins it while its deadline has not passed and the payments since the event day,
    before this day, have not reached its promised amount; otherwise the day starts a
    new event. ``starts``: the event start of every day so far."""
    # to the cent: a difference of two sums can fall a hair short of an exact payment
    paid_since_start = F.round(day["_paid_before"] - live["paid_at_start"], 2)
    joins = (
        live["start"].isNotNull()
        & (day["event_date"] <= live["cutoff"])
        & (paid_since_start < live["amount"])
    )

    def keep(old: str, new: str) -> Column:
        return F.when(joins, live[old]).otherwise(day[new]).alias(old)

    start = keep("start", "event_date")
    return F.struct(
        F.concat(live["starts"], F.array(start)).alias("starts"),
        start,
        keep("cutoff", "promise_cutoff"),
        keep("amount", "promise_amount"),
        keep("paid_at_start", "_paid_not_after"),
    )


def _no_event() -> Column:
    """The empty ``_event_step`` accumulator."""
    return F.struct(
        F.array().cast("array<date>").alias("starts"),
        F.lit(None).cast("date").alias("start"),
        F.lit(None).cast("date").alias("cutoff"),
        F.lit(None).cast("double").alias("amount"),
        F.lit(None).cast("double").alias("paid_at_start"),
    )


def _with_event_start(days: DataFrame) -> DataFrame:
    """``account_id``, ``_DAY_TERMS`` and ``event_start``, the event each promise day
    belongs to (``_event_step`` over the account's days in date order)."""
    ordered = F.array_sort(
        F.collect_list(F.struct(*_DAY_TERMS, "_paid_before", "_paid_not_after"))
    )
    return (
        days.groupBy("account_id")
        .agg(ordered.alias("_days"))
        .withColumn("_starts", F.aggregate("_days", _no_event(), _event_step)["starts"])
        .select("account_id", F.explode(F.arrays_zip("_days", "_starts")).alias("_d"))
        .select(
            "account_id",
            *[F.col(f"_d._days.{c}").alias(c) for c in _DAY_TERMS],
            F.col("_d._starts").alias("event_start"),
        )
    )


def _events(promises: DataFrame, days: DataFrame) -> DataFrame:
    """One event per ``event_start``: its first plan (``plan_id``, ``event_source``) and
    first follow-up promise (``event_name``); ``event_kind`` matched (both), table_only
    or followup_only; the start day's cutoff, promised amount and paid amount."""
    is_plan = F.col("plan_id").isNotNull()
    plan = F.min(F.when(is_plan, F.struct("event_date", "plan_id", "event_source")))
    call = F.min(F.when(~is_plan, F.struct("event_date", "event_name")))
    start_day = F.max(
        F.when(F.col("event_date") == F.col("event_start"), F.struct(*_TERMS))
    )
    return (
        promises.join(days, on=["account_id", "event_date"])
        .groupBy("account_id", "event_start")
        .agg(plan.alias("_plan"), call.alias("_call"), start_day.alias("_start"))
        .select(
            "account_id",
            F.col("event_start").alias("event_date"),
            F.when(F.col("_plan").isNull(), "followup_only")
            .when(F.col("_call").isNull(), "table_only")
            .otherwise("matched")
            .alias("event_kind"),
            F.coalesce("_plan.event_source", F.lit("followup")).alias("event_source"),
            F.col("_call.event_name").alias("event_name"),
            F.col("_plan.plan_id").alias("plan_id"),
            "_start.*",
        )
    )


def _judged(events: DataFrame) -> DataFrame:
    """``EVENTS``: ``promise_outcome`` paid when the payments reach the promised amount
    (to the cent, as in ``_event_step``), partial from ``PROMISE_MIN_AED``, else none.
    ``promise_paid_amount`` runs to the event's deadline, so after an event that ended
    early it overlaps the next event's: never sum it across events."""
    paid = F.round(F.coalesce("promise_paid_amount", F.lit(0.0)), 2)
    outcome = (
        F.when(paid >= F.col("promise_amount"), "paid")
        .when(paid >= PROMISE_MIN_AED, "partial")
        .otherwise("none")
    )
    return (
        events.withColumn("promise_paid_amount", paid)
        .withColumn("promise_outcome", outcome)
        .select(*EVENTS)
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    model_id: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment. ``EVENTS``.

    A promise is a non-cancelled PTP or settlement plan (dated at its start) or a
    follow-up promise. An event starts with the first promise and stays alive until its
    deadline passes or the payments since its day reach the promised amount; every
    promise meanwhile belongs to it, the first one after it starts a new event
    (D-A3-29). ``event_kind``: matched (plans and follow-up promises), table_only,
    followup_only.

    The event day sets the terms: ``promise_cutoff`` by ``deadline`` (default
    ``promise_deadline(product, model_id)``, D-A3-28) and ``promise_amount``, the latest
    due on or before that day (at least ``PROMISE_MIN_AED``). Judged once on the
    payments after the event day up to the cutoff: paid when they reach the amount,
    partial from ``PROMISE_MIN_AED``, else none. RL cash is dated at the month end, so
    the event month's cash counts in full and never ends an event mid-month.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    if deadline not in CUTOFFS:
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    promises = _promise_rows(obs_base, followup, agreements, instalments)
    days = promises.select("account_id", "event_date").distinct()
    days = _with_payments(_with_terms(days, dues, deadline), payments)
    return _judged(_events(promises, _with_event_start(days)))
`````

New:

`````python
"""A3 promise events (D-A3-25, -28, -29): DCORE plans and follow-up promises grouped
into events, each judged by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    NEXT_STATEMENT_MAX_DAYS,
    PROMISE_DAYS,
    PROMISE_MIN_AED,
    promise_deadline,
)
from .sources import DUES, INSTALMENTS, PAYMENTS

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]
# What a promise day decides for an event that starts on it (D-A3-29).
_TERMS = ("promise_cutoff", "promise_amount", "promise_paid_amount")
_DAY_TERMS = ("event_date", *_TERMS)


def _next_statement(day: Column, next_cycle_end: Column) -> Column:
    """The first cycle end after ``day``, at most ``NEXT_STATEMENT_MAX_DAYS`` days after
    it (no statement on record by then: that day)."""
    fallback = F.date_add(day, NEXT_STATEMENT_MAX_DAYS)
    return F.least(F.coalesce(next_cycle_end, fallback), fallback)


# ``promise_cutoff``, the last day a payment still counts, per deadline option
# (D-A3-28), from the promise day and the first cycle end after it.
CUTOFFS = {
    "next_statement": _next_statement,
    "month_end": lambda day, _: F.last_day(day),
    "next_month_end": lambda day, _: F.last_day(F.add_months(day, 1)),
    "30_days": lambda day, _: F.date_add(day, PROMISE_DAYS),
    "30_days_month_end": lambda day, _: F.last_day(F.date_add(day, PROMISE_DAYS)),
}
DEADLINES = tuple(CUTOFFS)


def _promise_rows(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
) -> DataFrame:
    """Every promise of the base's accounts, one row each: a DCORE plan dated at its
    start, a follow-up promise (``_dcore_codes.PROMISE_EVENT``) at its call day."""
    calls = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select(
            "account_id",
            F.col("day").alias("event_date"),
            F.col("name").alias("event_name"),
            F.lit(None).cast("string").alias("plan_id"),
            F.lit("followup").alias("event_source"),
        )
        .distinct()
    )
    plans = instalments.select(
        "account_id",
        F.col("plan_start").alias("event_date"),
        F.lit(None).cast("string").alias("event_name"),
        "plan_id",
        F.col("plan_type").alias("event_source"),
    ).distinct()
    return plans.unionByName(calls)


def _with_terms(days: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``days`` (``account_id``, ``event_date``) + ``promise_cutoff`` (``CUTOFFS``) and
    ``promise_amount``: the latest due on or before the day (cycles without a due amount
    skipped), at least ``PROMISE_MIN_AED`` (D-A3-29). One pass over the account's
    cycles."""
    day = F.col("event_date")
    known_due = F.col("due_amount").isNotNull() & (F.col("cycle_start") <= day)
    cycles = (
        days.join(
            dues.select("account_id", "cycle_start", "cycle_end", "due_amount"),
            on="account_id",
            how="left",
        )
        .groupBy("account_id", "event_date")
        .agg(
            F.min(F.when(F.col("cycle_end") > day, F.col("cycle_end"))).alias("_next"),
            F.max(F.when(known_due, F.struct("cycle_start", "due_amount")))[
                "due_amount"
            ].alias("_due"),
        )
    )
    return cycles.select(
        "account_id",
        "event_date",
        CUTOFFS[deadline](day, F.col("_next")).alias("promise_cutoff"),
        F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(PROMISE_MIN_AED))).alias(
            "promise_amount"
        ),
    )


def _with_payments(days: DataFrame, payments: DataFrame) -> DataFrame:
    """``days`` + two sums from one pass over the payments up to the day's
    ``promise_cutoff``: ``_paid_before`` (dated before the day) and
    ``promise_paid_amount`` (dated on or after it; NULL: none). A payment on the
    promise day counts toward the promise: it most likely came out of that call (RL
    cash is dated at the month end, so the promise month's cash counts in full)."""
    day = F.col("event_date")
    pays = payments.select(
        F.col("account_id").alias("_p_account"),
        "pay_date",
        F.col("amount").alias("_amount"),
    )
    before = F.col("pay_date") < day
    return (
        days.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & (F.col("pay_date") <= F.col("promise_cutoff")),
            "left",
        )
        .groupBy(*days.columns)
        .agg(
            F.coalesce(F.sum(F.when(before, F.col("_amount"))), F.lit(0.0)).alias(
                "_paid_before"
            ),
            F.sum(F.when(~before, F.col("_amount"))).alias("promise_paid_amount"),
        )
    )


def _event_step(live: Column, day: Column) -> Column:
    """Fold one promise day into ``live``, the event alive so far (D-A3-29). The day
    joins it while its deadline has not passed and the payments from the event day on,
    before this day, have not reached its promised amount; otherwise the day starts a
    new event. ``starts``: the event start of every day so far."""
    # to the cent: a difference of two sums can fall a hair short of an exact payment
    paid_since_start = F.round(day["_paid_before"] - live["paid_at_start"], 2)
    joins = (
        live["start"].isNotNull()
        & (day["event_date"] <= live["cutoff"])
        & (paid_since_start < live["amount"])
    )

    def keep(old: str, new: str) -> Column:
        return F.when(joins, live[old]).otherwise(day[new]).alias(old)

    start = keep("start", "event_date")
    return F.struct(
        F.concat(live["starts"], F.array(start)).alias("starts"),
        start,
        keep("cutoff", "promise_cutoff"),
        keep("amount", "promise_amount"),
        keep("paid_at_start", "_paid_before"),
    )


def _no_event() -> Column:
    """The empty ``_event_step`` accumulator."""
    return F.struct(
        F.array().cast("array<date>").alias("starts"),
        F.lit(None).cast("date").alias("start"),
        F.lit(None).cast("date").alias("cutoff"),
        F.lit(None).cast("double").alias("amount"),
        F.lit(None).cast("double").alias("paid_at_start"),
    )


def _with_event_start(days: DataFrame) -> DataFrame:
    """``account_id``, ``_DAY_TERMS`` and ``event_start``, the event each promise day
    belongs to (``_event_step`` over the account's days in date order)."""
    ordered = F.array_sort(F.collect_list(F.struct(*_DAY_TERMS, "_paid_before")))
    return (
        days.groupBy("account_id")
        .agg(ordered.alias("_days"))
        .withColumn("_starts", F.aggregate("_days", _no_event(), _event_step)["starts"])
        .select("account_id", F.explode(F.arrays_zip("_days", "_starts")).alias("_d"))
        .select(
            "account_id",
            *[F.col(f"_d._days.{c}").alias(c) for c in _DAY_TERMS],
            F.col("_d._starts").alias("event_start"),
        )
    )


def _events(promises: DataFrame, days: DataFrame) -> DataFrame:
    """One event per ``event_start``: its first plan (``plan_id``, ``event_source``) and
    first follow-up promise (``event_name``); ``event_kind`` matched (both), table_only
    or followup_only; the start day's cutoff, promised amount and paid amount."""
    is_plan = F.col("plan_id").isNotNull()
    plan = F.min(F.when(is_plan, F.struct("event_date", "plan_id", "event_source")))
    call = F.min(F.when(~is_plan, F.struct("event_date", "event_name")))
    start_day = F.max(
        F.when(F.col("event_date") == F.col("event_start"), F.struct(*_TERMS))
    )
    return (
        promises.join(days, on=["account_id", "event_date"])
        .groupBy("account_id", "event_start")
        .agg(plan.alias("_plan"), call.alias("_call"), start_day.alias("_start"))
        .select(
            "account_id",
            F.col("event_start").alias("event_date"),
            F.when(F.col("_plan").isNull(), "followup_only")
            .when(F.col("_call").isNull(), "table_only")
            .otherwise("matched")
            .alias("event_kind"),
            F.coalesce("_plan.event_source", F.lit("followup")).alias("event_source"),
            F.col("_call.event_name").alias("event_name"),
            F.col("_plan.plan_id").alias("plan_id"),
            "_start.*",
        )
    )


def _judged(events: DataFrame) -> DataFrame:
    """``EVENTS``: ``promise_outcome`` paid when the payments reach the promised amount
    (to the cent, as in ``_event_step``), partial from ``PROMISE_MIN_AED``, else none.
    ``promise_paid_amount`` runs to the event's deadline, so after an event that ended
    early it overlaps the next event's: never sum it across events."""
    paid = F.round(F.coalesce("promise_paid_amount", F.lit(0.0)), 2)
    outcome = (
        F.when(paid >= F.col("promise_amount"), "paid")
        .when(paid >= PROMISE_MIN_AED, "partial")
        .otherwise("none")
    )
    return (
        events.withColumn("promise_paid_amount", paid)
        .withColumn("promise_outcome", outcome)
        .select(*EVENTS)
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    model_id: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment. ``EVENTS``.

    A promise is a non-cancelled PTP or settlement plan (dated at its start) or a
    follow-up promise. An event starts with the first promise and stays alive until its
    deadline passes or the payments since its day reach the promised amount; every
    promise meanwhile belongs to it, the first one after it starts a new event
    (D-A3-29). ``event_kind``: matched (plans and follow-up promises), table_only,
    followup_only.

    The event day sets the terms: ``promise_cutoff`` by ``deadline`` (default
    ``promise_deadline(product, model_id)``, D-A3-28) and ``promise_amount``, the latest
    due on or before that day (at least ``PROMISE_MIN_AED``). Judged once on the
    payments from the event day up to the cutoff: paid when they reach the amount,
    partial from ``PROMISE_MIN_AED``, else none. RL cash is dated at the month end, so
    the event month's cash counts in full and never ends an event mid-month.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    if deadline not in CUTOFFS:
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    promises = _promise_rows(obs_base, followup, agreements, instalments)
    days = promises.select("account_id", "event_date").distinct()
    days = _with_payments(_with_terms(days, dues, deadline), payments)
    return _judged(_events(promises, _with_event_start(days)))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py`
action: replace · base sha256 `76aa555f6ef5d5593f98cdc0a78eb881dffdcd4e2490f7b8baf5c7a1f9de5804` · base trailing newline: yes · new sha256 `6f017e94bbe0819f6cbaa0c84d18e13d1731cee05decac516652eae855652379` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    require_columns,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)
from .promises import EVENTS
from .sources import CYCLE_LEDGER, DUES, EPISODE, INSTALMENTS, PAYMENTS


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    """``GRAIN`` and ``_anchor`` of every base row."""
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _commitment_counts(base: DataFrame, events: DataFrame, lower: Column) -> DataFrame:
    """Per base row with an event in ``[lower, observation date]``: the event, concluded,
    kept and partly kept counts and ``commitments_last_broken_n``, the not-kept events among
    the last ``BROKEN_STREAK`` concluded."""
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct(
                        "event_date", (~F.col("_kept")).cast("int").alias("broken")
                    ),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    return rows.groupBy(*GRAIN).agg(
        F.count(F.lit(1)).alias("commitments_n"),
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / broken / promised / no promise (D-A3-9, -26, -33).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only); concluded once their cutoff is on or before the observation date.
    An event is kept when paid; partial counts as not kept. Broken: the last 3 concluded
    all not kept (a broken event ranks first on a shared day), or at least 2 concluded
    and under 40% kept. Kept: at least 2 concluded and 80% kept. Partly kept: any
    kept event. Promised: any other event in the window. Else no_promise.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(events, EVENTS, "A3 promise events")
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    agg = _commitment_counts(base, events, lower)
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when(
            (F.col("commitments_last_broken_n") >= BROKEN_STREAK)
            | ((done >= MIN_CONCLUDED) & (rate < BROKEN_RATE)),
            "broken",
        )
        .when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .when(F.col("commitments_n") >= 1, "promised")
        .otherwise("no_promise")
    )
    counts = [
        "commitments_n",
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
        "commitments_last_broken_n",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_n",
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
            rate.alias("commitments_kept_rate"),
            "commitments_last_broken_n",
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_REPORTED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


# Contacts on the same day: the one later in this order counts as the latest (D-A3-32:
# promise > payment reported > refusal > dispute > contact > hung up).
_SAME_DAY_ORDER = ("hung_up", "success", "dispute", "refusal", "paid", "ptp")


def _disposition(name: Column) -> Column:
    """The ``_DISPOSITIONS`` label of a DCORE result name (NULL: not a contact)."""
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid on or after
    the refusal day, up to the observation date (Q-29, D-A3-30). A payment that may
    have come after the refusal lifts it: one dated the refusal day, and on RL the
    refusal month's cash (known only to the month)."""
    accounts = F.broadcast(refusals.select("account_id").distinct())
    cycles = dues.select("account_id", "cycle_start", "cycle_end").join(
        accounts, on="account_id", how="left_semi"
    )
    pays = (
        payments.join(accounts, on="account_id", how="left_semi")
        .alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_date") >= F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def _contact_events(
    episode: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """The account's DCORE events in ``[max(episode start, last DCORE_MAX_MONTHS
    months), observation date]`` with their ``_disp`` disposition (NULL: not a
    contact)."""
    lower = F.greatest(window_start(DCORE_MAX_MONTHS), F.col("_anchor"))
    return (
        _base(episode)
        .join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )


def _contact_summary(events: DataFrame) -> DataFrame:
    """Per base row: the latest right-party contact (``last_rpc_date``,
    ``last_rpc_disposition``; on one day, the latest by ``_SAME_DAY_ORDER``), the call
    days (``contact_dates_n``), the days with no pickup after the contact
    (``no_pickup_days_n``) and ``_dead``, 1 when a dead-line result came after it."""
    same_day_rank = F.lit(None).cast("int")
    for rank, label in enumerate(_SAME_DAY_ORDER):
        same_day_rank = F.when(F.col("_disp") == label, rank).otherwise(same_day_rank)
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct("day", same_day_rank.alias("same_day_rank"), "_disp"),
        )
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    last_day = F.col("_last")["day"]
    after = F.col("day") > last_day
    return (
        events.withColumn("_last", latest.over(Window.partitionBy(*GRAIN)))
        .groupBy(*GRAIN)
        .agg(
            F.max("_last")["day"].alias("last_rpc_date"),
            F.max("_last")["_disp"].alias("last_rpc_disposition"),
            F.size(
                F.collect_set(
                    F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
                )
            )
            .cast("long")
            .alias("contact_dates_n"),
            F.size(F.collect_set(F.when(after & no_pickup, F.col("day"))))
            .cast("long")
            .alias("no_pickup_days_n"),
            F.max(
                F.when(
                    after, F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")
                )
            ).alias("_dead"),
        )
    )


def _plan_after_refusal(refusals: DataFrame, instalments: DataFrame) -> DataFrame:
    """Rows whose plan started on or after the refusal day, by the observation date
    (D-A3-30: a plan of the same day may have followed the refusal)."""
    return (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") >= F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on one day, the latest by ``_SAME_DAY_ORDER``
    (D-A3-32).
    ``a3_refusal_flag``: it was a refusal, no plan started after it and no cycle / month
    with 100 AED or more paid may have come after it (D-A3-30). Diagnostics (not in the
    state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(payments, PAYMENTS, "A3 payments")
    require_columns(dues, DUES, "A3 dues")
    events = _contact_events(episode, followup, agreements)
    summary = _contact_summary(events)
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = _plan_after_refusal(refusals, instalments)
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        _base(episode)
        .select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
`````

New:

`````python
"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    require_columns,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)
from .promises import EVENTS
from .sources import CYCLE_LEDGER, DUES, EPISODE, INSTALMENTS, PAYMENTS


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    """``GRAIN`` and ``_anchor`` of every base row."""
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _commitment_counts(base: DataFrame, events: DataFrame, lower: Column) -> DataFrame:
    """Per base row with an event in ``[lower, observation date]``: the event, concluded,
    kept and partly kept counts."""
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    return rows.groupBy(*GRAIN).agg(
        F.count(F.lit(1)).alias("commitments_n"),
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
    )


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / promised / no promise (D-A3-9, -26, -33, -34).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only); concluded once their cutoff is on or before the observation date.
    An event is kept when paid; partial counts as not kept. Kept: at least 2 concluded
    and 80% kept. Partly kept: any kept event. Promised: any other event in the window.
    Else no_promise.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(events, EVENTS, "A3 promise events")
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    agg = _commitment_counts(base, events, lower)
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .when(F.col("commitments_n") >= 1, "promised")
        .otherwise("no_promise")
    )
    counts = [
        "commitments_n",
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_n",
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
            rate.alias("commitments_kept_rate"),
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_REPORTED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


# Contacts on the same day: the one later in this order counts as the latest (D-A3-32:
# promise > payment reported > refusal > dispute > contact > hung up).
_SAME_DAY_ORDER = ("hung_up", "success", "dispute", "refusal", "paid", "ptp")


def _disposition(name: Column) -> Column:
    """The ``_DISPOSITIONS`` label of a DCORE result name (NULL: not a contact)."""
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid on or after
    the refusal day, up to the observation date (Q-29, D-A3-30). A payment that may
    have come after the refusal lifts it: one dated the refusal day, and on RL the
    refusal month's cash (known only to the month)."""
    accounts = F.broadcast(refusals.select("account_id").distinct())
    cycles = dues.select("account_id", "cycle_start", "cycle_end").join(
        accounts, on="account_id", how="left_semi"
    )
    pays = (
        payments.join(accounts, on="account_id", how="left_semi")
        .alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_date") >= F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def _contact_events(
    episode: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """The account's DCORE events in ``[max(episode start, last DCORE_MAX_MONTHS
    months), observation date]`` with their ``_disp`` disposition (NULL: not a
    contact)."""
    lower = F.greatest(window_start(DCORE_MAX_MONTHS), F.col("_anchor"))
    return (
        _base(episode)
        .join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )


def _contact_summary(events: DataFrame) -> DataFrame:
    """Per base row: the latest right-party contact (``last_rpc_date``,
    ``last_rpc_disposition``; on one day, the latest by ``_SAME_DAY_ORDER``), the call
    days (``contact_dates_n``), the days with no pickup after the contact
    (``no_pickup_days_n``) and ``_dead``, 1 when a dead-line result came after it."""
    same_day_rank = F.lit(None).cast("int")
    for rank, label in enumerate(_SAME_DAY_ORDER):
        same_day_rank = F.when(F.col("_disp") == label, rank).otherwise(same_day_rank)
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct("day", same_day_rank.alias("same_day_rank"), "_disp"),
        )
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    last_day = F.col("_last")["day"]
    after = F.col("day") > last_day
    return (
        events.withColumn("_last", latest.over(Window.partitionBy(*GRAIN)))
        .groupBy(*GRAIN)
        .agg(
            F.max("_last")["day"].alias("last_rpc_date"),
            F.max("_last")["_disp"].alias("last_rpc_disposition"),
            F.size(
                F.collect_set(
                    F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
                )
            )
            .cast("long")
            .alias("contact_dates_n"),
            F.size(F.collect_set(F.when(after & no_pickup, F.col("day"))))
            .cast("long")
            .alias("no_pickup_days_n"),
            F.max(
                F.when(
                    after, F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")
                )
            ).alias("_dead"),
        )
    )


def _plan_after_refusal(refusals: DataFrame, instalments: DataFrame) -> DataFrame:
    """Rows whose plan started on or after the refusal day, by the observation date
    (D-A3-30: a plan of the same day may have followed the refusal)."""
    return (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") >= F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on one day, the latest by ``_SAME_DAY_ORDER``
    (D-A3-32).
    ``a3_refusal_flag``: it was a refusal, no plan started after it and no cycle / month
    with 100 AED or more paid may have come after it (D-A3-30). Diagnostics (not in the
    state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(payments, PAYMENTS, "A3 payments")
    require_columns(dues, DUES, "A3 dues")
    events = _contact_events(episode, followup, agreements)
    summary = _contact_summary(events)
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = _plan_after_refusal(refusals, instalments)
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        _base(episode)
        .select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/b28_check.py`
action: add · new sha256 `630e1ae841d1b645b06f78474fe0632ac083415a0ffcc5cef49f3095d9542876` · new trailing newline: yes

New:

`````python
"""TEMPORARY (bundle 28): the A1 and A3 states before and after the bundle's step 8.

``crx_<p>_b28_snapshot`` (run before step 8) copies the persisted A1 and A3 state
columns into ``crx_<p>_b28_old_states`` (explicit entries in
``catalog_tmp_b28_check.yml``). ``crx_<p>_b28_compare`` (run after step 8) joins that
copy to the new persisted outputs and logs, for ``model_id``:

- ``B28 ROWS``: rows old / new / in both, and per month the rows whose A1 or A3 state
  changed;
- ``B28 A1``: latest persona month, ``a1_state`` old x new, and the
  ``a1_cross_product_level`` changes (F4: card parent link, point-in-time CIF);
- ``B28 A3``: latest persona month, ``a3_state`` and ``a3_commitments_level`` old x new
  (same-day payments, no Broken level).

The old tables predate bundle 25's rules as well (its step 8 is folded into this one).
Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b28_snapshot      (before step 8)
    kedro run --pipeline=crx_<p>_b28_compare       (after step 8)
"""

import logging

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ._common import GRAIN

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "b28_check"]
A1_COLUMNS = ["a1_state", "a1_cross_product_level"]
A3_COLUMNS = ["a3_state", "a3_commitments_level"]


def snapshot(a1: DataFrame, a3: DataFrame) -> DataFrame:
    """``GRAIN`` and the A1 / A3 state columns (those the table has), one row per key."""

    def pick(df: DataFrame, cols: list[str]) -> DataFrame:
        return df.select(*GRAIN, *(c for c in cols if c in df.columns))

    return pick(a1, A1_COLUMNS).join(pick(a3, A3_COLUMNS), list(GRAIN), "full")


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _crosstab(df: DataFrame, col: str, changed_only: bool = False) -> list[str]:
    """``old_<col>`` x ``new_<col>`` counts over the rows with a value on either side
    (only the changed pairs if asked)."""
    old, new = f"old_{col}", f"new_{col}"
    if old not in df.columns or new not in df.columns:
        return [f"  {col}: not in both tables"]
    df = df.filter(F.col(old).isNotNull() | F.col(new).isNotNull())
    if changed_only:
        df = df.filter(~F.col(old).eqNullSafe(F.col(new)))
    total = max(df.count(), 1)
    rows = df.groupBy(old, new).count().orderBy(old, new).collect()
    return [f"  {col} old | new{' (changed only)' if changed_only else ''}:"] + (
        [
            f"    {r[old]} | {r[new]}: {r['count']} ({100 * r['count'] / total:.1f}%)"
            for r in rows
        ]
        or ["    none"]
    )


def _changed(col: str, columns: list[str]):
    """1 where a row on both sides changed ``col``."""
    old, new = f"old_{col}", f"new_{col}"
    if old not in columns or new not in columns:
        return F.lit(None).cast("int")
    both = F.col("old_row").isNotNull() & F.col("new_row").isNotNull()
    return (both & ~F.col(old).eqNullSafe(F.col(new))).cast("int")


def compare(  # pylint: disable=too-many-arguments
    old: DataFrame,
    a1: DataFrame,
    a3: DataFrame,
    *,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Log the ``B28`` blocks (module docstring)."""
    new = snapshot(a1, a3)

    def side(df: DataFrame, prefix: str) -> DataFrame:
        return df.select(
            *GRAIN,
            F.lit(1).alias(f"{prefix}_row"),
            *(F.col(c).alias(f"{prefix}_{c}") for c in df.columns if c not in GRAIN),
        )

    pairs = (
        side(old, "old").join(side(new, "new"), list(GRAIN), "full").localCheckpoint()
    )
    month = F.last_day("observation_date").alias("month")
    per_month = (
        pairs.groupBy(month)
        .agg(
            F.sum("old_row").alias("old"),
            F.sum("new_row").alias("new"),
            F.sum(F.col("old_row") * F.col("new_row")).alias("both"),
            F.sum(_changed("a1_state", pairs.columns)).alias("a1_changed"),
            F.sum(_changed("a3_state", pairs.columns)).alias("a3_changed"),
        )
        .orderBy("month")
        .collect()
    )
    _block(
        "B28 ROWS",
        model_id,
        ["  month: rows old / new / both, a1_state / a3_state changed (rows in both)"]
        + [
            f"    {r['month']}: {r['old']} / {r['new']} / {r['both']},"
            f" {r['a1_changed']}, {r['a3_changed']}"
            for r in per_month
        ],
    )
    latest = pairs.filter(
        F.trunc("observation_date", "month")
        == F.trunc(F.lit(str(persona_end_date)), "month")
    )
    _block(
        "B28 A1",
        model_id,
        _crosstab(latest, "a1_state")
        + _crosstab(latest, "a1_cross_product_level", changed_only=True),
    )
    _block(
        "B28 A3",
        model_id,
        _crosstab(latest, "a3_state") + _crosstab(latest, "a3_commitments_level"),
    )


def create_snapshot_pipeline(product: str) -> Pipeline:
    """Copy the persisted A1 / A3 states of ``product`` before step 8."""
    return pipeline(
        [
            node(
                func=snapshot,
                inputs={
                    "a1": f"crx_{product}_a1_ability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                },
                outputs=f"crx_{product}_b28_old_states",
                name=f"crx_{product}_b28_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline(product: str) -> Pipeline:
    """Log the old x new states of ``product`` after step 8."""
    return pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": f"crx_{product}_b28_old_states",
                    "a1": f"crx_{product}_a1_ability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"crx_{product}_b28_compare",
                tags=TAGS,
            )
        ]
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
Clean up after mirror bundle 28_rules_a1_a3.md, on the bundle's branch.
Run once, after step 8's blocks are pasted back.

- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the path from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for each of the four model_ids (skip folders that do not exist): `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/b28_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundle 28):
  - delete `conf/base/catalog/catalog_tmp_b28_check.yml`;
  - `src/enbd_collections/pipeline_registry.py`: the four `crx_<p>_b28_snapshot` / `crx_<p>_b28_compare` entries, their comment line and the `b28_check` import;
  - delete `src/enbd_collections/pipelines/crx_persona/b28_check.py`.
- Delete `data/input/mirror_bundles/`.

  Then check that `kedro registry list` still works and that `grep -rn "b28" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
