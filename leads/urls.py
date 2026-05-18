from django.urls import path, include
from rest_framework.routers import DefaultRouter
from leads.views import LeadViewSet
from ai_proxy.views import RateProxyView

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

urlpatterns = [
    path("rate/", RateProxyView.as_view(), name="bot-rate-proxy"),
    path("", include(router.urls)),
]
