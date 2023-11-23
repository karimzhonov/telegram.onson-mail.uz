from django.contrib.gis.db import models
from parler.models import TranslatableModel, TranslatedFields

class Storage(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, null=True),
        address=models.TextField(null=True, blank=True),
        text=models.TextField(null=True, blank=True)
    )
    slug = models.SlugField(unique=True)
    phone = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.slug
    

class Image(models.Model):
    image = models.ImageField()
    storage = models.ForeignKey(Storage, models.CASCADE)
