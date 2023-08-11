from channels.consumer import AsyncConsumer
import json
from User.models import User
from datetime import datetime
from .models import *
from User.serailizers import ChatMessageSerializer


class PeerConnectionConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        target = self.scope['target']
        user = self.scope['user']

        self.chatroom = f'interview_chatroom_{target.id}'

        await self.channel_layer.group_add(
            self.chatroom,
            self.channel_name
        )
        
        await self.send({"type": "websocket.accept"})

    async def websocket_disconnect(self, evnet):
        
        await self.channel_layer.group_send(
            self.chatroom,
            {
                'type':'chat_message',
                'text':json.dumps({'response':'user_left'})
            }
        )

    async def websocket_receive(self,event):
        json_dmp = json.loads(event['text'])
        data =  json_dmp['message']
        respo = {
            'response':data,
        }

        respo['user'] = self.scope['user'].id

        await self.channel_layer.group_send(
            self.chatroom,
            {
                'type':'chat_message',
                'text':json.dumps(respo)
            }
        )
        

    async def chat_message(self,event):
        await self.send({'type':'websocket.send','text':event['text']})



class NotificationConsumer(AsyncConsumer):

    async def websocket_connect(self,event):
        user = self.scope['user']
        self.chatroom = f'user_notification_{user.id}'

        await self.channel_layer.group_add(
            self.chatroom,
            self.channel_name
        )
        
        await self.send({"type": "websocket.accept"})

    async def notification_message(self,event):
        await self.send({'type':'websocket.send','text':'new_notification'})

    async def websocket_disconnect(self, event):
        await self.send({"type": "websocket.accept"})


    

class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self,event):

        second_user = self.scope['target']
        first_user = self.scope['user']
        thread = await self.get_thread(first_user,second_user)

        self.chatroom = f'chatroom_{thread.id}'
        self.thread = thread

        await self.channel_layer.group_add(
            self.chatroom,
            self.channel_name
        )
        
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self,event):
        dmp = json.loads(event['text'])
        message = dmp.get('message')

        if not message or not self.scope['user'] or not self.scope['target'] or not self.thread:
            await self.send({"type": "websocket.send","text" : 'Internal error'})

        msg = await self.save_message(self.thread,self.scope['user'],message)
        data = ChatMessageSerializer(msg,many=False).data

        response = {
            'message':json.dumps(data),
        }

        await self.channel_layer.group_send(
            self.chatroom,
            {
                'type':'chat_message',
                'text':json.dumps(response)
            }
        )

    async def chat_message(self,event):
        await self.send({'type':'websocket.send','text':event['text']})


    async def websocket_disconnect(self, event):
        await self.check_messages_count(self.thread)
        await self.send({"type": "websocket.accept"})



    @database_sync_to_async
    def get_user(self,user_id):
        usr = User.objects.filter(id=user_id)
        if usr.exists():
            return usr.first()
        else:
            return None
        
    @database_sync_to_async
    def check_messages_count(self,thread): 
        # thread.delete()
        if thread.chatmessage_thread.all().count() == 0:
            thread.delete()
            

        
    @database_sync_to_async
    def get_thread(self,first_person,second_person):
        thread = ChatThread.objects.filter(
            Q(primary_user=first_person, secondary_user=second_person) | 
            Q(primary_user=second_person, secondary_user=first_person)
            
        )
        if thread.exists():
            thread = thread.first()

        else:
            thread = ChatThread.objects.create(primary_user=first_person,secondary_user=second_person)

        return thread
    

    
    @database_sync_to_async
    def save_message(self,thread,user,message):
        return Chatmessage.objects.create(thread=thread,user=user,message=message)
