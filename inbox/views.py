import logging
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from inbox.handlers import handle_inbound
from inbox.twilio_client import normalize_whatsapp_from, send_whatsapp

try:
    from twilio.request_validator import RequestValidator
except ImportError:
    RequestValidator = None

logger = logging.getLogger(__name__)


def _signature_urls(request) -> list[str]:
    if getattr(settings, "TWILIO_WEBHOOK_URL", ""):
        return [settings.TWILIO_WEBHOOK_URL.strip()]
    seen = request.build_absolute_uri()
    https = re.sub(r"^http://", "https://", seen, flags=re.I)
    return list(dict.fromkeys([seen, https]))


def _validate_twilio(request) -> bool:
    if not settings.TWILIO_VALIDATE_SIGNATURE:
        return True
    if not RequestValidator or not settings.TWILIO_AUTH_TOKEN:
        logger.error("Twilio signature on but AUTH_TOKEN/validator missing")
        return False
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
    urls = _signature_urls(request)
    for url in urls:
        if validator.validate(url, request.POST, signature):
            return True
    logger.warning("Twilio signature failed for urls=%s", urls)
    return False


def _twiml_message(body: str) -> HttpResponse:
    text = (body or "Server error.").strip()
    if len(text) > 1500:
        text = text[:1497] + "..."
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(text)}</Message></Response>"
    )
    return HttpResponse(xml, content_type="text/xml; charset=utf-8")


@csrf_exempt
@require_POST
def whatsapp_inbound(request):
    if not _validate_twilio(request):
        return HttpResponseForbidden("Invalid Twilio signature")

    from_mobile = normalize_whatsapp_from(request.POST.get("From", ""))
    body = request.POST.get("Body", "")
    sid = request.POST.get("MessageSid", "")

    try:
        reply = handle_inbound(from_mobile, body, sid)
    except Exception:
        logger.exception("handle_inbound failed sid=%s mobile=%s", sid, from_mobile)
        reply = "Maaf kijiye, abhi error aaya. Thodi der baad dubara bhejiye ya Prince ko bolo."

    ok, detail = send_whatsapp(from_mobile, reply)
    if ok:
        return HttpResponse("<Response></Response>", content_type="text/xml")
    logger.error("REST WhatsApp send failed mobile=%s detail=%s", from_mobile, detail)
    return _twiml_message(reply)