from drf_yasg import openapi

PRODUCT_LIST_PARAMETERS = [
    # Search
    openapi.Parameter(
        "q", openapi.IN_QUERY, description="Search keyword", type=openapi.TYPE_STRING
    ),
    # Filters
    openapi.Parameter(
        "brand_id",
        openapi.IN_QUERY,
        description="Filter by brand ID",
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        "category_id",
        openapi.IN_QUERY,
        description="Filter by category ID",
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        "subcategory_id",
        openapi.IN_QUERY,
        description="Filter by subcategory ID",
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        "is_best_selling",
        openapi.IN_QUERY,
        description="1 = best selling products",
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        "in_stock",
        openapi.IN_QUERY,
        description="Only show products in stock",
        type=openapi.TYPE_BOOLEAN,
    ),
    openapi.Parameter(
        "min_price",
        openapi.IN_QUERY,
        description="Minimum product price",
        type=openapi.TYPE_NUMBER,
    ),
    openapi.Parameter(
        "max_price",
        openapi.IN_QUERY,
        description="Maximum product price",
        type=openapi.TYPE_NUMBER,
    ),
    # Pagination
    openapi.Parameter(
        "page",
        openapi.IN_QUERY,
        description="Page number",
        type=openapi.TYPE_INTEGER,
        default=1,
    ),
    openapi.Parameter(
        "limit",
        openapi.IN_QUERY,
        description="Items per page",
        type=openapi.TYPE_INTEGER,
        default=10,
    ),
    # Sorting
    openapi.Parameter(
        "sort_by",
        openapi.IN_QUERY,
        description="""
Sorting options:

- created_desc
- created_asc
- price_desc
- price_asc
- item_name_asc
- item_name_desc
""",
        type=openapi.TYPE_STRING,
        default="created_desc",
    ),
]


PRODUCT_LIST_RESPONSE = openapi.Response(
    description="Successful response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "data": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "products": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "barcode": openapi.Schema(type=openapi.TYPE_STRING),
                                "item_code": openapi.Schema(type=openapi.TYPE_STRING),
                                "item_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "image_url": openapi.Schema(type=openapi.TYPE_STRING),
                                "price": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "available_qty": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "brand_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "brand_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "category_id": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "category_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "subcategory_id": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "subcategory_name": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "is_best_selling": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN
                                ),
                            },
                        ),
                    ),
                    "pagination": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "page": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "limit": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "has_next": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "has_prev": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                    "filters_applied": openapi.Schema(type=openapi.TYPE_OBJECT),
                },
            ),
        },
    ),
)


from drf_yasg import openapi

# =========================================================
# CATEGORY LIST
# =========================================================

CATEGORY_LIST_PARAMETERS = [
    openapi.Parameter(
        "search",
        openapi.IN_QUERY,
        description="Search by category name or Arabic name",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "is_active",
        openapi.IN_QUERY,
        description="Filter active/inactive categories",
        type=openapi.TYPE_BOOLEAN,
    ),
    openapi.Parameter(
        "page",
        openapi.IN_QUERY,
        description="Page number",
        type=openapi.TYPE_INTEGER,
        default=1,
    ),
    openapi.Parameter(
        "limit",
        openapi.IN_QUERY,
        description="Items per page",
        type=openapi.TYPE_INTEGER,
        default=100,
    ),
]


CATEGORY_OBJECT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "name_ar": openapi.Schema(
            type=openapi.TYPE_STRING,
            nullable=True,
        ),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING,
            format="date-time",
            nullable=True,
        ),
    },
)


CATEGORY_LIST_RESPONSE = openapi.Response(
    description="Category list retrieved successfully",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "data": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=CATEGORY_OBJECT_SCHEMA
            ),
            "pagination": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "page": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "limit": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
        },
    ),
)


# =========================================================
# CATEGORY DETAILS
# =========================================================

CATEGORY_DETAILS_RESPONSE = openapi.Response(
    description="Category details",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "data": CATEGORY_OBJECT_SCHEMA,
        },
    ),
)


# =========================================================
# CATEGORY CREATE
# =========================================================

CATEGORY_CREATE_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["name"],
    properties={
        "name": openapi.Schema(type=openapi.TYPE_STRING, description="Category name"),
        "name_ar": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Arabic category name",
            nullable=True,
        ),
        "is_active": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            default=True,
        ),
    },
)


CATEGORY_CREATE_RESPONSE = openapi.Response(
    description="Category created successfully",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "message": openapi.Schema(
                type=openapi.TYPE_STRING, example="Category created successfully"
            ),
            "data": CATEGORY_OBJECT_SCHEMA,
        },
    ),
)
