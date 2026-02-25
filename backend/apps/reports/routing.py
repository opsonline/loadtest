from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/load-test/<str:report_id>/', consumers.LoadTestConsumer.as_asgi()),
]