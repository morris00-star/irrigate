import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import irrigation.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            irrigation.routing.websocket_urlpatterns
        )
    ),
})

