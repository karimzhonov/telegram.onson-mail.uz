from django.db import models

LANGUAGES = (
    ("ru", "Русский"),
    ("uz", "O'zbekcha"),
    ("uz_cl", "Узбекча"),
)

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.SlugField(blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    lang = models.CharField(choices=LANGUAGES, max_length=20, default="uz")

    def __str__(self) -> str:
        return self.username
    

class Info(models.Model):
    slug = models.SlugField(unique=True)
    file = models.FileField(upload_to="info")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.slug


class Text(models.Model):
    slug = models.SlugField()
    text = models.TextField()
    lang = models.CharField(choices=LANGUAGES, max_length=20)

    def __str__(self) -> str:
        return self.text
    
    class Meta:
        unique_together = (("slug", "lang"),)
    

def get_text(slug, lang, **kwargs):
    try:
        text = Text.objects.get(slug=slug, lang=lang)
    except Text.DoesNotExist:
        text = Text.objects.create(slug=slug, lang=lang, text=slug)
    return text.text.format(**kwargs)

async def aget_text(slug, lang, **kwargs):
    try:
        text = await Text.objects.aget(slug=slug, lang=lang)
    except Text.DoesNotExist:
        text = await Text.objects.acreate(slug=slug, lang=lang, text=slug)
    return text.text.format(**kwargs)
