from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from inbox.models import FollowUpTask, WhatsappEstateMessage
from inbox.twilio_client import send_whatsapp


def format_pending_list(tasks) -> str:
    if not tasks:
        return "Koi pending follow-up nahi hai. Set karne ke liye:\n`followup kal 5pm adajan broker call`"
    lines = ["*Aapke follow-up:*"]
    for t in tasks:
        lines.append(f"*{t.id}.* {t.due_at:%d/%m %H:%M} — {t.note}")
    lines.append("\nComplete: `done 3` (id number)")
    return "\n".join(lines)


def send_due_followup_reminders() -> int:
    now = timezone.now()
    due = FollowUpTask.objects.filter(
        status=FollowUpTask.STATUS_PENDING,
        due_at__lte=now,
    ).order_by("due_at")[:50]

    count = 0
    for task in due:
        body = (
            f"⏰ *Follow-up time!*\n\n"
            f"{task.note}\n\n"
            f"Due: {task.due_at:%d/%m/%Y %H:%M}\n"
            f"Done? Reply: `done {task.id}`"
        )
        ok, _ = send_whatsapp(task.owner_mobile, body, purpose="care")
        if ok:
            task.status = FollowUpTask.STATUS_SENT
            task.reminded_at = now
            task.save(update_fields=["status", "reminded_at"])
            count += 1
    return count


def send_daily_digest() -> int:
    if not getattr(settings, "WHATSAPP_REST_DAILY_CARE", False):
        return 0
    now = timezone.localtime()
    start_yesterday = now - timedelta(days=1)
    sent = 0

    for mobile in settings.FAMILY_ALLOWED_MOBILES:
        saved = WhatsappEstateMessage.objects.filter(
            sender_mobile=mobile,
            created_at__gte=start_yesterday,
        ).count()
        today_pending = FollowUpTask.objects.filter(
            owner_mobile=mobile,
            status=FollowUpTask.STATUS_PENDING,
            due_at__date=now.date(),
        ).order_by("due_at")[:5]
        overdue = FollowUpTask.objects.filter(
            owner_mobile=mobile,
            status=FollowUpTask.STATUS_PENDING,
            due_at__lt=now,
        ).count()

        lines = [f"*Roz ki report* ({now:%d/%m/%Y})", f"Kal save: *{saved}* listing(s)"]
        if overdue:
            lines.append(f"⚠️ Overdue follow-up: *{overdue}*")
        if today_pending:
            lines.append("*Aaj ke follow-up:*")
            for t in today_pending:
                lines.append(f"• {t.due_at:%H:%M} — {t.note}")
        else:
            lines.append("Aaj koi follow-up schedule nahi (ya sab ho chuka).")
        lines.append("\n`pending` — poori list | `followup kal …` — naya")

        ok, _ = send_whatsapp(mobile, "\n".join(lines), purpose="care")
        if ok:
            sent += 1
    return sent