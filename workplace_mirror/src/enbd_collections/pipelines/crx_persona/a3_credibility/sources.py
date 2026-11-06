"""A3 source nodes shared by both products: the episode anchor, the cycle ledger and
the DCORE promise instalments."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)

from .._common import GRAIN, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start

DUES = ["account_id", "cycle_start", "cycle_end", "due_amount", "billed_amount"]
PAYMENTS = ["account_id", "pay_from", "pay_date", "amount"]


def build_a3_episode(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for every base row (D-A3-2).

    ``episode_start`` is the first day of the month the current delinquency episode
    began, from A4 as of the observation date; NULL when A4 did not score the row (A3
    then reads Unknown, reason ``no_episode``, Q-12).
    """
    return obs_base.select(*GRAIN, "cif_id").join(
        episode_start(obs_base, deterioration), on=list(GRAIN), how="left"
    )


def build_cycle_ledger(dues: DataFrame, payments: DataFrame) -> DataFrame:
    """One row per account cycle: ``DUES`` + ``paid_amount``, the payments with
    ``cycle_start < pay_date <= cycle_end`` (paid before the next statement, D-A3-8).

    ``dues`` and ``payments`` follow the product contracts ``DUES`` / ``PAYMENTS``
    (CC: statement cycles and card payments; RL: months and the month's cash).
    """
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    paid = (
        dues.select("account_id", "cycle_start", "cycle_end")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(
            (F.col("pay_date") > F.col("cycle_start"))
            & (F.col("pay_date") <= F.col("cycle_end"))
        )
        .groupBy("account_id", "cycle_end")
        .agg(F.sum("amount").alias("paid_amount"))
    )
    return (
        dues.select(*DUES)
        .join(paid, on=["account_id", "cycle_end"], how="left")
        .withColumn("paid_amount", F.coalesce(F.col("paid_amount"), F.lit(0.0)))
    )


def build_instalments(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> DataFrame:
    """PTP and settlement instalments of the base's accounts (D-A3-7, D-A3-9).

    One row per instalment of a non-cancelled plan: ``account_id``, ``plan_id``,
    ``plan_type``, ``plan_start`` (PTP: promise start, else event date; settlement: event
    date, the only date DCORE keeps), ``due_date``, ``due_amount``, ``payment_amount``
    (DCORE's). Cancelled instalments are nulled by DCORE's own rule and dropped.
    """
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    require_columns(
        int_ptp,
        [
            "agreement_id",
            "promise_seqno",
            "promise_start",
            "event_date",
            "is_cancelled",
        ],
        "dcore_int_ptp",
    )
    require_columns(
        int_settlement,
        ["agreement_id", "rps_seqno", "event_date", "is_cancelled"],
        "dcore_int_settlement",
    )
    cols = ["due_date", "due_amount", "payment_amount", "instalment_status"]
    require_columns(
        ptp_instalments, ["promise_seqno", *cols], "dcore_prm_promise_instalments"
    )
    require_columns(
        settlement_instalments,
        ["rps_seqno", *cols],
        "dcore_prm_settlement_schedule_instalments",
    )
    links = scoped(
        agreements.select(
            string_key(agreements).alias("account_id"),
            F.col("agreement_id").cast("string").alias("agreement_id"),
        ),
        obs_base,
        "account_id",
    )

    def plans(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        plan: DataFrame, seq: str, start, kind: str, rows: DataFrame, cancelled
    ) -> DataFrame:
        live = plan.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            seq,
            F.concat_ws(":", F.lit(kind), F.col(seq).cast("string")).alias("plan_id"),
            F.lit(kind).alias("plan_type"),
            start.cast("date").alias("plan_start"),
        )
        return null_cancelled_instalment_fields(
            live.join(rows.select(seq, *cols), on=seq), cancelled
        ).drop(seq)

    ptp = plans(
        int_ptp,
        "promise_seqno",
        F.coalesce(F.col("promise_start"), F.col("event_date")),
        "ptp",
        ptp_instalments,
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = plans(
        int_settlement,
        "rps_seqno",
        F.col("event_date"),
        "settlement",
        settlement_instalments,
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    return (
        ptp.unionByName(settlement)
        .join(F.broadcast(links), on="agreement_id")
        .where(F.col("due_date").isNotNull())
        .select(
            "account_id",
            "plan_id",
            "plan_type",
            "plan_start",
            F.col("due_date").cast("date").alias("due_date"),
            F.col("due_amount").cast("double").alias("due_amount"),
            F.col("payment_amount").cast("double").alias("payment_amount"),
        )
    )
