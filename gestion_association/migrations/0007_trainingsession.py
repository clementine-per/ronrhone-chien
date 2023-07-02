# Generated by Django 3.1.4 on 2023-07-02 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0006_auto_20230513_0356'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_mise_a_jour', models.DateField(auto_now=True, verbose_name='Date de mise à jour')),
                ('date', models.DateField(verbose_name='Date de la séance')),
                ('type_training', models.CharField(choices=[('BILAN', 'Bilan comportemental'), ('PRE_SESSION', "Séance d'éducation"), ('POST_SESSION', 'Séance post adoption')], max_length=30, verbose_name='Type de session')),
                ('trainer', models.CharField(blank=True, max_length=150)),
                ('comment', models.CharField(blank=True, max_length=2000, verbose_name='Commentaire')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Montant')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trainings', to='gestion_association.animal')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]