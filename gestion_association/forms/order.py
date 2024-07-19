from django.forms import ModelForm
from gestion_association.models.order import Order


class OrderForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Order
        fields = (
            "date",
            "content",
            "amount",
            "comment",
        )

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'