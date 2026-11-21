from __future__ import annotations

import re

from django.conf import settings
from django.utils import timezone

from inbox.models import FamilyMember, LeadRecord, WhatsappEstateMessage
from inbox.twilio_client import send_whatsapp


def _member_label(mobile: str) -> str:
    m = FamilyMember.objects.filter(mobile=mobile).first()
    if m and m.name.strip():
        return m.name.strip()
    return f"number …{mobile[-4:]}"


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
    lines = [
        "✅ *Theek hai ji, maine yaad kar liya.*",
        "",
        f"*{lead.summary}*",
    ]
    if lead.contact_mobile:
        lines.append(f"📞 Phone: {lead.contact_mobile}")
    lines.append(f"📝 Diary number: *{lead.id}* (baad mein kaam aayega)")
    lines.append("")
    lines.append("Kisi aur ko dena ho to likho:")
    lines.append("*de do 9328059281* (ya member ka naam)")
    lines.append("Aaj ka kaam dekho: *meri list*")
    return "\n".join(lines)


def resolve_family_mobile(token: str) -> str | None:
    token = token.strip().lower()
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
    now = timezone.localtime()
    open_mine = LeadRecord.objects.filter(
        assignee_mobile=mobile,
        status=LeadRecord.STATUS_OPEN,
    ).order_by("next_action_at", "-created_at")[:5]

    if slot == "morning":
        title = f"☀️ *Subah ki namaste* — {now:%d %b}"
        closing = "Shaam ko ek chhota sa message aur aayega. Property paste karte raho."
    else:
        title = f"🌆 *Shaam ka haal* — {now:%d %b}"
        closing = "Ho chuka ho to *ho gaya* likh dena. Kal subah phir mileinge."

    lines = [title, ""]

    if open_mine:
        lines.append("*Aaj yeh yaad rakho:*")
        for L in open_mine:
            who = _member_label(L.shared_by_mobile)
            phone = L.contact_mobile or "—"
            lines.append(f"• {L.summary}")
            lines.append(f"  No. {L.id} | {who} ne bheji | 📞 {phone}")
            if L.action_note:
                lines.append(f"  Yaad: {L.action_note}")
    else:
        lines.append("Aaj koi pending property kaam nahi — naya message aaye to yahi bhej dena.")

    new_today = WhatsappEstateMessage.objects.filter(
        created_at__date=now.date(),
        sender_mobile=mobile,
    ).count()
    if new_today:
        lines.append(f"\nAaj aapne *{new_today}* property save karwai.")

    lines.append("")
    lines.append(closing)
    lines.append("*meri list* — poori diary")

    ok, _ = send_whatsapp(mobile, "\n".join(lines))
    if ok and open_mine:
        LeadRecord.objects.filter(id__in=[L.id for L in open_mine]).update(last_nudge=slot)
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