from django.contrib import admin
from .models import User, Dream, DreamMessage, Interpretation

# Register your models here.
admin.site.register(User)
admin.site.register(Dream)
admin.site.register(DreamMessage)
admin.site.register(Interpretation)