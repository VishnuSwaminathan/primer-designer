from . import models
from django.forms import ModelForm, Form
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

class ParameterForm(ModelForm):
    class Meta:
        model = models.UserInput
        fields = "__all__"

class CustomSubmitButton(Field):
    template = 'custom_submit_button.html'
    
class CustomTooltip(Field):
    template = 'tooltip.html'

class PrimerForm(Form):
    #msa_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'MSA Text'}))
    #msa_text = forms.CharField(required=False)
    msa_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Some helpful tip for input', 'class': 'form-control', 'data-toggle':"tooltip", 'data-placement':"left", 'title':"Optional"}))
    msa_file = forms.FileField()
    min_primer_len = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Min Primer Length - 19', 'class': 'form-control'}))
    max_primer_len = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Primer Length - 23', 'class': 'form-control'}))
    na_conc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Na Conc - 0.05', 'class': 'form-control'}))
    amplicon_lower = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Amplicon Lower - 75', 'class': 'form-control'}))
    amplicon_upper = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Amplicon Upper - 150', 'class': 'form-control'}))
    max_degeneracy = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Degeneracy - 1', 'class': 'form-control'}))
    min_melting_temp = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Min Melting Temperature - 56', 'class': 'form-control'}))
    max_melting_temp = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Max Melting Temperature - 62', 'class': 'form-control'}))
    min_gc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Min GC - 0.3', 'class': 'form-control'}))
    max_gc = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.00001', 'placeholder': 'Max GC - 0.6', 'class': 'form-control'}))
    find_gc_clamp = forms.BooleanField()
    filter_gc_clamp = forms.BooleanField()
    max_edit_distance = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Max Edit Distance - 1', 'class': 'form-control'}))
    outgroup_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Outgroup Text', 'class': 'form-control'}))
    #outgroup_file = forms.FileField(required=False)
    outgroup_file = forms.FileField()

    #we only need one or the other of file/text for seq data
    def clean(self):
        cleaned_data = super().clean()
        #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_show_errors = True
        #
        self.helper.layout = Layout(
            Row(
                Column('msa_text', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('msa_file', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('min_primer_len', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('max_primer_len', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('na_conc', css_class='form-group col-lg-3 col-sm-12 mb-2'),
                Column('amplicon_lower', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('amplicon_upper', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('max_degeneracy', css_class='form-group col-lg-3 col-sm-12 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('min_melting_temp', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('max_melting_temp', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('min_gc', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('max_gc', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('find_gc_clamp', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                Column('filter_gc_clamp', css_class='form-group col-lg-3 col-sm-6 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column('max_edit_distance', css_class='form-group col-lg-4 mb-2'),
                Column('outgroup_text', css_class='form-group col-lg-8 mb-2'),
                css_class='form-row'
            ),
            Row(
                Column(css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 mb-2'),
                Column('outgroup_file', css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 text-center mb-2'),
                Column(css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 mb-2'),
                css_class='form-row'
            ),
            #CustomSubmitButton('SUBMIT')
            Row(
                Column(css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 mb-2'),
                Column(Submit('submit', 'SUBMIT'), css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 text-center mb-2'),
                Column(css_class='form-group col-lg-4 col-md-4 col-sm-4 col-xs-4 mb-2'),
                css_class='form-row'
            )
            
        )
