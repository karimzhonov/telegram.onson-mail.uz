# Generated by Django 4.1.5 on 2023-11-18 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('username', models.SlugField(blank=True, null=True, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('lang', models.CharField(choices=[('ru', 'Русский'), ('uz', "O'zbekcha"), ('uz_cl', 'Узбекча')], default='uz', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('text', models.TextField()),
                ('lang', models.CharField(max_length=20, verbose_name=(('ru', 'Русский'), ('uz', "O'zbekcha"), ('uz_cl', 'Узбекча')))),
            ],
            options={
                'unique_together': {('slug', 'lang')},
            },
        ),
    ]
