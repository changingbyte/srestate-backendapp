from django.conf import settings
from django.core.management.base import BaseCommand

from inbox.family_access import ensure_roster, is_family_allowed
from inbox.models import FamilyMember


class Command(BaseCommand):
    help = "PA/Twilio quick checklist — kyun reply nahi aa raha"

    def handle(self, *args, **options):
        ensure_roster()
        self.stdout.write(f"TWILIO_ACCOUNT_SID set: {bool(settings.TWILIO_ACCOUNT_SID)}")
        self.stdout.write(f"TWILIO_AUTH_TOKEN set: {bool(settings.TWILIO_AUTH_TOKEN)}")
        self.stdout.write(f"TWILIO_WHATSAPP_FROM: {settings.TWILIO_WHATSAPP_FROM}")
        self.stdout.write(f"TWILIO_VALIDATE_SIGNATURE: {settings.TWILIO_VALIDATE_SIGNATURE}")
        self.stdout.write(f"TWILIO_WEBHOOK_URL: {getattr(settings, 'TWILIO_WEBHOOK_URL', '') or '(empty — set on PA if validate on)'}")
        self.stdout.write(f"WHATSAPP_REPLY_VIA_TWIML: {settings.WHATSAPP_REPLY_VIA_TWIML}")
        self.stdout.write(f"WHATSAPP_REST_OPERATOR_NOTIFY: {settings.WHATSAPP_REST_OPERATOR_NOTIFY}")
        self.stdout.write(f"WHATSAPP_REST_DAILY_CARE: {settings.WHATSAPP_REST_DAILY_CARE}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"FAMILY_ALLOWED_MOBILES: {settings.FAMILY_ALLOWED_MOBILES}")
        for m in FamilyMember.objects.order_by("mobile"):
            ok = is_family_allowed(m.mobile)
            self.stdout.write(f"  {m.name} {m.mobile} active={m.is_active} role={m.role} allowed={ok}")
        if settings.TWILIO_VALIDATE_SIGNATURE and not settings.TWILIO_WEBHOOK_URL:
            self.stdout.write(
                self.style.WARNING(
                    "Signature ON but TWILIO_WEBHOOK_URL empty — Twilio 403 possible on PythonAnywhere."
                )
            )