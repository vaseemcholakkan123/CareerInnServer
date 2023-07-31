import django
django.setup()
from . import consumers
from django.urls import path
from .consumers import PeerConnectionConsumer

websocket_urlpatterns = [
    path('peersocket/',PeerConnectionConsumer.as_asgi()),
]



