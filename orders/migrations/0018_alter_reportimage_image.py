# Generated by Django 4.1.5 on 2023-12-14 15:45

import admin_async_upload.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_alter_reportimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportimage',
            name='image',
            field=admin_async_upload.models.AsyncFileField(upload_to='report', verbose_name='Фото'),
        ),
    ]