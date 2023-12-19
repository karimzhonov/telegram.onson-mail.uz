from django import forms
from django.forms.utils import ErrorList
from import_export.forms import ConfirmImportForm, ImportForm

from storages.models import Storage


class UserImportForm(ImportForm):
    storage = forms.ModelChoiceField(Storage.objects)



class UserConfirmImportForm(ConfirmImportForm):
    storage = forms.ModelChoiceField(Storage.objects)
