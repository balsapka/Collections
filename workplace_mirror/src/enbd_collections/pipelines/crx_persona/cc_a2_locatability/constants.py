"""DCORE result description allowlists for the cc_a2_locatability pipeline.

Centralised here so that result-name allowlists can be inspected and updated
without navigating node logic.

All allowlists use result_name (szresultname), carried directly on
dcore_prm_followup_outcomes — not result_code — because descriptions are
self-documenting and stable across DCORE deployments.

Constants:
    _RIGHT_PARTY_CONTACT_RESULT_NAMES  — confirmed two-way contact (any channel)
    _REFUSING_RESULT_NAMES             — explicit refusal/hang-up/dispute signals
    _RINGING_RESULT_NAMES              — ringing no-answer (live channel, no pickup)
    _DECEASED_RESULT_NAMES             — confirmed or claimed deceased
    _DEPARTURE_RESULT_NAMES            — contact record states customer left UAE
    _FIELD_VISIT_RESULT_NAMES          — completed field visits only
    _HARDSHIP_RESULT_NAMES             — hardship / special-case signals
    _PROMISE_TO_PAY_RESULT_NAMES       — PTP and payment commitments
    _NOT_REACHABLE_RESULT_NAMES        — structurally invalid/dead contact info
    _RETAIN_PTP_RESULT_NAMES           — customer honoured/maintained an existing PTP
    _PAYMENT_CONFIRMED_RESULT_NAMES    — confirmed completed payment (not a promise)
"""

# Comprehensive right-party contact (RPC) set — every result_name that confirms
# the account holder was personally reached, regardless of result_category.
# Covers: payment commitments (PTP), payments made, verbal engagement/refusal,
# customer-disclosed circumstances, customer-initiated requests, and physical
# field-visit contact.
# Excludes: third-party messages, scheduling/routing notes, administrative
# referrals, system/technical codes, deceased status, and dunning letters.
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(_RIGHT_PARTY_CONTACT_RESULT_NAMES)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RIGHT_PARTY_CONTACT_RESULT_NAMES = {
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


# Explicit refusal signals — result names where confirmed right-party contact was
# made but the customer explicitly refused, hung up, or disputed.
# Subset of _RIGHT_PARTY_CONTACT_RESULT_NAMES (every entry here also confirms contact).
# Excludes settlement-seeking behaviour (engagement) and autodialler intermediates.
#
# Drives refusing_n counter → non_cooperative state (confirmed contact + refusal).
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(_REFUSING_RESULT_NAMES)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_REFUSING_RESULT_NAMES = {
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

# Ringing no-answer signals — phone rang at the customer end but was not answered.
# Excludes LINE BUSY (transient, does not indicate call screening).
# Drives ringing_n counter → avoiding state when ≥3 ringing events and line is live.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RINGING_RESULT_NAMES = {
    "RINGING NO REPLY",
    "RINGING NO RESPONSE",
}

# Confirmed or claimed deceased — drives deceased_flag → highest-priority state.
# Retained in _HARDSHIP_RESULT_NAMES as well (hardship_flag still used for routing).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_DECEASED_RESULT_NAMES = {
    "DECEASED",
    "DECEASED CLAIMED",
    "DECEASED OR EXPIRED",
    "DECEASED/EXPIRED",
    "KSA/DECEASED",
}

# Contact records explicitly stating customer has left UAE.
# Contributes to dcore_departure_flag — additional departure evidence
# from within the delinquency window.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_DEPARTURE_RESULT_NAMES = {
    "KSA/NATHEER-CROSSING FINAL EXIT VISA",
    "LEFT THE COUNTRY",
    "OUT OF COUNTRY",
}

# Completed field visit — excluded from phone rpc_n; tracked via field_visit_flag.
# Scheduling/workflow events (FIELD VISIT REJECTED/SENT/RE FIELD VISIT REQUIRED/
# REQUEST FOR FIELD VISIT) are excluded — they do not confirm contact.
# Note: FIELD VISIT DONE is also in _RIGHT_PARTY_CONTACT_RESULT_NAMES, so it
# contributes to contact_confirmed_n automatically.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_FIELD_VISIT_RESULT_NAMES = {
    "FIELD VISIT DONE",
}

# Hardship / special cases — accounts requiring non-standard treatment.
# Covers: death (confirmed and claimed), permanent disability, incarceration,
# bankruptcy, employment loss/termination, and income hardship signals.
# Flag separately — do not count as regular unreachable or RPC.
# Includes KSA-channel equivalents and additional signals from the data
# not in the reference doc (MEDICAL ISSUES, SALARY DELAY, UNPAID LEAVE).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_HARDSHIP_RESULT_NAMES = {
    "BANKRUPTCY",
    "CUSTOMER HAVE NO JOB",
    "CUSTOMER IS IN JAIL",
    "CUSTOMER IS PERMANENT DISABLED",
    "CUSTOMER TERMINATED",
    "DECEASED",
    "DECEASED CLAIMED",
    "DECEASED OR EXPIRED",
    "DECEASED/EXPIRED",
    "JOB LOST",
    "KSA/DECEASED",
    "KSA/DISABLED",
    "KSA/JOB LOST",
    "LEFT JOB",
    "MEDICAL ISSUES",
    "NIL SALARY",
    "SALARY DELAY",
    "SALARY REDUCTION",
    "UNPAID LEAVE",
}

# Promise to pay or willingness to pay — result names signalling the customer
# has committed to pay, made a payment arrangement, or actually paid.
# Covers: all PTP-category outcomes, actual payments (SUC), and INT entries
# where the customer verbally committed or agreed to a specific arrangement
# (balance consolidation, rewrite, deferment, settlement, salary-date promise).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_PROMISE_TO_PAY_RESULT_NAMES = {
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

# Customer is fundamentally unreachable — wrong/invalid number, line
# permanently dead/disconnected, or explicitly flagged uncontactable.
# Signals a structural contact barrier, not a single failed attempt.
# Excludes: transient failures (no answer, busy, disconnected call,
# voicemail, message left) — those only mean the customer didn't pick up
# this time, not that they are unreachable.
# Covers both autodialler (ININ-OUTBOUND-*) and manual/KSA-channel outcomes.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_NOT_REACHABLE_RESULT_NAMES = {
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

# Customer honoured or is actively maintaining an existing promise-to-pay — a
# stronger/narrower signal than generic _PROMISE_TO_PAY_RESULT_NAMES. Not restricted to
# a particular action_code: in practice RETAIN PTP is logged administratively (action_code
# IA) rather than against a live call, so consumers must not pre-filter to call-type
# action codes before matching this set.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RETAIN_PTP_RESULT_NAMES = {
    "CUSTOMER KEPT PROMISE MADE",
    "RETAIN PTP",
}

# Confirmed completed payment — distinct from a promise/commitment (_PROMISE_TO_PAY_
# RESULT_NAMES) or an unverified claim of payment ("CLAIMS MADE PAYMENT", which stays
# PTP-classified). Drives a dedicated "paid" disposition, separate from PTP.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_PAYMENT_CONFIRMED_RESULT_NAMES = {
    "ACCOUNT PAID",
    "CUSTOMER MADE PAYMENT",
}
