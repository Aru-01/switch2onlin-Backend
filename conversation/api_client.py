import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class MetaApiClient:
    def __init__(self):
        self.page_access_token = getattr(settings, "META_PAGE_ACCESS_TOKEN", "")
        self.whatsapp_phone_number_id = getattr(settings, "META_WHATSAPP_PHONE_NUMBER_ID", "")

    def get_headers(self):
        if not self.page_access_token:
            return {}
        return {"Authorization": f"Bearer {self.page_access_token}"}

    def send_meta_request(self, url, payload):
        """
        Base method to send POST requests to Meta.
        """
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta API Request Error: {str(e)}")
            return 500, {"error": str(e)}

    def fetch_user_profile(self, user_id, fields):
        """
        Fetches user profile data from Meta.
        """
        url = f"https://graph.facebook.com/v21.0/{user_id}?fields={fields}&access_token={self.page_access_token}"
        try:
            response = requests.get(url)
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta Profile Fetch Error: {str(e)}")
            return 500, {"error": str(e)}

    def get_media_info(self, media_id):
        """
        Gets the download URL for a given Meta Media ID.
        """
        url = f"https://graph.facebook.com/v21.0/{media_id}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code != 200:
                logger.error(f"Meta Media Info Error: {response.status_code} - {response.text}")
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta Media Info Exception: {str(e)}")
            return 500, {"error": str(e)}

    def download_media_content(self, url):
        """
        Downloads the raw media bytes from a Meta CDN URL.
        """
        try:
            # Note: Meta CDN URLs often require the same Bearer token
            response = requests.get(url, headers=self.get_headers(), stream=True)
            return response
        except Exception as e:
            logger.error(f"Meta Media Download Error: {str(e)}")
            return None
