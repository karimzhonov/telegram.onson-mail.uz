from django import forms
from django.utils.deprecation import MiddlewareMixin


class FormRequestMiddleware(MiddlewareMixin):
    def __call__(self, request):
        forms.BaseForm.request = request
        response = self.get_response(request)
        return response
