from inbox.models import LeadEvent, LeadRecord


def log_event(lead: LeadRecord, event_type: str, actor_mobile: str, detail: str = "") -> None:
    LeadEvent.objects.create(
        lead=lead,
        event_type=event_type,
        actor_mobile=actor_mobile,
        detail=detail[:500],
    )