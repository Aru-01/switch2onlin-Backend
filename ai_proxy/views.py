from rest_framework import views, permissions, status
from rest_framework.response import Response
import requests
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ai_proxy import schemas as sc


class BaseAIProxyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_base_url(self):
        base_url = getattr(settings, "AI_BOT_BASE_URL", "").rstrip("/")
        if not base_url:
            raise Exception("AI_BOT_BASE_URL not configured")
        return base_url

    def proxy_request(
        self, method, path, data=None, params=None, files=None, timeout=120
    ):
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
                timeout=timeout,
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
        tags=["AI Proxy - USD To IQD"],
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
        tags=["AI Proxy - USD To IQD"],
    )
    def post(self, request):
        return self.proxy_request("POST", "/rate", data=request.data)


class PromptProxyView(BaseAIProxyView):
    """
    Proxy for /prompt endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get AI prompt",
        tags=["AI Proxy - Prompt"],
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
        tags=["AI Proxy - Prompt"],
    )
    def put(self, request):
        return self.proxy_request("PUT", "/prompt", data=request.data)


class KnowledgeProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge endpoint
    """

    @swagger_auto_schema(
        operation_summary="List knowledge base",
        tags=["AI Proxy - Knowledge Files"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/knowledge")


class KnowledgeUploadProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge/upload endpoint
    """

    @swagger_auto_schema(
        operation_summary="Upload to knowledge base",
        tags=["AI Proxy - Knowledge Files"],
    )
    def post(self, request):
        # Handle file upload proxying
        files = {
            k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()
        }
        # Remove files from data to avoid double sending or errors
        data = {k: v for k, v in request.data.items() if k not in request.FILES}
        return self.proxy_request(
            "POST",
            "/knowledge/upload",
            data=data,
            files=files,
            params=request.query_params,
            timeout=300,
        )


class KnowledgeDetailProxyView(BaseAIProxyView):
    """
    Proxy for /knowledge/{knowledge_id} endpoint
    """

    @swagger_auto_schema(
        operation_summary="Delete knowledge item",
        tags=["AI Proxy - Knowledge Files"],
    )
    def delete(self, request, knowledge_id):
        return self.proxy_request("DELETE", f"/knowledge/{knowledge_id}")


class ProductTemplateProxyView(BaseAIProxyView):
    """
    Proxy for /products/upload-template endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get product upload template",
        tags=["AI Proxy - Products"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/products/upload-template")


class ProductUploadProxyView(BaseAIProxyView):
    """
    Proxy for /products/upload endpoint
    """

    @swagger_auto_schema(
        operation_summary="Upload products",
        tags=["AI Proxy - Products"],
    )
    def post(self, request):
        files = {
            k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()
        }
        # Remove files from data to avoid double sending or errors
        data = {k: v for k, v in request.data.items() if k not in request.FILES}
        return self.proxy_request(
            "POST",
            "/products/upload",
            data=data,
            files=files,
            params=request.query_params,
            timeout=300,
        )


class ProductFilterProxyView(BaseAIProxyView):
    """
    Proxy for /products/filters endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get product filters",
        tags=["AI Proxy - Products"],
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
        tags=["AI Proxy - Products"],
        manual_parameters=sc.PRODUCT_LIST_PARAMETERS,
        responses={200: sc.PRODUCT_LIST_RESPONSE},
    )
    def get(self, request):
        return self.proxy_request("GET", "/products", params=request.query_params)


class ProductDetailProxyView(BaseAIProxyView):
    """
    Proxy for /products/{barcode} endpoints (GET, PUT, DELETE)
    """

    @swagger_auto_schema(
        operation_summary="Get product by barcode",
        tags=["AI Proxy - Products Barcode"],
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
        tags=["AI Proxy - Products Barcode"],
    )
    def put(self, request, barcode):
        return self.proxy_request("PUT", f"/products/{barcode}", data=request.data)

    @swagger_auto_schema(
        operation_summary="Delete product by barcode",
        tags=["AI Proxy - Products Barcode"],
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
        manual_parameters=sc.CATEGORY_LIST_PARAMETERS,
        responses={
            200: sc.CATEGORY_LIST_RESPONSE,
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
        request_body=sc.CATEGORY_CREATE_REQUEST,
        responses={
            201: sc.CATEGORY_CREATE_RESPONSE,
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
            200: sc.CATEGORY_DETAILS_RESPONSE,
        },
    )
    def get(self, request, id):
        return self.proxy_request("GET", f"/categories/{id}")


class BrandListCreateProxyView(BaseAIProxyView):
    """
    Proxy for /brands endpoint
    """

    @swagger_auto_schema(
        operation_summary="List Brands",
        operation_description="""
Retrieve brand list with:

- Search
- Active filter
- Pagination
""",
        tags=["AI Proxy Brands"],
        manual_parameters=sc.BRAND_LIST_PARAMETERS,
        responses={
            200: sc.BRAND_LIST_RESPONSE,
        },
    )
    def get(self, request):
        return self.proxy_request("GET", "/brands", params=request.query_params)

    @swagger_auto_schema(
        operation_summary="Create Brand",
        operation_description="""
Create a new brand.

Features:
- Case-insensitive duplicate detection
- Arabic name support
""",
        tags=["AI Proxy Brands"],
        request_body=sc.BRAND_CREATE_REQUEST,
        responses={
            201: sc.BRAND_CREATE_RESPONSE,
        },
    )
    def post(self, request):
        return self.proxy_request("POST", "/brands", data=request.data)


class BrandDetailsProxyView(BaseAIProxyView):
    """
    Proxy for /brands/{id} endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get Brand Details",
        operation_description="Retrieve brand details by ID",
        tags=["AI Proxy Brands"],
        responses={
            200: sc.BRAND_DETAILS_RESPONSE,
        },
    )
    def get(self, request, id):
        return self.proxy_request("GET", f"/brands/{id}")


class SubcategoryListCreateProxyView(BaseAIProxyView):
    """
    Proxy for /subcategories endpoint
    """

    @swagger_auto_schema(
        operation_summary="List Subcategories",
        operation_description="""
Retrieve subcategory list with:

- Parent category filtering
- Search
- Active filter
- Pagination
""",
        tags=["AI Proxy Subcategories"],
        manual_parameters=sc.SUBCATEGORY_LIST_PARAMETERS,
        responses={
            200: sc.SUBCATEGORY_LIST_RESPONSE,
        },
    )
    def get(self, request):
        return self.proxy_request("GET", "/subcategories", params=request.query_params)

    @swagger_auto_schema(
        operation_summary="Create Subcategory",
        operation_description="""
Create a new subcategory under an existing category.

Features:
- Parent category validation
- Duplicate detection scoped to category
- Arabic name support
""",
        tags=["AI Proxy Subcategories"],
        request_body=sc.SUBCATEGORY_CREATE_REQUEST,
        responses={
            201: sc.SUBCATEGORY_CREATE_RESPONSE,
        },
    )
    def post(self, request):
        return self.proxy_request("POST", "/subcategories", data=request.data)


class SubcategoryDetailsProxyView(BaseAIProxyView):
    """
    Proxy for /subcategories/{id} endpoint
    """

    @swagger_auto_schema(
        operation_summary="Get Subcategory Details",
        operation_description="Retrieve subcategory details by ID",
        tags=["AI Proxy Subcategories"],
        responses={
            200: sc.SUBCATEGORY_DETAILS_RESPONSE,
        },
    )
    def get(self, request, id):
        return self.proxy_request("GET", f"/subcategories/{id}")
