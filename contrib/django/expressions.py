from django.db.models import FloatField, Func, Subquery


class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s::numeric, 2)'


class MaxSubquery(Subquery):
    template = "(SELECT max(%(field)s) FROM (%(subquery)s) _max)"
    output_field = FloatField()

    def __init__(self, queryset, field,output_field=FloatField(), **extra) -> None:
        extra['field'] = field
        super().__init__(queryset, output_field, **extra)


class MinSubquery(Subquery):
    template = "(SELECT min(%(field)s) FROM (%(subquery)s) _min)"
    output_field = FloatField()

    def __init__(self, queryset, field,output_field=FloatField(), **extra) -> None:
        extra['field'] = field
        super().__init__(queryset, output_field, **extra)


class AvgSubquery(Subquery):
    template = "(SELECT AVG(%(field)s) FROM (%(subquery)s) _avg)"
    output_field = FloatField()

    def __init__(self, queryset, field,output_field=FloatField(), **extra) -> None:
        extra['field'] = field
        super().__init__(queryset, output_field, **extra)


class CountSubquery(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = FloatField()

    def __init__(self, queryset,output_field=FloatField(), **extra) -> None:
        super().__init__(queryset, output_field, **extra)


class SumSubquery(Subquery):
    template = "(SELECT SUM(%(field)s) FROM (%(subquery)s) _sum)"
    output_field = FloatField()

    def __init__(self, queryset, field,output_field=FloatField(), **extra) -> None:
        extra['field'] = field
        super().__init__(queryset, output_field, **extra)