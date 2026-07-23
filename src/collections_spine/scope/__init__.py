"""Scope filtering for wide raw tables -- staging side.

Three composable leftsemi filters; scope sets are produced upstream and passed in
as node inputs. Column-name differences are handled by aliasing the small side
internally -- never by copying datasets.

Public API:
    filter_ids     -- keep rows whose id is in scope
    filter_windows -- keep rows whose date falls in any of the id's anchor windows
    filter_pairs   -- keep rows whose exact (id, date) pair is in scope
"""

from .filters import filter_ids, filter_pairs, filter_windows

__all__ = ["filter_ids", "filter_pairs", "filter_windows"]
