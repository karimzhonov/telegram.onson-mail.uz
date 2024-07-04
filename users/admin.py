from django.core.exceptions import ImproperlyConfigured

from admincharts.admin import AdminChartMixin
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Subquery, OuterRef, Case, When,Q, FloatField
from django.db.models.functions import TruncDate
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from import_export.admin import ImportExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from contrib.django.admin import table

from .forms import UserConfirmImportForm, UserImportForm
from .models import Client, ClientId, UserSettings, get_storages
from .resources import ClientIdResource

admin.site.unregister(User)


class UserSettingsAdmin(admin.StackedInline):
    model = UserSettings
    extra = 0
    max_num = 1


class IsWarningFilter(admin.ListFilter):
    title = "Красный паспорт"
    parameter_name = '_is_warning'

    def __init__(self, request, params, model, model_admin) -> None:
        super().__init__(request, params, model, model_admin)
        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify a 'parameter_name'."
                % self.__class__.__name__
            )
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def has_output(self) -> bool:
        return True
    
    def choices(self, changelist):
        for lookup, title in (
            (None, _("All")),
            ("1", _("Yes")),
            ("0", _("No")),
        ):
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def value(self):
        """
        Return the value (in string format) provided in the request's
        query string for this filter, if any, or None if the value wasn't
        provided.
        """
        return self.used_parameters.get(self.parameter_name)
    
    def queryset(self, request, queryset):
        from orders.models import Order, LIMIT_FOR_QUARTER
        if not self.value():
            return queryset
        return queryset.annotate(
            _last_quarter_value=Subquery(Order.objects.filter(client_id=OuterRef('pnfl')).quarter("date", "facture_price").order_by("-quarter").values("value")[:1], output_field=FloatField()),
            _is_warning=Case(When(Q(_last_quarter_value__gte=LIMIT_FOR_QUARTER), True), default=False)
        ).filter(_is_warning=self.value())
    

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
class ClientAdmin(AdminChartMixin, admin.ModelAdmin):
    list_display = ["fio", "pnfl", "passport", "last_quarter"]
    fields = ["pnfl", "passport", "fio", 'phone', "address", "passport_image", "preview_passport", "last_quarter", "quarter_table"]
    readonly_fields = ["preview_passport", "last_quarter", "quarter_table"]
    search_fields = ["fio", "pnfl", "passport"]
    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}
    list_chart_type = "line"
    list_filter = [IsWarningFilter, ]

    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(selected_client__storage__in=storages)

    @admin.display(description="Фото паспорта")
    def preview_passport(self, obj: Client):
        return format_html('<img src="%s" width="500"/>' % (obj.passport_image.url))
    
    @admin.display(description="Последный квартал")
    def last_quarter(self, obj: Client):
        last_quarter = obj.order_quarters().order_by("quarter").last()
        if not last_quarter:
            return 0
        return last_quarter["value"] if (last_quarter["date"].month - 1) // 3 + 1 == (timezone.now().date().month - 1) // 3 + 1 else 0
    
    @admin.display(description="Таблица кварталов")
    def quarter_table(self, obj: Client):
        return format_html(table(list(obj.order_quarters()), {"quarter": "Квартал", "value": "Значения"}))

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


@admin.register(ClientId)
class ClientIdAdmin(AdminChartMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ["get_id", "storage", "selected_client", "user"]
    readonly_fields = ["get_id", "storage"]
    resource_classes = [ClientIdResource]
    import_form_class = UserImportForm
    confirm_form_class = UserConfirmImportForm
    skip_admin_log = True
    list_filter = ["deleted", "storage", "selected_client"]
    search_fields = ["id", "id_str", "selected_client__fio", "clients__fio", "selected_client__passport", "clients__passport"]
    fields = ["get_id", "storage", "selected_client", "user", "clients", "deleted"]
    ordering = ["-id"]

    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}
    list_chart_type = "line"

    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

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

    def has_import_permission(self, request):
        return request.user.is_superuser

    def get_list_filter(self, request: HttpRequest) -> list[str]:
        if request.user.is_superuser:
            return super().get_list_filter(request)
        return ["deleted"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(storage__in=storages)
    
    def get_import_data_kwargs(self, request, *args, **kwargs):
        kwargs.update(form_data=kwargs.get("form").cleaned_data)
        return super().get_import_data_kwargs(request, *args, **kwargs)
    
    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form is None:
            return initial
        initial["storage"] = request.POST.get("storage")
        return initial

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
