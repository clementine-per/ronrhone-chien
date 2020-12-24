from enum import Enum

from django.core.validators import RegexValidator
from django.db import models

# Enum utilisée pour l'écran de recherche
class TypePersonChoice(Enum):
    FA = "Famille d'accueil"
    ADOPTANTE = "Adoptante"
    BENEVOLE = "Bénévole"

class Person(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=150)
    email = models.EmailField(max_length=150,
        unique=True,
        error_messages={
            'unique': ("A user with that username already exists."),
        },)
    adresse = models.CharField(max_length=500)
    code_postal_regex = RegexValidator(
        regex="^[0-9]*$", message="Veuillez entrer un code postal valide."
    )
    code_postal = models.CharField(validators=[code_postal_regex],max_length=5)
    ville = models.CharField(max_length=100)
    telephone_regex = RegexValidator(
        regex="[0-9]{10}", message="Veuillez entrer un numéro de téléphone valide."
    )
    telephone = models.CharField(validators=[telephone_regex], max_length=10)
    date_inscription = models.DateField(auto_now_add=True)
    profession = models.CharField(max_length=250)
    commentaire = models.CharField(max_length=1000, blank=True)
    inactif = models.BooleanField(default=False,
                                  verbose_name="Desactivé (Ne cocher que si vous ne souhaitez\
                                       plus gérer cette personne dans l'application) ")
    is_famille = models.BooleanField(default=False,
                                        verbose_name="Famille d'accueil")
    is_adoptante = models.BooleanField(default=False,
                                    verbose_name="Adoptante")
    is_benevole = models.BooleanField(default=False,
                                    verbose_name="Bénévole")
    commentaire_benevole = models.CharField(max_length=1000, blank=True)

    def get_adresse_complete(self):
        return f"{self.adresse} \n {self.code_postal} {self.ville}"