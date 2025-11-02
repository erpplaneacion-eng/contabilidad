from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal


class ProcesamientoRecibo(models.Model):
    """Modelo para almacenar información de procesamiento"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo_original = models.FileField(upload_to='pdfs_originales/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PROCESANDO', 'Procesando'),
            ('COMPLETADO', 'Completado'),
            ('ERROR', 'Error')
        ],
        default='PENDIENTE'
    )
    total_recibos = models.PositiveIntegerField(default=0)
    archivo_resultado = models.FileField(upload_to='pdfs_procesados/', null=True, blank=True)
    mensaje_error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Procesamiento {self.id} - {self.usuario.username}"


class ReciboDetectado(models.Model):
    """Modelo para almacenar información de cada recibo detectado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    procesamiento = models.ForeignKey(ProcesamientoRecibo, on_delete=models.CASCADE)
    numero_secuencial = models.PositiveIntegerField()
    coordenada_x = models.FloatField()
    coordenada_y = models.FloatField()
    ancho = models.FloatField()
    alto = models.FloatField()
    
    # Información extraída del recibo
    imagen_recibo = models.ImageField(upload_to='imagenes_recibos/', null=True, blank=True)
    nombre_beneficiario = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    entidad_bancaria = models.CharField(max_length=100, blank=True)
    numero_cuenta = models.CharField(max_length=50, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    fecha_aplicacion = models.DateField(null=True, blank=True)
    concepto = models.CharField(max_length=100, blank=True)
    estado_pago = models.CharField(max_length=50, blank=True)
    tipo_cuenta = models.CharField(max_length=20, blank=True)
    documento = models.CharField(max_length=50, blank=True)
    
    # Información de procesamiento
    texto_extraido = models.TextField(blank=True)
    fecha_deteccion = models.DateTimeField(auto_now_add=True)
    validado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['numero_secuencial']
        indexes = [
            models.Index(fields=['procesamiento', 'numero_secuencial']),
            models.Index(fields=['nombre_beneficiario']),
            models.Index(fields=['fecha_aplicacion']),
        ]
    
    def __str__(self):
        return f"Recibo {self.numero_secuencial} - {self.nombre_beneficiario or 'Sin nombre'}"
    
    @property
    def valor_formateado(self):
        """Retorna el valor formateado como moneda"""
        if self.valor:
            return f"${self.valor:,.2f}"
        return "N/A"