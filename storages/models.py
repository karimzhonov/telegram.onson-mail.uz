from django.contrib.gis.db import models
from parler.models import TranslatableModel, TranslatedFields


class Storage(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField("Название", max_length=255, null=True),
        address=models.TextField("Адрес", null=True, blank=True),
        text=models.TextField("Текст", null=True, blank=True)
    )
    slug = models.SlugField("Ключовая слова", unique=True)
    phone = models.CharField("Номер телефона", max_length=255, null=True)
    is_active = models.BooleanField("Актив", default=True)
    per_price = models.FloatField(default=5.5)

    def __str__(self) -> str:
        return self.slug
    
    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склади'
    

class Image(models.Model):
    image = models.ImageField("Фото")
    storage = models.ForeignKey(Storage, models.CASCADE, verbose_name="Склад")

    class Meta:
        verbose_name = 'Фото склада'
        verbose_name_plural = 'Фотки склада'
