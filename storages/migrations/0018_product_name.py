# Generated by Django 4.1.5 on 2023-12-11 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0017_remove_category_storage_category_parent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='Название'),
        ),
    ]