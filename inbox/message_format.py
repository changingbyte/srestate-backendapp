"""Format parsed estate dicts for WhatsApp (aligned with legacy MSG_MAPPING)."""

MSG_MAPPING = {
    "floor_space": "Carpet / size",
    "number_of_bedrooms": "BHK",
    "estate_type": "Property type",
    "estate_status": "Rent / buy",
    "area": "Area",
    "budget": "Budget",
    "apartment": "Society",
    "broker_mobile": "Contact",
    "furniture": "Furniture",
    "rent_status": "Rent status",
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
        return "(koi field parse nahi hui — raw message save hai)"
    return "\n".join(lines)


def format_estate_list(items: list[dict], max_items: int = 10) -> str:
    parts = []
    for i, item in enumerate(items[:max_items], start=1):
        parts.append(f"*{i}.*\n{format_estate_bullet(item)}")
    if len(items) > max_items:
        parts.append(f"... aur {len(items) - max_items} listings baaki hain")
    return "\n\n".join(parts)