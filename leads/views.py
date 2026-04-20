from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from leads.models import Lead
from leads.serializers import LeadSerializer
from leads.permissions import IsAIBotOrAdmin
from conversation.models import ConversationSender
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LeadPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("sender").all().order_by("-date")
    serializer_class = LeadSerializer
    pagination_class = LeadPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["sender__platform"]
    search_fields = ["interested_product"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def check_permissions(self, request):
        if self.action == "create":
            perm = IsAIBotOrAdmin()
            if not perm.has_permission(request, self):
                self.permission_denied(
                    request, message="Invalid API Key or Unauthorized"
                )
        else:
            super().check_permissions(request)

    @swagger_auto_schema(
        operation_description="Create a new lead. Bot only needs to send 'user_id' and 'interested_product'.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id", "interested_product"],
            properties={
                "user_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Meta Sender ID"
                ),
                "interested_product": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={201: LeadSerializer()},
        tags=["Leads"],
    )
    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        interested_product = request.data.get("interested_product")

        if not user_id or not interested_product:
            return Response(
                {"error": "user_id and interested_product are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sender = ConversationSender.objects.filter(sender_id=user_id).first()
        if not sender:
            return Response(
                {"error": f"No conversation found for user_id: {user_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        lead = Lead.objects.create(sender=sender, interested_product=interested_product)

        serializer = self.get_serializer(lead)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="List all leads. Admin only.",
        responses={200: LeadSerializer(many=True)},
        tags=["Leads"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Leads"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Leads"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Leads"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Leads"])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
