from __future__ import annotations

from django.conf import settings

from inbox.estate_parser import parse_estate_message, parse_multi_estate, parse_query_days
from inbox.followup_parser import parse_followup_note
from inbox.intent import Intent, detect_intent
from inbox.family_access import is_family_allowed
from inbox.family_admin import handle_add_member, handle_remove_member, handle_team
from inbox.lead_service import (
    assign_lead,
    complete_lead,
    create_lead_from_listing,
    format_my_leads,
    resolve_lead_for_reminder,
    save_reply_with_lead,
    schedule_lead_action,
)
from inbox.message_format import format_estate_list
from inbox.models import WhatsappEstateMessage
from inbox.search_service import search_listings
from inbox.twilio_client import send_whatsapp
from inbox.search_modes import SearchMode
from inbox.user_messages import (
    ADD_OK_PREFIX,
    HELP_TEXT,
    QUERY_EMPTY,
    QUERY_EMPTY_DEMAND,
    QUERY_EMPTY_RENT_DEMAND,
    QUERY_EMPTY_RENT_STOCK,
    QUERY_EMPTY_STOCK,
    QUERY_OK_DEMAND,
    QUERY_OK_PREFIX,
    QUERY_OK_RENT_DEMAND,
    QUERY_OK_RENT_STOCK,
    QUERY_OK_STOCK,
    QUERY_PARSE_FAIL,
    REJECT_MSG,
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


def handle_inbound(from_mobile: str, body: str, twilio_sid: str = "") -> str:
    if not is_family_allowed(from_mobile):
        return WHITELIST_MSG

    parsed_intent = detect_intent(body)
    intent = parsed_intent.intent
    remainder = parsed_intent.remainder

    if intent == Intent.GREET:
        return WELCOME_TEXT

    if intent == Intent.HELP:
        return HELP_TEXT

    if intent == Intent.LIST:
        return format_my_leads(from_mobile)

    if intent == Intent.TEAM:
        return handle_team(from_mobile)

    if intent == Intent.ADMIN_REMOVE:
        return handle_remove_member(from_mobile, remainder)

    if intent == Intent.ADMIN_ADD:
        return handle_add_member(from_mobile, remainder)

    if intent == Intent.ASSIGN:
        return assign_lead(from_mobile, remainder)

    if intent == Intent.DONE:
        lid = parsed_intent.diary_number
        return complete_lead(from_mobile, lid)

    if intent == Intent.SEARCH:
        # Poora message — warna "buyer ke liye / kharidar dhundo" ka mode kho jata hai
        q = body.strip()
        days = parse_query_days(q)
        if len(q.split()) < 2 and not days:
            return QUERY_PARSE_FAIL
        mode, rows = search_listings(q, days)
        if not rows:
            empty_map = {
                SearchMode.DEMAND: QUERY_EMPTY_DEMAND,
                SearchMode.STOCK: QUERY_EMPTY_STOCK,
                SearchMode.RENT_STOCK: QUERY_EMPTY_RENT_STOCK,
                SearchMode.RENT_DEMAND: QUERY_EMPTY_RENT_DEMAND,
            }
            return empty_map.get(mode, QUERY_EMPTY)
        prefix_map = {
            SearchMode.DEMAND: QUERY_OK_DEMAND,
            SearchMode.STOCK: QUERY_OK_STOCK,
            SearchMode.RENT_STOCK: QUERY_OK_RENT_STOCK,
            SearchMode.RENT_DEMAND: QUERY_OK_RENT_DEMAND,
        }
        prefix = prefix_map.get(mode, QUERY_OK_PREFIX)
        return prefix + format_estate_list(rows, settings.QUERY_MAX_RESULTS)

    if intent == Intent.MULTI_SAVE:
        items = parse_multi_estate(remainder or body, "")
        if not items:
            return REJECT_MSG
        chunks = []
        for item in items:
            listing = _model_from_parsed(
                item, remainder or body, from_mobile, WhatsappEstateMessage.KIND_ADD, twilio_sid
            )
            lead, dup = create_lead_from_listing(listing, item, from_mobile)
            chunks.append(save_reply_with_lead(lead, dup))
        if len(items) == 1:
            return chunks[0]
        return ADD_OK_PREFIX.format(count=len(items)) + "\n---\n".join(chunks[:3])

    if intent == Intent.REMIND:
        due, note = parse_followup_note(remainder or body)
        if not due:
            return "Kab yaad dilana hai? Jaise:\n*yaad kal sham broker ko phone*"
        lead = resolve_lead_for_reminder(from_mobile)
        if not lead:
            return "Pehle koi property ka message bhejo, phir yaad set karenge."
        schedule_lead_action(lead, due, note, from_mobile)
        return (
            f"✅ Theek hai ji.\n"
            f"Diary no. {lead.id} — {due:%d/%m %H:%M} ko yaad dilaaunga.\n"
            f"({note})\n"
            f"Subah-shaam wale message mein dikhega."
        )

    if intent == Intent.SAVE:
        text = remainder or body
        estate = parse_estate_message(text, "")
        if not estate:
            return REJECT_MSG
        # Search-style sentence SAVE par mat aaye
        from inbox.message_classify import is_explicit_search

        if is_explicit_search(body):
            mode, rows = search_listings(body.strip(), parse_query_days(body))
            if rows:
                prefix = QUERY_OK_STOCK
                return prefix + format_estate_list(rows, settings.QUERY_MAX_RESULTS)
            return QUERY_EMPTY_STOCK
        listing = _model_from_parsed(estate, body, from_mobile, WhatsappEstateMessage.KIND_SAVE, twilio_sid)
        lead, dup = create_lead_from_listing(listing, estate, from_mobile)
        return save_reply_with_lead(lead, dup)

    return REJECT_MSG


def process_and_reply(from_mobile: str, body: str, twilio_sid: str = "") -> None:
    reply = handle_inbound(from_mobile, body, twilio_sid)
    send_whatsapp(from_mobile, reply)