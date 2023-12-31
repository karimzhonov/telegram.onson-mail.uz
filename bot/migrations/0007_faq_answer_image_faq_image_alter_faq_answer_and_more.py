# Generated by Django 4.1.5 on 2023-12-04 11:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0006_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='answer_image',
            field=models.ImageField(blank=True, null=True, upload_to='faq_answer'),
        ),
        migrations.AddField(
            model_name='faq',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='faq'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
