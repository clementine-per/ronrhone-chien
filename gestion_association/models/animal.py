from datetime import timedelta
from decimal import Decimal
from enum import Enum

from django.db import models
from django.utils import timezone

from gestion_association.models import OuiNonChoice, TypeChoice, PerimetreChoice
from gestion_association.models.famille import Famille
from gestion_association.models.person import Person


class SexeChoice(Enum):
    F = "Femelle"
    M = "Mâle"
    NI = "Non identifié"


class OuiNonNullChoice(Enum):
    OUI = "Oui"
    NON = "Non"
    IND = "Indéterminé"


class TypeVaccinChoice(Enum):
    CHPL = "CHPL"
    CHPL4 = "CHPL4"
    CHPPIL = "CHPPiL"
    CHPPIL4 = "CHPPiL4"


class StatutAnimal(Enum):
    A_ADOPTER = "A l'adoption"
    ADOPTABLE = "Adoptable"
    ADOPTION = "En cours d'adoption"
    ADOPTE = "Adopté"
    ADOPTE_DEFINITIF = "Adopté définitivement"
    REHABILITATION = "Réhabilitation"
    SOIN = "En soin"
    SEVRAGE = "En sevrage"
    PERDU = "Perdu"
    DECEDE = "Décédé"
    RENDU = "Rendu à ses propriétaires"
    RELACHE = "Relâché"
    PEC = "Prendre en charge"


statuts_association = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTION.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.PEC.name,
    StatutAnimal.REHABILITATION.name,
    StatutAnimal.SOIN.name,
    StatutAnimal.SEVRAGE.name,
]


class TypePaiementChoice(Enum):
    MENSUEL = "Mensuel"
    UNIQUE = "En une fois"


class TrancheAge(Enum):
    ENFANT = "Enfant"
    ADULTE = "Adulte"
    SENIOR = "Sénior"


class Preference(models.Model):
    exterieur = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Extérieur",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    rehabilitation = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Réhabilitation",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    biberonnage = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Biberonnage",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    ville = models.CharField(
        max_length=3,
        default="IND",
        verbose_name="Vie en ville",
        choices=[(tag.name, tag.value) for tag in OuiNonNullChoice],
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
    enfants = models.CharField(
        max_length=3,
        default="IND",
        verbose_name="Ok enfants",
        choices=[(tag.name, tag.value) for tag in OuiNonNullChoice],
    )
    nb_heures_absence = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=" Nombre maximum d'heures d'absence consécutives",
    )

    def __str__(self):
        preferences = "Nécéssités : \n"
        if self.rehabilitation == OuiNonChoice.OUI.name:
            preferences += "Réhabilitation \n"
        if self.biberonnage == OuiNonChoice.OUI.name:
            preferences += "Biberonnage \n"
        if self.exterieur == OuiNonChoice.OUI.name:
            preferences += "Extérieur \n"
        if self.ville == OuiNonChoice.OUI.name:
            preferences += "Vie en ville ok \n"
        elif self.ville == OuiNonChoice.NON.name:
            preferences += "Pas de vie en ville \n"
        if self.congeneres == OuiNonChoice.OUI.name:
            preferences += "Ok congénères \n"
        elif self.congeneres == OuiNonChoice.NON.name:
            preferences += "Pas ok congénères \n"
        if self.chats == OuiNonChoice.OUI.name:
            preferences += "Ok chats \n"
        if self.enfants == OuiNonChoice.OUI.name:
            preferences += "Ok enfants \n"

        return preferences

class AnimalGroup(models.Model):
    # Groupes d'animaux par foreign key sur animal
    pass


class Animal(models.Model):
    date_mise_a_jour = models.DateField(verbose_name="Date de mise à jour", auto_now=True)
    nom = models.CharField(max_length=150, unique=True)
    circonstances = models.CharField(max_length=150)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    date_arrivee = models.DateField(verbose_name="Date de prise en charge", null=True, blank=True)
    sexe = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )
    type = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
        default="CHIEN",
    )
    sterilise = models.CharField(
        max_length=3,
        verbose_name="Stérilisé(e)",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    identification = models.CharField(
        max_length=150, verbose_name="Numéro d'identification", blank=True
    )
    lien_icad = models.URLField(max_length=150, verbose_name="Lien ICAD", blank=True)
    bilan = models.CharField(
        max_length=3,
        verbose_name="Bilan comportemental",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        default="NON",
    )
    primo_vaccine = models.CharField(
        max_length=3,
        verbose_name="Primo Vacciné(e)",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    vaccin_ok = models.CharField(
        max_length=3,
        verbose_name="Vaccins à jour",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    vaccin_rage = models.CharField(
        max_length=3,
        verbose_name="Vaccin rage",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    type_vaccin = models.CharField(
        max_length=10,
        verbose_name="Type de vaccin",
        default="CHPL",
        choices=[(tag.name, tag.value) for tag in TypeVaccinChoice],
    )
    date_dernier_vaccin = models.DateField(
        verbose_name="Date du dernier rappel de vaccin", null=True, blank=True
    )
    date_prochain_vaccin = models.DateField(
        verbose_name="Date du prochain rappel de vaccin", null=True, blank=True
    )
    date_sterilisation = models.DateField(
        verbose_name="Date de stérilisation", null=True, blank=True
    )
    date_vermifuge = models.DateField(
        verbose_name="Date du dernier vermifuge", null=True, blank=True
    )
    date_parasite = models.DateField(
        verbose_name="Date d'administration de l'anti parasite", null=True, blank=True
    )
    statut = models.CharField(
        max_length=30,
        default="REHABILITATION",
        choices=[(tag.name, tag.value) for tag in StatutAnimal],
    )
    date_mise_adoption = models.DateField(
        verbose_name="Date de mise à l'adoption", null=True, blank=True
    )
    adoptant = models.ForeignKey(
        Person,
        verbose_name="Adoptant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    educateur = models.ForeignKey(
        Person,
        verbose_name="Educateur",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chiens",
    )
    ancien_proprio = models.ForeignKey(
        Person,
        verbose_name="Ancien propriétaire",
        related_name="anciens_animaux",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    inactif = models.BooleanField(
        default=False,
        verbose_name="Desactivé (Ne cocher que si vous ne souhaitez\
                                           plus gérer cet animal dans l'application) ",
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    commentaire_bilan = models.CharField(max_length=150, blank=True)
    commentaire_sante = models.CharField(max_length=1000, blank=True)
    contact = models.CharField(max_length=500, blank=True, verbose_name="Contact prise en charge")
    preference = models.OneToOneField(Preference, on_delete=models.PROTECT, blank=True, null=True)
    groupe = models.ForeignKey(AnimalGroup, on_delete=models.CASCADE, blank=True, null=True)
    commentaire_animaux_lies = models.CharField(max_length=1000, blank=True)
    race = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True, verbose_name="Robe")
    tranche_age = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Tranche d'âge",
        choices=[(tag.name, tag.value) for tag in TrancheAge],
    )
    perimetre = models.CharField(
        max_length=30,
        default="UN",
        verbose_name="Périmètre de gestion",
        choices=[(tag.name, tag.value) for tag in PerimetreChoice],
    )
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Déterminer la tranche d'age à partir de la date de naissance
            if self.date_naissance:
                today = timezone.now().date()
                twelve_months = today - timedelta(days=12 * 30)
                senior = today - timedelta(days=30 * 12 * 10)
                date_naissance = self.date_naissance
                if date_naissance > twelve_months:
                    self.tranche_age = TrancheAge.ENFANT.name
                elif date_naissance > senior:
                    self.tranche_age = TrancheAge.ADULTE.name
                else:
                    self.tranche_age = TrancheAge.SENIOR.name
        # Mise à jour des préférences en fonction du statut
        if self.statut == StatutAnimal.REHABILITATION.name:
            self.preference.rehabilitation = OuiNonChoice.OUI.name
            self.preference.save()
        if self.ancien_proprio:
            self.ancien_proprio.is_ancien_proprio = True
            self.ancien_proprio.save()
        return super(Animal, self).save(*args, **kwargs)

    def get_latest_adoption(self):
        if self.adoption_set:
            return self.adoption_set.all().order_by("-id").first()
        return None

    def get_other_adoptions(self):
        if len(self.adoption_set.all()) > 1:
            return self.adoption_set.all().exclude(id=self.get_latest_adoption().id)
        return None

    def __str__(self):
        return self.nom

    def get_vaccin_str(self):
        #Primo vacciné
        date_str = ""
        if self.date_prochain_vaccin:
            date_str = " rappel avant le " + self.date_prochain_vaccin.strftime("%d/%m/%Y")
        if self.primo_vaccine == OuiNonChoice.OUI.name and self.vaccin_ok == OuiNonChoice.NON.name:
            return (
                self.type_vaccin + " "
                + " Primo " + date_str
            )
        elif (
            self.primo_vaccine == OuiNonChoice.OUI.name and self.vaccin_ok == OuiNonChoice.OUI.name
        ):
            return self.type_vaccin + date_str
        else:
            return "Non"

    def get_bilan_str(self):
        #Primo vacciné
        bilan_str = self.get_bilan_display()
        if self.commentaire_bilan:
            bilan_str += " ( " + self.commentaire_bilan + " )"
        return bilan_str

    def get_animaux_lies_str(self):
        result = ""
        if self.groupe:
            for animal in self.groupe.animal_set.all():
                if animal != self :
                    result += animal.nom + " "
        return result

    def get_animaux_lies(self):
        if self.groupe:
            return self.groupe.animal_set.exclude(id=self.pk)

    def is_sterilise(self):
        return self.sterilise == OuiNonChoice.OUI.name

    def is_en_soin_justif(self):
        return self.statut == StatutAnimal.SOIN.name and self.commentaire_sante

    def is_adoptable(self):
        return self.statut == StatutAnimal.ADOPTABLE.name or self.statut == StatutAnimal.A_ADOPTER.name

    def get_montant_veto_total(self):
        montant_total = Decimal(0)
        for vis in self.visites.all():
            if vis.montant:
                montant_total += vis.get_montant_par_animal()
        return f"{montant_total}"

    def get_montant_seances_total(self):
        total = 0
        for training in self.trainings.all():
            if training.amount is not None:
                total += training.amount
        return f"{total}"

    def get_montant_orders_total(self):
        total = 0
        for order in self.orders.all():
            if order.amount is not None:
                total += order.amount
        return f"{total}"


class Parrainage(models.Model):
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    personne = models.ForeignKey(Person, on_delete=models.PROTECT)
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    type_paiement = models.CharField(
        max_length=20,
        verbose_name="Type de paiement",
        default=TypePaiementChoice.MENSUEL.name,
        choices=[(tag.name, tag.value) for tag in TypePaiementChoice],
    )
    montant = models.DecimalField(
        verbose_name="Montant du parrainage",
        max_digits=5,
        decimal_places=2, blank=True, null=True
    )
    date_nouvelles = models.DateField(verbose_name="Date des dernières nouvelles données", blank=True, null=True)
