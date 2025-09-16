from django.contrib import admin
from .models import User, Dream, DreamMessage, Analysis, UserDevice, Subscription

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'is_active', 'google_id', 'image', 'user_plan', 'last_chat_at', 'next_available_chat_at', 'user_created_at', 'user_updated_at')
    list_display = ('id', 'username', 'email', 'is_active', 'google_id', 'user_plan', 'last_chat_at', 'next_available_chat_at', 'user_created_at', 'user_updated_at')
    search_fields = ('email', 'username')
    # list_filter = ('is_active', 'user_plan')
    readonly_fields = ('user_created_at', 'user_updated_at')

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    fields = ('user', 'device_name', 'device_ip', 'first_registered_at', 'last_login_at', 'deleted_at', 'is_active')
    list_display = ('id', 'user', 'device_id', 'device_name', 'device_ip', 'first_registered_at', 'last_login_at', 'deleted_at', 'is_active')
    readonly_fields = ['first_registered_at']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    fields = ('user', 'subscription_plan', 'price', 'is_active', 'created_at', 'updated_at', 'deleted_at')
    list_display = ('id', 'user', 'subscription_plan', 'price', 'is_active', 'created_at', 'updated_at', 'deleted_at')
    search_fields = ('user__email', 'subscription_plan')
    # list_filter = ('is_active', 'subscription_plan')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    fields = ('author', 'created_at', 'updated_at', 'deleted_at', 'is_active')
    list_display = ('id', 'author', 'created_at', 'updated_at', 'deleted_at', 'is_active')
    search_fields = ('author__email',)
    # list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DreamMessage)
class DreamMessageAdmin(admin.ModelAdmin):
    fields = ('dream', 'role', 'message', 'created_at')
    list_display = ('id', 'dream', 'role', 'created_at')
    search_fields = ('dream__id', 'role')
    # list_filter = ('role',)
    readonly_fields = ['created_at']

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    fields = ('dream', 'json_analyze', 'status', 'error', 'created_at', 'updated_at', 'deleted_at')
    list_display = ('id', 'status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

