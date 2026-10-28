"""Shared location vocabulary: travel purchases and UAE country spellings.

Used by the CASA card primary (row selection) and the location feature (evidence).
"""

from pyspark.sql import Column
from pyspark.sql import functions as F

# Airlines and air carriers, cruise lines, airlines (generic), travel agencies.
TRAVEL_MCCS = (*range(3000, 3300), 4411, 4511, 4722)

# Travel keywords for rows whose MCC is missing or generic; case-insensitive, whole words.
TRAVEL_KEYWORDS_RE = (
    r"(?i)\b(AIRLINE|AIRWAYS|AIR TICKET|FLIGHT|AIRPORT|DEPARTURE|"
    r"EMIRATES AIR|ETIHAD|FLYDUBAI|AIR ARABIA|WIZZ AIR|BOARDING PASS)\b"
)

_UAE_CODES = ("AE", "ARE", "UAE")


def is_travel(mcc: Column, *texts: Column) -> Column:
    """A travel MCC, or a travel keyword in any of ``texts``."""
    keyword = F.lit(False)
    for text in texts:
        keyword = keyword | F.coalesce(text, F.lit("")).rlike(TRAVEL_KEYWORDS_RE)
    return F.coalesce(mcc.cast("int").isin(*TRAVEL_MCCS), F.lit(False)) | keyword


def is_uae(country: Column) -> Column:
    """True for a UAE country name or code in free text (``UNITED ARAB EMIRATES``,
    ``U.A.E``, ``AE``, typos such as ``UNITER ARAB EMIRATES``), False for any other
    filled value, NULL when empty."""
    letters = F.regexp_replace(F.upper(country), "[^A-Z]", "")
    return F.when(letters == "", None).otherwise(
        letters.isin(*_UAE_CODES) | letters.contains("EMIRATES")
    )
