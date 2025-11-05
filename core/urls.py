"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="E-MEDATT API",
        default_version='v1',
        description="""
E-MEDATT API documentation for authentication and user management.

## Authentication
- Session-based authentication using CSRF tokens
- Email verification required for new accounts
- Password reset functionality available
- Multi-factor authentication for admin users

## Features
- User registration (Patient/Doctor)
- Email verification
- Profile management
- Password reset/change
- Account deletion
- Session management
- Admin user creation (superuser only)
""",
        terms_of_service="https://www.e-medatt.com/terms/",
        contact=openapi.Contact(email="support@e-medatt.com"),
        license=openapi.License(name="Private License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
    
    # Root redirect to Swagger UI
    path('', schema_view.with_ui('swagger', cache_timeout=0),
        name='api-docs'),
]
