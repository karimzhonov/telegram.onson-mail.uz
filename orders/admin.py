from typing import Any, Optional, Sequence
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportActionModelAdmin
from storages.models import ProductToCart
from users.models import ClientId, get_storages
from .models import Part, Order, Cart, Report
from .resources import OrderResource
from .forms import OrderImportForm, OrderConfirmImportForm, PartForm, OrderForm, ReportForm


class ProductToCartInline(admin.TabularInline):
    model = ProductToCart
    extra = 0


@admin.register(Part)
class PartAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_filter = ["storage"]
    list_display = ["number", "storage"]
    actions = ['send_notification']
    form = PartForm

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        if request.user.is_superuser:
            return super().get_list_filter(request)
        return []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(storage__in=storages)

    @admin.action(description="Отправка уведомления")
    def send_notification(self, request, queryset):
        for part in queryset:
            part.notificate_users()
        clients = Order.objects.filter(part__in=queryset).values_list("client__id", flat=True)
        storages = queryset.values_list("storage__id", flat=True)
        for clientid in ClientId.objects.filter(storage__id__in=storages, selected_client__id__in=clients).distinct("id"):
            clientid.send_notification()


@admin.register(Order)
class OrderAdmin(ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ["number", "part", "client_id", "client", "name", "weight", "facture_price", "payed_price"]
    list_filter = ["part", "part__storage", "client"]
    search_fields = ["part__number", "part__storage__slug", "client__passport"]
    resource_classes = []
    import_form_class = OrderImportForm
    confirm_form_class = OrderConfirmImportForm
    resource_classes = [OrderResource]
    form = OrderForm

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        if request.user.is_superuser:
            return super().get_list_filter(request)
        return []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(part__storage__in=storages)

    def get_import_data_kwargs(self, request, *args, **kwargs):
        kwargs.update(form_data=kwargs.get("form").cleaned_data)
        return super().get_import_data_kwargs(request, *args, **kwargs)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [ProductToCartInline]
    search_fields = ["clientid__id_str"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(clientid__storage__in=storages)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "clientid", "create_date"]
    fields = ["clientid", "image", "get_image"]
    readonly_fields = ["get_image"]
    search_fields = ["clientid__id_str"]
    form = ReportForm

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(clientid__storage__in=storages)

    def save_model(self, request: Any, obj: Report, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)
        obj.send_notification()

    @admin.display(description="Passport Image")
    def get_image(self, obj: Report):
        return format_html('<img src="%s" width="500" />' % (obj.image.url))
    