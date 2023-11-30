# Generated by Django 4.1.5 on 2023-11-29 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_client_create_date_clientid_create_date_and_more'),
        ('orders', '0008_alter_cart_clientid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='report')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('clientid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.clientid')),
            ],
        ),
    ]