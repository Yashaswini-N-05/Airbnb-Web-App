from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
import structlog

from .models import Listing, Image
from .serializers import (
    ListingListSerializer,
    ListingDetailSerializer,
    ListingCreateUpdateSerializer,
    ImageSerializer,
    ImageCreateSerializer,
)
from users.permissions import IsGuestOrHost, IsSuperAdmin
from utils.response import api_response

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List Listings", description="Browse all active listings."),
    create=extend_schema(summary="Create Listing", description="Create a new listing (hosts only)."),
    retrieve=extend_schema(summary="Get Listing", description="Get full details of a listing."),
    update=extend_schema(summary="Update Listing", description="Update a listing (host or admin only)."),
    partial_update=extend_schema(summary="Partial Update Listing"),
    destroy=extend_schema(summary="Delete Listing", description="Soft-delete a listing."),
)
class ListingViewSet(viewsets.ModelViewSet):
    """CRUD viewset for Listings."""

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["city", "country", "property_type", "is_active", "host"]
    search_fields = ["title", "description", "city", "country", "address"]
    ordering_fields = ["price_per_night", "created_at", "max_guests"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return Listing.objects.all().prefetch_related("images")
        if user.is_authenticated and hasattr(user, "is_host") and user.is_host():
            # Hosts can see their own + active listings
            from django.db.models import Q
            return Listing.objects.filter(
                Q(host=user) | Q(is_active=True)
            ).prefetch_related("images")
        # Public: only active
        return Listing.objects.filter(is_active=True).prefetch_related("images")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ListingCreateUpdateSerializer
        if self.action == "list":
            return ListingListSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsGuestOrHost()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only host owner or superuser can modify
        if request.method not in permissions.SAFE_METHODS:
            if not request.user.is_superuser and obj.host != request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not own this listing.")

    def perform_create(self, serializer):
        listing = serializer.save()
        logger.info("listing_created", listing_id=str(listing.pk), host_id=str(listing.host_id))

    def perform_destroy(self, instance):
        listing_id = str(instance.pk)
        instance.delete()  # soft delete
        logger.info("listing_deleted", listing_id=listing_id, actor_id=str(self.request.user.pk))

    @extend_schema(summary="My Listings", description="Get listings owned by the current user.")
    @action(detail=False, methods=["get"], url_path="my-listings", permission_classes=[permissions.IsAuthenticated])
    def my_listings(self, request):
        qs = Listing.objects.filter(host=request.user).prefetch_related("images")
        serializer = ListingListSerializer(qs, many=True, context={"request": request})
        return api_response(success=True, data=serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List Images for a Listing"),
    create=extend_schema(summary="Add Image to Listing"),
    destroy=extend_schema(summary="Delete Image"),
)
class ImageViewSet(viewsets.ModelViewSet):
    """Manage images for a listing."""

    serializer_class = ImageSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_pk")
        return Image.objects.filter(listing_id=listing_id)

    def get_serializer_class(self):
        if self.action == "create":
            return ImageCreateSerializer
        return ImageSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        listing_id = self.kwargs.get("listing_pk")
        listing = Listing.objects.get(pk=listing_id)
        if not self.request.user.is_superuser and listing.host != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this listing.")
        serializer.save(listing=listing)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in permissions.SAFE_METHODS:
            if not request.user.is_superuser and obj.listing.host != request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not own this listing.")
