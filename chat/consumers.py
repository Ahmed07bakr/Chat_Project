import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Conversation, Message
from googletrans import Translator
from asgiref.sync import sync_to_async



translator = Translator()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        conversation = await self.get_conversation(self.conversation_id)

        original_text = data['message']
        target_lang = user.userprofile.preferred_language

        translated = translator.translate(original_text, dest=target_lang).text

        message = await self.create_message(conversation, user, original_text, translated, target_lang)
        if data.get('type') == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'type': 'typing_status',
                    'message': translated,
                    'sender': user.username,
                    'timestamp': str(message.timestamp),
                }
            )
            return



    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender']
        }))


    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @staticmethod
    async def get_conversation(conversation_id):
        return await database_sync_to_async(Conversation.objects.get)(id=conversation_id)

    @staticmethod
    async def create_message(conversation, user, original_text, translated_text, lang):
        return await database_sync_to_async(Message.objects.create)(
            conversation=conversation,
            sender=user,
            original_text=original_text,
            translated_text=translated_text,
            language=lang,
        )

database_sync_to_async = sync_to_async
