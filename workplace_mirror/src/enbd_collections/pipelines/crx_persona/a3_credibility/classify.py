"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    deadline: str,
    persona_end_date: str,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off. Unknown:
    no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode with no
    evidence scores 0 points and is Low.
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn("a3_promise_deadline", F.lit(deadline))
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", "A3 credibility", persona_end_date)
    return out
