from django.db.models import Count
from django.db.models.functions import TruncDate
from jet.dashboard import modules

from .models import User


class UserLineChart(modules.DashboardModule):
    template = "bot/line_chart.html"
    title = 'График телеграм пользователи'

    class Media:
        js = ('jet.dashboard/vendor/chart.js/Chart.min.js', 'bot/line-chart.js')

    def init_with_context(self, context):
        create_qs = User.objects.annotate(
            date=TruncDate("create_date")
        ).values("date").annotate(value=Count("id")).values_list('date', 'value').order_by('date')
        for data in create_qs:
            self.children.append((*data, "Созданный пользователи"))

        last_qs = User.history.annotate(
            date=TruncDate("history_date")
        ).values("date").annotate(value=Count("id", distinct=True)).values_list('date', 'value').order_by('date')

        for data in last_qs:
            self.children.append((*data, "Активный пользователи"))
