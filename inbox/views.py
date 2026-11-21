from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from inbox.handlers import process_and_reply
from inbox.twilio_client import normalize_whatsapp_from

try:
    from twilio.request_validator import RequestValidator
except ImportError:
    RequestValidator = None


def _validate_twilio(request) -> bool:
    if not settings.TWILIO_VALIDATE_SIGNATURE:
        return True
    if not RequestValidator or not settings.TWILIO_AUTH_TOKEN:
        return False
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
    url = request.build_absolute_uri()
    return validator.validate(url, request.POST, signature)


@csrf_exempt
@require_POST
def whatsapp_inbound(request):
    if not _validate_twilio(request):
        return HttpResponseForbidden("Invalid Twilio signature")

    from_mobile = normalize_whatsapp_from(request.POST.get("From", ""))
    body = request.POST.get("Body", "")
    sid = request.POST.get("MessageSid", "")

    process_and_reply(from_mobile, body, sid)
    return HttpResponse("<Response></Response>", content_type="text/xml")