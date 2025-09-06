import json
from channels.generic.websocket import AsyncWebsocketConsumer 
from .models import Group ,Messages ,Message_type

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.room_group_name = f"chat_{self.group_id}"
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        user =self.scope['user']
        print(user,'\n\n\n\n')
        if not user.is_authenticated:
            await self.send(json.dumps({
                "error"  : "Authenticate user"
            }))
            return
        
        text_data_json = json.loads(text_data)
        text = text_data_json.get('text')
        message_type_str = text_data_json.get('type','text')

        if not text:
            await self.send(json.dumps({
                "error" : "No text found"
            }))
            return
        try:
            groupChat_instance =  await Group.objects.aget(id = self.group_id)
        except Group.DoesNotExist:
            await self.send(json.dumps({
                "error":"Group Does Not exists"
            }))

        try:
            message_type = await Message_type.objects.aget(type = message_type_str)
        except Message_type.DoesNotExist:
            await self.send(json.dumps({
                "error": f"Message type {message_type} Does Not exists"
            })) 


        message = await Messages.objects.acreate(group = groupChat_instance , user = user , content = text , type = message_type)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "GroupChat_message", "text": message.content ,"sender":user.email , "timestamp":str(message.sent_at),"message_type": message_type.type,}
        )

    # Receive message from room group
    async def GroupChat_message(self, event):       
        await self.send(json.dumps({
            'text': event['text'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_type': event['message_type'],
        }))
