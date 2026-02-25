import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Report
from .locust_engine import locust_engine


class LoadTestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.report_id = self.scope['url_route']['kwargs']['report_id']
        self.room_group_name = f'load_test_{self.report_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'load_test_update',
                'message': message
            }
        )

    # Receive message from room group
    async def load_test_update(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_stats_update(self, stats_data):
        """发送统计数据更新"""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': stats_data
        }))