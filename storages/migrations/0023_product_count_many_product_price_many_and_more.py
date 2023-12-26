# Generated by Django 4.1.5 on 2023-12-26 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0022_alter_storage_my_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='count_many',
            field=models.IntegerField(blank=True, null=True, verbose_name='Оптом кол-во'),
        ),
        migrations.AddField(
            model_name='product',
            name='price_many',
            field=models.FloatField(blank=True, null=True, verbose_name='Цена оптом'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, null=True, verbose_name='Вес'),
        ),
    ]
