from typing import Any
from django import forms
from django.forms.utils import ErrorList
from multiupload.fields import MultiImageField
from import_export.forms import ImportForm, ConfirmImportForm
from users.models import get_storages, Client, ClientId
from .models import Part, Order, Report, Cart


class OrderImportForm(ImportForm):
    part = forms.ModelChoiceField(Part.objects)
    date = forms.DateField()


class OrderConfirmImportForm(ConfirmImportForm):
    part = forms.ModelChoiceField(Part.objects)
    date = forms.DateField()


class PartForm(forms.ModelForm):
    
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

    class Meta:
        model = Part
        fields = "__all__"


class OrderForm(forms.ModelForm):
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
        self.fields["part"] = forms.ModelChoiceField(Part.objects.filter(storage__in=get_storages(self.request.user)), label="Партия")
        self.fields["client"] = forms.ModelChoiceField(Client.objects.filter(clientid__storage__in=get_storages(self.request.user)), label="Клиент")

    class Meta:
        model = Order
        fields = "__all__"


class CartForm(forms.ModelForm):
    def __init__(self, data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance: Cart=None,
        use_required_attribute=None,
        renderer=None) -> None:
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance, use_required_attribute, renderer)
        self.fields["part"] = forms.ModelChoiceField(Part.objects.filter(storage=instance.clientid.storage), label="Партия")

    class Meta:
        model = Cart
        fields = "__all__"


class CustomMultiImageField(MultiImageField):
    def run_validators(self, value):
        value = value or []
        for item in value:
            super().run_validators(item)


class ReportForm(forms.ModelForm):
    images = CustomMultiImageField(min_num=1, label="Фотографии")

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
        self.fields["clientid"] = forms.ModelChoiceField(ClientId.objects.filter(storage__in=get_storages(self.request.user)))

    class Meta:
        model = Report
        fields = ["clientid", "images"]

    def save(self, commit: bool = True) -> Any:
        for image in self.cleaned_data["images"]:
            obj = Report.objects.create(
                clientid=self.instance.clientid, image=image
            )
            obj.send_notification()
        return super().save(False)
