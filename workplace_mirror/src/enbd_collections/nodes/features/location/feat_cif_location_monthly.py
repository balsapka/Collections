"""Feature node: location evidence per customer and month.

One row per ``(cif_id, month_end)`` with any evidence, from the primary datasets only:

* ``last_uae_date`` / ``last_uae_source`` — the month's latest evidence that the customer
  was in the UAE: a login from the UAE, in-person card use in the UAE that is not a travel
  purchase;
* ``last_foreign_date`` / ``last_foreign_source`` — the month's latest evidence of being
  abroad: a login from abroad, in-person card use abroad, a collector's departure note;
* ``last_travel_date`` — the month's latest travel purchase (any channel).

Sources: ``login`` (``prm_digital_login_monthly``), ``debit_card``
(``prm_casa_card_transactions``), ``credit_card`` (``prm_transaction``, the model's scoped
cards) and ``dcore_note`` (``dcore_prm_followup_outcomes``). All of a customer's cards and
accounts count. Evidence is dated by day; on a same-day tie between sources the source
name decides, so reruns agree. Online purchases, transfers, incoming money and logins
without a country are not evidence.
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.primary.casa.prm_casa import ATM, IN_PERSON_POS_TYPES, POS
from enbd_collections.nodes.utils.location import is_travel, is_uae

# Debit rows with these reasons are not customer card use (fees, reversals, refunds,
# returns, deleted rows); NULL, '' and 'NA' mean no reason.
_EXCLUDED_REASONS = (
    "CHARGES",
    "FEES",
    "REVERSAL",
    "CANCELLED",
    "RETURNS",
    "CHEQUE RETURNS",
    "DDS Rejects/Reversal",
    "Status Deleted in Finacle",
)
# Merchants paid remotely (digital goods, telecom, direct marketing, software): never in
# person, whatever the terminal type says.
_REMOTE_MCCS = (*range(5815, 5819), 4814, 4816, 4899, *range(5964, 5970), 5734, 7372)
# Credit cards carry no card-present field: in person = cash advances and merchants paid
# at the counter — grocery, fuel, restaurants, pharmacy, transport, department /
# convenience stores.
_IN_PERSON_CREDIT_MCCS = (
    5411, 5422, 5441, 5451, 5462, 5499,
    5541, 5542,
    5812, 5813, 5814,
    5912,
    4111, 4121, 4131,
    5311, 5331,
)  # fmt: skip
_CREDIT_SPEND = ("purchase", "cash")
_DEPARTURE_RESULT_NAMES = (
    "KSA/NATHEER-CROSSING FINAL EXIT VISA",
    "LEFT THE COUNTRY",
    "OUT OF COUNTRY",
)
_EVENT_COLUMNS = ["cif_id", "event_date", "kind", "source"]


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def _events(cif: Column, day: Column, kind: Column, source: str) -> list[Column]:
    return [
        cif.cast("string").alias("cif_id"),
        day.cast("date").alias("event_date"),
        kind.alias("kind"),
        F.lit(source).alias("source"),
    ]


def _login_events(logins: DataFrame, floor: date) -> DataFrame:
    _require(
        logins,
        ["cif_id", "last_uae_login_date", "last_foreign_login_date"],
        "prm_digital_login_monthly",
    )
    uae = logins.select(
        *_events(F.col("cif_id"), F.col("last_uae_login_date"), F.lit("uae"), "login")
    )
    foreign = logins.select(
        *_events(
            F.col("cif_id"), F.col("last_foreign_login_date"), F.lit("foreign"), "login"
        )
    )
    return uae.unionByName(foreign).filter(F.col("event_date") >= F.lit(floor))


def _debit_events(cards: DataFrame) -> DataFrame:
    _require(
        cards,
        [
            "cif_id",
            "tran_date",
            "value_date",
            "channel_desc",
            "merchant_type_desc",
            "reason_for_excluding",
            "merchant_category",
            "merchant_name",
            "tran_narration_1",
            "place_country",
        ],
        "prm_casa_card_transactions",
    )
    channel = F.col("channel_desc")
    remote = F.coalesce(
        F.col("merchant_category").cast("int").isin(*_REMOTE_MCCS), F.lit(False)
    )
    in_person = (
        (channel == POS)
        & F.col("merchant_type_desc").isin(*IN_PERSON_POS_TYPES)
        & ~remote
    ) | (channel == ATM)
    travel = (channel == POS) & is_travel(
        F.col("merchant_category"), F.col("merchant_name"), F.col("tran_narration_1")
    )
    uae = is_uae(F.col("place_country"))
    rows = cards.filter(
        ~F.coalesce(F.trim("reason_for_excluding"), F.lit("")).isin(*_EXCLUDED_REASONS)
    )
    day = F.coalesce(F.col("value_date"), F.col("tran_date"))
    place = F.when(in_person & ~uae, "foreign").when(in_person & uae & ~travel, "uae")
    return rows.select(*_events(F.col("cif_id"), day, place, "debit_card")).unionByName(
        rows.filter(travel).select(
            *_events(F.col("cif_id"), day, F.lit("travel"), "debit_card")
        )
    )


def _credit_events(
    transactions: DataFrame, contracts: DataFrame, clients: DataFrame, floor: date
) -> DataFrame:
    _require(
        transactions,
        [
            "contract_id",
            "observation_date",
            "direction",
            "txn_category",
            "merchant_category_code",
            "is_international",
            "txn_description",
        ],
        "prm_transaction",
    )
    _require(contracts, ["contract_id", "client_id"], "prm_contract")
    _require(clients, ["client_id", "cif_id"], "prm_client")
    cif_of_contract = (
        contracts.select(F.col("contract_id").cast("string"), "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .select("contract_id", "cif_id")
    )
    category = F.col("txn_category")
    mcc = F.col("merchant_category_code")
    in_person = (category == "cash") | F.coalesce(
        mcc.cast("int").isin(*_IN_PERSON_CREDIT_MCCS), F.lit(False)
    )
    travel = (category == "purchase") & is_travel(mcc, F.col("txn_description"))
    abroad = F.col("is_international") == 1
    place = F.when(in_person & abroad, "foreign").when(
        in_person & ~abroad & ~travel, "uae"
    )
    rows = (
        transactions.filter(
            (F.col("direction") == -1)
            & category.isin(*_CREDIT_SPEND)
            & (F.col("observation_date") >= F.lit(floor))
        )
        .withColumn("contract_id", F.col("contract_id").cast("string"))
        .join(cif_of_contract, on="contract_id")
    )
    day = F.col("observation_date")
    return rows.select(
        *_events(F.col("cif_id"), day, place, "credit_card")
    ).unionByName(
        rows.filter(travel).select(
            *_events(F.col("cif_id"), day, F.lit("travel"), "credit_card")
        )
    )


def _departure_notes(
    followup: DataFrame, agreements: DataFrame, floor: date
) -> DataFrame:
    _require(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    _require(agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements")
    notes = followup.filter(
        F.upper(F.trim("result_name")).isin(*_DEPARTURE_RESULT_NAMES)
        & (F.to_date("action_ts") >= F.lit(floor))
    ).select(F.col("agreement_id").cast("string"), "action_ts")
    return notes.join(
        agreements.select("agreement_id", "cif_id").distinct(), on="agreement_id"
    ).select(
        *_events(
            F.col("cif_id"), F.to_date("action_ts"), F.lit("foreign"), "dcore_note"
        )
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    logins: DataFrame,
    casa_cards: DataFrame,
    transactions: DataFrame,
    contracts: DataFrame,
    clients: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Location evidence per ``(cif_id, month_end)`` from the first day of the last
    ``history_months`` months up to the persona start month (``prm_casa_card_transactions``
    keeps its own history)."""
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
    events = (
        _login_events(logins, floor)
        .unionByName(_debit_events(casa_cards))
        .unionByName(_credit_events(transactions, contracts, clients, floor))
        .unionByName(_departure_notes(followup, agreements, floor))
        .select(*_EVENT_COLUMNS)
        .filter(
            F.col("cif_id").isNotNull()
            & F.col("event_date").isNotNull()
            & F.col("kind").isNotNull()
        )
    )

    def latest(kind: str) -> Column:
        return F.max(F.when(F.col("kind") == kind, F.struct("event_date", "source")))

    return (
        events.groupBy("cif_id", F.last_day("event_date").alias("month_end"))
        .agg(
            latest("uae").alias("_uae"),
            latest("foreign").alias("_foreign"),
            F.max(F.when(F.col("kind") == "travel", F.col("event_date"))).alias(
                "last_travel_date"
            ),
        )
        .select(
            "cif_id",
            "month_end",
            F.col("_uae.event_date").alias("last_uae_date"),
            F.col("_uae.source").alias("last_uae_source"),
            F.col("_foreign.event_date").alias("last_foreign_date"),
            F.col("_foreign.source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )
