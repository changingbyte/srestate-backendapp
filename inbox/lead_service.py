from __future__ import annotations

import re

from django.conf import settings
from django.utils import timezone

from datetime import timedelta

from inbox.conversation import get_last_lead_id, touch_last_lead
from inbox.family_access import member_label, pick_operator_assignee
from inbox.lead_events import log_event
from inbox.models import FamilyMember, LeadRecord, WhatsappEstateMessage
from inbox.twilio_client import send_whatsapp


def _member_label(mobile: str) -> str:
    return member_label(mobile)


def build_summary(msg: WhatsappEstateMessage, parsed: dict) -> str:
    bits = []
    if msg.number_of_bedrooms:
        bits.append(f"{msg.number_of_bedrooms} BHK")
    if msg.area:
        bits.append(msg.area.title())
    if msg.estate_type:
        bits.append(msg.estate_type)
    if msg.estate_status:
        if msg.estate_status in ("rent",):
            bits.append("kiraye par")
        elif msg.estate_status in ("sell", "buy", "purchase"):
            bits.append("kharid-beka")
        else:
            bits.append(msg.estate_status)
    if msg.budget:
        bits.append(f"Rs {msg.budget}")
    return " ".join(bits) if bits else msg.raw_body[:70] + "…"


def find_recent_duplicate(parsed: dict, contact: str) -> LeadRecord | None:
    if not contact and not parsed.get("area"):
        return None
    since = timezone.now() - timedelta(hours=48)
    qs = LeadRecord.objects.filter(status=LeadRecord.STATUS_OPEN, created_at__gte=since)
    if contact:
        qs = qs.filter(contact_mobile=contact)
    area = (parsed.get("area") or "").strip()
    if area:
        qs = qs.filter(summary__icontains=area[:40])
    return qs.order_by("-created_at").first()


def create_lead_from_listing(
    listing: WhatsappEstateMessage,
    parsed: dict,
    shared_by: str,
) -> tuple[LeadRecord, LeadRecord | None]:
    contact = (parsed.get("broker_mobile") or listing.broker_mobile or "").replace(" ", "")[:10]
    dup = find_recent_duplicate(parsed, contact)
    assignee = pick_operator_assignee(exclude=None)
    lead = LeadRecord.objects.create(
        listing=listing,
        shared_by_mobile=shared_by,
        assignee_mobile=assignee,
        contact_mobile=contact,
        summary=build_summary(listing, parsed),
    )
    log_event(lead, "created", shared_by, lead.summary)
    log_event(lead, "assigned", "system", f"auto → {member_label(assignee)}")
    touch_last_lead(shared_by, lead.id)
    touch_last_lead(assignee, lead.id)
    if assignee != shared_by:
        send_whatsapp(
            assignee,
            (
                f"*Naya kaam — {member_label(shared_by)} ne bheja*\n\n"
                f"{lead.summary}\n"
                f"📞 {contact or 'message dekho'}\n"
                f"Diary no. {lead.id}\n\n"
                f"Ho jaye to: *ho gaya {lead.id}*"
            ),
        )
    if dup and dup.id != lead.id:
        log_event(lead, "duplicate_warn", shared_by, f"similar to #{dup.id}")
    return lead, dup


def _assign_hint_lines() -> list[str]:
    names = [
        m.name.strip()
        for m in FamilyMember.objects.exclude(name="").order_by("name")
        if m.name.strip()
    ]
    if not names:
        return ["*de do naam ya 10-digit number*"]
    hints = [f"• *de do {n.lower()}*" for n in names[:5]]
    hints.append("• ya *de do 10-digit mobile*")
    return hints


def save_reply_with_lead(lead: LeadRecord, duplicate: LeadRecord | None = None) -> str:
    who = member_label(lead.assignee_mobile)
    lines = [
        "✅ *Save ho gaya.*",
        "",
        f"*{lead.summary}*",
        f"👤 Kaam → *{who}* (auto)",
    ]
    if lead.contact_mobile:
        lines.append(f"📞 Phone: {lead.contact_mobile}")
    lines.append(f"📝 Diary no. *{lead.id}*")
    if duplicate:
        lines.append("")
        lines.append(
            f"⚠️ *Dhyan:* pehle bhi similar (#{duplicate.id}) — double save ho sakta hai. "
            f"Same ho to *ho gaya {lead.id}* likh kar hata dena."
        )
    if lead.assignee_mobile != lead.shared_by_mobile:
        lines.append("_Aur kisi ko dena ho: *de do naam*_")
    lines.append("*meri list* — aaj kya bacha")
    return "\n".join(lines)


def resolve_family_mobile(token: str) -> str | None:
    token = token.strip().lower()
    if re.fullmatch(r"\d{10}", token):
        from inbox.family_access import is_family_allowed

        if is_family_allowed(token):
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
        target = resolve_family_mobile(" ".join(parts[1:]))
    elif len(parts) == 1:
        if parts[0].isdigit():
            return "Kisko dena hai? Jaise: *de do rahul* ya *de do 9328059281*"
        target = resolve_family_mobile(parts[0])
    elif parts:
        target = resolve_family_mobile(" ".join(parts))
    if not target:
        return (
            "Kisko dena hai — naam ya 10 digit mobile likho.\n"
            "Jaise: *de do rahul* ya *de do 9328059281*"
        )
    if lead_id:
        try:
            lead = LeadRecord.objects.get(id=lead_id)
        except LeadRecord.DoesNotExist:
            return f"Diary number {lead_id} nahi mila."
    else:
        last_id = get_last_lead_id(actor_mobile)
        if last_id:
            try:
                lead = LeadRecord.objects.get(id=last_id, status=LeadRecord.STATUS_OPEN)
            except LeadRecord.DoesNotExist:
                lead = None
        else:
            lead = None
        if not lead:
            lead = (
                LeadRecord.objects.filter(
                    shared_by_mobile=actor_mobile,
                    status=LeadRecord.STATUS_OPEN,
                )
                .order_by("-created_at")
                .first()
            )
        if not lead:
            lead = LeadRecord.objects.filter(status=LeadRecord.STATUS_OPEN).order_by("-created_at").first()
        if not lead:
            return "Abhi koi open enquiry nahi — pehle property ka message bhejo."

    lead.assignee_mobile = target
    lead.save(update_fields=["assignee_mobile"])
    log_event(lead, "assigned", actor_mobile, f"→ {_member_label(target)}")
    touch_last_lead(actor_mobile, lead.id)
    touch_last_lead(target, lead.id)
    to_name = _member_label(target)
    from_name = _member_label(lead.shared_by_mobile)
    send_whatsapp(
        target,
        (
            f"*Namaste {to_name} ji,*\n"
            f"{from_name} ne aapko ek property di hai:\n\n"
            f"{lead.summary}\n"
            f"📞 {lead.contact_mobile or 'number message mein hai'}\n"
            f"Diary no. {lead.id}\n\n"
            f"Ho jaye to likhna: *ho gaya {lead.id}*"
        ),
    )
    return f"✅ *{to_name}* ko bata diya. Property diary no. {lead.id}."


def complete_lead(actor_mobile: str, lead_id: int | None) -> str:
    if lead_id is None:
        last_id = get_last_lead_id(actor_mobile)
        lead = None
        if last_id:
            try:
                lead = LeadRecord.objects.get(
                    id=last_id,
                    status=LeadRecord.STATUS_OPEN,
                )
                if lead.assignee_mobile != actor_mobile and lead.shared_by_mobile != actor_mobile:
                    lead = None
            except LeadRecord.DoesNotExist:
                lead = None
        if not lead:
            lead = (
                LeadRecord.objects.filter(assignee_mobile=actor_mobile, status=LeadRecord.STATUS_OPEN)
                .order_by("-created_at")
                .first()
            )
        if not lead:
            return "Koi pending kaam nahi dikhta. Shukriya!"
    else:
        try:
            lead = LeadRecord.objects.get(id=lead_id)
        except LeadRecord.DoesNotExist:
            return "Yeh diary number galat hai. *meri list* se sahi number dekho."

    if lead.assignee_mobile != actor_mobile and lead.shared_by_mobile != actor_mobile:
        return "Yeh enquiry aapke naam par nahi hai."

    lead.status = LeadRecord.STATUS_DONE
    lead.completed_at = timezone.now()
    lead.save(update_fields=["status", "completed_at"])
    log_event(lead, "done", actor_mobile, "")
    touch_last_lead(actor_mobile, lead.id)
    if lead.shared_by_mobile != actor_mobile:
        send_whatsapp(
            lead.shared_by_mobile,
            f"✅ Khush khabri: {_member_label(actor_mobile)} ne property no. {lead.id} complete kar di.\n{lead.summary}",
        )
    return f"✅ Bahut achha! No. {lead.id} band — {lead.summary}\nDhanyavaad 🙏"


def format_my_leads(mobile: str) -> str:
    mine = LeadRecord.objects.filter(
        assignee_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).order_by("-created_at")[:10]
    shared = LeadRecord.objects.filter(
        shared_by_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).exclude(assignee_mobile=mobile).order_by("-created_at")[:5]

    lines = ["*Aapki property diary*\n"]

    lines.append("*🔹 Aap par hai (phone / visit karna hai):*")
    if mine:
        for L in mine:
            if L.shared_by_mobile == mobile:
                src = "aapne bheji"
            else:
                src = f"{_member_label(L.shared_by_mobile)} ne di"
            phone = L.contact_mobile or "message dekho"
            lines.append(f"• No. {L.id} — {L.summary}")
            lines.append(f"  ({src}) | 📞 {phone}")
    else:
        lines.append("_Abhi koi kaam pending nahi. Araam karo 😊_")

    if shared:
        lines.append("\n*🔹 Aapne jisko diya (abhi open):*")
        for L in shared:
            lines.append(f"• No. {L.id} → {_member_label(L.assignee_mobile)} — {L.summary}")

    lines.append("\n*Ho gaya?* likho *ho gaya* ya *ho gaya 5*")
    lines.append("*Kisi ko dena?* *de do naam ya number*")
    return "\n".join(lines)


def send_care_message(mobile: str, slot: str) -> bool:
    from inbox.family_digest import build_group_care_message

    body = build_group_care_message(slot, mobile)
    ok, _ = send_whatsapp(mobile, body)
    if ok:
        open_mine = LeadRecord.objects.filter(
            assignee_mobile=mobile,
            status=LeadRecord.STATUS_OPEN,
        )[:5]
        if open_mine:
            LeadRecord.objects.filter(id__in=[L.id for L in open_mine]).update(last_nudge=slot)
    return ok


def send_twice_daily_care(slot: str) -> int:
    count = 0
    for mobile in settings.FAMILY_ALLOWED_MOBILES:
        if send_care_message(mobile, slot):
            count += 1
    return count


def schedule_lead_action(lead: LeadRecord, due_at, note: str, actor_mobile: str = "") -> None:
    lead.next_action_at = due_at
    lead.action_note = note[:255]
    lead.save(update_fields=["next_action_at", "action_note"])
    log_event(lead, "reminder", actor_mobile, note[:200])


def resolve_lead_for_reminder(actor_mobile: str) -> LeadRecord | None:
    last_id = get_last_lead_id(actor_mobile)
    if last_id:
        try:
            return LeadRecord.objects.get(
                id=last_id,
                status=LeadRecord.STATUS_OPEN,
            )
        except LeadRecord.DoesNotExist:
            pass
    return (
        LeadRecord.objects.filter(assignee_mobile=actor_mobile, status=LeadRecord.STATUS_OPEN)
        .order_by("-created_at")
        .first()
    )