from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tools/', include('server.apps.tools.urls')),
    path('employee/', include('server.apps.employee.urls')),
    path('', include('server.apps.authentication.urls')),
]
