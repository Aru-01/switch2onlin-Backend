import logging
from django.conf import settings
from django.utils import timezone
from conversation.models import (
    ConversationSender,
    ConversationMessage,
    PlatformChoices,
    MessageTypeChoices,
)
from conversation.api_client import MetaApiClient
from conversation.webhook_handler import WebhookParser

logger = logging.getLogger(__name__)

class MetaApiService:
    def __init__(self):
        self.client = MetaApiClient()

    def send_message(self, recipient_id, message_data, platform):
        url = ""
        payload = {}

        if platform == PlatformChoices.WHATSAPP:
            phone_id = self.client.whatsapp_phone_number_id
            url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_id,
                "type": message_data.get("type", "text"),
            }
            if payload["type"] == "text":
                payload["text"] = {"body": message_data.get("text")}
            elif payload["type"] == "image":
                payload["image"] = {"link": message_data.get("link")}

        elif platform in [PlatformChoices.FACEBOOK, PlatformChoices.INSTAGRAM]:
            url = "https://graph.facebook.com/v21.0/me/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "message": {},
            }
            if message_data.get("type") == "text":
                payload["message"]["text"] = message_data.get("text")
            elif message_data.get("type") == "image":
                payload["message"]["attachment"] = {
                    "type": "image",
                    "payload": {"url": message_data.get("link"), "is_reusable": True},
                }

        status_code, response_data = self.client.send_meta_request(url, payload)
        
        if status_code == 200:
            msg_id = response_data.get("message_id") or response_data.get("messages", [{}])[0].get("id")
            self._save_message(
                sender_id=recipient_id,
                platform=platform,
                msg_id=msg_id,
                text=message_data.get("text"),
                media_url=message_data.get("link"),
                msg_type=message_data.get("type", "text"),
                is_from_customer=False
            )
            return response_data
        else:
            logger.error(f"Meta API Error: {status_code} - {response_data}")
            return response_data

    def fetch_user_profile(self, user_id, platform):
        fields = "first_name,last_name,profile_pic" if platform == PlatformChoices.FACEBOOK else "username,profile_picture_url"
        status_code, data = self.client.fetch_user_profile(user_id, fields)
        
        if status_code == 200:
            sender = ConversationSender.objects.filter(sender_id=user_id).first()
            if sender:
                if platform == PlatformChoices.FACEBOOK:
                    sender.full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or "Facebook User"
                    sender.profile_pic_url = data.get("profile_pic")
                else:
                    sender.full_name = data.get("username", "Instagram User")
                    sender.profile_pic_url = data.get("profile_picture_url")
                sender.save()
            return data
        return None

    def handle_webhook(self, data: dict):
        obj_type = data.get("object")
        
        if obj_type in ["page", "instagram"]:
            platform = PlatformChoices.FACEBOOK if obj_type == "page" else PlatformChoices.INSTAGRAM
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    if "message" in event:
                        parsed = WebhookParser.parse_messenger_event(event) if obj_type == "page" else WebhookParser.parse_instagram_event(event)
                        self._save_message(**parsed)

        elif obj_type == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    messages = change.get("value", {}).get("messages", [])
                    for msg in messages:
                        parsed = WebhookParser.parse_whatsapp_event(msg)
                        self._save_message(**parsed)
        return True

    def _save_message(self, sender_id, platform, msg_id, text, media_url, msg_type, is_from_customer=True, timestamp=None):
        sender, _ = ConversationSender.objects.get_or_create(sender_id=sender_id, defaults={"platform": platform})
        sender.save() # Update last_interaction
        
        obj, created = ConversationMessage.objects.get_or_create(
            message_id=msg_id,
            defaults={
                "sender": sender,
                "text_content": text,
                "media_url": media_url,
                "message_type": msg_type,
                "is_from_customer": is_from_customer,
                "timestamp": timestamp or timezone.now()
            }
        )
        if not sender.full_name:
            self.fetch_user_profile(sender_id, platform)
        return obj
