from conversation.models import PlatformChoices, MessageTypeChoices

class WebhookParser:
    @staticmethod
    def parse_messenger_event(messaging_event):
        sender_id = messaging_event.get("sender", {}).get("id")
        msg = messaging_event.get("message", {})
        attachments = msg.get("attachments", [])
        
        media_url = None
        msg_type = MessageTypeChoices.TEXT
        if attachments:
            media_url = attachments[0].get("payload", {}).get("url")
            msg_type = MessageTypeChoices.IMAGE if attachments[0].get("type") == "image" else MessageTypeChoices.FILE
        
        return {
            "sender_id": sender_id,
            "platform": PlatformChoices.FACEBOOK,
            "msg_id": msg.get("mid"),
            "text": msg.get("text"),
            "media_url": media_url,
            "msg_type": msg_type
        }

    @staticmethod
    def parse_instagram_event(messaging_event):
        sender_id = messaging_event.get("sender", {}).get("id")
        msg = messaging_event.get("message", {})
        attachments = msg.get("attachments", [])
        
        media_url = None
        msg_type = MessageTypeChoices.TEXT
        if attachments:
            media_url = attachments[0].get("payload", {}).get("url")
            msg_type = MessageTypeChoices.IMAGE if attachments[0].get("type") == "image" else MessageTypeChoices.FILE
        
        return {
            "sender_id": sender_id,
            "platform": PlatformChoices.INSTAGRAM,
            "msg_id": msg.get("mid"),
            "text": msg.get("text"),
            "media_url": media_url,
            "msg_type": msg_type
        }

    @staticmethod
    def parse_whatsapp_event(msg):
        msg_type = MessageTypeChoices.IMAGE if msg.get("type") == "image" else MessageTypeChoices.TEXT
        media_url = msg.get("image", {}).get("id") if msg.get("type") == "image" else None
        
        return {
            "sender_id": msg.get("from"),
            "platform": PlatformChoices.WHATSAPP,
            "msg_id": msg.get("id"),
            "text": msg.get("text", {}).get("body"),
            "media_url": media_url,
            "msg_type": msg_type
        }
