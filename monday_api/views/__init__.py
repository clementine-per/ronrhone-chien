from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required()
def index(request):
    selected = "monday"
    title = "Intégration avec Monday"
    return render(request, "monday_api/index.html", locals())