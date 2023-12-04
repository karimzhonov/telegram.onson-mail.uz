import json, os, re
from threading import Thread
from asgiref.sync import sync_to_async, async_to_sync
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
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
        return f"{self.username} ({self.id})"
    
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


def slug_from_text(text, lang):
    with open(LOCALE_PATH, encoding="utf-8") as file:
        locale: dict[str, dict[str, str]] = json.load(file)
    for slug in locale[lang].keys():
        test = locale[lang][slug] == text or locale[lang][slug] in re.sub(r'\([^()]*\)', '', text)[:-1]
        if test:
            return slug
    raise ValueError(slug)


FAQ_TYPE_BOT = "faq_type_bot"
FAQ_TYPE_DELIVERY = "faq_type_delivery"

FAQ_TYPES = (
    (FAQ_TYPE_BOT, "Botda nosozlik"),
    (FAQ_TYPE_DELIVERY, "Yetkazib berishda nosozlik")
)


class FAQ(models.Model):
    text = models.TextField()
    type = models.CharField(max_length=255, choices=FAQ_TYPES)
    user = models.ForeignKey(User, models.CASCADE)
    answer = models.TextField(null=True)
    answer_user = models.ForeignKey(get_user_model(), models.CASCADE, null=True)
    not_active = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True, upload_to="faq")
    answer_image = models.ImageField(upload_to="faq_answer", blank=True, null=True)
    message_id = models.IntegerField(null=True)

    def __str__(self) -> str:
        return self.text

    async def save_image(self, content):
        return await sync_to_async(self.image.save)(f"{self.user_id}.png", content, True)

    def send_message(self):
        from aiogram import types
        from bot.models import get_text as _
        from bot.utils import create_bot
        from bot.settings import TOKEN
        
        bot = create_bot(TOKEN)
        answered = []
        if self.answer_user.first_name:
            answered.append(self.answer_user.first_name)
        if self.answer_user.last_name:
            answered.append(self.answer_user.last_name)
        if len(answered) == 0:
            answered.append(self.answer_user.username)
        answered = " ".join(answered)
        text = f"""
{answered}: {self.answer}
        """
        def main():
            if self.answer_image:
                file_path = os.path.join(settings.BASE_DIR, "media", str(self.answer_image))
                media = types.BufferedInputFile.from_file(file_path)
                return async_to_sync(bot.send_photo)(self.user_id, media, caption=text, reply_to_message_id=self.message_id)
            else:
                return async_to_sync(bot.send_message)(self.user_id, text=text, reply_to_message_id=self.message_id)
        Thread(target=main).start()
