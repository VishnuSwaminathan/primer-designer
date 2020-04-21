from . import models
from django.forms import ModelForm, Form
from django import forms
class ParameterForm(ModelForm):
    class Meta:
        model = models.UserInput
        fields = "__all__"

class PrimerForm(Form):
    msa_text = forms.CharField(required=False)
    msa_file = forms.FileField(required=False)
    min_primer_len = forms.IntegerField()
    max_primer_len = forms.IntegerField()
    na_conc = forms.FloatField()
    amplicon_lower = forms.IntegerField()
    amplicon_upper = forms.IntegerField()
    max_degeneracy = forms.IntegerField()
    min_melting_temp = forms.FloatField()
    max_melting_temp = forms.FloatField()
    min_gc = forms.FloatField()
    max_gc = forms.FloatField()
    find_gc_clamp = forms.BooleanField()
    filter_gc_clamp = forms.BooleanField()
    max_edit_distance = forms.IntegerField()
    outgroup_text = forms.CharField(required=False)
    outgroup_file = forms.FileField(required=False)

    #we only need one or the other of file/text for seq data
    def clean(self):
        cleaned_data = super().clean()
