import logging
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from inbox.handlers import handle_inbound
from inbox.twilio_client import normalize_whatsapp_from

try:
    from twilio.request_validator import RequestValidator
except ImportError:
    RequestValidator = None


logger = logging.getLogger(__name__)


def _validate_twilio(request) -> bool:
    if not settings.TWILIO_VALIDATE_SIGNATURE:
        return True
    if not RequestValidator or not settings.TWILIO_AUTH_TOKEN:
        return False
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
    # A reverse proxy can make Django see http:// while Twilio signed the public
    # https:// URL. Prefer an explicitly configured public endpoint; otherwise
    # accept the request URL and its HTTPS equivalent.
    if settings.TWILIO_WEBHOOK_URL:
        urls = [settings.TWILIO_WEBHOOK_URL]
    else:
        seen_url = request.build_absolute_uri()
        https_url = re.sub(r"^http://", "https://", seen_url, flags=re.I)
        urls = [seen_url, https_url]
    return any(validator.validate(url, request.POST, signature) for url in dict.fromkeys(urls))


def _twiml_message(body: str) -> HttpResponse:
    """Reply in the webhook response so the sender does not depend on a second REST send."""
    text = (body or "Maaf kijiye, koi jawab nahi bana.").strip()
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
        # Return valid TwiML so a sender is not left without any reply.
        logger.exception("Unable to process WhatsApp message sid=%s", sid)
        reply = "Maaf kijiye, message abhi process nahi hua. Ek baar phir bhejiye."
    return _twiml_message(reply)
