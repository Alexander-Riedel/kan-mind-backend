# Generated by Django 5.2.1 on 2025-05-18 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='fullname',
            field=models.TextField(default='Unknown'),
            preserve_default=False,
        ),
    ]
