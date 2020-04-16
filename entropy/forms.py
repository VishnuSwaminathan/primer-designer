from . import models
from django.forms import ModelForm

class ParameterForm(ModelForm):
    class Meta:
        model = models.UserInput
        fields = "__all__"
