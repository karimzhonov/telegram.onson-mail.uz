# Generated by Django 4.1.5 on 2023-11-30 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_alter_cart_options_alter_report_options_and_more'),
        ('users', '0017_client_create_date_clientid_create_date_and_more'),
        ('storages', '0013_storage_has_online_buy'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='categorytranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Категория Translation'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterModelOptions(
            name='producttranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Продукт Translation'},
        ),
        migrations.AlterField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Актив'),
        ),
        migrations.AlterField(
            model_name='category',
            name='storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.storage', verbose_name='Склад'),
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.category', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.CharField(default='$', max_length=20, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Актив'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(verbose_name='Вес'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to='product', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.product', verbose_name='Продукт'),
        ),
        migrations.AlterField(
            model_name='producttocart',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.cart', verbose_name='Карзина'),
        ),
        migrations.AlterField(
            model_name='producttocart',
            name='count',
            field=models.PositiveIntegerField(default=1, verbose_name='Кол-во'),
        ),
        migrations.AlterField(
            model_name='producttocart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.product', verbose_name='Продукт'),
        ),
        migrations.AlterField(
            model_name='producttochosen',
            name='clientid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.clientid', verbose_name='Клиент ИД'),
        ),
        migrations.AlterField(
            model_name='producttochosen',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.product', verbose_name='Продукт'),
        ),
        migrations.AlterField(
            model_name='producttranslation',
            name='desc',
            field=models.TextField(null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='producttranslation',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
    ]
