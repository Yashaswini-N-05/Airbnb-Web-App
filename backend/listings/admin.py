from django.contrib import admin
from core.admin import BaseModelAdmin, SoftDeleteModelAdmin
from .models import Listing, Image


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0
    fields = ["url", "caption", "is_cover", "order"]


@admin.register(Listing)
class ListingAdmin(SoftDeleteModelAdmin):
    list_display = [
        "title", "host", "property_type", "city", "country",
        "price_per_night", "max_guests", "is_active", "deleted_status", "created_at",
    ]
    list_filter = ["property_type", "is_active", "country", "is_deleted"]
    search_fields = ["title", "description", "city", "country", "host__email"]
    ordering = ["-created_at"]
    raw_id_fields = ["host"]
    inlines = [ImageInline]

    fieldsets = (
        (None, {
            "fields": ("host", "title", "description", "property_type", "is_active"),
        }),
        ("Location", {
            "fields": ("address", "city", "state", "country", "latitude", "longitude"),
        }),
        ("Details", {
            "fields": ("price_per_night", "max_guests", "bedrooms", "bathrooms", "beds", "amenities"),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("host")


@admin.register(Image)
class ImageAdmin(BaseModelAdmin):
    list_display = ["listing", "url", "caption", "is_cover", "order", "created_at"]
    list_filter = ["is_cover"]
    search_fields = ["listing__title", "caption"]
    raw_id_fields = ["listing"]
    ordering = ["listing", "-is_cover", "order"]
