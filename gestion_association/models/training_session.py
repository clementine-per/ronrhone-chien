from django.db import models

from enum import Enum

from gestion_association.models.animal import Animal


class TrainingTypeChoice(Enum):
    BILAN = "Bilan comportemental"
    PRE_SESSION = "Séance d'éducation"
    POST_SESSION = "Séance post adoption"


class TrainingSession(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    date = models.DateField(verbose_name="Date de la séance")
    type_training = models.CharField(
        max_length=30,
        verbose_name="Type de session",
        choices=[(tag.name, tag.value) for tag in TrainingTypeChoice],
    )
    trainer = models.CharField(max_length=150, blank=True, verbose_name="Educateur")
    comment = models.CharField(max_length=2000, blank=True, verbose_name="Commentaire")
    amount = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2, blank=True, null=True
    )
    animal = animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name="trainings")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Session {self.type_training} le {self.date} avec {self.trainer}"