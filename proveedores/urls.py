from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # Formulario de registro de proveedor
    path('registro/', views.proveedor_form_view, name='registro'),

    # Formulario de actualización de proveedor
    path('actualizar/<int:pk>/', views.proveedor_update_view, name='actualizar'),

    # Página de éxito
    path('success/<int:pk>/', views.success_view, name='success'),

    # Lista de proveedores (solo para staff)
    path('lista/', views.ProveedorListView.as_view(), name='lista'),

    # Detalle de proveedor
    path('detalle/<int:pk>/', views.ProveedorDetailView.as_view(), name='detalle'),
]
