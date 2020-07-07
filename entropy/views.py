from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic.edit import FormView
from .forms import *
from .primer_finder_classes import *
import io
import os
import logging
import csv
from django.conf import settings
#import pdb; pdb.set_trace()


# Get an instance of a logger
#logger = logging.getLogger(__name__)

"""
def index(request):
    return render(request, 'entropy/index.html', context={'form': ParameterForm()})
"""
#
class PrimerFinderView(FormView):
    def __init__(self):
        self.items = None
    
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
                                                  max_melting_temp=form_data['max_melting_temp'],
                                                  min_gc=form_data['min_gc'],
                                                  max_gc=form_data['max_gc'],
                                                  select_gc_clamp=form_data['find_gc_clamp'],
                                                  omit_gc_clamp=form_data['filter_gc_clamp'],
                                                  max_edit_dist=form_data['max_edit_distance'],
                                                  outgroup=outgroup_file)
        self.items = primerpairs
        #file_path = os.path.join(settings.TEMPLATE_URL, 'entropy-out.csv')
        #if os.path.exists(file_path):        
            #with open(file_path, 'wr') as output:
                
            
        #print(primerpairs)
        #return primer_results().
        #return render(self.request, 'entropy/index.html', {'primerpairs': primerpairs, 'action': self.action })
        #########################################################################################################################
        ##################################################### ^ OLD #############################################################
        no_results = False
        plot = None
        if primerpairs == -1:
            print("NO resutls found")
            no_results = True
            primerpairs = None
        if not no_results:
            print("Results Found")
            #primerFinder.saveCSV()
            plot = primerFinder.html_plot()
        print(len([pair for pair in primerpairs]))
        return render(self.request, 'entropy/index.html', {'primerpairs': primerpairs, 'action': self.action, 'no_results': no_results, 'form': self.form_class, 'plot':plot})
    
    def download(request, path):
        file_path = os.path.join(settings.TEMPLATE_URL, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/csv")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    
    def downloadURL(self, request, *args, **kwargs):
        response=HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="entropy-out-new.csv"'
        writer = csv.writer(response, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in self.items:
            writer.writerow(i)
        return response
        
            