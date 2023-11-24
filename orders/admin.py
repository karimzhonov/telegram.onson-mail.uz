from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportActionModelAdmin
from .models import Part, Order
from .resources import OrderResource
from .forms import OrderImportForm, OrderConfirmImportForm

@admin.register(Part)
class PartAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_filter = ["storage"]
    list_display = ["number", "storage"]
    actions = ['send_notification']

    @admin.action(description="Отправка уведомления")
    def send_notification(self, request, queryset):
        for part in queryset:
            part.notificate_users()
        

@admin.register(Order)
class OrderAdmin(ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ["number", "part", "client_id", "client", "name", "weight", "facture_price", "payed_price"]
    list_filter = ["part", "part__storage", "client"]
    resource_classes = []
    import_form_class = OrderImportForm
    confirm_form_class = OrderConfirmImportForm
    resource_classes = [OrderResource]

    def get_import_data_kwargs(self, request, *args, **kwargs):
        kwargs.update(form_data=kwargs.get("form").cleaned_data)
        self.get_urls
        return super().get_import_data_kwargs(request, *args, **kwargs)