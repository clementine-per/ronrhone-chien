from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from gestion_association.forms.order import OrderForm
from gestion_association.models.animal import Animal
from gestion_association.models.order import Order


class UpdateOrder(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "gestion_association/order/order_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.animal.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateOrder, self).get_context_data(**kwargs)
        context['title'] = "Mettre à jour une commande "
        return context


@login_required
def create_order_from_animal(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Commande/Achat pour " + animal.nom
    if request.method == "POST":
        form = OrderForm(data=request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.animal = animal
            order.save()
            return redirect("detail_animal", pk=animal.id)

    else:
        form = OrderForm()

    return render(request, "gestion_association/order/order_form.html", locals())