# Generated by Django 4.2.4 on 2023-09-20 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0003_alter_candidateprofile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateprofile',
            name='avatar',
            field=models.URLField(blank=True, default=None, null=True),
        ),
    ]
