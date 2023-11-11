from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Pastebin API",
        default_version='v1',
        description="Description of your API",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tools/', include('server.apps.tools.urls')),
    path('employee/', include([
        path('', include('server.apps.employee.urls')),
        path('', include('server.apps.authentication.urls')),
    ])),
    path('schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
