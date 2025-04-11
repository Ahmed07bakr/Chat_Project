from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from googletrans import Translator
from django.shortcuts import get_object_or_404, redirect
from .models import UserRating, UserFeedback
from django.contrib.admin.views.decorators import staff_member_required

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
        user = self.scope["user"]
        target_lang = user.userprofile.preferred_language

        translated = translator.translate(original_text, dest=target_lang).text

        serializer.save(
            sender=self.request.user,
            translated_text=translated,
            language=target_lang
        )

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user) | Message.objects.filter(conversation__participants=self.request.user)


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, "chat/conversations.html", {"conversations": conversations})


from django.shortcuts import get_object_or_404, redirect
from .models import UserRating

@login_required
def rate_user(request, user_id):
    if request.method == "POST":
        rated_user = get_object_or_404(User, id=user_id)
        stars = int(request.POST.get("stars"))
        UserRating.objects.update_or_create(
            rater=request.user,
            rated_user=rated_user,
            defaults={"stars": stars}
        )
    return redirect("conversation_list")



@login_required
def submit_feedback(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        report = request.POST.get("report") == "on"
        stars = int(request.POST.get("stars")) if not report else None

        UserFeedback.objects.update_or_create(
            rater=request.user,
            target=target,
            defaults={
                "stars": stars,
                "reported": report
            }
        )

    return redirect("conversation_list")  # or wherever you want to go next


def feedback_form(request, user_id):
    target = get_object_or_404(User, id=user_id)
    existing = UserFeedback.objects.filter(rater=request.user, target=target).first()

    return render(request, "feedback_form.html", {
        "target": target,
        "existing": existing
    })



@staff_member_required
def moderation_dashboard(request):
    users = User.objects.all()
    data = []
    for user in users:
        stats = user.feedback_stats
        if stats["report_count"] > 0 or stats["average_stars"] > 0:
            data.append({
                "user": user,
                "reports": stats["report_count"],
                "avg": stats["average_stars"],
            })

    return render(request, "moderation.html", {"users": data})


# user.feedback_stats["average_stars"]  
# user.feedback_stats["report_count"]





