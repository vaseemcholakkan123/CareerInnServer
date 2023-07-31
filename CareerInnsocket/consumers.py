from channels.consumer import AsyncConsumer
import json

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