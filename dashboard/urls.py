from django.urls import path
from .views import DashboardStatsView, RecentConversationView, TrendingProductsView

urlpatterns = [
    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("recent-conversations/", RecentConversationView.as_view(), name="recent-conversations"),
    path("trending-products/", TrendingProductsView.as_view(), name="trending-products"),
]
