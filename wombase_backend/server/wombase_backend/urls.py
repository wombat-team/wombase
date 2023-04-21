from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', include('server.apps.inventory.urls')),
    path('employee/', include('server.apps.employee.urls'))
]
