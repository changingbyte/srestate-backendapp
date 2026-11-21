from __future__ import annotations

import re

from inbox.family_access import (
    ROLE_OPERATOR,
    ROLE_TESTER,
    format_team_roster,
    is_super_admin,
    member_label,
)
from inbox.models import FamilyMember


def handle_team(_mobile: str) -> str:
    return format_team_roster()


def handle_remove_member(actor: str, token: str) -> str:
    if not is_super_admin(actor):
        return "Sirf Prince (super admin) team change kar sakta hai."
    token = token.strip()
    if re.fullmatch(r"\d{10}", token):
        m = FamilyMember.objects.filter(mobile=token).first()
    else:
        m = FamilyMember.objects.filter(name__icontains=token).first()
    if not m:
        return "Yeh naam/number team mein nahi mila."
    if m.role == "super_admin":
        return "Super admin ko band nahi kar sakte."
    m.is_active = False
    m.save(update_fields=["is_active"])
    return f"✅ *{m.name}* ({m.mobile}) ab bot use nahi kar payega."


def handle_add_member(actor: str, remainder: str) -> str:
    if not is_super_admin(actor):
        return "Sirf Prince (super admin) naya member jod sakta hai."
    parts = remainder.split(maxsplit=1)
    if len(parts) < 2 or not re.fullmatch(r"\d{10}", parts[0]):
        return "Jaise: *jodo 9876543210 Rahul*"
    mobile, name = parts[0], parts[1].strip()[:64]
    obj, created = FamilyMember.objects.update_or_create(
        mobile=mobile,
        defaults={"name": name, "role": ROLE_TESTER, "is_active": True},
    )
    verb = "joda" if created else "update kiya"
    return f"✅ *{obj.name}* ({mobile}) {verb}. Ab WhatsApp se message kar sakta hai."