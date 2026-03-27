from django.contrib import admin
from conversation.models import (
    ConversationSender,
    ConversationMessage,
)


@admin.register(ConversationSender)
class ConversationSenderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "sender_id", "platform", "last_interaction")
    search_fields = ("full_name", "sender_id")
    list_filter = ("platform",)


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "message_type", "is_from_customer", "timestamp")
    list_filter = ("is_from_customer", "message_type", "sender__platform")
    search_fields = ("text_content", "sender__full_name", "sender__sender_id")
