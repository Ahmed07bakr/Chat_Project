from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg


def get_avg_rating(self):
    return self.ratings_received.aggregate(Avg('stars'))['stars__avg'] or 0

User.add_to_class("average_rating", property(get_avg_rating))

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    original_text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, default='en')  # Language of translated_text
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    reactions = ArrayField(models.CharField(max_length=10), default=list, blank=True)

    


    class Meta:
        ordering = ['timestamp']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.CharField(max_length=10, default='en')


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# class UserRating(models.Model):
#     rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_ratings")
#     rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_ratings")
#     stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

class UserRating(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_given")
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_received")
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'rated_user')  # One rating per user pair



class UserFeedback(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback_given")
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback_received")
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    reported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rater", "target")


def get_feedback_stats(self):
    feedback = self.feedback_received.all()
    avg_stars = feedback.filter(reported=False).aggregate(Avg("stars"))["stars__avg"] or 0
    report_count = feedback.filter(reported=True).count()
    return {
        "average_stars": avg_stars,
        "report_count": report_count,
    }

User.add_to_class("feedback_stats", property(get_feedback_stats))

# user.feedback_stats["average_stars"]  
# user.feedback_stats["report_count"]



class ConversationRating(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
