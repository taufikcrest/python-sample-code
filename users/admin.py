from django.contrib import admin
from . models import User, UserToken, Notes
# Register your models here.

admin.site.register(User)
admin.site.register(UserToken)
admin.site.register(Notes)