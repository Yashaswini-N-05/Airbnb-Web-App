import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import SoftDeleteModel


class User(AbstractUser, SoftDeleteModel):
    """Custom user model with UUID primary key and roles"""

    # User Role Choices
    GUEST = "guest"
    HOST = "host"

    ROLE_CHOICES = [
        (GUEST, "Guest (Traveler/Booker)"),
        (HOST, "Host (Property Owner/Manager)"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.URLField(max_length=500, blank=True, null=True)

    # Role and Status
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=GUEST)
    is_verified_host = models.BooleanField(
        default=False, help_text="Host verification status"
    )
    host_approval_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        blank=True,
        null=True,
        help_text="Host application approval status",
    )

    # Preferences
    preferred_currency = models.CharField(max_length=10, default="USD")
    preferred_language = models.CharField(max_length=10, default="en")

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)

    # Host-specific fields
    business_name = models.CharField(max_length=200, blank=True, null=True)
    business_license = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) - {self.get_role_display()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def is_guest(self):
        """Check if user is a guest"""
        return self.role == self.GUEST

    def is_host(self):
        """Check if user is a host"""
        return self.role == self.HOST

    def is_admin_user(self):
        """Check if user is an admin"""
        return self.is_staff or self.is_superuser

    def can_list_properties(self):
        """Check if user can list properties"""
        return self.is_host() and self.host_approval_status == "approved"

    def can_book_properties(self):
        """Check if user can book properties"""
        return self.is_guest() or self.is_host()  # Hosts can also book

    def switch_to_host(self):
        """Switch user role from guest to host (pending approval)"""
        if self.role == self.GUEST:
            self.role = self.HOST
            self.host_approval_status = "pending"
            self.save()
            return True
        return False


class UserProfile(SoftDeleteModel):
    """Extended user profile information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Travel preferences (for guests)
    travel_preferences = models.JSONField(default=dict, blank=True)
    loyalty_programs = models.JSONField(default=dict, blank=True)

    # Host preferences (for hosts)
    hosting_experience = models.TextField(blank=True, null=True)
    property_types = models.JSONField(
        default=list, blank=True, help_text="Types of properties host manages"
    )
    instant_booking = models.BooleanField(
        default=False, help_text="Allow instant booking without approval"
    )

    # Privacy settings
    profile_public = models.BooleanField(default=True)
    show_reviews = models.BooleanField(default=True)
    show_contact_info = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"


class HostVerification(SoftDeleteModel):
    """Host verification documents and information"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="host_verification"
    )

    # Identity verification
    identity_document = models.URLField(
        blank=True, null=True, help_text="Government ID document"
    )
    address_proof = models.URLField(
        blank=True, null=True, help_text="Address verification document"
    )

    # Business verification
    business_registration = models.URLField(blank=True, null=True)
    insurance_certificate = models.URLField(blank=True, null=True)

    # Verification status
    identity_verified = models.BooleanField(default=False)
    address_verified = models.BooleanField(default=False)
    business_verified = models.BooleanField(default=False)

    # Admin notes
    verification_notes = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_hosts",
    )
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Host Verification"
        verbose_name_plural = "Host Verifications"

    def __str__(self):
        return f"Verification for {self.user.get_full_name()}"

    def is_fully_verified(self):
        """Check if host is fully verified"""
        return self.identity_verified and self.address_verified

    def verification_completion_percentage(self):
        """Calculate verification completion percentage"""
        total_checks = 3  # identity, address, business (optional)
        completed = sum(
            [self.identity_verified, self.address_verified, self.business_verified]
        )
        return (completed / total_checks) * 100


class UserActivity(SoftDeleteModel):
    """Track user activity and engagement"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.activity_type}"


class Favorite(SoftDeleteModel):
    """User's favorited listings."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="favorited_by"
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        ordering = ["-created_at"]
        unique_together = ("user", "listing")

    def __str__(self):
        return f"{self.user.get_full_name()} ♥ {self.listing.title}"
