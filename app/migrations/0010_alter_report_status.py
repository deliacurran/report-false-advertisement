# Generated by Django 4.2.7 on 2024-03-24 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_report_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('Review-Pending', 'Review-Pending'), ('Review-In-Progress', 'Review-In-Progress'), ('Review-Completed', 'Review-Completed')], default='Review-Pending', max_length=50),
        ),
    ]
