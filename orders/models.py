from asgiref.sync import async_to_sync
from django.db import models
from contrib.django.queryset import QuarterQuerysetMixin
from simple_history.models import HistoricalRecords


LIMIT_FOR_QUARTER = 950

IN_STORAGE = "in_storage"
IN_DELIVERY = "in_delivery"
DONE = "done"
PART_STATUS = (
    (IN_STORAGE, "В складе"),
    (IN_DELIVERY, "Доставка"),
    (DONE, "Доставлено")
)

class Part(models.Model):
    number = models.IntegerField("Номер")
    storage = models.ForeignKey("storages.Storage", models.CASCADE, verbose_name="Склад")
    status = models.CharField("Статус", max_length=50, default=IN_STORAGE, choices=PART_STATUS)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return str(self.number)
    
    class Meta:
        unique_together = (("storage", "number"),)
        verbose_name = 'Партия'
        verbose_name_plural = 'Партии'

    def notificate_users(self):
        from bot.models import get_text as _
        from bot.utils import create_bot
        from bot.settings import TOKEN
        from users.models import ClientId

        for order in Order.objects.select_related("client").filter(part=self):
            client_id = ClientId.objects.filter(storage=self.storage, selected_client=order.client, clients__in=[order.client], deleted=False, user__isnull=False).select_related("user").first()
            if not client_id or not client_id.user:
                continue
            user = client_id.user
            text = f"""
{_('part', user.lang)}: {self.number}
{_('order_number', user.lang)}: {order.number}
{_('client_id', user.lang)}: {order.clientid}
{_('client', user.lang)}: {order.client}
{_('passport', user.lang)}: {order.client.passport}
{_('order_name', user.lang)}: {order.name}
{_('order_weight', user.lang)}: {order.weight} {_('kg', user.lang)}
{_('order_facture_price', user.lang)}: {order.facture_price} $
{_('order_price', user.lang)}: {order.payed_price} $
{_('order_status', user.lang)}: {_(f'order_status_{self.status}', user.lang)}
            """
            bot = create_bot(TOKEN)
            async_to_sync(bot.send_message)(user.id, text)


class OrderQueryset(QuarterQuerysetMixin, models.QuerySet):
    pass


class Order(models.Model):
    part = models.ForeignKey(Part, models.CASCADE, verbose_name="Партия")
    number = models.IntegerField("Номер заказа", unique=True)
    clientid = models.CharField("Клиент ИД", max_length=255, null=True)
    client = models.ForeignKey("users.Client", models.CASCADE, to_field="pnfl", verbose_name="Клиент")
    name = models.CharField("Название", max_length=255)
    weight = models.FloatField("Вес")
    facture_price = models.FloatField("Счет-актура")
    date = models.DateField("Дата", null=True)
    history = HistoricalRecords()

    @property
    def payed_price(self):
        return round(self.weight * self.part.storage.per_price, 2)

    objects: OrderQueryset = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Закази'


class Cart(models.Model):
    clientid = models.OneToOneField("users.ClientId", models.CASCADE, verbose_name="Клиент ИД")

    def __str__(self) -> str:
        return str(self.clientid)

    @property
    def price(self):
        return round(sum([ptc.price for ptc in self.producttocart_set.select_related("product").all()]), 2)
    
    async def aprice(self):
        return round(sum([ptc.price async for ptc in self.producttocart_set.select_related("product").all()]), 2)

    async def aproducts(self):
        return self.producttocart_set.select_related("product").all()
    
    class Meta:
        verbose_name = 'Карзина клиента'
        verbose_name_plural = 'Карзина клиента'
    

class Report(models.Model):
    clientid = models.ForeignKey("users.ClientId", models.CASCADE, verbose_name="Клиент ИД")
    image = models.ImageField(upload_to="report", verbose_name="Фото")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self) -> str:
        return str(self.clientid)

    class Meta:
        verbose_name = 'Фото отчет'
        verbose_name_plural = 'Фото отчеты'

    def send_notification(self):
        from threading import Thread
        from bot.models import get_text as _
        from bot.utils import create_bot
        from bot.settings import TOKEN
        from bot.handlers.reports import _render_report

        user = self.clientid.user
        if not user:
            return
        text, photo = _render_report(self)
        bot = create_bot(TOKEN)
        
        def main():
            async_to_sync(bot.send_photo)(chat_id=user.id, photo=photo, caption=text)
        Thread(target=main).start()
