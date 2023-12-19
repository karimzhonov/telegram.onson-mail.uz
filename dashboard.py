from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import AppIndexDashboard, Dashboard


class AppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.children.append(modules.ModelList(
            title=_('Application models'),
            models=self.models(),
            column=0,
            order=0
        ))
        self.available_children.append(modules.RecentActions)

        if self.app_label == 'bot':
            from bot.dashboard import UserLineChart
            self.columns = 2
            self.children.append(UserLineChart())

        if self.app_label == 'orders':
            from orders.dashboard import OrderLineChart, OrderTotals
            self.columns = 2
            self.children.append(OrderLineChart())
            self.children.append(OrderTotals())


class IndexDashboard(Dashboard):
    columns = 2
    def init_with_context(self, context):
        from bot.dashboard import UserLineChart
        from orders.dashboard import OrderLineChart, OrderTotals
        self.children.append(OrderTotals())
        self.children.append(UserLineChart())
        self.children.append(OrderLineChart())
        self.children.append(modules.AppList())
        self.children.append(modules.RecentActions())
