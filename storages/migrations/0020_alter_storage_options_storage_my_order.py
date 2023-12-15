# Generated by Django 4.1.5 on 2023-12-14 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0019_alter_category_parent_alter_product_storage_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='storage',
            options={'ordering': ['my_order'], 'verbose_name': 'Склад', 'verbose_name_plural': 'Склади'},
        ),
        migrations.AddField(
            model_name='storage',
            name='my_order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]