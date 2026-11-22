from django.conf import settings
from twilio.rest import Client


def normalize_whatsapp_from(twilio_from: str) -> str:
    """whatsapp:+919876543210 -> 9876543210"""
    digits = "".join(c for c in twilio_from if c.isdigit())
    if len(digits) >= 10:
        return digits[-10:]
    return digits


def send_whatsapp(mobile: str, body: str, *, purpose: str = "general") -> tuple[bool, str]:
    """purpose: operator | assign | complete | care | general"""
    if purpose == "care" and not getattr(settings, "WHATSAPP_REST_DAILY_CARE", False):
        return False, "daily_care disabled (save Twilio quota)"
    if purpose in ("operator", "assign", "complete") and not getattr(
        settings, "WHATSAPP_REST_OPERATOR_NOTIFY", False
    ):
        return False, "operator notify disabled (save Twilio quota)"
    # Tests must never hit Twilio (real family numbers).
    if getattr(settings, "TESTING", False):
        return True, "test-skipped"
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return False, "Twilio not configured"
    if len(body) > 1500:
        body = body[:1497] + "..."
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:+91{mobile}",
            body=body,
        )
        return True, msg.sid
    except Exception as exc:
        return False, str(exc)