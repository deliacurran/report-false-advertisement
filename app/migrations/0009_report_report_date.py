# Generated by Django 4.2.7 on 2024-03-24 20:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_report_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='report_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
