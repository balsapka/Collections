"""T04c — CRX CC Raw Extract pipeline.

Promotes the T0-scoped raw DDI extracts (previously private helpers inside
T04b) to persisted intermediate catalog datasets consumed by T04b, T05, and T06.

Assets produced:
    crx_cc_transactions : CC transaction history, T0-scoped, enriched schema
    crx_cc_limits       : CC credit-limit snapshots, T0-scoped
    crx_cc_balance      : CC total_due billing history, T0-scoped
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
