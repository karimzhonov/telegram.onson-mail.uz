from typing import Any
from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from contrib.django.admin import ReadOnlyAdminModelMixin
from .models import Order


class ClientOrderQuarterFormset(ReadOnlyAdminModelMixin, BaseInlineFormSet):

    def get_queryset(self) -> Any:
        qs = super().get_queryset()
        return qs.quarter("date", "facture_price")
    

class ClientOrderQuarterForm(forms.BaseModelForm):
    base_fields = ["value", "quarter"]
    quarter = forms.DateField()
    value = forms.FloatField()


class ClientOrderQuarterInline(ReadOnlyAdminModelMixin, admin.TabularInline):
    model = Order
    extra = 0
