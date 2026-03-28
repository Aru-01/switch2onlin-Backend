from django.urls import path, include
from rest_framework.routers import DefaultRouter
from conversation.views import (
    WebhookView,
    ConversationSenderViewSet,
    SendMessageView,
    MediaProxyView,
)

router = DefaultRouter()
router.register(r"senders", ConversationSenderViewSet, basename="sender")

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="webhook"),
    path("send-message/", SendMessageView.as_view(), name="send_message"),
    path("media/<str:media_id>/", MediaProxyView.as_view(), name="media_proxy"),
    path("", include(router.urls)),
]
