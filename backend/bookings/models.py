from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from core.models import BaseModel


class Booking(BaseModel):
    """
    Booking model: links a guest (user) to a Listing for a date range.
    Stores pricing, status, and payment status. No soft delete so history is kept.
    """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_CANCELLED = "cancelled"
    STATUS_NO_SHOW = "no_show"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CHECKED_IN, "Checked In"),
        (STATUS_CHECKED_OUT, "Checked Out"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NO_SHOW, "No Show"),
    ]

    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_PARTIALLY_PAID = "partially_paid"
    PAYMENT_REFUNDED = "refunded"
    PAYMENT_FAILED = "failed"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_PARTIALLY_PAID, "Partially Paid"),
        (PAYMENT_REFUNDED, "Refunded"),
        (PAYMENT_FAILED, "Failed"),
    ]

    booking_reference = models.CharField(max_length=20, unique=True, db_index=True)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Guest who made the booking",
    )
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The listing being booked",
    )

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of guests",
    )
    adults_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of adults",
    )
    children_count = models.PositiveIntegerField(default=0, help_text="Number of children")

    total_nights = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of nights",
    )
    room_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Price per night",
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
        db_index=True,
    )

    special_requests = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["listing", "check_in_date", "check_out_date"]),
        ]

    def __str__(self):
        return f"{self.booking_reference} @ {self.listing.title}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self._generate_booking_reference()
        if self.check_in_date and self.check_out_date and not self.total_nights:
            self.total_nights = (self.check_out_date - self.check_in_date).days
        super().save(*args, **kwargs)

    def _generate_booking_reference(self):
        """Generate a unique booking reference (e.g. TN-XXXXXX)."""
        import random
        import string

        prefix = "TN-"
        chars = string.ascii_uppercase + string.digits
        while True:
            ref = prefix + "".join(random.choices(chars, k=8))
            if not Booking.objects.filter(booking_reference=ref).exists():
                return ref


class GuestDetail(BaseModel):
    """
    Guest detail for a booking: name and optional contact/identity info.
    One booking can have multiple guests; one can be marked as primary.
    """

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="guest_details",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "last_name", "first_name"]
        verbose_name = "Guest Detail"
        verbose_name_plural = "Guest Details"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Booking {self.booking.booking_reference})"
