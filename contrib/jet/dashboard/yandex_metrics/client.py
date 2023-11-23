# encoding: utf-8
import json
from urllib import request
from urllib.error import URLError
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy as _

JET_MODULE_YANDEX_METRIKA_CLIENT_ID = getattr(settings, 'JET_MODULE_YANDEX_METRIKA_CLIENT_ID', '')
JET_MODULE_YANDEX_METRIKA_CLIENT_SECRET = getattr(settings, 'JET_MODULE_YANDEX_METRIKA_CLIENT_SECRET', '')


class YandexMetrikaClient:
    OAUTH_BASE_URL = 'https://oauth.yandex.ru/'
    API_BASE_URL = 'https://api-metrika.yandex.net/'
    CLIENT_ID = JET_MODULE_YANDEX_METRIKA_CLIENT_ID
    CLIENT_SECRET = JET_MODULE_YANDEX_METRIKA_CLIENT_SECRET

    def __init__(self, access_token=None):
        self.access_token = access_token

    def request(self, base_url, url, data=None, headers=None):
        url = '%s%s' % (base_url, url)

        if data is not None:
            data = urlencode(data).encode()

        if headers is None:
            headers = {}

        req = request.Request(url, data, headers)

        try:
            f = request.urlopen(req)
            result = f.read().decode('utf8')
            result = json.loads(result)
        except URLError as e:
            print(e, url)
            return None, e

        return result, None

    def get_oauth_authorize_url(self, state=''):
        return '%sauthorize' \
               '?response_type=code' \
               '&state=%s' \
               '&client_id=%s' % (self.OAUTH_BASE_URL, state, self.CLIENT_ID)

    def oauth_request(self, url, data=None):
        return self.request(self.OAUTH_BASE_URL, url, data)

    def oath_token_request(self, code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }
        return self.oauth_request('token', data)

    def api_request(self, url, data=None):
        headers = None
        if self.access_token is not None:
            headers = {'Authorization': 'OAuth %s' % self.access_token}
        return self.request(self.API_BASE_URL, url, data, headers)

    def api_counters_request(self):
        return self.api_request('management/v1/counters')

    def api_stat_traffic_summary(self, counter, date1, date2, group=None):
        if group is None:
            group = 'day'
        return self.api_request('stat/v1/data/bytime?id=%s&date1=%s&date2=%s&group=%s&preset=sources_summary&metrics=ym:s:users,ym:s:visits,ym:s:pageviews' % (
            counter,
            date1.strftime('%Y%m%d'),
            date2.strftime('%Y%m%d'),
            group
        ))
