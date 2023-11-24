# Generated by Django 4.1.5 on 2023-11-24 05:11

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0003_infotranslation_delete_text_remove_info_slug_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='info',
            options={'verbose_name': 'Телеграм руководства', 'verbose_name_plural': 'Телеграм руководстви'},
        ),
        migrations.AlterModelOptions(
            name='infotranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Телеграм руководства Translation'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Телеграм пользователь', 'verbose_name_plural': 'Телеграм пользователи'},
        ),
        migrations.AddField(
            model_name='user',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 24, 5, 11, 11, 465593, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='info',
            name='file',
            field=models.FileField(upload_to='info', verbose_name='Видео или фото'),
        ),
        migrations.AlterField(
            model_name='info',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Актив'),
        ),
        migrations.AlterField(
            model_name='infotranslation',
            name='text',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='infotranslation',
            name='title',
            field=models.CharField(max_length=255, null=True, verbose_name='Загаловка'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='lang',
            field=models.CharField(choices=[('ru', 'Русский'), ('uz', "O'zbekcha"), ('uz-cl', 'Узбекча')], default='uz', max_length=20, verbose_name='Язык'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия'),
        ),
        migrations.CreateModel(
            name='HistoricalUser',
            fields=[
                ('id', models.IntegerField(db_index=True)),
                ('username', models.SlugField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('lang', models.CharField(choices=[('ru', 'Русский'), ('uz', "O'zbekcha"), ('uz-cl', 'Узбекча')], default='uz', max_length=20, verbose_name='Язык')),
                ('create_date', models.DateTimeField(blank=True, editable=False, null=True)),
                ('last_date', models.DateTimeField(default=datetime.datetime(2023, 11, 24, 5, 11, 11, 465593, tzinfo=datetime.timezone.utc))),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Телеграм пользователь',
                'verbose_name_plural': 'historical Телеграм пользователи',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
