from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from googletrans import Translator

translator = Translator()

@login_required
def chat_room(request, conversation_id):
    return render(request, "chat/room.html", {"conversation_id": conversation_id})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        original_text = self.request.data.get("original_text")
        target_lang = self.request.data.get("language", "en")
        translated = translator.translate(original_text, dest=target_lang).text

        serializer.save(
            sender=self.request.user,
            translated_text=translated,
            language=target_lang
        )

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user) | Message.objects.filter(conversation__participants=self.request.user)







