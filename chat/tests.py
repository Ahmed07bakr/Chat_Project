from django.test import TestCase
from chat.models import Conversation, Message
from django.contrib.auth.models import User

class ChatModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice')
        self.convo = Conversation.objects.create()
        self.convo.participants.add(self.user)

    def test_message_creation(self):
        msg = Message.objects.create(
            conversation=self.convo,
            sender=self.user,
            original_text="Hello",
            translated_text="Hola",
            language="es"
        )
        self.assertEqual(msg.sender.username, 'alice')
