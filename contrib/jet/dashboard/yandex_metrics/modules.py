import datetime
from urllib.error import HTTPError

from backend.jet_conf import JET_MODULE_YANDEX_METRIKA_ACCESS_TOKEN
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from jet.dashboard.modules import DashboardModule

from .client import YandexMetrikaClient
from .settings import YandexMetrikaChartSettingsForm, YandexMetrikaSettingsForm


class YandexMetrikaBase(DashboardModule):
    settings_form = YandexMetrikaSettingsForm
    ajax_load = True
    contrast = True
    period = None
    access_token = None
    expires_in = None
    token_type = None
    counter = None
    error = None

    def settings_dict(self):
        return {
            'period': self.period,
            'access_token': self.access_token,
            'expires_in': self.expires_in,
            'token_type': self.token_type,
            'counter': self.counter
        }

    def load_settings(self, settings):
        try:
            self.period = int(settings.get('period'))
        except TypeError:
            self.period = 0
        self.access_token = JET_MODULE_YANDEX_METRIKA_ACCESS_TOKEN
        self.expires_in = settings.get('expires_in')
        self.token_type = settings.get('token_type')
        self.counter = settings.get('counter')

    def init_with_context(self, context):
        raise NotImplementedError('subclasses of YandexMetrika must provide a init_with_context() method')

    def counters(self):
        client = YandexMetrikaClient(self.access_token)
        counters, exception = client.api_counters_request()

        if counters is not None:
            return counters['counters']
        else:
            return None

    def format_grouped_date(self, date, group):
        if group == 'week':
            date = u'%s — %s' % (
                (date - datetime.timedelta(days=7)).strftime('%d.%m'),
                date.strftime('%d.%m')
            )
        elif group == 'month':
            date = date.strftime('%b, %Y')
        else:
            date = formats.date_format(date, 'DATE_FORMAT')
        return date

    def counter_attached(self):
        if self.access_token is None:
            self.error = mark_safe(_('Please <a href="%s">attach Yandex account and choose Yandex Metrika counter</a> to start using widget') % reverse('jet-dashboard:update_module', kwargs={'pk': self.model.pk}))
            return False
        elif self.counter is None:
            self.error = mark_safe(_('Please <a href="%s">select Yandex Metrika counter</a> to start using widget') % reverse('jet-dashboard:update_module', kwargs={'pk': self.model.pk}))
            return False
        else:
            return True

    def api_stat_traffic_summary(self, group=None):
        if self.counter_attached():
            date1 = datetime.datetime.now() - datetime.timedelta(days=self.period)
            date2 = datetime.datetime.now()

            client = YandexMetrikaClient(self.access_token)
            result, exception = client.api_stat_traffic_summary(self.counter, date1, date2, group)

            if exception is not None:
                error = _('API request failed.')
                if isinstance(exception, HTTPError) and exception.code == 403:
                    error += _(' Try to <a href="%s">revoke and grant access</a> again') % reverse('jet-dashboard:update_module', kwargs={'pk': self.model.pk})
                self.error = mark_safe(error)
            else:
                return result


class YandexMetrikaVisitorsTotals(YandexMetrikaBase):
    """
    Yandex Metrika widget that shows total number of visitors, visits and viewers for a particular period of time.
    Period may be following: Today, Last week, Last month, Last quarter, Last year
    """

    title = _('Yandex Metrika visitors totals')
    template = 'jet.dashboard/modules/yandex_metrika_visitors_totals.html'

    #: Which period should be displayed. Allowed values - integer of days
    period = None

    def __init__(self, title=None, period=None, **kwargs):
        kwargs.update({'period': period})
        super(YandexMetrikaVisitorsTotals, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        result = self.api_stat_traffic_summary()
        if result is not None:
            try:
                self.children.append({'title': _('visitors'), 'value': max(result['totals'][0])})
                self.children.append({'title': _('visits'), 'value': sum(result['totals'][1])})
                self.children.append({'title': _('views'), 'value': sum(result['totals'][2])})
            except KeyError:
                self.error = _('Bad server response')


class YandexMetrikaVisitorsChart(YandexMetrikaBase):
    """
    Yandex Metrika widget that shows visitors/visits/viewer chart for a particular period of time.
    Data is grouped by day, week or month
    Period may be following: Today, Last week, Last month, Last quarter, Last year
    """

    title = _('Yandex Metrika visitors chart')
    template = 'jet.dashboard/modules/yandex_metrika_visitors_chart.html'
    style = 'overflow-x: auto;'

    #: Which period should be displayed. Allowed values - integer of days
    period = None

    #: What data should be shown. Possible values: ``visitors``, ``visits``, ``page_views``
    show = None

    #: Sets grouping of data. Possible values: ``day``, ``week``, ``month``
    group = None
    settings_form = YandexMetrikaChartSettingsForm

    class Media:
        js = ('jet.dashboard/vendor/chart.js/Chart.min.js', 'jet.dashboard/dashboard_modules/yandex_metrika.js')

    def __init__(self, title=None, period=None, show=None, group=None, **kwargs):
        kwargs.update({'period': period, 'show': show, 'group': group})
        super(YandexMetrikaVisitorsChart, self).__init__(title, **kwargs)

    def settings_dict(self):
        settings = super(YandexMetrikaVisitorsChart, self).settings_dict()
        settings['show'] = self.show
        settings['group'] = self.group
        return settings

    def load_settings(self, settings):
        super(YandexMetrikaVisitorsChart, self).load_settings(settings)
        self.show = settings.get('show')
        self.group = settings.get('group')

    def init_with_context(self, context):
        result = self.api_stat_traffic_summary(self.group)
        key_to_id = {
            'visitors': 0,
            'visits': 1,
            'page_views': 2,
        }
        if result is not None:
            try:
                key_id = key_to_id[self.show if self.show is not None else 'visitors']
                for i, date in enumerate(result['time_intervals']):
                    self.children.append((datetime.datetime.strptime(date[0], '%Y-%m-%d'), result['totals'][key_id][i]))
            except KeyError:
                self.error = _('Bad server response')
