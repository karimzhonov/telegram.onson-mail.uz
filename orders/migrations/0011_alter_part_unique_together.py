# Generated by Django 4.1.5 on 2023-11-30 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0014_alter_category_options_and_more'),
        ('orders', '0010_alter_cart_options_alter_report_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='part',
            unique_together={('storage', 'number')},
        ),
    ]
