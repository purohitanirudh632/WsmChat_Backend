import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer ,WebsocketConsumer
from .models import Chat ,Messages ,Message_type

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"
        # print(self.chat_id, self.room_group_name, '\n\n\n')

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
                "error"  : "Authenticate ussser user"
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
         chat_instance =  await Chat.objects.aget(id = self.chat_id)
        except Chat.DoesNotExist:
            await self.send(json.dumps({
                "error":"Chat not found"
            })) 
            return
        try:
            message_type = await Message_type.objects.aget( type = message_type_str)
        except Message_type.DoesNotExist:
            await self.send(json.dumps({
                "error":f"Message type '{message_type_str}'Does Not exists"
            }))
            return

        message = await Messages.objects.acreate(chat = chat_instance,user = user,content = text,type = message_type)    

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": message.content,
                "sender": user.email,
                "timestamp": str(message.sent_at),
                
            }
        )

    # Receive message from room group
    async def chat_message(self, event):       
        await self.send(text_data=json.dumps({
            "text": event["text"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            
        }))









# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.chat_id = self.scope['url_route']['kwargs']['chat_id']
#         self.room_group_name = f'chat_{self.chat_id}'
#         await self.channel_layer.group_add(self.room_group_name,self.channel_name)

#         self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )    

#     #recive message from the group

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         sender = self.scope['user'].email
#         # sender = content.get('sender', 'Anonymous')

#         await self.channel_name.group_send(
#             self.room_group_name,{
#                 'type':'chat_message',
#                 'message':message,
#                 'sender':sender   
#             }
#         )
#     async def chat_message(self,event):
#         message = event['message']
#         sender = event['sender']

#         await self.send(text_data=json.dumps({
#             'message':message,
#             'sender':sender
#         }))        