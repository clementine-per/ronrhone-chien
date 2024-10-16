from datetime import timedelta
from decimal import Decimal
from difflib import get_close_matches

import requests
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.functions import Lower
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption
from gestion_association.models.animal import Animal, statuts_association
from gestion_association.models.person import Person
from gestion_association.views.adoption import get_montant_adoption
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

api_key = settings.MONDAY_KEY
api_url = settings.MONDAY_URL
headers = {"Authorization": api_key, "API-version": "2023-10"}


@login_required
def check_api_adoptions(request):
    selected = "monday"
    title = "Intégration avec Monday : Adoptions"

    query = get_query()
    data = {'query': query}
    r = requests.post(url=api_url, json=data, headers=headers)
    adoptions = []
    errors = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    # Chaque ligne est une adoption
    for elt in content:
        adoption = get_adoption_from_values(elt)
        if adoption == "Not Found":
            errors.append("L'animal " + elt["name"] + " n'a pas été trouvé.")
        elif adoption:
            adoptions.append(adoption)

    nb_results = len(adoptions)

    return render(request, "monday_api/adoptions_to_import.html", locals())


@login_required
def integrate_adoptions(request):
    selected = "monday"
    title = "Intégration avec Monday : Adoptions"
    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    if not r.ok:
        raise Exception(r.content)
    imports = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    logger.info("DEBUT Import d'adoptions")
    # Chaque ligne est une adoption
    for elt in content:
        try:
            with transaction.atomic():
                adoption = get_adoption_from_values(elt)
                if adoption == "Not Found":
                    imports.append("L'animal " + elt["name"] + " n'a pas été trouvé.")
                    logger.warning("L'animal " + elt["name"] + " n'a pas été trouvé.")
                elif adoption:
                    adoption.pre_visite = OuiNonChoice.NON.name
                    adoption.visite_controle = OuiNonChoice.NON.name
                    today = timezone.now().date()
                    two_months = today + timedelta(days=2 * 30)
                    adoption.date_visite = two_months
                    adoption.adoptant.save()
                    adoption.animal.save()
                    adoption.save()
                    imports.append("Import de l'adoption de " + str(adoption.animal) + " par " + str(adoption.adoptant))
                    # Mise à jour du statut dans monday
                    mutation_request = get_modify_status_query(elt["id"])
                    data = {'query': mutation_request}
                    r = requests.post(url=api_url, json=data, headers=headers)
                    logger.warning("Import de l'adoption de " + str(adoption.animal) + " par " + str(adoption.adoptant))

        except Exception as e:
            imports.append("Erreur pour l'import de "+ str(adoption.adoptant) + " : " + str(e))
            logger.warning("Erreur pour l'import de l'adoptant "+ str(adoption.adoptant) + " : " + str(e))
    logger.info("FIN Import d'adoptions")
    return render(request, "monday_api/familles_import_results.html", locals())


def get_query():
    return 'query { boards(ids: [3101910912]) {\
    groups(ids: ["1660740380_cn_reponses_adoptio"]) {\
    items_page (limit: 15, query_params: {rules: [{column_id: "statut", compare_value: [0]}], operator: and})\
      { items {\
        id\
        name\
        column_values(ids: ["statut", "nom___pr_nom","texte8","t_l_phone", "adresse_postale__n___rue_",\
        "code_postal", "ville", "adresse_e_mail"\
         ]) {\
          id\
          value\
          text\
        }\
      } }\
    }\
  } }'


def get_modify_status_query(item_id):
    # Passer au statut Integré
    return 'mutation { change_column_value(item_id:' +item_id +', board_id: 3101910912,\
     column_id: "statut", value: "{\\\"index\\\":3}") {id\
  }\
}'


def get_adoption_from_values(adoption_values):
    adoption_columns = adoption_values["column_values"]
    personne = Person()
    adoption = Adoption()
    for value in adoption_columns:
        # Statut
        if value["id"] == "statut":
            animal_name = adoption_values["name"]
            # close_match is case sensitive
            corresponding_matches = get_close_matches(animal_name.lower(), get_animal_names(), 2, 0.7)
            if not len(corresponding_matches) > 0:
                return "Not Found"
            corresponding_match = corresponding_matches[0]
            animal = Animal.objects.get(nom__iexact=corresponding_match)
        # Nom
        elif value["id"] == "nom___pr_nom":
            personne.nom = value["text"].upper()
        # Prénom
        elif value["id"] == "texte8":
            personne.prenom = value["text"]
        # Adresse
        elif value["id"] == "adresse_postale__n___rue_":
            personne.adresse = value["text"]
        # Code postal
        elif value["id"] == "code_postal":
            personne.code_postal = value["text"]
        # Ville
        elif value["id"] == "ville":
            personne.ville = value["text"]
        # Téléphone
        elif value["id"] == "t_l_phone":
            telephone = value["text"]
            if not telephone.startswith('0'):
                telephone = "+" + telephone
            personne.telephone = telephone
        # Email
        elif value["id"] == "adresse_e_mail":
            personne.email = value["text"]
    # Check si l'adoptant est déjà en base
    nom_prenom_key = f"{slugify(personne.prenom)}.{personne.nom}"
    existing_person = Person.objects.filter(nom_prenom_key=nom_prenom_key.lower())
    if existing_person:
        existing_person[0].is_adoptante = True
        adoption.adoptant = existing_person[0]
    else:
        personne.is_adoptante = True
        adoption.adoptant = personne
    adoption.animal = animal
    adoption.montant = get_montant_adoption(animal)
    adoption.montant_restant = adoption.montant
    if adoption.montant and adoption.acompte_verse == OuiNonChoice.OUI.name:
        adoption.montant_restant = adoption.montant - Decimal(100)
    return adoption


def get_animal_names():
    return list(Animal.objects.filter(statut__in=statuts_association).values_list(Lower('nom'), flat=True))