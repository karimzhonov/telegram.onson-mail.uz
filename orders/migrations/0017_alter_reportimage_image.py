# Generated by Django 4.1.5 on 2023-12-13 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_remove_report_image_reportimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportimage',
            name='image',
            field=models.ImageField(upload_to='report', verbose_name='Фото'),
        ),
    ]