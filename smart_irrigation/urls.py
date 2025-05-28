from django.urls import path, include
from django.contrib import admin
from accounts.views import home
from irrigation import views as irrigation_views
from irrigation import api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('irrigation/', include('irrigation.urls')),  # Irrigation app URLs
    path('accounts/', include('accounts.urls')),
    path('about/', irrigation_views.about, name='about'),
    path('contact/', irrigation_views.contact, name='contact'),
    path('help/', irrigation_views.help, name='help'),
    path('__debug__/', include('debug_toolbar.urls')),
    path('keep-alive/', irrigation_views.keep_alive, name='keep-alive'),

    # API URLs (moved to project level)
    path('api/sensor-data/', api.receive_sensor_data, name='receive_sensor_data'),
    path('api/control/', api.control_system, name='control_system'),
    path('api/status/', api.get_system_status, name='get_system_status'),
    path('api/get_threshold/', api.get_threshold, name='get_threshold'),
    path('api/set_threshold/', api.set_threshold, name='set_threshold'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
