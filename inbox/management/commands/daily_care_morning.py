from django.core.management.base import BaseCommand

from inbox.lead_service import send_twice_daily_care


class Command(BaseCommand):
    help = "9 AM IST — one friendly morning message per family member"

    def handle(self, *args, **options):
        n = send_twice_daily_care("morning")
        self.stdout.write(self.style.SUCCESS(f"Morning care sent: {n}"))