from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Proveedor(models.Model):
    """Modelo principal para información general del proveedor"""

    NATURALEZA_JURIDICA_CHOICES = [
        ('PERSONA_NATURAL', 'Persona Natural'),
        ('PERSONA_JURIDICA', 'Persona Jurídica'),
        ('SOCIEDAD', 'Sociedad'),
    ]

    TIPO_IDENTIFICACION_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'NIT'),
        ('CE', 'Cédula de Extranjería'),
        ('PASAPORTE', 'Pasaporte'),
    ]

    CONDICIONES_PAGO_CHOICES = [
        ('001', 'Contado'),
        ('008', 'Crédito 8 Días'),
        ('010', 'Crédito 10 Días'),
        ('015', 'Crédito 15 Días'),
        ('030', 'Crédito 30 Días'),
        ('045', 'Crédito 45 Días'),
        ('060', 'Crédito 60 Días'),
        ('OTRO', 'Otro'),
    ]

    # Información General
    fecha_diligenciamiento = models.DateField(verbose_name='Fecha de Diligenciamiento')
    nombre_razon_social = models.CharField(max_length=200, verbose_name='Nombre o Razón Social')
    naturaleza_juridica = models.CharField(
        max_length=20,
        choices=NATURALEZA_JURIDICA_CHOICES,
        verbose_name='Naturaleza Jurídica'
    )
    tipo_identificacion = models.CharField(
        max_length=20,
        choices=TIPO_IDENTIFICACION_CHOICES,
        verbose_name='Tipo de Identificación'
    )
    numero_identificacion = models.CharField(max_length=20, verbose_name='Número de Identificación', unique=True)
    direccion = models.CharField(max_length=200, verbose_name='Dirección')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    celular = models.CharField(max_length=20, verbose_name='Celular')
    pais = models.CharField(max_length=100, default='Colombia', verbose_name='País')
    departamento = models.CharField(max_length=100, verbose_name='Departamento')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad')

    # Condiciones de Pago
    condicion_pago = models.CharField(
        max_length=10,
        choices=CONDICIONES_PAGO_CHOICES,
        verbose_name='Condición de Pago'
    )
    condicion_pago_otro = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Otra Condición de Pago (especificar)'
    )

    # Firma y Aprobación
    datos_representante_legal = models.CharField(
        max_length=200,
        verbose_name='Datos del Representante Legal'
    )
    firma_representante = models.ImageField(
        upload_to='firmas/',
        blank=True,
        null=True,
        verbose_name='Firma del Representante Legal'
    )
    sello = models.ImageField(
        upload_to='sellos/',
        blank=True,
        null=True,
        verbose_name='Sello'
    )

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_razon_social} - {self.numero_identificacion}"


class Contacto(models.Model):
    """Modelo para otros contactos del proveedor"""

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='contactos',
        verbose_name='Proveedor'
    )
    nombre_apellidos = models.CharField(max_length=200, verbose_name='Nombre y Apellidos')
    cargo = models.CharField(max_length=100, verbose_name='Cargo')
    direccion = models.CharField(max_length=200, verbose_name='Dirección')
    correo_electronico = models.EmailField(verbose_name='Correo Electrónico')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    celular = models.CharField(max_length=20, verbose_name='Celular')

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'

    def __str__(self):
        return f"{self.nombre_apellidos} - {self.cargo}"


class Impuesto(models.Model):
    """Modelo para impuestos del proveedor"""

    TIPO_IMPUESTO_CHOICES = [
        ('COMPRAS', 'Retención en la Fuente por Compras'),
        ('SERVICIOS', 'Retención en la Fuente por Servicios'),
        ('TRANSPORTE', 'Retención en la Fuente por Transporte'),
        ('OTRO', 'Retención en la Fuente por Otro Concepto'),
    ]

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='impuestos',
        verbose_name='Proveedor'
    )
    tipo_impuesto = models.CharField(
        max_length=20,
        choices=TIPO_IMPUESTO_CHOICES,
        verbose_name='Tipo de Impuesto'
    )
    aplica = models.BooleanField(default=False, verbose_name='¿Aplica?')
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        verbose_name='Porcentaje'
    )
    codigo_actividad_economica = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Código Actividad Económica (CIIU)'
    )
    tarifa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        verbose_name='Tarifa'
    )
    municipio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Municipio'
    )
    resolucion_exento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Si es exento, indicar número y fecha de resolución'
    )
    otro_concepto = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Especificar otro concepto'
    )

    class Meta:
        verbose_name = 'Impuesto'
        verbose_name_plural = 'Impuestos'

    def __str__(self):
        return f"{self.get_tipo_impuesto_display()} - {self.proveedor.nombre_razon_social}"


class DocumentoRequerido(models.Model):
    """Modelo para documentos requeridos del proveedor"""

    proveedor = models.OneToOneField(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Proveedor'
    )

    # Documentos
    fotocopia_rut = models.FileField(
        upload_to='documentos/rut/',
        blank=True,
        null=True,
        verbose_name='Fotocopia del RUT'
    )
    solicitud_vinculacion = models.FileField(
        upload_to='documentos/solicitud/',
        blank=True,
        null=True,
        verbose_name='Solicitud de Vinculación o Actualización'
    )
    certificado_camara_comercio = models.FileField(
        upload_to='documentos/camara/',
        blank=True,
        null=True,
        verbose_name='Certificado de Cámara y Comercio (No más de 30 días)'
    )
    certificacion_bancaria = models.FileField(
        upload_to='documentos/bancaria/',
        blank=True,
        null=True,
        verbose_name='Certificación Bancaria'
    )
    fotocopia_cc_representante = models.FileField(
        upload_to='documentos/cc_representante/',
        blank=True,
        null=True,
        verbose_name='Fotocopia C.C. Representante Legal'
    )
    autorizacion_datos = models.FileField(
        upload_to='documentos/autorizacion/',
        blank=True,
        null=True,
        verbose_name='Autorización para Recolección de Datos'
    )

    class Meta:
        verbose_name = 'Documento Requerido'
        verbose_name_plural = 'Documentos Requeridos'

    def __str__(self):
        return f"Documentos de {self.proveedor.nombre_razon_social}"
