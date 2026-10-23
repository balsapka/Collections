"""Observation base: (account_id, observation_date, cif_id) per product."""

from .pipeline import create_cc_pipeline, create_rl_pipeline

__all__ = ["create_cc_pipeline", "create_rl_pipeline"]
