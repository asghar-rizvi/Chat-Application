import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Group, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        
        # Add user to the WebSocket group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print('GroupName',self.group_name)
        # Load previous chat messages
        chat_history = await self.get_chat_history(self.group_name)
        print('Chat History...', chat_history)
        if chat_history:
            await self.send(text_data=json.dumps({
                'type': 'chat_history',
                'messages': chat_history
            }))
        else:
            print('No chat history')
    
    async def receive(self, text_data=None, bytes_data=None):
        if self.scope['user'].is_authenticated:
            data = json.loads(text_data)
            message = data['message']
            username = self.scope['user'].username
            
            print('Message Coming To Server...', message)
            print('Sender...', username)
            
            print('Adding Records into database')
            # Save message to the database
            group_obj = await self.get_group(self.group_name)
            await self.create_chat_message(username, message, group_obj)
            
            # Broadcast message to group
            print('Sending message to group')
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': username
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'message': 'Login required',
                'user': 'unknown'
            }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'chat_message',
            'message': event['message'],
            'user': event['user']
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    @database_sync_to_async
    def get_group(self, group_name):
        return Group.objects.get_or_create(group_name=group_name)[0]
    
    @database_sync_to_async
    def create_chat_message(self, username, message, group_obj):
        return ChatMessage.objects.create(message_chats=f"{username}: {message}", group=group_obj)
    
    @database_sync_to_async
    def get_chat_history(self, group_name):
        group = Group.objects.filter(group_name=group_name).first()
        if group:
            return [{
                'message': msg.message_chats
            } for msg in ChatMessage.objects.filter(group=group)]
        return []