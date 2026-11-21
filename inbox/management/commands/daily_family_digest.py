from django.core.management.base import BaseCommand

from inbox.followup_service import send_daily_digest


class Command(BaseCommand):
    help = "Morning WhatsApp digest for each family member (run once daily)"

    def handle(self, *args, **options):
        count = send_daily_digest()
        self.stdout.write(self.style.SUCCESS(f"Digests sent: {count}"))