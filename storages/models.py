from django.contrib.gis.db import models
from django.db.models.expressions import RawSQL
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from parler.managers import ImproperlyConfigured, TranslatableManager, TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFields


class Storage(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField("Название", max_length=255, null=True),
        address=models.TextField("Адрес", null=True, blank=True),
        text=models.TextField("Текст", null=True, blank=True)
    )
    slug = models.SlugField("Ключовая слова", unique=True)
    phone = models.CharField("Номер телефона", max_length=255, null=True)
    is_active = models.BooleanField("Актив", default=True)
    per_price = models.FloatField(default=5.5)
    has_online_buy = models.BooleanField(default=False, verbose_name="Есть онлайн магазин")
    my_order = models.IntegerField(default=0,
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return self.slug
    
    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склади'
        ordering = ['my_order']

    def calc(self, weight: float):
        if weight <= 1:
            return round(self.per_price, 2)
        return round(self.per_price * weight, 2)
    

class Image(models.Model):
    image = models.ImageField("Фото")
    storage = models.ForeignKey(Storage, models.CASCADE, verbose_name="Склад")

    class Meta:
        verbose_name = 'Фото склада'
        verbose_name_plural = 'Фотки склада'


class CategoryQueryset(TranslatableQuerySet):
    
    @staticmethod
    def _find_foreign_field_name(from_model, to_field_model):
        for key, value in from_model.__dict__.items():
            if isinstance(value, ForwardManyToOneDescriptor):
                if to_field_model == value.field.remote_field.model:
                    return key
        assert False, f"Invalid  '{from_model.__name__}' model. " \
                    f"Can not find foregin field to {to_field_model.__name__}"

    def filter_recursive(self, **kwargs):
        fields = [self._find_foreign_field_name(self.model, self.model)]
        table = f'{self.model._meta.app_label}_{self.model.__name__.lower()}'
        sql, params = self.filter(**kwargs).values('id').query.sql_with_params()
        params = tuple([f"'{p}'" if isinstance(p, str) else p for p in params])
        return self.filter(id__in=RawSQL(
            f"""
            WITH RECURSIVE r AS (
                SELECT id, parent_id
                FROM {table}
                WHERE id IN ({sql % params})
                UNION ALL
                SELECT {table}.id, {table}.parent_id
                FROM {table}
                     JOIN r
                          ON {' OR '.join([f'{table}.{field}_id = r.id' for field in fields])}
            )
            SELECT id FROM r""", ()
        ))


class CategoryManager(models.Manager.from_queryset(CategoryQueryset)):
    """
    The manager class which ensures the enhanced TranslatableQuerySet object is used.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        if not isinstance(qs, TranslatableQuerySet):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}._queryset_class does not inherit from TranslatableQuerySet"
            )
        return qs


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name="Название")
    )
    parent = models.ForeignKey("self", models.CASCADE, null=True, blank=True, verbose_name="Радительская категория")
    is_active = models.BooleanField(default=True, verbose_name="Актив")

    def __str__(self) -> str:
        return self.name if not self.parent else f"{self.name}->{self.parent}"
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    objects = CategoryManager()


class Product(models.Model):
    storage = models.ForeignKey(Storage, models.CASCADE, null=True, verbose_name="Склад")
    name=models.CharField(max_length=255, verbose_name="Название", null=True)
    currency = models.CharField(max_length=20, default="$", verbose_name="Валюта")
    price = models.FloatField(verbose_name="Цена", null=True, blank=True)
    price_many = models.FloatField(verbose_name="Цена оптом", null=True, blank=True)
    count_many = models.IntegerField(verbose_name="Оптом кол-во", null=True, blank=True)
    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория")
    is_active = models.BooleanField(default=True, verbose_name="Актив")
    weight = models.FloatField(verbose_name="Вес", null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создание")
    transfer_fee = models.FloatField("Комиссия за перевод (%)", null=True)
    buyer_price = models.FloatField("Услуга баера", null=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self) -> str:
        return str(self.name)
    
    @property
    def delivery_price(self):
        return self.category.storage.calc(self.weight)
    
    def product_to_text(self, lang, count=1):
        from bot.models import get_text as _
        if count == 1:
            return f"""
{_("product_name", lang)}: {self.name}
{_("product_category", lang)}: {self.category.name}
{_("product_weight", lang)}: {self.weight if self.weight else _("not_given", lang)}
{_("product_price", lang)}: {self.price if self.price else _("not_given", lang)} {self.currency if self.price else ""}
{_("product_price_many", lang, count=self.count_many)}: {self.price_many if self.price_many else _("not_given", lang)} {self.currency if self.price_many else ""}
{_("product_transfer_fee", lang)}: {self.transfer_fee} %
{_("product_buyer_price", lang)}: {self.buyer_price} {self.currency}"""
        if not self.count_many:
            price = self.price
        else:
            price = self.price_many if count >= self.count_many else self.price
            if not price:
                price = self.price
        return f"""
{_("product_name", lang)}: {self.name}
{_("product_category", lang)}: {self.category.name}
{_("product_weight", lang)}: {f'{self.weight} x {count} = {self.weight * count}' if self.weight else _("not_given", lang)}
{_("product_price", lang)}: {f'{price} {self.currency} x {count} = {price * count} {self.currency}' if price else _("not_given", lang)}
{_("product_transfer_fee", lang)}: {self.transfer_fee} %
{_("product_buyer_price", lang)}: {self.buyer_price} {self.currency}"""


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product", verbose_name="Фото")
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")


class ProductToCart(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")
    cart = models.ForeignKey("orders.Cart", models.CASCADE, verbose_name="Карзина")
    count = models.PositiveIntegerField(default=1, verbose_name="Кол-во")

    @property
    def price(self):
        if not self.product.count_many:
            price = self.product.price
        else:
            price = self.product.price if self.product.count_many > self.count else self.product.price_many
            if not price:
                price = self.product.price
        return round(price * self.count, 2) if price else None
    
    class Meta:
        unique_together = ["product", "cart"]


class ProductToChosen(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")
    clientid = models.ForeignKey("users.ClientId", models.CASCADE, verbose_name="Клиент ИД")
    