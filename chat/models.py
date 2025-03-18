from django.db import models
from django.contrib.auth.models import User

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"


class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends_1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends_2")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"

class Group(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_user2")
    group_name = models.CharField(max_length=255, unique=True)

    @staticmethod
    def get_or_create_group(user1, user2):
        # Ensure consistent ordering (user1 should always be alphabetically smaller)
        if user1.username > user2.username:
            user1, user2 = user2, user1

        group_name = f"{user1.username}_{user2.username}"
        group, created = Group.objects.get_or_create(user1=user1, user2=user2, group_name=group_name)
        return group


class ChatMessage(models.Model):
    message_chats = models.TextField() 
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    
