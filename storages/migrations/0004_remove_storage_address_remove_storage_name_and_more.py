# Generated by Django 4.1.5 on 2023-11-23 07:10

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0003_alter_storage_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='address',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='name',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='point',
        ),
        migrations.AddField(
            model_name='storage',
            name='phone',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='StorageTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255, null=True)),
                ('address', models.TextField(null=True)),
                ('text', models.TextField(null=True)),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='storages.storage')),
            ],
            options={
                'verbose_name': 'storage Translation',
                'db_table': 'storages_storage_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
