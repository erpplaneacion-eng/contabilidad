from django.contrib import admin
from .models import ProcesamientoRecibo, ReciboDetectado


@admin.register(ProcesamientoRecibo)
class ProcesamientoReciboAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'usuario', 'fecha_subida', 'estado', 'total_recibos'
    ]
    list_filter = ['estado', 'fecha_subida', 'usuario']
    search_fields = ['usuario__username', 'id']
    readonly_fields = ['id', 'fecha_subida']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'usuario', 'archivo_original', 'fecha_subida')
        }),
        ('Estado del Procesamiento', {
            'fields': ('estado', 'total_recibos', 'mensaje_error')
        }),
        ('Archivo Resultado', {
            'fields': ('archivo_resultado',)
        }),
    )


@admin.register(ReciboDetectado)
class ReciboDetectadoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_secuencial', 'nombre_beneficiario', 'valor', 
        'entidad_bancaria', 'fecha_aplicacion', 'validado'
    ]
    list_filter = ['validado', 'entidad_bancaria', 'fecha_aplicacion', 'procesamiento']
    search_fields = [
        'nombre_beneficiario', 'numero_cuenta', 'referencia', 'documento'
    ]
    readonly_fields = [
        'id', 'fecha_deteccion', 'numero_secuencial', 'procesamiento'
    ]
    
    fieldsets = (
        ('Información del Recibo', {
            'fields': ('procesamiento', 'numero_secuencial', 'nombre_beneficiario', 'valor')
        }),
        ('Datos Bancarios', {
            'fields': ('entidad_bancaria', 'numero_cuenta', 'tipo_cuenta', 'documento')
        }),
        ('Información de Transacción', {
            'fields': ('referencia', 'fecha_aplicacion', 'concepto', 'estado_pago')
        }),
        ('Coordenadas y Procesamiento', {
            'fields': ('coordenada_x', 'coordenada_y', 'ancho', 'alto')
        }),
        ('Archivos', {
            'fields': ('imagen_recibo', 'texto_extraido')
        }),
        ('Validación', {
            'fields': ('validado', 'fecha_deteccion')
        }),
    )