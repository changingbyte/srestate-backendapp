"""Subah/shaam — poori family ko ek jaisa group-style update."""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from inbox.lead_service import _member_label
from inbox.models import FamilyMember, LeadRecord, WhatsappEstateMessage


def format_family_roster() -> list[str]:
    lines = ["*Team - naam | mobile:*"]
    members = FamilyMember.objects.filter(
        mobile__in=settings.FAMILY_ALLOWED_MOBILES,
        is_active=True,
    ).order_by("name")
    if not members:
        for mobile in settings.FAMILY_ALLOWED_MOBILES:
            lines.append(f"• ...{mobile[-4:]} - {mobile}")
        return lines
    for m in members:
        name = m.name.strip() or f"Member {m.mobile[-4:]}"
        lines.append(f"• *{name}* - {m.mobile}")
    return lines


def format_family_pending_leads() -> list[str]:
    open_leads = LeadRecord.objects.filter(status=LeadRecord.STATUS_OPEN).order_by(
        "assignee_mobile", "-created_at"
    )[:12]
    if not open_leads:
        return ["_Abhi koi open property kaam nahi. Naya message aaye to bot par bhej dena._"]
    lines = ["*Poori family - pending:*"]
    for L in open_leads:
        assignee = _member_label(L.assignee_mobile)
        sharer = _member_label(L.shared_by_mobile)
        phone = L.contact_mobile or "-"
        lines.append(f"• No. {L.id} - {L.summary}")
        lines.append(f"  {sharer} → *{assignee}* | 📞 {phone}")
    return lines


def build_group_care_message(slot: str, recipient_mobile: str) -> str:
    now = timezone.localtime()
    brand = settings.FAMILY_BRAND_NAME

    if slot == "morning":
        headline = f"*Subah update* - {now:%d %b %Y}"
        closing = "Shaam ko phir poori family ka haal bhejenge."
    else:
        headline = f"*Shaam update* - {now:%d %b %Y}"
        closing = "Ho gaya ho to *ho gaya* likh dena. Kal subah phir."

    you = _member_label(recipient_mobile)
    mine = LeadRecord.objects.filter(
        assignee_mobile=recipient_mobile,
        status=LeadRecord.STATUS_OPEN,
    ).order_by("-created_at")[:3]

    lines = [
        f"*{brand}* 🏠",
        headline,
        "",
        *format_family_roster(),
        "",
        *format_family_pending_leads(),
        "",
        f"*Aap par ({you}):*",
    ]
    if mine:
        for L in mine:
            lines.append(f"• No. {L.id} - {L.summary}")
    else:
        lines.append("_Aap par koi pending nahi._")

    saved_today = WhatsappEstateMessage.objects.filter(created_at__date=now.date()).count()
    lines.append(f"\n*Aaj family ne save:* {saved_today} message")
    lines.append("")
    lines.append(closing)
    lines.append("*meri list* | *madad*")
    return "\n".join(lines)