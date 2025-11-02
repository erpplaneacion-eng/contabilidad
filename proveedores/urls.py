from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # Formulario de registro público de proveedor (sin autenticación)
    path('registro-publico/', views.proveedor_form_view, name='registro_publico'),

    # Formulario de actualización de proveedor (requiere autenticación)
    path('<int:pk>/editar/', views.proveedor_update_view, name='editar'),

    # Eliminar proveedor (requiere autenticación y permisos de admin)
    path('<int:pk>/eliminar/', views.proveedor_delete_view, name='eliminar'),

    # Página de éxito después del registro
    path('success/<int:pk>/', views.success_view, name='success'),

    # Lista de proveedores (requiere autenticación) - URL principal
    path('', views.ProveedorListView.as_view(), name='lista'),

    # Detalle de proveedor (requiere autenticación)
    path('<int:pk>/', views.ProveedorDetailView.as_view(), name='detalle'),
]
