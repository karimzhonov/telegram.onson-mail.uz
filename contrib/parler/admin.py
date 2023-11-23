from parler import admin
from parler.utils.views import get_language_tabs


class TranslatableAdmin(admin.TranslatableAdmin):
    def get_language_tabs(self, request, obj, available_languages, css_class=None):
        """
        Determine the language tabs to show.
        """
        current_language = self.get_form_language(request, obj)
        css_class = 'col-12' if not css_class else f'col-12 {css_class}'
        return get_language_tabs(
            request, current_language, available_languages, css_class=css_class
        )


class TranslatableTabularInline(admin.TranslatableTabularInline):
    def get_language_tabs(self, request, obj, available_languages, css_class=None):
        """
        Determine the language tabs to show.
        """
        current_language = self.get_form_language(request, obj)
        css_class = 'col-12' if not css_class else f'col-12 {css_class}'
        return get_language_tabs(
            request, current_language, available_languages, css_class=css_class
        )