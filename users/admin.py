from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from .models import ClientId, Client
from .resources import ClientIdResource

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientId)
class ClientIdAdmin(ImportExportActionModelAdmin):
    list_display = ["get_id", "storage", "selected_client", "user"]
    resource_classes = [ClientIdResource]
    skip_admin_log = True
    list_filter = ["deleted", "storage"]
