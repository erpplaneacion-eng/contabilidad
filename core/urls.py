"""
URLs de la aplicación core (dashboard principal y funcionalidades compartidas).
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_principal, name='dashboard'),
]
