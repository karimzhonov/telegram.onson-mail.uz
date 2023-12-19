from typing import Any, Callable, Optional, Sequence

from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.http.request import HttpRequest
from django.utils.html import format_html

from contrib.django.admin import ReadOnlyAdminModelMixin

from .models import Order, ReportImage


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

class ReportImageInline(admin.StackedInline):
    model = ReportImage
    extra = 0
    min_num = 1
    verbose_name = "Фотография"
    verbose_name_plural = "Фотографии"
    readonly_fields = ["get_image"]
    fields = ["get_image", "image"]

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return request.user.is_superuser

    @admin.display(description="Фотографии")
    def get_image(self, obj: ReportImage):
        return format_html('<img src="%s" width="500"/>' % (obj.image.url))
