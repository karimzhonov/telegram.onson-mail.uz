from typing import Any, Sequence
from django.urls import path, reverse
from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportActionModelAdmin
from storages.models import ProductToCart
from users.models import ClientId, get_storages
from contrib.django.admin import table
from .models import Part, Order, Cart, Report
from .resources import OrderResource
from .forms import OrderImportForm, OrderConfirmImportForm, PartForm, OrderForm, ReportForm, CartForm


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
    list_display = ["number", "part", "clientid", "client", "name", "weight", "facture_price", "payed_price"]
    list_filter = ["part", "part__storage", "client"]
    search_fields = ["part__number", "part__storage__slug", "client__passport"]
    readonly_fields = ["products_table"]
    exclude = ["products"]

    resource_classes = []
    import_form_class = OrderImportForm
    confirm_form_class = OrderConfirmImportForm
    resource_classes = [OrderResource]
    form = OrderForm

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form is None:
            return initial
        initial["part"] = request.POST.get("part")
        initial["date"] = request.POST.get("date")
        return initial

    @admin.display(description="Table")
    def products_table(self, obj: Order):
        return format_html(table(obj.products, {
            "name": "Название",
            "desc": "Описание",
            "currency": "Валюта",
            "price": "Цена",
            "category": "Категори",
            "weight": "Вес",
            "all_weight": "Вес все товара",
            "facture_price": "Счет-фактура"
        }))

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
    
    def export_admin_action(self, request, queryset):
        """
        Exports the selected rows using file_format.
        """
        export_format = 2

        if not export_format:
            messages.warning(request, _('You must select an export format.'))
        else:
            formats = self.get_export_formats()
            file_format = formats[int(export_format)]()

            export_data = self.get_export_data(file_format, queryset, request=request, encoding=self.to_encoding)
            content_type = file_format.get_content_type()
            response = HttpResponse(export_data, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (
                self.get_export_filename(request, queryset, file_format),
            )
            return response


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [ProductToCartInline]
    search_fields = ["clientid__id_str"]
    fields = ["clientid", "part", "table"]
    readonly_fields = ["table", "clientid"]
    form = CartForm

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/create_order/',
                self.admin_site.admin_view(self.create_order),
                name='%s_%s_create_order' % info),
        ]
        return my_urls + urls
    
    def create_order(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(id=kwargs.get("object_id"))
            if not cart.part:
                raise Exception("Выберите партию, сохраните, потом оформите заказ")
            order = cart.create_order()
            messages.success(request, f"Order created: {order}")
            url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name), current_app=self.admin_site.name)
            return HttpResponseRedirect(url)
        except Exception as _exp:
            messages.error(request, f"Error: {_exp}")
            url = reverse('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), kwargs=kwargs, current_app=self.admin_site.name)
            return HttpResponseRedirect(url)

    @admin.display(description="Info")
    def table(self, obj: Cart):
        info = self.model._meta.app_label, self.model._meta.model_name
        return format_html(table(obj.render_products(), {
            "name": "Название",
            "desc": "Описание",
            "currency": "Валюта",
            "price": "Цена",
            "category": "Категори",
            "weight": "Вес",
            "all_weight": "Вес все товара",
            "facture_price": "Счет-фактура"
        }, f'<a href="{reverse("admin:%s_%s_create_order" % info, kwargs={"object_id": obj.id}, current_app=self.admin_site.name)}" class="btn btn-success">Оформить</a>'))

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
    