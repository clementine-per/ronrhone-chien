from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from contract.utils import *
from gestion_association.models.animal import Animal


@login_required
def generate_contract(request, pk):
    # Animal data
    animal = Animal.objects.get(pk=pk)

    # Data for the canvas (reportlab)
    nb_page = 1
    # Create the HttpResponse object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Contrat_{}_{}.pdf"'.format(animal.nom, animal.id)
    p = canvas.Canvas(response)

    header(p, animal)
    personal_infos(p, animal)
    infos_animal(p, animal)
    # Page 2
    next_page(p, nb_page)
    educ_amounts(p, animal, 28)
    contract_pieces(p, animal, 20)
    payment(p, 16)
    # Page 3
    next_page(p, nb_page)
    engagement(p, animal, 28)
    next_page(p, nb_page)
    # Finalize the canvas
    p.save()

    return response