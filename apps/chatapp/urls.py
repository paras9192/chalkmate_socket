from django.urls import path, re_path
from . import consumers
from . import views

app_name = "chatapp"

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r"ws/chat/$", consumers.ChatConsumer.as_asgi()),
]



# HTTP URL patterns
urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
]
