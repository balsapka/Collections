"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` — ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` — the month-end balance (assets: deposits, investments, WM; NULL for
  credit products);
* ``is_current`` — credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` — credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``), so the A1 engine can leave out the scored account itself. Supplementary
cards post to their contract and never appear as a product of their own. CASA balances are
never a product here (they are A1's money held, ``feat_cif_casa_balance_monthly``).
"""

from __future__ import annotations

from pyspark.sql import DataFrame

PRODUCT_TYPES = ("deposit", "investment", "wm", "card", "loan")
COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    product_holding: DataFrame,
    loan_portfolio: DataFrame,
    card_balances: DataFrame,
    wm_assets: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the month ends of the last ``history_months`` months up to the
    persona start month on.

    TODO(sonnet): implement from the round-3 snippet's F4 builder
    (``tmp_validation/a1_family_redesign/round3_snippet.py``, family F4 with other cards,
    R3), which reads these sources: ``feat_product_holding`` (deposits / investments),
    ``bo_rr_portf_actv_acct_mthly`` (loans: DPD and instalment), the card balances
    snapshot (cards: DPD and minimum due) and the WM asset balances. Output exactly
    ``COLUMNS``, one row per ``(cif_id, month_end, product_account_id)``, ``cif_id`` as
    string; fail loud on missing columns (``_require`` as in ``feat_cif_casa``).
    """
    raise NotImplementedError(
        "feat_cif_cross_product.build: implement from the round-3 F4 builder "
        "(bundle 21, UAT step)"
    )
