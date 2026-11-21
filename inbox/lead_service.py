from __future__ import annotations

import re
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from inbox.models import FamilyMember, LeadRecord, WhatsappEstateMessage
from inbox.twilio_client import send_whatsapp


def _member_label(mobile: str) -> str:
    m = FamilyMember.objects.filter(mobile=mobile).first()
    if m and m.name.strip():
        return m.name.strip()
    return mobile[-4:]


def build_summary(msg: WhatsappEstateMessage, parsed: dict) -> str:
    bits = []
    if msg.number_of_bedrooms:
        bits.append(f"{msg.number_of_bedrooms}bhk")
    if msg.estate_type:
        bits.append(msg.estate_type)
    if msg.area:
        bits.append(msg.area)
    if msg.estate_status:
        bits.append(msg.estate_status)
    if msg.budget:
        bits.append(f"₹{msg.budget}")
    return " ".join(bits) if bits else (msg.raw_body[:80] + "…")


def create_lead_from_listing(
    listing: WhatsappEstateMessage,
    parsed: dict,
    shared_by: str,
) -> LeadRecord:
    contact = (parsed.get("broker_mobile") or listing.broker_mobile or "").replace(" ", "")[:10]
    return LeadRecord.objects.create(
        listing=listing,
        shared_by_mobile=shared_by,
        assignee_mobile=shared_by,
        contact_mobile=contact,
        summary=build_summary(listing, parsed),
    )


def save_reply_with_lead(lead: LeadRecord) -> str:
    who = _member_label(lead.shared_by_mobile)
    lines = [
        "Theek hai — listing yaad kar li 👍",
        f"*{lead.summary}*",
    ]
    if lead.contact_mobile:
        lines.append(f"Contact: {lead.contact_mobile}")
    lines.append(f"Lead #{lead.id} | Bheja: {who}")
    lines.append("")
    lines.append("Kisi family member ko dena ho: `assign 9328059281`")
    lines.append("Apni list: `meri leads`")
    return "\n".join(lines)


def resolve_family_mobile(token: str) -> str | None:
    token = token.strip()
    if re.fullmatch(r"\d{10}", token):
        if token in settings.FAMILY_ALLOWED_MOBILES:
            return token
        return None
    member = FamilyMember.objects.filter(name__icontains=token).first()
    if member:
        return member.mobile
    return None


def assign_lead(actor_mobile: str, remainder: str) -> str:
    parts = remainder.split()
    lead_id = None
    target = None
    if len(parts) >= 2 and parts[0].isdigit():
        lead_id = int(parts[0])
        target = resolve_family_mobile(parts[1])
    elif parts:
        target = resolve_family_mobile(parts[0])
        lead = (
            LeadRecord.objects.filter(shared_by_mobile=actor_mobile, status=LeadRecord.STATUS_OPEN)
            .order_by("-created_at")
            .first()
        )
        if lead:
            lead_id = lead.id
    if not target:
        return "Family number ya naam samajh nahi aaya. Example: `assign 9328059281` ya `assign 5 rahul`"
    if lead_id:
        try:
            lead = LeadRecord.objects.get(id=lead_id)
        except LeadRecord.DoesNotExist:
            return f"Lead #{lead_id} nahi mili."
    else:
        lead = LeadRecord.objects.filter(status=LeadRecord.STATUS_OPEN).order_by("-created_at").first()
        if not lead:
            return "Koi open lead nahi hai."

    if lead.shared_by_mobile != actor_mobile and lead.assignee_mobile != actor_mobile:
        pass

    lead.assignee_mobile = target
    lead.save(update_fields=["assignee_mobile"])
    to_name = _member_label(target)
    from_name = _member_label(lead.shared_by_mobile)
    send_whatsapp(
        target,
        (
            f"*{from_name}* ne aapko lead #{lead.id} di:\n"
            f"{lead.summary}\n"
            f"Contact: {lead.contact_mobile or 'message mein dekho'}\n\n"
            f"Ho jaye to: `ho gaya {lead.id}`"
        ),
    )
    return f"✅ Lead #{lead.id} ab *{to_name}* ke paas. Unhe message bhej diya."


def complete_lead(actor_mobile: str, lead_id: int) -> str:
    try:
        lead = LeadRecord.objects.get(id=lead_id)
    except LeadRecord.DoesNotExist:
        return "Yeh lead nahi mili."
    if lead.assignee_mobile != actor_mobile and lead.shared_by_mobile != actor_mobile:
        return "Ye lead aapki list mein nahi hai."
    lead.status = LeadRecord.STATUS_DONE
    lead.completed_at = timezone.now()
    lead.save(update_fields=["status", "completed_at"])
    if lead.shared_by_mobile != actor_mobile:
        send_whatsapp(
            lead.shared_by_mobile,
            f"✅ {_member_label(actor_mobile)} ne lead #{lead.id} complete kar di: {lead.summary}",
        )
    return f"Shabash — lead #{lead.id} band kar di. Record save hai."


def format_my_leads(mobile: str) -> str:
    mine = LeadRecord.objects.filter(
        assignee_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).order_by("-created_at")[:10]
    shared = LeadRecord.objects.filter(
        shared_by_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).exclude(assignee_mobile=mobile).order_by("-created_at")[:5]

    lines = ["*Aapka dashboard* (poora record database mein hai)\n"]

    lines.append("*📌 Aapko karna hai:*")
    if mine:
        for L in mine:
            from_who = _member_label(L.shared_by_mobile)
            src = "aapki" if L.shared_by_mobile == mobile else f"{from_who} ne bheji"
            lines.append(
                f"#{L.id} {L.summary} | {src} | call {L.contact_mobile or '—'}"
            )
    else:
        lines.append("_Abhi kuch pending nahi — araam se._")

    if shared:
        lines.append("\n*📤 Aapne jisko diya (open):*")
        for L in shared:
            lines.append(f"#{L.id} → {_member_label(L.assignee_mobile)} | {L.summary}")

    lines.append("\n`ho gaya 5` — complete | `assign 93xx` — kisi ko do")
    return "\n".join(lines)


def send_care_message(mobile: str, slot: str) -> bool:
    """One friendly message per person, twice a day (morning / evening)."""
    now = timezone.localtime()
    open_mine = LeadRecord.objects.filter(
        assignee_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).order_by("next_action_at", "-created_at")[:5]

    if slot == "morning":
        title = f"☀️ Subah {now:%d %b} — short update"
        closing = "Din mein ek baar shaam ko phir yaad dilaaunga. Bas `meri leads` ya seedha kaam karte raho."
    else:
        title = f"🌆 Shaam {now:%d %b} — gentle check-in"
        closing = "Kal subah phir milte hain. `ho gaya` likh dena jahan ho chuka."

    lines = [title, ""]

    if open_mine:
        lines.append("*Aaj worth your time:*")
        for L in open_mine:
            who = _member_label(L.shared_by_mobile)
            extra = f" | {L.action_note}" if L.action_note else ""
            lines.append(f"• #{L.id} {L.summary}")
            lines.append(f"  Bheja: {who} | Call: {L.contact_mobile or '—'}{extra}")
    else:
        lines.append("Koi open lead nahi — nayi listing paste kar sakte ho, main save kar lunga.")

    new_today = WhatsappEstateMessage.objects.filter(
        created_at__date=now.date(),
        sender_mobile=mobile,
    ).count()
    if new_today:
        lines.append(f"\nAaj aapne *{new_today}* listing save ki.")

    lines.append("")
    lines.append(closing)

    ok, _ = send_whatsapp(mobile, "\n".join(lines))
    if ok and open_mine:
        LeadRecord.objects.filter(
            id__in=[L.id for L in open_mine],
        ).update(last_nudge=slot)
    return ok


def send_twice_daily_care(slot: str) -> int:
    count = 0
    for mobile in settings.FAMILY_ALLOWED_MOBILES:
        if send_care_message(mobile, slot):
            count += 1
    return count


def schedule_lead_action(lead: LeadRecord, due_at, note: str) -> None:
    lead.next_action_at = due_at
    lead.action_note = note[:255]
    lead.save(update_fields=["next_action_at", "action_note"])