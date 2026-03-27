from django.urls import path, include

urlpatterns = [
    path("conversation/", include("conversation.urls")),
    path("", include("agent_manage.urls")),
]
