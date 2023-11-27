# Generated by Django 4.1.5 on 2023-11-24 03:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('storages', '0005_alter_storagetranslation_address_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0014_alter_clientid_unique_together_alter_clientid_user_and_more'),
        ('orders', '0003_part_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPart',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True)),
                ('status', models.CharField(choices=[('in_storage', 'В складе'), ('in_delivery', 'Доставка'), ('done', 'Доставлено')], default='in_storage', max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('storage', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='storages.storage')),
            ],
            options={
                'verbose_name': 'historical part',
                'verbose_name_plural': 'historical parts',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('clientid', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('weight', models.FloatField()),
                ('facture_price', models.FloatField()),
                ('date', models.DateField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('client', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.client', to_field='pnfl')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('part', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='orders.part')),
            ],
            options={
                'verbose_name': 'historical order',
                'verbose_name_plural': 'historical orders',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]