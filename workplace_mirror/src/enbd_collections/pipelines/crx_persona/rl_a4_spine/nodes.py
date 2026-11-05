"""RL A4 spine: the persona-window spine rows with their delinquency spell.

Inputs: rl_spine, crx_rl_spell_table, params:crx_persona
Output: crx_rl_a4_spine
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_rl_depart_spine(
    rl_spine: DataFrame,
    crx_rl_spell_table: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Build spell-scoped spine for departure signal computation (Node 0 of 5).

    Mirrors steps 1–4 of build_rl_a4_spine_projection WITHOUT the A4 label join,
    producing the raw spine grain used by all downstream departure nodes.

    Join logic (mirrors join_spine_to_spell pattern from _spine_utils.py):
        rl_spine["account_id"] == t0_table["account_id"]
        AND t0 <= observation_date
        AND spell_end IS NULL (always passes — open spell for RL)

    Args:
        rl_spine:           Model spine at (account_id, observation_date) grain.
        crx_rl_spell_table: T0 anchor. Required cols: account_id, spell_id, t0,
                            t0_censored_flag, spell_end, cif_id.
        crx_persona:        Persona param dict with persona_start_date /
                            persona_end_date.

    Returns:
        DataFrame at (account_id, observation_date) grain with cols::

            cif_id           string  NULL if no active non-censored spell
            account_id       string
            observation_date date
            spell_id         int     NULL if no active spell
            t0               date    NULL if no active spell
    """
    persona_start_date = crx_persona["persona_start_date"]
    persona_end_date = crx_persona["persona_end_date"]

    # Step 1: non-censored active spells (spell_end IS NULL = current episode)
    t0_filtered = crx_rl_spell_table.filter(
        (F.col("t0_censored_flag") == 0) & F.col("spell_end").isNull()
    ).select("account_id", "spell_id", "t0", "spell_end", "cif_id")

    # Step 2: left-join spine to spell info (all spine rows preserved)
    spine_for_join = (
        rl_spine.drop("cif_id") if "cif_id" in rl_spine.columns else rl_spine
    )
    spine_with_t0 = spine_for_join.join(t0_filtered, on="account_id", how="left")

    # Step 3: date filter — t0 <= observation_date (spell_end IS NULL always passes)
    spine_filtered = spine_with_t0.filter(
        F.col("t0").isNull() | (F.col("t0") <= F.col("observation_date"))
    )

    # Step 4: persona window filter
    start_dt = F.to_date(F.lit(persona_start_date))
    end_dt = F.to_date(F.lit(persona_end_date))
    result = spine_filtered.filter(
        (F.col("observation_date") >= start_dt) & (F.col("observation_date") <= end_dt)
    )

    n_rows = result.count()
    n_with_spell = result.filter(F.col("spell_id").isNotNull()).count()
    LOG.info(
        "build_rl_depart_spine [%s → %s]: %d spine rows | with active spell: %d (%.1f%%)",
        persona_start_date,
        persona_end_date,
        n_rows,
        n_with_spell,
        100.0 * n_with_spell / max(n_rows, 1),
    )

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
    )
