from asgiref.sync import async_to_sync, sync_to_async
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
        return f"{self.number} ({self.storage})"
    
    class Meta:
        unique_together = (("storage", "number"),)
        verbose_name = 'Партия'
        verbose_name_plural = 'Партии'

    def notificate_users(self):
        from bot.models import get_text as _
        from bot.utils import create_bot
        from bot.settings import TOKEN
        from users.models import ClientId
        from bot.handlers.online_buy.orders import _render_order
        
        for order in Order.objects.select_related("client").filter(part=self):
            client_ids = ClientId.objects.filter(storage=self.storage, selected_client=order.client, clients__in=[order.client], deleted=False, user__isnull=False).select_related("user").first()
            for client_id in client_ids:
                if not client_id.user:
                    continue
                user = client_id.user
                text = _render_order(user, order)
                bot = create_bot(TOKEN)
                async_to_sync(bot.send_message)(user.id, text)


class OrderQueryset(QuarterQuerysetMixin, models.QuerySet):
    pass


class Order(models.Model):
    part = models.ForeignKey(Part, models.CASCADE, verbose_name="Партия")
    number = models.IntegerField("Номер заказа", null=True)
    clientid = models.CharField("Клиент ИД", max_length=255, null=True)
    client = models.ForeignKey("users.Client", models.CASCADE, to_field="pnfl", verbose_name="Клиент")
    name = models.CharField("Название", max_length=255)
    weight = models.FloatField("Вес")
    facture_price = models.FloatField("Счет-актура")
    date = models.DateField("Дата", null=True)
    products = models.JSONField(default=list)
    with_online_buy = models.BooleanField(default=False)
    history = HistoricalRecords()

    @property
    def payed_price(self):
        return self.part.storage.calc(self.weight)

    objects: OrderQueryset = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Закази'


class Cart(models.Model):
    clientid = models.OneToOneField("users.ClientId", models.CASCADE, verbose_name="Клиент ИД")
    part = models.ForeignKey(Part, models.CASCADE, null=True)

    def __str__(self) -> str:
        return str(self.clientid)

    @property
    def price(self):
        return round(sum([ptc.price for ptc in self.producttocart_set.select_related("product").all()]), 2)
    
    async def aprice(self):
        return round(sum([ptc.price async for ptc in self.producttocart_set.select_related("product").all()]), 2)

    async def aproducts(self):
        return self.producttocart_set.select_related("product").all()
    
    def render_products(self):
        qs = self._annotated_qs()
        return [
            {
                "name": str(pc.product.name),
                "desc": str(pc.product.name),
                "currency": str(pc.product.currency),
                "price": float(pc.product.price),
                "category": str(pc.product.category),
                "weight": float(pc.product.weight),
                "all_weight": float(pc.weight),
                "facture_price": float(pc.facture_price)
            } for pc in qs
        ]
    
    def _annotated_qs(self):
        return self.producttocart_set.all().annotate(
            weight=models.F("count") * models.F("product__weight"),
            # price=models.F("weight") * models.F("product__category__storage__per_price"),
            facture_price=models.F("count") * models.F("product__price"),
        )
    
    def create_order(self):
        qs = self._annotated_qs()
        name = ", ".join([f"{pc.product} {pc.count} шт." for pc in qs])
        products = self.render_products()
        number = Order.objects.filter(part__storage=self.part.storage).order_by("number").last()
        number = 1 if not number else number.number + 1
        order = Order.objects.create(
            number=number,
            part=self.part,
            clientid=str(self.clientid),
            client=self.clientid.selected_client,
            name=name,
            **qs.aggregate(facture_price=models.Sum(models.F("count") * models.F("product__price")), weight=models.Sum("weight")),
            products=products,
            with_online_buy=True
        )
        self.delete()
        return order
    
    async def acreate_order(self, part: Part):
        return await sync_to_async(self.create_order)(part=part)
    
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
