"""Listing vs search vs command — family WhatsApp ke saare common patterns."""

from __future__ import annotations

import re

from inbox.estate_parser import ESTATE_SIGNAL_KEYS, parse_estate_message

# Broker listing often starts like this (SAVE, even with question marks elsewhere).
_LISTING_OPENERS = re.compile(
    r"^(?:"
    r"available|for\s+sale|resale|to\s+let|new\s+project|"
    r"tenant\s+required|required\s+tenant|urgent|hot\b|"
    r"\d\s*bhk|flat\s+\d|plot\s+\d"
    r")\b",
    re.I,
)

_HAS_BROKER_PHONE = re.compile(r"\b[6-9]\d{9}\b")
_HAS_MONEY = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:cr|crore|lakh|lac|lk|k))\b|\b\d{4,8}\s*(?:pm|per\s+month)",
    re.I,
)

# Dhundhne wali baat — SAVE mat karo.
_SEARCH_OPENERS = re.compile(
    r"(?:^|\b)(?:"
    r"query|search|khojo|khojho|dhundo|dhundho|dhoondo|"
    r"buyer\s+ke\s+liye|client\s+ke\s+liye|kharidar\s+dhundo|buyer\s+dhundo|"
    r"kiraye\s+par\s+lena|tenant\s+dhundo|kirayedar\s+dhundo|"
    r"i\s+have\s+(?:a\s+)?buyer|have\s+(?:a\s+)?buyer|buyer\s+for|"
    r"koi\s+seller|seller\s+hai|any\s+seller|need\s+seller|"
    r"looking\s+for|want\s+to\s+(?:buy|rent)|need\s+(?:a\s+)?(?:flat|bhk|property|3)|"
    r"koi\s+(?:flat|bhk|property|listing)|kuch\s+mila|mila\s+kya|hai\s+kya|"
    r"is\s+there\s+any|any\s+(?:flat|bhk)"
    r")\b",
    re.I,
)

_QUESTION_MARK = re.compile(r"\?|kya\s+hai|hai\s+na\b", re.I)


def is_explicit_search(text: str) -> bool:
    return bool(_SEARCH_OPENERS.search(text))


def is_strong_listing(text: str) -> bool:
    if _LISTING_OPENERS.search(text.strip()):
        return True
    if _HAS_BROKER_PHONE.search(text) and _HAS_MONEY.search(text):
        return True
    parsed = parse_estate_message(text)
    if not parsed:
        return False
    signals = sum(1 for k in ESTATE_SIGNAL_KEYS if parsed.get(k))
    if signals < 2:
        return False
    if _HAS_BROKER_PHONE.search(text) or _HAS_MONEY.search(text):
        return True
    # Area + BHK + rent/sell keyword without search opener
    if signals >= 3:
        return True
    status = parsed.get("estate_status") or ""
    if signals >= 2 and status in ("sell", "rent", "buy", "resale", "lease"):
        return True
    return False


def should_save_not_search(text: str) -> bool:
    """True = property paste (diary save)."""
    if is_explicit_search(text):
        return False
    if _QUESTION_MARK.search(text) and not is_strong_listing(text):
        return False
    return is_strong_listing(text)