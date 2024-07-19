from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from gestion_association.forms.training_session import TrainingSessionForm
from gestion_association.models.animal import Animal
from gestion_association.models.person import Person
from gestion_association.models.training_session import TrainingSession


class UpdateTrainingSession(LoginRequiredMixin, UpdateView):
    model = TrainingSession
    form_class = TrainingSessionForm
    template_name = "gestion_association/training_session/training_session_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.animal.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateTrainingSession, self).get_context_data(**kwargs)
        context['title'] = "Mettre à jour " + str(self.object)
        return context


@login_required
def create_training_from_animal(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Session d'éducation pour " + animal.nom
    if request.method == "POST":
        form = TrainingSessionForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("detail_animal", pk=animal.id)

    else:
        form = TrainingSessionForm()
        form.fields["animal"].initial = animal

    return render(request, "gestion_association/training_session/training_session_form.html", locals())

@login_required
def training_session_price(request):
    montant = ""
    if request.POST["trainer_person"]:
        educateur = Person.objects.get(id=request.POST["trainer_person"])
        type = request.POST["type_training"]
        if type and type == "BILAN" and educateur.tarif_bilan:
            return JsonResponse(
                {
                    "montant_seance": educateur.tarif_bilan,
                }
            )
        if educateur.tarif_seance:
            montant = educateur.tarif_seance
    return JsonResponse(
        {
            "montant_seance": montant,
        }
    )
