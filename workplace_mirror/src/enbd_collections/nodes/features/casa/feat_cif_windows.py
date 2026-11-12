"""Feature nodes: monthly salary, CASA inflow and net flow per customer, all history.

One table, ``feat_cif_inflow_outflow_salary_monthly``, one row per ``(cif_id, month_end)``. For each
field - ``salary_internal``, ``salary_external``, ``salary_consolidated``, ``inflow``,
``outflow``, ``netflow`` - the month and its trailing 3, 6 and 12 month average
(``<field>``, ``<field>_3m_avg``, ``_6m_avg``, ``_12m_avg``). A row uses only data up to
its ``month_end`` (R2). Three nodes build it:

* ``build_casa_flow``     - ``inflow`` and ``outflow`` (credits and debits on CASA) and
  ``netflow`` (inflow - outflow) from WM's rolling-window columns at the month's last
  weekly snapshot;
* ``build_salary_windows`` - the three salary fields, windowed here because WM has no
  salary windows;
* ``join_windows``         - full outer join of the two on ``(cif_id, month_end)``.

``union_models`` then consolidates the four per-model tables into one, cut at
``persona_end_date`` (pipeline ``casa_windows_all_models``).

An average divides by N (a missing month counts as 0) and, as in WM, is NULL unless the
whole lookback is in the data. WM weekly tables carry ``week_number`` as ``yyyyMM0W``
(week 01-04 of the month), so the ``in_last_0_N_weeks`` window of week 04 covers N + 1
weeks ending with that month.
"""

from __future__ import annotations

from functools import reduce

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .feat_cif_casa import _cif, _require, _wm_month

AVG_MONTHS = {"3m": 3, "6m": 6, "12m": 12}
# WM ``in_last_0_N_weeks`` windows (4 weeks per month, the snapshot week included) that
# hold exactly 1, 3, 6 and 12 months.
FLOW_WEEKS = {"": (3, 1), "_3m_avg": (11, 3), "_6m_avg": (23, 6), "_12m_avg": (47, 12)}
LAST_WEEK_OF_MONTH = "04"
SALARY_FIELDS = ("internal", "external", "consolidated")
# Model variants whose per-model tables ``union_models`` consolidates (tie-break order).
MODEL_IDS = ("cc_60_180", "cc_180_plus", "rl_60_180", "rl_180_plus")
_BUREAU_CARRY_MONTHS = 1  # a pull also counts in the month after it (A1 spec S14)


def _wm_sum(metric: str, weeks: int) -> str:
    return f"ft_{metric}_in_last_0_{weeks}_weeks_sum"


def build_casa_flow(wm_casa_flow: DataFrame) -> DataFrame:
    """``inflow[_<3m|6m|12m>_avg]``, ``outflow[...]`` and ``netflow[...]`` per ``(cif_id, month_end)``
    from ``wm_fea_casa_cc_inflow_outflow`` (CASA only).

    The month is WM's ``0_3`` window at the month's last weekly snapshot (week 04); the
    N-month average is WM's ``0_11`` / ``0_23`` / ``0_47`` window divided by N. Inflow is
    ``inflow_casa_amt``, outflow ``outflow_casa_amt``; net flow is inflow minus outflow
    (WM's own gap column has the opposite sign). A value is NULL where WM lacks the
    history for its window; a month without a week-04 row has no row. All history.
    """
    metrics = ("inflow_casa_amt", "outflow_casa_amt")
    _require(
        wm_casa_flow,
        [
            "cif_id",
            "week_number",
            *[_wm_sum(m, weeks) for m in metrics for weeks, _ in FLOW_WEEKS.values()],
        ],
        "wm_fea_casa_cc_inflow_outflow",
    )
    values = []
    for suffix, (weeks, months) in FLOW_WEEKS.items():
        inflow = F.col(_wm_sum("inflow_casa_amt", weeks)).cast("double")
        outflow = F.col(_wm_sum("outflow_casa_amt", weeks)).cast("double")
        values += [
            (inflow / months).alias(f"inflow{suffix}"),
            (outflow / months).alias(f"outflow{suffix}"),
            ((inflow - outflow) / months).alias(f"netflow{suffix}"),
        ]
    week = F.col("week_number").cast("string")
    return wm_casa_flow.filter(F.substring(week, 7, 2) == LAST_WEEK_OF_MONTH).select(
        _cif(), F.last_day(_wm_month()).alias("month_end"), *values
    )


def _month_number_of(column: Column) -> Column:
    return F.year(column) * 12 + F.month(column) - 1


def _external_series(bureau_salary: DataFrame) -> DataFrame:
    """``ext`` per ``(cif_id, month_end)``: each pull's month, and the month after it
    unless that month has its own pull (never before a pull; pulls every 2 months make a
    continuous series). A pull of 0 (salary account closed) ends the carry. The same rule
    as A1's ``_with_next_month`` (S14).
    """
    pulls = bureau_salary.select(
        _cif(), "month_end", F.col("bureau_salary").cast("double")
    )
    pulls = pulls.groupBy("cif_id", "month_end").agg(
        F.max("bureau_salary").alias("bureau_salary")
    )
    carried = pulls.select(
        "cif_id",
        F.last_day(F.add_months("month_end", _BUREAU_CARRY_MONTHS)).alias("month_end"),
        F.col("bureau_salary").alias("_carried"),
    )
    return pulls.join(carried, on=["cif_id", "month_end"], how="full").select(
        "cif_id",
        "month_end",
        F.coalesce("bureau_salary", "_carried").alias("ext"),
    )


def _internal_series(internal_salary: DataFrame) -> DataFrame:
    """``int`` per ``(cif_id, month_end)``: the month's internal salary."""
    return (
        internal_salary.select(
            _cif(), "month_end", F.col("salary").cast("double").alias("int")
        )
        .groupBy("cif_id", "month_end")
        .agg(F.max("int").alias("int"))
    )


def _history_start(internal: DataFrame, external: DataFrame) -> DataFrame:
    """One row: the first month of each source's data (``internal_start``,
    ``external_start``) and of both (``consolidated_start``, the later of the two). Before
    it the source is unknown, not zero."""
    first = _month_number_of(F.min("month_end"))
    return (
        internal.agg(first.alias("internal_start"))
        .crossJoin(external.agg(first.alias("external_start")))
        .withColumn(
            "consolidated_start", F.greatest("internal_start", "external_start")
        )
    )


def _monthly_salary(internal: DataFrame, external: DataFrame) -> DataFrame:
    """``internal``, ``external``, ``consolidated`` per ``(cif_id, month_nr)``: the
    internal salary, the carried bureau salary and the larger of the two; NULL where the
    source is not above 0."""
    both = internal.join(external, on=["cif_id", "month_end"], how="full")
    return both.select(
        "cif_id",
        _month_number_of(F.col("month_end")).alias("month_nr"),
        F.when(F.col("int") > 0, F.col("int")).alias("internal"),
        F.when(F.col("ext") > 0, F.col("ext")).alias("external"),
    ).withColumn("consolidated", F.greatest("internal", "external"))


def _data_end(internal: DataFrame, bureau_salary: DataFrame) -> DataFrame:
    """One row: ``end_nr``, the latest month with real data - an internal salary month or
    a bureau pull month, never the month a pull is carried into (that may not have
    happened yet)."""
    months = internal.select("month_end").unionByName(bureau_salary.select("month_end"))
    return months.agg(_month_number_of(F.max("month_end")).alias("end_nr"))


def _month_grid(monthly: DataFrame, data_end: DataFrame) -> DataFrame:
    """Every ``(cif_id, month_nr)`` from the customer's first salary month to 11 months
    after the last (the 12-month window still reaches it), no gaps - so a row-based window
    of N rows is N calendar months. Never past ``data_end``."""
    reach = max(AVG_MONTHS.values()) - 1
    bounds = (
        monthly.groupBy("cif_id")
        .agg(F.min("month_nr").alias("first_nr"), F.max("month_nr").alias("last_nr"))
        .crossJoin(F.broadcast(data_end))
    )
    return bounds.select(
        "cif_id",
        F.explode(
            F.sequence(
                F.col("first_nr"), F.least(F.col("last_nr") + reach, F.col("end_nr"))
            )
        ).alias("month_nr"),
    )


def _trailing(months: int):
    return (
        Window.partitionBy("cif_id").orderBy("month_nr").rowsBetween(-(months - 1), 0)
    )


def _salary_columns() -> list[Column]:
    """``salary_<field>`` and ``salary_<field>_<3m|6m|12m>_avg`` for every field. As in
    WM, an average is NULL unless its whole lookback is inside the source's data."""
    columns = []
    for field in SALARY_FIELDS:
        month = F.coalesce(field, F.lit(0.0))
        columns.append(month.alias(f"salary_{field}"))
        for label, months in AVG_MONTHS.items():
            covered = F.col("month_nr") - (months - 1) >= F.col(f"{field}_start")
            columns.append(
                F.when(covered, F.sum(month).over(_trailing(months)) / months).alias(
                    f"salary_{field}_{label}_avg"
                )
            )
    return columns


def build_salary_windows(
    internal_salary: DataFrame, bureau_salary: DataFrame
) -> DataFrame:
    """``salary_<internal|external|consolidated>[_<3m|6m|12m>_avg]`` per
    ``(cif_id, month_end)``.

    * internal - ``feat_cif_internal_salary_monthly`` (salary credited in the month);
    * external - ``feat_cif_bureau_salary_monthly``: AECB salary alerts from
      ``prm_bureau_alert_enriched`` only, as A1, no loan-level pulls; a level on the pull
      date, carried one month forward;
    * consolidated - the larger of the two in each month.

    The plain column is the month's value (0 where none above 0); ``_<N>m_avg`` is the
    last N months summed and divided by N, the row's month included, NULL unless the whole
    lookback is inside the source's data (as WM does; ``consolidated`` needs both
    sources). All history: a row for every month from a customer's first salary month to
    the latest real month in the data, i.e. never a future month a bureau pull would be
    carried into (at most 11 months past the customer's last salary),
    kept where the last 12 months hold a consolidated salary.
    """
    _require(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    _require(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    internal, external = _internal_series(internal_salary), _external_series(
        bureau_salary
    )
    monthly = _monthly_salary(internal, external)
    grid = (
        _month_grid(monthly, _data_end(internal, bureau_salary))
        .join(monthly, on=["cif_id", "month_nr"], how="left")
        .crossJoin(F.broadcast(_history_start(internal, external)))
    )
    month_start = F.to_date(
        F.format_string(
            "%04d-%02d-01",
            (F.col("month_nr") / 12).cast("int"),
            F.col("month_nr") % 12 + 1,
        )
    )
    has_salary = (
        F.sum(F.coalesce("consolidated", F.lit(0.0))).over(
            _trailing(max(AVG_MONTHS.values()))
        )
        > 0
    )
    values = grid.select(
        "cif_id", "month_nr", *_salary_columns(), has_salary.alias("_has_salary")
    )
    return values.filter("_has_salary").select(
        "cif_id",
        F.last_day(month_start).alias("month_end"),
        *[c for c in values.columns if c.startswith("salary_")],
    )


def join_windows(flow: DataFrame, salary: DataFrame) -> DataFrame:
    """``feat_cif_inflow_outflow_salary_monthly``: ``build_casa_flow`` and
    ``build_salary_windows`` on ``(cif_id, month_end)``, every row of either side kept, all
    history (the cut at ``persona_end_date`` is in ``union_models``). Nothing is filled: salary
    columns are NULL on a customer-month with no salary in the last 12 months (or before
    the salary history), flow columns where WM has no row or does not populate the window.
    """
    _require(flow, ["cif_id", "month_end"], "build_casa_flow")
    _require(salary, ["cif_id", "month_end"], "build_salary_windows")
    return flow.join(salary, on=["cif_id", "month_end"], how="full")


def union_models(persona_end_date: str, **tables: DataFrame) -> DataFrame:
    """One ``feat_cif_inflow_outflow_salary_monthly`` for all customers of the four models:
    the per-model tables (keyword ``<model_id>`` for each of ``MODEL_IDS``) stacked, cut at
    ``persona_end_date`` and reduced to one row per ``(cif_id, month_end)``.

    A customer in more than one model has the same WM columns in each; the bureau columns
    come from model-scoped alerts and may differ. The row kept is the one with the most
    non-NULL values (a whole row, never a mix of columns), then the first model in
    ``MODEL_IDS`` order.
    """
    missing = sorted(set(MODEL_IDS) - set(tables))
    if missing:
        raise ValueError(f"union_models is missing tables for: {missing}")
    stacked = reduce(
        DataFrame.unionByName,
        [tables[m].withColumn("_src", F.lit(i)) for i, m in enumerate(MODEL_IDS)],
    )
    values = [c for c in stacked.columns if c not in ("cif_id", "month_end", "_src")]
    filled = sum((F.col(c).isNotNull().cast("int") for c in values), F.lit(0))
    best = Window.partitionBy("cif_id", "month_end").orderBy(
        filled.desc(), F.col("_src").asc()
    )
    return (
        stacked.filter(F.col("month_end") <= F.to_date(F.lit(str(persona_end_date))))
        .withColumn("_rank", F.row_number().over(best))
        .filter(F.col("_rank") == 1)
        .drop("_rank", "_src")
    )
