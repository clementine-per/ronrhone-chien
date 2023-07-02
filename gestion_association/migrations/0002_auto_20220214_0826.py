# Generated by Django 3.1.4 on 2022-02-14 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animal',
            name='felv',
        ),
        migrations.RemoveField(
            model_name='animal',
            name='fiv',
        ),
        migrations.AddField(
            model_name='animal',
            name='bilan',
            field=models.CharField(choices=[('OUI', 'Oui'), ('NON', 'Non')], default='NON', max_length=3, verbose_name='Bilan comportemental'),
        ),
        migrations.AddField(
            model_name='animal',
            name='commentaire_bilan',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='animal',
            name='vaccin_rage',
            field=models.CharField(choices=[('OUI', 'Oui'), ('NON', 'Non')], default='NON', max_length=3, verbose_name='Vaccin rage'),
        ),
        migrations.AddField(
            model_name='famille',
            name='formation_faite',
            field=models.CharField(choices=[('OUI', 'Oui'), ('NON', 'Non')], default='NON', max_length=3, verbose_name='Formation réalisée'),
        ),
        migrations.AddField(
            model_name='famille',
            name='formation_payee',
            field=models.CharField(choices=[('OUI', 'Oui'), ('NON', 'Non')], default='NON', max_length=3, verbose_name='Formation payée'),
        ),
        migrations.AlterField(
            model_name='animal',
            name='type_vaccin',
            field=models.CharField(choices=[('CHPL', 'CHPL'), ('CHPL4', 'CHPL4'), ('CHPPIL', 'CHPPiL'), ('CHPPIL4', 'CHPPiL4')], default='CHPL', max_length=10, verbose_name='Type de vaccin'),
        ),
    ]