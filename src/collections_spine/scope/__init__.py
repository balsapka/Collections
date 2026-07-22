"""Config-driven scope filtering for wide raw tables.

Public API:
    build_scope_ids   -- distinct id set (spine layer; computed ONCE)
    add_window_bounds -- per-anchor (id, win_start, win_end) for `range`
    build_grid        -- exploded (id, obs_grain) for `grid`
    apply_scope       -- reduce a raw table to scope (joins only, never distinct)
    scoped_stage      -- staging node: apply_scope then a pure transform
"""

from .filters import (
    add_window_bounds,
    apply_scope,
    build_grid,
    build_scope_ids,
    scoped_stage,
)

__all__ = [
    "add_window_bounds",
    "apply_scope",
    "build_grid",
    "build_scope_ids",
    "scoped_stage",
]
