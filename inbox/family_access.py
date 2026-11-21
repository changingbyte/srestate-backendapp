"""Kaun allowed hai, operator ko auto-assign, super admin."""

from __future__ import annotations

from django.conf import settings

from inbox.models import FamilyMember, LeadRecord

ROLE_SUPER_ADMIN = "super_admin"
ROLE_OPERATOR = "operator"
ROLE_TESTER = "tester"

DEFAULT_ROSTER = (
    ("9328059281", "JP Halwai", ROLE_OPERATOR),
    ("9327676327", "Jitendra Bajaj", ROLE_OPERATOR),
    ("7984702696", "Prince", ROLE_SUPER_ADMIN),
    ("6354511915", "Shubham Bajaj", ROLE_TESTER),
    ("7069936766", "Jash", ROLE_TESTER),
)

SUPER_ADMIN_MOBILE = "7984702696"


def ensure_roster() -> None:
    """Create missing members. Do not turn someone back on if Prince hatado them."""
    for mobile, name, role in DEFAULT_ROSTER:
        obj, created = FamilyMember.objects.get_or_create(
            mobile=mobile,
            defaults={"name": name, "role": role, "is_active": True},
        )
        if not created:
            obj.name = name
            obj.role = role
            obj.save(update_fields=["name", "role"])


def is_family_allowed(mobile: str) -> bool:
    m = FamilyMember.objects.filter(mobile=mobile).first()
    if m is not None:
        return m.is_active
    return mobile in settings.FAMILY_ALLOWED_MOBILES


def is_super_admin(mobile: str) -> bool:
    m = FamilyMember.objects.filter(mobile=mobile).first()
    if m and m.role == ROLE_SUPER_ADMIN and m.is_active:
        return True
    return mobile == SUPER_ADMIN_MOBILE


def operator_mobiles() -> list[str]:
    active = set(
        FamilyMember.objects.filter(role=ROLE_OPERATOR, is_active=True).values_list(
            "mobile", flat=True
        )
    )
    ordered = [m for m, _, role in DEFAULT_ROSTER if role == ROLE_OPERATOR and m in active]
    extras = sorted(active - set(ordered))
    ops = ordered + extras
    return ops or ["9328059281", "9327676327"]


def pick_operator_assignee(exclude: str | None = None) -> str:
    ops = operator_mobiles()
    if not ops:
        return exclude or SUPER_ADMIN_MOBILE
    if len(ops) == 1:
        return ops[0]
    last = LeadRecord.objects.order_by("-id").values_list("assignee_mobile", flat=True).first()
    if last in ops:
        idx = ops.index(last)
        return ops[(idx + 1) % len(ops)]
    return ops[0] if exclude not in ops else ops[1 % len(ops)]


def member_label(mobile: str) -> str:
    m = FamilyMember.objects.filter(mobile=mobile).first()
    if m and m.name.strip():
        return m.name.strip()
    return f"…{mobile[-4:]}"


def format_team_roster() -> str:
    lines = ["*Shreeshyam — team*", ""]
    for m in FamilyMember.objects.order_by("role", "name"):
        status = "✅" if m.is_active else "❌ band"
        role_h = {"super_admin": "Admin", "operator": "Kaam", "tester": "Test"}.get(
            m.role, m.role
        )
        lines.append(f"{status} *{m.name}* — {m.mobile} ({role_h})")
    lines.append("")
    lines.append("_Naya save → JP / Jitendra par auto._")
    lines.append("_Admin (Prince): *hatado jash* | *jodo 99… Naam*_")
    return "\n".join(lines)