"""Config-driven scope filtering for wide raw tables -- staging side.

Scope sets (scope_ids / windows / grid) are produced upstream and passed in as
node inputs; this module only applies them.

Public API:
    apply_scope  -- reduce a raw table to scope (joins only, never distinct)
    scoped_stage -- staging node: apply_scope then a pure transform
"""

from .filters import apply_scope, scoped_stage

__all__ = ["apply_scope", "scoped_stage"]
