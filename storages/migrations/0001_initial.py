# Generated by Django 4.1.5 on 2023-11-18 10:37
import parler
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(blank=True, default='', null=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storages.storage')),
            ],
        ),
    ]
