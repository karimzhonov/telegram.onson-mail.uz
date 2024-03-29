import asyncio
import json
import os
import re
from typing import Any, Dict, Iterable, Optional, Tuple

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from parler.models import TranslatableModel, TranslatedFields
from simple_history.models import HistoricalRecords

from app.settings import LANGUAGES
from bot.utils import get_file

LOCALE_PATH = os.path.join(settings.BASE_DIR, "bot/assets/jsons/locale.json")


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    username = models.SlugField(blank=True, null=True, unique=True, max_length=255)
    first_name = models.CharField("Имя", max_length=255, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    lang = models.CharField("Язык", choices=LANGUAGES, max_length=20, default="uz")
    create_date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создание")
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
        title=models.CharField("Загаловка", max_length=255, null=True, unique=True),
        text=models.TextField("Текст", null=True)
    )
    file = models.ImageField("Фото", upload_to="info", null=True, blank=True)
    is_active = models.BooleanField("Актив", default=True)
    url = models.URLField("Ссылка", blank=True, null=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.title or str(self.id)
    
    class Meta:
        verbose_name = 'Телеграм руководства'
        verbose_name_plural = 'Телеграм руководстви'

    def send_notification(self):
        from bot.handlers.start import _render_info
        from bot.settings import TOKEN
        from bot.utils import create_bot
        bot = create_bot(TOKEN)
        count = 0
        async def theard_main(count):
            async for user in User.objects.all():
                if await self.users.filter(id=user.id).aexists():
                    continue
                await sync_to_async(self.users.add)(user)
                try:
                    text, file, method = await sync_to_async(_render_info)(self)
                    if method == "answer_photo":
                        await bot.send_photo(user.id, photo=file, caption=text)
                    elif method == "answer":
                        await bot.send_message(user.id, text)
                    count += 1
                except Exception as exp:
                    print(exp)
            return count
        count = asyncio.run(theard_main(count))
        return count


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
    text = models.TextField(verbose_name="Вапрос")
    type = models.CharField(verbose_name="Тип", max_length=255, choices=FAQ_TYPES)
    user = models.ForeignKey(User, models.CASCADE, verbose_name="Владелец вопроса")
    answer = models.TextField(null=True, verbose_name="Ответ", blank=True)
    answer_user = models.ForeignKey(get_user_model(), models.CASCADE, null=True, verbose_name="Ответил")
    not_active = models.BooleanField(default=False, verbose_name="Ответено")
    image = models.ImageField(null=True, blank=True, upload_to="faq", verbose_name="Фото вапроса")
    answer_image = models.ImageField(upload_to="faq_answer", blank=True, null=True, verbose_name="Фото ответа")
    message_id = models.BigIntegerField(null=True)
    storage = models.ForeignKey("storages.Storage", models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.text

    async def save_image(self, content):
        return await sync_to_async(self.image.save)(f"{self.user_id}.png", content, True)

    def send_message(self):
        from bot.models import get_text as _
        from bot.settings import TOKEN
        from bot.utils import create_bot
        
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
        async def main():
            if self.answer_image:
                media = get_file(str(self.answer_image))
                return await bot.send_photo(self.user_id, media, caption=text, reply_to_message_id=self.message_id)
            else:
                return await bot.send_message(self.user_id, text=text, reply_to_message_id=self.message_id)
        asyncio.run(main())


class Message(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="message", verbose_name="Фото")
    date = models.DateTimeField(auto_now_add=True)
    message_id = models.BigIntegerField(null=True)
    sender_user = models.ForeignKey(get_user_model(), models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщении'
    
    def __str__(self) -> str:
        return self.text
    
    def send_message(self, user=None):
        from bot.models import get_text as _
        from bot.settings import TOKEN
        from bot.utils import create_bot
        
        bot = create_bot(TOKEN)
        text = self.text
        async def main():
            if self.image:
                media = get_file(str(self.image))
                return await bot.send_photo(self.user_id, media, caption=text)
            else:
                return await bot.send_message(self.user_id, text=text)
        message = asyncio.run(main())
        self.message_id = message.message_id
        self.sender_user = user
        self.save()

    def delete(self, using=None, keep_parents=False) -> Tuple[int, Dict[str, int]]:
        from bot.models import get_text as _
        from bot.settings import TOKEN
        from bot.utils import create_bot

        if self.message_id:
            bot = create_bot(TOKEN)
            async def main():
                return await bot.delete_message(self.user_id, self.message_id)
                
            asyncio.run(main())
        return super().delete(using, keep_parents)
