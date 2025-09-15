from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid 

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    user_created_at = models.DateTimeField(auto_now_add=True)
    user_updated_at = models.DateTimeField(auto_now=True)

    class Plan(models.TextChoices):
        FREE = "free", "Free"
        PLUS = "plus", "Plus"

    user_plan = models.CharField(max_length=100, default=Plan.FREE, choices=Plan.choices)
    last_chat_at = models.DateTimeField(null=True, blank=True)
    next_available_chat_at = models.DateTimeField(null=True, blank=True)

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
    
class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_id = models.CharField(max_length=36, default=uuid.uuid4, editable=False)
    device_name = models.CharField(max_length=100, blank=True, default="My Default Device")
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    first_registered_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'device_id'], name='unique_device_user'
            )
        ]
    
class Dream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dreams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.is_active}"

class DreamMessage(models.Model):
    dream = models.ForeignKey(Dream, on_delete=models.CASCADE, related_name='messages')

    class Role(models.TextChoices):
        USER = "user", "User"
        ANALYST = "analyst", "Analyst"
        SYSTEM = "system", "System"

    role = models.CharField(max_length=20, choices=Role.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dream_id.id} - {self.role}"

class Interpretation(models.Model):
    dream = models.OneToOneField(Dream, on_delete=models.CASCADE, related_name='interpretation')
    json_analyze = models.JSONField()

    def __str__(self):
        return f"Interpretation of {self.dream_id}"