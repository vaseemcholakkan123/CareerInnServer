import django
django.setup()
from . import consumers
from django.urls import path
from .consumers import PeerConnectionConsumer,NotificationConsumer

websocket_urlpatterns = [
    path('peersocket/',PeerConnectionConsumer.as_asgi()),
    path('notifications/',NotificationConsumer.as_asgi()),
]



