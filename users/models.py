from django.db import models
from bot.models import get_text as _
from asgiref.sync import sync_to_async


class Client(models.Model):
    pnfl = models.CharField(max_length=255, unique=True)
    passport = models.CharField(max_length=255, unique=True)
    fio = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True)
    passport_image = models.ImageField(upload_to="passport-image", null=True)
    address = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.fio
    
    async def save_passport_image(self, content):
        return await sync_to_async(self.passport_image.save)(f"{self.fio}.png", content, True)
    
    def order_quarters(self):
        from orders.models import Order

        return Order.objects.filter(client=self).quarter("date", "facture_price")
    
    def is_warning(self):
        from orders.models import LIMIT_FOR_QUARTER
        last_quarter = self.order_quarters().order_by("quarter").last()
        if not last_quarter:
            return False
        return last_quarter["value"] >= LIMIT_FOR_QUARTER
    
    async def ais_warning(self):
        return await sync_to_async(self.is_warning)()


class ClientId(models.Model):
    storage = models.ForeignKey("storages.Storage", models.CASCADE)
    selected_client = models.ForeignKey(Client, models.CASCADE, null=True, blank=True, related_name="selected_client")
    user = models.ForeignKey("bot.User", models.CASCADE, null=True)
    clients = models.ManyToManyField(Client)
    id_str = models.CharField(max_length=255, unique=True, blank=True, null=True)
    deleted = models.BooleanField(default=False)

    def get_id(self):
        if self.id_str:
            return self.id_str
        return f"{self.storage}-{self.id}"
    
    class Meta:
        unique_together = (("storage", "selected_client", "user"),)


    async def aadd_client(self, *args: list[Client]):
        return await sync_to_async(self.clients.add)(*args)
    
    async def aremove_client(self, *args: list[Client]):
        return await sync_to_async(self.clients.remove)(*args)
    
