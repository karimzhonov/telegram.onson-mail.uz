from typing import Sequence
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin
from contrib.django.admin import table
from .models import ClientId, Client, UserSettings, get_storages
from .resources import ClientIdResource


admin.site.unregister(User)


class UserSettingsAdmin(admin.StackedInline):
    model = UserSettings
    extra = 0
    max_num = 1


@admin.register(User)
class UserAdmin(_UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "usersettings")
    inlines = [UserSettingsAdmin]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(usersettings__storages__in=storages)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["fio", "pnfl", "passport", "last_quarter"]
    fields = ["pnfl", "passport", "fio", 'phone', "address", "passport_image", "preview_passport", "last_quarter", "quarter_table"]
    readonly_fields = ["preview_passport", "last_quarter", "quarter_table"]
    search_fields = ["fio", "pnfl", "passport"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(selected_client__storage__in=storages)

    @admin.display(description="Passport Image")
    def preview_passport(self, obj: Client):
        return format_html('<img src="%s" width="500"/>' % (obj.passport_image.url))
    
    @admin.display(description="Last quarter")
    def last_quarter(self, obj: Client):
        last_quarter = obj.order_quarters().order_by("quarter").last()
        return 0 if not last_quarter else last_quarter["value"]
    
    @admin.display(description="Quarter table")
    def quarter_table(self, obj: Client):
        return format_html(table(list(obj.order_quarters()), {"quarter": "Квартал", "value": "Значения"}))


@admin.register(ClientId)
class ClientIdAdmin(SimpleHistoryAdmin, ImportExportActionModelAdmin):
    list_display = ["get_id", "storage", "selected_client", "user"]
    readonly_fields = ["get_id", "storage"]
    resource_classes = [ClientIdResource]
    skip_admin_log = True
    list_filter = ["deleted", "storage"]
    search_fields = ["id", "id_str", "selected_client__fio", "clients__fio", "selected_client__passport", "clients__passport"]
    fields = ["get_id", "storage", "selected_client", "user", "clients", "deleted"]
    ordering = ["-id"]

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        if request.user.is_superuser:
            return super().get_list_filter(request)
        return ["deleted"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(storage__in=storages)
