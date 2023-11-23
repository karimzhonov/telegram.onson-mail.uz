from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin
from .models import ClientId, Client
from .resources import ClientIdResource

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fields = ["pnfl", "passport", "fio", 'phone', "address", "passport_image", "preview_passport"]
    readonly_fields = ["preview_passport"]

    @admin.display(description="Passport Image")
    def preview_passport(self, obj: Client):
        return format_html('<img src="%s" width="150" height="150" />' % (obj.passport_image.url))


@admin.register(ClientId)
class ClientIdAdmin(ImportExportActionModelAdmin):
    list_display = ["get_id", "storage", "selected_client", "user"]
    resource_classes = [ClientIdResource]
    skip_admin_log = True
    list_filter = ["deleted", "storage"]
