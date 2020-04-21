from django.urls import path

from . import views

urlpatterns = [
    path('', views.PrimerFinderView.as_view(), name='index'),
]
