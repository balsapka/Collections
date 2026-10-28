"""Primary node: the account → DCORE agreement map of the model's collections scope.

``dcore_observation_spine`` carries the map on the spine's (billing) dates; here the
dates are dropped, so every DCORE event of an agreement can be read up to any
observation date. One agreement per account holds in PROD (A2 v01); the table keeps
whatever pairs the spine has.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

_COLUMNS = ["account_id", "agreement_id", "cif_id"]


def build(dcore_observation_spine: DataFrame) -> DataFrame:
    """Distinct ``(account_id, agreement_id, cif_id)``, ids as strings."""
    missing = sorted(set(_COLUMNS) - set(dcore_observation_spine.columns))
    if missing:
        raise ValueError(f"dcore_observation_spine is missing columns: {missing}")
    return (
        dcore_observation_spine.select(
            *[F.col(c).cast("string").alias(c) for c in _COLUMNS]
        )
        .filter(F.col("account_id").isNotNull() & F.col("agreement_id").isNotNull())
        .distinct()
    )
