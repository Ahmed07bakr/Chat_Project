from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet
from .views import chat_room , conversation_list, rate_user , submit_feedback , moderation_dashboard

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('conversations/', conversation_list, name='conversation_list'),
    path("rate-user/<int:user_id>/", rate_user, name="rate_user"),
    path("feedback/<int:user_id>/", submit_feedback, name="submit_feedback"),
    path("moderation/", moderation_dashboard, name="moderation_dashboard"),




]

urlpatterns += [
    path('room/<int:conversation_id>/', chat_room, name='chat_room'),
]


