from django.contrib import admin

# Register your models here.
from .models import *

class UserAdminModel(admin.ModelAdmin):
    list_display = ('username','user_type','user_subtype')
    search_fields=('username',)

# admin.site.register(User,UserAdminModel)