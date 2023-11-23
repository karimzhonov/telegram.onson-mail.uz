from django.contrib import admin
from django.http.request import HttpRequest
from contrib.parler.admin import TranslatableAdmin
from .models import User, Info


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Info)
class InfoAdmin(TranslatableAdmin):
    pass
