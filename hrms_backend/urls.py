"""
URL configuration for hrms_backend project.
"""
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from hrms.views import api_root, health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('', api_root),
    path('api/', include('hrms.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
