# Generated by Django 4.1.5 on 2023-11-29 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0012_alter_producttocart_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='storage',
            name='has_online_buy',
            field=models.BooleanField(default=False),
        ),
    ]
