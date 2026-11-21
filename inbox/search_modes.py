"""Search: sale buy/sell + rent lena/dena."""

from __future__ import annotations

import re
from enum import Enum


class SearchMode(Enum):
    AUTO = "auto"
    STOCK = "stock"  # sale: client ko dikhao (sell listings)
    DEMAND = "demand"  # sale: kharidar dhundo (buy enquiry)
    RENT_STOCK = "rent_stock"  # kiraye par rehna — rent listings
    RENT_DEMAND = "rent_demand"  # kiraye par dena — tenant chahiye


_STOCK_PHRASES = (
    "buyer ke liye",
    "client ke liye",
    "customer ke liye",
    "kharidar ko",
    "kharidne wale ko",
    "dikhana hai",
    "option chahiye",
    "options chahiye",
    "client ko",
    "i have a buyer",
    "i have buyer",
    "have a buyer",
    "have buyer",
    "buyer for",
    "buyer hai",
    "koi seller",
    "seller hai",
    "any seller",
    "need seller",
    "seller for",
    "looking for",
    "need flat",
    "need 3bhk",
    "want to buy",
    "want to rent",
    "koi flat",
)

_DEMAND_PHRASES = (
    "kharidar dhundo",
    "buyer dhundo",
    "buyer chahiye",
    "kharidar chahiye",
    "enquiry dhundo",
    "mere flat",
    "mera flat",
    "flat bech",
    "bech raha",
    "bechna hai",
    "sale kar",
    "sale hai",
    "kharidi enquiry",
    "purchase enquiry",
)

# Kiraye par rehna / rent lena (tenant)
_RENT_STOCK_PHRASES = (
    "kiraye par lena",
    "kiray par lena",
    "rent lena",
    "rent chahiye",
    "kiraya chahiye",
    "kiraye par rehna",
    "rehna hai",
    "kirayedar ban",
    "rent par",
    "client ko rent",
)

# Kiraye par dena / tenant dhundo (landlord)
_RENT_DEMAND_PHRASES = (
    "kiraye par dena",
    "kiray par dena",
    "tenant chahiye",
    "tenant dhundo",
    "kirayedar dhundo",
    "kirayedar chahiye",
    "rent out",
    "rent dena",
    "kiraya dena",
    "leta do",
)


def _alt(phrases: tuple[str, ...]) -> str:
    return "|".join(re.escape(p) for p in sorted(phrases, key=len, reverse=True))


def _trigger_re(phrases: tuple[str, ...]) -> re.Pattern:
    return re.compile(
        r"^(?:khojo|khojho|dhundo|dhundho|dhoondo|dhundhna|search|query|enquiry)\s+"
        rf"({_alt(phrases)})\s+(.+)$",
        re.I | re.DOTALL,
    )


def _bare_re(phrases: tuple[str, ...]) -> re.Pattern:
    return re.compile(rf"^({_alt(phrases)})\s+(.+)$", re.I)


_TRIGGERS = (
    (_trigger_re(_RENT_STOCK_PHRASES), SearchMode.RENT_STOCK),
    (_trigger_re(_RENT_DEMAND_PHRASES), SearchMode.RENT_DEMAND),
    (_trigger_re(_STOCK_PHRASES), SearchMode.STOCK),
    (_trigger_re(_DEMAND_PHRASES), SearchMode.DEMAND),
    (_bare_re(_RENT_STOCK_PHRASES), SearchMode.RENT_STOCK),
    (_bare_re(_RENT_DEMAND_PHRASES), SearchMode.RENT_DEMAND),
    (_bare_re(_STOCK_PHRASES), SearchMode.STOCK),
    (_bare_re(_DEMAND_PHRASES), SearchMode.DEMAND),
)


def prepare_search(body: str) -> tuple[SearchMode, str]:
    text = body.strip()
    lower = text.lower()

    for pattern, mode in _TRIGGERS:
        m = pattern.match(text)
        if m:
            return mode, m.group(m.lastindex).strip()

    mode = SearchMode.AUTO
    cleaned = text
    phrase_groups = (
        (_RENT_STOCK_PHRASES, SearchMode.RENT_STOCK),
        (_RENT_DEMAND_PHRASES, SearchMode.RENT_DEMAND),
        (_STOCK_PHRASES, SearchMode.STOCK),
        (_DEMAND_PHRASES, SearchMode.DEMAND),
    )
    for phrases, picked in phrase_groups:
        for p in phrases:
            if p in lower:
                mode = picked
                cleaned = re.sub(re.escape(p), " ", cleaned, flags=re.I)
                break
        if mode != SearchMode.AUTO:
            break

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(
        r"^(?:khojo|khojho|dhundo|dhundho|dhoondo|dhundhna|search|query|enquiry)\s+",
        "",
        cleaned,
        flags=re.I,
    ).strip()
    return mode, cleaned or text