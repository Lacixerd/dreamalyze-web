from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    user_created_at = models.DateTimeField(auto_now_add=True)
    user_updated_at = models.DateTimeField(auto_now=True)
    user_plan = models.CharField(max_length=100, default='free')
    last_chat_at = models.DateTimeField(null=True, blank=True)
    next_available_chat_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def update_chat_dates(self):
        self.last_chat_at = timezone.now()
        if self.user_plan == 'free':
            self.next_available_chat_at = self.last_chat_at + timedelta(days=30)
        self.save(update_fields=['last_chat_at', 'next_available_chat_at'])

    def can_send_chat(self):
        if not self.next_available_chat_at:
            return True
        return self.next_available_chat_at <= timezone.now()

    def __str__(self):
        return f"{self.email}"
    
class Dream(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dreams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.author} - {self.is_active}"

class DreamMessage(models.Model):
    dream_id = models.ForeignKey(Dream, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dream_id} - {self.role}"

class Interpretation(models.Model):
    dream_id = models.OneToOneField(Dream, on_delete=models.CASCADE, related_name='interpretation')
    json_analyze = models.JSONField()

    def __str__(self):
        return f"Interpretation of {self.dream_id}"