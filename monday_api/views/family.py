import json
import sys

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render

from gestion_association.models import OuiNonChoice
from gestion_association.models.famille import Famille, StatutFamille
from gestion_association.models.person import Person

api_key = settings.MONDAY_KEY
api_url = settings.MONDAY_URL
headers = {"Authorization": api_key, "API-version": "2023-10"}


@login_required()
def check_api_fa(request):
    selected = "monday"
    title = "Intégration avec Monday : Familles d'accueil"

    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    print(json.loads(r.content))
    sys.stdout.flush()
    familles = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    # Chaque ligne est une famille d'accueil
    for fa in content:
        famille = get_fa_from_values(fa)
        if famille:
            familles.append(famille)
    nb_results = len(familles)

    return render(request, "monday_api/familles_to_import.html", locals())


@login_required()
def integrate_fa(request):
    selected = "monday"
    title = "Intégration avec Monday : Familles d'accueil"
    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    if not r.ok:
        raise Exception(r.content)
    imports = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items_page"]["items"]
    # Chaque ligne est une famille d'accueil
    for fa in content:
        try:
            with transaction.atomic():
                famille = get_fa_from_values(fa)
                if famille:
                    famille.personne.save()
                    famille.save()
                    imports.append("Import famille d'accueil de " + str(famille.personne))

                    # Mise à jour du statut dans monday
                    mutation_request = get_modify_status_query(fa["id"])
                    data = {'query': mutation_request}
                    r = requests.post(url=api_url, json=data, headers=headers)

        except Exception as e:
            imports.append("Erreur pour l'import de "+ str(famille.personne) + " : " + str(e))

    return render(request, "monday_api/familles_import_results.html", locals())


def get_query():
    return 'query { boards(ids: [3379463594]) {\
    groups(ids: ["1665848993_p_le_chiens_questio"]) {\
      items_page { items {\
        id\
        name\
        column_values(ids: ["statut96", "s_lection_multiple","s_lection_multiple1", \
        "dropdown", "texte", "t_l_phone", "e_mail", "long_texte4", "status",\
         "texte3", "texte2", "texte1", "texte5", "texte8","texte9", "s_lection_unique3"]) {\
          id\
          value\
          text\
        }\
      } }\
    }\
  } }'


def get_modify_status_query(item_id):
    # statut96 correspond à la colonne statut et l'index 3 au statut "Disponible actuellement"
    return 'mutation { change_column_value(item_id:' +item_id +', board_id: 3379463594,\
     column_id: "statut96", value: "{\\\"index\\\":8}") {id\
  }\
}'


def get_fa_from_values(fa_values):
    fa_columns = fa_values["column_values"]
    personne = Person()
    famille = Famille()
    famille.nb_places = 1
    for value in fa_columns:
        # Statut
        if value["id"] == "statut96":
            # On ne veux que les FA à intégrer
            if value["text"] != "A intégrer":
                return None
        # Nom
        elif value["id"] == "texte":
            personne.nom = value["text"].upper()
        # Prénom
        elif value["id"] == "texte3":
            personne.prenom = value["text"]
        # Adresse
        elif value["id"] == "texte1":
            personne.adresse = value["text"]
        # Code postal
        elif value["id"] == "texte5":
            personne.code_postal = value["text"]
        # Ville
        elif value["id"] == "texte8":
            personne.ville = value["text"].upper()
        # Téléphone
        elif value["id"] == "t_l_phone":
            telephone = value["text"]
            if not telephone.startswith('0'):
                telephone = "+" + telephone
            personne.telephone = telephone
        # Email
        elif value["id"] == "e_mail":
            personne.email = value["text"]
        # FA - Commentaire
        elif value["id"] == "texte9":
            famille.commentaire = value["text"]
        # FA - Détail des accueils acceptés
        elif value["id"] == "s_lection_multiple":
            famille.detail_places = value["text"]
        # FA - Animaux FA
        elif value["id"] == "dropdown":
            famille.autres_animaux = value["text"]
            animals = value["text"].lower()
            if "chat" in animals:
                famille.chats = OuiNonChoice.OUI.name
            else:
                famille.chats = OuiNonChoice.NON.name
            if "chien" in animals:
                famille.congeneres = OuiNonChoice.OUI.name
            else:
                famille.congeneres = OuiNonChoice.NON.name
        # FA - Composition du foyer
        elif value ["id"] == "texte2":
            famille.household = value["text"]
        # FA - Temps d'absence
        elif value ["id"] == "long_texte4":
            famille.absence = value["text"]
        # FA - Véhicule
        elif value["id"] == "status":
            famille.vehicule = value["text"]
        # FA - Logement
        elif value["id"] == "s_lection_unique3":
            famille.house = value["text"]

    personne.is_famille = True
    famille.statut = StatutFamille.DISPONIBLE.name
    famille.personne = personne
    return famille