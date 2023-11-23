# Generated by Django 4.1.5 on 2023-11-22 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_info_alter_text_lang'),
        ('users', '0002_client_passport_image_clientid_client_client_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='client_id',
        ),
        migrations.AddField(
            model_name='clientid',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.user'),
        ),
    ]
