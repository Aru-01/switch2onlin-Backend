from rest_framework import views, permissions, status
from rest_framework.response import Response
import requests
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ai_proxy.schemas import (
    PRODUCT_LIST_PARAMETERS,
    PRODUCT_LIST_RESPONSE,
    CATEGORY_CREATE_REQUEST,
    CATEGORY_CREATE_RESPONSE,
    CATEGORY_DETAILS_RESPONSE,
    CATEGORY_LIST_PARAMETERS,
    CATEGORY_LIST_RESPONSE,
    CATEGORY_OBJECT_SCHEMA,
)


class BaseAIProxyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_base_url(self):
        base_url = getattr(settings, "AI_BOT_BASE_URL", "").rstrip("/")
        if not base_url:
            raise Exception("AI_BOT_BASE_URL not configured")
        return base_url

    def proxy_request(self, method, path, data=None, params=None, files=None):
        try:
            base_url = self.get_base_url()
            target_url = f"{base_url}/{path.lstrip('/')}"

            # Forward the request to AI backend
            response = requests.request(
                method=method,
                url=target_url,
                json=data if not files else None,
                data=data if files else None,
                params=params,
                files=files,
                timeout=30,
            )

            # Try to return JSON if possible, otherwise return raw content
            try:
                return Response(response.json(), status=response.status_code)
            except ValueError:
                return Response(response.content, status=response.status_code)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RateProxyView(BaseAIProxyView):
    """
    Proxy for /rate endpoint
    """

    permission_classes = [permissions.AllowAny]  # Matching original BotRateProxyView

    @swagger_auto_schema(
        operation_summary="Get current rate",
        tags=["AI Proxy"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/rate")

    @swagger_auto_schema(
        operation_summary="Update rate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "iqd_rate": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        ),
        tags=["AI Proxy"],
    )
    def post(self, request):
        return self.proxy_request("POST", "/rate", data=request.data)


class PromptProxyView(BaseAIProxyView):
    """
    Proxy for /prompt endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get AI prompt",
        tags=["AI Proxy"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/prompt")

    @swagger_auto_schema(
        operation_summary="Update AI prompt",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "prompt": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        tags=["AI Proxy"],
    )
    def put(self, request):
        return self.proxy_request("PUT", "/prompt", data=request.data)


class KnowledgeProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge endpoint
    """

    @swagger_auto_schema(
        operation_summary="List knowledge base",
        tags=["AI Proxy"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/knowledge")


class KnowledgeUploadProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge/upload endpoint
    """

    @swagger_auto_schema(
        operation_summary="Upload to knowledge base",
        tags=["AI Proxy"],
    )
    def post(self, request):
        # Handle file upload proxying
        files = {
            k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()
        }
        # Remove files from data to avoid double sending or errors
        data = {k: v for k, v in request.data.items() if k not in request.FILES}
        return self.proxy_request("POST", "/knowledge/upload", data=data, files=files)


class KnowledgeDetailProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge/{knowledge_id} endpoint
    """

    @swagger_auto_schema(
        operation_summary="Delete knowledge item",
        tags=["AI Proxy"],
    )
    def delete(self, request, knowledge_id):
        return self.proxy_request("DELETE", f"/knowledge/{knowledge_id}")


class ProductTemplateProxyView(BaseAIProxyView):
    """
    Proxy for /products/upload-template endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get product upload template",
        tags=["AI Proxy"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/products/upload-template")


class ProductUploadProxyView(BaseAIProxyView):
    """
    Proxy for /products/upload endpoint
    """

    @swagger_auto_schema(
        operation_summary="Upload products",
        tags=["AI Proxy"],
    )
    def post(self, request):
        files = {
            k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()
        }
        # Remove files from data to avoid double sending or errors
        data = {k: v for k, v in request.data.items() if k not in request.FILES}
        return self.proxy_request("POST", "/products/upload", data=data, files=files)


class ProductFilterProxyView(BaseAIProxyView):
    """
    Proxy for /products/filters endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get product filters",
        tags=["AI Proxy"],
    )
    def get(self, request):
        return self.proxy_request(
            "GET", "/products/filters", params=request.query_params
        )


class ProductListProxyView(BaseAIProxyView):
    """
    Proxy for /products endpoint
    """

    @swagger_auto_schema(
        operation_summary="List Products",
        operation_description="""
List, search, filter and paginate products.
""",
        tags=["AI Proxy"],
        manual_parameters=PRODUCT_LIST_PARAMETERS,
        responses={200: PRODUCT_LIST_RESPONSE},
    )
    def get(self, request):
        return self.proxy_request("GET", "/products", params=request.query_params)


class ProductDetailProxyView(BaseAIProxyView):
    """
    Proxy for /products/{barcode} endpoints (GET, PUT, DELETE)
    """

    @swagger_auto_schema(
        operation_summary="Get product by barcode",
        tags=["AI Proxy"],
    )
    def get(self, request, barcode):
        return self.proxy_request("GET", f"/products/{barcode}")

    @swagger_auto_schema(
        operation_summary="Update product by barcode",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "price": openapi.Schema(type=openapi.TYPE_NUMBER),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "category": openapi.Schema(type=openapi.TYPE_STRING),
                "stock": openapi.Schema(type=openapi.TYPE_INTEGER),
                "image_url": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        tags=["AI Proxy"],
    )
    def put(self, request, barcode):
        return self.proxy_request("PUT", f"/products/{barcode}", data=request.data)

    @swagger_auto_schema(
        operation_summary="Delete product by barcode",
        tags=["AI Proxy"],
    )
    def delete(self, request, barcode):
        return self.proxy_request("DELETE", f"/products/{barcode}")


class CategoryListCreateProxyView(BaseAIProxyView):
    """
    Proxy for /categories endpoint
    """

    @swagger_auto_schema(
        operation_summary="List Categories",
        operation_description="""
Retrieve category list with:

- Search
- Active filter
- Pagination
""",
        tags=["AI Proxy Categories"],
        manual_parameters=CATEGORY_LIST_PARAMETERS,
        responses={
            200: CATEGORY_LIST_RESPONSE,
        },
    )
    def get(self, request):
        return self.proxy_request("GET", "/categories", params=request.query_params)

    @swagger_auto_schema(
        operation_summary="Create Category",
        operation_description="""
Create a new category.

Features:
- Case-insensitive duplicate detection
- Arabic name support
""",
        tags=["AI Proxy Categories"],
        request_body=CATEGORY_CREATE_REQUEST,
        responses={
            201: CATEGORY_CREATE_RESPONSE,
        },
    )
    def post(self, request):
        return self.proxy_request("POST", "/categories", data=request.data)


class CategoryDetailsProxyView(BaseAIProxyView):
    """
    Proxy for /categories/{id} endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get Category Details",
        operation_description="Retrieve category details by ID",
        tags=["AI Proxy Categories"],
        responses={
            200: CATEGORY_DETAILS_RESPONSE,
        },
    )
    def get(self, request, id):
        return self.proxy_request("GET", f"/categories/{id}")
