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

    class Plan(models.TextChoices):
        FREE = "free", "Free"
        PLUS = "plus", "Plus"

    user_plan = models.CharField(max_length=100, default=Plan.FREE, choices=Plan.choices)
    last_chat_at = models.DateTimeField(null=True, blank=True)
    next_available_chat_at = models.DateTimeField(null=True, blank=True)
    user_created_at = models.DateTimeField(auto_now_add=True)
    user_updated_at = models.DateTimeField(auto_now=True)
    user_deleted_at = models.DateTimeField(blank=True, null=True)
    
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
    
class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="subscription")

    class SubPlan(models.TextChoices):
        FREE = "free", "Free"
        PLUS = "plus", "Plus"

    subscription_plan = models.CharField(max_length=50, choices=SubPlan.choices, default=SubPlan.PLUS)
    price = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def extend_subscription(self):
        if self.is_active:
            self.updated_at = self.updated_at + timedelta(days=30)
        self.save(update_fields=['updated_at'])

    def expiry_control(self):
        if self.updated_at > timezone.now():
            self.is_active = False
        self.save(update_fields=['is_active'])

    def save(self, *args, **kwargs):
        if not self.updated_at:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_id = models.CharField(max_length=36, default=uuid.uuid4, editable=False)
    device_name = models.CharField(max_length=100, blank=True, default="My Default Device")
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    first_registered_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def update_last_login(self):
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])

    def save(self, *args, **kwargs):
        if not self.last_login_at:
            self.last_login_at = timezone.now()
        super().save(*args, **kwargs)

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
    deleted_at = models.DateTimeField(blank=True, null=True)
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

class Analysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dream = models.OneToOneField(Dream, on_delete=models.CASCADE, related_name='interpretation')
    json_analyze = models.JSONField()

    class AnalysisStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    status = models.CharField(max_length=50, choices=AnalysisStatus.choices, default=AnalysisStatus.PENDING)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Analysis of {self.dream_id}"