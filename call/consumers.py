import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import CustomUser
from .models import Call,ICECandidate

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join user's personal group for call notifications
        self.user_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Join room group (existing chat functionality)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
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
        
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'call_signal':
            await self.handle_call_signal(data)
    
    async def handle_chat_message(self, data):
        """Handle regular chat messages (existing functionality)"""
        message = data['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def handle_call_signal(self, data):
        """Handle WebRTC signaling for calls"""
        call_id = data.get('call_id')
        signal_type = data.get('signal_type')
        
        if not call_id:
            return
        
        # Get call and verify user is participant
        call = await self.get_call(call_id)
        if not call or self.user.id not in [call.caller_id, call.receiver_id]:
            return
        
        # Determine the other participant
        other_user_id = call.receiver_id if call.caller_id == self.user.id else call.caller_id
        
        # Forward the signal to the other participant
        await self.channel_layer.group_send(
            f"user_{other_user_id}",
            {
                'type': 'call_signal',
                'message': {
                    'type': 'call_signal',
                    'call_id': call_id,
                    'signal_type': signal_type,
                    'data': data.get('data', {}),
                    'from_user': self.user.id
                }
            }
        )
    
    # Message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user'],
            'user_id': event['user_id']
        }))
    
    async def call_notification(self, event):
        """Send call notification to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))
    
    async def call_signal(self, event):
        """Send call signal to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))
    
    # Database operations
    @database_sync_to_async
    def get_call(self, call_id):
        try:
            return Call.objects.get(id=call_id)
        except Call.DoesNotExist:
            return None