from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Read serializer for reviews — includes nested user info."""

    user = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, coerce_to_string=False)

    class Meta:
        model = Review
        fields = [
            "id", "listing", "listing_title", "user",
            "title", "content", "rating",
            "reviewer_name", "reviewer_country", "review_date",
            "is_active", "is_verified",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "listing", "user", "is_verified", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating a review (listing set from URL, user from request)."""

    rating = serializers.DecimalField(max_digits=3, decimal_places=1, coerce_to_string=False)

    class Meta:
        model = Review
        fields = [
            "title", "content", "rating",
            "reviewer_name", "reviewer_country", "review_date",
        ]

    def create(self, validated_data):
        # listing and user are set by the view's perform_create
        return Review.objects.create(**validated_data)
