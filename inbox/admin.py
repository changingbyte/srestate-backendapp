from django.contrib import admin

from inbox.models import FamilyMember, WhatsappEstateMessage


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