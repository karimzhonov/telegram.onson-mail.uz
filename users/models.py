from django.db import models
from bot.models import get_text as _
from asgiref.sync import sync_to_async
from simple_history.models import HistoricalRecords


class Client(models.Model):
    pnfl = models.CharField('ПИНФЛ', max_length=255, unique=True)
    passport = models.CharField('Паспорт серия и номер', max_length=255, unique=True)
    fio = models.CharField('ФИО', max_length=255)
    phone = models.CharField('Номер телефона', max_length=255, null=True)
    passport_image = models.ImageField('Паспорт фото', upload_to="passport-image", null=True)
    address = models.CharField('Адрес', max_length=255, null=True)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.fio
    
    class Meta:
        verbose_name = 'Паспорт клиента'
        verbose_name_plural = 'Паспорта клиентов'
    
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
    storage = models.ForeignKey("storages.Storage", models.CASCADE, verbose_name="Склад")
    selected_client = models.ForeignKey(Client, models.CASCADE, null=True, blank=True, related_name="selected_client", verbose_name="Выбранный клиент")
    user = models.ForeignKey("bot.User", models.CASCADE, null=True, verbose_name="Телеграм пользователь")
    clients = models.ManyToManyField(Client, verbose_name="Поспорта клиентов")
    id_str = models.CharField(verbose_name="ИД", max_length=255, unique=True, blank=True, null=True)
    deleted = models.BooleanField(verbose_name="Не автивный", default=False)
    create_date = models.DateField(auto_now_add=True)
    
    history = HistoricalRecords()

    def get_id(self):
        if self.id_str:
            return self.id_str
        return f"{self.storage.slug}-{self.id}"
    get_id.short_description = "ID"
    
    class Meta:
        unique_together = (("storage", "selected_client", "user"),)
        verbose_name = 'ИД клиента'
        verbose_name_plural = 'ИД клиентов'


    async def aadd_client(self, *args: list[Client]):
        return await sync_to_async(self.clients.add)(*args)
    
    async def aremove_client(self, *args: list[Client]):
        return await sync_to_async(self.clients.remove)(*args)
    
