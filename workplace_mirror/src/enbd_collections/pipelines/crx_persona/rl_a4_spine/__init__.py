"""RL A4 Spine — structural spine/spell window projection for Retail Loans.

Inputs: rl_spine, crx_rl_spell_table
Output: crx_rl_a4_spine
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
