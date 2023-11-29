from typing import Any
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportActionModelAdmin
from storages.models import ProductToCart
from .models import Part, Order, Cart, Report
from .resources import OrderResource
from .forms import OrderImportForm, OrderConfirmImportForm


class ProductToCartInline(admin.TabularInline):
    model = ProductToCart
    extra = 0


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
        return super().get_import_data_kwargs(request, *args, **kwargs)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [ProductToCartInline]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["clientid", "create_date"]

    def save_model(self, request: Any, obj: Report, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)
        obj.send_notification()
