from django.contrib import admin
from .models import User, Dream, DreamMessage, Interpretation, UserDevice

# Register your models here.
admin.site.register(User)
admin.site.register(Dream)
admin.site.register(DreamMessage)
admin.site.register(Interpretation)

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    fields = ('user', 'device_name', 'device_ip', 'first_registered_at', 'last_login_at', 'deleted_at', 'is_active')
    list_display = ('id', 'user', 'device_id', 'device_name', 'device_ip', 'first_registered_at', 'last_login_at', 'deleted_at', 'is_active')
    readonly_fields = ('first_registered_at', 'last_login_at')