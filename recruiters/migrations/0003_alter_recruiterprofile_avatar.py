# Generated by Django 4.2.4 on 2023-09-30 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiters', '0002_remove_recruiterprofile_background_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiterprofile',
            name='avatar',
            field=models.URLField(blank=True, null=True),
        ),
    ]