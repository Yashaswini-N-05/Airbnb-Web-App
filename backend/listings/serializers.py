from rest_framework import serializers
from .models import Listing, Image
from users.serializers import UserSerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "url", "caption", "is_cover", "order", "created_at"]
        read_only_fields = ["id", "created_at"]


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["url", "caption", "is_cover", "order"]


class ListingListSerializer(serializers.ModelSerializer):
    """Compact listing representation for list views."""

    host = UserSerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "host",
            "title",
            "property_type",
            "city",
            "state",
            "country",
            "price_per_night",
            "max_guests",
            "bedrooms",
            "bathrooms",
            "beds",
            "amenities",
            "cover_image",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_cover_image(self, obj):
        return obj.cover_image


class ListingDetailSerializer(serializers.ModelSerializer):
    """Full listing representation with all images, reviews, and unavailable dates."""

    host = UserSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    unavailable_dates = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "host",
            "title",
            "description",
            "property_type",
            "address",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "price_per_night",
            "max_guests",
            "bedrooms",
            "bathrooms",
            "beds",
            "amenities",
            "images",
            "reviews",
            "unavailable_dates",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "host", "created_at", "updated_at"]

    def get_reviews(self, obj):
        from reviews.serializers import ReviewSerializer
        return ReviewSerializer(obj.reviews.filter(is_active=True), many=True).data

    def get_unavailable_dates(self, obj):
        from bookings.models import Booking
        from datetime import timedelta
        # Fetch non-cancelled bookings
        bookings = Booking.objects.filter(
            listing=obj
        ).exclude(status=Booking.STATUS_CANCELLED)
        
        dates = []
        for booking in bookings:
            current = booking.check_in_date
            while current <= booking.check_out_date:
                dates.append(current.isoformat())
                current += timedelta(days=1)
        return dates


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a listing."""

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "property_type",
            "address",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "price_per_night",
            "max_guests",
            "bedrooms",
            "bathrooms",
            "beds",
            "amenities",
            "is_active",
        ]

    def create(self, validated_data):
        validated_data["host"] = self.context["request"].user
        return super().create(validated_data)
