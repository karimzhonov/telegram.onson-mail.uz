import json, os
from django.db import models
from django.conf import settings
from parler.models import TranslatableModel, TranslatedFields
from app.settings import LANGUAGES
LOCALE_PATH = os.path.join(settings.BASE_DIR, "bot/assets/jsons/locale.json")


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.SlugField(blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    lang = models.CharField(choices=LANGUAGES, max_length=20, default="uz")

    def __str__(self) -> str:
        return self.username
    

class Info(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255, null=True),
        text=models.TextField(null=True)
    )
    file = models.FileField(upload_to="info")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.slug
    

def get_text(slug, lang, **kwargs):
    with open(LOCALE_PATH, encoding="utf-8") as file:
        locale: dict[str, dict[str, str]] = json.load(file)

    for _lang, _ in LANGUAGES:
        locale[_lang].setdefault(slug, slug)
    if settings.DEBUG:
        with open(LOCALE_PATH, "w", encoding="utf-8") as file:
            json.dump(locale, file, indent=4, ensure_ascii=False)
    return locale[lang][slug].format(**kwargs)


def check_text(slug, text, lang):
    with open(LOCALE_PATH, encoding="utf-8") as file:
        locale: dict[str, dict[str, str]] = json.load(file)
    locale[lang].setdefault(slug, slug)
    test = locale[lang][slug] == text or locale[lang][slug] == slug
    if test:
        return True
    texts = []
    for _, values in locale.items():
        texts.append(values.get(slug))
    return text in texts
