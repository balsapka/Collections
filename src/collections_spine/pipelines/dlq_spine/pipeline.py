"""DLQ contract-spine pipeline.

Reproduces the final dataset of the old ``build_contract_spine`` -- a distinct
``(contract_idt, observation_date, cif_id, dlq_bucket_from_hist)`` spine -- via
the selectivity-first node chain in
``src/collections_spine/nodes/spine_builders.py``.

Progressive narrowing: DLQ band -> product scope -> collateral scope -> client
enrichment, with two spine-driven staging builds (contract attributes, client)
hanging off the narrowed spine. Register it in ``pipeline_registry.py``::

    from src.collections_spine.pipelines.dlq_spine import create_pipeline as dlq_spine

    def register_pipelines():
        p = dlq_spine()
        return {"dlq_spine": p, "__default__": p}
"""

from kedro.pipeline import Pipeline, node, pipeline

from src.collections_spine.nodes.spine_builders import (
    apply_collateral,
    build_billing_spine,
    build_client_spine,
    contract_dlq,
    contract_pit,
    dlq_candidate_ids,
    dlq_spine,
    enrich_product,
    finalize_contract_spine,
    slim_contract,
    stage_client,
    stage_contract_attribute,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # --- spine foundation -------------------------------------------
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
            # --- DLQ scope --------------------------------------------------
            node(
                func=contract_dlq,
                inputs=["contract_pit", "params:modelling"],
                outputs="contract_dlq",
                name="contract_dlq",
            ),
            node(
                func=dlq_spine,
                inputs="contract_dlq",
                outputs="dlq_spine",
                name="dlq_spine",
            ),
            # --- product scope ----------------------------------------------
            node(
                func=enrich_product,
                inputs=["contract_dlq", "raw_stg_product_config", "params:modelling"],
                outputs="product_enriched",
                name="enrich_product",
            ),
            # --- collateral scope (spine-driven attribute build) ------------
            node(
                func=stage_contract_attribute,
                inputs=["raw_stg_contract_attribute", "dlq_spine"],
                outputs="contract_attribute_pivoted",
                name="stage_contract_attribute",
            ),
            node(
                func=apply_collateral,
                inputs=["product_enriched", "contract_attribute_pivoted", "params:modelling"],
                outputs="collateral_scoped",
                name="apply_collateral",
            ),
            # --- client enrichment (spine-driven client build) --------------
            node(
                func=build_client_spine,
                inputs="collateral_scoped",
                outputs="client_spine",
                name="build_client_spine",
            ),
            node(
                func=stage_client,
                inputs=["raw_stg_client", "client_spine"],
                outputs="client_staged",
                name="stage_client",
            ),
            node(
                func=finalize_contract_spine,
                inputs=["collateral_scoped", "client_staged"],
                outputs="contract_spine",
                name="finalize_contract_spine",
            ),
        ],
        tags="dlq_spine",
    )
