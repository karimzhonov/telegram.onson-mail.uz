# Generated by Django 4.1.5 on 2023-12-15 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0022_alter_storage_my_order'),
        ('bot', '0012_info_url_alter_info_file_alter_infotranslation_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='storage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='storages.storage'),
        ),
        migrations.AddField(
            model_name='info',
            name='users',
            field=models.ManyToManyField(to='bot.user'),
        ),
    ]