from django import forms
from import_export.forms import ImportForm, ConfirmImportForm
from .models import Part


class OrderImportForm(ImportForm):
    part = forms.ModelChoiceField(Part.objects)
    date = forms.DateField()


class OrderConfirmImportForm(ConfirmImportForm):
    part = forms.ModelChoiceField(Part.objects)
    date = forms.DateField()