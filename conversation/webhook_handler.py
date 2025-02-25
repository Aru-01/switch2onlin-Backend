from conversation.models import PlatformChoices, MessageTypeChoices


class WebhookParser:
    @staticmethod
    def parse_messenger_event(messaging_event):
        sender_id = messaging_event.get("sender", {}).get("id")
        msg = messaging_event.get("message", {})

        # Skip echo messages (sent by the page/bot) — prevents infinite loop
        if msg.get("is_echo"):
            return None

        attachments = msg.get("attachments", [])

        media_url = None
        msg_type = MessageTypeChoices.TEXT
        if attachments:
            media_url = attachments[0].get("payload", {}).get("url")
            att_type = attachments[0].get("type")
            type_map = {
                "image": MessageTypeChoices.IMAGE,
                "video": MessageTypeChoices.VIDEO,
                "audio": MessageTypeChoices.AUDIO,
                "file": MessageTypeChoices.FILE,
            }
            msg_type = type_map.get(att_type, MessageTypeChoices.FILE)

        return {
            "sender_id": sender_id,
            "platform": PlatformChoices.FACEBOOK,
            "msg_id": msg.get("mid"),
            "text": msg.get("text"),
            "media_url": media_url,
            "msg_type": msg_type,
            "sender_name": None,
        }

    @staticmethod
    def parse_instagram_event(messaging_event):
        sender_id = messaging_event.get("sender", {}).get("id")
        msg = messaging_event.get("message", {})

        # Skip echo messages (sent by the bot) — prevents infinite loop
        if msg.get("is_echo"):
            return None

        attachments = msg.get("attachments", [])

        media_url = None
        msg_type = MessageTypeChoices.TEXT
        if attachments:
            media_url = attachments[0].get("payload", {}).get("url")
            att_type = attachments[0].get("type")
            type_map = {
                "image": MessageTypeChoices.IMAGE,
                "video": MessageTypeChoices.VIDEO,
                "audio": MessageTypeChoices.AUDIO,
                "file": MessageTypeChoices.FILE,
            }
            msg_type = type_map.get(att_type, MessageTypeChoices.FILE)

        return {
            "sender_id": sender_id,
            "platform": PlatformChoices.INSTAGRAM,
            "msg_id": msg.get("mid"),
            "text": msg.get("text"),
            "media_url": media_url,
            "msg_type": msg_type,
            "sender_name": None,
        }

    @staticmethod
    def parse_whatsapp_event(msg, contacts=None):
        whatsapp_type = msg.get("type")
        msg_type = MessageTypeChoices.TEXT
        media_url = None
        text_content = None

        # Map WhatsApp types to our internal MessageTypeChoices
        type_map = {
            "image": MessageTypeChoices.IMAGE,
            "video": MessageTypeChoices.VIDEO,
            "audio": MessageTypeChoices.AUDIO,
            "document": MessageTypeChoices.FILE,
            "sticker": MessageTypeChoices.STICKER,
            "location": MessageTypeChoices.LOCATION,
        }

        if whatsapp_type in type_map:
            msg_type = type_map[whatsapp_type]
            media_data = msg.get(whatsapp_type, {})
            media_url = media_data.get("id")
            # --- CAPTION FIX ---
            # Extract caption from image/video/document if it exists
            text_content = media_data.get("caption")

        # If it's a plain text message, get the body
        if whatsapp_type == "text":
            text_content = msg.get("text", {}).get("body")

        # --- NAME FIX ---
        sender_name = None
        sender_id = msg.get("from")
        if contacts:
            for contact in contacts:
                if contact.get("wa_id") == sender_id:
                    profile = contact.get("profile", {})
                    sender_name = profile.get("name")
                    break

        return {
            "sender_id": sender_id,
            "platform": PlatformChoices.WHATSAPP,
            "msg_id": msg.get("id"),
            "text": text_content,
            "media_url": media_url,
            "msg_type": msg_type,
            "sender_name": sender_name,
        }
