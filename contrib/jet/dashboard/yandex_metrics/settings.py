# encoding: utf-8
from django import forms
from django.utils.encoding import force_str
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class YandexMetrikaSettingsForm(forms.Form):
    counter = forms.ChoiceField(label=_('Counter'))
    period = forms.ChoiceField(label=_('Statistics period'), choices=(
        (0, _('Today')),
        (6, _('Last week')),
        (30, _('Last month')),
        (31 * 3 - 1, _('Last quarter')),
        (364, _('Last year')),
    ))

    def set_module(self, module):
        self.set_counter_choices(module)

    def set_counter_choices(self, module):
        counters = module.counters()
        if counters is not None:
            self.fields['counter'].choices = (('', '-- %s --' % force_str(_('none'))),)
            self.fields['counter'].choices.extend(map(lambda x: (x['id'], x['site']), counters))
        else:
            label = force_str(_('grant access first')) if module.access_token is None else force_str(_('counters loading failed'))
            self.fields['counter'].choices = (('', '-- %s -- ' % label),)


class YandexMetrikaChartSettingsForm(YandexMetrikaSettingsForm):
    show = forms.ChoiceField(label=_('Show'), choices=(
        ('visitors', capfirst(_('visitors'))),
        ('visits', capfirst(_('visits'))),
        ('page_views', capfirst(_('views'))),
    ))
    group = forms.ChoiceField(label=_('Group'), choices=(
        ('day', _('By day')),
        ('week', _('By week')),
        ('month', _('By month')),
    ))
