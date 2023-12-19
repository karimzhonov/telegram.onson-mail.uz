from typing import Sequence

from admincharts.admin import AdminChartMixin
from adminsortable2.admin import SortableAdminMixin
from django.contrib.gis import admin
from django.http.request import HttpRequest

from contrib.parler.admin import TranslatableAdmin
from orders.models import Order
from users.models import get_storages

from .forms import ProductForm
from .models import Category, Image, Product, ProductImage, Storage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Storage)
class StorageAdmin(SortableAdminMixin, AdminChartMixin, TranslatableAdmin):
    inlines = [ImageInline]
    non_editable_fields = ['slug']
    list_chart_type = "bar"
    ordering = ["my_order"]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return storages
    
    def get_list_chart_queryset(self, changelist):
        return changelist.queryset
    
    def get_list_chart_options(self, queryset):
        return {"aspectRatio": 1 / queryset.count() * 10, "responsive": True, "indexAxis": 'y'}
    
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

    def get_list_chart_data(self, queryset):
        datasets = {
            "datasets": [],
        }
        totals = []
        create_qs = queryset
        
        for data in create_qs:
            totals.append({"y": data.name, "x": Order.objects.filter(part__storage=data).count()})
        datasets["datasets"].append({"label": "Кол-во заказов", "data": totals, "backgroundColor": "red", "borderColor": "red"})
        return datasets


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    search_fields = ["translations__name"]
    list_display = ["name", "parent"]

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        if request.user.is_superuser:
            return super().get_list_filter(request)
        return []


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ["name", "category"]
    search_fields = ["translations__name", "category__translations__name"]
    form = ProductForm

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        storages = get_storages(request.user)
        return super().get_queryset(request).filter(storage__in=storages)
