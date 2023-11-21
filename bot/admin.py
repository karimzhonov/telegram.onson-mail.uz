from django.contrib import admin
from django.http.request import HttpRequest

from .models import User, Text, Info


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['text', 'slug', 'lang']
    list_filter = ['lang']


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    pass
