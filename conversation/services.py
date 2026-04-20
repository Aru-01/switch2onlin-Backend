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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import threading
from conversation.bot_service import BotService

logger = logging.getLogger(__name__)


class MetaApiService:
    def __init__(self):
        self.client = MetaApiClient()

    def send_message(self, recipient_id, message_data, platform):
        url = ""
        payload = {}

        token = self.client.get_token_for_platform(platform)

        if platform == PlatformChoices.WHATSAPP:
            phone_id = self.client.whatsapp_phone_number_id
            url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_id,
                "type": message_data.get("type", "text"),
            }
            if payload["type"] == "text":
                payload["text"] = {"body": message_data.get("text")}
            elif payload["type"] == "image":
                payload["image"] = {"link": message_data.get("link")}

        elif platform == PlatformChoices.FACEBOOK:
            url = "https://graph.facebook.com/v25.0/me/messages"
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

        elif platform == PlatformChoices.INSTAGRAM:
            if token and token.startswith("IGA"):
                url = "https://graph.instagram.com/v25.0/me/messages"
            else:
                ig_account_id = getattr(
                    settings, "META_INSTAGRAM_BUSINESS_ACCOUNT_ID", ""
                )
                url = f"https://graph.facebook.com/v25.0/{ig_account_id}/messages"
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

        status_code, response_data = self.client.send_meta_request(
            url, payload, token=token
        )

        logger.info(
            f"[SEND] platform={platform} | recipient={recipient_id} | "
            f"url={url} | status={status_code} | response={response_data}"
        )

        if status_code == 200:
            msg_id = response_data.get("message_id") or response_data.get(
                "messages", [{}]
            )[0].get("id")
            self._save_message(
                sender_id=recipient_id,
                platform=platform,
                msg_id=msg_id,
                text=message_data.get("text"),
                media_url=message_data.get("link"),
                msg_type=message_data.get("type", "text"),
                is_from_customer=False,
            )
            return response_data
        else:
            logger.error(f"Meta API Error: {status_code} - {response_data}")
            return response_data

    def fetch_user_profile(self, user_id, platform):
        if platform == PlatformChoices.WHATSAPP:
            return None
        if platform == PlatformChoices.INSTAGRAM:
            logger.info(
                f"Skipping profile fetch for Instagram user {user_id} "
                "(IGSID lookup not supported with Page token)."
            )
            sender = ConversationSender.objects.filter(sender_id=user_id).first()
            is_placeholder = (
                not sender.full_name
                or sender.full_name == "-"
                or sender.full_name.startswith("User-")
                or sender.full_name.startswith("IG-User-")
            )
            if sender and is_placeholder:
                suffix = user_id[-4:] if len(user_id) >= 4 else user_id
                sender.full_name = f"IG-User-{suffix}"
                sender.save()
            return None

        sender = ConversationSender.objects.filter(sender_id=user_id).first()
        if not sender:
            return None

        fields = "id,name,first_name,last_name,profile_pic"

        token = self.client.get_token_for_platform(platform)
        status_code, data = self.client.fetch_user_profile(user_id, fields, token=token)

        if status_code == 200:
            name = data.get("name")
            username = data.get("username")
            first = data.get("first_name")
            last = data.get("last_name")

            final_name = name or username
            if not final_name and first:
                final_name = f"{first} {last or ''}".strip()

            if final_name:
                sender.full_name = final_name

            pic = data.get("profile_pic")
            if pic:
                sender.profile_pic_url = pic

            logger.info(
                f"Profile OK for {platform} user {user_id}: name='{sender.full_name}'"
            )
        else:
            logger.warning(
                f"Profile fetch failed for {platform} user {user_id}: {data}"
            )

        if not sender.full_name:
            suffix = user_id[-4:] if len(user_id) >= 4 else user_id
            sender.full_name = f"User-{suffix}"

        sender.save()
        return data if status_code == 200 else None

    def handle_webhook(self, data: dict):
        obj_type = data.get("object")

        if obj_type in ["page", "instagram"]:
            platform = (
                PlatformChoices.FACEBOOK
                if obj_type == "page"
                else PlatformChoices.INSTAGRAM
            )
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    if "message" in event:
                        parsed = (
                            WebhookParser.parse_messenger_event(event)
                            if obj_type == "page"
                            else WebhookParser.parse_instagram_event(event)
                        )
                        if parsed is None:
                            continue
                        self._save_message(**parsed)

        elif obj_type == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    for msg in messages:
                        parsed = WebhookParser.parse_whatsapp_event(
                            msg, contacts=contacts
                        )
                        self._save_message(**parsed)
        return True

    def _save_message(
        self,
        sender_id,
        platform,
        msg_id,
        text,
        media_url,
        msg_type,
        is_from_customer=True,
        timestamp=None,
        sender_name=None,
    ):
        sender, _ = ConversationSender.objects.get_or_create(
            sender_id=sender_id, defaults={"platform": platform}
        )

        is_placeholder = (
            not sender.full_name
            or sender.full_name == "-"
            or sender.full_name.startswith("User-")
            or sender.full_name.startswith("IG-User-")
            or sender.full_name == sender_id
        )
        should_update_name = sender_name and (is_placeholder or platform == "whatsapp")

        if should_update_name:
            if sender.full_name != sender_name:
                sender.full_name = sender_name
                sender.save()
            is_placeholder = False  # Name is now set
        else:
            sender.save()

        obj, msg_created = ConversationMessage.objects.get_or_create(
            message_id=msg_id,
            defaults={
                "sender": sender,
                "text_content": text,
                "media_url": media_url,
                "message_type": msg_type,
                "is_from_customer": is_from_customer,
                "timestamp": timestamp or timezone.now(),
            },
        )

        # If message already exists (duplicate webhook / echo), skip processing
        if not msg_created:
            logger.debug(f"Skipping duplicate message_id={msg_id}")
            return obj

        if is_placeholder and platform != PlatformChoices.WHATSAPP:
            self.fetch_user_profile(sender_id, platform)

        if media_url and msg_type != MessageTypeChoices.TEXT:
            self.download_and_persist_media(media_url, obj)

        # Only trigger bot reply for genuinely new customer messages
        if is_from_customer and msg_created:
            threading.Thread(target=self._trigger_bot_reply, args=(obj,)).start()

        return obj

    def _trigger_bot_reply(self, message_obj):
        bot_service = BotService()
        bot_res = bot_service.get_bot_reply_for_message(message_obj)

        if not bot_res:
            return

        sender_id = message_obj.sender.sender_id
        platform = message_obj.sender.platform
        reply_text = bot_res.get("reply")
        image_url = bot_res.get("image_url")
        products = bot_res.get("products", [])

        if reply_text:
            self.send_message(sender_id, {"type": "text", "text": reply_text}, platform)

        if image_url:
            self.send_message(sender_id, {"type": "image", "link": image_url}, platform)

        if products:
            product_text = "*Found Products:*\n"
            for p in products:
                product_text += f"- {p.get('name')} ({p.get('price')})\n"
            self.send_message(
                sender_id, {"type": "text", "text": product_text}, platform
            )

    def download_and_persist_media(self, media_id, message_obj):
        if not str(media_id).isdigit():
            return

        status_code, media_info = self.client.get_media_info(media_id)
        if status_code != 200:
            logger.error(
                f"Persistence: Could not fetch info for media {media_id} - {media_info}"
            )
            return

        download_url = media_info.get("url")
        mime_type = media_info.get("mime_type", "application/octet-stream")

        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "video/mp4": "mp4",
            "audio/mpeg": "mp3",
            "audio/ogg": "ogg",
            "audio/amr": "amr",
            "application/pdf": "pdf",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "image/gif": "gif",
        }
        ext = ext_map.get(
            mime_type, mime_type.split("/")[-1] if "/" in mime_type else "bin"
        )

        media_response = self.client.download_media_content(download_url)
        if not media_response or media_response.status_code != 200:
            logger.error(f"Persistence: Could not download bytes for media {media_id}")
            return

        filename = f"conversations/{media_id}.{ext}"
        if default_storage.exists(filename):
            default_storage.delete(filename)

        path = default_storage.save(filename, ContentFile(media_response.content))
        message_obj.media_url = path
        message_obj.save()
        logger.info(f"Media persisted to: {path}")
