from django.contrib import admin
from django.http.request import HttpRequest
from contrib.parler.admin import TranslatableAdmin
from .models import User, Info


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Info)
class InfoAdmin(TranslatableAdmin):
    pass
