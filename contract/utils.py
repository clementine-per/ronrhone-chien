

# Styles and colors for generating the contract
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from reportlab.lib.colors import black, red
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph

from gestion_association.models import OuiNonChoice

ronrhone_color = '#00bfff'
titleStyle = ParagraphStyle(name="Style", textColor=ronrhone_color, fontSize=0.8 * cm, borderWidth=2,
                            borderColor=ronrhone_color,
                            borderRadius=0.2 * cm,
                            borderPadding=(0.2 * cm, 0.5 * cm, 1.5 * cm, 0.5 * cm))
subtitleStyle = ParagraphStyle(name="Style", textColor=black, fontSize=0.7 * cm, borderWidth=1,
                               borderColor=ronrhone_color,
                               # top , right, bottom, left
                               borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
blackParagraphStyle = ParagraphStyle(name="Black", textColor="black", alignement=TA_JUSTIFY, fontSize=0.4 * cm,
                                     fontName="Helvetica", borderPadding=(0.5 * cm, 0.5 * cm, 0.5 * cm, 0.5 * cm))



def next_page(p, nb_page):
    # page footer
    page_footer(p, nb_page)
    # Go to next page
    p.showPage()
    return nb_page + 1


def page_footer(p, nb_page):
    p.setFont("Times-Italic", 0.35 * cm)
    p.setFillColor('#808080')
    p.drawString(2.7 * cm, 0.2 * cm,
                 "Association Ron’Rhône - 98, chemin de la Combe Moussin 38270 BEAUFORT - n° SIRET : 82140540400012")
    p.setFont("Times-Bold", 0.5 * cm)
    p.setFillColor("#000000")
    p.drawString(20 * cm, 0.2 * cm, f"{str(nb_page)}/3")


def header(p, animal):
    # logo header
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/logo.PNG",
        0.75 * cm,
        23.25 * cm,
        width=5.5 * cm,
        height=5.5 * cm,
        mask="auto",
    )

    para = Paragraph("{} <br/><br/> {} <br/>" \
                     .format("Contrat d'adoption de ", animal.nom)
                     , style=titleStyle)
    para.wrap(8 * cm, 7 * cm)
    para.drawOn(p, 8.5 * cm, 26 * cm)


def personal_infos(p, animal):
    # Personal information of the person adopting

    para = Paragraph("{} <br/>" \
                     .format("Informations personnelles de l'adoptant")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, 22.5 * cm)
    p.setFont("Times-Bold", 0.45 * cm)
    p.drawString(2 * cm, 21.3 * cm, f"- Nom et prénom : {animal.adoptant.prenom} {animal.adoptant.nom}")
    date_birth= ""
    if animal.adoptant.date_naissance:
        date_birth = animal.adoptant.date_naissance.strftime("%d/%m/%Y")
    p.drawString(2 * cm, 20.5 * cm, f"- Date de naissance : {date_birth}")
    p.drawString(2 * cm, 19.7 * cm, f"- Adresse postale : {animal.adoptant.adresse}, {animal.adoptant.code_postal}")
    p.drawString(2 * cm, 18.9 * cm, f"- Téléphone : {animal.adoptant.telephone}")
    p.drawString(8 * cm, 18.9 * cm, f"- Adresse e-mail : {animal.adoptant.email}")
    p.drawString(2 * cm, 18.1 * cm, f"- Profession : {animal.adoptant.profession}")

    # Checkbox
    styleSquare = ParagraphStyle(
        name="Style",
        borderWidth=1,
        borderColor="#000000",
        borderPadding=(0.2 * cm, 0.1 * cm, 0.2 * cm, 0.1 * cm),
    )
    para = Paragraph(" ", style=styleSquare)
    para.wrap(0.2 * cm, 1 * cm)
    para.drawOn(p, 2.2 * cm, 17.5 * cm)

    p.setFont("Helvetica", 0.4 * cm)
    para = Paragraph("Moi, l'adoptant, déclare consentir à ce que l'Association Ron'Rhône transmette "
                     "ce contrat d'adoption à la Fondation Capellino/Almo Nature, dans le cadre "
                     "de la bonne mise en œuvre du projet Companion Animal For Life, "
                     "dont l’association est partenaire et uniquement dans ce cadre."
                     "<br/>Plus d’information sur www.companionanimalforlife.org ou à "
                     "partir de ce QR code")
    para.wrap(11 * cm, 15 * cm)
    para.drawOn(p, 3 * cm, 14.8 * cm)
    # QR code
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/QR.jpg",
        15 * cm,
        14.6 * cm,
        width=3.6 * cm,
        height=3.6 * cm,
        mask="auto",
    )


def infos_animal(p, animal):
    para = Paragraph("{} <br/>" \
                     .format("Informations sur le chien")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 16 * cm)
    para.drawOn(p, 4.30 * cm, 13.5 * cm)

    p.setFont("Helvetica", 0.4 * cm)
    p.drawString(2 * cm, 12.35 * cm, f"- Identification : {animal.identification}")
    p.drawString(2 * cm, 11.75 * cm, f"- Nom du chien : {animal.nom}")
    p.drawString(2 * cm, 11.15 * cm, f"- Vaccination : {animal.get_type_vaccin_display()}")
    p.drawString(2 * cm, 10.55 * cm, "- Sexe : " + animal.sexe)
    p.drawString(11 * cm, 10.55 * cm, "- Race : " + animal.race)
    date_naissance = "-"
    if animal.date_naissance:
        date_naissance = animal.date_naissance.strftime("%d/%m/%Y")
    p.drawString(2 * cm, 9.95 * cm, "- Date de naissance : " + date_naissance)
    p.drawString(11 * cm, 9.95 * cm, "- Robe : " + animal.color)
    p.drawString(2 * cm, 9.35 * cm, "- Signes particuliers : ")

    p.drawString(2 * cm, 8.5 * cm, f"Frais d'adoption : {animal.get_latest_adoption().montant} €")
    sterilisation = ""
    if animal.sterilise == OuiNonChoice.OUI.name:
        sterilisation = "sterilisation, "
    p.drawString(2 * cm, 8 * cm, f"Soins inclus dans ces frais : {sterilisation} "
                                 f"identification, vaccination, bilan comportemental,")
    p.drawString(2 * cm, 7.5 * cm, "antiparasitaires internes et externes")
    p.drawString(2 * cm, 7 * cm, f"Le prochain rappel de vaccin de {animal.nom} est à"
                                   f" faire le : {animal.date_prochain_vaccin.strftime('%d/%m/%Y')}")
    p.setFont("Helvetica-Bold", 0.4 * cm)
    p.drawString(2 * cm, 6.5 * cm, "Attention, ce rappel est à votre charge !")
    if animal.sterilise == OuiNonChoice.NON.name:
        p.setFont("Helvetica", 0.4 * cm)
        if animal.date_naissance:
            date_ste_min_str = (animal.date_naissance + relativedelta(months=10)).strftime("%d/%m/%Y")
            date_ste_max_str = (animal.date_naissance + relativedelta(months=12)).strftime("%d/%m/%Y")
        p.drawString(2 * cm, 5.8 * cm, f"Étant donné son âge, {animal.nom} devra être stérilisé(e) entre le "
                                     f"{date_ste_min_str} et le {date_ste_max_str}. Aucune saillie, ")
        p.drawString(2 * cm, 5.3 * cm, f"qu’elle soit volontaire ou accidentelle, n’est autorisée. "
                                       f"En cas de gestation, {animal.nom} sera récupéré(e)")
        p.drawString(2 * cm, 4.8 * cm, "par l’Association sans remboursement des frais engagés"
                                       " et l'adoption sera annulée.")
        p.drawString(2 * cm, 4.3 * cm, "Un chèque de caution d’un montant de 200€ sera à fournir à la "
                                       "famille d’accueil lors du transfert")
        p.drawString(2 * cm, 3.8 * cm, f"de {animal.nom}.")


def educ_amounts(p, animal, offset):
    p.setFont("Helvetica", 0.4 * cm)
    p.drawString(2 * cm, offset * cm, f"Affin de permettre à {animal.nom} "
                                      f"d’appréhender au mieux son arrivée dans votre foyer, un forfait ")
    p.drawString(2 * cm, (offset-0.5) * cm, "de 1heure(s) d’éducation est nécessaire.")
    p.drawString(2 * cm, (offset-1) * cm, "Il vous faut organiser cette séance avec notre éducatrice : "
                                          "Super Chien Educ / Aurélie ")
    p.drawString(2 * cm, (offset - 1.5) * cm, "CORNILLON au 06.35.93.39.94")
    p.drawString(2 * cm, (offset - 2.5) * cm, "Cette heure vous est proposée au tarif Associatif (30€), "
                                              "à régler avec les frais d’adoption ")
    p.drawString(2 * cm, (offset - 3) * cm, f"avant l’arrivée de {animal.nom}.")

    ammount_block_style = ParagraphStyle(name="Style", textColor=black, fontSize=0.5 * cm,
                                         fontName="Helvetica", borderWidth=2,
                                borderColor=black, leading=0.6 * cm,
                                borderRadius=0.2 * cm,
                                borderPadding=(0.2 * cm, 0.5 * cm, 0.5 * cm, 1 * cm))
    para = Paragraph(f" Somme totale à régler : {animal.get_latest_adoption().montant + Decimal(30)} € <br/>"
                     f" Acompte déjà versé : "
                     f"{animal.get_latest_adoption().montant - animal.get_latest_adoption().montant_restant} € <br/>"
                     f" Somme restant due : {animal.get_latest_adoption().montant_restant} €"
                     , style=ammount_block_style)
    para.wrap(14 * cm, 16 * cm)
    para.drawOn(p, 2.7 * cm, (offset - 5.5) * cm)
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/star.PNG",
        2 * cm,
        (offset - 4.2) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/star.PNG",
        2 * cm,
        (offset - 4.8) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/star.PNG",
        2 * cm,
        (offset - 5.4) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )


def contract_pieces(p, animal, offset):
    para = Paragraph("{} <br/>" \
                     .format("Pièces à joindre au contrat")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, offset * cm)
    p.setFont("Helvetica", 0.4 * cm)
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/star.PNG",
        2 * cm,
        (offset - 1.5) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawString(2.5 * cm, (offset - 1.5) * cm, "Photocopie d'une pièce d'identité")
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/star.PNG",
        2 * cm,
        (offset - 2) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawString(2.5 * cm, (offset - 2) * cm, "Justificatif de domicile de moins de trois mois")
    if animal.sterilise == OuiNonChoice.NON.name:
        p.drawImage(
            f"{settings.STATIC_ROOT}/img/star.PNG",
            2 * cm,
            (offset - 2.5) * cm,
            width=0.5 * cm,
            height=0.5 * cm,
            mask="auto",
        )
        p.drawString(2.5 * cm, (offset - 2.5) * cm, "Chèque de caution de 200,00€ à l’ordre de "
                                                    "l’Association RONRHONE.")


def payment(p, offset):
    # Personal information of the person adopting

    para = Paragraph("{} <br/>" \
                     .format("Règlement")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, offset * cm)
    p.setFont("Helvetica-Bold", 0.35 * cm)
    p.setFillColor(red)
    p.drawString(5 * cm, (offset - 1.4) * cm, "NOUS REFUSONS LE PAIEMENT PAR CHÈQUE")
    p.setFont("Helvetica", 0.4 * cm)
    p.setFillColor(black)
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/fleche.PNG",
        2 * cm,
        (offset - 2.1) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawString(2.5 * cm, (offset - 2) * cm, " Virement standard :")
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/RIB.PNG",
        2 * cm,
        (offset - 7.6) * cm,
        width=17 * cm,
        height=5.5 * cm,
        mask="auto",
    )
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/fleche.PNG",
        2 * cm,
        (offset - 8.2) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawString(2.5 * cm, (offset - 8.1) * cm, " Lydia : 06.64.62.32.07 ")
    p.drawImage(
        f"{settings.STATIC_ROOT}/img/fleche.PNG",
        2 * cm,
        (offset - 8.7) * cm,
        width=0.5 * cm,
        height=0.5 * cm,
        mask="auto",
    )
    p.drawString(2.5 * cm, (offset - 8.6) * cm, " Paylib : 06.64.62.32.07")
    p.drawString(2.5 * cm, (offset - 9.6) * cm, "Si vous le souhaitez, un reçu de paiement "
                                              "peut vous être envoyé par mail.")
    p.setFillColor(red)
    p.drawString(2.5 * cm, (offset - 10.5) * cm, "Le restant dû devra être réglé sous 3 jours "
                                               "suivant la signature de ce contrat et ")
    p.drawString(2.5 * cm, (offset - 11) * cm, "l'animal devra être récupéré au maximum 7 jours "
                                                 "après la réception du virement,sans quoi")
    p.drawString(2.5 * cm, (offset - 11.5) * cm, "ce contrat sera caduc et l’adoption annulée "
                                                 "sans remboursement.")

def engagement(p, animal, offset):
    para = Paragraph("{} <br/>" \
                     .format("Engagement")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, offset * cm)
    para = Paragraph(
        "Je soussigné <font color=red>[NOM]__________________[PRENOM]______________________</font> certifie \
                 l'exactitude des information renseignées sur ce contrat et m'engage à respecter la charte \
                jointe à ce dernier. Le non-respect de ce contrat, et/ou de la charte fournie  avec celui-ci,"
        " entraîne sa résiliation et ainsi la restitution <font color=red>immédiate</font> "
        "du chien à l'association <font face='helvetica-bold'>Ron'Rhône</font>, "
        "sans remboursement des frais d'adoption. <br/> L'identification au nom du nouveau propriétaire "
        "sera établie deux mois après la date de l'adoption en relation avec une visite, soit aux environs du"
        "__/__/__. Dans cette même période, l'association et le nouveau propriétaire devront entretenir "
        "un rapport régulier pour s'assurer du bien-être de l'animal dans son nouvel habitat. <br/>"
        "Nous vous rappelons que nous restons à votre disposition pour "
        "toutes questions concernant le chien avant et après l'adoption. <br/> <br/>"
        "Imprimé en deux exemplaire, un pour chacune des parties.",
        style=blackParagraphStyle
    )
    para.wrap(17 * cm, 9 * cm)
    para.drawOn(p, 2 * cm, (offset-6.5) * cm)

    boldParagraphStyle = ParagraphStyle(name="Black", textColor="black", alignement=TA_JUSTIFY, fontSize=0.4 * cm,
                                         fontName="Helvetica-bold", borderPadding=(0.5 * cm, 0.5 * cm, 0.5 * cm, 0.5 * cm))
    para = Paragraph("Le __/__/__ <br/> Signature de l'adoptant, <br/> précédée de la mention « Lu et Approuvé » ",
                     style=boldParagraphStyle)
    para.wrap(10 * cm, 15 * cm)
    para.drawOn(p, 2 * cm, (offset - 8) * cm)
    para = Paragraph("Le __/__/__ <br/> Signature d'un(e) représentant(e) <br/> de l'association <br/> ",
                     style=boldParagraphStyle)
    para.wrap(10 * cm, 15 * cm)
    para.drawOn(p, 12 * cm, (offset - 8) * cm)

