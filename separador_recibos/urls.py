from django.urls import path
from . import views

app_name = 'separador_recibos'

urlpatterns = [
    # URLs principales
    path('', views.upload_pdf, name='upload_pdf'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tabla/', views.TablaRecibosView.as_view(), name='tabla_recibos'),
    
    # URLs de procesamiento
    path('procesando/<uuid:procesamiento_id>/', views.process_status, name='process_status'),
    path('resultados/<uuid:procesamiento_id>/', views.results, name='results'),
    path('descargar/<uuid:procesamiento_id>/', views.download_result, name='download_result'),
    
    # URLs de recibos individuales
    path('recibo/<uuid:recibo_id>/', views.ver_recibo, name='ver_recibo'),
    path('recibo/<uuid:recibo_id>/imagen/', views.descargar_imagen, name='descargar_imagen'),
    
    
    # URLs AJAX
    path('ajax/validar/<uuid:recibo_id>/', views.validar_recibo, name='validar_recibo'),
    
    # URLs de exportación
    path('exportar/', views.exportar_recibos, name='exportar_recibos'),
    path('exportar-imagenes/', views.exportar_imagenes_seleccionadas, name='exportar_imagenes_seleccionadas'),
    path('descargar-pdfs/<uuid:procesamiento_id>/', views.descargar_pdfs_procesamiento, name='descargar_pdfs_procesamiento'),
    path('descargar-pdfs-seleccionados/', views.descargar_pdfs_seleccionados, name='descargar_pdfs_seleccionados'),
]