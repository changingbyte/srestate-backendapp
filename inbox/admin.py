from django.contrib import admin

from inbox.models import (
    ConversationState,
    FamilyMember,
    FollowUpTask,
    LeadEvent,
    LeadRecord,
    WhatsappEstateMessage,
)


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "is_active")
    search_fields = ("name", "mobile")


@admin.register(WhatsappEstateMessage)
class WhatsappEstateMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender_mobile",
        "message_kind",
        "area",
        "estate_type",
        "budget",
        "number_of_bedrooms",
        "created_at",
    )
    list_filter = ("message_kind", "estate_type", "estate_status", "area")
    search_fields = ("raw_body", "sender_mobile", "area")


@admin.register(LeadRecord)
class LeadRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "summary",
        "shared_by_mobile",
        "assignee_mobile",
        "contact_mobile",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("summary", "shared_by_mobile", "assignee_mobile", "contact_mobile")


@admin.register(FollowUpTask)
class FollowUpTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "owner_mobile", "due_at", "status", "note", "created_at")
    list_filter = ("status", "due_at")
    search_fields = ("note", "owner_mobile")


@admin.register(LeadEvent)
class LeadEventAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "event_type", "actor_mobile", "detail", "created_at")
    list_filter = ("event_type",)
    search_fields = ("detail", "actor_mobile")


@admin.register(ConversationState)
class ConversationStateAdmin(admin.ModelAdmin):
    list_display = ("mobile", "last_lead_id", "updated_at")