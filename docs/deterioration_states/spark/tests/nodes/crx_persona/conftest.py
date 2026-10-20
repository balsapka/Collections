"""Local SparkSession for the crx_persona node tests (synthetic data only, no catalog).

If src/tests already provides a session-scoped `spark` fixture, delete this file and the
tests use that one. Needs Java 8/11/17 on the machine (JAVA_HOME) and pyspark >= 3.3.
"""
import os
import sys

import pytest


@pytest.fixture(scope="session")
def spark():
    from pyspark.sql import SparkSession

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    session = (
        SparkSession.builder.master("local[2]")
        .appName("crx_persona_tests")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")      # the strictest setting (Spark 4 default)
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
