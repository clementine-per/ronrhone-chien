from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import TarifAdoption, TarifBonSterilisation, Adoption, BonSterilisation, \
    OuiNonVisiteChoice
from gestion_association.models.animal import Animal, statuts_association, StatutAnimal
from gestion_association.models.famille import Famille, StatutAccueil, Accueil

statuts_adoption = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTION.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.ADOPTE.name,
]

@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"

    today = timezone.now().date()
    interval_10 = today + timedelta(days=10)
    interval_5_weeks_ago = today - timedelta(days=35)
    interval_5_months_ago = today - relativedelta(months=5)
    interval_12_months_ago = today - relativedelta(months=7)
    # Valeurs str utilisées dans le template html
    today_str = today.strftime("%Y-%m-%d")
    interval_10_str = interval_10.strftime("%Y-%m-%d")
    interval_5_weeks_ago_str = interval_5_weeks_ago.strftime("%Y-%m-%d")
    interval_12_months_ago_str = interval_12_months_ago.strftime("%Y-%m-%d")

    statuts_association_filter = ""
    for statut in statuts_association:
        statuts_association_filter += 'statuts='
        statuts_association_filter += statut
        statuts_association_filter += '&'
    # Partie adoptions
    # A proposer à l'adoption
    a_proposer = Animal.objects.filter(inactif=False).filter(statut='ADOPTABLE').count()
    #A l'adoption
    a_l_adoption = Animal.objects.filter(inactif=False).filter(statut='A_ADOPTER').count()
    # Acomptes
    acomptes = Adoption.objects.filter(annule=False).filter(acompte_verse=OuiNonChoice.NON.name).count()
    # Adoptions pré-visites
    adoption_previsite = Adoption.objects.filter(annule=False).filter(animal__statut='ADOPTION') \
        .filter(pre_visite=OuiNonChoice.NON.name).filter(acompte_verse=OuiNonChoice.OUI.name).count()
    # Adoptions en attente de paiement complet
    adoption_paiement_list = Adoption.objects.filter(annule=False).filter(animal__statut='ADOPTION').filter(pre_visite=OuiNonChoice.OUI.name) \
        .filter(acompte_verse=OuiNonChoice.OUI.name).filter(montant_restant__gt = Decimal(0))
    adoption_paiement_montant = adoption_paiement_list.aggregate(Sum('montant_restant'))
    adoption_paiement = adoption_paiement_list.count()
    # Adoptions attendant leur visite de contrôle
    adoption_post = Adoption.objects.filter(annule=False).filter(visite_controle=OuiNonChoice.NON.name)\
        .filter(date_visite__lte=today).filter(animal__sterilise=OuiNonChoice.OUI.name)\
        .filter(animal__statut__in=statuts_adoption).count()
    # Post visite à contrôler
    adoption_controle = Adoption.objects.filter(annule=False).\
        filter(visite_controle__in=[OuiNonVisiteChoice.ALIMENTAIRE.name,OuiNonVisiteChoice.VACCIN.name])\
    .filter(animal__statut__in=statuts_adoption).count()
    # En attente d'adoption définitive
    waiting_adoption_over = Adoption.objects.filter(annule=False).filter(animal__statut='ADOPTE') \
        .count()
    # Adoptions à clore
    adoption_over = Adoption.objects.filter(annule=False).filter(animal__statut='ADOPTE')\
        .filter(visite_controle=OuiNonChoice.OUI.name).count()
    # Adoptions sans sterilisation
    adoption_ste = Adoption.objects.filter(annule=False).filter(animal__statut__in=(StatutAnimal.ADOPTION.name,StatutAnimal.ADOPTE_DEFINITIF.name, StatutAnimal.ADOPTE.name)).\
        filter(animal__sterilise=OuiNonChoice.NON.name) \
        .filter(animal__date_naissance__lte=interval_12_months_ago).count()


    # Partie soins
     # Animaux en soin
    soins = Animal.objects.filter(inactif=False).filter(statut='SOIN').count()
    # Animaux avec soin manquant
    soins_manquants = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association)\
        .filter(Q(Q(sterilise=OuiNonChoice.NON.name)&Q(date_naissance__lte=interval_5_months_ago))| Q(vaccin_ok=OuiNonChoice.NON.name)|\
    Q(identification__exact='')).count()
    # Bon de stérilisation à envoyer
    bon_a_envoyer = BonSterilisation.objects.filter(envoye=OuiNonChoice.NON.name).count()
    # Bon de stérilisation arrivant à expiation (10 jours)
    bon_a_utilise = BonSterilisation.objects.filter(utilise=OuiNonChoice.NON.name).filter(date_max__gte=today)\
        .filter(date_max__lte=interval_10).count()
    # Vaccins à faire (10 jours)
    vaccins = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association).filter(date_prochain_vaccin__gte=today)\
        .filter(date_prochain_vaccin__lte=interval_10).count()
    # Vaccins dépassés
    vaccins_retard = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association).filter(date_prochain_vaccin__lte=today) \
        .count()
    # Partie FA
    # Animaux en FA
    en_famille = Animal.objects.filter(inactif=False).filter(famille__isnull=False).count()
    # Familles disponibles
    disponibles = Famille.objects.filter(statut='DISPONIBLE').count()
    # Familles à visiter
    visites = Famille.objects.filter(statut='A_VISITER').count()
    # Animaux à placer
    a_placer = Animal.objects.filter(inactif=False).filter(famille__isnull=True).filter(statut__in=statuts_association).count()
    # Animaux à déplacer sous 10 jours
    a_deplacer_10 = Famille.objects.filter(animal__isnull=False).filter(indisponibilite__date_debut__gte=today)\
        .filter(indisponibilite__date_debut__lte=interval_10).count()
    # Animaux à déplacer manuellement (accueils arrivant à terme)
    accueils_a_deplacer = Accueil.objects.filter(statut=StatutAccueil.A_DEPLACER.name).count()

    #Taux de remplissage
    familles_occupees =  Famille.objects.filter(animal__isnull=False).distinct().count()
    total_familles = Famille.objects.filter(statut__in=('DISPONIBLE','OCCUPE')).count()
    if total_familles > 0:
        taux_remplissage = int((familles_occupees/total_familles) * 100)

    return render(request, "gestion_association/home.html", locals())


@login_required
def parametrage(request):
    selected = "parametrage"
    tarifs_adoption = TarifAdoption.objects.all()
    tarifs_sterilisation = TarifBonSterilisation.objects.all()
    return render(request, "gestion_association/parametrage.html", locals())
