from django.contrib.gis import admin
from parler.admin import TranslatableAdmin
from .models import Storage, Image


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Storage)
class StorageAdmin(TranslatableAdmin):
    pass
