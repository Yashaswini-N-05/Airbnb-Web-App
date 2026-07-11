"""Custom pagination for API (allows client to request larger page size for admin)."""
from rest_framework.pagination import PageNumberPagination


class OptionalPageSizePagination(PageNumberPagination):
    """PageNumberPagination with optional page_size query param (max 2000)."""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 2000
