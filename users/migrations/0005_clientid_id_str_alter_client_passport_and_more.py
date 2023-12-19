# Generated by Django 4.1.5 on 2023-11-22 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_info_alter_text_lang'),
        ('storages', '0003_alter_storage_name'),
        ('users', '0004_clientid_clients_alter_clientid_selected_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientid',
            name='id_str',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='passport',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='pnfl',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='clientid',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.user'),
        ),
        migrations.AlterUniqueTogether(
            name='clientid',
            unique_together={('storage', 'selected_client')},
        ),
    ]
