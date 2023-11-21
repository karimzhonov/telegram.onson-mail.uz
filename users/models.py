from django.db import models
from bot.models import get_text as _


class Client(models.Model):
    pnfl = models.CharField(max_length=255)
    passport = models.CharField(max_length=255)
    fio = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.fio
    