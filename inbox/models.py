from django.db import models


class FamilyMember(models.Model):
    name = models.CharField(max_length=64)
    mobile = models.CharField(max_length=10, unique=True)
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