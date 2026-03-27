from django.conf import settings
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
        serializer = ConversationMessageSerializer(messages, many=True)
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
