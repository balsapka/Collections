"""DLQ contract-spine pipeline.

Wires the selectivity-first node chain in
``src/collections_spine/nodes/spine_builders.py`` into a Kedro pipeline. Register
it in your project's ``pipeline_registry.py`` (see this package's README), e.g.::

    from src.collections_spine.pipelines.dlq_spine import create_pipeline as dlq_spine

    def register_pipelines():
        dlq = dlq_spine()
        return {"dlq_spine": dlq, "__default__": dlq}
"""

from kedro.pipeline import Pipeline, node, pipeline

from src.collections_spine.nodes.spine_builders import (
    build_billing_spine,
    contract_pit,
    dlq_candidate_ids,
    dlq_spine,
    slim_contract,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=slim_contract,
                inputs=["raw_stg_contract", "params:modelling"],
                outputs="contract_slim",
                name="slim_contract",
            ),
            node(
                func=dlq_candidate_ids,
                inputs=["contract_slim", "params:modelling"],
                outputs="dlq_candidate_ids",
                name="dlq_candidate_ids",
            ),
            node(
                func=build_billing_spine,
                inputs=["raw_stg_billing", "dlq_candidate_ids", "params:modelling"],
                outputs="billing_spine",
                name="build_billing_spine",
            ),
            node(
                func=contract_pit,
                inputs=["contract_slim", "billing_spine", "params:modelling"],
                outputs="contract_pit",
                name="contract_pit",
            ),
            node(
                func=dlq_spine,
                inputs=["contract_pit", "params:modelling"],
                outputs="dlq_spine",
                name="dlq_spine",
            ),
        ],
        tags="dlq_spine",
    )
