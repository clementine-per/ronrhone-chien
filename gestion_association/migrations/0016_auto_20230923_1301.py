# Generated by Django 3.1.4 on 2023-09-23 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0015_auto_20230708_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='telephone',
            field=models.CharField(max_length=14),
        ),
    ]