"""Local real-life smoke — sab scenarios print."""

from django.core.management.base import BaseCommand

from inbox.family_access import ensure_roster
from inbox.handlers import handle_inbound
from inbox.models import LeadRecord, WhatsappEstateMessage

SCENARIOS = [
    ("Prince", "7984702696", "Add 3bhk vesu sell fully furnished 90 lakh"),
    ("Shubham", "6354511915", "Query 3bhk vesu buy furnished"),
    ("Jash", "7069936766", "I have buyer for 3bhk vesu"),
    ("JP", "9328059281", "meri list"),
    ("Jitendra", "9327676327", "meri list"),
    ("Prince", "7984702696", "team"),
]


class Command(BaseCommand):
    help = "Print handler replies for real family numbers (no Twilio send in handle_inbound)"

    def handle(self, *args, **options):
        ensure_roster()
        WhatsappEstateMessage.objects.all().delete()
        LeadRecord.objects.all().delete()
        for label, mobile, msg in SCENARIOS:
            out = handle_inbound(mobile, msg)
            self.stdout.write(self.style.HTTP_INFO(f"\n=== {label} ({mobile}): {msg}"))
            self.stdout.write(out[:500])
            if len(out) > 500:
                self.stdout.write("…")
        self.stdout.write(self.style.SUCCESS(f"\nLeads: {LeadRecord.objects.count()}"))