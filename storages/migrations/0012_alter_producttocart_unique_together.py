# Generated by Django 4.1.5 on 2023-11-29 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_cart_clientid'),
        ('storages', '0011_producttochosen'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='producttocart',
            unique_together={('product', 'cart')},
        ),
    ]
