from django.utils import timezone

from inbox.models import ConversationState


def touch_last_lead(mobile: str, lead_id: int) -> None:
    ConversationState.objects.update_or_create(
        mobile=mobile,
        defaults={"last_lead_id": lead_id, "updated_at": timezone.now()},
    )


def get_last_lead_id(mobile: str) -> int | None:
    row = ConversationState.objects.filter(mobile=mobile).first()
    return row.last_lead_id if row else None