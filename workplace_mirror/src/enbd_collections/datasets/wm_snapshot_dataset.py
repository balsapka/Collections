"""Read-only Kedro dataset: one ``adv_load_date`` snapshot of a WM feature table.

WM ``04_feature`` tables are written as ``<root>/adv_load_date=YYYY-MM-DD/``; each
partition is a full-history snapshot (weekly rows in ``week_number``, ``yyyyMM0W``).
The dataset reads one partition, the ``snapshot`` date from globals, and falls back to
another partition when that one is missing or cannot be read. The tables belong to WM,
so a damaged partition cannot be fixed or rebuilt from this repo.

Readable means every byte of the partition comes back: the dataset scans the whole
partition once (Spark's ``noop`` sink) before returning it. HDFS can list a file whose
block no DataNode can serve (``BlockMissingException``), so the listing alone proves
nothing.

Fallback order: newer partitions first (nearest first), then older ones (nearest
first), at most ``max_fallback`` of them. A partition is only used when its
``week_number`` range covers the ``required_from`` and ``required_through`` months (each
optional): an older snapshot that would leave the last months empty, or a partition
without the full history, is refused. When no partition qualifies, the load
fails with the reason for each one tried. A fallback is logged as a warning.

Catalog example::

    wm_fea_casa_eod_avg_balance:
      type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
      filepath: ".../04_feature/fea_casa_eod_avg_bal_by_cif"
      snapshot: "${globals:snapshot_adv_load_date}"
      required_from: "2025-02-01"
      required_through: "${globals:crx_persona.persona_end_date}"
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from kedro.io.core import AbstractDataset, DatasetError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(str(value)) if value else None


def _month(day: date) -> int:
    """``day``'s month as ``yyyyMM``, the leading part of a WM ``week_number``."""
    return day.year * 100 + day.month


# Kedro aliases load / save to _load / _save; there is no base __init__ to call.
# pylint: disable=abstract-method,super-init-not-called,too-many-instance-attributes
# pylint: disable=broad-exception-caught
class WMSnapshotDataset(AbstractDataset[None, DataFrame]):
    """One snapshot partition of a WM table, with fallback to its neighbours."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        filepath: str,
        snapshot: str,
        partition_column: str = "adv_load_date",
        required_from: str | None = None,
        required_through: str | None = None,
        week_column: str = "week_number",
        max_fallback: int = 3,
        file_format: str = "parquet",
        load_args: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._root = filepath.rstrip("/")
        self._snapshot = date.fromisoformat(str(snapshot))
        self._column = partition_column
        self._required_from = _date(required_from)
        self._required = _date(required_through)
        self._week = week_column
        self._max_fallback = max_fallback
        self._format = file_format
        self._load_args = load_args or {}
        self.metadata = metadata

    def _describe(self) -> dict[str, Any]:
        return {
            "filepath": self._root,
            "snapshot": str(self._snapshot),
            "partition_column": self._column,
            "required_from": self._required_from,
            "required_through": self._required,
            "max_fallback": self._max_fallback,
        }

    def _save(self, data: None) -> None:
        raise DatasetError(f"{self._root} belongs to WM; this dataset is read-only.")

    def _exists(self) -> bool:
        return bool(self.partitions())

    def _load(self) -> DataFrame:
        available = self.partitions()
        refused = []
        for day in self.candidates(self._snapshot, available, self._max_fallback):
            problem = "no partition"
            if day in available:
                df, problem = self._read(day)
                problem = problem or self.coverage_problem(df)
            if problem:
                refused.append(f"{day}: {problem}")
                continue
            if day != self._snapshot:
                logger.warning(
                    "%s: using %s=%s instead of %s (%s)",
                    self._root,
                    self._column,
                    day,
                    self._snapshot,
                    "; ".join(refused),
                )
            return df
        raise DatasetError(
            f"{self._root}: no usable {self._column} partition. " + "; ".join(refused)
        )

    @staticmethod
    def candidates(
        target: date, available: list[date], max_fallback: int
    ) -> list[date]:
        """``target``, then up to ``max_fallback`` other partitions: newer ones from the
        nearest on, then older ones from the nearest back."""
        newer = sorted(d for d in available if d > target)
        older = sorted((d for d in available if d < target), reverse=True)
        return [target] + (newer + older)[:max_fallback]

    @staticmethod
    def problem(err: Exception) -> str:
        """A one-line reason from a read error: the deepest Java cause (e.g.
        ``BlockMissingException: ...``) when there is one, else the first line."""
        cause = getattr(err, "java_exception", None)
        while cause is not None and cause.getCause() is not None:
            cause = cause.getCause()
        text = str(cause.toString()) if cause is not None else str(err).strip()
        return (text.splitlines() or [type(err).__name__])[0][:300]

    def coverage_problem(self, df: DataFrame) -> str | None:
        """Why ``df``'s weeks miss the ``required_from`` or ``required_through`` month,
        or None (also when neither is set). Logs the partition's week range."""
        if not (self._required_from or self._required):
            return None
        week = F.col(self._week).cast("long")
        first, last = df.agg(F.min(week), F.max(week)).first()
        logger.info("%s: weeks %s to %s", self._root, first, last)
        if last is None:
            return "no rows"
        if self._required_from and first // 100 > _month(self._required_from):
            return f"weeks start at {first}, run needs {_month(self._required_from)}"
        if self._required and last // 100 < _month(self._required):
            return f"weeks end at {last}, run needs month {_month(self._required)}"
        return None

    def partitions(self) -> list[date]:
        """The dates of the ``<partition_column>=YYYY-MM-DD`` folders under the root."""
        spark = SparkSession.builder.getOrCreate()
        jvm, jsc = spark._jvm, spark._jsc  # pylint: disable=protected-access
        root = jvm.org.apache.hadoop.fs.Path(self._root)
        fs = root.getFileSystem(jsc.hadoopConfiguration())
        if not fs.exists(root):
            return []
        pattern = re.compile(rf"{re.escape(self._column)}=(\d{{4}}-\d{{2}}-\d{{2}})$")
        found = []
        for status in fs.listStatus(root):
            match = pattern.match(status.getPath().getName())
            if status.isDirectory() and match:
                found.append(date.fromisoformat(match.group(1)))
        return found

    def _read(self, day: date) -> tuple[DataFrame | None, str | None]:
        """The partition and None, or None and why it cannot be read in full (the
        footers are read on load, the rest by the ``noop`` scan)."""
        spark = SparkSession.builder.getOrCreate()
        reader = spark.read.format(self._format).options(**self._load_args)
        try:
            df = reader.load(f"{self._root}/{self._column}={day}")
            df.write.format("noop").mode("overwrite").save()
        except Exception as err:  # noqa: BLE001 - any read failure means fall back
            return None, self.problem(err)
        return df, None
