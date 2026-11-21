from django.db import models


class FamilyMember(models.Model):
    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_OPERATOR = "operator"
    ROLE_TESTER = "tester"
    ROLE_CHOICES = (
        (ROLE_SUPER_ADMIN, "Super admin"),
        (ROLE_OPERATOR, "Operator"),
        (ROLE_TESTER, "Tester"),
    )

    name = models.CharField(max_length=64)
    mobile = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=16, default=ROLE_TESTER, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.mobile})"


class WhatsappEstateMessage(models.Model):
    KIND_SAVE = "save"
    KIND_ADD = "add"
    KIND_QUERY = "query"

    raw_body = models.TextField()
    sender_mobile = models.CharField(max_length=10, db_index=True)
    twilio_sid = models.CharField(max_length=64, blank=True, default="")
    message_kind = models.CharField(max_length=16, default=KIND_SAVE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    estate_status = models.CharField(max_length=32, blank=True, default="", db_index=True)
    estate_type = models.CharField(max_length=32, blank=True, default="", db_index=True)
    area = models.CharField(max_length=128, blank=True, default="", db_index=True)
    budget = models.BigIntegerField(null=True, blank=True, db_index=True)
    number_of_bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    apartment = models.CharField(max_length=128, blank=True, default="")
    broker_mobile = models.CharField(max_length=10, blank=True, default="")
    extracted_json = models.JSONField(default=dict)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.sender_mobile} @ {self.created_at:%Y-%m-%d}"


class LeadRecord(models.Model):
    """Who shared the lead, who should act, whom to contact."""

    STATUS_OPEN = "open"
    STATUS_DONE = "done"

    listing = models.ForeignKey(
        WhatsappEstateMessage,
        on_delete=models.CASCADE,
        related_name="leads",
    )
    shared_by_mobile = models.CharField(max_length=10, db_index=True)
    assignee_mobile = models.CharField(max_length=10, db_index=True)
    contact_mobile = models.CharField(max_length=10, blank=True, default="", db_index=True)
    summary = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=16, default=STATUS_OPEN, db_index=True)
    next_action_at = models.DateTimeField(null=True, blank=True, db_index=True)
    action_note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_nudge = models.CharField(max_length=16, blank=True, default="")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"#{self.id} {self.summary} → {self.assignee_mobile}"


class ConversationState(models.Model):
    mobile = models.CharField(max_length=10, primary_key=True)
    last_lead_id = models.PositiveIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeadEvent(models.Model):
    EVENT_CREATED = "created"
    EVENT_ASSIGNED = "assigned"
    EVENT_REMINDER = "reminder"
    EVENT_DONE = "done"
    EVENT_DUPLICATE_WARN = "duplicate_warn"

    lead = models.ForeignKey(LeadRecord, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=32, db_index=True)
    actor_mobile = models.CharField(max_length=10, blank=True, default="")
    detail = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class FollowUpTask(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"

    owner_mobile = models.CharField(max_length=10, db_index=True)
    note = models.TextField()
    due_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=16, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reminded_at = models.DateTimeField(null=True, blank=True)
    listing = models.ForeignKey(
        WhatsappEstateMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="followups",
    )
    lead = models.ForeignKey(
        LeadRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="followups",
    )

    class Meta:
        ordering = ("due_at",)

    def __str__(self):
        return f"{self.owner_mobile} @ {self.due_at:%Y-%m-%d %H:%M} — {self.note[:40]}"