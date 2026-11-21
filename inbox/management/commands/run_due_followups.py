from django.core.management.base import BaseCommand

from inbox.followup_service import send_due_followup_reminders


class Command(BaseCommand):
    help = "Send WhatsApp when follow-up due time is reached (run every 15 min on PythonAnywhere)"

    def handle(self, *args, **options):
        count = send_due_followup_reminders()
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {count}"))