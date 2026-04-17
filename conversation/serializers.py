from rest_framework import serializers
from conversation.models import (
    ConversationSender,
    ConversationMessage,
)
from django.urls import reverse
from django.conf import settings


class ConversationMessageSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = ConversationMessage
        fields = "__all__"

    def get_media_url(self, obj):
        if not obj.media_url:
            return None
        
        request = self.context.get("request")
        
        # Check if it's already an absolute URL
        if str(obj.media_url).startswith(("http://", "https://")):
            return obj.media_url

        # Check if it's a local persisted path (e.g., 'conversations/...')
        # We check if it looks like a path or doesn't look like a numeric ID
        if not str(obj.media_url).isdigit():
            if not request:
                return f"{settings.MEDIA_URL}{obj.media_url}"
            return request.build_absolute_uri(f"{settings.MEDIA_URL}{obj.media_url}")

        # If it's a numeric ID (WhatsApp/Meta Media ID), use the proxy
        if request:
            url_path = reverse("media_proxy", kwargs={"media_id": obj.media_url})
            return request.build_absolute_uri(url_path)
        
        return obj.media_url


class ConversationSenderSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and retrieving senders without nested messages.
    """

    class Meta:
        model = ConversationSender
        fields = [
            "id",
            "sender_id",
            "full_name",
            "profile_pic_url",
            "platform",
            "last_interaction",
            "created_at",
        ]
