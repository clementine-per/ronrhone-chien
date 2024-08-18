from datetime import datetime

import requests
import json

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.template.defaultfilters import slugify

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal, Preference, SexeChoice
from gestion_association.models.person import Person
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

api_key = settings.MONDAY_KEY
api_url = settings.MONDAY_URL
headers = {"Authorization": api_key, "API-version": "2023-10"}


@login_required
def check_api_animals(request):
    selected = "monday"
    title = "Intégration avec Monday : Prises en charge"

    query = get_query()
    data = {'query': query}
    r = requests.post(url=api_url, json=data, headers=headers)
    animals = []
    errors = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    # Chaque ligne est une adoption
    for elt in content:
        animal = get_animal_from_values(elt)
        animals.append(animal)

    nb_results = len(animals)

    return render(request, "monday_api/animals_to_import.html", locals())


@login_required
def integrate_animals(request):
    selected = "monday"
    title = "Intégration avec Monday : Prises en charge"
    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    if not r.ok:
        raise Exception(r.content)
    imports = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    logger.info("DEBUT Import des prises en charge")
    # Chaque ligne est une adoption
    for elt in content:
        try:
            with transaction.atomic():
                animal = get_animal_from_values(elt)
                animal.pre_visite = OuiNonChoice.NON.name
                animal.preference.save()
                animal.ancien_proprio.save()
                animal.save()
                imports.append("Import de l'animal de " + str(animal) + " dont l'ancien propriétaire est "
                               + str(animal.ancien_proprio))
                # Mise à jour du statut dans monday
                mutation_request = get_modify_status_query(elt["id"])
                data = {'query': mutation_request}
                r = requests.post(url=api_url, json=data, headers=headers)
                logger.warning("Import de l'animal de " + str(animal) + " dont l'ancien propriétaire est "
                               + str(animal.ancien_proprio))

        except Exception as e:
            imports.append("Erreur pour l'import de "+ str(animal) + " : " + str(e))
            logger.warning("Erreur pour l'import de "+ str(animal) + " : " + str(e))
    logger.info("FIN Import des prises en charge")
    return render(request, "monday_api/animals_import_results.html", locals())


def get_query():
    return 'query { boards(ids: [3377298117]) {\
    groups(ids: ["1665769578_p_le_chiens_demande"]) {\
      items_page (limit: 15, query_params: {rules: [{column_id: "status", compare_value: [157]}], operator: and})\
      { items {\
        id\
        name\
        column_values(ids: ["statut", "texte78","status","texte8", "chiffre5",\
        "texte", "texte4","t_l_phone","e_mail", "lieu","texte37", "date",\
        "statut_19", "texte3","statut_124","statut_175", "statut_17",\
        "long_texte_5","date_18__1", "s_lection_unique5__1"\
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
    return 'mutation { change_column_value(item_id:' +item_id +', board_id: 3377298117,\
     column_id: "status", value: "{\\\"index\\\":1}") {id\
  }\
}'


def get_animal_from_values(values):
    columns = values["column_values"]
    personne = Person()
    animal = Animal()
    preference = Preference()
    # Nom de l'animal
    animal.nom = values["name"]
    for value in columns:
        # Nom
        if value["id"] == "texte":
            personne.nom = value["text"].upper()
        # Commentaire
        if value["id"] == "texte78" or value["id"] == "long_texte5":
            animal.commentaire += value["text"] + " "
        # Race
        if value["id"] == "texte8":
            animal.race = value["text"]
        # Identification
        if value["id"] == "chiffre5":
            animal.identification = value["text"]
        # Date de naissance
        if value["id"] == "date":
            animal.date_naissance = datetime.strptime(value["text"], '%Y-%m-%d').date()
        # Date de vaccin
        if value["id"] == "date_18__1":
            if value["text"]:
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.vaccin_ok = OuiNonChoice.OUI.name
                date_vaccin = datetime.strptime(value["text"], '%Y-%m-%d').date()
                animal.date_dernier_vaccin = date_vaccin
                animal.date_prochain_vaccin = date_vaccin + relativedelta(years=3)
        # Congénères et chats
        elif value["id"] == "statut_19" and value["text"]:
            if "chats" in value["text"].lower():
                preference.chats = OuiNonChoice.OUI.name
            else:
                preference.chats = OuiNonChoice.NON.name
            if "chiens" in value["text"].lower():
                preference.congeneres = OuiNonChoice.OUI.name
            else :
                preference.congeneres = OuiNonChoice.NON.name
        # Sterilisation
        elif value["id"] == "s_lection_unique5__1":
            if not value["text"] or "non" in value["text"].lower():
                animal.sterilise = OuiNonChoice.NON.name
            else:
                animal.sterilise = OuiNonChoice.OUI.name
        # Genre
        elif value["id"] == "statut_124":
            if value["text"] == "Femelle":
                animal.sexe = SexeChoice.F.name
            elif value["text"] == "Mâle":
                animal.sexe = SexeChoice.M.name
            else:
                animal.sexe = SexeChoice.NI.name
        # Soins
        elif value["id"] == "statut_175":
            if "stérilisé" in value["text"].lower():
                animal.sterilise = OuiNonChoice.OUI.name
            if "vacciné" in value["text"].lower():
                animal.vaccin_ok = OuiNonChoice.OUI.name
                animal.primo_vaccine = OuiNonChoice.OUI.name
        # Circonstances d'abandon
        elif value["id"] == "statut_17":
            animal.circonstances = value["text"]
        # Prénom
        elif value["id"] == "texte4":
            personne.prenom = value["text"]
        # Adresse
        elif value["id"] == "lieu":
            personne.adresse = value["text"]
        # Code postal
        elif value["id"] == "code_postal":
            personne.code_postal = value["text"]
        # Ville
        elif value["id"] == "texte37":
            personne.ville = value["text"]
        # Téléphone
        elif value["id"] == "t_l_phone":
            telephone = value["text"]
            if not telephone.startswith('0'):
                telephone = "+" + telephone
            personne.telephone = telephone
        # Email
        elif value["id"] == "e_mail":
            personne.email = value["text"]
    # Check si l'adoptant est déjà en base
    nom_prenom_key = f"{slugify(personne.prenom)}.{personne.nom}"
    existing_person = Person.objects.filter(nom_prenom_key=nom_prenom_key.lower())
    if existing_person:
        existing_person[0].is_ancien_proprio = True
        animal.ancien_proprio = existing_person[0]
    else:
        personne.is_ancien_proprio = True
        animal.ancien_proprio = personne
    animal.preference = preference
    return animal