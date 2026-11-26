"""Spec test for ``WMSnapshotDataset`` (local Spark, temp folder).

Run: ``JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/wm_snapshot_spec.py``
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# pylint: disable=wrong-import-position,invalid-name,protected-access,abstract-class-instantiated
from kedro.io.core import DatasetError
from pyspark.sql import SparkSession

from enbd_collections.datasets.wm_snapshot_dataset import WMSnapshotDataset

spark = SparkSession.builder.master("local[1]").getOrCreate()
spark.sparkContext.setLogLevel("OFF")
D = date.fromisoformat


def write(base: Path, day: str, last: int) -> None:
    """A snapshot partition whose weeks run up to ``last``."""
    rows = [(1, w) for w in (20260801, last)]
    spark.createDataFrame(rows, "cif_id long, week_number int").write.parquet(
        str(base / f"adv_load_date={day}")
    )


def damage(base: Path, day: str) -> None:
    """Zero the data pages of each part file (footer kept), so the partition opens but
    its scan fails, as with an unreadable HDFS block."""
    for part in (base / f"adv_load_date={day}").glob("part-*.parquet"):
        data = bytearray(part.read_bytes())
        end = len(data) - 8 - int.from_bytes(data[-8:-4], "little")
        data[4:end] = b"\x00" * (end - 4)
        part.write_bytes(bytes(data))
        part.with_name(f".{part.name}.crc").unlink(missing_ok=True)


def dataset(base: Path, snapshot: str, **kwargs) -> WMSnapshotDataset:
    """The dataset on ``base`` pinned to ``snapshot``."""
    return WMSnapshotDataset(filepath=str(base), snapshot=snapshot, **kwargs)


def last_week(frame) -> int:
    """The latest ``week_number`` in ``frame``."""
    return frame.agg({"week_number": "max"}).first()[0]


def check(name: str, cond: bool) -> None:
    """Print the result; stop on a failure."""
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        sys.exit(1)


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / "fea_x"
    write(root, "2026-08-02", 20260704)
    write(root, "2026-09-02", 20260804)
    write(root, "2026-10-02", 20260904)
    write(root, "2026-11-02", 20261004)
    (root / "_SUCCESS").touch()

    check(
        "order: target, newer nearest first, then older nearest first",
        WMSnapshotDataset.candidates(
            D("2026-09-02"), [D("2026-08-02"), D("2026-10-02"), D("2026-11-02")], 3
        )
        == [D("2026-09-02"), D("2026-10-02"), D("2026-11-02"), D("2026-08-02")],
    )
    check(
        "max_fallback caps the tries",
        len(WMSnapshotDataset.candidates(D("2026-09-02"), [D("2026-08-02")] * 5, 2))
        == 3,
    )

    df = dataset(root, "2026-10-02").load()
    check(
        "healthy target: its rows, no partition column",
        df.columns == ["cif_id", "week_number"] and last_week(df) == 20260904,
    )
    check(
        "missing target: nearest newer partition",
        last_week(dataset(root, "2026-09-15").load()) == 20260904,
    )

    damage(root, "2026-10-02")
    check(
        "damaged partition: opens, but the full scan reports it",
        dataset(root, "2026-10-02")._read(D("2026-10-02"))[1] is not None,
    )
    check(
        "damaged target: newer partition first",
        last_week(dataset(root, "2026-10-02").load()) == 20261004,
    )
    damage(root, "2026-11-02")
    check(
        "damaged target and newer: older partition that covers the run month",
        last_week(dataset(root, "2026-10-02", required_through="2026-08-31").load())
        == 20260804,
    )
    try:
        dataset(root, "2026-10-02", required_through="2026-09-30").load()
        check("only older partitions that stop early: fails", False)
    except DatasetError as err:
        msg = str(err)
        check(
            "only older partitions that stop early: fails with each reason",
            "2026-10-02: " in msg
            and "2026-11-02: " in msg
            and "2026-09-02: weeks end at 20260804" in msg,
        )

    try:
        dataset(root, "2026-08-02", required_from="2026-06-01").load()
        check("partition without the history: fails", False)
    except DatasetError as err:
        check(
            "partition without the history: fails",
            "2026-08-02: weeks start at 20260704, run needs 202606" in str(err),
        )

    try:
        dataset(root, "2026-10-02").save(None)
        check("save refused", False)
    except DatasetError:
        check("save refused", True)
    check("exists", dataset(root, "2026-10-02").exists())
    check(
        "missing root: not exists", not dataset(Path(tmp) / "x", "2026-10-02").exists()
    )

print("all passed")
