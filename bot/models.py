import json, os, re
from asgiref.sync import sync_to_async
from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords
from parler.models import TranslatableModel, TranslatedFields
from app.settings import LANGUAGES
LOCALE_PATH = os.path.join(settings.BASE_DIR, "bot/assets/jsons/locale.json")


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.SlugField(blank=True, null=True, unique=True)
    first_name = models.CharField("Имя", max_length=255, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    lang = models.CharField("Язык", choices=LANGUAGES, max_length=20, default="uz")
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    last_date = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.username
    
    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'

    async def acreate_historical_record(self):
        return await sync_to_async(self.save)()
    

class Info(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField("Загаловка", max_length=255, null=True),
        text=models.TextField("Текст", null=True)
    )
    file = models.FileField("Видео или фото", upload_to="info")
    is_active = models.BooleanField("Актив", default=True)

    def __str__(self):
        return self.title or str(self.id)
    
    class Meta:
        verbose_name = 'Телеграм руководства'
        verbose_name_plural = 'Телеграм руководстви'
    

def get_text(slug, lang, **kwargs) -> str:
    with open(LOCALE_PATH, encoding="utf-8") as file:
        locale: dict[str, dict[str, str]] = json.load(file)

    for _lang, _ in LANGUAGES:
        locale[_lang].setdefault(slug, slug)
    if settings.DEBUG:
        with open(LOCALE_PATH, "w", encoding="utf-8") as file:
            json.dump(locale, file, indent=4, ensure_ascii=False)
    return locale[lang][slug].format(**kwargs)


def check_text(slug, text, lang) -> str:
    with open(LOCALE_PATH, encoding="utf-8") as file:
        locale: dict[str, dict[str, str]] = json.load(file)
    locale[lang].setdefault(slug, slug)
    test = locale[lang][slug] == text or locale[lang][slug] in re.sub(r'\([^()]*\)', '', text)[:-1]
    if test:
        return True
    texts = []
    for _, values in locale.items():
        texts.append(values.get(slug))
    return text in texts
