from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from . import views
from reviews.views import ReviewViewSet

router = DefaultRouter()
router.register(r"listings", views.ListingViewSet, basename="listing")

# Nested router: /api/listings/{listing_pk}/images/
listings_router = nested_routers.NestedDefaultRouter(router, r"listings", lookup="listing")
listings_router.register(r"images", views.ImageViewSet, basename="listing-images")

# Nested router: /api/listings/{listing_pk}/reviews/
listings_router.register(r"reviews", ReviewViewSet, basename="listing-reviews")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(listings_router.urls)),
]
