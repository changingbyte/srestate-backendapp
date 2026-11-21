"""Property ko simple Hindi mein dikhana."""

MSG_MAPPING = {
    "floor_space": "Nikashi / size",
    "number_of_bedrooms": "BHK (kamre)",
    "estate_type": "Kis type ki",
    "estate_status": "Rent ya bechna",
    "area": "Area / ilaka",
    "budget": "Daam / budget",
    "apartment": "Society / building",
    "broker_mobile": "Phone number",
    "furniture": "Furniture",
    "rent_status": "Rent detail",
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
        return "Poora message diary mein save hai."
    return "\n".join(lines)


def format_estate_list(items: list[dict], max_items: int = 10) -> str:
    parts = []
    for i, item in enumerate(items[:max_items], start=1):
        parts.append(f"*{i}.*\n{format_estate_bullet(item)}")
    if len(items) > max_items:
        parts.append(f"... aur {len(items) - max_items} aur hain")
    return "\n\n".join(parts)