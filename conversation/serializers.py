from rest_framework import serializers
from conversation.models import (
    ConversationSender,
    ConversationMessage,
)


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = "__all__"


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
