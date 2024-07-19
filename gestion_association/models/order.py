from django.db import models

from gestion_association.models.animal import Animal


class Order(models.Model):
    date = models.DateField(verbose_name="Date d'achat")
    content = models.CharField(verbose_name="Contenu", max_length=150, blank=True)
    comment = models.CharField(verbose_name="Commentaire", max_length=1000, blank=True)
    amount = models.DecimalField(
        verbose_name="Montant",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name="orders")