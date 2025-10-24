from django.contrib import admin
from .models import Proveedor, Contacto, Impuesto, DocumentoRequerido


class ContactoInline(admin.TabularInline):
    """Inline para gestionar contactos desde el admin de Proveedor"""
    model = Contacto
    extra = 1
    fields = ['nombre_apellidos', 'cargo', 'correo_electronico', 'telefono', 'celular', 'ciudad']


class ImpuestoInline(admin.TabularInline):
    """Inline para gestionar impuestos desde el admin de Proveedor"""
    model = Impuesto
    extra = 1
    fields = ['tipo_impuesto', 'aplica', 'porcentaje', 'tarifa', 'municipio']


class DocumentoRequeridoInline(admin.StackedInline):
    """Inline para gestionar documentos desde el admin de Proveedor"""
    model = DocumentoRequerido
    can_delete = False
    fields = [
        'fotocopia_rut',
        'solicitud_vinculacion',
        'certificado_camara_comercio',
        'certificacion_bancaria',
        'fotocopia_cc_representante',
        'autorizacion_datos',
    ]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Administración del modelo Proveedor"""

    list_display = [
        'numero_identificacion',
        'nombre_razon_social',
        'naturaleza_juridica',
        'ciudad',
        'telefono',
        'fecha_creacion',
    ]

    list_filter = [
        'naturaleza_juridica',
        'tipo_identificacion',
        'departamento',
        'condicion_pago',
        'fecha_creacion',
    ]

    search_fields = [
        'nombre_razon_social',
        'numero_identificacion',
        'ciudad',
        'datos_representante_legal',
    ]

    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    fieldsets = (
        ('Información General', {
            'fields': (
                'fecha_diligenciamiento',
                'nombre_razon_social',
                'naturaleza_juridica',
                'tipo_identificacion',
                'numero_identificacion',
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion',
                'pais',
                'departamento',
                'ciudad',
                'telefono',
                'celular',
            )
        }),
        ('Condiciones de Pago', {
            'fields': (
                'condicion_pago',
                'condicion_pago_otro',
            )
        }),
        ('Representante Legal', {
            'fields': (
                'datos_representante_legal',
                'firma_representante',
                'sello',
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [ContactoInline, ImpuestoInline, DocumentoRequeridoInline]

    date_hierarchy = 'fecha_creacion'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('contactos', 'impuestos')


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    """Administración del modelo Contacto"""

    list_display = [
        'nombre_apellidos',
        'cargo',
        'proveedor',
        'correo_electronico',
        'telefono',
        'ciudad',
    ]

    list_filter = ['cargo', 'ciudad']

    search_fields = [
        'nombre_apellidos',
        'cargo',
        'correo_electronico',
        'proveedor__nombre_razon_social',
    ]

    autocomplete_fields = ['proveedor']


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    """Administración del modelo Impuesto"""

    list_display = [
        'proveedor',
        'tipo_impuesto',
        'aplica',
        'porcentaje',
        'tarifa',
        'municipio',
    ]

    list_filter = ['tipo_impuesto', 'aplica', 'municipio']

    search_fields = [
        'proveedor__nombre_razon_social',
        'codigo_actividad_economica',
        'municipio',
    ]

    autocomplete_fields = ['proveedor']


@admin.register(DocumentoRequerido)
class DocumentoRequeridoAdmin(admin.ModelAdmin):
    """Administración del modelo DocumentoRequerido"""

    list_display = ['proveedor', 'tiene_rut', 'tiene_camara_comercio', 'tiene_certificacion_bancaria']

    search_fields = ['proveedor__nombre_razon_social']

    autocomplete_fields = ['proveedor']

    def tiene_rut(self, obj):
        """Indica si tiene RUT"""
        return bool(obj.fotocopia_rut)
    tiene_rut.boolean = True
    tiene_rut.short_description = 'RUT'

    def tiene_camara_comercio(self, obj):
        """Indica si tiene certificado de cámara de comercio"""
        return bool(obj.certificado_camara_comercio)
    tiene_camara_comercio.boolean = True
    tiene_camara_comercio.short_description = 'Cámara de Comercio'

    def tiene_certificacion_bancaria(self, obj):
        """Indica si tiene certificación bancaria"""
        return bool(obj.certificacion_bancaria)
    tiene_certificacion_bancaria.boolean = True
    tiene_certificacion_bancaria.short_description = 'Certificación Bancaria'


# Personalización del sitio de administración
admin.site.site_header = "Administración de Proveedores"
admin.site.site_title = "Portal de Proveedores"
admin.site.index_title = "Gestión de Proveedores"
