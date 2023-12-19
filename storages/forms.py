from django import forms
from django.db import models
from django.forms.utils import ErrorList

from users.models import get_storages

from .models import Category, Product


class ProductForm(forms.ModelForm):
    def __init__(self, data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None) -> None:
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance, use_required_attribute, renderer)
        self.fields["storage"] = forms.ModelChoiceField(get_storages(self.request.user), label="Склад")
        self.fields["category"] = forms.ModelChoiceField(Category.objects.exclude(
            models.Q(category__isnull=False)
        ), label="Категория")

    class Meta:
        model = Product
        fields = "__all__"
