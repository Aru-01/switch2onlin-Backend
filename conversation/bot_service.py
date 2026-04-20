import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self):
        base_url = getattr(settings, "AI_BOT_BASE_URL", "").rstrip("/")
        if not base_url:
            logger.warning("AI_BOT_BASE_URL is not configured in settings/.env")
            self.api_url = None
        else:
            self.api_url = f"{base_url}/reply"

    def get_bot_reply_for_message(self, message_obj):
        """
        Wrapper that extracts data from a message object and constructs a public URL if needed.
        """
        user_id = message_obj.sender.sender_id
        platform = message_obj.sender.platform
        message = message_obj.text_content
        media_url = message_obj.media_url

        bot_image_url = None

        if media_url:
            if str(media_url).startswith(("http://", "https://")):
                bot_image_url = media_url
            elif not str(media_url).isdigit():
                site_url = ""
                csrf_origins = getattr(settings, "CSRF_TRUSTED_ORIGINS", [])
                if csrf_origins:
                    for origin in csrf_origins:
                        if "localhost" not in origin and "127.0.0.1" not in origin:
                            site_url = origin.rstrip("/")
                            break

                if site_url:
                    bot_image_url = f"{site_url}{settings.MEDIA_URL}{media_url}"
                else:
                    logger.warning(
                        "BotService: Could not determine public SITE_URL for local media."
                    )

        return self.get_bot_reply(user_id, message, bot_image_url, platform)

    def get_bot_reply(self, user_id, message, image_url=None, platform=None):
        """
        Sends a message to the external AI bot and returns the response.
        """
        if not self.api_url:
            logger.error("BotService: API URL is not configured. Cannot get reply.")
            return None

        payload = {
            "user_id": user_id,
            "message": message or "",
            "image_url": image_url,
            "platform": platform,
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"BotService: Received response for {user_id}")
                return {
                    "reply": data.get("reply"),
                    "image_url": data.get("image_url"),
                    "products": data.get("products", []),
                }
            else:
                logger.error(
                    f"BotService Error: {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"BotService Exception: {str(e)}")
            return None
