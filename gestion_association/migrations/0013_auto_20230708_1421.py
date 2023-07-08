# Generated by Django 3.1.4 on 2023-07-08 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0012_remove_famille_preference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='famille',
            name='nb_heures_absence',
        ),
        migrations.AddField(
            model_name='famille',
            name='absence',
            field=models.CharField(blank=True, max_length=300, verbose_name="Temps d'absence"),
        ),
        migrations.AddField(
            model_name='famille',
            name='house',
            field=models.CharField(blank=True, max_length=300, verbose_name='Logement'),
        ),
        migrations.AddField(
            model_name='famille',
            name='household',
            field=models.CharField(blank=True, max_length=300, verbose_name='Composition du foyer'),
        ),
    ]