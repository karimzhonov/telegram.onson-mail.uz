from django.contrib.gis import admin
from contrib.parler.admin import TranslatableAdmin
from .models import Storage, Image, Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Storage)
class StorageAdmin(TranslatableAdmin):
    inlines = [ImageInline]
    non_editable_fields = ['slug']
    
    def get_exclude(self, request, obj=None):
        defaults = super().get_exclude(request, obj=obj) or ()
        if obj: # if we are updating an object
            defaults = (*defaults, *self.non_editable_fields)
        return defaults or None

    def get_fields(self, request, obj=None):
        defaults = super().get_fields(request, obj=obj)
        if obj: # if we are updating an object
            defaults = tuple(f for f in defaults if f not in self.non_editable_fields)
        return defaults


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    pass


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductImageInline]
