# Generated by Django 4.1.5 on 2023-12-07 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0015_remove_producttranslation_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='buyer_price',
            field=models.FloatField(null=True, verbose_name='Услуга баера'),
        ),
        migrations.AddField(
            model_name='product',
            name='transfer_fee',
            field=models.FloatField(null=True, verbose_name='Комиссия за перевод'),
        ),
    ]
