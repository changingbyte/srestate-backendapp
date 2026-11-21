from django.core.management.base import BaseCommand

from inbox.family_access import DEFAULT_ROSTER, ensure_roster


class Command(BaseCommand):
    help = "JP / Jitendra operators + Prince admin + testers — fixed roster"

    def handle(self, *args, **options):
        ensure_roster()
        for mobile, name, role in DEFAULT_ROSTER:
            self.stdout.write(f"{mobile}: {name} ({role})")
        self.stdout.write(self.style.SUCCESS("Roster OK — migrate + reload on PA."))