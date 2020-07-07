from django.urls import path

from . import views
#from views import PrimerFinderView

urlpatterns = [
    path('', views.PrimerFinderView.as_view(), name='index'),
    path('api/results', views.PrimerFinderView.as_view(), name='primer_results'),
    path('download/', views.PrimerFinderView.downloadURL, name="downloadURL"),
]
