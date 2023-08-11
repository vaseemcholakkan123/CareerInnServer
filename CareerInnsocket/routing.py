import django
django.setup()
from . import consumers
from django.urls import path
from .consumers import PeerConnectionConsumer,NotificationConsumer,ChatConsumer

websocket_urlpatterns = [
    path('peersocket/',PeerConnectionConsumer.as_asgi()),
    path('notifications/',NotificationConsumer.as_asgi()),
    path('chat/',ChatConsumer.as_asgi()),
]



