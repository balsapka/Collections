"""Feature node: CASA inflow, outflow and net flow per customer and month, CASA schemes only.

Same output columns as ``feat_cif_windows.build_casa_flow`` (``inflow``, ``outflow``,
``netflow`` and their ``_3m_avg`` / ``_6m_avg`` / ``_12m_avg``), but built from the legs of
``wm_pri_labelled_transactions`` that sit on a current or savings account
(``prm_casa_accounts``, Finacle scheme codes), instead of WM's CIF-week aggregate, which
counts every FTR leg including loan accounts. Nothing else is removed: fees, reversals,
own-account transfers and bank recoveries on a CASA account are still counted, as in WM.

An average divides by N (a month without legs counts as 0) and is NULL unless the whole
lookback is inside the complete months of the data.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .feat_cif_casa import _cif, _require
from .feat_cif_windows import AVG_MONTHS, _month_number_of, _trailing

# A month is complete when the data starts within the first / ends within the last few days
# of it (weekends can leave the last day empty).
_EDGE_DAYS = 3
_REACH = max(AVG_MONTHS.values()) - 1
_FIELDS = ("inflow", "outflow", "netflow")


def _casa_legs(wm_labelled: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """``cif_id``, ``d`` (date), ``flow`` (inflow / outflow) and ``amt`` (AED) of the CASA
    legs on a current or savings account."""
    _require(
        wm_labelled,
        ["cif_id", "acid", "tran_date", "in_out_flow", "tran_amt", "product_category"],
        "wm_pri_labelled_transactions",
    )
    _require(casa_accounts, ["foracid"], "prm_casa_accounts")
    accounts = casa_accounts.select(
        F.trim(F.col("foracid").cast("string")).alias("foracid")
    ).distinct()
    return (
        wm_labelled.filter(
            (F.col("product_category") == "CASA") & F.col("tran_amt").isNotNull()
        )
        .select(
            _cif(),
            F.trim(F.col("acid").cast("string")).alias("foracid"),
            F.to_date("tran_date").alias("d"),
            F.col("in_out_flow").alias("flow"),
            F.col("tran_amt").cast("double").alias("amt"),
        )
        .join(accounts, on="foracid", how="left_semi")
    )


def _complete_months(legs: DataFrame) -> DataFrame:
    """One row: ``start_nr`` / ``end_nr``, the first and last complete month of the legs."""
    edges = legs.agg(F.min("d").alias("first_d"), F.max("d").alias("last_d"))
    starts_early = F.dayofmonth("first_d") <= _EDGE_DAYS
    ends_late = F.datediff(F.last_day("last_d"), F.col("last_d")) <= _EDGE_DAYS
    return edges.select(
        (
            _month_number_of(F.col("first_d")) + F.when(starts_early, 0).otherwise(1)
        ).alias("start_nr"),
        (_month_number_of(F.col("last_d")) - F.when(ends_late, 0).otherwise(1)).alias(
            "end_nr"
        ),
    )


def _grid(monthly: DataFrame, bounds: DataFrame) -> DataFrame:
    """Every ``(cif_id, month_nr)`` from the customer's first month with legs to 11 months
    after the last, no gaps, never past the last complete month."""
    per_cif = (
        monthly.groupBy("cif_id")
        .agg(F.min("month_nr").alias("first_nr"), F.max("month_nr").alias("last_nr"))
        .crossJoin(F.broadcast(bounds))
    )
    return per_cif.select(
        "cif_id",
        F.explode(
            F.sequence(
                F.col("first_nr"), F.least(F.col("last_nr") + _REACH, F.col("end_nr"))
            )
        ).alias("month_nr"),
    )


def _flow_columns() -> list[Column]:
    """``inflow`` / ``outflow`` / ``netflow`` and their averages, grouped by window."""
    columns = []
    for suffix, months in {
        "": 1,
        **{f"_{k}_avg": v for k, v in AVG_MONTHS.items()},
    }.items():
        covered = F.col("month_nr") - (months - 1) >= F.col("start_nr")
        for field in _FIELDS:
            total = (
                F.sum(F.col(field)).over(_trailing(months))
                if months > 1
                else F.col(field)
            )
            columns.append(F.when(covered, total / months).alias(f"{field}{suffix}"))
    return columns


def build_casa_scheme_flow(
    wm_labelled: DataFrame, casa_accounts: DataFrame
) -> DataFrame:
    """``inflow``, ``outflow``, ``netflow`` and their ``_3m_avg`` / ``_6m_avg`` /
    ``_12m_avg`` per ``(cif_id, month_end)``, in the order inflow, outflow, netflow within
    each window.

    * the month - credits (``in_out_flow`` = inflow) and debits (outflow) on current and
      savings accounts, in AED; ``netflow`` = inflow - outflow;
    * ``_<N>m_avg`` - the last N months summed and divided by N, the row's month included,
      NULL unless the whole lookback is in the complete months of the data.

    All history, complete months only (a partial first or last month is dropped): a row for
    every month from a customer's first month with legs to the last complete month (at
    most 11 months past their last leg), kept where the last 12 months have any leg.
    """
    legs = _casa_legs(wm_labelled, casa_accounts)
    bounds = _complete_months(legs)
    monthly = (
        legs.withColumn("month_nr", _month_number_of(F.col("d")))
        .groupBy("cif_id", "month_nr")
        .agg(
            F.sum(F.when(F.col("flow") == "inflow", F.col("amt"))).alias("inflow"),
            F.sum(F.when(F.col("flow") == "outflow", F.col("amt"))).alias("outflow"),
        )
        .crossJoin(F.broadcast(bounds))
        .filter(F.col("month_nr").between(F.col("start_nr"), F.col("end_nr")))
        .select("cif_id", "month_nr", "inflow", "outflow")
    )
    grid = (
        _grid(monthly, bounds)
        .join(monthly, on=["cif_id", "month_nr"], how="left")
        .crossJoin(F.broadcast(bounds))
        .withColumn("inflow", F.coalesce("inflow", F.lit(0.0)))
        .withColumn("outflow", F.coalesce("outflow", F.lit(0.0)))
        .withColumn("netflow", F.col("inflow") - F.col("outflow"))
    )
    active = F.sum(F.col("inflow") + F.col("outflow")).over(_trailing(_REACH + 1)) > 0
    values = grid.select(
        "cif_id", "month_nr", *_flow_columns(), active.alias("_active")
    )
    month_start = F.to_date(
        F.format_string(
            "%04d-%02d-01",
            (F.col("month_nr") / 12).cast("int"),
            F.col("month_nr") % 12 + 1,
        )
    )
    return values.filter("_active").select(
        "cif_id",
        F.last_day(month_start).alias("month_end"),
        *[c for c in values.columns if c.startswith(_FIELDS)],
    )
