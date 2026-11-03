"""Shared payment-attribution and due-amount helpers for A3 Dimension B and C.

Both dimensions need to know, per billing cycle, how much the customer paid,
whether it arrived by the due date, and how much was actually due that cycle –
factored once here so build_a3_dlq_payment_signals_payment_sum_waterfall (post-onset, "payments in
delinquency") and build_a3_pre_dlq_payment_signals_single_payment_cycle_count (pre-onset, "record
before
delinquency") reuse identical logic instead of diverging.

Naming mirrors the existing pipeline-local shared module
crx_persona/_spine_utils.py.
"""

# pylint: disable=too-many-lines

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    instalment_amount_flags,
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from enbd_collections.pipelines.crx_persona._spine_utils import join_spine_to_spell
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _PAYMENT_CYCLE_FLOOR_LOOKBACK_D,
    _PAYMENT_CYCLE_MAX_LENGTH_D,
    _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
    _TAU_A3V2_COMMITMENTS_WINDOW_M,
    _TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS,
    _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS,
    _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    _TAU_A3V2_PRE_DLQ_WINDOW_M,
)


def _floor_column(history_floor_date):
    """The history floor as a date literal, or None when no floor is set."""
    return F.lit(str(history_floor_date)).cast("date") if history_floor_date else None


def resolve_dlq_payment_window(
    cc_spine: DataFrame,
    crx_cc_spell_table: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """DLQ-depth-dependent payment-evidence window, shared by both Dimension
    B methods (build_a3_dlq_payment_signals_payment_sum_waterfall / _dpd) – pure extraction of a
    block that was duplicated near-verbatim between the two, no behavior
    change (2026-10-21).

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): the
    window never starts before it. Never binding for observation dates a few
    months past the floor; a guard that keeps the rule explicit.

    Two windows: the "Regular" window (_window_months / _window_start: 3 months at
    61-180 DPD, 6 at 180+) and the "any payment" window (_any_window_months /
    _any_window_start: same at 61-180, 12 months at 180+) used for Some vs None
    and the strong negatives. _any_window_start <= _window_start.

    _min_payment_aed: 100 at 180+ DPD, else 0 – the minimum payment for a cycle to
    qualify / a payment to count (see payment_meets_floor).

    Returns:
        DataFrame with (account_id, observation_date, t0, dlq_bucket_from_hist,
        _window_months, _window_start, _any_window_months, _any_window_start,
        _min_payment_aed).
    """
    spine_with_spell = join_spine_to_spell(cc_spine, crx_cc_spell_table)

    spine_with_dlq = spine_with_spell.join(
        cc_spine.select(
            F.col("contract_id").alias("account_id"),
            "observation_date",
            "dlq_bucket_from_hist",
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    floor = _floor_column(history_floor_date)

    def _window_start(months_col):
        starts = [F.col("t0"), F.add_months(F.col("observation_date"), -months_col)]
        if floor is not None:
            starts.append(floor)
        return F.greatest(*starts)

    is_180_plus = F.col("dlq_bucket_from_hist") >= 8
    return (
        spine_with_dlq.withColumn(
            "_window_months",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS)
            ).otherwise(F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180)),
        )
        .withColumn(
            "_any_window_months",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS)
            ).otherwise(F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180)),
        )
        .withColumn("_window_start", _window_start(F.col("_window_months")))
        .withColumn("_any_window_start", _window_start(F.col("_any_window_months")))
        .withColumn(
            "_min_payment_aed",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS)
            ).otherwise(F.lit(0.0)),
        )
    )


def payment_meets_floor(payment_col):
    """Boolean: the payment reaches the spine row's minimum payment (``s._min_payment_aed``:
    100 AED at 180+ DPD, 0 otherwise = no floor). For use inside aggregate_dlq_window
    expressions, where the spine row is the ``s`` alias."""
    return (F.col("s._min_payment_aed") <= 0) | (
        payment_col >= F.col("s._min_payment_aed")
    )


def resolve_dpd_bucket_movement_history(
    crx_cc_full_history: DataFrame, history_floor_date: str = None
) -> DataFrame:
    """Per-cycle dlq_level_m + its lag (dlq_level_prev_m), shared by both Dimension
    B and C's dpd_bucket_movement methods (build_a3_dlq_payment_signals_dpd_bucket_movement /
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement).

    Sourced from crx_cc_full_history – the full, floor-free account history – rather
    than crx_cc_billing (windowed via crx_cc_acct_windows, floored at
    min(t0) - 12 months). Same BS_PMT_CYCLE_DUE ground truth as crx_cc_billing.dlq_level_m
    (confirmed identical extraction field), but unbounded, so even the very first
    post-onset row has a genuine previous cycle to compare against instead of a NULL
    lag at the edge of the 12-month window.

    A lag, not a lead (2026-10-26 fix): a billing statement's own bucket numbers
    already reflect whatever cash arrived since the PREVIOUS statement – confirmed by
    hand-reconciling a real account's billing/balance history (logs/dim_c_validation.log,
    Scenario 2): a payment "labeled" on a given billing_date has zero visible effect on
    that same row's own past_due_amount (which keeps growing by the usual monthly
    charge), and only reconciles exactly against the NEXT row once that payment is
    subtracted. So "did this row's bucket improve" must compare this row's own
    dlq_level_m against the PRIOR row's (dlq_level_prev_m) – comparing against the next
    row instead (the pre-fix behavior) attaches the evidence of a transition to the row
    one cycle before the one whose own ledger state actually shows it.

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): rows
    before it are dropped BEFORE the lag, so the first in-window statement has a
    NULL previous level (no credit) and is never compared with a statement from
    before the 2021-2023 billing gap. crx_cc_full_history itself stays unfloored.

    Args:
        crx_cc_full_history: account_id, billing_date, dlq_bucket (int, nullable).
        history_floor_date: ISO date or None.

    Returns:
        DataFrame with (account_id, billing_date, dlq_level_m, dlq_level_prev_m).
    """
    history = crx_cc_full_history.select(
        "account_id", "billing_date", F.col("dlq_bucket").alias("dlq_level_m")
    )
    floor = _floor_column(history_floor_date)
    if floor is not None:
        history = history.where(F.col("billing_date") >= floor)
    w_account_history = Window.partitionBy("account_id").orderBy("billing_date")
    return history.withColumn(
        "dlq_level_prev_m", F.lag("dlq_level_m").over(w_account_history)
    )


def resolve_pre_dlq_spell_window(
    cc_spine: DataFrame,
    crx_cc_spell_table: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Pre-onset 12-month window, population-filtered to spells active in
    cc_spine – shared by both Dimension C methods
    (build_a3_pre_dlq_payment_signals_single_payment_cycle_count
    / _dpd) – pure extraction of a block that was duplicated near-verbatim
    between the two, no behavior change (2026-10-21).

    The spell is the one active at the observation date (join_spine_to_spell), so
    an account with an old cured spell and a newer one uses the newer one.

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): the
    window never starts before it. A spell whose T0 is before the floor therefore
    gets a start after T0, matches no cycles and reads as "no record"; T0 shortly
    after the floor keeps only the in-floor months. Other callers (RL) leave it
    None and are unchanged.

    Returns:
        DataFrame with (account_id, spell_id, t0, _window_start).
    """
    active_spells = (
        join_spine_to_spell(cc_spine, crx_cc_spell_table)
        .select("account_id", "t0")
        .where(F.col("t0").isNotNull())
        .distinct()
    )

    window_start = F.add_months(F.col("t0"), -_TAU_A3V2_PRE_DLQ_WINDOW_M)
    floor = _floor_column(history_floor_date)
    if floor is not None:
        window_start = F.greatest(window_start, floor)

    return (
        crx_cc_spell_table.select("account_id", "spell_id", "t0")
        .join(active_spells, on=["account_id", "t0"], how="inner")
        .withColumn("_window_start", window_start)
    )


def attribute_payments_to_billing_cycles(
    billing: DataFrame, transactions: DataFrame
) -> DataFrame:
    """Attribute payment transactions to the billing cycle they land in.

    Cycle attribution uses billing_date < banking_date <= next_billing_date – NOT
    due_date – because due_date (~billing_date+25d) falls short of the next
    statement cut (~billing_date+30d), leaving a ~5-6 day dead zone where late
    payments would otherwise be dropped or misattributed to the wrong cycle.
    This was found and fixed in the exploratory notebook
    (notebooks/data_engineering/crx_cc_account_payment_profiling.ipynb).
    due_date is used only for the separate on_time_payment_sum_in_cycle check.

    Excludes is_post_block_x_fee (Block-W sentinel-date fee-accrual artifacts)
    and anything not categorised "payment" via TXN_CATEGORIES.

    Args:
        billing: crx_cc_billing. Required cols: contract_id, observation_date
            (billing_date), due_date, next_billing_date.
        transactions: crx_cc_transactions. Required cols: contract_id,
            observation_date (banking_date), txn_amount_aed, txn_category,
            is_post_block_x_fee.

    Returns:
        DataFrame at grain (contract_id, billing_date, due_date,
        next_billing_date) with:
            payment_sum_in_cycle (double)         – total payment in the cycle.
            on_time_payment_sum_in_cycle (double) – payment with banking_date
                                                    <= due_date only.
    """
    billing_cycles = billing.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
    )

    payments = transactions.filter(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        F.col("contract_id"),
        F.col("observation_date").alias("banking_date"),
        F.col("txn_amount_aed"),
    )

    attributed = billing_cycles.alias("b").join(
        payments.alias("p"),
        (F.col("b.contract_id") == F.col("p.contract_id"))
        & (F.col("p.banking_date") > F.col("b.billing_date"))
        & (
            F.col("b.next_billing_date").isNull()
            | (F.col("p.banking_date") <= F.col("b.next_billing_date"))
        ),
        "left",
    )

    return attributed.groupBy(
        F.col("b.contract_id").alias("contract_id"),
        F.col("b.billing_date").alias("billing_date"),
        F.col("b.due_date").alias("due_date"),
        F.col("b.next_billing_date").alias("next_billing_date"),
    ).agg(
        F.coalesce(F.sum("p.txn_amount_aed"), F.lit(0.0)).alias("payment_sum_in_cycle"),
        F.coalesce(
            F.sum(
                F.when(
                    F.col("p.banking_date") <= F.col("b.due_date"),
                    F.col("p.txn_amount_aed"),
                )
            ),
            F.lit(0.0),
        ).alias("on_time_payment_sum_in_cycle"),
    )


_QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST = [
    f"overdue_bucket_0{i}" for i in range(7, 0, -1)
]
# bucket_08 is NOT in this list – it is decomposed into synthetic sub-items
# (see _bucket08_slice_cols in resolve_dlq_waterfall_qualifying_months_cleared) and walked
# first, ahead of bucket_07, instead of being walked as one named column.


def resolve_dlq_waterfall_qualifying_months_cleared(  # pylint: disable=too-many-locals
    balance: DataFrame,
    cycles: DataFrame,
    qualifying_share: float = 1.0,
    bucket08_baseline_lookback_m: int = 24,
    bucket08_max_split: int = 6,
) -> DataFrame:
    """Count how many overdue-bucket "months" a cycle's payment fully clears.

    Dimension-B-only extension of resolve_due_amount_m's single-bucket view. A
    payment doesn't necessarily land just the oldest open bucket – a
    lumpsum payment can clear several buckets in one shot (e.g. bucket_06=600
    + bucket_05=550, payment=1200 clears both, 2 qualifying months, not 1).

    Two corrections to the naive "walk the existing buckets" view, both found
    by hand-tracing real lumpsum cycles in logs/sample_scenario1.log against
    the resulting statements, and cross-checked against sample_scenario3.log
    and sample_scenario4.log (2026-10-20):

    1. overdue_bucket_08 is included, as the OLDEST item in the walk – NOT
       excluded as a "terminal accumulator". resolve_due_amount_m's exclusion
       of bucket_08 was an unconfirmed assumption; a large enough payment
       (e.g. a 10,500 payment in sample_scenario1) does clear it, oldest-
       first, same as 07..01 – confirmed by the resulting next statement.
       Under pure non-payment (sample_scenario4), bucket_08 only ever
       accumulates (never ages back down on its own), consistent with it
       being a real waterfall slot a payment can reach, not a dead counter.
    2. The cycle's own freshly-billed minimum_due is appended as the NEWEST
       item in the same walk, scaled by qualifying_share like every other
       item. It isn't in any bucket yet at snapshot time, but it's exactly
       what becomes the new bucket_01 on the *next* statement if the
       leftover payment doesn't cover it. Confirmed two ways: (a) in
       sample_scenario1, the next cycle's new bucket_01 was numerically
       identical to this cycle's own minimum_due, carried forward unpaid;
       (b) sample_scenario4's clean period independently confirms
       total_due == (existing overdue as of this statement) +
       (this cycle's own minimum_due) exactly, the same relationship this
       fix relies on.
    3. overdue_bucket_08, when included, is no longer walked as ONE atomic
       item (2026-10-21). A large accumulated bucket_08 can represent
       several real historical months' worth of charges; walking it
       atomically means a payment that is genuinely larger than one month's
       due but smaller than the full accumulated pot credits zero months –
       indistinguishable from paying nothing (confirmed by hand against
       logs/scenarios.log scenario 1: a 5,200 payment against a 5,066.04
       bucket_08, trailing minimum_due baseline ~2,400, credited 0 months
       atomic vs. 1 decomposed). bucket_08 is split into up to
       bucket08_max_split uniform synthetic slices, each sized
       bucket_08 / n where n = the account's own bucket_08 amount divided by
       its trailing bucket08_baseline_lookback_m-cycle average minimum_due
       (rounded, floored at 1, capped), and walked oldest-first ahead of
       bucket_07 – same walk mechanics, just more/smaller items. If no
       reliable trailing baseline exists (e.g. no real billing history in
       the lookback), bucket_08 falls back to being walked as one atomic
       item (n=1) – the pre-fix behaviour, a conscious degrade rather than
       an invented number, matching resolve_due_amount_m's own honest-NULL
       philosophy.

    The walk (08 -> 07 -> ... -> 01 -> minimum_due) accumulates each item's
    amount and counts how many the cycle's payment_sum_in_cycle fully
    covers, strictly in order: a later item is never credited ahead of an
    earlier one that is not yet cleared, and an item only partially covered
    stops the walk there – no partial credit, matching "at least 100% of
    one month's due" wording. Zero/null buckets are skipped without
    breaking the walk or affecting the running total.

    The RETURNED count is a plain count, not a net-of-something adjustment
    (correction 4, 2026-10-21, replacing a prior "net, not gross" design):
    minimum_due is walked as just the newest item in the same oldest-first
    list (correction 2 above), and the function returns exactly how many
    items – decomposed bucket_08 slices, buckets 07..01, and minimum_due –
    the cycle's payment fully clears, full stop. This axis answers one
    question, "how many months of minimum due did the customer pay," which
    is inherently a count, not a value to be netted against anything.

    A prior design (2026-10-20 through 2026-10-21) instead subtracted 1 from
    the bucket-only count whenever the leftover payment did NOT also cover
    minimum_due, specifically to make this function's count match
    dlq_level_m's month-over-month delta on the DPD-bucket method
    (build_a3_dlq_payment_signals_dpd_bucket_movement) exactly, cycle for cycle. That
    convergence goal is now understood to be the wrong target:
    dlq_level_m is a lossy single-integer summary of the ladder (confirmed
    repeatedly – e.g. a large bucket_08 can silently represent several real
    months, which is exactly why correction 3 above exists), so forcing this
    function to match its delta means inheriting dlq_level_m's own
    compression artifacts rather than reporting the real count. Found by
    hand against logs/scenarios.log scenario 3's 2025-02-25 row: a 34,484.32
    payment against b04=2,578.22 plus three 7,500 buckets plus a 7,500
    minimum_due sums to exactly 32,578.22 (1,906.10 left over, discarded,
    same as every other over-payment this walk handles) – genuinely 5
    months' due paid, matching the real dlq drop of 5 (9->... no, 5->0)
    exactly. The old net-of-new-charge formula stopped at 4: it used
    minimum_due only as a pass/fail gate that could subtract credit, never
    add it, so a payment that covered every old bucket AND the new charge
    still scored one short of what was actually paid. Expected consequence:
    this function's count and dlq_level_m's delta will now disagree on some
    cycles (e.g. scenario 2's 2024-08-25: this function reads 3 – a
    decomposed bucket_08 slice, bucket_07, and bucket_06, each a real
    month-sized amount, all three fully paid – where dlq_level_m's delta
    reads 2, because Way4's own bucket_08 had already compressed more than
    one month into what dlq_level_m counts as a single occupied slot). That
    divergence is accepted, not a regression: dlq_level_m
    (build_a3_dlq_payment_signals_dpd_bucket_movement) remains a cheap, always-available
    cross-check/fallback; this function is the authoritative count whenever
    the billing ledger is available.

    PROD OOM fix, 2026-10-21 (mechanical, not a behavior change). The walk
    below used to thread a plain Python 3-tuple of raw Column objects through
    the loop (each iteration nesting the previous iteration's Column inside a
    new F.when(...).otherwise(...)) – 14 items (6 bucket08 slices + 7 ladder
    buckets + minimum_due) x 3 tuple elements produced one single, unevaluated
    ~42-node-deep Column AST, fed straight into this function's own final
    .select() below. In production, build_a3_payment_cycles hung 10+ minutes
    then crashed with java.lang.OutOfMemoryError: Java heap space, with the
    stack trace pointing at Catalyst's ColumnResolutionHelper during exactly
    that .select() call – i.e. analysis time, not row execution, and
    identical on every call regardless of data volume (the depth is
    structural, driven by the fixed 14-item list length). This exact
    pathology had already been diagnosed in an earlier session (45+ seconds
    to build a Catalyst plan for a single trivial row – see
    test_cc_a3_dimension_bc_signals.py's module docstring) but left
    unaddressed since performance tuning was out of scope for that pass; it
    is now a real production outage, so the walk below materializes each
    iteration's (running_total, still_clearing, gross_cleared) state as 3
    real, uniquely-named DataFrame columns via .withColumns() instead of
    nesting raw Column objects – the same pattern the bucket08-slice loop
    above already uses safely for the same reason (each step becomes a
    shallow Project node Catalyst resolves cheaply by column-name reference,
    instead of one deep expression tree). The arithmetic per step
    (candidate_total / meets_threshold / clears, and the three
    F.when(...).otherwise(...) updates) is byte-identical to before – only
    the threading mechanism changed. See
    test_cc_a3_dimension_bc_signals.py's TestResolveQualifyingMonthsClearedRealSpark
    for a real-Spark timing regression test and a reconstruction of this
    docstring's own scenario-1/scenario-3 anchors proving the output is
    unchanged.

    sample_scenario3.log's largest cycle (a 12,700 payment against ~19,678
    in old arrears + current due) does NOT reconcile even with both fixes –
    the shortfall is a genuine account-closure/final-settlement event
    (confirmed: the account's balance goes to true zero and cc_spine has no
    further rows for it at all), not a cash waterfall this function can or
    should model. No live A3 output is affected by that gap, since no later
    observation row's window ever includes that cycle.

    Not used by Dimension C: "paid as billed" there is inherently per-cycle
    and on-time (by due_date) – a later lumpsum clearing an old bucket cannot
    retroactively make that original cycle's payment on-time, so Dimension C
    keeps using resolve_due_amount_m / the single oldest-bucket figure
    unchanged (see build_a3_pre_dlq_payment_signals_single_payment_cycle_count). This function feeds
    only build_a3_dlq_payment_signals_payment_sum_waterfall (Dimension B), which has no on-time
    requirement ("qualifying ... promised or not").

    Args:
        balance: crx_cc_balance. Required cols: contract_id, observation_date
            (billing_date), overdue_bucket_01..08, minimum_due.
        cycles: attribute_payments_to_billing_cycles output (pre-rename –
            contract_id, billing_date, payment_sum_in_cycle).
        qualifying_share: fraction of an item's amount required to count it
            as cleared (matches _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE).
        bucket08_baseline_lookback_m: trailing cycles (rows), per account, to
            average minimum_due over for the bucket_08 decomposition baseline
            (matches _TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M).
        bucket08_max_split: ceiling on how many synthetic sub-items a single
            bucket_08 lump can be split into (matches
            _TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP).

    Returns:
        DataFrame with (account_id, billing_date, waterfall_qualifying_months_cleared_m).
    """
    balance_buckets = balance.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("minimum_due"),
        F.col("overdue_bucket_08"),
        *_QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST,
    )

    _w_trailing_minimum_due = (
        Window.partitionBy("contract_id")
        .orderBy("billing_date")
        .rowsBetween(-bucket08_baseline_lookback_m, -1)
    )
    balance_with_baseline = balance_buckets.withColumn(
        "_minimum_due_baseline",
        F.avg(F.when(F.col("minimum_due") > 0, F.col("minimum_due"))).over(
            _w_trailing_minimum_due
        ),
    )

    _bucket_08_amt = F.coalesce(F.col("overdue_bucket_08"), F.lit(0.0))
    _has_baseline = F.col("_minimum_due_baseline").isNotNull() & (
        F.col("_minimum_due_baseline") > 0
    )
    _n_bucket08_items = F.when(
        _has_baseline,
        F.greatest(
            F.lit(1),
            F.least(
                F.lit(bucket08_max_split),
                F.round(_bucket_08_amt / F.col("_minimum_due_baseline")).cast("int"),
            ),
        ),
    ).otherwise(
        F.lit(1)
    )  # no baseline -> atomic fallback, n=1 (pre-fix behaviour)

    balance_with_slices = balance_with_baseline.withColumn(
        "_n_bucket08_items", _n_bucket08_items
    )
    _slice_cols = [f"_bucket08_slice_{i:02d}" for i in range(1, bucket08_max_split + 1)]
    for i, slice_col in enumerate(_slice_cols, start=1):
        balance_with_slices = balance_with_slices.withColumn(
            slice_col,
            F.when(
                F.lit(i) <= F.col("_n_bucket08_items"),
                _bucket_08_amt / F.col("_n_bucket08_items").cast("double"),
            ).otherwise(F.lit(0.0)),
        )

    joined = cycles.select("contract_id", "billing_date", "payment_sum_in_cycle").join(
        balance_with_slices, on=["contract_id", "billing_date"], how="left"
    )

    def _walk_one_item_materialized(df, idx, prev_names, amount_col):
        """One waterfall-walk step, materialized as 3 real DataFrame columns
        instead of nesting the previous step's Column objects inside a new
        F.when(...) – see this function's "PROD OOM fix" docstring paragraph
        above for why. prev_names / the returned names are plain column-name
        strings threaded through the driving loop below; the arithmetic here
        is byte-identical to the pre-fix _walk_one_item closure."""
        prev_running_total = F.col(prev_names[0])
        prev_still_clearing = F.col(prev_names[1])
        prev_gross_cleared = F.col(prev_names[2])

        amt = F.coalesce(F.col(amount_col), F.lit(0.0))
        candidate_total = prev_running_total + amt * F.lit(qualifying_share)
        meets_threshold = F.col("payment_sum_in_cycle") >= candidate_total
        clears = prev_still_clearing & (amt > 0) & meets_threshold

        names = (
            f"_running_total_{idx:02d}",
            f"_still_clearing_{idx:02d}",
            f"_gross_cleared_{idx:02d}",
        )
        df = df.withColumns(
            {
                names[0]: F.when(clears, candidate_total).otherwise(prev_running_total),
                names[1]: F.when(
                    amt > 0, prev_still_clearing & meets_threshold
                ).otherwise(prev_still_clearing),
                names[2]: F.when(clears, prev_gross_cleared + 1).otherwise(
                    prev_gross_cleared
                ),
            }
        ).drop(
            *prev_names
        )  # bound schema width -- only the current step's state survives
        return df, names

    # minimum_due walked as the newest item, same as every bucket -- this
    # axis answers one question, "how many months of minimum due did the
    # customer pay," so there is nothing special about the freshest one
    # (2026-10-21 fix, replacing the old net-of-new-charge penalty entirely).
    # Real anchor: logs/scenarios.log scenario 3's 2025-02-25 row -- a
    # 34,484.32 payment against b04=2,578.22 + b03/b02/b01=7,500 each +
    # minimum_due=7,500 sums to exactly 32,578.22, with 1,906.10 left over
    # (simply discarded, same as every other over-payment in this walk) --
    # genuinely 5 months' due paid in full, matching the real dlq drop 5->0
    # exactly. The old formula stopped at the bucket walk (gross=4) and used
    # minimum_due only as a pass/fail gate that could subtract credit, never
    # add it, so a payment covering ALL of the old debt plus the new
    # charge still only scored 4, one short of what was actually paid.
    _walk_cols_oldest_first = (
        _slice_cols + _QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST + ["minimum_due"]
    )
    _seed_names = ("_running_total_00", "_still_clearing_00", "_gross_cleared_00")
    joined = joined.withColumns(
        {
            _seed_names[0]: F.lit(0.0),
            _seed_names[1]: F.lit(True),
            _seed_names[2]: F.lit(0),
        }
    )
    _state_names = _seed_names
    for _idx, _col_name in enumerate(_walk_cols_oldest_first, start=1):
        joined, _state_names = _walk_one_item_materialized(
            joined, _idx, _state_names, _col_name
        )
    qualifying_months_cleared = F.col(_state_names[2])

    return joined.select(
        F.col("contract_id").alias("account_id"),
        F.col("billing_date"),
        qualifying_months_cleared.alias("waterfall_qualifying_months_cleared_m"),
    )


def filter_payment_cycles(
    cycles: DataFrame, history_floor_date: str = None
) -> DataFrame:
    """Drop billing cycles that span a stretch of missing statements.

    A cycle runs from one statement to the NEXT statement that exists, so a missing
    stretch (the 2021-2023 billing gap, a missing statement run) becomes one long cycle
    whose payment sum covers several months against a single (stale) due amount. Two
    rules, both on the cycle's own dates:

    * billing_date >= history_floor_date - _PAYMENT_CYCLE_FLOOR_LOOKBACK_D days (only when
      a floor is set): keeps the legitimate predecessor of the first in-floor statement
      (up to ~35 days earlier), drops a cycle that starts years before the floor;
    * datediff(next_billing_date, billing_date) <= _PAYMENT_CYCLE_MAX_LENGTH_D days (a
      NULL next_billing_date, the account's latest cycle, is kept – it is never a
      result evidence).

    Dropped cycles give no payment evidence at all (they are not turned into
    zero-payment months).

    Args:
        cycles: attribute_payments_to_billing_cycles output (billing_date,
            next_billing_date, ...).
        history_floor_date: ISO date or None (params:cc_a3_history_floor_date).
    """
    result = cycles.where(
        F.col("next_billing_date").isNull()
        | (
            F.datediff(F.col("next_billing_date"), F.col("billing_date"))
            <= _PAYMENT_CYCLE_MAX_LENGTH_D
        )
    )
    floor = _floor_column(history_floor_date)
    if floor is not None:
        result = result.where(
            F.col("billing_date") >= F.date_sub(floor, _PAYMENT_CYCLE_FLOOR_LOOKBACK_D)
        )
    return result


def resolve_due_amount_m(balance: DataFrame) -> DataFrame:
    """Resolve "one month's due amount" per billing cycle for A3 Dimension B/C.

    due_amount_m = coalesce(overdue_bucket_07, ..., overdue_bucket_01, minimum_due),
    treating 0 the same as NULL at every step. Way4 represents the minimum_due
    (ENBD_DUE) coverage collapse about DLQ as an explicit 0 – not NULL – so a
    plain F.coalesce(minimum_due, ...) would never actually fall through to the
    next candidate; this is why each candidate is wrapped to treat 0 as missing.

    overdue_bucket_01 is the newest cycle's missed amount – verified against
    sample billing data (logs/billing_cycle.log, billing5.log, billing6.log) to
    consistently equal the prior cycle's minimum_due, i.e. the right
    single-month granularity. Once minimum_due goes dark, new amounts stop
    landing in overdue_bucket_01 too (nothing new is being billed that cycle);
    the existing single-month figure keeps aging through buckets 02..07 as a
    pure FIFO shift (confirmed: past_due_amount stays flat while this happens).

    A payment clears the oldest outstanding bucket first (standard collections
    waterfall – the longest-overdue amount is settled before anything newer),
    so bucket_07 (the most aged of 01..07) is the one actually at stake for
    "did this cycle's payment clear what's due" and must be checked first;
    falling through 07..01 then minimum_due recovers the oldest still-open
    single-month figure, which is the amount a qualifying payment needs to
    clear.

    overdue_bucket_08 is deliberately EXCLUDED – it is Way4's terminal
    accumulator bucket (confirmed by its magnitude: ~20x a single bucket's
    value once the ladder fully drains into it), not a single month's amount.
    total_due is also deliberately excluded – confirmed by sample data to grow
    unboundedly from compounding interest/fees even at zero payment activity,
    making a "100% of total_due" bar structurally unreachable deep in
    delinquency.

    NULL when none of the candidates has a real value – genuinely nothing
    determinable to check a payment against that cycle (pre-delinquency before
    anything is billed, or post write-off/settlement, or the ladder has fully
    drained into the bucket_08 accumulator with no single-month figure left).
    [CONFIRM] – the single highest-impact assumption in the A3 framework.

    Args:
        balance: crx_cc_balance. Required cols: contract_id, observation_date
            (billing_date), minimum_due, overdue_bucket_01..07.

    Returns:
        DataFrame with (account_id, billing_date, due_amount_m).
    """

    def _nonzero(column: str):
        return F.when(F.col(column).isNotNull() & (F.col(column) != 0.0), F.col(column))

    candidates = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]
    due_amount_m = F.coalesce(*[_nonzero(c) for c in candidates])

    return balance.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").alias("billing_date"),
        due_amount_m.alias("due_amount_m"),
    )


def resolve_bucket08_fallback_due(
    balance: DataFrame, baseline_months: int = _TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS
) -> DataFrame:
    """Due amount for statements where only overdue_bucket_08 is left (default method).

    resolve_due_amount_m returns NULL once buckets 01-07 and minimum_due are all 0 and
    bucket 08 holds the money, so such a cycle can never qualify. Per account, the
    stagnation point is the first balance row in that state; the frozen baseline is the
    average minimum_due of its last ``baseline_months`` months with a positive
    minimum_due before that point. Every later stagnated statement gets that one number.
    Accounts with no positive minimum_due before stagnation get no row (stay NULL).

    Args:
        balance: crx_cc_balance (contract_id, observation_date, minimum_due,
            overdue_bucket_01..08).
        baseline_months: months of positive minimum_due averaged.

    Returns:
        (account_id, billing_date, due_amount_fallback_m) for stagnated statements of
        accounts that have a baseline.
    """

    def _nonzero(column: str):
        return F.col(column).isNotNull() & (F.col(column) != 0.0)

    ladder_empty = F.lit(True)
    for column in [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]:
        ladder_empty = ladder_empty & ~_nonzero(column)
    stagnated = ladder_empty & _nonzero("overdue_bucket_08")

    rows = balance.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").alias("billing_date"),
        "minimum_due",
        stagnated.alias("_stagnated"),
    )
    stagnation = (
        rows.filter("_stagnated")
        .groupBy("account_id")
        .agg(F.min("billing_date").alias("_stagnation_date"))
    )
    baseline = (
        rows.join(stagnation, "account_id")
        .filter(
            _nonzero("minimum_due")
            & (F.col("billing_date") < F.col("_stagnation_date"))
        )
        .groupBy("account_id", F.trunc("billing_date", "month").alias("_month"))
        .agg(F.avg("minimum_due").alias("_month_min_due"))
        .withColumn(
            "_recency",
            F.row_number().over(
                Window.partitionBy("account_id").orderBy(F.col("_month").desc())
            ),
        )
        .filter(F.col("_recency") <= baseline_months)
        .groupBy("account_id")
        .agg(F.avg("_month_min_due").alias("due_amount_fallback_m"))
    )
    return (
        rows.filter("_stagnated")
        .join(baseline, "account_id")
        .select("account_id", "billing_date", "due_amount_fallback_m")
    )


def aggregate_dlq_window(
    spine_with_window: DataFrame,
    cycles: DataFrame,
    evidence_date_col: str,
    qualifying_months_expr,
    any_payment_expr,
) -> DataFrame:
    """Shared Dimension B window join + aggregation for all three approaches.

    Joins each spine row (account_id, observation_date) to the cycles whose
    ``evidence_date_col`` (the statement that shows the cycle's result) falls
    in (_any_window_start, observation_date]. The window is open at the start
    because the cycle whose result statement IS t0 is the pre-onset payment
    that failed to stop the account going delinquent, and closed at the end
    because the statement at observation_date is already known at the
    observation. Two windows share that one join:

    * "Regular": sums ``qualifying_months_expr`` (per-cycle int) over cycles
      after _window_start (3 months at 61-180 DPD, 6 at 180+) into
      dlq_payment_qualifying_month_cnt;
    * "any payment": flags every joined cycle where ``any_payment_expr``
      (per-cycle boolean) holds as dlq_payment_any_flag, over the whole
      _any_window_start window (same as Regular at 61-180, 12 months at 180+).

    Both expressions reference the cycles side via the ``c`` alias. Each
    approach supplies only its own per-cycle expressions; the join and the
    grouping are identical across approaches. ``spine_with_window`` must carry
    _window_start / _window_months / _any_window_start / _any_window_months.
    """
    joined = spine_with_window.alias("s").join(
        cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col(f"c.{evidence_date_col}") > F.col("s._any_window_start"))
        & (F.col(f"c.{evidence_date_col}") <= F.col("s.observation_date")),
        "left",
    )
    in_regular_window = F.col(f"c.{evidence_date_col}") > F.col("s._window_start")
    return joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.observation_date").alias("observation_date"),
        F.col("s.t0").alias("t0"),
        F.col("s._window_months").alias("dlq_payment_window_months"),
        F.col("s._any_window_months").alias("dlq_payment_any_window_months"),
    ).agg(
        F.coalesce(
            F.sum(F.when(in_regular_window, qualifying_months_expr)), F.lit(0)
        ).alias("dlq_payment_qualifying_month_cnt"),
        F.coalesce(
            F.max(F.when(any_payment_expr, F.lit(1)).otherwise(F.lit(0))),
            F.lit(0),
        ).alias("dlq_payment_any_flag"),
    )


def aggregate_pre_dlq_window(
    spells: DataFrame,
    cycles: DataFrame,
    paid_as_billed_col: str,
    evidence_date_col: str = "next_billing_date",
    min_months_due: int = _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
) -> DataFrame:
    """Shared Dimension C window join + aggregation for both approaches.

    Joins each spell to the cycles whose ``evidence_date_col`` (the
    statement/month-end row that shows the cycle's result) falls in
    [_window_start, t0), counts cycles with a due amount
    (pre_dlq_months_due_n) and those flagged ``paid_as_billed_col``
    (pre_dlq_months_paid_as_billed_n), and derives
    pre_dlq_paid_as_billed_share – NULL below ``min_months_due``
    (the "no_record" condition downstream). ``cycles`` must carry ``_has_due``
    and the named boolean column.
    """
    joined = spells.alias("s").join(
        cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col(f"c.{evidence_date_col}") >= F.col("s._window_start"))
        & (F.col(f"c.{evidence_date_col}") < F.col("s.t0")),
        "left",
    )
    agg = joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.spell_id").alias("spell_id"),
        F.col("s.t0").alias("t0"),
    ).agg(
        F.coalesce(F.sum(F.col("c._has_due").cast("int")), F.lit(0)).alias(
            "pre_dlq_months_due_n"
        ),
        F.coalesce(
            F.sum((F.col("c._has_due") & F.col(f"c.{paid_as_billed_col}")).cast("int")),
            F.lit(0),
        ).alias("pre_dlq_months_paid_as_billed_n"),
    )
    return agg.withColumn(
        "pre_dlq_paid_as_billed_share",
        F.when(
            F.col("pre_dlq_months_due_n") >= min_months_due,
            F.col("pre_dlq_months_paid_as_billed_n").cast("double")
            / F.col("pre_dlq_months_due_n").cast("double"),
        ),  # NULL otherwise -> "No record" downstream
    )


def pooled_trailing_broken_streak(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    agreement_bridge: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
    months_back: int = _TAU_A3V2_COMMITMENTS_WINDOW_M,
    n_latest: int = _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
) -> DataFrame:
    """Dimension A streak: the broken run at the head of the latest concluded instalments.

    Pools PTP and settlement instalments of an agreement, keeps those due in the last
    months_back months, takes the latest n_latest concluded ones and counts the
    consecutive broken ones from the most recent. A streak of n_latest means "the last
    N concluded were all broken".

    Concluded = due on or before the observation date and either fully paid or overdue
    (an instalment due today and still unpaid is not concluded). Broken = overdue, i.e.
    not fully paid, partial payments included. Paid / overdue and the cancelled-
    instalment rule are dcore's own (instalment_amount_flags,
    null_cancelled_instalment_fields). On the same due date a broken instalment ranks
    first (the stricter reading).

    Args:
        agreement_bridge: (iagreementseqno, observation_date, ...) rows to score.
        int_ptp / ptp_instalments: dcore_int_ptp, dcore_prm_promise_instalments.
        int_settlement / settlement_instalments: dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments.

    Returns:
        (iagreementseqno, observation_date, commitments_broken_streak) for agreements
        with at least one concluded instalment in the window; absent agreements have
        no concluded instalment (streak 0 for the caller).
    """
    instalment_cols = ["agreement_id", "due_date", "due_amount", "payment_amount"]
    ptp = null_cancelled_instalment_fields(
        int_ptp.select("agreement_id", "promise_seqno").join(
            ptp_instalments.select(
                "promise_seqno",
                "due_date",
                "due_amount",
                "payment_amount",
                "instalment_status",
            ),
            on="promise_seqno",
        ),
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = null_cancelled_instalment_fields(
        int_settlement.select("agreement_id", "rps_seqno").join(
            settlement_instalments.select(
                "rps_seqno",
                "due_date",
                "due_amount",
                "payment_amount",
                "instalment_status",
            ),
            on="rps_seqno",
        ),
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    instalments = (
        ptp.select(*instalment_cols)
        .unionByName(settlement.select(*instalment_cols))
        .where(F.col("due_date").isNotNull())
    )

    scored = (
        agreement_bridge.where(F.col("iagreementseqno").isNotNull())
        .select(F.col("iagreementseqno").alias("agreement_id"), "observation_date")
        .distinct()
    )
    in_window = scored.join(instalments, on="agreement_id").where(
        (F.col("due_date") <= F.col("observation_date"))
        & (F.col("due_date") >= F.add_months(F.col("observation_date"), -months_back))
    )

    is_paid, _, is_overdue = instalment_amount_flags()
    ranked = (
        in_window.where(is_paid | is_overdue)
        .withColumn("_broken", F.when(is_overdue, 1).otherwise(0))
        .withColumn(
            "_rn",
            F.row_number().over(
                Window.partitionBy("agreement_id", "observation_date").orderBy(
                    F.col("due_date").desc(), F.col("_broken").desc()
                )
            ),
        )
        .where(F.col("_rn") <= n_latest)
    )
    return (
        ranked.groupBy("agreement_id", "observation_date")
        .agg(
            F.count(F.lit(1)).alias("_n"),
            F.min(F.when(F.col("_broken") == 0, F.col("_rn"))).alias("_first_kept"),
        )
        .select(
            F.col("agreement_id").alias("iagreementseqno"),
            "observation_date",
            F.coalesce(F.col("_first_kept") - 1, F.col("_n"))
            .cast("int")
            .alias("commitments_broken_streak"),
        )
    )


def _plan_starts(int_ptp: DataFrame, int_settlement: DataFrame) -> DataFrame:
    """(agreement_id, start, plan_type) for every non-cancelled PTP and settlement plan.

    PTP start = coalesce(promise_start, event_date); settlement start = event_date (its
    first instalment due date, the only date dcore keeps for it) [CONFIRM: proxy].
    """
    ptp = int_ptp.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
        "agreement_id",
        F.coalesce(F.col("promise_start"), F.col("event_date")).alias("start"),
        F.lit("ptp").alias("plan_type"),
    )
    settlement = int_settlement.where(
        F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1
    ).select(
        "agreement_id",
        F.col("event_date").alias("start"),
        F.lit("settlement").alias("plan_type"),
    )
    return ptp.unionByName(settlement)


def flag_plans_on_record(
    signals: DataFrame, int_ptp: DataFrame = None, int_settlement: DataFrame = None
) -> DataFrame:
    """Flag a PTP / settlement on record between T0 and the observation date.

    Adds ptp_on_record_flag and arrangement_on_record_flag (1 when the agreement has a
    non-cancelled PTP / settlement plan started in [t0, observation_date]; a NULL t0 is
    an unbounded lower bound). Both are NULL when the plan tables are not supplied.
    Used by the No-response strong negative ("no promise or arrangement on record").

    Args:
        signals: rows with account_id, observation_date, iagreementseqno, t0.
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
    """
    keys = ["account_id", "observation_date"]
    if int_ptp is None or int_settlement is None:
        return signals.withColumn(
            "ptp_on_record_flag", F.lit(None).cast("int")
        ).withColumn("arrangement_on_record_flag", F.lit(None).cast("int"))

    scored = (
        signals.where(F.col("iagreementseqno").isNotNull())
        .select(*keys, "iagreementseqno", "t0")
        .distinct()
    )
    on_record = (
        scored.join(
            _plan_starts(int_ptp, int_settlement),
            F.col("iagreementseqno") == F.col("agreement_id"),
        )
        .where(
            (F.col("start") <= F.col("observation_date"))
            & (F.col("t0").isNull() | (F.col("start") >= F.col("t0")))
        )
        .groupBy(*keys)
        .agg(
            F.max(F.when(F.col("plan_type") == "ptp", 1).otherwise(0)).alias(
                "ptp_on_record_flag"
            ),
            F.max(F.when(F.col("plan_type") == "settlement", 1).otherwise(0)).alias(
                "arrangement_on_record_flag"
            ),
        )
    )
    return (
        signals.join(on_record, on=keys, how="left")
        .withColumn(
            "ptp_on_record_flag", F.coalesce(F.col("ptp_on_record_flag"), F.lit(0))
        )
        .withColumn(
            "arrangement_on_record_flag",
            F.coalesce(F.col("arrangement_on_record_flag"), F.lit(0)),
        )
    )


def flag_followups_after_refusal(  # pylint: disable=too-many-locals
    signals: DataFrame,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
    transactions: DataFrame = None,
) -> DataFrame:
    """Flag what followed the latest right-party refusal, for the Refusal strong negative.

    Only rows whose last_rpc_disposition is the refusal ('rtp') are looked at; the
    others get 0. Adds, all dated strictly after last_rpc_date and up to the
    observation date:
        refusal_followed_by_commitment (int) – a non-cancelled PTP (start =
            coalesce(promise_start, event_date)) or settlement (start = event_date,
            its first instalment due date, the only date dcore keeps) of the agreement.
            0 when the plan tables are not supplied.
        refusal_followed_by_payment (int)     – a card payment of any amount.
        refusal_followed_by_payment_min_amount (int) – card payments since the refusal
            sum to at least the 180+ minimum payment (Dimension B's guard).
        payment_evidence_available (int)      – 1 when transactions were supplied; when
            0 the payment flags are 0 and the caller falls back to Dimension B's
            any-payment flag.

    Args:
        signals: Rows with account_id, observation_date, iagreementseqno,
            last_rpc_disposition, last_rpc_date.
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
        transactions: crx_cc_transactions (contract_id, observation_date = banking
            date, txn_amount_aed, txn_category, is_post_block_x_fee).
    """
    keys = ["account_id", "observation_date"]
    refusals = (
        signals.where(F.col("last_rpc_disposition") == "rtp")
        .select(*keys, "iagreementseqno", "last_rpc_date")
        .distinct()
    )

    result = signals
    if int_ptp is not None and int_settlement is not None:
        starts = _plan_starts(int_ptp, int_settlement)
        followed_commitment = (
            refusals.join(
                starts,
                (F.col("iagreementseqno") == F.col("agreement_id"))
                & (F.col("start") > F.col("last_rpc_date"))
                & (F.col("start") <= F.col("observation_date")),
            )
            .select(*keys)
            .distinct()
            .withColumn("refusal_followed_by_commitment", F.lit(1))
        )
        result = result.join(followed_commitment, on=keys, how="left")
    else:
        result = result.withColumn("refusal_followed_by_commitment", F.lit(0))

    if transactions is not None:
        payments = transactions.where(
            (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
        ).select(
            F.col("contract_id").alias("account_id"),
            F.col("observation_date").alias("banking_date"),
            "txn_amount_aed",
        )
        followed_payment = (
            refusals.join(
                payments,
                (refusals["account_id"] == payments["account_id"])
                & (payments["banking_date"] > refusals["last_rpc_date"])
                & (payments["banking_date"] <= refusals["observation_date"]),
            )
            .groupBy(refusals["account_id"], refusals["observation_date"])
            .agg(
                F.lit(1).alias("refusal_followed_by_payment"),
                F.when(
                    F.sum("txn_amount_aed")
                    >= _TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS,
                    F.lit(1),
                )
                .otherwise(F.lit(0))
                .alias("refusal_followed_by_payment_min_amount"),
            )
        )
        result = result.join(followed_payment, on=keys, how="left").withColumn(
            "payment_evidence_available", F.lit(1)
        )
    else:
        result = (
            result.withColumn("refusal_followed_by_payment", F.lit(0))
            .withColumn("refusal_followed_by_payment_min_amount", F.lit(0))
            .withColumn("payment_evidence_available", F.lit(0))
        )

    flag_cols = [
        "refusal_followed_by_commitment",
        "refusal_followed_by_payment",
        "refusal_followed_by_payment_min_amount",
    ]
    for col in flag_cols:
        result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)).cast("int"))
    return result.withColumn(
        "payment_evidence_available", F.col("payment_evidence_available").cast("int")
    )
