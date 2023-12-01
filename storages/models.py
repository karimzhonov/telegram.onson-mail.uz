from django.contrib.gis.db import models
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
    has_online_buy = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.slug
    
    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склади'
    

class Image(models.Model):
    image = models.ImageField("Фото")
    storage = models.ForeignKey(Storage, models.CASCADE, verbose_name="Склад")

    class Meta:
        verbose_name = 'Фото склада'
        verbose_name_plural = 'Фотки склада'


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name="Название")
    )
    storage = models.ForeignKey(Storage, models.CASCADE, verbose_name="Склад")
    is_active = models.BooleanField(default=True, verbose_name="Актив")

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name="Название")
    )
    currency = models.CharField(max_length=20, default="$", verbose_name="Валюта")
    price = models.FloatField(verbose_name="Цена")
    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория")
    is_active = models.BooleanField(default=True, verbose_name="Актив")
    weight = models.FloatField(verbose_name="Вес")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создание")

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self) -> str:
        return self.name
    
    @property
    def delivery_price(self):
        return round(self.category.storage.per_price * self.weight, 2)


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product", verbose_name="Фото")
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")


class ProductToCart(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")
    cart = models.ForeignKey("orders.Cart", models.CASCADE, verbose_name="Карзина")
    count = models.PositiveIntegerField(default=1, verbose_name="Кол-во")

    @property
    def price(self):
        return round(self.product.price * self.count, 2)
    
    class Meta:
        unique_together = ["product", "cart"]


class ProductToChosen(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Продукт")
    clientid = models.ForeignKey("users.ClientId", models.CASCADE, verbose_name="Клиент ИД")
    