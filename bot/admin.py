from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from admincharts.admin import AdminChartMixin
from contrib.parler.admin import TranslatableAdmin
from .models import User, Info


@admin.register(User)
class UserAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "line"
    list_chart_options = {"responsive": True, "scales": {
        "y": {"min": 0}
    }}

    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [],
        }
        totals = []
        create_qs = User.objects.annotate(
            date=TruncDate("create_date")
        ).values("date").annotate(value=Count("id")).values_list('date', 'value').order_by('date')
        
        for data in create_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Созданный пользователи", "data": totals, "backgroundColor": "red", "borderColor": "red"})

        totals = []
        last_qs = User.history.annotate(
            date=TruncDate("history_date")
        ).values("date").annotate(value=Count("id", distinct=True)).values_list('date', 'value').order_by('date')

        for data in last_qs:
            totals.append({"x": data[0], "y": data[1]})
        datasets["datasets"].append({"label": "Активный пользователи", "data": totals, "backgroundColor": "green", "borderColor": "green"})
        return datasets


@admin.register(Info)
class InfoAdmin(TranslatableAdmin):
    pass
