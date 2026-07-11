from django.contrib import admin
from .models import Booking, GuestDetail


class GuestDetailInline(admin.TabularInline):
    model = GuestDetail
    extra = 0
    fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "is_primary",
        "date_of_birth",
        "nationality",
        "passport_number",
    ]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "booking_reference",
        "user",
        "listing",
        "check_in_date",
        "check_out_date",
        "status",
        "payment_status",
        "total_amount",
        "currency",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["booking_reference", "user__email", "listing__title"]
    readonly_fields = ["booking_reference", "created_at", "updated_at", "cancelled_at"]
    inlines = [GuestDetailInline]
    raw_id_fields = ["user", "listing"]
    date_hierarchy = "check_in_date"


@admin.register(GuestDetail)
class GuestDetailAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "booking", "is_primary"]
    list_filter = ["is_primary"]
    search_fields = ["first_name", "last_name", "booking__booking_reference"]
    raw_id_fields = ["booking"]
