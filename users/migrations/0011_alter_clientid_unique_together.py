# Generated by Django 4.1.5 on 2023-11-22 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_clientid_selected_client'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='clientid',
            unique_together=set(),
        ),
    ]
