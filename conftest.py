"""Pytest bootstrap: make both import roots resolvable and share one Spark session.

The library is imported as ``collections_spine`` (src on path) while the node
modules import ``src.collections_spine`` (repo root on path) -- add both so either
style resolves under pytest.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent
for _p in (_ROOT, _ROOT / "src"):
    _sp = str(_p)
    if _sp not in sys.path:
        sys.path.insert(0, _sp)


@pytest.fixture(scope="session")
def spark():
    pytest.importorskip("pyspark")
    from pyspark.sql import SparkSession

    session = (
        SparkSession.builder.master("local[2]")
        .appName("collections_spine-tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()
