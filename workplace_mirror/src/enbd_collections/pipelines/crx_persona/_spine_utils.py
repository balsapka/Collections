"""Shared spine and CIF utilities for crx_persona pipelines.

Used by: cc_a1_ability, cc_a2_locatability, cc_a3_payment_credibility,
rl_a3_payment_credibility.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def join_spine_to_spell(cc_spine: DataFrame, spell_table: DataFrame) -> DataFrame:
    """Join cc_spine to crx_cc_spell_table to obtain spell window columns.

    Uses an equality-only join on ``contract_id == account_id`` so Spark can
    plan a hash/sort-merge join, then applies date-range filters as separate
    post-join steps.  This is more efficient than embedding the date conditions
    inside the ``on=`` clause (which forces a cross-join-with-filter plan).

    Left join preserves all spine rows; spell columns are NULL for spine points
    with no active spell at that observation_date (e.g. new accounts added to
    the spine before the spell table is regenerated).

    Args:
        cc_spine:    Model-id-scoped spine; required cols: contract_id,
            observation_date.
        spell_table: crx_cc_spell_table; required cols: account_id, spell_id,
            t0, spell_end.

    Returns:
        DataFrame with columns:
            account_id       (string)  — alias of contract_id
            observation_date (date)
            spell_id         (int)     — NULL if no active spell
            t0               (date)    — NULL if no active spell
    """
    spine = cc_spine.alias("spine")
    spell = spell_table.select("account_id", "spell_id", "t0", "spell_end").alias(
        "spell"
    )
    return (
        spine.join(
            spell,
            on=F.col("spine.contract_id") == F.col("spell.account_id"),
            how="left",
        )
        .filter(
            F.col("spell.t0").isNull()
            | (F.col("spell.t0") <= F.col("spine.observation_date"))
        )
        .filter(
            F.col("spell.spell_end").isNull()
            | (F.col("spine.observation_date") <= F.col("spell.spell_end"))
        )
        .select(
            F.col("spine.contract_id").alias("account_id"),
            F.col("spine.observation_date"),
            F.col("spell.spell_id"),
            F.col("spell.t0"),
        )
    )


def _build_cif_bridge(contract: DataFrame, client: DataFrame) -> DataFrame:
    """Two-hop bridge: contract_id → cif_id.

    prm_contract holds the link between account/contract numbers and the
    customer CIF.  prm_client carries the canonical cif_id field.

    Returns DataFrame with columns: (contract_id, cif_id).
    """
    return (
        contract.select("contract_id", "client_id")
        .join(
            client.select("client_id", "cif_id"),
            on="client_id",
            how="inner",
        )
        .select("contract_id", "cif_id")
        .dropDuplicates(["contract_id"])
    )


def rl_spine_as_cc_shim(rl_a4_spine: DataFrame) -> "tuple[DataFrame, DataFrame]":
    """Reshape an RL spine into the (cc_spine, spell_table) column contract.

    CC build functions such as build_a3_commitment_signals take a cc_spine +
    spell_table pair and call join_spine_to_spell() internally, which hard-codes
    cc_spine["contract_id"] == spell_table["account_id"]. RL spines use
    account_id (not contract_id) and already carry a broadcast spell_id/t0 per
    row — resolved once when crx_rl_a4_spine was built — rather than a separate
    spell table. This derives both shapes from that single spine so the CC
    function can run completely unchanged (R14 reuse / R18 additive — no CC
    code touched).

    Args:
        rl_a4_spine: RL spine already joined to its T0/spell window — e.g.
            crx_rl_a4_spine. Required cols: account_id, observation_date,
            cif_id, spell_id, t0.

    Returns:
        Tuple of:
            cc_spine_shim:    (contract_id, observation_date, cif_id) — one row
                per rl_a4_spine row.
            spell_table_shim: (account_id, spell_id, t0, spell_end) — one row
                per (account_id, spell_id); spell_end is always NULL (RL has no
                closed-spell concept at this grain — join_spine_to_spell only
                needs t0 <= observation_date, which NULL spell_end satisfies).
    """
    cc_spine_shim = rl_a4_spine.select(
        F.col("account_id").alias("contract_id"),
        F.col("observation_date"),
        F.col("cif_id"),
    )
    spell_table_shim = (
        rl_a4_spine.select("account_id", "spell_id", "t0")
        .where(F.col("spell_id").isNotNull())
        .dropDuplicates(["account_id", "spell_id"])
        .withColumn("spell_end", F.lit(None).cast("date"))
    )
    return cc_spine_shim, spell_table_shim
