
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
# from .views import IndexView

schema_view = get_schema_view(
    openapi.Info(
        title="Emedatt API",
        default_version='v1',
        description="API documentation for Emedatt Backend",
        terms_of_service="https://www.emedatt.com/terms/",
        contact=openapi.Contact(email="anyimossi.dev@gmail.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path('', IndexView.as_view(), name='index'),
    path("admin/", admin.site.urls),
    path('api/v1/', include('apps.accounts.urls')),
    
    
    # Swagger documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
