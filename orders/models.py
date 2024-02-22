import asyncio
from collections import defaultdict

from asgiref.sync import sync_to_async
from django.db import models
from simple_history.models import HistoricalRecords

from admin_async_upload.models import AsyncFileField
from contrib.django.queryset import QuarterQuerysetMixin

LIMIT_FOR_QUARTER = 950

IN_FIRST_AEROPORT = "in_first"
IN_SECOND_AEROPORT = "in_second"
IN_CUSTOMS = "in_customs"
IN_DELIVERY = "in_delivery"
PART_STATUS = (
    (IN_FIRST_AEROPORT, "В аэропорту отправителя"),
    (IN_SECOND_AEROPORT, "В аэропорту принимателя"),
    (IN_CUSTOMS, "в Таможенном процессе"),
    (IN_DELIVERY, "в доставке")
)

class Part(models.Model):
    number = models.IntegerField("Номер")
    storage = models.ForeignKey("storages.Storage", models.CASCADE, verbose_name="Склад")
    status = models.CharField("Статус", max_length=50, default=IN_FIRST_AEROPORT, choices=PART_STATUS)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.number} ({self.storage})"
    
    class Meta:
        unique_together = (("storage", "number"),)
        verbose_name = 'Партия'
        verbose_name_plural = 'Партии'

    def notificate_users(self):
        import asyncio

        from bot.handlers.online_buy.orders import _render_order
        from bot.models import get_text as _
        from bot.settings import TOKEN
        from bot.utils import create_bot
        from users.models import ClientId
        
        bot = create_bot(TOKEN)
        count = 0
        async def theard_main(count):
            async for order in Order.objects.select_related("client", "part", "part__storage").filter(part=self):
                client_ids = ClientId.objects.select_related("user").filter(storage=self.storage, selected_client=order.client, clients__in=[order.client], deleted=False, user__isnull=False).select_related("user")
                async for client_id in client_ids:
                    if not client_id.user:
                        continue
                    user = client_id.user
                    text = await _render_order(user, order, True)
                    try:
                        await bot.send_message(user.id, text)
                        count += 1
                    except Exception as _exp:
                        print(_exp)
            return count
        count = asyncio.run(theard_main(count))
        return count


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
    with_online_buy = models.BooleanField(default=False, verbose_name="С онлайн магазина")
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
    
    def render_cart(self, lang):
        from bot.models import get_text as _
        text = [f"{_('client_id', lang)}: <code>{self.clientid.get_id()}</code>"]
        summa = defaultdict(int)
        has_not_given = False
        for pc in self._annotated_qs():
            if pc.price:
                pc_summa = round((pc.price + pc.product.buyer_price) * (1 + pc.product.transfer_fee * 0.01), 2)
                summa[pc.product.currency] += pc_summa
            else:
                pc_summa = round((pc.product.buyer_price) * (1 + pc.product.transfer_fee * 0.01), 2)
                has_not_given = True
            text.append(pc.product.product_to_text(lang, pc.count))
        cart_itog = [f"{_('cart_itog', lang)}: "]
        for sc, s in summa.items():
            cart_itog.append(f"{round(s, 2)} {sc}")
        if has_not_given:
            cart_itog.append(_("not_given_prices_in_cart", lang))
        cart_itog = "\n".join(cart_itog)
        text.append("\n")
        text.append(cart_itog)
        return "\n".join(text)
    
    async def arender_cart(self, lang):
        return await sync_to_async(self.render_cart)(lang=lang)
    
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
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self) -> str:
        return str(self.clientid)

    class Meta:
        verbose_name = 'Фото отчет'
        verbose_name_plural = 'Фото отчеты'

    def send_notification(self):
        from bot.handlers.reports import _render_report
        from bot.models import get_text as _
        from bot.settings import TOKEN
        from bot.utils import create_bot

        user = self.clientid.user
        if not user:
            return
        photo = _render_report(self)
        bot = create_bot(TOKEN)
        asyncio.run(bot.send_media_group(chat_id=user.id, media=photo))


class ReportImage(models.Model):
    report = models.ForeignKey(Report, models.CASCADE)
    image = AsyncFileField(upload_to="report", verbose_name="Фото")

    def __str__(self) -> str:
        return str(self.report)
