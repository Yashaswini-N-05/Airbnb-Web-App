import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import SoftDeleteModel


class Review(SoftDeleteModel):
    """Review for a Listing."""

    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )

    # Review content
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rating (0-10)",
    )

    # Review metadata
    reviewer_name = models.CharField(max_length=100, blank=True)
    reviewer_country = models.CharField(max_length=100, blank=True)
    review_date = models.DateField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.listing.title} - {self.rating}/10 by {self.reviewer_name or 'Anonymous'}"
