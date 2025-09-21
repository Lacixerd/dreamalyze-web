from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta, date
import calendar
import uuid 

# Create your models here.
class ProductPlan(models.Model):
    plan = models.CharField(max_length=100)
    plan_description = models.TextField()
    lemon_id = models.CharField(max_length=255)
    price = models.FloatField()
    max_credit_amount = models.IntegerField(default=0)
    plan_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan}"
    
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductPlan, on_delete=models.SET_NULL, null=True)
    lemon_checkout_id = models.CharField(max_length=255, blank=True, null=True)

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    image = models.URLField(null=True, blank=True)
    google_id = models.CharField(max_length=255, null=True, blank=True)
    user_plan = models.OneToOneField(ProductPlan, on_delete=models.CASCADE, related_name="user", null=True, blank=True)
    last_chat_at = models.DateTimeField(null=True, blank=True)
    user_created_at = models.DateTimeField(auto_now_add=True)
    user_updated_at = models.DateTimeField(auto_now=True)
    user_deleted_at = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email}"
    
class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="subscription")
    subscription_plan = models.OneToOneField(ProductPlan, on_delete=models.CASCADE, related_name="subscription")
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

def get_today_day():
    return date.today().day

class UserCredits(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="credits")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="credits", blank=True, null=True)
    total_amount = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    minimum_balance = models.IntegerField(default=0)
    last_renewed = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.user and self.user.user_plan:
            self.total_amount = self.user.user_plan.max_credit_amount
            self.amount = self.user.user_plan.max_credit_amount
        super().save(*args, **kwargs)

    def should_renew_today(self):
        today = date.today()
        signup_day = self.created_at.day

        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        renewal_day = min(signup_day, last_day_of_month)

        return today.day == renewal_day and (self.last_renewed is None or self.last_renewed.month != today.month)

    def renew(self):
        user_obj = self.user
        self.total_amount = user_obj.user_plan.max_credit_amount
        self.amount = user_obj.user_plan.max_credit_amount
        self.last_renewed = timezone.now().date()
        self.save(update_fields=['amount', 'last_renewed'])

    def update_current_credits(self):
        if self.amount <= self.total_amount and self.amount > self.minimum_balance:
            self.amount -= 1
        self.save(update_fields=['amount'])
        return self.amount
    
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
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def set_description(self, dream_id):
        related_message = str(DreamMessage.objects.filter(dream=self).order_by('created_at').first().message)
        splitted_message = related_message.rsplit(" ")
        description_list = []
        counter = 0
        for value in splitted_message:
            counter += int(len(value))
            if counter < 45:
                description_list.append(value)
            else:
                description_list.append("...")
                break
        last_version = " ".join(description_list)
        self.description = last_version
        self.save(update_fields=['description'])

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
        return f"{self.dream.id} - {self.role}"

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
        return f"Analysis of {self.dream.id}"
    
class AIAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_answers')
    ai_model = models.CharField(max_length=100)
    dream = models.ForeignKey(Dream, on_delete=models.CASCADE, related_name='ai_answers')
    answer = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"AI Answer of {self.dream_id}"