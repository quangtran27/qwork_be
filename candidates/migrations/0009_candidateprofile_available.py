# Generated by Django 4.2.4 on 2023-12-14 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0008_alter_candidateprofile_saved_jobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]
