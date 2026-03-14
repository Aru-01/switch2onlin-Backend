from django.urls import path
from ai_proxy import views
from ai_proxy.views import (
    ProductDetailProxyView,
    CategoryDetailsProxyView,
    CategoryListCreateProxyView,
    BrandDetailsProxyView,
    BrandListCreateProxyView,
    SubcategoryDetailsProxyView,
    SubcategoryListCreateProxyView,
)

urlpatterns = [
    path("rate/", views.RateProxyView.as_view(), name="ai-rate-proxy"),
    path("prompt/", views.PromptProxyView.as_view(), name="ai-prompt-proxy"),
    path("knowledge/", views.KnowledgeProxyView.as_view(), name="ai-knowledge-proxy"),
    path(
        "knowledge/upload/",
        views.KnowledgeUploadProxyView.as_view(),
        name="ai-knowledge-upload-proxy",
    ),
    path(
        "knowledge/<str:knowledge_id>/",
        views.KnowledgeDetailProxyView.as_view(),
        name="ai-knowledge-detail-proxy",
    ),
    path(
        "products/filters/",
        views.ProductFilterProxyView.as_view(),
        name="ai-product-filter-proxy",
    ),
    path(
        "products/upload-template/",
        views.ProductTemplateProxyView.as_view(),
        name="ai-product-template-proxy",
    ),
    path(
        "products/upload/",
        views.ProductUploadProxyView.as_view(),
        name="ai-product-upload-proxy",
    ),
    path(
        "products/", views.ProductListProxyView.as_view(), name="ai-product-list-proxy"
    ),
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
    path(
        "brands/",
        BrandListCreateProxyView.as_view(),
        name="proxy-brand-list-create",
    ),
    path(
        "brands/<int:id>/",
        BrandDetailsProxyView.as_view(),
        name="proxy-brand-details",
    ),
    path(
        "subcategories/",
        SubcategoryListCreateProxyView.as_view(),
        name="proxy-subcategory-list-create",
    ),
    path(
        "subcategories/<int:id>/",
        SubcategoryDetailsProxyView.as_view(),
        name="proxy-subcategory-details",
    ),
]
