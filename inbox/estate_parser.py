"""Parse unstructured WhatsApp real-estate text (lexicon + regex, no Mongo)."""

from __future__ import annotations

import json
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone

_LEXICON_CACHE: dict | None = None

ESTATE_SIGNAL_KEYS = (
    "area",
    "estate_type",
    "estate_status",
    "number_of_bedrooms",
    "apartment",
)


def load_lexicon() -> dict:
    global _LEXICON_CACHE
    if _LEXICON_CACHE is None:
        path = Path(settings.LEXICON_PATH)
        _LEXICON_CACHE = json.loads(path.read_text(encoding="utf-8"))
    return _LEXICON_CACHE


def _normalise_aliases(text_lower: str, lexicon: dict) -> str:
    """Replace broker spellings with canonical lexicon terms before matching."""
    for alias, canonical in sorted(
        lexicon.get("aliases", {}).items(), key=lambda item: len(item[0]), reverse=True
    ):
        pattern = rf"(?<!\w){re.escape(alias.lower())}(?!\w)"
        text_lower = re.sub(pattern, canonical.lower(), text_lower)
    return text_lower


def _match_lexicon(text_lower: str, field: str, lexicon: dict) -> str | None:
    # The JSON lists stay alphabetic for maintainability; longest terms win matches.
    for term in sorted(lexicon.get(field, []), key=len, reverse=True):
        if term.lower() in text_lower:
            return term.lower()
    return None


def _parse_budget(text: str) -> int | None:
    text_lower = text.lower().replace(",", "")
    patterns = [
        (r"(\d+(?:\.\d+)?)\s*(?:cr|crore)", 10_000_000),
        (r"(\d+(?:\.\d+)?)\s*(?:lk|lac|lakh|lacs)", 100_000),
        (r"(\d+(?:\.\d+)?)\s*k\s*(?:per month|/month|pm\b)?", 1_000),
        (r"(?:budget|rs|₹)\s*(\d{4,12})", 1),
        (r"(\d{4,9})\s*(?:per month|/month|pm\b)", 1),
    ]
    for pattern, multiplier in patterns:
        m = re.search(pattern, text_lower)
        if m:
            return int(float(m.group(1)) * multiplier)
    numbers = re.findall(r"\b([1-9]\d{3,8})\b", text_lower)
    if numbers:
        return int(numbers[0])
    return None


def _parse_bhk(text_lower: str) -> int | None:
    m = re.search(r"(\d)\s*bhk", text_lower)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d)\s*bed", text_lower)
    if m:
        return int(m.group(1))
    return None


def _parse_broker_mobile(text: str) -> str | None:
    nums = re.findall(r"\b(\d{10})\b", text)
    return nums[0] if nums else None


def parse_estate_message(body: str, sender_mobile: str = "") -> dict | None:
    text = body.strip()
    if not text:
        return None
    raw_text_lower = text.lower()
    lex = load_lexicon()
    text_lower = _normalise_aliases(raw_text_lower, lex)

    parsed: dict = {}
    for field in ("area", "estate_status", "apartment", "furniture", "rent_status"):
        hit = _match_lexicon(text_lower, field, lex)
        if hit:
            parsed[field] = hit

    estate_type = _match_lexicon(text_lower, "property_type", lex)
    if estate_type:
        parsed["estate_type"] = estate_type

    bhk = _parse_bhk(raw_text_lower)
    if bhk is not None:
        parsed["number_of_bedrooms"] = bhk
        # A bare "3 BHK" is broker shorthand for a residential flat.
        parsed.setdefault("estate_type", "flat")

    budget = _parse_budget(text)
    if budget is not None:
        parsed["budget"] = budget

    broker = _parse_broker_mobile(text)
    if broker:
        parsed["broker_mobile"] = broker
    elif sender_mobile:
        parsed["broker_mobile"] = sender_mobile

    status_aliases = {
        "book": "sell",
        "booking": "sell",
        "lease": "rent",
        "new project": "sell",
        "purchase": "buy",
        "resale": "sell",
        "sale": "sell",
        "to let": "rent",
    }
    if parsed.get("estate_status") in status_aliases:
        parsed["estate_status"] = status_aliases[parsed["estate_status"]]

    signals = sum(1 for k in ESTATE_SIGNAL_KEYS if parsed.get(k))
    if signals == 0:
        return None
    return parsed


def parse_multi_estate(body: str, sender_mobile: str) -> list[dict]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
    if len(blocks) <= 1:
        one = parse_estate_message(body, sender_mobile)
        return [one] if one else []

    results = []
    for block in blocks:
        item = parse_estate_message(block, sender_mobile)
        if item:
            results.append(item)
    return results


def parse_query_days(body: str) -> int | None:
    lower = body.lower()
    m = re.search(r"last\s+(\d+)\s+days?", lower)
    if m:
        return int(m.group(1))
    if "last month" in lower:
        return 30
    m = re.search(r"pichle\s+(\d+)\s*din", lower)
    if m:
        return int(m.group(1))
    if "pichle mahine" in lower or "pichla mahina" in lower:
        return 30
    if "is hafte" in lower or "is week" in lower:
        return 7
    return None


_HELP_WORDS = frozenset(
    {
        "help",
        "madad",
        "madat",
        "sahayata",
        "sahaayata",
        "kaise",
        "kese",
        "batao",
        "bataiye",
        "samjhao",
        "samjhaye",
        "kya karna hai",
    }
)

_GREETINGS = frozenset(
    {
        "hi",
        "hii",
        "hey",
        "hello",
        "hola",
        "namaste",
        "namaskar",
        "good morning",
        "good evening",
        "good afternoon",
        "gm",
        "kaise ho",
        "kese ho",
    }
)

_QUERY_PREFIXES = (
    "query",
    "khojo",
    "khojho",
    "dhoondo",
    "dhundo",
    "dhundho",
    "dhundhna",
)

_ADD_PREFIXES = ("add", "jodo", "save karo", "save")

_FOLLOWUP_PREFIXES = ("yaad", "yaad dilao", "kal phone", "followup", "reminder")

_PENDING_PREFIXES = ("pending", "meri followup", "meri follow up", "due list", "aaj ka kaam")

_LEADS_PREFIXES = (
    "meri list",
    "meri leads",
    "mera kaam",
    "kya bacha",
    "pending",
    "aaj ka kaam",
    "meri enquiry",
)

_ASSIGN_PREFIXES = ("de do", "dedo", "bhej do", "bhejo", "assign", "sambhalo", "isko do")

_DONE_PREFIXES = ("done", "ho gaya", "complete", "khatam", "ho gya")


def is_greeting_only(body: str) -> bool:
    text = body.strip().lower().rstrip("!?.。 ")
    if text in _GREETINGS:
        return True
    for g in ("good morning", "good evening", "good afternoon"):
        if text == g or text.startswith(g + " "):
            return True
    return False


def wants_help(body: str) -> bool:
    lower = body.strip().lower()
    if lower in _HELP_WORDS:
        return True
    hints = (
        "save kaise",
        "kaise save",
        "kaise bheju",
        "kya likhu",
        "kya likhe",
        "property kaise",
        "yeh kaise chalega",
        "samjha do",
    )
    return any(h in lower for h in hints)


def strip_command_prefix(body: str) -> tuple[str, str | None]:
    """Returns (remainder, command) where command is query|add|help|greet or None."""
    text = body.strip()
    lower = text.lower()

    if is_greeting_only(text):
        return "", "greet"
    if lower in _HELP_WORDS or wants_help(text):
        return "", "help"

    for prefix in _QUERY_PREFIXES:
        if lower == prefix:
            return "", "query"
        if lower.startswith(prefix + " "):
            return text[len(prefix) :].strip(), "query"

    for prefix in _ADD_PREFIXES:
        if lower == prefix:
            return "", "add"
        if lower.startswith(prefix + " "):
            return text[len(prefix) :].strip(), "add"
        if lower.startswith(prefix + "\n"):
            return text[len(prefix) :].strip(), "add"

    for prefix in _FOLLOWUP_PREFIXES:
        if lower == prefix:
            return "", "followup"
        if lower.startswith(prefix + " "):
            return text[len(prefix) :].strip(), "followup"

    for prefix in _LEADS_PREFIXES:
        if lower == prefix or lower.startswith(prefix + " "):
            return "", "leads"

    for prefix in _ASSIGN_PREFIXES:
        if lower.startswith(prefix + " "):
            return text[len(prefix) :].strip(), "assign"

    for prefix in _PENDING_PREFIXES:
        if lower == prefix or lower.startswith(prefix + " "):
            return "", "leads"

    for prefix in _DONE_PREFIXES:
        if lower.startswith(prefix + " "):
            return text[len(prefix) :].strip(), "done"
        if lower == prefix and prefix in ("done", "ho gaya", "ho gya", "complete", "khatam"):
            return "", "done"

    return text, None
