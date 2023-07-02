from django.forms import ModelForm

from gestion_association.forms.visite_medicale import statuts_association_adopte
from gestion_association.models.animal import Animal
from gestion_association.models.training_session import TrainingSession


class TrainingSessionForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = TrainingSession
        fields = (
            "date",
            "type_training",
            "trainer",
            "comment",
            "amount",
            "animal",
        )

    def __init__(self, *args, **kwargs):
        super(TrainingSessionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'
        self.fields['animal'].queryset = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association_adopte)