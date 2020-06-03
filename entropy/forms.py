from . import models
from django.forms import ModelForm, Form
from django import forms
class ParameterForm(ModelForm):
    class Meta:
        model = models.UserInput
        fields = "__all__"

class PrimerForm(Form):
    #msa_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'MSA Text'}))
    #msa_text = forms.CharField(required=False)
    msa_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Some helpful tip for input'}))
    msa_file = forms.FileField(required=False)
    min_primer_len = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Min Primer Length'}))
    max_primer_len = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Primer Length'}))
    na_conc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Na Conc'}))
    amplicon_lower = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Amplicon Lower'}))
    amplicon_upper = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Amplicon Upper'}))
    max_degeneracy = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Degeneracy'}))
    min_melting_temp = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Min Melting Temperature'}))
    max_melting_temp = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Max Melting Temperature'}))
    min_gc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Min GC'}))
    max_gc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Max GC'}))
    find_gc_clamp = forms.BooleanField()
    filter_gc_clamp = forms.BooleanField()
    max_edit_distance = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Edit Distance'}))
    outgroup_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Outgroup Text'}))
    outgroup_file = forms.FileField(required=False)
#
    #we only need one or the other of file/text for seq data
    def clean(self):
        cleaned_data = super().clean()
