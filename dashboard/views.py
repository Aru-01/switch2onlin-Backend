from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from conversation.models import ConversationSender, PlatformChoices, ConversationMessage
from conversation.serializers import ConversationSenderSerializer
from leads.models import Lead
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get general dashboard statistics (counts, last 7 days activity, platform distribution).",
        tags=["Dashboard-stats"],
    )
    def get(self, request):
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=6)

        stats = {
            "total_conversations": ConversationSender.objects.count(),
            "today_conversations": ConversationSender.objects.filter(
                created_at__date=today
            ).count(),
            "total_leads": Lead.objects.count(),
            "today_leads": Lead.objects.filter(date__date=today).count(),
        }

        daily_activity = (
            ConversationMessage.objects.filter(timestamp__date__gte=seven_days_ago)
            .annotate(date=TruncDate("timestamp"))
            .values("date")
            .annotate(active_users=Count("sender", distinct=True))
            .order_by("date")
        )

        activity_map = {item["date"]: item["active_users"] for item in daily_activity}

        last_7_days = {}
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_name = day.strftime("%a")
            last_7_days[day_name] = activity_map.get(day, 0)

        platform_counts = ConversationSender.objects.values("platform").annotate(
            count=Count("platform")
        )
        total = stats["total_conversations"]
        platform_distribution = {p[0]: 0 for p in PlatformChoices.choices}

        if total > 0:
            for item in platform_counts:
                platform_distribution[item["platform"]] = round(
                    (item["count"] / total) * 100, 2
                )

        data = {
            **stats,
            "conversations_last_7_days": last_7_days,
            "platform_distribution": platform_distribution,
        }
        return Response(data)


class RecentConversationView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get 5 most recent conversations.",
        tags=["Dashboard-stats"],
    )
    def get(self, request):
        recent_senders = ConversationSender.objects.all().order_by("-last_interaction")[
            :5
        ]
        serializer = ConversationSenderSerializer(recent_senders, many=True)
        return Response(serializer.data)


class TrendingProductsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get top 5 trending products from leads in the last 7 days.",
        tags=["Dashboard-stats"],
    )
    def get(self, request):
        seven_days_ago = timezone.now().date() - timedelta(days=7)

        trending = (
            Lead.objects.filter(date__date__gte=seven_days_ago)
            .values("interested_product")
            .annotate(queries=Count("id"))
            .order_by("-queries")[:5]
        )

        return Response(trending)
