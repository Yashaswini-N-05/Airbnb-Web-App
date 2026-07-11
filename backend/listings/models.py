from django.db import models
from core.models import SoftDeleteModel, BaseModel


PROPERTY_TYPE_CHOICES = [
    ("apartment", "Apartment"),
    ("house", "House"),
    ("villa", "Villa"),
    ("cabin", "Cabin"),
    ("condo", "Condo"),
    ("cottage", "Cottage"),
    ("studio", "Studio"),
    ("loft", "Loft"),
    ("townhouse", "Townhouse"),
    ("boat", "Boat"),
    ("treehouse", "Treehouse"),
    ("other", "Other"),
]


class Listing(SoftDeleteModel):
    """
    A property listing posted by a host.
    Replaces the old Hotel model.
    """

    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="listings",
        help_text="The host/owner of this listing",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPE_CHOICES,
        default="apartment",
    )

    # Location
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )

    # Pricing
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night in USD",
    )

    # Capacity & Details
    max_guests = models.PositiveIntegerField(default=1)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    beds = models.PositiveIntegerField(default=1)

    # Amenities stored as a JSON list e.g. ["wifi", "pool", "parking"]
    amenities = models.JSONField(default=list, blank=True)

    # Status
    is_active = models.BooleanField(default=True, help_text="Visible to guests")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        indexes = [
            models.Index(fields=["host"]),
            models.Index(fields=["city", "country"]),
            models.Index(fields=["price_per_night"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.city}, {self.country})"

    @property
    def cover_image(self):
        """Return the cover/main image URL or None."""
        img = self.images.filter(is_cover=True).first()
        if img:
            return img.url
        img = self.images.first()
        return img.url if img else None


class Image(BaseModel):
    """
    An image attached to a Listing.
    """

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images",
    )
    url = models.URLField(max_length=1000, help_text="Image URL (e.g. Cloudinary)")
    caption = models.CharField(max_length=255, blank=True)
    is_cover = models.BooleanField(default=False, help_text="Main/cover image")
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ["-is_cover", "order", "created_at"]
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return f"Image for {self.listing.title} ({'cover' if self.is_cover else f'order {self.order}'})"

    def save(self, *args, **kwargs):
        # Ensure only one cover image per listing
        if self.is_cover:
            Image.objects.filter(listing=self.listing, is_cover=True).exclude(
                pk=self.pk
            ).update(is_cover=False)
        super().save(*args, **kwargs)
