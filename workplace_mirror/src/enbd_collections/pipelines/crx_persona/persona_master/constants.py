"""The persona layer over the four axes: how each axis state is banded and which
combination is which persona. Every mapping here is a business rule GRR owns; changing a
persona is a change to one dict.
"""

# A1 ability: can they pay?
ABILITY_BAND = {
    "high": "able",
    "moderate": "able",
    "low": "unable",
    "unknown": "unseen",
}

# A3 payment credibility: do they pay, and keep their word?
CREDIBILITY_BAND = {
    "high": "credible",
    "moderate": "credible",
    "low": "not_credible",
    "unknown": "unseen",
}

# Ability band x credibility band -> persona segment (what to offer them).
SEGMENTS = {
    ("able", "credible"): "willing_and_able",
    ("able", "not_credible"): "able_not_paying",
    ("able", "unseen"): "able_no_track_record",
    ("unable", "credible"): "paying_while_stretched",
    ("unable", "not_credible"): "unable_not_paying",
    ("unable", "unseen"): "unable_no_track_record",
    ("unseen", "credible"): "paying_capacity_unseen",
    ("unseen", "not_credible"): "not_paying_capacity_unseen",
    ("unseen", "unseen"): "no_evidence",
}
DECEASED_SEGMENT = "deceased"  # a deceased customer gets no other segment

# A2 locatability -> contact route (how to reach them), first match wins:
# deceased; abroad (location Skip, whatever the calls say); gone dark (the last
# failed call days with no contact since); reachable; else unconfirmed.
ROUTE_DECEASED = "deceased"
ROUTE_ABROAD = "abroad"
ROUTE_GONE_DARK = "gone_dark"
ROUTE_REACHABLE = "reachable"
ROUTE_UNCONFIRMED = "unconfirmed"

# A4 deterioration -> journey group (how they got here).
JOURNEY_GROUP = {
    "early_payment_default": "never_settled",
    "straight_roller_early_life": "never_settled",
    "straight_roller_seasoned": "sudden_stop",
    "repeat_delinquent": "recurring",
    "slow_roller": "partial_payer",
    "stabilized": "partial_payer",
    "unknown": "unknown",
}

# The axis outputs' own housekeeping columns; the master writes one computed_at.
AXIS_DROP = ("computed_at", "cif_id", "det_segment")
