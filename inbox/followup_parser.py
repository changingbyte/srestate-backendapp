"""Parse follow-up / reminder messages (Hinglish dates)."""

from __future__ import annotations

import re
from datetime import datetime, time, timedelta

from django.utils import timezone


def _default_due_time() -> time:
    return time(9, 0)


def parse_followup_datetime(text: str) -> datetime | None:
    """Parse kal/aaj/dd-mm and optional time from the message."""
    lower = text.lower()
    now = timezone.localtime()

    due_date = now.date()
    due_time = _default_due_time()

    if re.search(r"\bkal\b", lower):
        due_date = (now + timedelta(days=1)).date()
    elif re.search(r"\bparso\b", lower):
        due_date = (now + timedelta(days=2)).date()
    elif re.search(r"\baaj\b", lower):
        due_date = now.date()

    dm = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", text)
    if dm:
        d, m = int(dm.group(1)), int(dm.group(2))
        y = int(dm.group(3)) if dm.group(3) else now.year
        if y < 100:
            y += 2000
        try:
            due_date = datetime(y, m, d).date()
        except ValueError:
            pass

    tm = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", lower)
    if tm:
        hour = int(tm.group(1))
        minute = int(tm.group(2) or 0)
        ampm = tm.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        if not ampm and hour <= 12 and "subah" not in lower and "sham" not in lower:
            if "sham" in lower or "evening" in lower:
                if hour < 12:
                    hour += 12
        due_time = time(hour, minute)

    naive = datetime.combine(due_date, due_time)
    return timezone.make_aware(naive, timezone.get_current_timezone())


def parse_followup_note(remainder: str) -> tuple[datetime | None, str]:
    """Strip date hints; return due datetime and human note."""
    due = parse_followup_datetime(remainder)
    note = remainder
    for pat in (
        r"\bkal\b",
        r"\bparso\b",
        r"\baaj\b",
        r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
        r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b",
    ):
        note = re.sub(pat, "", note, flags=re.IGNORECASE)
    note = re.sub(r"\s+", " ", note).strip(" -,:")
    return due, note or "Follow-up"