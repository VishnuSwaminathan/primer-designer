from django.shortcuts import render
from django.http import HttpResponse

from .forms import *
def index(request):
    return render(request, 'entropy/index.html', context={'form': ParameterForm()})
