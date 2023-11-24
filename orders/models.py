from asgiref.sync import async_to_sync
from django.db import models
from contrib.django.queryset import QuarterQuerysetMixin
from simple_history.models import HistoricalRecords

PRICE_PER_KG = 5.5
LIMIT_FOR_QUARTER = 1000

IN_STORAGE = "in_storage"
IN_DELIVERY = "in_delivery"
DONE = "done"
PART_STATUS = (
    (IN_STORAGE, "В складе"),
    (IN_DELIVERY, "Доставка"),
    (DONE, "Доставлено")
)

class Part(models.Model):
    number = models.IntegerField("Номер", unique=True)
    storage = models.ForeignKey("storages.Storage", models.CASCADE, verbose_name="Склад")
    status = models.CharField("Статус", max_length=50, default=IN_STORAGE, choices=PART_STATUS)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return str(self.number)
    
    class Meta:
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
    number = models.IntegerField("Номер заказа")
    clientid = models.CharField("Клиент ИД", max_length=255, null=True)
    client = models.ForeignKey("users.Client", models.CASCADE, to_field="pnfl", verbose_name="Клиент")
    name = models.CharField("Название", max_length=255)
    weight = models.FloatField("Вес")
    facture_price = models.FloatField("Счет-актура")
    date = models.DateField("Дата", null=True)
    history = HistoricalRecords()

    @property
    def payed_price(self):
        return self.weight * PRICE_PER_KG

    objects: OrderQueryset = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Закази'
