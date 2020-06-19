from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import FormView
from .forms import *
from .primer_finder_classes import *
import io
import logging
#import pdb; pdb.set_trace()


# Get an instance of a logger
#logger = logging.getLogger(__name__)

"""
def index(request):
    return render(request, 'entropy/index.html', context={'form': ParameterForm()})
"""
#
class PrimerFinderView(FormView):
    template_name = "entropy/index.html"
    form_class = PrimerForm
    action = "primer_finder"
    success_url="/results/"

    #TODO double check that I need this. It might be for ajax
    '''
    def get_context_data(self, *args, **kwargs):
        context = super(PrimerFinderView, self).get_context_data(**kwargs)
        context['action'] = self.action
        return context
    '''

    def form_invalid(self, form):
        return super().form_invalid(form)
    
    
    def form_valid(self, form):
        form_data = form.cleaned_data
        msa_bytesIO = self.request.FILES['msa_file'].file
        msa_file = io.TextIOWrapper(msa_bytesIO)
        outgroup_bytesIO = self.request.FILES['outgroup_file'].file
        outgroup_file = io.TextIOWrapper(outgroup_bytesIO)
        primerFinder = PrimerFinder()
        primers = primerFinder.identify_primers(filename=msa_file,
                                                min_primer_length=form_data['min_primer_len'],
                                                max_primer_length=form_data['max_primer_len'],
                                                na_conc=form_data['na_conc'])

        primerpairs = primerFinder.identify_pairs(primers=primers,
                                                  amp_min=form_data['amplicon_lower'],
                                                  amp_max=form_data['amplicon_upper'],
                                                  max_degeneracy=form_data['max_degeneracy'],
                                                  min_melting_temp=form_data['min_melting_temp'],
                                                  min_gc=form_data['min_gc'],
                                                  max_gc=form_data['max_gc'],
                                                  select_gc_clamp=form_data['find_gc_clamp'],
                                                  omit_gc_clamp=form_data['filter_gc_clamp'],
                                                  max_edit_dist=form_data['max_edit_distance'],
                                                  outgroup=outgroup_file)
        #print(primerpairs)
        #return primer_results().
        return render(self.request, 'entropy/index.html', {'primerpairs': primerpairs, 'action': self.action })
        
        
    #def primer_results(self, *args, **kwargs):
        
        # try: 
           # primepairs
        #except NameError: 
            #return render(self.request, 'entropy/erroReturn.html')
            #print('nothing')
        #else:
            #return render(self.request, 'entropy/index.html', {'primerpairs': primerpairs, 'action': self.action })
        
