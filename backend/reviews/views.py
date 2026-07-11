from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from utils.response import api_response
import structlog

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List Reviews for a Listing"),
    create=extend_schema(summary="Create a Review"),
    retrieve=extend_schema(summary="Get Review Detail"),
    destroy=extend_schema(summary="Delete a Review"),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """Read and write reviews for a listing."""

    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_pk")
        qs = Review.objects.filter(is_active=True)
        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        listing_id = self.kwargs.get("listing_pk")
        from listings.models import Listing
        listing = Listing.objects.get(pk=listing_id)
        user = self.request.user if self.request.user.is_authenticated else None
        reviewer_name = getattr(user, "full_name", None) or getattr(user, "email", "Anonymous")
        review = serializer.save(listing=listing, user=user, reviewer_name=reviewer_name)
        logger.info("review_created", review_id=str(review.pk), listing_id=str(listing_id))
