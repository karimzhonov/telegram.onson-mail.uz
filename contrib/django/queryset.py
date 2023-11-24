from django.db.models.functions import TruncQuarter
from django.db import models


class QuarterQuerysetMixin:
    def quarter(self, date_field, func_field, func="Sum", **func_kwargs) -> models.QuerySet:
        Func = getattr(models, func)
        return self.annotate(
            quarter=TruncQuarter(date_field)
        ).values('quarter').annotate(value=Func(func_field, **func_kwargs)
        ).values('quarter', 'value')
