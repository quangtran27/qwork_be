# Generated by Django 4.2.4 on 2023-09-30 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_remove_job_city_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='salaryFrom',
            new_name='salary_from',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='salaryTo',
            new_name='salary_to',
        ),
    ]
