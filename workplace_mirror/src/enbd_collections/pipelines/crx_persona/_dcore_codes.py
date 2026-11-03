"""DCORE follow-up vocabulary (``dcore_prm_followup_outcomes``) shared by A2 and A3.

Single source of truth for call action codes and result-name sets. A2 (reachability,
deceased) and A3 (payment credibility) import from here and never from each other.
Result names are compared upper-cased and trimmed. The departure notes (location
evidence) live in the location feature.

The A2 ``FAILED_CALL`` and A3 ``NOT_REACHABLE`` / ``RINGING`` sets overlap only partly:
they are different classifications, not copies.
"""

OUTBOUND_CODES = ("OC", "CB")  # outbound call, callback: we called
INBOUND_CODES = ("IC",)  # the customer called us
CALL_CODES = (*OUTBOUND_CODES, *INBOUND_CODES)  # IA administrative notes never count
SUCCESS_CATEGORY = "SUC"

# The account holder was reached personally (any call code, any category).
RIGHT_PARTY_CONTACT = frozenset(
    {
        "ACCOUNT PAID",
        "APPRECIATIONS",
        "BALCON WOP 12 MONTHS",
        "BALCON WOP 24 MONTHS",
        "BALCON WP 12 MONTHS",
        "BALCON WP 24 MONTHS",
        "BALCON WP 48 MONTHS",
        "CHANGE OF EMPLOYER",
        "CLAIMS MADE PAYMENT",
        "CODE25 WILL PAY AT SALARY",
        "CUSTOMER BEHAVIOUR GREEN",
        "CUSTOMER BEHAVIOUR ORANGE",
        "CUSTOMER BEHAVIOUR RED",
        "CUSTOMER BEHAVIOUR YELLOW",
        "CUSTOMER HAVE NO JOB",
        "CUSTOMER HUNG UP",
        "CUSTOMER IS PERMANENT DISABLED",
        "CUSTOMER KEPT PROMISE MADE",
        "CUSTOMER MADE PAYMENT",
        "CUSTOMER MISBEHAVED",
        "CUSTOMER TERMINATED",
        "CUSTOMER WANTS SETTLEMENT",
        "CUSTOMER WILL VISIT US",
        "CUSTOMER_HUNG_UP",
        "DEBT COUNSELLING",
        "DEFERMENT FOR IMPACTED CUSTOMERS",
        "DEMAND FOR HUMAN AGENT",
        "DIGITAL COLLECT  PTP SUBSCRIBED",
        "DISPUTE",
        "E MAIL RECEIVED",
        "EPP REQUEST",
        "EXPECTING EOSB",
        "FIELD VISIT DONE",
        "FIELD VISIT REJECTED",
        "JOB LOST",
        "KSA/CALLBACK",
        "KSA/CONNECT AND DROP",
        "KSA/CUSTOMER WILL PAY AT SALARY",
        "KSA/CUSTOMER WILL SEND EMAIL",
        "KSA/CUSTOMER WILL VISIT US",
        "KSA/DISPUTE",
        "KSA/EARLY/FINAL SETTLEMENT",
        "KSA/EOSB",
        "KSA/JOB LOST",
        "KSA/NEED DEFERMENT",
        "KSA/PAID AMOUNT",
        "KSA/PARTIAL PAYMENT",
        "KSA/PROMISE TO PAY",
        "KSA/REFUSE TO PAY",
        "KSA/RESCHEDULING REQUEST",
        "MEDICAL ISSUES",
        "MEMBER ON LEAVE/VACATION",
        "NEED BALCON",
        "NEED DEFERMENT",
        "NEED RESTRUCTURE",
        "NEW SECURITY CHEQUE COLLECTED",
        "NIL SALARY",
        "NO NEED DEFERMENT",
        "PARTIALLY PAID",
        "POST DATED CHEQUE AVAILABLE",
        "POST DATED COLLECTED",
        "PROMISE TO PAY",
        "PROMISE TO PAY PARTIALLY",
        "PROMISE TO PAY SCHEDULED",
        "RECEIVED EOSB",
        "REFUSE TO PAY",
        "REFUSED TO PAY",
        "REQUEST FOR DUE DATE CHANGE",
        "REQUEST FOR FUNDING ACCOUNT CHANGE",
        "REQUEST FOR LIEN REMOVAL",
        "REQUEST FOR PAYMENT MODE CHANGE",
        "REQUEST TO PRESENT SECURITY CHEQUE",
        "REQUESTED FOR FD LIQUIDATION",
        "RESTRUCTURE NOT REQUIRED",
        "RESTRUCTURE REQUIRED",
        "REWRITE AGREED",
        "REWRITE NOT AGREED",
        "SALARY DELAY",
        "SALARY REDUCTION",
        "SETTLEMENT",
        "SOFTPTP",
        "UNPAID LEAVE",
        "WILL PAY AT SALARY",
    }
)

# A failed outbound call: it rang out or nobody answered (a message left included), or the
# line is dead / the number invalid. CALL CONNECTED without SUC and any other outcome
# (e.g. LINE BUSY) is a neutral attempt: neither failed nor a contact.
FAILED_CALL = frozenset(
    {
        # rang out, no answer
        "RINGING NO REPLY",
        "RINGING NO RESPONSE",
        "NO ANSWER",
        "LEFT_MSG",
        # dead line, invalid number
        "CUSTOMER NOT CONTACTABLE",
        "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
        "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
        "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
        "ININ-OUTBOUND-SIT-UNCALLABLE",
        "KSA/MOBILE SWITCHED OFF",
        "KSA/OUT OF SERVICE",
        "KSA/UNCONTACTABLE",
        "KSA/WRONG NUMBER",
        "LINE DISCONNECTED",
        "MOBILE SWICTHED OFF",
        "MOBILE SWITCHED OFF",
        "NOT REACHABLE",
        "OUTBOUND-INVALID-PHONE-NUMBER",
        "PHONE OUT OF SERVICE",
        "UNCONTACTABLE",
        "WRONG NO",
        "WRONG NUMBER",
    }
)

# Collector skip-trace statuses: a diagnostic column, not location or reachability evidence.
SKIP_TRACE = frozenset({"SKIP - UNDER TRACING", "SKIP - TRACED"})

# Dropped before any reachability rule: administrative entries, RL legal / repossession
# routing (plus every "RPO CASE …" name) and the skip-trace statuses.
IGNORED = frozenset(
    {
        "RESULT NOT FOUND",
        "FOLLOW UP",
        "E MAIL SENT",
        "LEGAL NOTICE SENT",
        "VEHICLE REPOSSESED/UNDER AUCTION",
        *SKIP_TRACE,
    }
)
IGNORED_PREFIX = "RPO CASE"

# Confirmed or claimed (a relative's claim counts until disproved).
DECEASED = frozenset(
    {
        "DECEASED",
        "DECEASED CLAIMED",
        "DECEASED OR EXPIRED",
        "DECEASED/EXPIRED",
        "KSA/DECEASED",
    }
)

# Explicit refusal signals – result names where confirmed right-party contact was
# made but the customer explicitly refused, hung up, or disputed.
# Subset of RIGHT_PARTY_CONTACT (every entry here also confirms contact).
# Excludes settlement-seeking behaviour (engagement) and autodialler intermediates.
#
# Drives refusing_n counter → non_cooperative state (confirmed contact + refusal).
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(REFUSING)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
REFUSING = {
    "CUSTOMER HUNG UP",
    "CUSTOMER MISBEHAVED",
    "CUSTOMER_HUNG_UP",
    "DISPUTE",
    "KSA/DISPUTE",
    "KSA/REFUSE TO PAY",
    "REFUSE TO PAY",
    "REFUSED TO PAY",
    "REWRITE NOT AGREED",
}

# Ringing no-answer signals – phone rang at the customer end but was not answered.
# Excludes LINE BUSY (transient, does not indicate call screening).
# Drives ringing_n counter → avoiding state when ≥3 ringing events and line is live.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RINGING = {
    "RINGING NO REPLY",
    "RINGING NO RESPONSE",
}

# Promise to pay or willingness to pay – result names signalling the customer
# has committed to pay, made a payment arrangement, or actually paid.
# Covers: all PTP-category outcomes, actual payments (SUC), and INT entries
# where the customer verbally committed or agreed to a specific arrangement
# (balance consolidation, rewrite, deferment, settlement, salary-date promise).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PROMISE_TO_PAY = {
    "ACCOUNT PAID",
    "BALCON WOP 12 MONTHS",
    "BALCON WOP 24 MONTHS",
    "BALCON WP 12 MONTHS",
    "BALCON WP 24 MONTHS",
    "BALCON WP 48 MONTHS",
    "CLAIMS MADE PAYMENT",
    "CODE25 WILL PAY AT SALARY",
    "CUSTOMER KEPT PROMISE MADE",
    "CUSTOMER MADE PAYMENT",
    "DEFERMENT FOR IMPACTED CUSTOMERS",
    "DIGITAL COLLECT  PTP SUBSCRIBED",
    "HISTORICAL PROMISE TO PAY",
    "KSA/CUSTOMER WILL PAY AT SALARY",
    "KSA/EARLY/FINAL SETTLEMENT",
    "KSA/PAID AMOUNT",
    "KSA/PARTIAL PAYMENT",
    "KSA/PROMISE TO PAY",
    "PARTIALLY PAID",
    "PROMISE TO PAY",
    "PROMISE TO PAY PARTIALLY",
    "PROMISE TO PAY SCHEDULED",
    "REWRITE AGREED",
    "SETTLEMENT",
    "SOFTPTP",
    "WILL PAY AT SALARY",
}

# Customer is fundamentally unreachable – wrong/invalid number, line
# permanently dead/disconnected, or explicitly flagged uncontactable.
# Signals a structural contact barrier, not a single failed attempt.
# Excludes: transient failures (no answer, busy, disconnected call,
# voicemail, message left) – those only mean the customer didn't pick up
# this time, not that they are unreachable.
# Covers both autodialler (ININ-OUTBOUND-*) and manual/KSA-channel outcomes.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
NOT_REACHABLE = {
    "CUSTOMER NOT CONTACTABLE",
    "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
    "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
    "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
    "ININ-OUTBOUND-SIT-UNCALLABLE",
    "KSA/MOBILE SWITCHED OFF",
    "KSA/OUT OF SERVICE",
    "KSA/UNCONTACTABLE",
    "KSA/WRONG NUMBER",
    "LINE DISCONNECTED",
    "MOBILE SWICTHED OFF",
    "MOBILE SWITCHED OFF",
    "NOT REACHABLE",
    "OUTBOUND-INVALID-PHONE-NUMBER",
    "PHONE OUT OF SERVICE",
    "UNCONTACTABLE",
    "WRONG NO",
    "WRONG NUMBER",
}

# Customer honoured or is actively maintaining an existing promise-to-pay – a
# stronger/narrower signal than generic PROMISE_TO_PAY. Not restricted to
# a particular action_code: in practice RETAIN PTP is logged administratively (action_code
# IA) rather than against a live call, so consumers must not pre-filter to call-type
# action codes before matching this set.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RETAIN_PTP = {
    "CUSTOMER KEPT PROMISE MADE",
    "RETAIN PTP",
}

# Confirmed completed payment – distinct from a promise/commitment (PROMISE_TO_PAY) or
# an unverified claim of payment ("CLAIMS MADE PAYMENT", which stays PTP-classified).
# Drives a dedicated "paid" disposition, separate from PTP.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PAYMENT_CONFIRMED = {
    "ACCOUNT PAID",
    "CUSTOMER MADE PAYMENT",
}
