# Generated by Django 4.2.4 on 2023-10-06 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_rename_salaryfrom_job_salary_from_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='updated',
            field=models.DateField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='Application',
        ),
    ]
