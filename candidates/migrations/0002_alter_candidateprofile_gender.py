# Generated by Django 4.2.4 on 2023-09-20 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Nam'), ('famele', 'Nữ')], default=1),
        ),
    ]