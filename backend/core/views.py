from rest_framework import permissions, filters, status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Country, City
from .serializers import (
    CountrySerializer,
    CitySerializer,
)
from users.permissions import IsSuperAdmin
from utils.response import api_response
import structlog

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List Countries", description="List all countries"
    ),
)
class CountryViewSet(ModelViewSet):
    """Country viewset"""
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]
    ordering = ["name"]


@extend_schema_view(
    list=extend_schema(
        summary="Admin - List Countries", description="Admin list of all countries"
    ),
    create=extend_schema(
        summary="Admin - Create Country", description="Create a new country"
    ),
    retrieve=extend_schema(
        summary="Admin - Get Country Details",
        description="Get full details of a country",
    ),
    update=extend_schema(
        summary="Admin - Update Country", description="Update country details"
    ),
    partial_update=extend_schema(
        summary="Admin - Partially Update Country",
        description="Partially update country details",
    ),
    destroy=extend_schema(
        summary="Admin - Delete Country", description="Delete a country"
    ),
)
class AdminCountryViewSet(ModelViewSet):
    """Admin country management viewset"""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        """Return paginated list of countries in api_response format."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data)
            return api_response(success=True, data=paginated.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Return single country in api_response format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(success=True, data=serializer.data)

    def create(self, request, *args, **kwargs):
        """Create country and return in api_response format."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        country = serializer.save()
        logger.info(
            "country_created",
            country_id=str(country.pk),
            code=country.code,
            actor_id=str(request.user.pk),
        )
        return api_response(
            success=True,
            data=CountrySerializer(country).data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Update country and return in api_response format."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        country = serializer.save()
        return api_response(success=True, data=CountrySerializer(country).data)

    def destroy(self, request, *args, **kwargs):
        """Delete country and return in api_response format."""
        instance = self.get_object()
        country_id = str(instance.pk)
        instance.delete()
        logger.info(
            "country_deleted",
            country_id=country_id,
            actor_id=str(request.user.pk),
        )
        return api_response(
            success=True,
            data={},
            status_code=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List Cities", description="List all cities"
    ),
)
class CityViewSet(ModelViewSet):
    """City viewset"""
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "is_popular"]
    search_fields = ["name", "country__name"]
    ordering_fields = ["name"]
    ordering = ["name"]
