# Generated by Django 4.1.7 on 2023-05-09 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_permission_endpoint'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeerole',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='authentication.permission'),
        ),
    ]
