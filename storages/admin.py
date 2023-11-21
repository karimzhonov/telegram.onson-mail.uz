from django.contrib.gis import admin
from .models import Storage, Image


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Storage)
class StorageAdmin(admin.OSMGeoAdmin):
    pass
