from typing import Any, Optional

from admincharts.admin import AdminChartMixin
from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html

from contrib.parler.admin import TranslatableAdmin
from users.models import get_storages

from .models import FAQ, FAQ_TYPE_BOT, Info, User


@admin.register(User)
class UserAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "line"
    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(clientid__storage__in=storages)
    
    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [], 
        }

        totals = []
        last_qs = User.history.annotate(
            id__in=queryset.values_list("id"),
            date=TruncDate("history_date")
        ).values("date").annotate(value=Count("id", distinct=True)).values_list('date', 'value').order_by('date')

        for data in last_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Активный пользователи", "data": totals, "backgroundColor": "green", "borderColor": "green"})
        
        totals = []
        create_qs = queryset.annotate(
            date=TruncDate("create_date")
        ).values("date").annotate(value=Count("id")).values_list('date', 'value').order_by('date')
        
        for data in create_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Созданный пользователи", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets


@admin.register(Info)
class InfoAdmin(TranslatableAdmin):
    actions = ["send_notification"]
    exclude = ["users"]

    @admin.action(description="Send Notification")
    def send_notification(self, request, queryset):
        count = 0
        for info in queryset:
            count += info.send_notification()
        messages.success(request, f"Пользователи: {count}")


@admin.register(FAQ)
class FAQAdmin(AdminChartMixin, admin.ModelAdmin):
    readonly_fields = ["faq_image", "faq_answer_image", "text", "user", "answer_user", "not_active", "image", ]
    exclude = ["image", "message_id"]
    list_display = ["user", "text", "answer_user", "answer", "type", "not_active"]
    list_filter = ["type", "user", "answer_user", "not_active"]

    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}
    list_chart_type = "line"

    def get_list_chart_queryset(self, changelist):
        return changelist.queryset

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: FAQ=None) -> bool:
        if obj and obj.not_active:
            return False
        return super().has_change_permission(request, obj)

    @admin.display(description="Фото вапроса")
    def faq_image(self, obj: FAQ):
        return format_html('<img src="%s" width="500"/>' % (obj.image.url))

    @admin.display(description="Фото ответа")
    def faq_answer_image(self, obj: FAQ):
        return format_html('<img src="%s" width="500"/>' % (obj.answer_image.url))
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).exclude(type=FAQ_TYPE_BOT)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if change:
            obj.not_active = True
            obj.answer_user = request.user
        super().save_model(request, obj, form, change)
        if change:
            obj.send_message()
    
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
        datasets["datasets"].append({"label": "Созданный пользователи", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets
