"""Format parsed estate dicts for WhatsApp (aligned with legacy MSG_MAPPING)."""

MSG_MAPPING = {
    "floor_space": "FLOOR SPACE IS",
    "number_of_bedrooms": "BEDROOMS",
    "estate_type": "TYPE",
    "estate_status": "STATUS",
    "area": "AREA",
    "budget": "BUDGET",
    "apartment": "SOCIETY",
    "broker_mobile": "CONTACT",
    "furniture": "FURNITURE",
    "rent_status": "RENT STATUS",
}


def _scalar(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def format_estate_bullet(parsed: dict) -> str:
    lines = []
    for key, label in MSG_MAPPING.items():
        val = _scalar(parsed.get(key))
        if val not in (None, "", [], 0, "0"):
            lines.append(f"{label}: {val}")
    if not lines:
        return "(no structured fields)"
    return "\n".join(lines)


def format_estate_list(items: list[dict], max_items: int = 10) -> str:
    parts = []
    for i, item in enumerate(items[:max_items], start=1):
        parts.append(f"*{i}.*\n{format_estate_bullet(item)}")
    if len(items) > max_items:
        parts.append(f"... and {len(items) - max_items} more")
    return "\n\n".join(parts)