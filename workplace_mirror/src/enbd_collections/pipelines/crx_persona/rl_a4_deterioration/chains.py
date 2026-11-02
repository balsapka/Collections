"""Restructure chains: a restructured loan and the closed original loans behind it.

``int_loan_restructure_link`` is one edge per (restructured account, original account). An
original can itself be a restructured loan, so edges are walked transitively; plain Python,
as the link is small and a cycle must not loop.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, NamedTuple


class Edge(NamedTuple):
    """One link row. ``known``: the later of restructure flag and original closure."""

    account: str
    original: str
    known: date
    match_type: str
    candidates: int


class Chain(NamedTuple):
    """One restructured account with everything walked behind it."""

    account: str
    known: date
    n_originals: int
    match_type: str
    candidates: int


class Member(NamedTuple):
    """One original loan of a chain. ``is_end``: it has no original of its own."""

    account: str
    original: str
    is_end: bool


def resolve_chains(
    edges: Iterable[Edge], accounts: Iterable[str]
) -> tuple[list[Chain], list[Member]]:
    """Walk every account in ``accounts`` back through ``edges``."""
    by_account: dict[str, list[Edge]] = defaultdict(list)
    for edge in edges:
        by_account[edge.account].append(edge)

    chains, members = [], []
    for account in accounts:
        seen, stack, walked = {account}, [account], []
        while stack:
            for edge in by_account.get(stack.pop(), ()):
                walked.append(edge)
                if edge.original not in seen:
                    seen.add(edge.original)
                    stack.append(edge.original)
        if not walked:
            continue
        originals = sorted(seen - {account})
        chains.append(
            Chain(
                account,
                max(e.known for e in walked),
                len(originals),
                (
                    "many_to_one"
                    if any(e.match_type == "many_to_one" for e in walked)
                    else "one_to_one"
                ),
                max(e.candidates for e in walked),
            )
        )
        members += [Member(account, o, o not in by_account) for o in originals]
    return chains, members
