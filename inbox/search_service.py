from __future__ import annotations

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from inbox.estate_parser import parse_estate_message, parse_query_days
from inbox.models import WhatsappEstateMessage
from inbox.search_modes import SearchMode, prepare_search

STOCK_STATUSES = ("sell", "resale", "sale", "available", "book")
DEMAND_STATUSES = ("buy", "purchase")
RENT_LISTING_STATUSES = ("rent", "lease", "available")


def _status_filter(qs, statuses: tuple[str, ...]):
    q = Q()
    for s in statuses:
        q |= Q(estate_status__icontains=s)
    return qs.filter(q) if statuses else qs


def _is_tenant_requirement(row: WhatsappEstateMessage) -> bool:
    body = row.raw_body.lower()
    if "tenant required" in body or "required tenant" in body or "tenant chahiye" in body:
        return True
    rs = str((row.extracted_json or {}).get("rent_status") or "").lower()
    return rs in ("required", "tenant")


def _rent_stock_filter(qs):
    return _status_filter(qs, RENT_LISTING_STATUSES)


def _rent_demand_filter(qs):
    return _status_filter(qs, RENT_LISTING_STATUSES)


def _apply_rent_mode_rows(rows: list[WhatsappEstateMessage], mode: SearchMode) -> list[WhatsappEstateMessage]:
    if mode == SearchMode.RENT_STOCK:
        return [r for r in rows if not _is_tenant_requirement(r)]
    if mode == SearchMode.RENT_DEMAND:
        return [r for r in rows if _is_tenant_requirement(r)]
    return rows


def resolve_search_mode(mode: SearchMode, parsed_status: str | None) -> SearchMode:
    if mode in (SearchMode.STOCK, SearchMode.DEMAND, SearchMode.RENT_STOCK, SearchMode.RENT_DEMAND):
        return mode
    if parsed_status in ("rent", "lease"):
        return SearchMode.RENT_STOCK
    if parsed_status in ("buy", "purchase"):
        return SearchMode.STOCK
    if parsed_status in ("sell", "sale", "resale"):
        return SearchMode.STOCK
    if parsed_status == "required":
        return SearchMode.DEMAND
    return SearchMode.STOCK


def apply_mode_filter(qs, mode: SearchMode, parsed_status: str | None):
    if mode == SearchMode.RENT_STOCK:
        return _rent_stock_filter(qs)
    if mode == SearchMode.RENT_DEMAND:
        return _rent_demand_filter(qs)
    if mode == SearchMode.DEMAND:
        return _status_filter(qs, DEMAND_STATUSES)
    if parsed_status in ("rent", "lease") and mode == SearchMode.STOCK:
        return _rent_stock_filter(qs)
    return _status_filter(qs, STOCK_STATUSES)


def search_listings(
    query_text: str,
    days: int | None = None,
    mode: SearchMode | None = None,
) -> tuple[SearchMode, list[dict]]:
    hint_mode, cleaned = prepare_search(query_text)
    if mode is None:
        mode = hint_mode

    filters = parse_estate_message(cleaned, "") or {}
    days = days or parse_query_days(cleaned)
    mode = resolve_search_mode(mode, filters.get("estate_status"))

    qs = WhatsappEstateMessage.objects.filter(
        message_kind__in=(WhatsappEstateMessage.KIND_SAVE, WhatsappEstateMessage.KIND_ADD)
    )
    if days:
        qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))

    structured = apply_mode_filter(qs, mode, filters.get("estate_status"))

    if filters.get("area"):
        structured = structured.filter(area__icontains=filters["area"])
    if filters.get("estate_type"):
        structured = structured.filter(estate_type__icontains=filters["estate_type"])
    if filters.get("number_of_bedrooms"):
        structured = structured.filter(number_of_bedrooms=filters["number_of_bedrooms"])
    if filters.get("budget"):
        structured = structured.filter(budget__lte=filters["budget"])
    if filters.get("furniture"):
        furn = filters["furniture"][:20]
        furn_q = Q(raw_body__icontains="furnish") | Q(raw_body__icontains=furn[:12])
        with_furn = structured.filter(furn_q)
        structured = with_furn if with_furn.exists() else structured

    rows: list[WhatsappEstateMessage] = []
    if filters or mode != SearchMode.AUTO:
        rows = _apply_rent_mode_rows(
            list(structured.order_by("-created_at")[:25]),
            mode,
        )[:15]

    if not rows:
        words = [
            w
            for w in cleaned.lower().split()
            if len(w) >= 3 and w not in ("buy", "sell", "rent", "query", "khojo", "dhundo")
        ][:8]
        if words:
            q = Q()
            for w in words:
                q |= Q(raw_body__icontains=w) | Q(area__icontains=w) | Q(apartment__icontains=w)
            fallback = apply_mode_filter(qs.filter(q), mode, filters.get("estate_status"))
            rows = _apply_rent_mode_rows(
                list(fallback.order_by("-created_at")[:25]),
                mode,
            )[:15]

    return mode, [r.extracted_json for r in rows]