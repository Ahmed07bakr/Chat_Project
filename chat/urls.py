from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet
from .views import chat_room , conversation_list

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('conversations/', conversation_list, name='conversation_list'),

]

urlpatterns += [
    path('room/<int:conversation_id>/', chat_room, name='chat_room'),
]


