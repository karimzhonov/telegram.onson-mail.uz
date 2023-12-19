from django.db.models import Count
from django.db.models.functions import TruncDate
from jet.dashboard import modules

from .models import DONE, IN_DELIVERY, IN_STORAGE, Order


class OrderLineChart(modules.DashboardModule):
    template = "bot/line_chart.html"
    title = 'График заказов'

    class Media:
        js = ('jet.dashboard/vendor/chart.js/Chart.min.js', 'bot/line-chart.js')

    def init_with_context(self, context):
        create_qs = Order.objects.annotate(
            _date=TruncDate("date")
        ).values("_date").annotate(value=Count("id")).values_list('_date', 'value').order_by('_date')
        for data in create_qs:
            self.children.append((*data, "Кол-во заказов"))


class OrderTotals(modules.DashboardModule):
    """
    Yandex Metrika widget that shows total number of visitors, visits and viewers for a particular period of time.
    Period may be following: Today, Last week, Last month, Last quarter, Last year
    """

    title = 'Информация о заказов'
    template = 'jet.dashboard/modules/yandex_metrika_visitors_totals.html'


    def init_with_context(self, context):
        self.children.append({'title': "Кол-во заказов", 'value': Order.objects.count()})
        self.children.append({'title': "Кол-во заказов в складе", 'value': Order.objects.filter(part__status=IN_STORAGE).count()})
        self.children.append({'title': "Кол-во заказов доставке", 'value': Order.objects.filter(part__status=IN_DELIVERY).count()})
        self.children.append({'title': "Кол-во заказов доставленные", 'value': Order.objects.filter(part__status=DONE).count()})
