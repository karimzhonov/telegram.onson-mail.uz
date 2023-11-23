from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin
from contrib.django.admin import table
from orders.inlines import ClientOrderQuarterInline
from .models import ClientId, Client
from .resources import ClientIdResource


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["fio", "pnfl", "passport", "last_quarter"]
    fields = ["pnfl", "passport", "fio", 'phone', "address", "passport_image", "preview_passport", "last_quarter", "quarter_table"]
    readonly_fields = ["preview_passport", "last_quarter", "quarter_table"]
    search_fields = ["fio", "pnfl", "passport"]

    @admin.display(description="Passport Image")
    def preview_passport(self, obj: Client):
        return format_html('<img src="%s" width="150" height="150" />' % (obj.passport_image.url))
    
    @admin.display(description="Last quarter")
    def last_quarter(self, obj: Client):
        last_quarter = obj.order_quarters().order_by("quarter").last()
        return 0 if not last_quarter else last_quarter["value"]
    
    @admin.display(description="Quarter table")
    def quarter_table(self, obj: Client):
        return format_html(table(list(obj.order_quarters()), {"quarter": "Квартал", "value": "Значения"}))


@admin.register(ClientId)
class ClientIdAdmin(ImportExportActionModelAdmin):
    list_display = ["get_id", "storage", "selected_client", "user"]
    resource_classes = [ClientIdResource]
    skip_admin_log = True
    list_filter = ["deleted", "storage"]
    search_fields = ["get_id"]
