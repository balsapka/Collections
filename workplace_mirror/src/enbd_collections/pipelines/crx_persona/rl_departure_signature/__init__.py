"""RL Departure Signature pipeline (RL-A2-2).

Inputs: rl_spine, crx_rl_spell_table, comp_financial_tran_repos_dly,
        feat_payroll_indicator, feat_fx_leakage, prm_digital_login_monthly
Output: crx_rl_departure_signature
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
