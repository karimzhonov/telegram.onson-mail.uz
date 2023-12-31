# Generated by Django 4.1.5 on 2023-11-22 04:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_client_client_id_clientid_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientid',
            name='clients',
            field=models.ManyToManyField(to='users.client'),
        ),
        migrations.AlterField(
            model_name='clientid',
            name='selected_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_client', to='users.client'),
        ),
    ]
