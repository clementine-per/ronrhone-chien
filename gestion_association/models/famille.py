from enum import Enum

from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from gestion_association.models import OuiNonChoice
from gestion_association.models.person import Person


class StatutFamille(Enum):
    DISPONIBLE = "Disponible"
    OCCUPE = "Occupée"
    A_VISITER = "A visiter"
    INDISPONIBLE = "Temporairement indisponible"
    INACTIVE = "Inactive"
    ADHESION = "Attente adhésion"


class OuiNonNullChoice(Enum):
    OUI = "Oui"
    NON = "Non"
    IND = "Indéterminé"


class StatutAccueil(Enum):
    EN_COURS = "En cours"
    TERMINE = "Terminé"
    A_DEPLACER = "A déplacer"


class Famille(models.Model):
    date_mise_a_jour = models.DateField(verbose_name="Date de mise à jour", auto_now=True)
    personne = models.OneToOneField(
        Person,
        verbose_name="Personne",
        on_delete=models.PROTECT,
    )
    statut = models.CharField(
        max_length=20,
        verbose_name="Statut",
        default="A_VISITER",
        choices=[(tag.name, tag.value) for tag in StatutFamille],
    )
    nb_animaux_historique = models.IntegerField(
        default=0, verbose_name="Nombre d'animaux au total"
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    nb_places = models.IntegerField(verbose_name="Nombre de places")
    detail_places = models.CharField(max_length=1000, blank=True, verbose_name="Détail des accueils acceptés")
    household = models.CharField(max_length=300, blank=True, verbose_name="Composition du foyer")
    house = models.CharField(max_length=300, blank=True, verbose_name="Logement")
    autres_animaux = models.CharField(max_length=1000, blank=True, verbose_name="Animaux de la FA ")
    absence = models.CharField(max_length=300, blank=True, verbose_name="Temps d'absence")
    vehicule = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Véhiculé(e)",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    exterieur = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Extérieur",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    congeneres = models.CharField(
        max_length=3,
        default="IND",
        verbose_name="Ok congénères",
        choices=[(tag.name, tag.value) for tag in OuiNonNullChoice],
    )
    chats = models.CharField(
        max_length=3,
        default="IND",
        verbose_name="Ok chats",
        choices=[(tag.name, tag.value) for tag in OuiNonNullChoice],
    )

    def get_nb_places_str(self):
        count = self.nb_places
        if self.animal_set:
            count -= self.animal_set.count()
        return str(count) + "/" + str(self.nb_places)

    def get_indisponibilites_str(self):
        result = ""
        if self.indisponibilite_set.order_by("date_debut").all():
            for indispo in self.indisponibilite_set.all():
                result += str(indispo)
                result += "<br>"
        return mark_safe(result)

    def get_disponibilite_str(self):
        today = timezone.now().date()
        result = self.get_statut_display()
        prochaines_indispos = self.indisponibilite_set.filter(date_fin__gte=today).all()
        if prochaines_indispos:
            result += "\n"
            result += "Prochaines indisponibilités : "
            for indispo in prochaines_indispos:
                result += "\n"
                result += str(indispo)
        return mark_safe(result)

    def get_preference_str(self):
        result = ""
        if self.detail_places:
            result += "Détail des accueils acceptés : "
            result +=self.detail_places
            result += "\n"
        if self.house:
            result += "Logement : "
            result +=self.house
            result += "\n"
        if self.household:
            result += "Composition du foyer : "
            result +=self.household
            result += "\n"
        if self.exterieur and self.exterieur == "OUI":
            result += " avec extérieur"
        else:
            result += " sans extérieur"
        result += "\n"
        if self.autres_animaux:
            result += "Autres animaux de la FA : "
            result +=self.autres_animaux
            result += "\n"
        if self.absence :
            result += "Temps d'absence : "
            result += str(self.absence)
            result += "\n"
        return result

    def to_json(self):
        return {
            "id": self.pk,
            "places_disponible": self.get_nb_places_str(),
            "personne": str(self.personne),
            "disponibilites": self.get_disponibilite_str(),
            "caracteristiques": self.get_preference_str(),
            "commentaire": self.commentaire,
        }


class Indisponibilite(models.Model):
    date_debut = models.DateField(verbose_name="Date de départ")
    date_fin = models.DateField(verbose_name="Date de retour")
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT)

    def __str__(self):
        result = "Du "
        result += self.date_debut.strftime("%d/%m/%Y")
        result += " au "
        result += self.date_fin.strftime("%d/%m/%Y")
        return result


class Accueil(models.Model):
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT)
    animal = models.ForeignKey("Animal", on_delete=models.PROTECT)
    commentaire = models.CharField(max_length=1000, blank=True)
    statut = models.CharField(
        max_length=20,
        verbose_name="Statut",
        default="EN_COURS",
        choices=[(tag.name, tag.value) for tag in StatutAccueil],
    )

    def is_termine(self):
        return self.statut == StatutAccueil.TERMINE.name

    def save(self, *args, **kwargs):
        # Maj statut lors de la création de l'adoption
        if self._state.adding:
            # Un animal ne peut pas être dans deux FA à la fois
            # On termine donc l'autre accueil éventuel
            for accueil in self.animal.accueil_set.filter(statut__in=[StatutAccueil.A_DEPLACER.name,StatutAccueil.EN_COURS.name]).all():
                accueil.date_fin = timezone.now().date()
                accueil.statut = StatutAccueil.TERMINE.name
                accueil.save()
                # S'il s'agissait du dernier accueil de l'ancienne FA, on la remet disponible
                if not accueil.famille.accueil_set.filter(statut__in=[StatutAccueil.A_DEPLACER.name,StatutAccueil.EN_COURS.name]):
                    accueil.famille.statut = StatutFamille.DISPONIBLE.name
                    accueil.famille.save()
            #On change la FA de l'animal
            self.animal.famille = self.famille
            self.animal.save()
            #On passe le statut FA à occupé
            self.famille.statut = StatutFamille.OCCUPE.name
            self.famille.save()
        else :
            # Si date de fin aujourd'hui ou dans le passé, l'accueil est terminé
            if self.date_fin and self.date_fin <= timezone.now().date():
                self.statut = StatutAccueil.TERMINE.name
                self.animal.famille = None
                self.animal.save()
                # S'il s'agissait du dernier accueil de la FA, elle redevient disponible
                if not self.famille.accueil_set.filter(statut__in=[StatutAccueil.A_DEPLACER.name,StatutAccueil.EN_COURS.name]).exclude(id = self.id):
                    self.famille.statut = StatutFamille.DISPONIBLE.name
                    self.famille.save()
            # Si date de fin dans le futur, l'animal est à déplacer
            if self.date_fin and self.date_fin > timezone.now().date():
                self.statut = StatutAccueil.A_DEPLACER.name

        return super().save(*args, **kwargs)
