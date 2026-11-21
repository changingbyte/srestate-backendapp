from django.conf import settings
from twilio.rest import Client


def send_whatsapp(to_mobile: str, body: str) -> dict:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return {"success": False, "msg": "Twilio not configured"}
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            body=body[:1600],
            to=f"whatsapp:+91{to_mobile}",
        )
        return {"success": True, "sid": message.sid}
    except Exception as exc:
        return {"success": False, "msg": str(exc)}


def normalize_whatsapp_from(raw_from: str) -> str:
    """Twilio From like whatsapp:+919876543210 -> 9876543210."""
    digits = "".join(c for c in raw_from if c.isdigit())
    if len(digits) >= 10:
        return digits[-10:]
    return digits