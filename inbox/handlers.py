from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from inbox.estate_parser import (
    parse_estate_message,
    parse_multi_estate,
    parse_query_days,
    strip_command_prefix,
)
from inbox.message_format import format_estate_bullet, format_estate_list
from inbox.models import WhatsappEstateMessage
from inbox.twilio_client import send_whatsapp
from inbox.user_messages import (
    ADD_OK_PREFIX,
    HELP_TEXT,
    QUERY_EMPTY,
    QUERY_OK_PREFIX,
    QUERY_PARSE_FAIL,
    REJECT_MSG,
    SAVE_OK,
    WELCOME_TEXT,
    WHITELIST_MSG,
)


def _model_from_parsed(parsed: dict, raw: str, mobile: str, kind: str, sid: str = "") -> WhatsappEstateMessage:
    return WhatsappEstateMessage.objects.create(
        raw_body=raw,
        sender_mobile=mobile,
        twilio_sid=sid,
        message_kind=kind,
        estate_status=parsed.get("estate_status") or "",
        estate_type=parsed.get("estate_type") or "",
        area=parsed.get("area") or "",
        budget=parsed.get("budget"),
        number_of_bedrooms=parsed.get("number_of_bedrooms"),
        apartment=parsed.get("apartment") or "",
        broker_mobile=parsed.get("broker_mobile") or "",
        extracted_json=parsed,
    )


def query_archive(filters: dict, days: int | None, sender: str | None) -> list[dict]:
    qs = WhatsappEstateMessage.objects.filter(
        message_kind__in=(WhatsappEstateMessage.KIND_SAVE, WhatsappEstateMessage.KIND_ADD)
    )
    if days:
        qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))
    if sender:
        qs = qs.filter(sender_mobile=sender)

    if filters.get("area"):
        qs = qs.filter(area__icontains=filters["area"])
    if filters.get("estate_type"):
        qs = qs.filter(estate_type__icontains=filters["estate_type"])
    if filters.get("estate_status"):
        qs = qs.filter(estate_status__icontains=filters["estate_status"])
    if filters.get("number_of_bedrooms"):
        qs = qs.filter(number_of_bedrooms=filters["number_of_bedrooms"])
    if filters.get("budget"):
        qs = qs.filter(budget__lte=filters["budget"])

    limit = settings.QUERY_MAX_RESULTS
    return [row.extracted_json for row in qs[:limit]]


def handle_inbound(from_mobile: str, body: str, twilio_sid: str = "") -> str:
    if from_mobile not in settings.FAMILY_ALLOWED_MOBILES:
        return WHITELIST_MSG

    remainder, command = strip_command_prefix(body)

    if command == "greet":
        return WELCOME_TEXT

    if command == "help":
        return HELP_TEXT

    if command == "query":
        filters = parse_estate_message(remainder, from_mobile) or {}
        days = parse_query_days(remainder)
        if not filters and not days:
            return QUERY_PARSE_FAIL
        rows = query_archive(filters, days, sender=None)
        if not rows:
            return QUERY_EMPTY
        return QUERY_OK_PREFIX + format_estate_list(rows, settings.QUERY_MAX_RESULTS)

    if command == "add":
        items = parse_multi_estate(remainder, from_mobile)
        if not items:
            return REJECT_MSG
        for item in items:
            _model_from_parsed(item, remainder, from_mobile, WhatsappEstateMessage.KIND_ADD, twilio_sid)
        return ADD_OK_PREFIX.format(count=len(items)) + format_estate_list(items, min(3, len(items)))

    parsed = parse_estate_message(body, from_mobile)
    if not parsed:
        return REJECT_MSG

    _model_from_parsed(parsed, body, from_mobile, WhatsappEstateMessage.KIND_SAVE, twilio_sid)
    return SAVE_OK + format_estate_bullet(parsed)


def process_and_reply(from_mobile: str, body: str, twilio_sid: str = "") -> None:
    reply = handle_inbound(from_mobile, body, twilio_sid)
    send_whatsapp(from_mobile, reply)