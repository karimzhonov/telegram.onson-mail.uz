from typing import Sequence

from admincharts.admin import AdminChartMixin
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
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
        return 0 if not last_quarter else last_quarter["value"]
    
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

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
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
