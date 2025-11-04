"""
URLs de la aplicación core (dashboard principal y funcionalidades compartidas).
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard_principal, name='dashboard'),
    path('api/municipios/<str:departamento_id>/', views.get_municipios, name='get_municipios'),
]
