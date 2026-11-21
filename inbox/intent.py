"""Natural Hindi / Hinglish intent — bina strict commands ke."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from inbox.estate_parser import is_greeting_only, strip_command_prefix, wants_help
from inbox.message_classify import is_explicit_search, should_save_not_search
from inbox.search_modes import (
    _bare_re,
    _DEMAND_PHRASES,
    _RENT_DEMAND_PHRASES,
    _RENT_STOCK_PHRASES,
    _STOCK_PHRASES,
)


class Intent(Enum):
    GREET = "greet"
    HELP = "help"
    LIST = "list"
    TEAM = "team"
    ADMIN_REMOVE = "admin_remove"
    ADMIN_ADD = "admin_add"
    SEARCH = "search"
    ASSIGN = "assign"
    DONE = "done"
    REMIND = "remind"
    MULTI_SAVE = "multi_save"
    SAVE = "save"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    intent: Intent
    remainder: str
    diary_number: int | None = None


_DONE_RE = re.compile(
    r"^(?:ho\s*gaya|ho\s*gya|ho\s*chuka|ho\s*chuki|khatam|complete)(?:\s+(\d+))?\s*$",
    re.I,
)
_DONE_INLINE_RE = re.compile(
    r"(?:^|\s)(?:ho\s*gaya|ho\s*gya|ho\s*chuka)\s+(\d+)\s*$",
    re.I,
)
_ASSIGN_RE = re.compile(
    r"(?:^|\s)(?:de\s*do|dedo|bhej\s*do|bhejo|sambhalo|assign|isko\s*do)\s+(.+)$",
    re.I,
)
_SEARCH_RE = re.compile(
    r"(?:^|\s)(?:khojo|khojho|dhundo|dhundho|dhoondo|dhundhna|search|query)\s+(.+)$",
    re.I,
)
_SEARCH_LOOSE_RE = re.compile(r"\b(khojo|khojho|dhundo|dhundho|dhoondo)\b", re.I)
_BUYER_CLIENT_RE = re.compile(
    r"\b(i\s+have\s+(a\s+)?buyer|have\s+(a\s+)?buyer|buyer\s+for|buyer\s+hai|client\s+for)\b",
    re.I,
)
_SELLER_STOCK_RE = re.compile(
    r"\b(koi\s+seller|seller\s+hai|any\s+seller|need\s+seller|seller\s+for|seller\s+mila)\b",
    re.I,
)
_LIST_RE = re.compile(
    r"(?:^|\s)(?:meri\s+list|mera\s+kaam|kya\s+bacha|aaj\s+ka\s+kaam|meri\s+enquiry|meri\s+leads|pending)(?:\s|$)",
    re.I,
)
_TEAM_RE = re.compile(r"^(?:team|parivar|family)\s*$", re.I)
_ADMIN_REMOVE_RE = re.compile(r"^(?:hatado|remove|nikalo)\s+(.+)$", re.I)
_ADMIN_ADD_RE = re.compile(r"^(?:jodo|add\s+member?)\s+(\d{10}\s+.+)$", re.I)
_REMIND_RE = re.compile(
    r"(?:^|\s)(?:yaad|yaad\s*dilao|kal\s+phone|reminder|followup)\s+(.+)$",
    re.I,
)


def _extract_diary_number(text: str) -> int | None:
    m = re.search(r"(?:no\.?|number|#)\s*(\d{1,6})", text, re.I)
    if m:
        return int(m.group(1))
    parts = text.split()
    for p in parts:
        if p.isdigit() and len(p) <= 4:
            return int(p)
    return None


def detect_intent(body: str) -> ParsedIntent:
    text = body.strip()
    if not text:
        return ParsedIntent(Intent.UNKNOWN, "")

    lower = text.lower()

    if is_greeting_only(text):
        return ParsedIntent(Intent.GREET, "")
    if lower in ("madad", "help", "batao", "bataiye", "samjhao") or wants_help(text):
        return ParsedIntent(Intent.HELP, "")

    m = _LIST_RE.search(lower)
    if m:
        return ParsedIntent(Intent.LIST, "")

    if _TEAM_RE.match(text):
        return ParsedIntent(Intent.TEAM, "")

    m = _ADMIN_REMOVE_RE.match(text)
    if m:
        return ParsedIntent(Intent.ADMIN_REMOVE, m.group(1).strip())

    m = _ADMIN_ADD_RE.match(text)
    if m:
        return ParsedIntent(Intent.ADMIN_ADD, m.group(1).strip())

    m = _DONE_RE.match(text) or _DONE_INLINE_RE.search(text)
    if m:
        num = m.group(1) if m.lastindex else None
        return ParsedIntent(Intent.DONE, text, diary_number=int(num) if num else None)

    m = _ASSIGN_RE.search(text)
    if m:
        return ParsedIntent(Intent.ASSIGN, m.group(1).strip())

    m = _SEARCH_RE.search(text)
    if m:
        return ParsedIntent(Intent.SEARCH, text)

    if _BUYER_CLIENT_RE.search(text) or _SELLER_STOCK_RE.search(text):
        return ParsedIntent(Intent.SEARCH, text)

    m = _REMIND_RE.search(text)
    if m:
        return ParsedIntent(Intent.REMIND, m.group(1).strip())

    # Legacy prefixes (query / add / de do at start)
    remainder, command = strip_command_prefix(body)
    cmd_map = {
        "greet": Intent.GREET,
        "help": Intent.HELP,
        "leads": Intent.LIST,
        "pending": Intent.LIST,
        "assign": Intent.ASSIGN,
        "done": Intent.DONE,
        "query": Intent.SEARCH,
        "add": Intent.MULTI_SAVE,
        "followup": Intent.REMIND,
    }
    if command and command in cmd_map:
        diary = None
        if command == "done" and remainder:
            diary = _extract_diary_number(remainder) or (
                int(remainder.split()[0]) if remainder.split()[0].isdigit() else None
            )
        return ParsedIntent(cmd_map[command], remainder, diary_number=diary)

    for bare in (
        _bare_re(_RENT_STOCK_PHRASES),
        _bare_re(_RENT_DEMAND_PHRASES),
        _bare_re(_STOCK_PHRASES),
        _bare_re(_DEMAND_PHRASES),
    ):
        m = bare.match(text)
        if m:
            return ParsedIntent(Intent.SEARCH, text)

    if is_explicit_search(text) or _SEARCH_LOOSE_RE.search(text):
        return ParsedIntent(Intent.SEARCH, text)
    if any(p in lower for p in ("mila kya", "koi listing")):
        return ParsedIntent(Intent.SEARCH, text)
    if _BUYER_CLIENT_RE.search(text) or _SELLER_STOCK_RE.search(text):
        return ParsedIntent(Intent.SEARCH, text)

    if should_save_not_search(text):
        return ParsedIntent(Intent.SAVE, text)

    return ParsedIntent(Intent.SEARCH, text)