"""
ASGI config for CareerInn project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from .middlewares import JwtAuthForAsgiStack
from channels.auth import AuthMiddlewareStack
from CareerInnsocket.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareerInn.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket":  AuthMiddlewareStack( 
                            JwtAuthForAsgiStack( URLRouter(websocket_urlpatterns))
                                        )
    
    }
)

application = ASGIStaticFilesHandler(application)