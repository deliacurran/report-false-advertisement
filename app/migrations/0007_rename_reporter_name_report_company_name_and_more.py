# Generated by Django 4.2.7 on 2024-03-24 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_report_report_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='reporter_name',
            new_name='company_name',
        ),
        migrations.AddField(
            model_name='report',
            name='category',
            field=models.CharField(choices=[('Food', 'Food'), ('Retail', 'Retail'), ('Jobs', 'Jobs'), ('Services', 'Services'), ('Medical', 'Medical'), ('Other', 'Other')], default='Other', max_length=50),
        ),
        migrations.AddField(
            model_name='report',
            name='reporter_email',
            field=models.CharField(default='Anonymous', max_length=200),
        ),
    ]
