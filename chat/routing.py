from django.urls import path
from .consumer import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:group_name>/', ChatConsumer.as_asgi()),
]
