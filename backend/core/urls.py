from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Public router for ViewSets
router = DefaultRouter()
router.register(r"countries", views.CountryViewSet, basename="country")
router.register(r"cities", views.CityViewSet, basename="city")

# Admin router
admin_router = DefaultRouter()
admin_router.register(
    r"admin/countries", views.AdminCountryViewSet, basename="admin-country"
)

app_name = "core"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(admin_router.urls)),
]