from django.contrib.gis import admin
from admincharts.admin import AdminChartMixin
from contrib.parler.admin import TranslatableAdmin
from orders.models import Order
from .models import Storage, Image, Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Storage)
class StorageAdmin(AdminChartMixin, TranslatableAdmin):
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

    list_chart_type = "bar"
    list_chart_options = {"responsive": True, "indexAxis": 'y',}

    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [],
        }
        totals = []
        create_qs = Storage.objects.translated("ru").all()
        
        for data in create_qs:
            totals.append({"y": data.name, "x": Order.objects.filter(part__storage=data).count()})
        datasets["datasets"].append({"label": "Кол-во заказов", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    pass


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductImageInline]
