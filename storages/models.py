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
        name=models.CharField(max_length=255)
    )
    storage = models.ForeignKey(Storage, models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        desc=models.TextField(null=True)
    )
    currency = models.CharField(max_length=20, default="$")
    price = models.FloatField()
    category = models.ForeignKey(Category, models.CASCADE)
    is_active = models.BooleanField(default=True)
    weight = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
    @property
    def delivery_price(self):
        return self.category.storage.per_price * self.weight


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product")
    product = models.ForeignKey(Product, models.CASCADE)


class ProductToCart(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    cart = models.ForeignKey("orders.Cart", models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    @property
    def price(self):
        return self.product.price * self.count
    
    class Meta:
        unique_together = ["product", "cart"]


class ProductToChosen(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    clientid = models.ForeignKey("users.ClientId", models.CASCADE)
    