"""TEMPORARY (refactor bundle R-A): the moved ``build_rl_depart_spine`` must rebuild
``crx_rl_a4_spine`` exactly. Logs one block; removed by the bundle's cleanup."""

import logging

from pyspark.sql import DataFrame

logger = logging.getLogger(__name__)


def compare_rl_a4_spine(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Row counts, schema and rows in one output but not the other (``exceptAll``)."""
    same_schema = old.schema.simpleString() == new.schema.simpleString()
    cols = old.columns
    lines = [
        f"model_id: {model_id}",
        f"rows old / new: {old.count()} / {new.count()}",
        f"same schema: {same_schema}",
    ]
    if same_schema:
        lines += [
            f"rows only in old: {old.exceptAll(new.select(*cols)).count()}",
            f"rows only in new: {new.select(*cols).exceptAll(old).count()}",
        ]
    else:
        lines += [
            f"old: {old.schema.simpleString()}",
            f"new: {new.schema.simpleString()}",
        ]
    block = "\n".join(lines)
    logger.info(
        "\n=== RA SPINE OUTPUT START ===\n%s\n=== RA SPINE OUTPUT END ===", block
    )
