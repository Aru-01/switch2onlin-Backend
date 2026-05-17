from django.urls import path
from ai_proxy.views import (
    RateProxyView,
    PromptProxyView,
    KnowledgeProxyView,
    KnowledgeUploadProxyView,
    KnowledgeDetailProxyView,
    ProductTemplateProxyView,
    ProductUploadProxyView,
    ProductFilterProxyView,
    ProductListProxyView,
    ProductDetailProxyView,
    CategoryDetailsProxyView,
    CategoryListCreateProxyView,
)

urlpatterns = [
    path("rate/", RateProxyView.as_view(), name="ai-rate-proxy"),
    path("prompt/", PromptProxyView.as_view(), name="ai-prompt-proxy"),
    path("knowledge/", KnowledgeProxyView.as_view(), name="ai-knowledge-proxy"),
    path(
        "knowledge/upload/",
        KnowledgeUploadProxyView.as_view(),
        name="ai-knowledge-upload-proxy",
    ),
    path(
        "knowledge/<str:knowledge_id>/",
        KnowledgeDetailProxyView.as_view(),
        name="ai-knowledge-detail-proxy",
    ),
    path(
        "products/filters/",
        ProductFilterProxyView.as_view(),
        name="ai-product-filter-proxy",
    ),
    path(
        "products/upload-template/",
        ProductTemplateProxyView.as_view(),
        name="ai-product-template-proxy",
    ),
    path(
        "products/upload/",
        ProductUploadProxyView.as_view(),
        name="ai-product-upload-proxy",
    ),
    path("products/", ProductListProxyView.as_view(), name="ai-product-list-proxy"),
    path(
        "products/<str:barcode>/",
        ProductDetailProxyView.as_view(),
        name="ai-product-detail-proxy",
    ),
    path(
        "categories/",
        CategoryListCreateProxyView.as_view(),
        name="proxy-category-list-create",
    ),
    path(
        "categories/<int:id>/",
        CategoryDetailsProxyView.as_view(),
        name="proxy-category-details",
    ),
]
