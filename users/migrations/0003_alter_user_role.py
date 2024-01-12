# Generated by Django 4.2.4 on 2024-01-12 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Quản trị viên'), ('staff', 'Nhân viên'), ('recruiter', 'Nhà tuyển dụng'), ('candidate', 'Ứng cử viên')], default='candidate'),
        ),
    ]
