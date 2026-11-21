from django.core.management.base import BaseCommand

from inbox.lead_service import send_twice_daily_care


class Command(BaseCommand):
    help = "6 PM IST — one gentle evening check-in per family member"

    def handle(self, *args, **options):
        n = send_twice_daily_care("evening")
        self.stdout.write(self.style.SUCCESS(f"Evening care sent: {n}"))