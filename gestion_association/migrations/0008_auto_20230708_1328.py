# Generated by Django 3.1.4 on 2023-07-08 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0007_trainingsession'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='famille',
            name='formation_faite',
        ),
        migrations.RemoveField(
            model_name='famille',
            name='formation_payee',
        ),
        migrations.RemoveField(
            model_name='famille',
            name='longue_duree',
        ),
        migrations.RemoveField(
            model_name='famille',
            name='niveau',
        ),
        migrations.RemoveField(
            model_name='famille',
            name='taille_logement',
        ),
        migrations.RemoveField(
            model_name='famille',
            name='type_animal',
        ),
        migrations.AddField(
            model_name='famille',
            name='exterieur',
            field=models.CharField(choices=[('OUI', 'Oui'), ('NON', 'Non')], default='NON', max_length=3, verbose_name='Extérieur'),
        ),
        migrations.AlterField(
            model_name='trainingsession',
            name='trainer',
            field=models.CharField(blank=True, max_length=150, verbose_name='Educateur'),
        ),
    ]