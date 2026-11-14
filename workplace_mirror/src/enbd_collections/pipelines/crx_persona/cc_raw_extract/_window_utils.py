"""Per-account windowing shared by the ``cc_raw_extract`` nodes: partition pruning on
``edp_load_date`` and the per-account date scope."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.utils.config import EDP_LOAD_DATE_BUFFER_MONTHS


def prune_by_edp_load_date(raw_df: DataFrame, acct_windows: DataFrame) -> DataFrame:
    """``raw_df`` pruned on ``edp_load_date`` (the Hive partition column) to the global
    [min(acct_start), max(acct_end)] of ``acct_windows`` widened by
    ``EDP_LOAD_DATE_BUFFER_MONTHS``. The buffer absorbs the lag between an event date
    and its load-date partition; ``cc_spine`` has no backward lookback of its own. A
    superset filter: callers still scope each account to its own window with
    ``scope_to_acct_window``."""
    window_lo, window_hi = acct_windows.agg(
        F.min("acct_start"), F.max("acct_end")
    ).first()
    load_date_lo = F.add_months(F.lit(window_lo), -EDP_LOAD_DATE_BUFFER_MONTHS)
    load_date_hi = F.add_months(F.lit(window_hi), EDP_LOAD_DATE_BUFFER_MONTHS)
    return raw_df.where(
        F.col("edp_load_date").cast(DateType()).between(load_date_lo, load_date_hi)
    )


def scope_to_acct_window(
    raw_df: DataFrame, acct_windows: DataFrame, date_col: str
) -> DataFrame:
    """``raw_df`` with ``contract_idt`` cast to long (the raw key is a double), joined
    to ``acct_windows`` (keyed by ``contract_idt``, with ``acct_start`` / ``acct_end``)
    and cut to ``date_col`` within [acct_start, acct_end]."""
    return (
        raw_df.withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col(date_col).cast(DateType()) >= F.col("acct_start"))
            & (F.col(date_col).cast(DateType()) <= F.col("acct_end"))
        )
    )
