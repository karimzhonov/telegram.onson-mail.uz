# Generated by Django 4.1.5 on 2023-11-28 04:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_client_create_date_clientid_create_date_and_more'),
        ('orders', '0006_alter_historicalorder_number_alter_order_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clientid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.clientid')),
            ],
        ),
    ]
