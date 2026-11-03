"""RL-native Dimension B window resolver for rl_a3_payment_credibility.

Dimension C's window resolver needs no RL-native rebuild – CC's
resolve_pre_dlq_spell_window (cc_a3_payment_credibility._signals_common)
only needs account_id/observation_date/spell_id/t0/spell_end, no CC-bucket
-specific column, so it is reused unchanged via rl_spine_as_cc_shim() in
nodes.py directly. Only Dimension B's window resolver needs a rebuild here
because CC's resolve_dlq_payment_window reads cc_spine.dlq_bucket_from_hist
(a column rl_spine_as_cc_shim's cc_spine_shim does not carry) and its 3mo/6mo
split threshold is a CC-bucket-numeral that does not translate literally to
RL's 0-7 scale.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import (
    join_spine_to_spell,
    rl_spine_as_cc_shim,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility.constants import (
    _DLQ_WINDOW_SPLIT_THRESHOLD_RL,
    _TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID,
)


def resolve_rl_dlq_payment_window(
    crx_rl_a4_spine: DataFrame,
    crx_rl_a3_dlq_cycles: DataFrame,
) -> DataFrame:
    """RL-native rebuild of cc_a3_payment_credibility._signals_common
    .resolve_dlq_payment_window.

    Reuses join_spine_to_spell (via rl_spine_as_cc_shim) unchanged for the
    account/spell/t0 join – only the window-length decision itself is new.
    No separate spell-table input is needed (unlike CC's
    resolve_dlq_payment_window, which takes crx_cc_spell_table): RL's
    crx_rl_a4_spine already carries spell_id/t0 directly, and
    rl_spine_as_cc_shim derives both shim halves from it alone. Current
    dlq_bucket is read from crx_rl_a3_dlq_cycles' dlq_level_m at
    (account_id, billing_date == observation_date), not from the spine
    (rl_spine_as_cc_shim's cc_spine_shim carries no bucket column).

    Window-depth split at _DLQ_WINDOW_SPLIT_THRESHOLD_RL (7, RL's single
    terminal 180+ bucket) – see constants.py for why this is not a literal
    copy of CC's ">= 8" threshold.

    Args:
        crx_rl_a4_spine: RL spine – (account_id, observation_date, spell_id, t0).
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output – (account_id,
            billing_date, dlq_level_m).

    Returns:
        DataFrame with (account_id, observation_date, t0, _window_months,
        _window_start, _any_window_months, _any_window_start, _min_payment_aed (100 in
        the deep band, else 0). The "any payment"
        window (Some vs None, strong negatives) is 12 months in the deep band, the
        regular window elsewhere; "Regular" keeps _window_*.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spine_with_spell = join_spine_to_spell(cc_spine_shim, spell_table_shim)

    current_bucket = crx_rl_a3_dlq_cycles.select(
        F.col("account_id"),
        F.col("billing_date").alias("observation_date"),
        F.col("dlq_level_m").alias("_current_dlq_bucket"),
    )

    spine_with_dlq = spine_with_spell.join(
        current_bucket, on=["account_id", "observation_date"], how="left"
    )

    is_deep = F.col("_current_dlq_bucket") >= _DLQ_WINDOW_SPLIT_THRESHOLD_RL

    def _window_start(months_col):
        return F.greatest(
            F.col("t0"),
            F.add_months(F.col("observation_date"), -months_col),
        )

    return (
        spine_with_dlq.withColumn(
            "_window_months",
            F.when(is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP)).otherwise(
                F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID)
            ),
        )
        .withColumn(
            "_any_window_months",
            F.when(
                is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP)
            ).otherwise(F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID)),
        )
        .withColumn("_window_start", _window_start(F.col("_window_months")))
        .withColumn("_any_window_start", _window_start(F.col("_any_window_months")))
        .withColumn(
            "_min_payment_aed",
            F.when(is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP)).otherwise(
                F.lit(0.0)
            ),
        )
    )
