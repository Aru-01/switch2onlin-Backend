from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework import viewsets, views, status, response, generics
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from conversation.models import (
    ConversationSender,
    ConversationMessage,
    PlatformChoices,
)
from conversation.serializers import (
    ConversationSenderSerializer,
    ConversationMessageSerializer,
)
from conversation.services import MetaApiService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class WebhookView(views.APIView):
    """
    Handles Meta Webhook verification (GET) and incoming events (POST).
    """

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Meta Webhook Verification (GET)",
        responses={200: openapi.Response("Challenge code")},
        tags=["Conversations"],
    )
    def get(self, request):
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        verify_token = getattr(settings, "META_VERIFY_TOKEN", "my_verify_token")

        if mode == "subscribe" and token == verify_token:
            return response.Response(int(challenge), status=status.HTTP_200_OK)
        return response.Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Handle incoming Meta Webhook events (POST)",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={200: "EVENT_RECEIVED"},
        tags=["Conversations"],
    )
    def post(self, request):
        service = MetaApiService()
        service.handle_webhook(request.data)
        return response.Response("EVENT_RECEIVED", status=status.HTTP_200_OK)


class ConversationSenderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for listing and retrieving senders (users).
    Messages are intentionally excluded from the list view for performance.
    """

    queryset = ConversationSender.objects.all().order_by("-last_interaction")
    serializer_class = ConversationSenderSerializer

    @swagger_auto_schema(tags=["Conversations"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Conversations"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieves all messages for a specific sender.",
        responses={200: ConversationMessageSerializer(many=True)},
        tags=["Conversations"],
    )
    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """
        Retrieves all messages for a specific sender.
        Access via: /api/v1/conversation/senders/{id}/messages/
        """
        sender = self.get_object()
        messages = sender.messages.all().order_by("timestamp")
        serializer = ConversationMessageSerializer(messages, many=True, context={"request": request})
        return response.Response(serializer.data)


class SendMessageView(views.APIView):
    """
    API to send a message (text or image) to a specific recipient.
    """

    @swagger_auto_schema(
        operation_description="Send a message (text or image) to a Meta recipient.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "recipient_id": openapi.Schema(type=openapi.TYPE_STRING),
                "text": openapi.Schema(type=openapi.TYPE_STRING),
                "image_url": openapi.Schema(type=openapi.TYPE_STRING),
                "platform": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["facebook", "instagram", "whatsapp"]
                ),
            },
            required=["recipient_id"],
        ),
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT)},
        tags=["Conversations"],
    )
    def post(self, request):
        recipient_id = request.data.get("recipient_id")
        text = request.data.get("text")
        image_url = request.data.get("image_url")
        platform = request.data.get("platform", PlatformChoices.FACEBOOK)

        if not recipient_id:
            return response.Response(
                {"error": "recipient_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not text and not image_url:
            return response.Response(
                {"error": "text or image_url is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = MetaApiService()
        message_data = {}
        if text:
            message_data = {"type": "text", "text": text}
        elif image_url:
            message_data = {"type": "image", "link": image_url}

        result = service.send_message(recipient_id, message_data, platform)
        if result:
            return response.Response(result, status=status.HTTP_200_OK)
        return response.Response(
            {"error": "Failed to send message"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class MediaProxyView(views.APIView):
    """
    Proxies media content from Meta Graph API using its ID.
    This resolves the 'wamid' media IDs into actual image/file data.
    """

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Resolves and serves media (image/video/file) from Meta using its ID.",
        manual_parameters=[
            openapi.Parameter(
                "media_id",
                openapi.IN_PATH,
                description="The Meta Media ID",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "Binary media data"},
        tags=["Conversations"],
    )
    def get(self, request, media_id):
        # Check if we already have this message and if it's already persisted
        msg = ConversationMessage.objects.filter(media_url=media_id).first()
        
        service = MetaApiService()
        
        # If the message exists, we can try to persist it now if not done yet
        if msg:
            service.download_and_persist_media(media_id, msg)
            if not str(msg.media_url).isdigit():
                # It was just persisted! Redirect to the new local URL
                from django.urls import reverse
                serializer = ConversationMessageSerializer(msg, context={"request": request})
                return response.Response({"url": serializer.data["media_url"]}, status=302)

        # Fallback to direct proxy for IDs that aren't yet in our local DB or failed to persist
        status_code, media_info = service.client.get_media_info(media_id)

        if status_code != 200:
            return response.Response(
                {
                    "error": "Meta API Error (Media Info)",
                    "status_code": status_code,
                    "details": media_info,
                },
                status=status_code,
            )

        download_url = media_info.get("url")
        if not download_url:
            return response.Response(
                {"error": "Download URL not found in Meta response"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Download the actual bytes from Meta CDN
        media_response = service.client.download_media_content(download_url)
        if not media_response or media_response.status_code != 200:
            return response.Response(
                {"error": "Failed to download media bytes from Meta CDN"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Proxies the response with original Content-Type
        return StreamingHttpResponse(
            media_response.iter_content(chunk_size=8192),
            content_type=media_info.get("mime_type", "application/octet-stream"),
        )


