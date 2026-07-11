from rest_framework import serializers

from .models import Booking, GuestDetail
from users.serializers import UserSerializer


class ListingMiniSerializer(serializers.Serializer):
    """Minimal listing info embedded in booking responses."""
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    cover_image = serializers.SerializerMethodField()
    city = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)
    price_per_night = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)

    def get_cover_image(self, obj):
        return obj.cover_image


class GuestDetailSerializer(serializers.ModelSerializer):
    """Guest detail serializer for read (nested in booking)."""

    class Meta:
        model = GuestDetail
        fields = [
            "id", "first_name", "last_name", "email",
            "phone", "date_of_birth", "nationality",
            "passport_number", "is_primary",
        ]
        read_only_fields = ["id"]


class GuestDetailCreateSerializer(serializers.ModelSerializer):
    """Guest detail for create/update booking."""

    class Meta:
        model = GuestDetail
        fields = [
            "first_name", "last_name", "email",
            "phone", "date_of_birth", "nationality",
            "passport_number", "is_primary",
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Booking list serializer with nested user, listing, and guest_details."""

    user = UserSerializer(read_only=True)
    listing = ListingMiniSerializer(read_only=True)
    guest_details = GuestDetailSerializer(many=True, read_only=True)
    room_rate = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    taxes = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    fees = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Booking
        fields = [
            "id", "booking_reference", "user", "listing",
            "check_in_date", "check_out_date",
            "guests_count", "adults_count", "children_count",
            "total_nights", "room_rate", "taxes", "fees",
            "total_amount", "currency",
            "status", "payment_status",
            "special_requests", "guest_details",
            "created_at", "updated_at",
            "cancelled_at", "cancellation_reason",
        ]
        read_only_fields = ["id", "booking_reference", "created_at", "updated_at"]


class BookingDetailSerializer(BookingListSerializer):
    pass


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["special_requests", "status"]
        extra_kwargs = {"special_requests": {"required": False}, "status": {"required": False}}

    def validate_status(self, value):
        request = self.context.get("request")
        if request and not (
            request.user.is_superuser
            or (hasattr(request.user, "is_host") and request.user.is_host())
        ):
            raise serializers.ValidationError("Only host or admin can change status.")
        return value


class BookingCreateSerializer(serializers.ModelSerializer):
    """Create a booking: pass listing_id + dates + guests."""

    guest_details = GuestDetailCreateSerializer(many=True, required=False, default=list)
    listing_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            "listing_id",
            "check_in_date", "check_out_date",
            "guests_count", "adults_count", "children_count",
            "special_requests", "guest_details",
        ]

    def validate(self, attrs):
        from listings.models import Listing

        listing_id = attrs.get("listing_id")
        check_in = attrs.get("check_in_date")
        check_out = attrs.get("check_out_date")
        adults = attrs.get("adults_count", 1)
        children = attrs.get("children_count", 0)
        guests_count = attrs.get("guests_count", 1)

        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    {"check_out_date": "Check-out must be after check-in."}
                )
            if (check_out - check_in).days < 1:
                raise serializers.ValidationError(
                    {"check_out_date": "Stay must be at least one night."}
                )

        if guests_count != adults + children:
            raise serializers.ValidationError(
                {"guests_count": "Must equal adults_count + children_count."}
            )

        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise serializers.ValidationError({"listing_id": "Invalid or inactive listing."})

        # Booking validation overlap check (Step 11)
        overlapping = Booking.objects.filter(
            listing=listing,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        ).exclude(status=Booking.STATUS_CANCELLED).exists()
        if overlapping:
            raise serializers.ValidationError("Booking validation failed: overlapping dates exist.")

        if listing.max_guests < guests_count:
            raise serializers.ValidationError(
                {"guests_count": f"Listing allows maximum {listing.max_guests} guests."}
            )

        total_nights = (check_out - check_in).days
        price = listing.price_per_night
        total = price * total_nights

        attrs["listing"] = listing
        attrs["total_nights"] = total_nights
        attrs["room_rate"] = price
        attrs["total_amount"] = total
        attrs["taxes"] = 0
        attrs["fees"] = 0
        attrs["currency"] = "USD"
        return attrs

    def create(self, validated_data):
        guest_details_data = validated_data.pop("guest_details", [])
        validated_data.pop("listing_id", None)
        validated_data["user"] = self.context["request"].user
        booking = Booking.objects.create(**validated_data)
        for i, gd in enumerate(guest_details_data):
            gd = dict(gd)
            is_primary = gd.pop("is_primary", i == 0)
            GuestDetail.objects.create(booking=booking, is_primary=is_primary, **gd)
        return booking
