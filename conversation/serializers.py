from rest_framework import serializers
from conversation.models import (
    ConversationSender,
    ConversationMessage,
)
from django.urls import reverse


class ConversationMessageSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = ConversationMessage
        fields = "__all__"

    def get_media_url(self, obj):
        if not obj.media_url:
            return None
        
        # If media_url is a numeric ID (WhatsApp/Meta Media ID)
        if obj.media_url.isdigit():
            request = self.context.get("request")
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
