# wildfiresapi/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wildfires/', include('wildfiresapi.urls')),
]
