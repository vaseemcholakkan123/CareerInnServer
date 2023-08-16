import django
django.setup()

from . import consumers
from django.urls import path
from .consumers import PeerConnectionConsumer,NotificationConsumer,ChatConsumer

websocket_urlpatterns = [
    path('careerinn-api/peersocket/',PeerConnectionConsumer.as_asgi()),
    path('careerinn-api/notifications/',NotificationConsumer.as_asgi()),
    path('careerinn-api/chat/',ChatConsumer.as_asgi()),
]



