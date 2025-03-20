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

    class Meta:
        unique_together = ('user1', 'user2')


class ChatMessage(models.Model):
    group_name = models.CharField(max_length=255) 
    message_data = models.JSONField()  # Storing {'user': username, 'message': message}
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_data['user']}: {self.message_data['message']}"
    
    
