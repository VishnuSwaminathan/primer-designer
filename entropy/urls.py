from django.urls import path

from . import views

urlpatterns = [
    path('', views.PrimerFinderView.as_view(), name='index'),
    path('api/results', views.PrimerFinderView.as_view(), name='primer_results')
]
