from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy", "message": "Trip Nest API is running"})

urlpatterns = [
    path("", health_check),
    path("healthz", health_check),
    path("admin/", admin.site.urls),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/', include('listings.urls')),
    path('api/', include('core.urls')),
    path('api/', include('bookings.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
