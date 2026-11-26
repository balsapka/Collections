"""Master end-to-end persona pipelines, one per ``model_id``.

Chains every upstream data domain the persona axes read, then obs_base, the
full DPD history, A4, A1, A2 and A3 (CC also runs ``cc_raw_extract``), so one
run leaves all persona outputs ready.

Registered as ``<model_id>.persona_e2e``: the part before the first dot is what
``ModelConfigHook`` uses to set ``model_id`` (DLQ range, HDFS paths).

    kedro run --env=dev --pipeline=cc_60_180.persona_e2e

RL masters also run the CC Way4 staging and primary scoped to RL customers,
because A2 and the location features read ``prm_client``, ``prm_contract`` and
``prm_transaction``.

Left out on purpose: target builders, UC1 (needs external datasets with no
producer), ``casa_windows*``, ``cc_dpl*``, ``cc_way4_features``.
"""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import bureau, digital_login, demographics
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_a4_deterioration,
    cc_full_history,
    cc_raw_extract,
    obs_base,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
    rl_full_history,
)
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm
from enbd_collections.pipelines.retail_loans import features as rl_feat
from enbd_collections.pipelines.retail_loans import intermediate as rl_int
from enbd_collections.pipelines.retail_loans import primary as rl_prm
from enbd_collections.pipelines.retail_loans import spine as rl_spine
from enbd_collections.pipelines.retail_loans import staging as rl_stg

_RL_SCOPED_CIF_SPINE_NODE = "build_data_spine_cifs_rl_scoped"


def _shared_domains(cif_obs_spine: str) -> Pipeline:
    """Upstream domains both products read (DCORE, CASA, products, bureau, ...)."""
    return (
        dcore_stg.create_pipeline()
        + dcore_prm.create_pipeline()
        + dcore_int.create_pipeline()
        + casa_prm.create_pipeline()
        + casa_feat.create_pipeline()
        + products_prm.create_pipeline()
        + products_feat.create_pipeline()
        + bureau.create_pipeline()
        + bureau_salary_bounces.create_pipeline()
        + digital_login.create_pipeline()
        + location_features.create_pipeline()
        + demographics.create_pipeline(cif_obs_spine=cif_obs_spine)
    )


def _cc_way4_for_rl() -> Pipeline:
    """CC Way4 staging and primary scoped to the RL customers (A2 reads them).

    Same as the standalone ``rl_*.cc_scope`` scope, staging and primary, minus
    ``data_spine_cifs``, which the RL spine already produces in the same run.
    """
    scope = cc_way4_spine.create_rl_scoped_scope_pipeline()
    return (
        Pipeline([n for n in scope.nodes if n.name != _RL_SCOPED_CIF_SPINE_NODE])
        + cc_way4_stg.create_pipeline()
        + cc_way4_prm.create_pipeline()
    )


def create_cc_pipeline(spine: Pipeline) -> Pipeline:
    """Credit-card master: Way4 spine and domain, shared domains, persona axes."""
    return (
        spine
        + cc_way4_stg.create_pipeline()
        + cc_way4_prm.create_pipeline()
        + _shared_domains("cc_cif_obs_spine")
        + obs_base.create_cc_pipeline()
        + cc_full_history.create_pipeline()
        + cc_a4_deterioration.create_pipeline()
        + cc_raw_extract.create_pipeline()
        + cc_a1_ability.create_pipeline()
        + cc_a2_locatability.create_pipeline()
        + cc_a3_payment_credibility.create_pipeline()
    )


def create_rl_pipeline(spine: Pipeline, features: Pipeline) -> Pipeline:
    """Retail-loans master: RL spine and domain, shared domains, persona axes."""
    return (
        spine
        + rl_stg.create_pipeline()
        + rl_prm.create_pipeline()
        + rl_int.create_pipeline()
        + features
        + _cc_way4_for_rl()
        + _shared_domains("rl_cif_obs_spine")
        + obs_base.create_rl_pipeline()
        + rl_full_history.create_pipeline()
        + rl_a4_deterioration.create_pipeline()
        + rl_a1_ability.create_pipeline()
        + rl_a2_locatability.create_pipeline()
        + rl_a3_payment_credibility.create_pipeline()
    )


def create_cc_60_180_pipeline() -> Pipeline:
    """Master for ``cc_60_180``."""
    return create_cc_pipeline(cc_way4_spine.create_pipeline())


def create_cc_180_plus_pipeline() -> Pipeline:
    """Master for ``cc_180_plus``."""
    return create_cc_pipeline(cc_way4_spine.create_180_plus_pipeline())


def create_rl_60_180_pipeline() -> Pipeline:
    """Master for ``rl_60_180``."""
    return create_rl_pipeline(rl_spine.create_pipeline(), rl_feat.create_pipeline())


def create_rl_180_plus_pipeline() -> Pipeline:
    """Master for ``rl_180_plus``."""
    return create_rl_pipeline(
        rl_spine.create_180_plus_pipeline(), rl_feat.create_rl_180_plus_pipeline()
    )
