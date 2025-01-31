from typing import Any, Sequence

from admincharts.admin import AdminChartMixin
from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from contrib.django.admin import table
from storages.models import ProductToCart
from users.models import ClientId, get_storages

from .forms import CartForm, OrderConfirmImportForm, OrderImportForm, PartForm, ReportForm
from .inlines import ReportImageInline
from .models import Cart, Order, Part, Report
from .resources import OrderResource
from .formats import OrderXLSX


class ProductToCartInline(admin.TabularInline):
    model = ProductToCart
    extra = 0


@admin.register(Part)
class PartAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_filter = ["storage"]
    list_display = ["number", "storage", "status"]
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
        count_orders = 0
        for part in queryset:
            count_orders += part.notificate_users()
        clients = Order.objects.filter(part__in=queryset).values_list("client__id", flat=True)
        storages = queryset.values_list("storage__id", flat=True)
        cout_clientid = 0
        for clientid in ClientId.objects.filter(storage__id__in=storages, selected_client__id__in=clients).distinct("id"):
            cout_clientid += clientid.send_notification()
        messages.success(request, f"Заказы: {count_orders}, Клиент: {cout_clientid}")


@admin.register(Order)
class OrderAdmin(AdminChartMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ["number", "part", "clientid", "client", "name", "weight", "facture_price", "payed_price"]
    search_fields = ["part__number", "client__passport", "client__pnfl"]
    readonly_fields = ["products_table"]
    exclude = ["products"]

    import_form_class = OrderImportForm
    confirm_form_class = OrderConfirmImportForm
    resource_classes = [OrderResource]
    # form = OrderForm
    skip_admin_log = True
    formats = [OrderXLSX]

    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}
    list_chart_type = "line"

    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

    def has_import_permission(self, request):
        return request.user.is_superuser

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
            return ["part", "part__storage", "client", ("date", admin.DateFieldListFilter)]
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
        
    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [], 
        }
        totals = []
        create_qs = queryset.annotate(
            _date=TruncDate("date")
        ).values("_date").annotate(value=Count("id")).values_list('_date', 'value').order_by('_date')
        
        for data in create_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Закази", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets


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

    @admin.display(description="Продукти")
    def table(self, obj: Cart):
        return format_html(table(obj.render_products(), {
            "name": "Название",
            "desc": "Описание",
            "currency": "Валюта",
            "price": "Цена",
            "category": "Категори",
            "weight": "Вес",
            "all_weight": "Вес все товара",
            "facture_price": "Счет-фактура"
        }))

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(clientid__storage__in=storages)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin, AdminChartMixin):
    list_display = ["clientid", "create_date"]
    search_fields = ["clientid__id_str", "clientid__id"]
    list_display_links = ["clientid"]
    form = ReportForm
    inlines = [ReportImageInline]
    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}
    list_chart_type = "line"

    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(clientid__storage__in=storages)
    
    def save_related(self, request: Any, form: Any, formsets: Any, change: Any) -> None:
        super().save_related(request, form, formsets, change)
        print(request.POST, request.FILES)
        object = form.instance
        if object.reportimage_set.all().exists():
            object.send_notification()
    
    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [], 
        }
        totals = []
        create_qs = queryset.annotate(
            date=TruncDate("create_date")
        ).values("date").annotate(value=Count("id")).values_list('date', 'value').order_by('date')
        
        for data in create_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Созданный пользователи", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets
    
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if not request.user.is_superuser:
            return response
        # This could be a redirect and not have context_data
        if not hasattr(response, "context_data"):
            return response

        if "cl" in response.context_data:
            changelist = response.context_data["cl"]
            chart_queryset = self.get_list_chart_queryset(changelist)
            response.context_data["adminchart_queryset"] = chart_queryset
            response.context_data[
                "adminchart_chartjs_config"
            ] = self.get_list_chart_config(chart_queryset)
        else:
            response.context_data["adminchart_queryset"] = None
            response.context_data["adminchart_chartjs_config"] = None

        return response
