# Generated by Django 4.1.5 on 2024-01-11 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0017_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='message_id',
            field=models.BigIntegerField(null=True),
        ),
    ]