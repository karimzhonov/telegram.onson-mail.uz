from django.contrib import admin

from .models import Part, Order

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_filter = ["storage"]
    list_display = ["number", "storage"]
    actions = ['send_notification']

    @admin.action(description="Отправка уведомления")
    def send_notification(self, request, queryset):
        for part in queryset:
            part.notificate_users()
        

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["number", "part", "client_id", "client", "name", "weight", "facture_price", "payed_price"]
    list_filter = ["part", "part__storage", "client"]
