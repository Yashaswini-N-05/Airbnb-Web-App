from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Booking, GuestDetail
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
)
from users.permissions import IsGuestOrHost, IsSuperAdmin
from .permissions import IsBookingGuestOrHotelOwnerOrSuperAdmin
from utils.response import api_response
import structlog

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List Bookings",
        description="List bookings for the current user (guest: own bookings; host: bookings at own hotels; admin: all).",
    ),
    create=extend_schema(
        summary="Create Booking",
        description="Create a new booking (guest or host).",
    ),
    retrieve=extend_schema(
        summary="Get Booking Details",
        description="Get detailed information about a booking.",
    ),
    partial_update=extend_schema(
        summary="Partially Update Booking",
        description="Update booking (e.g. cancel). Owner, hotel host, or admin only.",
    ),
    destroy=extend_schema(
        summary="Delete Booking",
        description="Delete a booking (admin only). Prefer cancelling instead.",
    ),
)
class BookingViewSet(ModelViewSet):
    """Booking viewset: list, create, retrieve, partial_update, destroy (admin)."""

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "payment_status", "listing", "user"]
    ordering_fields = ["created_at", "check_in_date", "check_out_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Booking.objects.select_related("user", "listing").prefetch_related(
            "guest_details"
        ).exclude(status=Booking.STATUS_CANCELLED)
        if not self.request.user.is_authenticated:
            return qs.none()
            
        if self.request.user.is_superuser:
            return qs

        # Check filter parameters
        listing_id = self.request.query_params.get("listing") or self.request.query_params.get("listingId")
        author_id = self.request.query_params.get("authorId") or self.request.query_params.get("host")
        user_id = self.request.query_params.get("user") or self.request.query_params.get("userId")

        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        if author_id:
            qs = qs.filter(listing__host_id=author_id)
        if user_id:
            qs = qs.filter(user_id=user_id)

        # If no specific filter was passed, default to showing user's own bookings as a guest, 
        # OR bookings on their listings as a host
        if not (listing_id or author_id or user_id):
            from django.db.models import Q
            qs = qs.filter(Q(user=self.request.user) | Q(listing__host=self.request.user))
            
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        if self.action in ["update", "partial_update"]:
            return BookingUpdateSerializer
        if self.action == "list":
            return BookingListSerializer
        return BookingDetailSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsSuperAdmin()]
        if self.action == "create":
            return [IsGuestOrHost()]
        if self.action in ["retrieve", "partial_update", "update", "cancel", "complete_payment"]:
            return [
                permissions.IsAuthenticated(),
                IsBookingGuestOrHotelOwnerOrSuperAdmin(),
            ]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()
        booking = serializer.instance
        logger.info(
            "booking_created",
            booking_id=str(booking.pk),
            user_id=str(booking.user_id),
            listing_id=str(booking.listing_id),
        )

    def perform_destroy(self, instance):
        booking_id = str(instance.pk)
        super().perform_destroy(instance)
        logger.info(
            "booking_deleted",
            booking_id=booking_id,
            actor_id=str(self.request.user.pk),
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(
        summary="Cancel Booking",
        description="Cancel a booking. Owner, hotel host, or admin only.",
        request=dict,
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel a booking. Owner, hotel host, or admin only."""
        booking = self.get_object()
        if booking.status == Booking.STATUS_CANCELLED:
            return api_response(
                success=False,
                errors={"detail": "Booking is already cancelled."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        reason = request.data.get("cancellation_reason", "")
        booking.status = Booking.STATUS_CANCELLED
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason
        booking.save()
        logger.info(
            "booking_cancelled",
            booking_id=str(booking.pk),
            actor_id=str(request.user.pk),
        )
        serializer = BookingDetailSerializer(booking, context={"request": request})
        return api_response(success=True, data=serializer.data)

    @extend_schema(
        summary="Complete Payment",
        description="Mark a booking as paid. For demo/simplified flow; in production this would integrate with a payment provider.",
        request=dict,
    )
    @action(detail=True, methods=["post"], url_path="complete-payment")
    def complete_payment(self, request, pk=None):
        """Mark booking payment as paid. Guest, hotel host, or admin only."""
        booking = self.get_object()
        if booking.status == Booking.STATUS_CANCELLED:
            return api_response(
                success=False,
                errors={"detail": "Cannot pay a cancelled booking."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if booking.payment_status == Booking.PAYMENT_PAID:
            return api_response(
                success=False,
                errors={"detail": "Payment is already complete."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        booking.payment_status = Booking.PAYMENT_PAID
        booking.save()
        logger.info(
            "booking_payment_completed",
            booking_id=str(booking.pk),
            actor_id=str(request.user.pk),
        )
        serializer = BookingDetailSerializer(booking, context={"request": request})
        return api_response(success=True, data=serializer.data)
