import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from conversation.models import ConversationSender, ConversationMessage, PlatformChoices, MessageTypeChoices
from conversation.views import MediaProxyView
from conversation.serializers import ConversationMessageSerializer
from django.utils import timezone

class MediaProxyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sender = ConversationSender.objects.create(
            sender_id="whatsapp_user", platform=PlatformChoices.WHATSAPP
        )

    @patch('conversation.api_client.MetaApiClient.get_media_info')
    @patch('conversation.api_client.MetaApiClient.download_media_content')
    def test_media_proxy_success(self, mock_download, mock_get_info):
        # Mock Meta API response for media info
        mock_get_info.return_value = (200, {
            "url": "https://meta-cdn.com/asdf",
            "mime_type": "image/jpeg"
        })
        
        # Mock Meta API response for actual download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"fake_image_data"]
        mock_download.return_value = mock_response

        # Request to our proxy
        url = reverse('media_proxy', kwargs={'media_id': '12345'})
        request = self.factory.get(url)
        view = MediaProxyView.as_view()
        response = view(request, media_id='12345')

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        # Check streaming content
        content = b"".join(response.streaming_content)
        self.assertEqual(content, b"fake_image_data")

    def test_serializer_url_transformation(self):
        # Message with a numeric ID as media_url
        msg = ConversationMessage.objects.create(
            sender=self.sender,
            message_id="msg_1",
            media_url="12345",
            message_type="image",
            timestamp=timezone.now()
        )
        
        # Request context for absolute URL construction
        request = self.factory.get('/api/v1/conversation/messages/')
        serializer = ConversationMessageSerializer(msg, context={'request': request})
        
        # Verify the URL is transformed
        data = serializer.data
        self.assertIn('/api/v1/conversation/media/12345/', data['media_url'])
        self.assertTrue(data['media_url'].startswith('http'))
