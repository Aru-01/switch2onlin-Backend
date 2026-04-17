from django.db import models


class PlatformChoices(models.TextChoices):
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    WHATSAPP = "whatsapp", "WhatsApp"


class MessageTypeChoices(models.TextChoices):
    TEXT = "text", "Text"
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    FILE = "file", "File"
    STICKER = "sticker", "Sticker"
    LOCATION = "location", "Location"


class ConversationSender(models.Model):
    sender_id = models.CharField(max_length=255, unique=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    profile_pic_url = models.URLField(max_length=1000, blank=True, null=True)
    platform = models.CharField(
        max_length=20, choices=PlatformChoices.choices, default=PlatformChoices.FACEBOOK
    )
    last_interaction = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name or self.sender_id} ({self.platform})"


class ConversationMessage(models.Model):
    sender = models.ForeignKey(
        ConversationSender, on_delete=models.CASCADE, related_name="messages"
    )
    message_id = models.CharField(max_length=255, unique=True, db_index=True)
    text_content = models.TextField(blank=True, null=True)
    media_url = models.CharField(max_length=1000, blank=True, null=True)
    message_type = models.CharField(
        max_length=20,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.TEXT,
    )
    is_from_customer = models.BooleanField(default=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        direction = "Incoming" if self.is_from_customer else "Outgoing"
        return f"{direction} - {self.sender.full_name or self.sender.sender_id} at {self.timestamp}"
