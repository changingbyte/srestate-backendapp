from django.conf import settings
from django.core.management.base import BaseCommand

from inbox.models import FamilyMember


class Command(BaseCommand):
    help = "Create FamilyMember rows from FAMILY_ALLOWED_MOBILES"

    def handle(self, *args, **options):
        for mobile in settings.FAMILY_ALLOWED_MOBILES:
            obj, created = FamilyMember.objects.get_or_create(
                mobile=mobile,
                defaults={"name": f"Member {mobile[-4:]}"},
            )
            flag = "created" if created else "exists"
            self.stdout.write(f"{mobile}: {flag}")
        self.stdout.write(
            "Tip: Admin mein naam set karo — `assign rahul` kaam karega."
        )