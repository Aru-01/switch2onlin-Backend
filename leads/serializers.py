from rest_framework import serializers
from leads.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="sender.full_name", read_only=True)
    platform = serializers.CharField(source="sender.platform", read_only=True)
    sender_id = serializers.CharField(source="sender.sender_id", read_only=True)

    class Meta:
        model = Lead
        fields = ["id", "sender_id", "name", "interested_product", "platform", "date"]
        read_only_fields = ["id", "date"]
