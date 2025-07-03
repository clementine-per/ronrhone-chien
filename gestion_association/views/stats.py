import calendar
import locale
import sys

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.utils.timezone import datetime

from gestion_association.forms.stats import AnneeChoice, AnneeStatsForm, DureeAdoptionStatsForm
from gestion_association.models.adoption import Adoption

from django.db.models import F, ExpressionWrapper, IntegerField, Avg, Sum, Q
from django.db.models.functions import ExtractYear, ExtractMonth

from gestion_association.models.animal import Animal
from gestion_association.models.training_session import TrainingSession
from gestion_association.models.visite_medicale import VisiteMedicale


@login_required
def index(request):
    # Partie Adoptions
    labels_mois = []
    # Adoptions pour l'année en cours
    data_adoptions_current = []
    # Adoptions pour l'année précédente
    data_adoptions_past = []

    adoptions = Adoption.objects.all()
    # Pour que les mois soient en français
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    date = datetime.now()


    i = 1
    current = date.year
    past = date.year - 1

    while (i < 13):
        labels_mois.append(calendar.month_name[i])
        data_adoptions_current.append(adoptions.filter(date__year=date.year).filter(date__month=i).count())
        data_adoptions_past.append(adoptions.filter(date__year=date.year - 1).filter(date__month=i).count())
        i += 1

    # Prise en compte des filtres utilisateurs éventuels
    if request.method == "POST":
        adoption_duree_form = DureeAdoptionStatsForm(request.POST)
        if adoption_duree_form.is_valid():
            annee = adoption_duree_form.cleaned_data.get("annee")
            age = adoption_duree_form.cleaned_data.get("age")
            if annee:
                adoptions = adoptions.filter(date__year=annee)
            if age:
                adoptions = adoptions.annotate(start_year=ExtractYear('animal__date_naissance'),
                                   start_month=ExtractMonth('animal__date_naissance'),
                                   end_year=ExtractYear('date'),
                                   end_month=ExtractMonth('date'),
                ).annotate(
                    month_diff=ExpressionWrapper(
                        (F('end_year') - F('start_year')) * 12 + (F('end_month') - F('start_month')),
                        output_field=IntegerField()
                    )
                )
                if age == "CHIOT":
                    adoptions = adoptions.filter(month_diff__lt=6)
                elif age == "ADULTE":
                    adoptions = adoptions.filter(month_diff__gte=6).filter(month_diff__lt=96)
                elif age == "SENIOR":
                    adoptions = adoptions.filter(month_diff__gte=96)

    else:
        adoption_duree_form = DureeAdoptionStatsForm()


    # Partie Adoptions par durée
    labels_durees = ["Moins de 4 semaines", "1 à 2 mois", "2 à 5 mois", "Plus de 5 mois"]
    # Adoptions pour l'année en cours
    data_adoptions_duree = []
    data_adoptions_duree.append(adoptions.filter(nb_jours__lt=28).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=28).filter(nb_jours__lt=60).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=60).filter(nb_jours__lt=150).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=150).count())

    moyenne = adoptions.aggregate(moyenne=Avg('nb_jours'))
    total_adoptions = adoptions.count()

    # Partie données financières
    visites = VisiteMedicale.objects.all()
    trainings = TrainingSession.objects.all()

    adoptions_finance = Adoption.objects.filter(annule=False).exclude(montant=None)
    # Récupération de l'année saisie par l'utilisateur
    annee_finance = None
    if request.method == "POST":
        annee_form = AnneeStatsForm(request.POST)
        if annee_form.is_valid():
            annee_finance = annee_form.cleaned_data.get("annee_finance")
            if annee_finance:
                adoptions_finance = adoptions_finance.filter(date__year=annee_finance)
                visites = visites.filter(date__year=annee_finance)
                trainings = trainings.filter(date__year=annee_finance)
    else:
        annee_form = AnneeStatsForm()
    # Calcul du montant total des visites médicales
    montant_total_visites = visites.aggregate(montant_total=Sum('montant'))['montant_total'] or 0
    # Calcul du montant total des séances d'éducation
    montant_total_trainings = trainings.aggregate(montant_total=Sum('amount'))['montant_total'] or 0
    # Calcul du montant total des adoptions
    montant_total_adoptions = adoptions_finance.aggregate(montant_total=Sum('montant'))['montant_total'] or 0
    # Calcul résultat financier
    resultat_financier = montant_total_adoptions - montant_total_visites - montant_total_trainings
    # Moyenne du montant des visites médicales par animal et pour différents ages (age au moment de l'arrivée dans l'asso)
    chats = Animal.objects.annotate(start_year=ExtractYear('date_naissance'),
                                   start_month=ExtractMonth('date_naissance'),
                                   end_year=ExtractYear('date_arrivee'),
                                   end_month=ExtractMonth('date_arrivee'),
                ).annotate(
                    month_diff=ExpressionWrapper(
                        (F('end_year') - F('start_year')) * 12 + (F('end_month') - F('start_month')),
                        output_field=IntegerField()
                    )
                )

    chiots = chats.filter(month_diff__lt=6)
    adultes = chats.filter(month_diff__gte=6).filter(month_diff__lt=96)
    seniors = chats.filter(month_diff__gte=96)
    years = []

    if annee_finance:
        years = [annee_finance]
    else:
        years = [(tag.value) for tag in AnneeChoice]
        
    moyenne_par_animal = Animal.objects.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_chiots = chiots.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_adultes = adultes.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_seniors = seniors.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0

    # Données pour graphique répartition par types de visites
    labels_types = ["Soins groupés", "Vaccination seule", "Stérilisation seule", "Urgence et Chirurgie", "Consultations", "Autres"]
    data_type_visites = []
    print (visites.filter(type_visite__in=["PACK", "PACK_STE"]).aggregate(Sum('montant'))['montant__sum'] or 0)
    sys.stdout.flush()
    data_type_visites.append(float(visites.filter(type_visite__in=["PACK", "PACK_STE"]).aggregate(Sum('montant'))['montant__sum'] or 0))
    data_type_visites.append(float(visites.filter(type_visite__in=["VAC_PRIMO", "VAC_RAPPEL"]).aggregate(Sum('montant'))['montant__sum'] or 0))
    data_type_visites.append(float(visites.filter(type_visite__in=["STE"]).aggregate(Sum('montant'))['montant__sum'] or 0))
    data_type_visites.append(float(visites.filter(type_visite__in=["URGENCE", "CHIRURGIE"]).aggregate(Sum('montant'))['montant__sum'] or 0))
    data_type_visites.append(float(visites.filter(type_visite__in=["CONSULT"]).aggregate(Sum('montant'))['montant__sum'] or 0))
    data_type_visites.append(float(visites.filter(type_visite__in=["AUTRE","IDE", "OSTEO"]).aggregate(Sum('montant'))['montant__sum'] or 0))


    return render(request, "gestion_association/stats.html", locals())