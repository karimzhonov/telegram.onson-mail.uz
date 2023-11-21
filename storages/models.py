from django.contrib.gis.db import models


class Storage(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(default="", blank=True, null=True)
    point = models.PointField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    

class Image(models.Model):
    image = models.ImageField()
    storage = models.ForeignKey(Storage, models.CASCADE)

