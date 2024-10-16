# Generated by Django 3.1.4 on 2024-05-20 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0019_person_nom_pro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='tarif_horaire',
        ),
        migrations.AddField(
            model_name='person',
            name='tarif_bilan',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Prix d'un bilan comportemental"),
        ),
        migrations.AddField(
            model_name='person',
            name='tarif_seance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Prix d'une séance d'éducation"),
        ),
    ]
