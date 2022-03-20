from django.forms import ModelForm

from gestion_association.models.animal import Preference


class PreferenceFaForm(ModelForm):
    class Meta:
        model = Preference
        fields = (
            "exterieur",
            "rehabilitation",
            "biberonnage",
            "ville",
            "congeneres",
            "chats",
            "chats",
            "enfants"
        )
        labels = {
            'chats': 'Présence de chats',
            'congeneres': "Présence d'autres chiens",
            'ville': 'Vie en ville',
            'enfants': 'Enfants de moins de 12 ans'
        }


class PreferenceAnimalForm(ModelForm):
    class Meta:
        model = Preference
        fields = "__all__"
