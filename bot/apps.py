from django.apps import AppConfig
from django.utils import timezone
from django.conf import settings


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    verbose_name = 'Телеграм бот'

    def ready(self) -> None:
        timezone.activate(settings.TIME_ZONE)
