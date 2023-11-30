from django import forms
from django.forms.utils import ErrorList
from import_export.forms import ImportForm, ConfirmImportForm
from users.models import get_storages, Client, ClientId
from .models import Part, Order, Report


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
        self.fields["storage"] = forms.ModelChoiceField(get_storages(self.request.user))

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
        self.fields["part"] = forms.ModelChoiceField(Part.objects.filter(storage__in=get_storages(self.request.user)))
        self.fields["client"] = forms.ModelChoiceField(Client.objects.filter(selected_client__storage__in=get_storages(self.request.user)))

    class Meta:
        model = Order
        fields = "__all__"


class ReportForm(forms.ModelForm):
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
        fields = "__all__"
